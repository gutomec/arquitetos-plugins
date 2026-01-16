# Hybrid KB Agent SDK

Sistema multi-agente para GraphRAG com Milvus e Neo4j, usando Claude Agent SDK.

## Instalação

### Local (desenvolvimento)

```bash
cd agent-sdk
pip install -e .
```

### Docker (produção)

```bash
cd docker
cp .env.example .env
# Edite .env com suas credenciais

# Stack completa (Milvus + Neo4j + Agent)
docker compose -f docker-compose.full.yml up -d
```

## Uso

### CLI

```bash
# Buscar documentos
hybrid-kb search "documentos sobre machine learning"

# Ingerir documento
hybrid-kb ingest documento.txt

# Analisar schema
hybrid-kb analyze

# Verificar saúde
hybrid-kb health

# Modo interativo
hybrid-kb interactive

# Listar skills
hybrid-kb skills
```

### Python

```python
import asyncio
from hybrid_kb import HybridKBOrchestrator

async def main():
    # Inicializar orchestrator
    orchestrator = HybridKBOrchestrator(
        milvus_uri="http://localhost:19530",
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_pass="password"
    )

    # Ingerir documento
    result = await orchestrator.ingest(
        content="Conteúdo do documento...",
        metadata={"title": "Meu Documento"}
    )
    print(result)

    # Buscar
    result = await orchestrator.search("machine learning", strategy="hybrid")
    print(result)

    # Verificar saúde
    result = await orchestrator.health()
    print(result)

    orchestrator.close()

asyncio.run(main())
```

### Agentes Especializados

```python
from hybrid_kb import IngestionAgent, RetrievalAgent, HybridKBTools

# Usar agente diretamente
tools = HybridKBTools()
ingestion = IngestionAgent(tools=tools)

result = await ingestion.run("Processe este documento sobre IA...")
```

## Agentes

| Agente | Função |
|--------|--------|
| `IngestionAgent` | Processamento de documentos |
| `RetrievalAgent` | Busca e retrieval |
| `SchemaAnalystAgent` | Análise de schema |
| `HealthMonitorAgent` | Monitoramento |

## Skills

| Skill | Conteúdo |
|-------|----------|
| `chunking_strategies` | Estratégias de chunking semântico |
| `embedding_selection` | Guia de seleção de embeddings |
| `query_optimization` | Otimização de queries |
| `schema_design` | Design de schema Neo4j |
| `graphrag_patterns` | Padrões GraphRAG |

```python
from hybrid_kb import Skills

# Acessar skill
print(Skills.chunking_strategies())
```

## Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `ANTHROPIC_API_KEY` | API key do Claude | (obrigatório) |
| `MILVUS_URI` | URI do Milvus | `http://localhost:19530` |
| `NEO4J_URI` | URI do Neo4j | `bolt://localhost:7687` |
| `NEO4J_USER` | Usuário Neo4j | `neo4j` |
| `NEO4J_PASS` | Senha Neo4j | `password` |
| `GOOGLE_API_KEY` | API key Google | (opcional) |
| `COHERE_API_KEY` | API key Cohere | (opcional) |

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator                          │
│     Classifica intent e roteia para agente/tool         │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Ingestion   │  │   Retrieval   │  │    Schema     │
│     Agent     │  │     Agent     │  │    Analyst    │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    HybridKBTools                         │
│   - ingest_document    - vector_search                  │
│   - build_knowledge    - graph_search                   │
│     _graph             - hybrid_search                  │
│   - analyze_schema     - multi_hop_reasoning            │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                                     ▼
┌───────────────┐                     ┌───────────────┐
│    Milvus     │                     │    Neo4j      │
│  Vector DB    │                     │   Graph DB    │
└───────────────┘                     └───────────────┘
```

## License

MIT
