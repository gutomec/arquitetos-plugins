# Command: /a2ui-add

## Metadata

```yaml
name: a2ui-add
description: Adiciona componentes shadcn e adapters A2UI ao projeto
usage: /a2ui-add [tipo] [nome] [--adapter] [--no-adapter]
```

## Prompt

Voce e o A2UI Component Manager. Adicione componentes shadcn e crie adapters A2UI correspondentes.

## Instrucoes

### 1. Tipos de Adicao

**component (default):**
- Adicionar componente shadcn
- Criar adapter A2UI automaticamente
- Registrar no catalogo

**adapter:**
- Criar apenas adapter para componente existente
- Nao instalar via shadcn CLI

**custom:**
- Criar componente customizado
- Criar adapter customizado
- Registrar ambos

### 2. Componentes Disponiveis

**Layout:**
- Card, Accordion, Tabs, Collapsible
- Dialog, Sheet, Drawer, Popover
- Separator, AspectRatio, ScrollArea

**Forms:**
- Button, Input, Textarea, Select
- Checkbox, Radio, Switch, Slider
- DatePicker, Combobox, Form

**Data Display:**
- Table, DataTable, Badge, Avatar
- Progress, Skeleton, Carousel

**Feedback:**
- Alert, AlertDialog, Toast
- Tooltip, HoverCard

**Navigation:**
- NavigationMenu, Breadcrumb
- Pagination, Command, ContextMenu

### 3. Workflow de Adicao

```typescript
async function addComponent(type: string, name: string, options: Options) {
  // 1. Adicionar componente shadcn
  if (type !== 'adapter') {
    await exec(`npx shadcn@latest add ${name}`);
  }

  // 2. Criar adapter (se --adapter ou default)
  if (options.adapter !== false) {
    const adapterCode = generateAdapter(name);
    await writeFile(`adapters/${name}Adapter.ts`, adapterCode);
  }

  // 3. Registrar no catalogo
  await updateCatalog(name);

  // 4. Gerar exemplo de uso
  const example = generateUsageExample(name);

  return { component: name, adapter: adapterCode, example };
}
```

### 4. Geracao de Adapter

```typescript
function generateAdapter(componentName: string): string {
  return `
import { createAdapter, extractValue, renderChild } from '@a2ui-bridge/react';
import { ${componentName} } from '@/components/ui/${componentName.toLowerCase()}';

interface A2UI${componentName}Props {
  // Props A2UI especificas
}

export const ${componentName}Adapter = createAdapter<A2UI${componentName}Props>(
  ${componentName},
  {
    mapProps: (a2ui, ctx) => ({
      // Mapear props A2UI para shadcn
      children: a2ui.child ? renderChild(a2ui.child, ctx) : undefined,
      className: a2ui.className,
    }),
  }
);
`;
}
```

### 5. Output

```markdown
# Componente Adicionado

## shadcn Component
- Instalado: `components/ui/${name}.tsx`
- Dependencias: [lista se houver]

## A2UI Adapter
- Criado: `adapters/${name}Adapter.ts`
- Registrado em: `adapters/index.ts`

## Uso A2UI

```json
{
  "surfaceUpdate": {
    "surfaceId": "main",
    "components": [
      {
        "id": "my-${name.toLowerCase()}",
        "component": {
          "${name}": {
            // props especificas
          }
        }
      }
    ]
  }
}
```

## Uso React

```tsx
import { ${name} } from '@/components/ui/${name.toLowerCase()}';

<${name}>Content</${name}>
```
```

## Exemplos

```
/a2ui-add button
/a2ui-add card --no-adapter
/a2ui-add adapter DataTable
/a2ui-add custom MyWidget
/a2ui-add dialog sheet drawer
```

## Agente

Usar: `adapter-creator`

## Skill

Basear em catalogo de adapters do agente
