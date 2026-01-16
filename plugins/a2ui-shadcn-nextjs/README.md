# Plugin: A2UI + shadcn + Next.js Specialist

Plugin completo para Claude Code especializado em criar, analisar, corrigir, atualizar e customizar projetos que utilizam A2UI Protocol, shadcn/ui e Next.js.

## Visao Geral

Este plugin fornece um sistema completo de agentes, skills, comandos e workflows para trabalhar com a stack A2UI + shadcn + Next.js.

### Stack Suportada

| Tecnologia | Versao | Descricao |
|------------|--------|-----------|
| A2UI Protocol | v0.8+ | Protocolo declarativo para UI gerada por AI |
| shadcn/ui | v3+ | Sistema de componentes com OKLCH e Tailwind v4 |
| Next.js | 15+ | Framework React com App Router |
| Tailwind CSS | v4+ | Framework CSS utility-first |
| React | 19+ | Biblioteca de UI |

## Comandos Disponiveis

| Comando | Descricao |
|---------|-----------|
| `/a2ui-create` | Criar novo projeto A2UI + shadcn + Next.js |
| `/a2ui-analyze` | Analisar projeto para problemas e oportunidades |
| `/a2ui-fix` | Corrigir problemas automaticamente |
| `/a2ui-update` | Atualizar dependencias e migrar versoes |
| `/a2ui-design` | Criar e customizar temas visuais |
| `/a2ui-add` | Adicionar componentes e adapters |

## Inicio Rapido

### Criar Novo Projeto

```bash
/a2ui-create meu-app
```

Isso criara um projeto completo com:
- Next.js 15 configurado
- shadcn/ui com tema indigo
- A2UI Bridge integrado
- Exemplo de chat funcional
- Dark mode configurado

### Analisar Projeto Existente

```bash
/a2ui-analyze
```

Retorna relatorio com:
- Status geral do projeto
- Problemas criticos e alertas
- Recomendacoes de melhoria

### Corrigir Problemas

```bash
/a2ui-fix
```

Auto-detecta e corrige:
- Problemas de instalacao
- Estilos nao aplicados
- Erros de hydration
- Streaming quebrado

### Customizar Tema

```bash
/a2ui-design --color=teal --style=vibrant
```

Gera tema completo com:
- Paleta OKLCH
- Dark mode automatico
- CSS variables unificadas
- usageHint styles

## Estrutura do Plugin

```
.claude/plugins/a2ui-shadcn-nextjs/
├── agents/
│   ├── a2ui-shadcn-architect.md    # Orquestrador principal
│   ├── a2ui-analyzer.md            # Analise de codigo
│   ├── shadcn-fixer.md             # Correcao de problemas
│   ├── theme-designer.md           # Design de temas
│   └── adapter-creator.md          # Criacao de adapters
├── skills/
│   ├── create/SKILL.md             # Criacao de projetos
│   ├── analyze/SKILL.md            # Analise
│   ├── fix/SKILL.md                # Correcoes
│   ├── update/SKILL.md             # Atualizacoes
│   └── design/SKILL.md             # Theming
├── commands/
│   ├── a2ui-create.md
│   ├── a2ui-analyze.md
│   ├── a2ui-fix.md
│   ├── a2ui-update.md
│   ├── a2ui-design.md
│   └── a2ui-add.md
├── workflows/
│   ├── project-setup.md            # Setup completo
│   ├── diagnose-and-fix.md         # Diagnostico
│   ├── theme-customization.md      # Customizacao visual
│   ├── adapter-development.md      # Criar adapters
│   └── migration.md                # Migracoes
└── templates/
    ├── project/                    # Templates de projeto
    ├── api/                        # Templates de API
    ├── components/                 # Templates de componentes
    ├── adapters/                   # Templates de adapters
    └── a2ui-messages/              # Templates de JSON A2UI
```

## Agentes

### a2ui-shadcn-architect

Agente principal que orquestra todas as operacoes. Especializado em:
- Criacao de projetos completos
- Decisoes arquiteturais
- Integracao de componentes

### a2ui-analyzer

Especialista em analise de codigo e auditoria:
- Verificacao de estrutura
- Validacao de protocolo A2UI
- Analise de performance
- Auditoria de seguranca

### shadcn-fixer

Especialista em resolucao de problemas:
- 12 problemas comuns mapeados
- Diagnostico automatico
- Fixes com validacao

### theme-designer

Especialista em design visual:
- Geracao de paletas OKLCH
- Templates de tema
- Dark mode automatico
- usageHint styles

### adapter-creator

Especialista em adapters A2UI:
- Catalogo de adapters padrao
- Templates para customizacao
- Data binding
- Actions e eventos

## Skills com Progressive Disclosure

Cada skill opera em 3 niveis:

### Level 1: Quick (Padrao)
Operacao rapida para casos simples.

### Level 2: Full
Operacao completa com todas as opcoes.

### Level 3: Enterprise
Operacao robusta para producao.

## Workflows

### project-setup
Fluxo completo para criar projeto do zero.

### diagnose-and-fix
Fluxo para identificar e corrigir problemas.

### theme-customization
Fluxo para customizar visual completo.

### adapter-development
Fluxo para criar adapters customizados.

### migration
Fluxo para migracoes entre versoes.

## Templates

### Projeto
- `providers.tsx.template` - Configuracao de providers
- `layout.tsx.template` - Layout raiz
- `globals.css.template` - CSS completo com A2UI mapping

### API
- `agent-route.ts.template` - Endpoint de streaming A2UI

### Componentes
- `a2ui-chat.tsx.template` - Chat com Surface
- `theme-toggle.tsx.template` - Toggle de tema

### Adapters
- `base-adapter.ts.template` - Template base
- `input-adapter.ts.template` - Input com data binding
- `catalog.ts.template` - Catalogo de adapters

### Mensagens A2UI
- `basic-card.json` - Card simples
- `form-with-actions.json` - Formulario completo
- `data-table.json` - Tabela de dados

## Preset shadcn Recomendado

```bash
npx shadcn@latest create --preset "https://ui.shadcn.com/init?base=radix&style=nova&baseColor=neutral&theme=indigo&iconLibrary=lucide&font=inter&menuAccent=subtle&menuColor=default&radius=small&template=next" --template next
```

## Dependencias A2UI

```bash
npm install @a2ui-bridge/core @a2ui-bridge/react @a2ui-bridge/react-shadcn
```

## Recursos

### Documentacao Oficial
- [A2UI Protocol](https://github.com/nicholasgriffintn/ai-platform-ui-spec)
- [shadcn/ui](https://ui.shadcn.com)
- [Next.js](https://nextjs.org)
- [Tailwind CSS](https://tailwindcss.com)

### Conhecimento Base
- `/research/A2UI_SHADCN_INTEGRATION_GUIDE.md`
- `/research/A2UI_STYLING_GUIDE.md`
- `/research/SHADCN_UI_KNOWLEDGE_BASE.md`

## Versao

- Plugin: 1.0.0
- A2UI Protocol: v0.8
- shadcn/ui: v3+
- Tailwind: v4+
- Next.js: 15+
