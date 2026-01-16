# Arquitetos Plugins - Marketplace

Marketplace de plugins para Claude Code criados pelo sistema Arquitetos de Prompt.

## Como Usar

### 1. Adicionar o Marketplace (uma vez)

```bash
# No Claude Code
/plugin marketplace add seu-usuario/arquitetos-plugins
```

### 2. Instalar Plugins

```bash
# Listar plugins disponiveis
/plugin marketplace list arquitetos-plugins

# Instalar um plugin
/plugin install media-forge@arquitetos-plugins
```

## Plugins Disponiveis

| Plugin | Descricao | Versao |
|--------|-----------|--------|
| `media-forge` | Geracao de imagens e videos com IA | 1.0.0 |

## Variaveis de Ambiente Necessarias

Antes de usar os plugins, configure as seguintes variaveis de ambiente:

```bash
# No seu ~/.bashrc ou ~/.zshrc
export FAL_KEY="sua-chave-fal"
export GEMINI_API_KEY="sua-chave-gemini"
export OPENAI_API_KEY="sua-chave-openai"
export REPLICATE_API_TOKEN="seu-token-replicate"
```

Ou crie um arquivo `.env` no diretorio do projeto.

## Estrutura do Marketplace

```
arquitetos-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── media-forge/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── .mcp.json
│       ├── agents/
│       ├── commands/
│       └── skills/
└── README.md
```

## Publicar no GitHub

1. Crie um repositorio no GitHub chamado `arquitetos-plugins`
2. Copie o conteudo desta pasta `marketplace/` para o repositorio
3. Faca push para o GitHub
4. Pronto! Usuarios podem adicionar com `/plugin marketplace add seu-usuario/arquitetos-plugins`

## Licenca

MIT
