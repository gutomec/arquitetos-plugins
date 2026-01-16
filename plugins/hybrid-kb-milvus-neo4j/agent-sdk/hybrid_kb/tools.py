"""
Hybrid KB Tools - Agent SDK
===========================
Tools para integração com Milvus e Neo4j.
"""

from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
from pymilvus import MilvusClient
import google.generativeai as genai
import cohere
import hashlib
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """Resultado padronizado de tool."""
    success: bool
    data: Any = None
    error: Optional[str] = None


class HybridKBTools:
    """
    Tools para operações no sistema Hybrid KB.

    Uso:
        tools = HybridKBTools()
        result = await tools.vector_search("machine learning", top_k=5)
    """

    def __init__(
        self,
        milvus_uri: str = None,
        neo4j_uri: str = None,
        neo4j_user: str = None,
        neo4j_pass: str = None,
        google_api_key: str = None,
        cohere_api_key: str = None
    ):
        # Configuração via parâmetros ou variáveis de ambiente
        self.milvus_uri = milvus_uri or os.getenv("MILVUS_URI", "http://localhost:19530")
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_pass = neo4j_pass or os.getenv("NEO4J_PASS", "password")
        self.neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY", "")
        self.cohere_api_key = cohere_api_key or os.getenv("COHERE_API_KEY", "")

        # Dimensões de embedding
        self.EMBEDDING_DIM_GOOGLE = 768
        self.EMBEDDING_DIM_COHERE = 1024

        # Clientes (inicializados sob demanda)
        self._milvus_client = None
        self._neo4j_driver = None
        self._cohere_client = None

    # =========================================================================
    # CONNECTION MANAGEMENT
    # =========================================================================

    @property
    def milvus(self) -> MilvusClient:
        """Get or create Milvus client."""
        if self._milvus_client is None:
            self._milvus_client = MilvusClient(uri=self.milvus_uri)
        return self._milvus_client

    @property
    def neo4j(self):
        """Get or create Neo4j driver."""
        if self._neo4j_driver is None:
            self._neo4j_driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_pass)
            )
        return self._neo4j_driver

    def close(self):
        """Close all connections."""
        if self._neo4j_driver:
            self._neo4j_driver.close()

    # =========================================================================
    # EMBEDDING FUNCTIONS
    # =========================================================================

    async def generate_embedding(
        self,
        text: str,
        provider: Literal["google", "cohere"] = "google"
    ) -> List[float]:
        """Generate embedding using specified provider."""
        try:
            if provider == "google":
                genai.configure(api_key=self.google_api_key)
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                return result['embedding']
            else:
                if self._cohere_client is None:
                    self._cohere_client = cohere.Client(self.cohere_api_key)
                response = self._cohere_client.embed(
                    texts=[text],
                    model="embed-english-v3.0",
                    input_type="search_document"
                )
                return response.embeddings[0]
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    # =========================================================================
    # INGESTION TOOLS
    # =========================================================================

    async def ingest_document(
        self,
        content: str,
        metadata: dict = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        embedding_provider: Literal["google", "cohere"] = "google",
        collection_name: str = "documents"
    ) -> ToolResult:
        """
        Ingest a document into the hybrid knowledge base.

        Args:
            content: Document content to ingest
            metadata: Optional metadata dict
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
            embedding_provider: google or cohere
            collection_name: Milvus collection name
        """
        try:
            # Generate document ID
            doc_id = hashlib.md5(content[:500].encode()).hexdigest()[:12]

            # Chunk the document
            chunks = self._semantic_chunk(content, chunk_size, chunk_overlap)

            # Generate embeddings and prepare data
            vectors = []
            for i, chunk in enumerate(chunks):
                embedding = await self.generate_embedding(chunk, embedding_provider)
                vectors.append({
                    "id": f"{doc_id}_{i}",
                    "vector": embedding,
                    "text": chunk,
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "metadata": json.dumps(metadata or {})
                })

            # Insert into Milvus
            self._ensure_collection(collection_name, embedding_provider)
            self.milvus.insert(collection_name=collection_name, data=vectors)

            # Create document node in Neo4j
            with self.neo4j.session(database=self.neo4j_database) as session:
                session.run("""
                    MERGE (d:Document {id: $doc_id})
                    SET d.chunk_count = $chunk_count,
                        d.created_at = datetime(),
                        d.metadata = $metadata
                """, doc_id=doc_id, chunk_count=len(chunks),
                    metadata=json.dumps(metadata or {}))

            return ToolResult(
                success=True,
                data={
                    "doc_id": doc_id,
                    "chunks_created": len(chunks),
                    "collection": collection_name,
                    "embedding_provider": embedding_provider
                }
            )
        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            return ToolResult(success=False, error=str(e))

    async def build_knowledge_graph(
        self,
        content: str,
        doc_id: str = None,
        entity_types: List[str] = None
    ) -> ToolResult:
        """
        Extract entities and relationships from content and build knowledge graph.
        """
        try:
            if entity_types is None:
                entity_types = ["Person", "Organization", "Document", "Topic", "Concept"]

            if doc_id is None:
                doc_id = hashlib.md5(content[:500].encode()).hexdigest()[:12]

            # Extract entities using simple pattern matching
            # In production, use an LLM for better extraction
            entities = self._extract_entities(content, entity_types)

            # Create nodes and relationships in Neo4j
            with self.neo4j.session(database=self.neo4j_database) as session:
                for entity in entities:
                    session.run(f"""
                        MERGE (e:{entity['type']} {{name: $name}})
                        WITH e
                        MATCH (d:Document {{id: $doc_id}})
                        MERGE (d)-[:MENTIONS]->(e)
                    """, name=entity['name'], doc_id=doc_id)

            return ToolResult(
                success=True,
                data={
                    "doc_id": doc_id,
                    "entities_created": len(entities),
                    "entity_types": list(set(e['type'] for e in entities))
                }
            )
        except Exception as e:
            logger.error(f"Knowledge graph build error: {e}")
            return ToolResult(success=False, error=str(e))

    # =========================================================================
    # RETRIEVAL TOOLS
    # =========================================================================

    async def vector_search(
        self,
        query: str,
        top_k: int = 5,
        collection_name: str = "documents",
        embedding_provider: Literal["google", "cohere"] = "google",
        filter_expr: str = None
    ) -> ToolResult:
        """
        Semantic vector search in Milvus.
        """
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query, embedding_provider)

            # Search in Milvus
            results = self.milvus.search(
                collection_name=collection_name,
                data=[query_embedding],
                limit=top_k,
                filter=filter_expr,
                output_fields=["text", "doc_id", "chunk_index", "metadata"]
            )

            # Format results
            formatted = []
            for hits in results:
                for hit in hits:
                    formatted.append({
                        "id": hit.get("id"),
                        "score": hit.get("distance"),
                        "text": hit.get("entity", {}).get("text", ""),
                        "doc_id": hit.get("entity", {}).get("doc_id", ""),
                        "metadata": hit.get("entity", {}).get("metadata", "{}")
                    })

            return ToolResult(success=True, data={"results": formatted, "count": len(formatted)})
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return ToolResult(success=False, error=str(e))

    async def graph_search(
        self,
        cypher_query: str,
        parameters: dict = None
    ) -> ToolResult:
        """
        Execute Cypher query on Neo4j.
        """
        try:
            with self.neo4j.session(database=self.neo4j_database) as session:
                result = session.run(cypher_query, parameters or {})
                records = [dict(record) for record in result]

            return ToolResult(success=True, data={"results": records, "count": len(records)})
        except Exception as e:
            logger.error(f"Graph search error: {e}")
            return ToolResult(success=False, error=str(e))

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        collection_name: str = "documents",
        embedding_provider: Literal["google", "cohere"] = "google",
        graph_depth: int = 2
    ) -> ToolResult:
        """
        Combined vector + graph search for GraphRAG.
        """
        try:
            # 1. Vector search for semantic matches
            vector_result = await self.vector_search(
                query, top_k, collection_name, embedding_provider
            )

            if not vector_result.success:
                return vector_result

            vector_docs = vector_result.data.get("results", [])
            doc_ids = list(set(d.get("doc_id") for d in vector_docs if d.get("doc_id")))

            # 2. Graph traversal for related entities
            graph_context = []
            if doc_ids:
                graph_result = await self.graph_search(f"""
                    MATCH (d:Document)-[:MENTIONS]->(e)
                    WHERE d.id IN $doc_ids
                    WITH e, count(d) as mentions
                    ORDER BY mentions DESC
                    LIMIT 10
                    MATCH (e)-[r]-(related)
                    RETURN e.name as entity, labels(e) as types,
                           type(r) as relationship, related.name as related_entity
                """, {"doc_ids": doc_ids})

                if graph_result.success:
                    graph_context = graph_result.data.get("results", [])

            return ToolResult(
                success=True,
                data={
                    "vector_results": vector_docs,
                    "graph_context": graph_context,
                    "doc_ids": doc_ids,
                    "strategy": "hybrid"
                }
            )
        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            return ToolResult(success=False, error=str(e))

    async def multi_hop_reasoning(
        self,
        start_entity: str,
        question: str,
        max_hops: int = 3
    ) -> ToolResult:
        """
        Multi-hop graph traversal for complex reasoning.
        """
        try:
            result = await self.graph_search(f"""
                MATCH path = (start {{name: $entity}})-[*1..{max_hops}]-(end)
                WITH path, relationships(path) as rels, nodes(path) as nodes
                UNWIND nodes as n
                WITH DISTINCT n, rels, length(path) as path_length
                RETURN n.name as entity, labels(n) as types, path_length
                ORDER BY path_length
                LIMIT 20
            """, {"entity": start_entity})

            return ToolResult(
                success=True,
                data={
                    "start_entity": start_entity,
                    "paths": result.data.get("results", []) if result.success else [],
                    "max_hops": max_hops
                }
            )
        except Exception as e:
            logger.error(f"Multi-hop reasoning error: {e}")
            return ToolResult(success=False, error=str(e))

    # =========================================================================
    # SCHEMA TOOLS
    # =========================================================================

    async def analyze_schema(self) -> ToolResult:
        """Analyze Neo4j schema - node types, relationships, properties."""
        try:
            with self.neo4j.session(database=self.neo4j_database) as session:
                # Get node labels
                labels = session.run("CALL db.labels()").value()

                # Get relationship types
                rel_types = session.run("CALL db.relationshipTypes()").value()

                # Get property keys
                props = session.run("CALL db.propertyKeys()").value()

                # Get schema visualization
                schema_viz = session.run("""
                    CALL db.schema.visualization()
                """).data()

            return ToolResult(
                success=True,
                data={
                    "node_labels": labels,
                    "relationship_types": rel_types,
                    "property_keys": props,
                    "schema_visualization": schema_viz
                }
            )
        except Exception as e:
            logger.error(f"Schema analysis error: {e}")
            return ToolResult(success=False, error=str(e))

    async def analyze_collections(self) -> ToolResult:
        """Analyze Milvus collections - stats, indexes, fields."""
        try:
            collections = self.milvus.list_collections()

            collection_stats = []
            for coll_name in collections:
                try:
                    stats = self.milvus.get_collection_stats(coll_name)
                    collection_stats.append({
                        "name": coll_name,
                        "row_count": stats.get("row_count", 0),
                        "stats": stats
                    })
                except Exception:
                    collection_stats.append({"name": coll_name, "error": "Could not get stats"})

            return ToolResult(
                success=True,
                data={
                    "collections": collection_stats,
                    "total_collections": len(collections)
                }
            )
        except Exception as e:
            logger.error(f"Collection analysis error: {e}")
            return ToolResult(success=False, error=str(e))

    async def health_check(self) -> ToolResult:
        """Check health of all system components."""
        try:
            health = {
                "milvus": {"status": "unknown"},
                "neo4j": {"status": "unknown"},
                "embeddings": {"google": "unknown", "cohere": "unknown"}
            }

            # Check Milvus
            try:
                self.milvus.list_collections()
                health["milvus"] = {"status": "healthy", "uri": self.milvus_uri}
            except Exception as e:
                health["milvus"] = {"status": "unhealthy", "error": str(e)}

            # Check Neo4j
            try:
                with self.neo4j.session(database=self.neo4j_database) as session:
                    session.run("RETURN 1")
                health["neo4j"] = {"status": "healthy", "uri": self.neo4j_uri}
            except Exception as e:
                health["neo4j"] = {"status": "unhealthy", "error": str(e)}

            # Check embeddings
            if self.google_api_key:
                health["embeddings"]["google"] = "configured"
            if self.cohere_api_key:
                health["embeddings"]["cohere"] = "configured"

            all_healthy = (
                health["milvus"]["status"] == "healthy" and
                health["neo4j"]["status"] == "healthy"
            )

            return ToolResult(
                success=True,
                data={
                    "overall": "healthy" if all_healthy else "degraded",
                    "components": health,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return ToolResult(success=False, error=str(e))

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _semantic_chunk(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into semantic chunks."""
        # Simple chunking by sentences
        sentences = text.replace('\n', ' ').split('. ')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
                current_chunk = overlap_text + sentence + ". "

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _ensure_collection(self, collection_name: str, provider: str):
        """Ensure Milvus collection exists with correct schema."""
        dim = self.EMBEDDING_DIM_GOOGLE if provider == "google" else self.EMBEDDING_DIM_COHERE

        if not self.milvus.has_collection(collection_name):
            self.milvus.create_collection(
                collection_name=collection_name,
                dimension=dim,
                metric_type="COSINE",
                auto_id=False
            )

    def _extract_entities(self, text: str, entity_types: List[str]) -> List[dict]:
        """Simple entity extraction. Replace with LLM-based extraction in production."""
        # This is a placeholder - in production use NER or LLM
        entities = []
        words = text.split()

        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2 and word.isalpha():
                entity_type = entity_types[i % len(entity_types)]
                entities.append({"name": word, "type": entity_type})

        return entities[:20]  # Limit to 20 entities


# Tool definitions for Claude API
TOOL_DEFINITIONS = [
    {
        "name": "ingest_document",
        "description": "Ingest a document into the hybrid knowledge base. Chunks the content, generates embeddings, stores in Milvus, and creates nodes in Neo4j.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Document content to ingest"},
                "metadata": {"type": "object", "description": "Optional metadata"},
                "chunk_size": {"type": "integer", "default": 512},
                "embedding_provider": {"type": "string", "enum": ["google", "cohere"], "default": "google"}
            },
            "required": ["content"]
        }
    },
    {
        "name": "vector_search",
        "description": "Semantic vector search in the knowledge base using embeddings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "default": 5},
                "embedding_provider": {"type": "string", "enum": ["google", "cohere"], "default": "google"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "graph_search",
        "description": "Execute Cypher query on the Neo4j knowledge graph.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cypher_query": {"type": "string", "description": "Cypher query to execute"},
                "parameters": {"type": "object", "description": "Query parameters"}
            },
            "required": ["cypher_query"]
        }
    },
    {
        "name": "hybrid_search",
        "description": "Combined vector + graph search for GraphRAG. First finds semantically similar documents, then enriches with graph context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "default": 5},
                "graph_depth": {"type": "integer", "default": 2}
            },
            "required": ["query"]
        }
    },
    {
        "name": "multi_hop_reasoning",
        "description": "Multi-hop graph traversal for complex reasoning questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_entity": {"type": "string", "description": "Starting entity name"},
                "question": {"type": "string", "description": "Question to answer"},
                "max_hops": {"type": "integer", "default": 3}
            },
            "required": ["start_entity", "question"]
        }
    },
    {
        "name": "analyze_schema",
        "description": "Analyze Neo4j knowledge graph schema - node types, relationships, properties.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "analyze_collections",
        "description": "Analyze Milvus vector collections - stats, indexes, document counts.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "health_check",
        "description": "Check health status of all system components (Milvus, Neo4j, embeddings).",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "build_knowledge_graph",
        "description": "Extract entities and relationships from content and build knowledge graph in Neo4j.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to extract entities from"},
                "doc_id": {"type": "string", "description": "Optional document ID"},
                "entity_types": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["content"]
        }
    }
]
