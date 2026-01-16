# Skill: A2UI + shadcn Project Creator

## Metadata

```yaml
name: a2ui-create
version: 1.0.0
description: Cria projetos A2UI + shadcn + Next.js completos e funcionais
trigger: Quando usuario pede para criar projeto, inicializar, setup, ou novo app A2UI/shadcn
```

## Progressive Disclosure

### Level 1: Quick Start (Default)

**Trigger**: "crie um projeto", "novo app", "setup rapido"

**Acao**:
```bash
# 1. Criar projeto com preset padrao
npx shadcn@latest create --preset "https://ui.shadcn.com/init?base=radix&style=nova&baseColor=neutral&theme=indigo&iconLibrary=lucide&font=inter&menuAccent=subtle&menuColor=default&radius=small&template=next" --template next my-a2ui-app

# 2. Instalar A2UI
cd my-a2ui-app
npm install @a2ui-bridge/core @a2ui-bridge/react @a2ui-bridge/react-shadcn

# 3. Setup basico automatico
```

**Output**: Projeto funcional com estrutura basica A2UI + shadcn.

---

### Level 2: Customized Setup

**Trigger**: "criar com customizacoes", "projeto personalizado", menciona opcoes especificas

**Perguntar ao usuario**:
1. Nome do projeto?
2. Biblioteca A2UI preferida?
   - @a2ui-bridge/react-shadcn (recomendado)
   - @zhama/a2ui
   - @xpert-ai/a2ui-react
3. Tema base?
   - Indigo (padrao)
   - Slate
   - Custom color
4. Incluir exemplos?
   - Chat com agente
   - Dashboard
   - Form builder

**Acao**: Configurar baseado nas respostas.

---

### Level 3: Enterprise Setup

**Trigger**: "projeto enterprise", "producao", "completo", "robusto"

**Incluir**:
- Autenticacao (NextAuth)
- Database (Prisma + PostgreSQL)
- API de agente com streaming
- Testes (Vitest + Playwright)
- CI/CD (GitHub Actions)
- Docker
- Monitoramento (Sentry)
- Analytics

---

## Estrutura Gerada (Level 1)

```
my-a2ui-app/
├── app/
│   ├── layout.tsx              # Root layout com providers
│   ├── page.tsx                # Home page
│   ├── globals.css             # Tailwind + CSS vars
│   ├── providers.tsx           # Theme + A2UI providers
│   └── api/
│       └── agent/
│           └── route.ts        # A2UI streaming endpoint
├── components/
│   ├── ui/                     # shadcn components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── a2ui/
│   │   ├── surface.tsx         # A2UI Surface wrapper
│   │   └── chat.tsx            # Chat component
│   └── theme-toggle.tsx        # Dark mode toggle
├── adapters/
│   ├── index.ts                # Catalogo de adapters
│   └── custom/                 # Adapters customizados
├── lib/
│   ├── utils.ts                # cn() helper
│   └── a2ui.ts                 # A2UI utilities
├── components.json             # shadcn config
├── tailwind.config.ts          # Tailwind config
├── next.config.ts              # Next.js config
└── package.json
```

## Arquivos Gerados

### app/providers.tsx

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

### app/layout.tsx

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'A2UI + shadcn App',
  description: 'AI-powered UI with A2UI Protocol and shadcn/ui',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

### app/api/agent/route.ts

```typescript
import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  const { prompt } = await req.json();

  // Simula resposta A2UI do agente
  const a2uiMessages = generateA2UIResponse(prompt);

  // Stream JSONL
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      for (const message of a2uiMessages) {
        controller.enqueue(encoder.encode(JSON.stringify(message) + '\n'));
        await new Promise((r) => setTimeout(r, 50));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'application/x-ndjson',
      'Transfer-Encoding': 'chunked',
    },
  });
}

function generateA2UIResponse(prompt: string) {
  return [
    {
      surfaceUpdate: {
        surfaceId: 'chat',
        components: [
          {
            id: 'response-card',
            component: {
              Card: {
                child: 'card-content',
              },
            },
          },
          {
            id: 'card-content',
            component: {
              Column: {
                children: ['response-title', 'response-text'],
              },
            },
          },
          {
            id: 'response-title',
            component: {
              Text: {
                text: { literalString: 'Resposta do Agente' },
                usageHint: 'h3',
              },
            },
          },
          {
            id: 'response-text',
            component: {
              Text: {
                text: { literalString: `Voce disse: "${prompt}"` },
                usageHint: 'body',
              },
            },
          },
        ],
      },
    },
    {
      beginRendering: {
        surfaceId: 'chat',
        root: 'response-card',
      },
    },
  ];
}
```

### components/a2ui/chat.tsx

```typescript
'use client';

import { useState } from 'react';
import { Surface, useA2UIProcessor } from '@a2ui-bridge/react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Send } from 'lucide-react';

export function A2UIChat() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const processor = useA2UIProcessor();

  async function sendMessage() {
    if (!input.trim() || loading) return;

    setLoading(true);
    try {
      const response = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const lines = decoder.decode(value).split('\n');
        for (const line of lines) {
          if (line.trim()) {
            const message = JSON.parse(line);
            processor.handleMessage(message);
          }
        }
      }

      setInput('');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[600px] max-w-2xl mx-auto">
      <Card className="flex-1 overflow-auto p-4 mb-4">
        <Surface
          surfaceId="chat"
          onAction={(action) => {
            console.log('Action:', action);
          }}
        />
      </Card>

      <div className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Digite sua mensagem..."
          disabled={loading}
        />
        <Button onClick={sendMessage} disabled={loading}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
```

### app/page.tsx

```typescript
import { A2UIChat } from '@/components/a2ui/chat';
import { ThemeToggle } from '@/components/theme-toggle';

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">A2UI + shadcn Demo</h1>
        <ThemeToggle />
      </div>

      <A2UIChat />
    </main>
  );
}
```

## Validacao

Apos criar, verificar:

```
[ ] npm run dev funciona
[ ] Pagina carrega sem erros
[ ] Dark mode toggle funciona
[ ] Chat envia mensagem
[ ] Surface renderiza resposta
[ ] Streaming funciona (UI atualiza incrementalmente)
```

## Comandos Relacionados

- `/a2ui-create` - Criar projeto
- `/a2ui-add-component` - Adicionar componente
- `/a2ui-add-adapter` - Adicionar adapter customizado
