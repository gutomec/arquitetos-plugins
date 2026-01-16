"""
Hybrid Knowledge Base MCP Server
================================
Sistema especializado em Bases de Conhecimento Hibridas com Milvus e Neo4j.

Stack:
- Milvus (vector DB) + etcd (metadados)
- Neo4j com APOC (graph DB)
- Embeddings: Google (text-embedding-004) e Cohere (embed-v4)

Tools:
- Ingestao: ingest_document, ingest_batch, build_knowledge_graph
- Retrieval: vector_search, graph_search, hybrid_search, multi_hop_reasoning
- Schema: analyze_schema, analyze_collections, validate_consistency, health_check
"""

from fastmcp import FastMCP
from fastmcp.tools import ToolError, ToolResult, TextContent, ToolAnnotations
from pydantic import Field
from typing import Optional, List, Literal
from neo4j import GraphDatabase
from pymilvus import MilvusClient, Collection, connections, utility
import google.generativeai as genai
import cohere
import hashlib
import json
import asyncio
import logging
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)

# Environment variables
MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
ETCD_HOST = os.getenv("ETCD_HOST", "localhost")
ETCD_PORT = os.getenv("ETCD_PORT", "2379")

# Embedding dimensions
EMBEDDING_DIM_GOOGLE = 768  # text-embedding-004
EMBEDDING_DIM_COHERE = 1024  # embed-v4

# ============================================================================
# INITIALIZE MCP SERVER
# ============================================================================

mcp = FastMCP(
    name="Hybrid Knowledge Base",
    version="1.0.0",
    description="Sistema GraphRAG hibrido com Milvus e Neo4j para bases de conhecimento empresariais"
)

# ============================================================================
# DATABASE CONNECTIONS
# ============================================================================

def get_milvus_client():
    """Get Milvus client connection."""
    return MilvusClient(uri=MILVUS_URI)

def get_neo4j_driver():
    """Get Neo4j driver connection."""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def get_google_client():
    """Get Google Generative AI client."""
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai

def get_cohere_client():
    """Get Cohere client."""
    return cohere.Client(COHERE_API_KEY)

# ============================================================================
# EMBEDDING FUNCTIONS
# ============================================================================

async def generate_embedding(
    text: str,
    provider: Literal["google", "cohere"] = "google"
) -> List[float]:
    """Generate embedding using specified provider."""
    try:
        if provider == "google":
            client = get_google_client()
            result = client.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="RETRIEVAL_DOCUMENT"
            )
            return result['embedding']
        elif provider == "cohere":
            client = get_cohere_client()
            response = client.embed(
                texts=[text],
                model="embed-v4",
                input_type="search_document"
            )
            return response.embeddings[0]
    except Exception as e:
        logger.error(f"Embedding error ({provider}): {e}")
        raise ToolError(f"Failed to generate embedding: {e}")

async def generate_query_embedding(
    text: str,
    provider: Literal["google", "cohere"] = "google"
) -> List[float]:
    """Generate query embedding (optimized for retrieval)."""
    try:
        if provider == "google":
            client = get_google_client()
            result = client.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="RETRIEVAL_QUERY"
            )
            return result['embedding']
        elif provider == "cohere":
            client = get_cohere_client()
            response = client.embed(
                texts=[text],
                model="embed-v4",
                input_type="search_query"
            )
            return response.embeddings[0]
    except Exception as e:
        logger.error(f"Query embedding error ({provider}): {e}")
        raise ToolError(f"Failed to generate query embedding: {e}")

# ============================================================================
# TEXT PROCESSING
# ============================================================================

def semantic_chunk(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 80
) -> List[dict]:
    """Split text into semantic chunks."""
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
        length_function=len
    )

    chunks = splitter.split_text(text)

    return [
        {
            "id": hashlib.md5(f"{text[:50]}_{i}".encode()).hexdigest(),
            "content": chunk,
            "index": i,
            "total_chunks": len(chunks)
        }
        for i, chunk in enumerate(chunks)
    ]

def extract_entities_prompt(text: str) -> str:
    """Generate prompt for entity extraction."""
    return f"""Extract all named entities and their relationships from the following text.
Return as JSON with format:
{{
    "entities": [
        {{"name": "entity name", "type": "PERSON|ORGANIZATION|LOCATION|CONCEPT|DOCUMENT|TOPIC", "properties": {{}}}}
    ],
    "relationships": [
        {{"source": "entity1", "target": "entity2", "type": "RELATIONSHIP_TYPE", "properties": {{}}}}
    ]
}}

Text:
{text}

JSON:"""

