# Workflow: A2UI Project Setup

## Metadata

```yaml
name: a2ui-project-setup
description: Workflow completo para setup de projeto A2UI + shadcn + Next.js
trigger: /a2ui-create ou quando usuario quer criar novo projeto
version: 1.0.0
```

## Diagrama

```
┌─────────────────┐
│  1. Requisitos  │
│   (Perguntar)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Criar Base  │
│   (shadcn CLI)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Instalar    │
│   A2UI Bridge   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. Configurar  │
│    Providers    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. Criar API   │
│   de Streaming  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. Criar UI    │
│    (Surface)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  7. Validar     │
│   (npm run dev) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  8. Entregar    │
│  (Instrucoes)   │
└─────────────────┘
```

## Etapas Detalhadas

### Etapa 1: Coletar Requisitos

**Agente**: a2ui-shadcn-architect

**Perguntas**:
1. Nome do projeto?
2. Template (chat/dashboard/form)?
3. Tema (indigo/slate/custom)?
4. Nivel de setup (quick/custom/enterprise)?

**Defaults**:
```yaml
nome: my-a2ui-app
template: chat
tema: indigo
nivel: quick
```

### Etapa 2: Criar Projeto Base

**Agente**: a2ui-shadcn-architect

**Acoes**:
```bash
npx shadcn@latest create --preset "https://ui.shadcn.com/init?base=radix&style=nova&baseColor=neutral&theme=${TEMA}&iconLibrary=lucide&font=inter&menuAccent=subtle&menuColor=default&radius=small&template=next" --template next ${NOME}

cd ${NOME}
```

**Verificacao**:
- Diretorio criado
- package.json existe
- components.json existe

### Etapa 3: Instalar A2UI Bridge

**Agente**: a2ui-shadcn-architect

**Acoes**:
```bash
npm install @a2ui-bridge/core @a2ui-bridge/react @a2ui-bridge/react-shadcn
```

**Verificacao**:
- Dependencias em package.json
- node_modules/@a2ui-bridge existe

### Etapa 4: Configurar Providers

**Agente**: a2ui-shadcn-architect

**Arquivos**:
- `app/providers.tsx` - ThemeProvider + A2UIBridgeProvider
- `app/layout.tsx` - Atualizar para usar Providers

**Verificacao**:
- Providers exportados
- Layout usa Providers

### Etapa 5: Criar API de Streaming

**Agente**: a2ui-shadcn-architect

**Arquivos**:
- `app/api/agent/route.ts` - Endpoint POST com streaming JSONL

**Verificacao**:
- Route handler existe
- Retorna Content-Type: application/x-ndjson

### Etapa 6: Criar UI com Surface

**Agente**: adapter-creator

**Arquivos**:
- `components/a2ui/surface.tsx` - Wrapper do Surface
- `components/a2ui/chat.tsx` - Componente de chat (se template=chat)
- `adapters/index.ts` - Catalogo de adapters

**Verificacao**:
- Surface importado corretamente
- Catalogo registra shadcnComponents

### Etapa 7: Validar Setup

**Agente**: a2ui-analyzer

**Acoes**:
```bash
npm run dev
```

**Verificacoes**:
- [ ] Build compila sem erros
- [ ] Pagina carrega no browser
- [ ] Dark mode toggle funciona
- [ ] Surface renderiza
- [ ] Streaming funciona

### Etapa 8: Entregar

**Agente**: a2ui-shadcn-architect

**Output**:
```markdown
# Projeto Criado com Sucesso!

## Localizacao
`${PWD}/${NOME}`

## Iniciar
```bash
cd ${NOME}
npm run dev
```

## Estrutura
[Mostrar arvore de arquivos]

## Proximos Passos
1. Customizar tema: `/a2ui-design`
2. Adicionar componentes: `/a2ui-add [componente]`
3. Criar adapters: `/a2ui-add adapter [nome]`

## Documentacao
- A2UI Protocol: [link]
- shadcn/ui: [link]
```

## Rollback

Se qualquer etapa falhar:
1. Logar erro detalhado
2. Sugerir fix com `/a2ui-fix`
3. Se critico, remover diretorio criado

## Duracao Estimada

- Quick: ~2 minutos
- Custom: ~5 minutos
- Enterprise: ~15 minutos
