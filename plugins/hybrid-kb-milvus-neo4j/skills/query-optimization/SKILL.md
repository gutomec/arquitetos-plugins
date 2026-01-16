# Skill: Query Optimization

Guia de otimizacao de queries vetoriais (Milvus) e Cypher (Neo4j) no sistema Hybrid Knowledge Base.

## Overview

Esta skill fornece tecnicas avancadas para otimizar queries no sistema hibrido, garantindo latencia baixa e alta precisao de retrieval.

## Milvus Query Optimization

### Index Selection

| Index Type | Best For | Build Time | Query Time | Memory |
|------------|----------|------------|------------|--------|
| *FLAT* | < 100K vectors | Nenhum | O(n) | 1x |
| *IVF_FLAT* | 100K - 1M | Rapido | O(n/nlist) | 1.1x |
| *IVF_SQ8* | 1M - 10M | Medio | O(n/nlist) | 0.25x |
| *HNSW* | 10M+ | Lento | O(log n) | 1.5x |
| *DiskANN* | > RAM | Muito lento | O(log n) | Disco |

### HNSW Configuration (Recomendado)

```python
index_params = {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {
        "M": 16,              # Conexoes por node (8-64)
        "efConstruction": 256  # Quality vs build time (64-512)
    }
}

search_params = {
    "metric_type": "COSINE",
    "params": {
        "ef": 64  # Query accuracy vs speed (16-512)
    }
}
```

### Tuning Guidelines

| Objetivo | M | efConstruction | ef |
|----------|---|----------------|-----|
| *Speed* | 8 | 128 | 32 |
| *Balance* | 16 | 256 | 64 |
| *Quality* | 32 | 512 | 128 |

### Filter Optimization

```python
# RUIM: Filtro apos busca vetorial
results = collection.search(
    data=[query_vector],
    limit=1000,  # Busca muitos, filtra depois
    output_fields=["*"]
)
filtered = [r for r in results if r["doc_type"] == "technical"]

# BOM: Filtro durante busca
results = collection.search(
    data=[query_vector],
    limit=10,
    filter='doc_type == "technical"',  # Filtro nativo
    output_fields=["content", "title"]
)
```

### Batch Queries

```python
# RUIM: Queries sequenciais
for query in queries:
    result = collection.search(data=[query_embed(query)], limit=5)

# BOM: Batch query
all_embeddings = [query_embed(q) for q in queries]
results = collection.search(
    data=all_embeddings,  # Batch
    limit=5
)
```

## Neo4j Cypher Optimization

### Query Patterns

#### Pattern 1: Use Indices

```cypher
-- RUIM: Scan completo
MATCH (d:Document)
WHERE d.title CONTAINS 'machine learning'
RETURN d

-- BOM: Com indice full-text
CALL db.index.fulltext.queryNodes('document_title', 'machine learning')
YIELD node
RETURN node

-- Criar indice
CREATE FULLTEXT INDEX document_title FOR (d:Document) ON EACH [d.title]
```

#### Pattern 2: Limite Traversal

```cypher
-- RUIM: Traversal ilimitado
MATCH (e1:Entity)-[*]-(e2:Entity)
WHERE e1.name = 'Hinton'
RETURN e2

-- BOM: Limite hops
MATCH (e1:Entity)-[*1..3]-(e2:Entity)
WHERE e1.name = 'Hinton'
RETURN e2
LIMIT 100
```

#### Pattern 3: Use PROFILE

```cypher
-- Analisar query
PROFILE
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE d.source = 'arxiv'
RETURN d.title, count(c)

-- Ver plano de execucao
-- Procure por: AllNodesScan (ruim), NodeIndexSeek (bom)
```

#### Pattern 4: Agregacoes Eficientes

```cypher
-- RUIM: Coleta e conta
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, collect(c) as chunks
RETURN d.title, size(chunks)

-- BOM: Count direto
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
RETURN d.title, count(c) as chunk_count
```

### APOC Optimizations

