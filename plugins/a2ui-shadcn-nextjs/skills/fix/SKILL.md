# Skill: A2UI + shadcn Fixer

## Metadata

```yaml
name: a2ui-fix
version: 1.0.0
description: Corrige problemas em projetos A2UI + shadcn + Next.js de forma inteligente
trigger: Quando usuario reporta erro, bug, problema, ou algo nao funciona
```

## Progressive Disclosure

### Level 1: Auto-Fix Common Issues

**Trigger**: "nao funciona", "erro", "bug", sem detalhes especificos

**Acao**:
1. Detectar automaticamente problemas comuns
2. Aplicar fixes conhecidos
3. Validar se resolveu

---

### Level 2: Guided Fix

**Trigger**: Usuario descreve problema especifico

**Acao**:
1. Analisar descricao do problema
2. Investigar arquivos relacionados
3. Propor solucao
4. Aplicar com confirmacao

---

### Level 3: Deep Debug

**Trigger**: "problema complexo", "nao sei o que e", erro persistente

**Acao**:
1. Analise completa do projeto
2. Trace de execucao
3. Comparacao com setup correto
4. Fix gradual com validacao

---

## Problemas e Solucoes

### Categoria: Instalacao

#### P1: shadcn CLI nao funciona

**Sintoma**: `command not found: shadcn-ui`

**Diagnostico**:
```bash
which shadcn
npm list shadcn
```

**Fix**:
```bash
# Usar npx ao inves de comando global
npx shadcn@latest add button
```

---

#### P2: Dependencias A2UI faltando

**Sintoma**: `Module not found: '@a2ui-bridge/react'`

**Diagnostico**:
```bash
grep "@a2ui" package.json
```

**Fix**:
```bash
npm install @a2ui-bridge/core @a2ui-bridge/react @a2ui-bridge/react-shadcn
```

---

#### P3: components.json invalido

**Sintoma**: `Error: Could not find components.json`

**Diagnostico**:
```bash
cat components.json 2>/dev/null || echo "Arquivo nao existe"
```

**Fix**:
```bash
npx shadcn@latest init
```

---

### Categoria: Estilos

#### P4: Componentes sem estilo

**Sintoma**: Componentes renderizam mas sem CSS

**Diagnostico**:
```bash
grep "globals.css" app/layout.tsx
grep ":root" app/globals.css
```

**Fix**:
```typescript
// app/layout.tsx - Garantir import
import "./globals.css";
```

```css
/* app/globals.css - Garantir variaveis */
@import "tailwindcss";

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.488 0.243 264.376);
  /* ... todas as variaveis */
}
```

---

#### P5: Dark mode nao funciona

**Sintoma**: Toggle de tema sem efeito

**Diagnostico**:
```bash
grep "ThemeProvider" app/
grep "\.dark" app/globals.css
grep "next-themes" package.json
```

**Fix**:
```typescript
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider";

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"  // IMPORTANTE
          defaultTheme="system"
          enableSystem
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

```css
/* app/globals.css */
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  /* ... todas as variaveis dark */
}
```

---

#### P6: Tailwind nao aplica classes

**Sintoma**: Classes Tailwind ignoradas

**Diagnostico**:
```bash
grep "content" tailwind.config.ts
```

**Fix**:
```typescript
// tailwind.config.ts
export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/@a2ui-bridge/**/*.{js,ts,jsx,tsx}", // ADD
  ],
  // ...
}
```

---

### Categoria: Runtime

#### P7: Hydration mismatch

**Sintoma**: `Hydration failed because...`

**Diagnostico**:
```bash
grep -r "window\." components/
grep -r "document\." components/
grep -r "localStorage" components/
```

**Fix**:
```typescript
"use client";

import { useEffect, useState } from "react";

export function SafeComponent() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null; // ou skeleton
  }

  return <div>Conteudo que usa APIs do browser</div>;
}
```

---

#### P8: Surface nao renderiza

**Sintoma**: A2UI Surface em branco

**Diagnostico**:
```bash
grep "A2UIBridgeProvider" app/
grep "components=" app/
```

**Fix**:
```typescript
// app/providers.tsx
import { A2UIBridgeProvider } from '@a2ui-bridge/react';
import { shadcnComponents } from '@a2ui-bridge/react-shadcn';

