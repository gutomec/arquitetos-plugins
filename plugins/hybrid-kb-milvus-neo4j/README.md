# Hybrid Knowledge Base Plugin

Sistema GraphRAG hibrido de classe empresarial com Milvus e Neo4j para bases de conhecimento.

## Features

- *Vector Search*: Busca semantica com Milvus usando embeddings Google/Cohere
- *Graph Search*: Queries Cypher no Neo4j com suporte a APOC
- *Hybrid Search*: Combina vector + graph para GraphRAG completo
- *Multi-hop Reasoning*: Travessia multi-hop para raciocinio complexo
- *Entity Extraction*: Construcao automatica de grafo de conhecimento

## Stack

| Component | Technology |
|-----------|------------|
| Vector DB | Milvus 2.4+ |
| Graph DB | Neo4j 5.x + APOC |
| Metadata | etcd |
| Embeddings | Google text-embedding-004, Cohere embed-v4 |
| MCP Server | FastMCP 2.0 |

## Installation

```bash
# Add marketplace (once)
/plugin marketplace add gutomec/arquitetos-plugins

# Install plugin
/plugin install hybrid-kb-milvus-neo4j@arquitetos-plugins
```

## Configuration

Set environment variables:

```bash
# Required
export GOOGLE_API_KEY="your-google-api-key"
export COHERE_API_KEY="your-cohere-api-key"
export NEO4J_PASS="your-neo4j-password"

# Optional (defaults shown)
export MILVUS_URI="http://localhost:19530"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_DATABASE="neo4j"
```

## Quick Start with Docker

```bash
# Start infrastructure
cd mcp-server
docker-compose up -d

# Wait for services
docker-compose ps
```

## Commands

| Command | Description |
|---------|-------------|
| `/ingerir` | Ingere documentos na base de conhecimento |
| `/buscar` | Executa buscas hibridas GraphRAG |
| `/schema` | Analisa schema do sistema |
| `/health` | Verifica saude dos servicos |

## Agents

| Agent | Role |
|-------|------|
| kb-orchestrator | Coordena pipeline de ingestao e busca |
| ingestion-agent | Processa e indexa documentos |
| retrieval-agent | Executa buscas otimizadas |
| schema-analyst | Analisa e valida estruturas |
| health-monitor | Monitora saude do sistema |

## MCP Tools

### Ingestion
- `ingest_document` - Processa documento individual
- `ingest_batch` - Processamento em lote
- `build_knowledge_graph` - Construcao de grafo

### Retrieval
- `vector_search` - Busca semantica em Milvus
- `graph_search` - Query Cypher em Neo4j
- `hybrid_search` - Busca combinada GraphRAG
- `multi_hop_reasoning` - Travessia multi-hop

### Schema Analysis
- `analyze_schema` - Analise do schema Neo4j
- `analyze_collections` - Estatisticas do Milvus
- `validate_consistency` - Validacao cross-database
- `health_check` - Status de saude

## Skills

- *chunking-strategies*: Guia de estrategias de chunking
- *embedding-selection*: Como escolher entre Google e Cohere
- *query-optimization*: Otimizacao de queries
- *schema-design*: Melhores praticas de schema

## Performance Targets

| Operation | Target |
|-----------|--------|
| Vector search | < 50ms |
| Graph query | < 100ms |
| Hybrid search | < 200ms |
| Multi-hop (3 hops) | < 500ms |

## License

MIT

## Author

Arquitetos de Prompt
