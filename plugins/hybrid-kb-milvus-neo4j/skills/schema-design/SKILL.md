# Skill: Schema Design

Melhores praticas para design de schema no sistema Hybrid Knowledge Base com Milvus e Neo4j.

## Overview

Esta skill fornece orientacao para projetar schemas otimizados para o sistema GraphRAG hibrido, garantindo consistencia, performance e escalabilidade.

## Milvus Collection Design

### Collection Schema

```python
from pymilvus import CollectionSchema, FieldSchema, DataType

# Schema padrao para documentos
fields = [
    FieldSchema(
        name="id",
        dtype=DataType.VARCHAR,
        is_primary=True,
        max_length=64
    ),
    FieldSchema(
        name="vector",
        dtype=DataType.FLOAT_VECTOR,
        dim=768  # Google: 768, Cohere: 1024
    ),
    FieldSchema(
        name="content",
        dtype=DataType.VARCHAR,
        max_length=65535
    ),
    FieldSchema(
        name="doc_id",
        dtype=DataType.VARCHAR,
        max_length=64
    ),
    FieldSchema(
        name="chunk_index",
        dtype=DataType.INT64
    ),
    FieldSchema(
        name="title",
        dtype=DataType.VARCHAR,
        max_length=512
    ),
    FieldSchema(
        name="source",
        dtype=DataType.VARCHAR,
        max_length=256
    ),
    FieldSchema(
        name="doc_type",
        dtype=DataType.VARCHAR,
        max_length=32
    ),
    FieldSchema(
        name="created_at",
        dtype=DataType.VARCHAR,
        max_length=32
    )
]

schema = CollectionSchema(
    fields=fields,
    description="Knowledge base document chunks"
)
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Collection | lowercase_underscore | `documents`, `legal_docs` |
| Field | lowercase_underscore | `doc_id`, `chunk_index` |
| Index | collection_field_idx | `documents_vector_idx` |

### Partitioning Strategy

```python
# Particionar por tipo de documento
partitions = ["technical", "legal", "general"]

# Ou por periodo
partitions = ["2024_q1", "2024_q2", "2024_q3", "2024_q4"]

# Criar particoes
for partition in partitions:
    collection.create_partition(partition)

# Inserir em particao especifica
collection.insert(data, partition_name="technical")

# Buscar em particao especifica
collection.search(
    data=[query_vector],
    partition_names=["technical"],
    limit=10
)
```

## Neo4j Graph Design

### Node Types

```cypher
// Core nodes do sistema
(:Document {
    id: STRING,           // UUID ou hash
    title: STRING,        // Titulo do documento
    source: STRING,       // Origem (url, path, api)
    doc_type: STRING,     // Tipo (text, markdown, pdf)
    chunk_count: INTEGER, // Numero de chunks
    created_at: DATETIME, // Timestamp de criacao
    updated_at: DATETIME  // Timestamp de atualizacao
})

(:Chunk {
    id: STRING,           // doc_id + chunk_index
    content: STRING,      // Conteudo do chunk
    index: INTEGER,       // Posicao no documento
    token_count: INTEGER  // Contagem de tokens
})

(:Entity {
    id: STRING,           // UUID ou nome normalizado
    name: STRING,         // Nome da entidade
    type: STRING,         // PERSON, ORG, LOCATION, CONCEPT, TOPIC
    description: STRING,  // Descricao opcional
    aliases: [STRING]     // Nomes alternativos
})
```

### Relationship Types

```cypher
// Relacionamentos core
(Document)-[:HAS_CHUNK]->(Chunk)
(Chunk)-[:MENTIONS {count: INT, positions: [INT]}]->(Entity)
(Entity)-[:RELATED_TO {type: STRING, weight: FLOAT}]->(Entity)
(Document)-[:CITES]->(Document)
(Entity)-[:AUTHORED]->(Document)
(Entity)-[:WORKS_AT]->(Entity)
```

### Design Rules

| Rule | Recommendation | Reason |
|------|----------------|--------|
| Node types | 3-7 | Muitos reduz precisao, poucos perde distincoes |
| Relationship types | 5-15 | Balance entre expressividade e complexidade |
| Properties | Tipadas | Evita erros de query |
| IDs | UUID ou hash | Unicidade garantida |

## Indices e Constraints

### Neo4j Indices

```cypher
// Constraint de unicidade (cria indice automaticamente)
CREATE CONSTRAINT document_id FOR (d:Document) REQUIRE d.id IS UNIQUE
CREATE CONSTRAINT entity_id FOR (e:Entity) REQUIRE e.id IS UNIQUE
CREATE CONSTRAINT chunk_id FOR (c:Chunk) REQUIRE c.id IS UNIQUE

// Indices de busca
CREATE INDEX document_source FOR (d:Document) ON (d.source)
CREATE INDEX document_type FOR (d:Document) ON (d.doc_type)
CREATE INDEX entity_type FOR (e:Entity) ON (e.type)
CREATE INDEX entity_name FOR (e:Entity) ON (e.name)

// Indice full-text
CREATE FULLTEXT INDEX document_content FOR (d:Document) ON EACH [d.title]
CREATE FULLTEXT INDEX entity_search FOR (e:Entity) ON EACH [e.name, e.description]

// Indice vetorial (se armazenando embeddings no Neo4j)
CREATE VECTOR INDEX chunk_embeddings FOR (c:Chunk) ON c.embedding
OPTIONS {indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
}}
```

### Milvus Indices

```python
# Criar indice vetorial
index_params = {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {"M": 16, "efConstruction": 256}
}

