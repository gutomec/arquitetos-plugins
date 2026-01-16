# Command: /a2ui-create

## Metadata

```yaml
name: a2ui-create
description: Cria um novo projeto A2UI + shadcn + Next.js completo
usage: /a2ui-create [nome-projeto] [--template=chat|dashboard|form] [--theme=indigo|slate|custom]
```

## Prompt

Voce e o A2UI Project Creator. Crie um projeto A2UI + shadcn + Next.js completo e funcional.

## Instrucoes

### 1. Coletar Informacoes

Se o usuario nao especificou, pergunte:
- Nome do projeto (default: my-a2ui-app)
- Template desejado (chat, dashboard, form)
- Cor primaria (indigo padrao)

### 2. Criar Projeto Base

```bash
# Criar projeto com preset shadcn
npx shadcn@latest create --preset "https://ui.shadcn.com/init?base=radix&style=nova&baseColor=neutral&theme=$THEME&iconLibrary=lucide&font=inter&menuAccent=subtle&menuColor=default&radius=small&template=next" --template next $PROJECT_NAME

cd $PROJECT_NAME

# Instalar dependencias A2UI
npm install @a2ui-bridge/core @a2ui-bridge/react @a2ui-bridge/react-shadcn
```

### 3. Gerar Arquivos

Criar os seguintes arquivos:

**app/providers.tsx**
```typescript
'use client';

import { ThemeProvider } from 'next-themes';
import { A2UIBridgeProvider } from '@a2ui-bridge/react';
import { shadcnComponents } from '@a2ui-bridge/react-shadcn';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <A2UIBridgeProvider components={shadcnComponents}>
        {children}
      </A2UIBridgeProvider>
    </ThemeProvider>
  );
}
```

**app/layout.tsx** - Atualizar para usar Providers

**app/api/agent/route.ts** - Endpoint de streaming A2UI

**components/a2ui/surface.tsx** - Wrapper do Surface

**adapters/index.ts** - Catalogo de adapters

### 4. Validar

```bash
npm run dev
# Verificar se:
# - Projeto inicia sem erros
# - Pagina carrega
# - Dark mode funciona
# - Surface renderiza
```

### 5. Output

Informar ao usuario:
- Localizacao do projeto
- Como iniciar: `npm run dev`
- Proximos passos sugeridos

## Exemplos

```
/a2ui-create meu-app
/a2ui-create --template=dashboard
/a2ui-create meu-chat --theme=slate
```

## Agente

Usar: `a2ui-shadcn-architect`

## Skill

Invocar: `a2ui-create` (Level 1, 2 ou 3 baseado na complexidade)
