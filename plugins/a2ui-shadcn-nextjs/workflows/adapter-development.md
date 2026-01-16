# Workflow: Adapter Development

## Metadata

```yaml
name: a2ui-adapter-development
description: Workflow para criar e testar adapters A2UI customizados
trigger: /a2ui-add adapter ou quando usuario quer criar componente customizado
version: 1.0.0
```

## Diagrama

```
┌─────────────────┐
│  1. Definir     │
│   Componente    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Analisar    │
│   Props A2UI    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Analisar    │
│   Props shadcn  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. Mapear      │
│   Props         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. Implementar │
│   Adapter       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. Data        │
│   Binding       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  7. Actions     │
│   e Eventos     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  8. Registrar   │
│   no Catalogo   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  9. Testar      │
│   Adapter       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 10. Documentar  │
└─────────────────┘
```

## Etapas Detalhadas

### Etapa 1: Definir Componente

**Agente**: adapter-creator

**Coletar**:
- Nome do componente
- Componente shadcn base (ou custom)
- Funcionalidade desejada

**Categorias**:
```typescript
type ComponentCategory =
  | 'layout'      // Card, Accordion, Tabs
  | 'typography'  // Text, Heading, Label
  | 'form'        // Input, Select, Checkbox
  | 'feedback'    // Alert, Toast, Progress
  | 'data'        // Table, Badge, Avatar
  | 'navigation'  // Menu, Breadcrumb
  | 'custom';     // Componente novo
```

### Etapa 2: Analisar Props A2UI

**Agente**: adapter-creator

**Definir interface A2UI**:
```typescript
// Exemplo para um Rating component
interface A2UIRatingProps {
  // Valor
  value?: A2UIText;  // { literalNumber: N } ou { path: '/rating' }

  // Configuracao
  max?: number;
  readonly?: boolean;

  // Estilo semantico
  usageHint?: 'rating' | 'stars' | 'score';

  // Acao
  action?: A2UIAction;
}
```

### Etapa 3: Analisar Props shadcn

**Agente**: adapter-creator

**Identificar props do componente base**:
```typescript
// Props do componente shadcn/React
interface RatingProps {
  value: number;
  max?: number;
  onChange?: (value: number) => void;
  disabled?: boolean;
  className?: string;
}
```

### Etapa 4: Mapear Props

**Agente**: adapter-creator

**Criar mapeamento**:
```typescript
const propMapping = {
  // A2UI -> shadcn
  'value': (a2ui, ctx) => extractValue(a2ui.value, ctx) ?? 0,
  'max': (a2ui) => a2ui.max ?? 5,
  'readonly': (a2ui) => a2ui.readonly,
  'disabled': (a2ui) => a2ui.readonly,
  'className': (a2ui) => getUsageHintClass(a2ui.usageHint),
};
```

### Etapa 5: Implementar Adapter

**Agente**: adapter-creator

**Template base**:
```typescript
import { createAdapter, extractValue } from '@a2ui-bridge/react';
import { Rating } from '@/components/ui/rating';

interface A2UIRatingProps {
  value?: A2UIText;
  max?: number;
  readonly?: boolean;
  usageHint?: string;
  action?: A2UIAction;
}

export const RatingAdapter = createAdapter<A2UIRatingProps>(
  Rating,
  {
    mapProps: (a2ui, ctx) => ({
      value: extractValue(a2ui.value, ctx) ?? 0,
      max: a2ui.max ?? 5,
      disabled: a2ui.readonly,
      className: a2ui.usageHint ? `usage-${a2ui.usageHint}` : undefined,
    }),
  }
);
```

### Etapa 6: Data Binding

**Agente**: adapter-creator

**Adicionar suporte a binding bidirecional**:
```typescript
import { createAdapter, extractValue, useDataBinding } from '@a2ui-bridge/react';

export const RatingAdapter = createAdapter<A2UIRatingProps>(
  Rating,
  {
    mapProps: (a2ui, ctx) => {
      // Binding bidirecional para value
      const binding = useDataBinding(a2ui.value, ctx);

      return {
        value: binding.value ?? 0,
        max: a2ui.max ?? 5,
        disabled: a2ui.readonly,
        onChange: (newValue: number) => {
          binding.setValue(newValue);
        },
      };
    },
  }
);
```

