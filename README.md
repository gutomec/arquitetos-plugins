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
/plugin install landing-page-builder@arquitetos-plugins
/plugin install a2ui-shadcn-nextjs@arquitetos-plugins
```

## Plugins Disponiveis

| Plugin | Descricao | Versao |
|--------|-----------|--------|
| `a2ui-shadcn-nextjs` | Sistema especialista em A2UI Protocol, shadcn/ui e Next.js | 1.0.0 |
| `media-forge` | Geracao de imagens e videos com IA (Imagen 4, Veo 3, FLUX) | 1.0.0 |
| `data-forge` | Analise de dados e estatistica avancada (CSV, Excel, Bancos) | 1.0.0 |
| `landing-page-builder` | Criacao de landing pages de alta conversao com UI/UX 2026 | 1.0.0 |

### A2UI + shadcn + Next.js

Sistema especialista em A2UI Protocol, shadcn/ui e Next.js:
- Cria projetos com preset shadcn v3 (OKLCH, Base UI)
- Analisa e corrige configuracoes existentes
- Atualiza projetos antigos para padroes 2026
- Customiza temas e design tokens
- Preset: `npx shadcn@latest create --preset "https://ui.shadcn.com/init?base=radix&style=nova&baseColor=neutral&theme=indigo&iconLibrary=lucide&font=inter&menuAccent=subtle&menuColor=default&radius=small&template=next"`

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

### Landing Page Builder

Sistema multi-agente para criar landing pages de alta conversao:
- Copywriting com frameworks de conversao
- UI/UX moderno 2026 (Bento Grid, Glassmorphism)
- Animacoes 60fps com Framer Motion e GSAP
- API de leads com SQLite
- Admin dashboard completo

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
│   ├── a2ui-shadcn-nextjs/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/
│   │   ├── commands/
│   │   ├── skills/
│   │   └── workflows/
│   ├── media-forge/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/
│   │   ├── commands/
│   │   └── skills/
│   ├── data-forge/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── agents/
│   │   ├── commands/
│   │   └── skills/
│   └── landing-page-builder/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── agents/
│       ├── commands/
│       └── skills/
└── README.md
```

## Licenca

MIT