```cypher
-- Parallel execution
CALL apoc.cypher.parallel(
    'MATCH (d:Document) WHERE d.id IN $ids RETURN d',
    {ids: $doc_ids},
    'id'
)

-- Batch processing
CALL apoc.periodic.iterate(
    'MATCH (d:Document) RETURN d',
    'SET d.processed = true',
    {batchSize: 1000, parallel: true}
)
```

## Hybrid Query Optimization

### Parallel Execution

```python
import asyncio

async def hybrid_search(query: str) -> dict:
    """Executa vector e graph em paralelo."""

    # Execucao paralela
    vector_task = vector_search(query)
    graph_task = graph_search(query)

    vector_results, graph_results = await asyncio.gather(
        vector_task,
        graph_task
    )

    # Merge results
    return merge_and_rerank(vector_results, graph_results)
```

### Query Routing

```python
def route_query(query: str) -> str:
    """Roteia query para estrategia otima."""

    # Indicadores semanticos → vector
    semantic_indicators = ['similar', 'like', 'about', 'related']
    if any(ind in query.lower() for ind in semantic_indicators):
        return 'vector'

    # Indicadores estruturais → graph
    structural_indicators = ['who', 'when', 'authored', 'published']
    if any(ind in query.lower() for ind in structural_indicators):
        return 'graph'

    # Complexo → hybrid
    if len(query.split()) > 10 or '?' in query:
        return 'hybrid'

    return 'vector'  # default
```

### Result Fusion

```python
def reciprocal_rank_fusion(
    vector_results: list,
    graph_results: list,
    k: int = 60
) -> list:
    """Funde resultados usando RRF."""

    scores = {}

    # Score de vector results
    for rank, doc in enumerate(vector_results):
        doc_id = doc['id']
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    # Score de graph results
    for rank, doc in enumerate(graph_results):
        doc_id = doc['id']
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    # Sort by combined score
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

## Caching Strategies

### Query Cache

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_vector_search(query_hash: str) -> list:
    """Cache de resultados frequentes."""
    # Implementation
    pass

def search_with_cache(query: str) -> list:
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return cached_vector_search(query_hash)
```

### Embedding Cache

```python
# Redis cache para embeddings
import redis

redis_client = redis.Redis()

async def get_embedding_cached(text: str) -> list:
    cache_key = f"emb:{hashlib.md5(text.encode()).hexdigest()}"

    # Try cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Generate and cache
    embedding = await generate_embedding(text)
    redis_client.setex(cache_key, 3600, json.dumps(embedding))

    return embedding
```

## Performance Targets

| Operation | Target | Max Acceptable |
|-----------|--------|----------------|
| Vector search | < 50ms | 100ms |
| Graph simple | < 50ms | 100ms |
| Graph traversal | < 100ms | 200ms |
| Hybrid search | < 200ms | 500ms |
| Multi-hop (3) | < 300ms | 1000ms |

## Troubleshooting

### Query muito lenta

*Diagnostico*:
```python
# Milvus
from pymilvus import utility
utility.get_query_segment_info(collection_name)

# Neo4j
PROFILE <query>
```

*Solucoes*:
1. Verificar se indice esta construido
2. Reduzir top_k
3. Adicionar filtros mais restritivos
4. Particionar collection

### Resultados irrelevantes

*Diagnostico*:
- Verificar embedding provider
- Verificar task type (document vs query)
- Analisar chunks retornados

*Solucoes*:
1. Ajustar chunking strategy
2. Re-rankear com modelo cross-encoder
3. Adicionar filtros de metadata

### Memoria insuficiente

*Diagnostico*:
```python
collection.get_stats()  # Ver tamanho
```

*Solucoes*:
1. Usar quantizacao (SQ8, PQ)
2. Habilitar mmap
3. Particionar por data/tipo
4. Migrar para DiskANN

## Best Practices Summary

### DO

1. Use indices apropriados (HNSW para > 1M)
2. Filtre durante busca, nao depois
3. Execute vector/graph em paralelo
4. Cache queries e embeddings frequentes
5. Use PROFILE para analisar Cypher
6. Limite traversal no grafo

### DON'T

1. Nao faca full scan em collections grandes
2. Nao ignore indices no Neo4j
3. Nao retorne todos os campos
4. Nao use traversal ilimitado
5. Nao misture provedores de embedding
