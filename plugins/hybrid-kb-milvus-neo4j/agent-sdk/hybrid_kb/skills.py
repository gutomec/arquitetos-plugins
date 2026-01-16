"""
Hybrid KB Skills - Knowledge Modules
====================================
Skills contendo conhecimento especializado para os agentes.
"""


class Skills:
    """
    Conhecimento especializado para agentes do Hybrid KB.

    Uso:
        skills = Skills()
        chunking_guide = skills.chunking_strategies()
    """

    @staticmethod
    def chunking_strategies() -> str:
        """Estratégias de chunking semântico para documentos."""
        return """
# Chunking Strategies for Hybrid KB

## Overview
Semantic chunking preserves meaning by splitting at natural boundaries rather than arbitrary character limits.

## Recommended Approaches

### 1. Sentence-Based Chunking
- Split on sentence boundaries (., !, ?)
- Preserve paragraph context
- Target: 256-512 tokens per chunk
- Overlap: 10-20% for context continuity

### 2. Semantic Chunking
- Use embedding similarity to find natural breakpoints
- Keep semantically related content together
- Best for: Technical documents, research papers

### 3. Document-Aware Chunking
- Respect document structure (headers, sections)
- Maintain hierarchy information in metadata
- Best for: Structured documents, manuals

## Configuration Guidelines

| Document Type | Chunk Size | Overlap | Strategy |
|--------------|------------|---------|----------|
| Legal documents | 512 chars | 20% | Sentence-based |
| Technical docs | 1024 chars | 15% | Document-aware |
| Articles | 768 chars | 10% | Semantic |
| Code | 256 chars | 25% | Syntax-aware |

## Best Practices

1. **Always include metadata**: doc_id, chunk_index, source
2. **Preserve context**: Include section headers in each chunk
3. **Handle tables**: Keep tables as single chunks when possible
4. **Code blocks**: Never split code blocks mid-function
5. **Test retrieval**: Validate chunk quality with sample queries
"""

    @staticmethod
    def embedding_selection() -> str:
        """Guia de seleção de providers de embedding."""
        return """
# Embedding Provider Selection Guide

## Available Providers

### Google (text-embedding-004)
- **Dimensions**: 768
- **Strengths**: Fast, good multilingual support, free tier available
- **Best for**: General purpose, Portuguese content, cost-sensitive deployments
- **Latency**: ~50ms per request
- **Rate limits**: 60 requests/minute (free tier)

### Cohere (embed-v4)
- **Dimensions**: 1024
- **Strengths**: Higher quality, better for technical content
- **Best for**: Enterprise deployments, English-heavy content
- **Latency**: ~100ms per request
- **Rate limits**: Based on plan

## Selection Matrix

| Use Case | Recommended Provider | Reason |
|----------|---------------------|--------|
| Portuguese legal docs | Google | Better multilingual support |
| Technical papers | Cohere | Higher precision |
| Mixed language | Google | Balanced performance |
| High volume (>1M docs) | Google | Cost efficiency |
| Quality-critical | Cohere | Slightly better accuracy |

## Hybrid Approach

For best results, consider:
1. Use Google for initial ingestion (cost)
2. Use Cohere for query embeddings (quality)
3. Store both embeddings if budget allows

## Performance Tips

1. **Batch embeddings**: Process 100 texts at once
2. **Cache embeddings**: Store for repeated queries
3. **Async processing**: Don't block on API calls
4. **Fallback strategy**: If one provider fails, use the other
"""

    @staticmethod
    def query_optimization() -> str:
        """Otimização de queries para GraphRAG."""
        return """
# Query Optimization for Hybrid Search

## Query Routing Decision Matrix

| Query Pattern | Route | Example |
|--------------|-------|---------|
| "similar to", "like", "about" | vector_search | "documents similar to machine learning" |
| "who", "when", "where" | graph_search | "who authored the paper on NLP" |
| "how many", "count" | graph_search | "how many papers cite this author" |
| Complex, multi-entity | hybrid_search | "papers about ML that cite Bengio's work" |
| Relationship-focused | graph_search | "connection between X and Y" |

## Vector Search Optimization

1. **Top-K Selection**:
   - Start with k=5 for precision
   - Increase to k=10-20 for recall
   - Use k=3 for focused answers

2. **Filter Expressions**:
   - Filter by doc_type: `doc_type == "paper"`
   - Filter by date: `created_at > 2023`
   - Combine: `doc_type == "paper" AND year >= 2023`

3. **Similarity Thresholds**:
   - > 0.8: Highly relevant
   - 0.6-0.8: Relevant
   - < 0.6: Consider excluding

## Graph Search Optimization

1. **Cypher Best Practices**:
   - Use indexes on frequently queried properties
   - Limit traversal depth (max 3-4 hops)
   - Use APOC procedures for complex operations

2. **Common Patterns**:
   ```cypher
   // Find related entities
   MATCH (d:Document)-[:MENTIONS]->(e:Entity)
   WHERE d.id IN $doc_ids
   RETURN e.name, count(*) as mentions

   // Multi-hop traversal
   MATCH path = (start)-[*1..3]-(end)
   WHERE start.name = $entity
   RETURN path LIMIT 10
   ```

## Hybrid Search Strategy

1. **Sequential**: Vector first, then graph enrichment
2. **Parallel**: Both searches simultaneously, merge results
3. **Iterative**: Start with vector, use graph for refinement

## Performance Targets

| Metric | Target | Action if Exceeded |
|--------|--------|-------------------|
| Vector search | < 50ms | Check index, reduce k |
| Graph traversal | < 100ms | Add indexes, limit depth |
| Hybrid total | < 200ms | Parallelize searches |
| End-to-end | < 2s | Cache common queries |
"""

    @staticmethod
    def schema_design() -> str:
        """Design de schema para Neo4j knowledge graph."""
        return """
# Knowledge Graph Schema Design

## Recommended Node Types (3-7 types)

### Core Types
1. **Document**: Source documents, papers, articles
   - Properties: id, title, content_hash, created_at, source_type

2. **Entity**: Named entities extracted from documents
   - Properties: name, type, confidence, first_seen

3. **Topic**: Thematic categories
   - Properties: name, description, parent_topic

4. **Chunk**: Document chunks stored in Milvus
   - Properties: id, doc_id, milvus_id, chunk_index

### Domain-Specific (add as needed)
- Person, Organization, Location (for NER)
- Concept, Technology, Method (for technical docs)
- Case, Law, Court (for legal docs)

## Recommended Relationships (5-15 types)

### Document Relationships
- `(Document)-[:MENTIONS]->(Entity)`
- `(Document)-[:DISCUSSES]->(Topic)`
- `(Document)-[:CITES]->(Document)`
- `(Document)-[:HAS_CHUNK]->(Chunk)`

### Entity Relationships
- `(Entity)-[:RELATED_TO]->(Entity)`
- `(Person)-[:WORKS_AT]->(Organization)`
- `(Person)-[:AUTHORED]->(Document)`

### Hierarchical
- `(Topic)-[:SUBTOPIC_OF]->(Topic)`
- `(Entity)-[:INSTANCE_OF]->(Concept)`

## Index Strategy

```cypher
-- Essential indexes
CREATE INDEX doc_id FOR (d:Document) ON (d.id);
CREATE INDEX entity_name FOR (e:Entity) ON (e.name);
CREATE INDEX chunk_milvus FOR (c:Chunk) ON (c.milvus_id);

-- Full-text for search
CREATE FULLTEXT INDEX doc_content FOR (d:Document) ON EACH [d.title, d.summary];

-- Vector index (Neo4j 5.x+)
CREATE VECTOR INDEX entity_embedding FOR (e:Entity) ON e.embedding
OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}};
```

## Schema Validation

### Quality Metrics
- Entity resolution accuracy > 85%
- Relationship extraction precision > 80%
- No orphan nodes (all connected)
- No duplicate entities (merge on name+type)

### Health Checks
```cypher
-- Find orphan nodes
MATCH (n) WHERE NOT (n)--() RETURN count(n);

-- Find duplicate entities
MATCH (e:Entity)
WITH e.name as name, count(*) as count
WHERE count > 1
RETURN name, count;

-- Check relationship distribution
MATCH ()-[r]->()
RETURN type(r), count(*) as count
ORDER BY count DESC;
```

## Best Practices

1. **Start simple**: 3-4 node types, 5-7 relationships
2. **Iterate based on queries**: Add types as needed
3. **Document decisions**: Keep ADR for schema changes
4. **Version your schema**: Track changes over time
5. **Test with real queries**: Validate schema supports use cases
"""

    @staticmethod
    def graphrag_patterns() -> str:
        """Padrões e melhores práticas para GraphRAG."""
        return """
# GraphRAG Best Practices

## Architecture Overview

```
Query → Router → [Vector | Graph | Hybrid] → Context Assembly → LLM → Response
```

## Query Routing

### Classification Rules
1. **Vector-only**: Semantic similarity, conceptual matching
   - "What documents discuss machine learning?"
   - "Find papers similar to this abstract"

2. **Graph-only**: Structural queries, relationships
   - "Who authored papers about NLP?"
   - "What topics are connected to deep learning?"

3. **Hybrid**: Complex reasoning, multi-hop
   - "Find papers about ML that cite authors from Stanford"
   - "What are the key concepts connecting X and Y?"

## Context Assembly

### Strategy 1: Sequential
```python
# 1. Vector search for initial context
vector_results = vector_search(query, top_k=5)

# 2. Extract doc_ids
doc_ids = [r.doc_id for r in vector_results]

# 3. Graph enrichment
graph_context = graph_search(doc_ids, depth=2)

# 4. Merge contexts
final_context = merge(vector_results, graph_context)
```

### Strategy 2: Parallel
```python
# Execute both searches in parallel
vector_task = asyncio.create_task(vector_search(query))
graph_task = asyncio.create_task(graph_search(query_entities))

vector_results, graph_results = await asyncio.gather(vector_task, graph_task)

# Merge with ranking
final_context = rank_and_merge(vector_results, graph_results)
```

## Self-Correction

### Grading Pipeline
1. **Relevance Grader**: Are retrieved docs relevant to query?
2. **Groundedness Grader**: Is the answer grounded in context?
3. **Answer Grader**: Does the answer address the question?

### Fallback Strategy
```python
result = hybrid_search(query)

if relevance_score < 0.6:
    # Reformulate query
    new_query = reformulate(query, result.context)
    result = hybrid_search(new_query)

if relevance_score < 0.4:
    # Expand search
    result = web_search_fallback(query)
```

## Performance Optimization

### Caching
- Cache frequent queries (TTL: 1 hour)
- Cache entity embeddings (TTL: 24 hours)
- Cache graph subgraphs (TTL: 1 hour)

### Batching
- Batch embedding requests (100 at a time)
- Batch graph writes (transaction batches)
- Batch Milvus inserts (1000 vectors)

### Monitoring
- Track query latency (p50, p95, p99)
- Monitor cache hit rates
- Alert on degraded components

## Common Pitfalls

1. **Over-retrieval**: Too many results dilute context
   - Solution: Use stricter thresholds, smaller top_k

2. **Under-retrieval**: Missing relevant information
   - Solution: Use hybrid search, increase top_k

3. **Entity resolution failures**: Duplicate or missed entities
   - Solution: Use better NER, implement merge logic

4. **Graph explosion**: Too many hops, too many relationships
   - Solution: Limit traversal depth, filter relationship types

5. **Stale data**: Vector and graph out of sync
   - Solution: Atomic updates, consistency validation
"""

    @classmethod
    def all(cls) -> dict:
        """Retorna todas as skills disponíveis."""
        return {
            "chunking_strategies": cls.chunking_strategies(),
            "embedding_selection": cls.embedding_selection(),
            "query_optimization": cls.query_optimization(),
            "schema_design": cls.schema_design(),
            "graphrag_patterns": cls.graphrag_patterns()
        }

    @classmethod
    def get(cls, skill_name: str) -> str:
        """Obtém uma skill específica por nome."""
        skills = cls.all()
        return skills.get(skill_name, f"Skill '{skill_name}' not found. Available: {list(skills.keys())}")