### Etapa 7: Actions e Eventos

**Agente**: adapter-creator

**Adicionar suporte a actions**:
```typescript
export const RatingAdapter = createAdapter<A2UIRatingProps>(
  Rating,
  {
    mapProps: (a2ui, ctx) => {
      const binding = useDataBinding(a2ui.value, ctx);

      return {
        value: binding.value ?? 0,
        max: a2ui.max ?? 5,
        disabled: a2ui.readonly,
        onChange: (newValue: number) => {
          // Atualizar data model
          binding.setValue(newValue);

          // Disparar action se definida
          if (a2ui.action) {
            ctx.onAction({
              name: a2ui.action.name,
              context: [
                ...(a2ui.action.context || []),
                { key: 'value', value: newValue },
              ],
            });
          }
        },
      };
    },
  }
);
```

### Etapa 8: Registrar no Catalogo

**Agente**: adapter-creator

**Atualizar adapters/index.ts**:
```typescript
import { shadcnComponents } from '@a2ui-bridge/react-shadcn';
import { RatingAdapter } from './RatingAdapter';

export const customComponents = {
  ...shadcnComponents,
  Rating: RatingAdapter,
};

// Usar no provider
// <A2UIBridgeProvider components={customComponents}>
```

### Etapa 9: Testar Adapter

**Agente**: a2ui-analyzer

**Criar teste de integracao**:
```typescript
// __tests__/adapters/RatingAdapter.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { A2UIBridgeProvider, Surface } from '@a2ui-bridge/react';
import { customComponents } from '@/adapters';

const mockMessages = [
  {
    surfaceUpdate: {
      surfaceId: 'test',
      components: [
        {
          id: 'rating-1',
          component: {
            Rating: {
              value: { literalNumber: 3 },
              max: 5,
              action: { name: 'rate' },
            },
          },
        },
      ],
    },
  },
  {
    beginRendering: { surfaceId: 'test', root: 'rating-1' },
  },
];

test('Rating adapter renders and handles interaction', async () => {
  const onAction = jest.fn();

  render(
    <A2UIBridgeProvider components={customComponents}>
      <Surface surfaceId="test" onAction={onAction} />
    </A2UIBridgeProvider>
  );

  // Processar mensagens
  // Verificar render
  // Simular interacao
  // Verificar action disparada
});
```

### Etapa 10: Documentar

**Agente**: adapter-creator

**Gerar documentacao**:
```markdown
# Rating Adapter

## A2UI Props

| Prop | Tipo | Descricao |
|------|------|-----------|
| value | A2UIText | Valor atual (literalNumber ou path) |
| max | number | Valor maximo (default: 5) |
| readonly | boolean | Se somente leitura |
| usageHint | string | Estilo semantico |
| action | A2UIAction | Acao ao mudar valor |

## Exemplo A2UI JSON

```json
{
  "component": {
    "Rating": {
      "value": { "path": "/user/rating" },
      "max": 5,
      "action": {
        "name": "updateRating",
        "context": [{ "key": "userId", "value": "123" }]
      }
    }
  }
}
```

## Uso com Data Binding

O adapter suporta binding bidirecional. Quando o usuario muda o valor,
o data model e atualizado automaticamente no path especificado.
```

## Checklist Final

```
[ ] Interface A2UI definida
[ ] Props mapeadas corretamente
[ ] extractValue usado para text/value
[ ] renderChild usado para children
[ ] useDataBinding para inputs
[ ] onAction para eventos
[ ] Registrado no catalogo
[ ] Teste de integracao criado
[ ] Documentacao gerada
```

## Adapters de Referencia

Consultar implementacoes existentes:
- `ButtonAdapter` - Actions simples
- `TextFieldAdapter` - Data binding
- `CardAdapter` - Children/slots
- `TableAdapter` - Listas e iteracao
