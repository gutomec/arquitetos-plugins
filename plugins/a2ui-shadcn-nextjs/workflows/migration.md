# Workflow: Migration

## Metadata

```yaml
name: a2ui-migration
description: Workflow para migracoes seguras entre versoes de A2UI, shadcn, Tailwind, Next.js e React
trigger: /a2ui-update --major ou quando usuario menciona migracao
version: 1.0.0
```

## Diagrama

```
┌─────────────────┐
│  1. Identificar │
│   Versoes       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Planejar    │
│   Migracao      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Criar       │
│   Backup        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. Executar    │
│   Pre-Migration │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. Atualizar   │
│   Dependencias  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. Executar    │
│   Codemods      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  7. Atualizar   │
│   Configs       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  8. Validar     │
│   Build         │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│  OK   │ │ Fail  │
└───┬───┘ └───┬───┘
    │         │
    │         ▼
    │    ┌─────────┐
    │    │ Rollback│
    │    └────┬────┘
    │         │
    ▼         ▼
┌─────────────────┐
│  9. Testes      │
│   Manuais       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 10. Finalizar   │
│   e Documentar  │
└─────────────────┘
```

## Migracoes Suportadas

### A2UI v0.8 -> v0.9

**Breaking Changes**:
- `beginRendering` renomeado para `createSurface`
- Propriedade `styles` removida das mensagens
- Adjacency list agora obrigatorio

**Codemod**:
```typescript
async function migrateA2UIv08tov09(projectPath: string) {
  const files = await glob(`${projectPath}/**/*.{ts,tsx,js,jsx}`);

  for (const file of files) {
    let content = await readFile(file, 'utf-8');

    // 1. Renomear beginRendering -> createSurface
    content = content.replace(/beginRendering/g, 'createSurface');

    // 2. Remover styles das mensagens
    content = content.replace(/,?\s*styles:\s*\{[^}]+\}/g, '');

    // 3. Verificar adjacency list
    if (content.includes('surfaceUpdate') && !content.includes('adjacencyList')) {
      console.warn(`${file}: Pode precisar de adjacencyList`);
    }

    await writeFile(file, content);
  }
}
```

### shadcn v2 -> v3

**Breaking Changes**:
- HSL -> OKLCH cores
- forwardRef -> ref como prop
- Radix -> Base UI (parcial)
- Novos estilos: Nova, Maia, Lyra
- `data-slot` adicionado

**Codemod para cores**:
```typescript
function hslToOklch(h: number, s: number, l: number): string {
  // Converter HSL para sRGB
  const rgb = hslToRgb(h, s, l);

  // Converter sRGB para OKLCH
  const oklch = rgbToOklch(rgb);

  return `oklch(${oklch.L.toFixed(3)} ${oklch.C.toFixed(3)} ${oklch.H.toFixed(1)})`;
}

async function migrateShadcnColors(cssPath: string) {
  let content = await readFile(cssPath, 'utf-8');

  // Regex para HSL: "222.2 47.4% 11.2%"
  const hslRegex = /(\d+\.?\d*)\s+(\d+\.?\d*)%\s+(\d+\.?\d*)%/g;

  content = content.replace(hslRegex, (match, h, s, l) => {
    return hslToOklch(parseFloat(h), parseFloat(s), parseFloat(l));
  });

  await writeFile(cssPath, content);
}
```

**Codemod para forwardRef**:
```typescript
async function migrateForwardRef(projectPath: string) {
  const files = await glob(`${projectPath}/components/**/*.tsx`);

  for (const file of files) {
    let content = await readFile(file, 'utf-8');

    // Detectar pattern forwardRef
    const forwardRefPattern = /const (\w+) = React\.forwardRef<([^,]+),\s*([^>]+)>\(\s*\(\s*\{([^}]+)\},\s*ref\s*\)/g;

    content = content.replace(forwardRefPattern, (match, name, refType, propsType, props) => {
      return `function ${name}({ ${props}, ref }: ${propsType} & { ref?: React.Ref<${refType}> })`;
    });

    // Remover .displayName se existir
    content = content.replace(/\w+\.displayName = ['"][^'"]+['"];\n?/g, '');

    await writeFile(file, content);
  }
}
```

### Tailwind v3 -> v4

**Breaking Changes**:
- Nova estrutura de imports
- `@theme` directive
- CSS-first config
- `tailwindcss-animate` -> `tw-animate-css`

