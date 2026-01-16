# Arquitetos Plugins - Marketplace

Marketplace de plugins para Claude Code criados pelo sistema Arquitetos de Prompt.

## Como Usar

### 1. Adicionar o Marketplace (uma vez)

```bash
# No Claude Code
/plugin marketplace add gutomec/arquitetos-plugins
```

### 2. Instalar Plugins

```bash
# Listar plugins disponiveis
/plugin marketplace list arquitetos-plugins

# Instalar um plugin
/plugin install media-forge@arquitetos-plugins
/plugin install data-forge@arquitetos-plugins
```

## Plugins Disponiveis

| Plugin | Descricao | Versao |
|--------|-----------|--------|
| `media-forge` | Geracao de imagens e videos com IA (Imagen 4, Veo 3, FLUX) | 1.0.0 |
| `data-forge` | Analise de dados e estatistica avancada (CSV, Excel, Bancos) | 1.0.0 |

### Media Forge

Sistema multi-agente para geracao de midia com IA:
- Imagen 4, Veo 3, FLUX, DALL-E, Nano Banana
- Geracao de imagens e videos
- Edicao e transformacao de midia

### Data Forge

O sistema de analise de dados mais avancado do universo:
- Conexao: CSV, Excel, Parquet, PostgreSQL, MySQL, SQLite
- Profiling automatico: schema, tipos, qualidade
- Estatisticas: t-test, ANOVA, correlacoes, regressao
- Insights automaticos actionaveis
- Linguagem natural: perguntas em portugues

## Variaveis de Ambiente Necessarias

Antes de usar os plugins, configure as seguintes variaveis de ambiente:

```bash
# No seu ~/.bashrc ou ~/.zshrc

# Media Forge
export FAL_KEY="sua-chave-fal"
export GEMINI_API_KEY="sua-chave-gemini"
export OPENAI_API_KEY="sua-chave-openai"
export REPLICATE_API_TOKEN="seu-token-replicate"

# Data Forge (opcional, para bancos de dados)
export DATABASE_URL="postgresql://user:pass@host:5432/database"
```

Ou crie um arquivo `.env` no diretorio do projeto.

## Estrutura do Marketplace

```
arquitetos-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── media-forge/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── .mcp.json
│   │   ├── agents/
│   │   ├── commands/
│   │   └── skills/
│   └── data-forge/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       ├── commands/
│       └── skills/
└── README.md
```

## Licenca

MIT
