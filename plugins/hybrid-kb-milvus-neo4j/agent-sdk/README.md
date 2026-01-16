# Knowledge Base Agent

Sistema multi-agente self-contained para bases de conhecimento multi-tenant.

Pode ser plugado como subagente em qualquer sistema Claude Agent SDK.

## Instalação

```bash
pip install knowledge-base-agent

# Com suporte completo a documentos
pip install knowledge-base-agent[full]
```

## Uso como Subagente

```python
from knowledge_base_agent import KnowledgeBaseAgent

# O agente auto-inicializa toda a infraestrutura
kb_agent = KnowledgeBaseAgent()

# Usar com linguagem natural
result = await kb_agent.run(
    "Crie uma base de conhecimento chamada 'Documentos Legais' como global",
    user_id="user123"
)
print(result)

# Fazer upload de arquivo
result = await kb_agent.run(
    "Faça upload do arquivo contrato.pdf para a base 'Documentos Legais'",
    user_id="user123"
)

# Buscar
result = await kb_agent.run(
    "Busque documentos sobre cláusulas contratuais",
    user_id="user123"
)
```

## Uso como API Direta

```python
from knowledge_base_agent import KnowledgeBaseAgent

kb_agent = KnowledgeBaseAgent()

# Criar KB
kb = await kb_agent.create_knowledge_base(
    user_id="user123",
    name="Minha Base",
    visibility="private",  # ou "global"
    embedding_provider="google"  # ou "cohere"
)

# Upload de arquivo
with open("documento.pdf", "rb") as f:
    result = await kb_agent.upload_file(
        kb_id=kb["id"],
        user_id="user123",
        filename="documento.pdf",
        content=f.read()
    )

# Buscar
results = await kb_agent.search(
    query="minha consulta",
    user_id="user123",
    search_type="hybrid"  # vector, graph, ou hybrid
)
```

## Uso como Tool Provider

```python
from knowledge_base_agent import get_kb_tools, KnowledgeBaseAgent

# Obter definições de tools para usar em outro agente
tools = get_kb_tools()

# Em seu agente principal
class MyAgent:
    def __init__(self):
        self.kb_agent = KnowledgeBaseAgent()
        self.tools = get_kb_tools()

    async def handle_tool_call(self, tool_name, tool_input):
        if tool_name.startswith("kb_"):
            return await self.kb_agent.execute_tool(tool_name, tool_input)
```

## Tools Disponíveis

| Tool | Descrição |
|------|-----------|
| `kb_create` | Criar nova base de conhecimento |
| `kb_list` | Listar bases acessíveis |
| `kb_delete` | Deletar base de conhecimento |
| `kb_upload_file` | Upload de arquivo (base64) |
| `kb_upload_from_url` | Upload via URL (Minio presigned) |
| `kb_list_files` | Listar arquivos de uma KB |
| `kb_delete_file` | Deletar arquivo |
| `kb_search` | Buscar (vector/graph/hybrid) |
| `kb_get_upload_url` | Obter URL presigned para upload |
| `kb_process_file` | Processar arquivo após upload |
| `kb_health` | Verificar saúde do sistema |

## Formatos Suportados

- PDF, DOCX, XLSX, PPTX
- TXT, MD, CSV, JSON, HTML
- ZIP (extrai e processa automaticamente)

## Visibilidade

- **private**: Apenas o dono e seus agentes podem acessar
- **global**: Todos os usuários/agentes podem acessar

## Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `KB_POSTGRES_URL` | URL do PostgreSQL | `postgresql://postgres:postgres@localhost:5432/knowledge_base` |
| `KB_MILVUS_URI` | URI do Milvus | `http://localhost:19530` |
| `KB_NEO4J_URI` | URI do Neo4j | `bolt://localhost:7687` |
| `KB_NEO4J_USER` | Usuário Neo4j | `neo4j` |
| `KB_NEO4J_PASS` | Senha Neo4j | `password` |
| `KB_MINIO_ENDPOINT` | Endpoint Minio | `localhost:9000` |
| `KB_MINIO_ACCESS_KEY` | Access Key | `minioadmin` |
| `KB_MINIO_SECRET_KEY` | Secret Key | `minioadmin` |
| `GOOGLE_API_KEY` | API Key Google | - |
| `COHERE_API_KEY` | API Key Cohere | - |
| `ANTHROPIC_API_KEY` | API Key Claude | - |

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                     Parent Agent System                          │
│                 (Seu sistema Agent SDK)                          │
└─────────────────────────────────────────────────────────────────┘
                               │
                    Chama como subagente
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   KnowledgeBaseAgent                             │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Tools     │  │   Storage   │  │  Processing │             │
│  │  Interface  │  │   Manager   │  │   Pipeline  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│  Auto-inicializa toda a infraestrutura no primeiro uso          │
└─────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────┐
        ▼          ▼           ▼           ▼          ▼
   ┌────────┐ ┌────────┐  ┌────────┐  ┌────────┐ ┌────────┐
   │Postgres│ │ Milvus │  │ Neo4j  │  │ Minio  │ │ Redis  │
   │Metadata│ │Vectors │  │ Graph  │  │ Files  │ │ Cache  │
   └────────┘ └────────┘  └────────┘  └────────┘ └────────┘
```

## Auto-Inicialização

O agente cria automaticamente:
- Tabelas no PostgreSQL (se não existirem)
- Bucket no Minio (se não existir)
- Índices no Neo4j (se não existirem)
- Collections no Milvus (ao criar KBs)

## Exemplo Completo

```python
import asyncio
from knowledge_base_agent import KnowledgeBaseAgent

async def main():
    # Criar agente (auto-inicializa infraestrutura)
    agent = KnowledgeBaseAgent()

    # Verificar saúde
    health = await agent.health_check()
    print("Health:", health)

    # Criar KB global
    kb = await agent.create_knowledge_base(
        user_id="admin",
        name="Documentos da Empresa",
        visibility="global",
        description="Base de conhecimento compartilhada"
    )
    print("Created KB:", kb)

    # Upload de arquivo
    with open("manual.pdf", "rb") as f:
        result = await agent.upload_file(
            kb_id=kb["id"],
            user_id="admin",
            filename="manual.pdf",
            content=f.read()
        )
    print("Upload result:", result)

    # Buscar
    results = await agent.search(
        query="como configurar o sistema",
        user_id="user456",  # Outro usuário pode buscar em KBs globais
        search_type="hybrid"
    )
    print("Search results:", results)

asyncio.run(main())
```

## Licença

MIT