collection.create_index(
    field_name="vector",
    index_params=index_params
)

# Criar indices escalares para filtros frequentes
collection.create_index(
    field_name="doc_type",
    index_name="doc_type_idx"
)
```

## Data Modeling Patterns

### Pattern 1: Document-Centric

```
                    ┌──────────────┐
                    │   Document   │
                    │  (metadata)  │
                    └──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │ Chunk 0 │  │ Chunk 1 │  │ Chunk 2 │
        └─────────┘  └─────────┘  └─────────┘
```

*Use quando*: Documentos sao a unidade principal de trabalho

### Pattern 2: Entity-Centric

```
        ┌──────────┐           ┌──────────┐
        │ Entity A │──RELATED──│ Entity B │
        └──────────┘           └──────────┘
              │                       │
              └───────┬───────────────┘
                      │
              ┌───────▼───────┐
              │   Mentions    │
              │ (in Chunks)   │
              └───────────────┘
```

*Use quando*: Foco em relacoes entre entidades

### Pattern 3: Topic-Centric

```
                    ┌───────────┐
                    │   Topic   │
                    └───────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │   Doc 1  │  │   Doc 2  │  │   Doc 3  │
      └──────────┘  └──────────┘  └──────────┘
```

*Use quando*: Organizacao tematica e prioritaria

## Sync Strategy

### Milvus-Neo4j Synchronization

```python
# Pattern: Armazenar mesmos IDs em ambos
doc_id = hashlib.md5(content[:100].encode()).hexdigest()
chunk_id = f"{doc_id}_{chunk_index}"

# Milvus: chunk_id como primary key
milvus_data = {
    "id": chunk_id,
    "vector": embedding,
    "doc_id": doc_id,
    ...
}

# Neo4j: mesmo chunk_id
cypher = """
MERGE (c:Chunk {id: $chunk_id})
SET c.content = $content
WITH c
MATCH (d:Document {id: $doc_id})
MERGE (d)-[:HAS_CHUNK]->(c)
"""
```

### Consistency Check

```python
def validate_sync() -> dict:
    """Verifica sincronizacao entre Milvus e Neo4j."""

    # IDs no Milvus
    milvus_ids = set(
        r["doc_id"] for r in
        collection.query(filter="", output_fields=["doc_id"])
    )

    # IDs no Neo4j
    with neo4j.session() as session:
        result = session.run("MATCH (d:Document) RETURN d.id")
        neo4j_ids = set(r["d.id"] for r in result)

    return {
        "milvus_only": milvus_ids - neo4j_ids,
        "neo4j_only": neo4j_ids - milvus_ids,
        "synced": milvus_ids & neo4j_ids
    }
```

## Best Practices

### DO

1. *Planeje antes de implementar*
   - Defina node/relationship types antes de ingerir
   - Considere queries mais frequentes

2. *Use IDs consistentes*
   - Mesmo ID em Milvus e Neo4j
   - UUIDs ou hashes deterministicos

3. *Crie indices proativamente*
   - Em properties usadas em WHERE/filtros
   - Em properties de join

4. *Documente o schema*
   - Mantenha documentacao atualizada
   - Inclua exemplos de queries

5. *Versione o schema*
   - Use migrations para mudancas
   - Mantenha compatibilidade retroativa

### DON'T

1. *Nao crie node types demais*
   - 3-7 e o ideal
   - Consolide tipos similares

2. *Nao armazene dados redundantes*
   - Embeddings no Milvus, nao no Neo4j
   - Metadados estruturados no Neo4j

3. *Nao ignore cardinalidade*
   - Relationships 1:N vs N:M afetam queries
   - Indices dependem de cardinalidade

4. *Nao misture ambientes*
   - Dev, staging, prod devem ter schemas identicos
   - Use migrations consistentes

## Migration Examples

### Adding a New Field

```python
# Milvus: Adicionar campo requer recrear collection
# 1. Backup dados existentes
# 2. Criar nova collection com schema atualizado
# 3. Migrar dados

# Neo4j: Mais flexivel
"""
MATCH (d:Document)
WHERE d.new_field IS NULL
SET d.new_field = 'default_value'
"""
```

### Renaming a Relationship

```cypher
// Neo4j: Criar nova e remover antiga
MATCH (d:Document)-[old:HAS_CHUNK]->(c:Chunk)
MERGE (d)-[new:CONTAINS_CHUNK]->(c)
SET new = old
DELETE old
```

## Template: Complete Schema

```python
# schema.py - Schema completo do sistema

MILVUS_COLLECTIONS = {
    "documents": {
        "fields": [...],
        "index": {"type": "HNSW", "metric": "COSINE"},
        "partitions": ["technical", "legal", "general"]
    }
}

NEO4J_SCHEMA = {
    "nodes": ["Document", "Chunk", "Entity"],
    "relationships": ["HAS_CHUNK", "MENTIONS", "RELATED_TO", "CITES"],
    "constraints": [
        "CREATE CONSTRAINT document_id FOR (d:Document) REQUIRE d.id IS UNIQUE",
        "CREATE CONSTRAINT chunk_id FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT entity_id FOR (e:Entity) REQUIRE e.id IS UNIQUE"
    ],
    "indices": [
        "CREATE INDEX document_source FOR (d:Document) ON (d.source)",
        "CREATE INDEX entity_type FOR (e:Entity) ON (e.type)"
    ]
}
```