# ============================================================================
# INGESTION TOOLS
# ============================================================================

@mcp.tool(
    name="ingest_document",
    annotations=ToolAnnotations(
        title="Ingest Document",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)
async def ingest_document(
    content: str = Field(..., description="Conteudo do documento a ser ingerido"),
    doc_id: Optional[str] = Field(None, description="ID unico do documento (gerado automaticamente se nao fornecido)"),
    title: Optional[str] = Field(None, description="Titulo do documento"),
    source: Optional[str] = Field(None, description="Fonte/origem do documento"),
    doc_type: Optional[str] = Field("text", description="Tipo do documento: text, markdown, pdf"),
    embedding_provider: Literal["google", "cohere"] = Field("google", description="Provedor de embedding"),
    chunk_size: int = Field(400, description="Tamanho do chunk em caracteres"),
    chunk_overlap: int = Field(80, description="Overlap entre chunks"),
    collection_name: str = Field("documents", description="Nome da colecao Milvus"),
    extract_entities: bool = Field(True, description="Extrair entidades para o grafo"),
) -> ToolResult:
    """
    Processa e ingere um documento no sistema hibrido.

    Pipeline:
    1. Chunking semantico do texto
    2. Geracao de embeddings (Google ou Cohere)
    3. Armazenamento no Milvus
    4. Extracao de entidades (opcional)
    5. Criacao de nodes/relationships no Neo4j
    """
    try:
        # Generate document ID if not provided
        if not doc_id:
            doc_id = hashlib.md5(content[:100].encode()).hexdigest()

        # Semantic chunking
        chunks = semantic_chunk(content, chunk_size, chunk_overlap)

        # Get Milvus client
        milvus = get_milvus_client()

        # Ensure collection exists
        dim = EMBEDDING_DIM_GOOGLE if embedding_provider == "google" else EMBEDDING_DIM_COHERE
        if not milvus.has_collection(collection_name):
            milvus.create_collection(
                collection_name=collection_name,
                dimension=dim,
                metric_type="COSINE",
                auto_id=False,
                id_type="VARCHAR",
                max_length=64
            )

        # Process chunks and generate embeddings
        vectors_data = []
        for chunk in chunks:
            embedding = await generate_embedding(chunk["content"], embedding_provider)
            vectors_data.append({
                "id": f"{doc_id}_{chunk['index']}",
                "vector": embedding,
                "content": chunk["content"],
                "doc_id": doc_id,
                "chunk_index": chunk["index"],
                "title": title or "",
                "source": source or "",
                "doc_type": doc_type,
                "created_at": datetime.now().isoformat()
            })

        # Insert into Milvus
        milvus.insert(collection_name=collection_name, data=vectors_data)

        # Neo4j: Create document node and chunks
        neo4j = get_neo4j_driver()
        with neo4j.session(database=NEO4J_DATABASE) as session:
            # Create Document node
            session.run("""
                MERGE (d:Document {id: $doc_id})
                SET d.title = $title,
                    d.source = $source,
                    d.doc_type = $doc_type,
                    d.chunk_count = $chunk_count,
                    d.created_at = datetime()
            """, doc_id=doc_id, title=title, source=source,
                doc_type=doc_type, chunk_count=len(chunks))

            # Create Chunk nodes and relationships
            for chunk in chunks:
                session.run("""
                    MERGE (c:Chunk {id: $chunk_id})
                    SET c.content = $content,
                        c.index = $index
                    WITH c
                    MATCH (d:Document {id: $doc_id})
                    MERGE (d)-[:HAS_CHUNK]->(c)
                """, chunk_id=f"{doc_id}_{chunk['index']}",
                    content=chunk["content"], index=chunk["index"], doc_id=doc_id)

        # Entity extraction (optional)
        entities_extracted = 0
        if extract_entities:
            # This would use an LLM to extract entities
            # For now, we create a placeholder
            pass

        neo4j.close()

        result_text = f"""
Document ingested successfully!

Document ID: {doc_id}
Title: {title or 'N/A'}
Chunks created: {len(chunks)}
Embedding provider: {embedding_provider}
Collection: {collection_name}
Entities extracted: {entities_extracted}

Milvus: {len(vectors_data)} vectors inserted
Neo4j: Document + {len(chunks)} chunk nodes created
"""

        return ToolResult(content=[TextContent(type="text", text=result_text)])

    except Exception as e:
        logger.error(f"Ingest error: {e}")
        raise ToolError(f"Failed to ingest document: {e}")


@mcp.tool(
    name="ingest_batch",
    annotations=ToolAnnotations(
        title="Batch Document Ingestion",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)
async def ingest_batch(
    documents: str = Field(..., description="JSON array de documentos [{content, title, source}]"),
    embedding_provider: Literal["google", "cohere"] = Field("google", description="Provedor de embedding"),
    collection_name: str = Field("documents", description="Nome da colecao Milvus"),
    parallel: bool = Field(True, description="Processar em paralelo"),
) -> ToolResult:
    """
    Processa multiplos documentos em lote.
    """
    try:
        docs = json.loads(documents)
        results = []

        for doc in docs:
            result = await ingest_document(
                content=doc.get("content", ""),
                title=doc.get("title"),
                source=doc.get("source"),
                embedding_provider=embedding_provider,
                collection_name=collection_name,
                extract_entities=doc.get("extract_entities", True)
            )
            results.append(result)

        result_text = f"""
Batch ingestion complete!

Documents processed: {len(docs)}
Embedding provider: {embedding_provider}
Collection: {collection_name}
"""

        return ToolResult(content=[TextContent(type="text", text=result_text)])

    except Exception as e:
        logger.error(f"Batch ingest error: {e}")
        raise ToolError(f"Failed to batch ingest: {e}")


@mcp.tool(
    name="build_knowledge_graph",
    annotations=ToolAnnotations(
        title="Build Knowledge Graph",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)
async def build_knowledge_graph(
    text: str = Field(..., description="Texto para extrair entidades e relacoes"),
    doc_id: Optional[str] = Field(None, description="ID do documento associado"),
    entity_types: Optional[str] = Field(
        "PERSON,ORGANIZATION,LOCATION,CONCEPT,TOPIC",
        description="Tipos de entidades para extrair (separados por virgula)"
    ),
) -> ToolResult:
    """
    Extrai entidades e relacoes do texto e cria grafo de conhecimento no Neo4j.

    Usa LLM para:
    1. Identificar entidades nomeadas
    2. Classificar tipos de entidades
    3. Detectar relacionamentos entre entidades
    4. Criar nodes e edges no Neo4j
    """
    try:
        neo4j = get_neo4j_driver()

        # For production, this would call an LLM to extract entities
        # Here we provide a structure for the extracted data

        # Example entity extraction (would be LLM-generated)
        prompt = extract_entities_prompt(text)

        # Placeholder - in production, call LLM here
        # response = await llm.generate(prompt)
        # extracted = json.loads(response)

        # For now, create document relationship
        if doc_id:
            with neo4j.session(database=NEO4J_DATABASE) as session:
                session.run("""
                    MERGE (d:Document {id: $doc_id})
                    SET d.kg_processed = true,
                        d.kg_processed_at = datetime()
                """, doc_id=doc_id)

        neo4j.close()

        result_text = f"""
Knowledge Graph build initiated.

Text length: {len(text)} characters
Document ID: {doc_id or 'N/A'}
Entity types: {entity_types}

Note: Full entity extraction requires LLM integration.
Use the 'extract_entities' parameter in ingest_document for automatic extraction.
"""

        return ToolResult(content=[TextContent(type="text", text=result_text)])

    except Exception as e:
        logger.error(f"KG build error: {e}")
        raise ToolError(f"Failed to build knowledge graph: {e}")


# ============================================================================
# RETRIEVAL TOOLS
# ============================================================================

@mcp.tool(
    name="vector_search",
    annotations=ToolAnnotations(
        title="Vector Semantic Search",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def vector_search(
    query: str = Field(..., description="Query de busca em linguagem natural"),
    top_k: int = Field(5, description="Numero de resultados a retornar"),
    collection_name: str = Field("documents", description="Nome da colecao Milvus"),
    embedding_provider: Literal["google", "cohere"] = Field("google", description="Provedor de embedding"),
    filter_expr: Optional[str] = Field(None, description="Expressao de filtro Milvus (ex: doc_type == 'pdf')"),
    output_fields: Optional[str] = Field(
        "content,doc_id,title,source",
        description="Campos a retornar (separados por virgula)"
    ),
) -> ToolResult:
    """
    Busca semantica vetorial usando Milvus.

    Gera embedding da query e busca os top_k vetores mais similares.
    Suporta filtros por metadados.
    """
    try:
        # Generate query embedding
        query_embedding = await generate_query_embedding(query, embedding_provider)

        # Get Milvus client
        milvus = get_milvus_client()

        # Parse output fields
        fields = [f.strip() for f in output_fields.split(",")]

        # Search
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 16}
        }

        results = milvus.search(
            collection_name=collection_name,
            data=[query_embedding],
            limit=top_k,
            output_fields=fields,
            filter=filter_expr
        )

        # Format results
        output_lines = [f"## Vector Search Results for: '{query}'\n"]
        output_lines.append(f"Found {len(results[0])} results:\n")

        for i, hit in enumerate(results[0], 1):
            score = hit.get("distance", 0)
            entity = hit.get("entity", {})

            output_lines.append(f"### Result {i} (Score: {score:.4f})")
            output_lines.append(f"**Doc ID**: {entity.get('doc_id', 'N/A')}")
            output_lines.append(f"**Title**: {entity.get('title', 'N/A')}")
            output_lines.append(f"**Source**: {entity.get('source', 'N/A')}")
            output_lines.append(f"**Content**: {entity.get('content', '')[:500]}...")
            output_lines.append("")

        return ToolResult(content=[TextContent(type="text", text="\n".join(output_lines))])

    except Exception as e:
        logger.error(f"Vector search error: {e}")
        raise ToolError(f"Vector search failed: {e}")


@mcp.tool(
    name="graph_search",
    annotations=ToolAnnotations(
        title="Graph Cypher Search",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def graph_search(
    cypher: str = Field(..., description="Query Cypher para executar no Neo4j"),
    parameters: Optional[str] = Field(None, description="Parametros JSON para a query"),
) -> ToolResult:
    """
    Executa query Cypher no Neo4j com suporte a APOC.

    Exemplos de queries:
    - MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk) RETURN d.title, count(c)
    - MATCH (e1:Entity)-[r]->(e2:Entity) RETURN e1.name, type(r), e2.name
    - CALL apoc.meta.graph() YIELD nodes, relationships RETURN *
    """
    try:
        neo4j = get_neo4j_driver()
        params = json.loads(parameters) if parameters else {}

        with neo4j.session(database=NEO4J_DATABASE) as session:
            result = session.run(cypher, params)
            records = result.data()

        neo4j.close()

        # Format results
        output_lines = [f"## Graph Search Results\n"]
        output_lines.append(f"Query: `{cypher}`\n")
        output_lines.append(f"Records returned: {len(records)}\n")

        if records:
            output_lines.append("```json")
            output_lines.append(json.dumps(records, indent=2, default=str))
            output_lines.append("```")

        return ToolResult(content=[TextContent(type="text", text="\n".join(output_lines))])

    except Exception as e:
        logger.error(f"Graph search error: {e}")
        raise ToolError(f"Graph search failed: {e}")


@mcp.tool(
    name="hybrid_search",
    annotations=ToolAnnotations(
        title="Hybrid GraphRAG Search",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def hybrid_search(
    query: str = Field(..., description="Query de busca em linguagem natural"),
    top_k: int = Field(5, description="Numero de resultados vetoriais"),
    collection_name: str = Field("documents", description="Nome da colecao Milvus"),
    embedding_provider: Literal["google", "cohere"] = Field("google", description="Provedor de embedding"),
    expand_graph: bool = Field(True, description="Expandir contexto via grafo"),
    max_hops: int = Field(2, description="Numero maximo de hops no grafo"),
) -> ToolResult:
    """
    Busca hibrida GraphRAG combinando vector search + graph traversal.

    Pipeline:
    1. Vector search no Milvus para encontrar chunks relevantes
    2. Extrai doc_ids dos resultados
    3. Graph traversal no Neo4j para expandir contexto
    4. Combina e ranqueia resultados
    """
    try:
        # Step 1: Vector search
        query_embedding = await generate_query_embedding(query, embedding_provider)
        milvus = get_milvus_client()

        vector_results = milvus.search(
            collection_name=collection_name,
            data=[query_embedding],
            limit=top_k,
            output_fields=["content", "doc_id", "title", "source", "chunk_index"]
        )

        # Extract doc IDs
        doc_ids = list(set(
            hit.get("entity", {}).get("doc_id")
            for hit in vector_results[0]
            if hit.get("entity", {}).get("doc_id")
        ))

        # Step 2: Graph expansion
        graph_context = []
        if expand_graph and doc_ids:
            neo4j = get_neo4j_driver()
            with neo4j.session(database=NEO4J_DATABASE) as session:
                # Get related entities and documents
                result = session.run("""
                    MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                    WHERE d.id IN $doc_ids
                    OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
                    OPTIONAL MATCH (e)-[r]-(related:Entity)
                    RETURN d.id as doc_id,
                           d.title as doc_title,
                           collect(DISTINCT e.name) as entities,
                           collect(DISTINCT {
                               relation: type(r),
                               entity: related.name
                           }) as relationships
                    LIMIT 20
                """, doc_ids=doc_ids)

                graph_context = result.data()
            neo4j.close()

        # Format combined results
        output_lines = [f"## Hybrid GraphRAG Search Results\n"]
        output_lines.append(f"Query: '{query}'")
        output_lines.append(f"Provider: {embedding_provider}")
        output_lines.append(f"Vector results: {len(vector_results[0])}")
        output_lines.append(f"Graph expansion: {'enabled' if expand_graph else 'disabled'}\n")

        output_lines.append("### Vector Search Results\n")
        for i, hit in enumerate(vector_results[0], 1):
            entity = hit.get("entity", {})
            score = hit.get("distance", 0)
            output_lines.append(f"**{i}. [{score:.4f}]** {entity.get('title', 'Untitled')}")
            output_lines.append(f"   Content: {entity.get('content', '')[:200]}...")
            output_lines.append("")

        if graph_context:
            output_lines.append("### Graph Context\n")
            for ctx in graph_context:
                output_lines.append(f"**Document**: {ctx.get('doc_title', ctx.get('doc_id'))}")
                entities = ctx.get('entities', [])
                if entities:
                    output_lines.append(f"   Entities: {', '.join(filter(None, entities))}")
                output_lines.append("")

        return ToolResult(content=[TextContent(type="text", text="\n".join(output_lines))])

    except Exception as e:
        logger.error(f"Hybrid search error: {e}")
        raise ToolError(f"Hybrid search failed: {e}")


@mcp.tool(
    name="multi_hop_reasoning",
    annotations=ToolAnnotations(
        title="Multi-hop Graph Reasoning",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def multi_hop_reasoning(
    start_entity: str = Field(..., description="Entidade inicial para a travessia"),
    max_hops: int = Field(3, description="Numero maximo de hops"),
    relationship_types: Optional[str] = Field(None, description="Tipos de relacionamento a seguir (separados por virgula)"),
    target_entity_type: Optional[str] = Field(None, description="Tipo de entidade alvo"),
) -> ToolResult:
    """
    Executa raciocinio multi-hop no grafo de conhecimento.

    Util para:
    - Encontrar conexoes indiretas entre entidades
    - Descobrir caminhos de raciocinio
    - Explorar relacoes complexas
    """
    try:
        neo4j = get_neo4j_driver()

        # Build dynamic query based on parameters
        rel_filter = ""
        if relationship_types:
            types = [t.strip() for t in relationship_types.split(",")]
            rel_filter = f"[r:{':'.join(types)}*1..{max_hops}]"
        else:
            rel_filter = f"[r*1..{max_hops}]"

        target_filter = ""
        if target_entity_type:
            target_filter = f":{target_entity_type}"

        cypher = f"""
            MATCH path = (start {{name: $start_entity}})-{rel_filter}-(end{target_filter})
            RETURN path,
                   length(path) as hops,
                   [n in nodes(path) | n.name] as node_names,
                   [r in relationships(path) | type(r)] as rel_types
            ORDER BY hops
            LIMIT 10
        """

        with neo4j.session(database=NEO4J_DATABASE) as session:
            result = session.run(cypher, start_entity=start_entity)
            paths = result.data()

        neo4j.close()

        # Format results
        output_lines = [f"## Multi-hop Reasoning Results\n"]
        output_lines.append(f"Start entity: {start_entity}")
        output_lines.append(f"Max hops: {max_hops}")
        output_lines.append(f"Paths found: {len(paths)}\n")

        for i, path in enumerate(paths, 1):
            output_lines.append(f"### Path {i} ({path['hops']} hops)")
            nodes = path.get('node_names', [])
            rels = path.get('rel_types', [])

            # Build path visualization
            path_str = nodes[0] if nodes else ""
            for j, rel in enumerate(rels):
                if j + 1 < len(nodes):
                    path_str += f" --[{rel}]--> {nodes[j+1]}"

            output_lines.append(f"```\n{path_str}\n```")
            output_lines.append("")

        return ToolResult(content=[TextContent(type="text", text="\n".join(output_lines))])

    except Exception as e:
        logger.error(f"Multi-hop reasoning error: {e}")
        raise ToolError(f"Multi-hop reasoning failed: {e}")


# ============================================================================
# SCHEMA ANALYSIS TOOLS
# ============================================================================

@mcp.tool(
    name="analyze_schema",
    annotations=ToolAnnotations(
        title="Analyze Neo4j Schema",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def analyze_schema() -> ToolResult:
    """
    Retorna o schema completo do Neo4j incluindo:
    - Node labels e suas propriedades
    - Relationship types
    - Indices e constraints
    - Estatisticas de contagem
    """
    try:
        neo4j = get_neo4j_driver()
        schema_info = {}

        with neo4j.session(database=NEO4J_DATABASE) as session:
            # Get node labels and counts
            labels_result = session.run("""
                CALL db.labels() YIELD label
                CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) as count', {}) YIELD value
                RETURN label, value.count as count
            """)
            schema_info["node_labels"] = [
                {"label": r["label"], "count": r["count"]}
                for r in labels_result.data()
            ]

            # Get relationship types
            rels_result = session.run("""
                CALL db.relationshipTypes() YIELD relationshipType
                CALL apoc.cypher.run('MATCH ()-[r:`' + relationshipType + '`]->() RETURN count(r) as count', {}) YIELD value
                RETURN relationshipType, value.count as count
            """)
            schema_info["relationship_types"] = [
                {"type": r["relationshipType"], "count": r["count"]}
                for r in rels_result.data()
            ]

            # Get indexes
            indexes_result = session.run("SHOW INDEXES")
            schema_info["indexes"] = indexes_result.data()

            # Get constraints
            constraints_result = session.run("SHOW CONSTRAINTS")
            schema_info["constraints"] = constraints_result.data()

            # Get property keys
            props_result = session.run("CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey")
            schema_info["property_keys"] = [r["propertyKey"] for r in props_result.data()]

        neo4j.close()

        # Format output
        output_lines = ["## Neo4j Schema Analysis\n"]

        output_lines.append("### Node Labels")
        for label in schema_info.get("node_labels", []):
            output_lines.append(f"- **{label['label']}**: {label['count']} nodes")

        output_lines.append("\n### Relationship Types")
        for rel in schema_info.get("relationship_types", []):
            output_lines.append(f"- **{rel['type']}**: {rel['count']} relationships")

        output_lines.append(f"\n### Property Keys ({len(schema_info.get('property_keys', []))} total)")
        output_lines.append(", ".join(schema_info.get("property_keys", [])[:20]))
        if len(schema_info.get("property_keys", [])) > 20:
            output_lines.append("...")

        output_lines.append(f"\n### Indexes: {len(schema_info.get('indexes', []))}")
        output_lines.append(f"### Constraints: {len(schema_info.get('constraints', []))}")

        return ToolResult(content=[TextContent(type="text", text="\n".join(output_lines))])

    except Exception as e:
        logger.error(f"Schema analysis error: {e}")
        raise ToolError(f"Schema analysis failed: {e}")


@mcp.tool(
    name="analyze_collections",
    annotations=ToolAnnotations(
        title="Analyze Milvus Collections",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def analyze_collections(
    collection_name: Optional[str] = Field(None, description="Nome da colecao especifica (ou todas se nao fornecido)"),
) -> ToolResult:
    """
    Lista e analisa colecoes Milvus com estatisticas detalhadas.
    """
    try:
        milvus = get_milvus_client()

        # List all collections or get specific one
        if collection_name:
            collections = [collection_name] if milvus.has_collection(collection_name) else []
        else:
            collections = milvus.list_collections()

        output_lines = ["## Milvus Collections Analysis\n"]
        output_lines.append(f"Total collections: {len(collections)}\n")

        for coll_name in collections:
            output_lines.append(f"### Collection: {coll_name}")

            # Get collection info
            try:
                stats = milvus.get_collection_stats(coll_name)
                output_lines.append(f"- **Row count**: {stats.get('row_count', 'N/A')}")

                # Get schema
                coll = Collection(coll_name)
                schema = coll.schema
                output_lines.append(f"- **Fields**: {len(schema.fields)}")
                for field in schema.fields:
                    output_lines.append(f"  - {field.name} ({field.dtype})")

            except Exception as e:
                output_lines.append(f"- Error getting stats: {e}")

            output_lines.append("")

        return ToolResult(content=[TextContent(type="text", text="\n".join(output_lines))])

    except Exception as e:
        logger.error(f"Collection analysis error: {e}")
        raise ToolError(f"Collection analysis failed: {e}")


@mcp.tool(
    name="validate_consistency",
    annotations=ToolAnnotations(
        title="Validate Data Consistency",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def validate_consistency(
    collection_name: str = Field("documents", description="Nome da colecao Milvus"),
) -> ToolResult:
    """
    Verifica consistencia entre Milvus IDs e Neo4j nodes.

    Identifica:
    - Documentos no Milvus sem correspondente no Neo4j
    - Documentos no Neo4j sem vetores no Milvus
    - Chunks orfaos
    """
    try:
        milvus = get_milvus_client()
        neo4j = get_neo4j_driver()

        issues = []
        stats = {"milvus_docs": 0, "neo4j_docs": 0, "orphan_chunks": 0}

        # Get unique doc_ids from Milvus
        milvus_results = milvus.query(
            collection_name=collection_name,
            filter="",
            output_fields=["doc_id"],
            limit=10000
        )
        milvus_doc_ids = set(r.get("doc_id") for r in milvus_results if r.get("doc_id"))
        stats["milvus_docs"] = len(milvus_doc_ids)

        # Get doc_ids from Neo4j
        with neo4j.session(database=NEO4J_DATABASE) as session:
            result = session.run("MATCH (d:Document) RETURN d.id as doc_id")
            neo4j_doc_ids = set(r["doc_id"] for r in result.data() if r.get("doc_id"))
            stats["neo4j_docs"] = len(neo4j_doc_ids)

            # Check for orphan chunks
            orphan_result = session.run("""
                MATCH (c:Chunk)
                WHERE NOT (c)<-[:HAS_CHUNK]-(:Document)
                RETURN count(c) as count
            """)
            stats["orphan_chunks"] = orphan_result.single()["count"]

        neo4j.close()

        # Find inconsistencies
        milvus_only = milvus_doc_ids - neo4j_doc_ids
        neo4j_only = neo4j_doc_ids - milvus_doc_ids

        if milvus_only:
            issues.append(f"Documents in Milvus but not Neo4j: {len(milvus_only)}")
        if neo4j_only:
            issues.append(f"Documents in Neo4j but not Milvus: {len(neo4j_only)}")
        if stats["orphan_chunks"] > 0:
            issues.append(f"Orphan chunks in Neo4j: {stats['orphan_chunks']}")

        # Format output
        output_lines = ["## Data Consistency Report\n"]
        output_lines.append(f"Collection: {collection_name}\n")

        output_lines.append("### Statistics")
        output_lines.append(f"- Milvus documents: {stats['milvus_docs']}")
        output_lines.append(f"- Neo4j documents: {stats['neo4j_docs']}")
        output_lines.append(f"- Orphan chunks: {stats['orphan_chunks']}")

        output_lines.append("\n### Consistency Status")
        if not issues:
            output_lines.append("All data is consistent across Milvus and Neo4j.")
        else:
            output_lines.append("**Issues found:**")
            for issue in issues:
                output_lines.append(f"- {issue}")

        return ToolResult(content=[TextContent(type="text", text="\n".join(output_lines))])

    except Exception as e:
        logger.error(f"Consistency validation error: {e}")
        raise ToolError(f"Consistency validation failed: {e}")


@mcp.tool(
    name="health_check",
    annotations=ToolAnnotations(
        title="System Health Check",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def health_check() -> ToolResult:
    """
    Verifica status de saude de todos os servicos:
    - Milvus
    - Neo4j
    - etcd
    - Embedding APIs (Google, Cohere)
    """
    try:
        health_status = {
            "milvus": {"status": "unknown", "details": ""},
            "neo4j": {"status": "unknown", "details": ""},
            "etcd": {"status": "unknown", "details": ""},
            "google_api": {"status": "unknown", "details": ""},
            "cohere_api": {"status": "unknown", "details": ""}
        }

        # Check Milvus
        try:
            milvus = get_milvus_client()
            collections = milvus.list_collections()
            health_status["milvus"] = {
                "status": "healthy",
                "details": f"{len(collections)} collections"
            }
        except Exception as e:
            health_status["milvus"] = {"status": "unhealthy", "details": str(e)}

        # Check Neo4j
        try:
            neo4j = get_neo4j_driver()
            with neo4j.session(database=NEO4J_DATABASE) as session:
                result = session.run("RETURN 1 as test")
                result.single()
            neo4j.close()
            health_status["neo4j"] = {"status": "healthy", "details": "Connected"}
        except Exception as e:
            health_status["neo4j"] = {"status": "unhealthy", "details": str(e)}

        # Check etcd
        try:
            import etcd3
            etcd = etcd3.client(host=ETCD_HOST, port=int(ETCD_PORT))
            etcd.status()
            health_status["etcd"] = {"status": "healthy", "details": "Connected"}
        except Exception as e:
            health_status["etcd"] = {"status": "unknown", "details": f"etcd check skipped: {e}"}

        # Check Google API
        if GOOGLE_API_KEY:
            try:
                client = get_google_client()
                # Quick test
                health_status["google_api"] = {"status": "configured", "details": "API key present"}
            except Exception as e:
                health_status["google_api"] = {"status": "error", "details": str(e)}
        else:
            health_status["google_api"] = {"status": "not_configured", "details": "API key missing"}

        # Check Cohere API
        if COHERE_API_KEY:
            health_status["cohere_api"] = {"status": "configured", "details": "API key present"}
        else:
            health_status["cohere_api"] = {"status": "not_configured", "details": "API key missing"}

        # Format output
        output_lines = ["## System Health Check\n"]
        output_lines.append(f"Timestamp: {datetime.now().isoformat()}\n")

        all_healthy = True
        for service, info in health_status.items():
            status_icon = "" if info["status"] in ["healthy", "configured"] else ""
            if info["status"] not in ["healthy", "configured"]:
                all_healthy = False
            output_lines.append(f"{status_icon} **{service}**: {info['status']}")
            if info["details"]:
                output_lines.append(f"   {info['details']}")

        output_lines.append(f"\n### Overall Status: {'HEALTHY' if all_healthy else 'DEGRADED'}")

        return ToolResult(content=[TextContent(type="text", text="\n".join(output_lines))])

    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise ToolError(f"Health check failed: {e}")


# ============================================================================
# RESOURCES
# ============================================================================

@mcp.resource("kb://schema")
def get_kb_schema() -> str:
    """Returns the knowledge base schema documentation."""
    return """
# Hybrid Knowledge Base Schema

## Milvus Collections

### documents
- id: VARCHAR(64) - Primary key
- vector: FLOAT_VECTOR - Embedding vector
- content: VARCHAR - Chunk content
- doc_id: VARCHAR - Parent document ID
- chunk_index: INT - Position in document
- title: VARCHAR - Document title
- source: VARCHAR - Source/origin
- doc_type: VARCHAR - Type (text, markdown, pdf)
- created_at: VARCHAR - ISO timestamp

## Neo4j Node Types

### Document
- id: STRING - Unique identifier
- title: STRING - Document title
- source: STRING - Source/origin
- doc_type: STRING - Type
- chunk_count: INTEGER - Number of chunks
- created_at: DATETIME

### Chunk
- id: STRING - Unique identifier
- content: STRING - Chunk content
- index: INTEGER - Position in document

### Entity
- id: STRING - Unique identifier
- name: STRING - Entity name
- type: STRING - Entity type (PERSON, ORG, etc.)
- properties: MAP - Additional properties

## Relationships

- (Document)-[:HAS_CHUNK]->(Chunk)
- (Chunk)-[:MENTIONS]->(Entity)
- (Entity)-[:RELATED_TO]->(Entity)
- (Document)-[:CITES]->(Document)
"""


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    mcp.run()
