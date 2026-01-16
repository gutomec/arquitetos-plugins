---
name: ultra-arquiteto-plugins
description: Cria plugins completos para Claude Code e Claude Agent SDK. Use quando o usuario solicitar criacao de sistemas de agentes, skills, workflows, automacoes ou plugins completos. Combina pesquisa web, discussao BMAD multi-agente e geracao paralela por 5 arquitetos especializados.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Task
  - TodoWrite
---

# Ultra Arquiteto de Plugins

Sistema avancado para criacao de plugins completos para Claude Code e Claude Agent SDK.

## Quick Start

1. Receba a solicitacao do usuario
2. Execute pesquisa web sobre o dominio
3. Convoque discussao BMAD
4. Execute 5 arquitetos em paralelo
5. Gere output dual (Claude Code + Agent SDK)
6. Publique no marketplace GitHub

## Processo Detalhado

### Fase 1: Analise de Requisitos

Ao receber uma solicitacao:

```
1. Identificar intencao principal
2. Extrair requisitos explicitos
3. Inferir requisitos implicitos
4. Determinar dominio de conhecimento
5. Gerar palavras-chave para pesquisa
```

### Fase 2: Pesquisa Web

Executar pesquisas:

```
- "{dominio} best practices 2025 2026"
- "{dominio} experts methodology"
- "Claude Code {dominio} integration"
- "Claude Agent SDK {dominio}"
```

### Fase 3: Discussao BMAD

Convocar agentes para debate:

- *Architect (Winston)*: Arquitetura tecnica
- *Analyst (Mary)*: Requisitos e gaps
- *Developer (Amelia)*: Viabilidade tecnica
- *Agent Builder (Bond)*: Estrutura de agentes

### Fase 4: Geracao Paralela

5 arquitetos especializados:

| Arquiteto | Especialidade |
|-----------|---------------|
| arquiteto-agentes | Subagents com personas |
| arquiteto-skills | Skills com progressive disclosure |
| arquiteto-workflows | Fluxos de orquestracao |
| arquiteto-tools | MCP servers e hooks |
| arquiteto-commands | Slash commands |

### Fase 5: Output Dual

Gerar estruturas completas:

*Claude Code:*
```
.claude/
├── agents/*.md
├── skills/*/SKILL.md
├── commands/*.md
└── hooks/*.sh
```

*Claude Agent SDK:*
```
python/
├── agents.py
├── tools.py
├── hooks.py
└── main.py

typescript/
├── agents.ts
├── tools.ts
├── hooks.ts
└── index.ts
```

### Fase 6: Publicacao no Marketplace GitHub

Apos gerar o plugin, publicar automaticamente no marketplace `gutomec/arquitetos-plugins`.

#### Estrutura do Marketplace

```
marketplace/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── {nome-plugin}/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── .mcp.json          # MCP servers (auto-config)
│       ├── README.md
│       ├── agents/
│       ├── commands/
│       └── skills/
└── README.md
```

#### Passos de Publicacao

1. *Criar estrutura marketplace* em `_bmad-output/{plugin}/marketplace/`

2. *Gerar plugin.json*:
```json
{
  "name": "{nome-plugin}",
  "version": "1.0.0",
  "description": "{descricao}",
  "author": { "name": "Arquitetos de Prompt" },
  "homepage": "https://github.com/gutomec/arquitetos-plugins",
  "repository": "https://github.com/gutomec/arquitetos-plugins",
  "commands": "./commands/",
  "agents": "./agents/",
  "skills": "./skills/",
  "mcpServers": "./.mcp.json"
}
```

3. *Gerar .mcp.json* com servidores MCP necessarios (usando `${VAR}` para chaves)

4. *Clonar marketplace existente*:
```bash
cd _bmad-output/{plugin}
git clone https://github.com/gutomec/arquitetos-plugins.git marketplace-repo
```

5. *Copiar plugin para marketplace*:
```bash
cp -r marketplace/plugins/{nome-plugin} marketplace-repo/plugins/
```

6. *Atualizar marketplace.json* adicionando o novo plugin ao array `plugins`

7. *Commit e push*:
```bash
cd marketplace-repo
git add .
git commit -m "Add {nome-plugin} plugin - {descricao curta}"
git push origin main
```

8. *Informar usuario*:
```
Plugin publicado com sucesso!

Para instalar:
/plugin marketplace add gutomec/arquitetos-plugins  # (se ainda nao adicionou)
/plugin install {nome-plugin}@arquitetos-plugins
```

#### Template marketplace.json

Ao adicionar novo plugin, incluir no array `plugins`:
```json
{
  "name": "{nome-plugin}",
  "source": "./plugins/{nome-plugin}",
  "description": "{descricao}",
  "version": "1.0.0",
  "author": { "name": "Arquitetos de Prompt" },
  "keywords": ["{keyword1}", "{keyword2}"]
}
```

## Guardrails de Seguranca

### Comandos Permitidos (Git)
- git clone
- git add
- git commit
- git push
- gh repo (para criar repos se necessario)

### Comandos Bloqueados
- rm -rf
- sudo
- chmod 777
- curl | bash
- wget -O - | sh
- git push --force (a menos que usuario solicite)

### Validacoes Obrigatorias
- Inputs sanitizados
- Tools com menor privilegio
- Credenciais nunca expostas
- Malware/backdoors bloqueados

## Templates

Consulte os arquivos de template em:
- [AGENT_TEMPLATE.md](templates/AGENT_TEMPLATE.md)
- [SKILL_TEMPLATE.md](templates/SKILL_TEMPLATE.md)
- [COMMAND_TEMPLATE.md](templates/COMMAND_TEMPLATE.md)
- [SDK_TEMPLATE.md](templates/SDK_TEMPLATE.md)

## Exemplos de Uso

### Exemplo 1: Plugin de Testes

```
Usuario: Crie um plugin para automacao de testes com Jest e Playwright
```

Resultado: Plugin com agentes test-runner, test-generator, skills de coverage, commands /test, /e2e

Publicado em: `gutomec/arquitetos-plugins`
Instalar: `/plugin install test-automation@arquitetos-plugins`

### Exemplo 2: Plugin de DevOps

```
Usuario: Crie um plugin para CI/CD com GitHub Actions
```

Resultado: Plugin com agentes pipeline-builder, deploy-manager, skills de workflow-yaml, commands /deploy, /rollback

Publicado em: `gutomec/arquitetos-plugins`
Instalar: `/plugin install devops-ci@arquitetos-plugins`

### Exemplo 3: Plugin de Media (Completo)

```
Usuario: Crie um plugin para geracao de imagens e videos com IA
```

Resultado:
- Agentes: media-orchestrator, image-architect, video-director, batch-processor, media-editor
- Commands: /gerar-imagem, /gerar-video, /animar-imagem, /batch-imagens, /editar-imagem
- Skills: prompt-engineering-media, model-selection-guide, batch-processing-patterns
- MCP Servers: fal-video, nano-banana-pro, dalle3 (auto-configurados)

Publicado em: `gutomec/arquitetos-plugins`
Instalar: `/plugin install media-forge@arquitetos-plugins`

## Marketplace

Todos os plugins criados sao publicados automaticamente em:

*Repositorio:* https://github.com/gutomec/arquitetos-plugins

*Para usuarios instalarem:*
```bash
# Adicionar marketplace (uma vez)
/plugin marketplace add gutomec/arquitetos-plugins

# Instalar qualquer plugin
/plugin install {nome-plugin}@arquitetos-plugins

# Atualizar marketplace
/plugin marketplace update arquitetos-plugins
```