export function Providers({ children }) {
  return (
    <A2UIBridgeProvider components={shadcnComponents}>
      {children}
    </A2UIBridgeProvider>
  );
}

// Componente que usa Surface
import { Surface } from '@a2ui-bridge/react';

function MyComponent() {
  return (
    <Surface
      surfaceId="main"  // Deve corresponder ao surfaceId das mensagens
      onAction={(action) => console.log(action)}
    />
  );
}
```

---

#### P9: Streaming nao funciona

**Sintoma**: UI nao atualiza incrementalmente

**Diagnostico**:
```bash
grep "Content-Type" app/api/
grep "ReadableStream" app/api/
```

**Fix**:
```typescript
// app/api/agent/route.ts
export async function POST(req: Request) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      for (const message of a2uiMessages) {
        // Enviar cada mensagem
        controller.enqueue(
          encoder.encode(JSON.stringify(message) + '\n')
        );
        // Pequeno delay para visualizar streaming
        await new Promise(r => setTimeout(r, 50));
      }
      controller.close();
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'application/x-ndjson',  // IMPORTANTE
      'Transfer-Encoding': 'chunked',
      'Cache-Control': 'no-cache',
    }
  });
}
```

---

### Categoria: A2UI Protocol

#### P10: Componente nao reconhecido

**Sintoma**: `Unknown component: CustomWidget`

**Diagnostico**:
```bash
grep "CustomWidget" adapters/
```

**Fix**:
```typescript
// adapters/index.ts
import { CustomWidgetAdapter } from './CustomWidgetAdapter';

export const customComponents = {
  ...shadcnComponents,
  CustomWidget: CustomWidgetAdapter,  // Registrar no catalogo
};

// Usar catalogo customizado no provider
<A2UIBridgeProvider components={customComponents}>
```

---

#### P11: Action nao dispara

**Sintoma**: Clique em botao nao faz nada

**Diagnostico**:
```bash
grep "onAction" adapters/ButtonAdapter
grep "action" # no JSON A2UI
```

**Fix**:
```typescript
// Adapter
const ButtonAdapter = createAdapter(Button, {
  mapProps: (a2ui, ctx) => ({
    // ...
    onClick: () => {
      if (a2ui.action) {
        ctx.onAction({
          name: a2ui.action.name,
          context: a2ui.action.context || [],
        });
      }
    },
  }),
});

// Surface
<Surface
  surfaceId="main"
  onAction={(action) => {
    console.log('Action received:', action);
    // Processar action
  }}
/>
```

---

#### P12: Data binding nao atualiza

**Sintoma**: Valor de input nao reflete no data model

**Diagnostico**:
```bash
grep "useDataBinding" adapters/
grep "path" # no JSON A2UI
```

**Fix**:
```typescript
// Adapter com data binding
import { createAdapter, useDataBinding } from '@a2ui-bridge/react';

const TextFieldAdapter = createAdapter(Input, {
  mapProps: (a2ui, ctx) => {
    const binding = useDataBinding(a2ui.text, ctx);

    return {
      value: binding.value || '',
      onChange: (e) => {
        binding.setValue(e.target.value);  // Atualiza data model
      },
    };
  },
});
```

---

## Workflow de Fix

```typescript
async function fixA2UIProject(problem?: string) {
  // 1. Se problema nao especificado, detectar automaticamente
  if (!problem) {
    const issues = await detectCommonIssues();
    if (issues.length === 0) {
      return "Nenhum problema detectado automaticamente. Descreva o problema.";
    }
    problem = issues[0].type;
  }

  // 2. Mapear problema para solucao
  const solution = PROBLEM_SOLUTIONS[problem];
  if (!solution) {
    return "Problema desconhecido. Vou investigar manualmente.";
  }

  // 3. Aplicar fix
  await applyFix(solution);

  // 4. Validar
  const fixed = await validateFix(problem);
  if (!fixed) {
    return "Fix aplicado mas problema persiste. Investigando mais...";
  }

  return `Problema "${problem}" corrigido com sucesso.`;
}
```

## Comandos Relacionados

- `/a2ui-fix` - Auto-fix problemas
- `/a2ui-fix-styles` - Focar em estilos
- `/a2ui-fix-runtime` - Focar em runtime
- `/a2ui-fix-protocol` - Focar em protocolo