**Migracao de globals.css**:
```css
/* ANTES (v3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* DEPOIS (v4) */
@import "tailwindcss";
@import "tw-animate-css";

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  /* ... */
}
```

**Migracao de tailwind.config.ts**:
```typescript
// ANTES (v3)
export default {
  content: [...],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
}

// DEPOIS (v4)
export default {
  content: [...],
  // Maioria das configs agora em CSS
}
```

### Next.js 14 -> 15

**Breaking Changes**:
- `fetch` nao cacheia por default
- Turbopack default em dev
- React 19 support

**Codemod**:
```typescript
async function migrateNextjs14to15(projectPath: string) {
  const files = await glob(`${projectPath}/**/*.{ts,tsx}`);

  for (const file of files) {
    let content = await readFile(file, 'utf-8');

    // Adicionar cache: 'force-cache' onde fetch era cacheado implicitamente
    // (Requer analise manual - apenas alertar)
    if (content.includes('fetch(') && !content.includes('cache:')) {
      console.warn(`${file}: Verificar comportamento de cache do fetch`);
    }

    await writeFile(file, content);
  }

  // Atualizar next.config
  const configPath = `${projectPath}/next.config.ts`;
  let config = await readFile(configPath, 'utf-8');

  // Remover turbo experimental se existir
  config = config.replace(/experimental:\s*\{\s*turbo:\s*true,?\s*\}/g, '');

  await writeFile(configPath, config);
}
```

### React 18 -> 19

**Breaking Changes**:
- `forwardRef` deprecated
- `ref` como prop normal
- Hooks asyncronos

**Codemod**: (mesmo de shadcn v2->v3 para forwardRef)

## Workflow Detalhado

### Etapa 1: Identificar Versoes

```bash
# Verificar versoes atuais
cat package.json | jq '.dependencies, .devDependencies'

# Verificar ultima versao disponivel
npm show @a2ui-bridge/core version
npm show next version
npm show react version
npm show tailwindcss version
```

### Etapa 2: Planejar Migracao

**Output**:
```markdown
# Plano de Migracao

## Atualizacoes Identificadas

| Package | Atual | Target | Tipo |
|---------|-------|--------|------|
| @a2ui-bridge/core | 0.8.2 | 0.9.0 | major |
| react | 18.2.0 | 19.0.0 | major |

## Ordem de Execucao
1. React 18 -> 19 (breaking: forwardRef)
2. shadcn v2 -> v3 (breaking: HSL->OKLCH, forwardRef)
3. Tailwind v3 -> v4 (breaking: imports)
4. A2UI v0.8 -> v0.9 (breaking: beginRendering)

## Risco
Alto - multiplas breaking changes

## Tempo Estimado
30-60 minutos
```

### Etapa 3: Criar Backup

```bash
# Criar branch de backup
git checkout -b backup/pre-migration-$(date +%Y%m%d)
git add -A
git commit -m "Backup before migration"
git checkout -

# Ou backup de arquivos
cp -r . ../${PROJECT_NAME}-backup-$(date +%Y%m%d)
```

### Etapa 4-7: Executar Migracao

Executar codemods na ordem planejada, validando apos cada etapa.

### Etapa 8: Validar Build

```bash
# Limpar cache
rm -rf node_modules .next
npm install

# Build
npm run build

# Se falhar, analisar erros e corrigir manualmente
```

### Etapa 9: Testes Manuais

```markdown
## Checklist de Testes

- [ ] App inicia sem erros
- [ ] Pagina principal carrega
- [ ] Dark mode funciona
- [ ] Componentes shadcn renderizam corretamente
- [ ] Surface A2UI renderiza
- [ ] Streaming funciona
- [ ] Actions disparam corretamente
- [ ] Data binding funciona
```

### Etapa 10: Finalizar

**Se sucesso**:
```bash
git add -A
git commit -m "chore: migrate to A2UI v0.9, React 19, shadcn v3, Tailwind v4"
```

**Se falha**:
```bash
git checkout backup/pre-migration-$(date +%Y%m%d)
# Ou restaurar backup de arquivos
```

## Comandos

```
/a2ui-update --check              # Ver atualizacoes disponiveis
/a2ui-update --major              # Executar todas as migracoes major
/a2ui-update --major --target=a2ui # Migrar apenas A2UI
/a2ui-rollback                    # Reverter ultima migracao
```
