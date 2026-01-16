# Skill: A2UI + shadcn Updater

## Metadata

```yaml
name: a2ui-update
version: 1.0.0
description: Atualiza projetos A2UI + shadcn para versoes mais recentes com migracao segura
trigger: Quando usuario pede para atualizar, migrar, upgrade, ou menciona nova versao
```

## Progressive Disclosure

### Level 1: Check for Updates

**Trigger**: "tem atualizacao?", "verificar versoes"

**Acao**:
1. Verificar versoes instaladas
2. Comparar com versoes mais recentes
3. Listar atualizacoes disponiveis

---

### Level 2: Safe Update

**Trigger**: "atualizar", "upgrade"

**Acao**:
1. Criar backup
2. Atualizar dependencias compatíveis
3. Rodar migrações automaticas
4. Validar funcionamento

---

### Level 3: Major Migration

**Trigger**: "migrar para v2", "atualizar major", "breaking changes"

**Acao**:
1. Analise de impacto
2. Plano de migracao detalhado
3. Migracao passo a passo com validacao
4. Rollback se necessario

---

## Atualizacoes Cobertas

### 1. A2UI Protocol v0.8 -> v0.9

**Breaking Changes**:
- `beginRendering` -> `createSurface`
- Theming removido das mensagens
- Adjacency list obrigatório

**Migracao**:
```typescript
// ANTES (v0.8)
{
  beginRendering: {
    surfaceId: "main",
    root: "header",
    styles: { primaryColor: "#6366f1" }  // REMOVIDO em v0.9
  }
}

// DEPOIS (v0.9)
{
  createSurface: {
    surfaceId: "main",
    root: "header"
    // Sem styles - theming e no cliente
  }
}
```

**Script de migracao**:
```typescript
async function migrateA2UIv08tov09() {
  // 1. Buscar arquivos com beginRendering
  const files = await glob('**/*.{ts,tsx}');

  for (const file of files) {
    let content = await readFile(file);

    // 2. Substituir beginRendering por createSurface
    content = content.replace(/beginRendering/g, 'createSurface');

    // 3. Remover propriedade styles
    content = content.replace(/,?\s*styles:\s*\{[^}]+\}/g, '');

    // 4. Salvar
    await writeFile(file, content);
  }

  // 5. Atualizar dependencias
  await exec('npm install @a2ui-bridge/core@latest @a2ui-bridge/react@latest');
}
```

---

### 2. shadcn/ui v2 -> v3

**Breaking Changes**:
- Radix -> Base UI (algumas APIs mudam)
- HSL -> OKLCH colors
- Novos estilos: Nova, Maia, Lyra
- `forwardRef` removido (React 19)
- `data-slot` adicionado

**Migracao**:
```bash
# Backup primeiro
cp -r components/ui components/ui.backup

# Atualizar CLI
npx shadcn@latest diff

# Re-adicionar componentes atualizados
npx shadcn@latest add button -o
npx shadcn@latest add card -o
# ... para cada componente
```

**Migracao de cores**:
```css
/* ANTES (HSL) */
:root {
  --primary: 222.2 47.4% 11.2%;
}

/* DEPOIS (OKLCH) */
:root {
  --primary: oklch(0.205 0.025 265.754);
}
```

**Script de conversao HSL -> OKLCH**:
```typescript
function hslToOklch(h: number, s: number, l: number): string {
  // Converter HSL para RGB
  // Converter RGB para OKLCH
  // Retornar string formatada
  return `oklch(${L.toFixed(3)} ${C.toFixed(3)} ${H.toFixed(3)})`;
}

async function migrateColorsToOklch() {
  const cssFile = 'app/globals.css';
  let content = await readFile(cssFile);

  // Regex para encontrar HSL
  const hslRegex = /(\d+\.?\d*)\s+(\d+\.?\d*)%\s+(\d+\.?\d*)%/g;

  content = content.replace(hslRegex, (match, h, s, l) => {
    return hslToOklch(parseFloat(h), parseFloat(s), parseFloat(l));
  });

  await writeFile(cssFile, content);
}
```

---

### 3. Tailwind v3 -> v4

**Breaking Changes**:
- Nova estrutura de config
- `@theme` directive
- Cores inline
- Removido `tailwindcss-animate`

**Migracao**:
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
  /* ... */
}
```

```typescript
// ANTES (tailwind.config.ts v3)
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

// DEPOIS (tailwind.config.ts v4)
// Maioria das configs movidas para CSS
export default {
  content: [...],
}
```

---

### 4. Next.js 14 -> 15

**Breaking Changes**:
- `fetch` cache diferente
- Turbopack default
- React 19 support

**Migracao**:
```typescript
// Atualizar next.config
const nextConfig = {
  // Turbopack agora e default em dev
  experimental: {
    // turbo: true, // Nao precisa mais
  }
};

// Fetch agora nao cacheia por default
// ANTES
fetch(url) // Cacheava automaticamente

// DEPOIS
fetch(url, { cache: 'force-cache' }) // Explicito
```

---

### 5. React 18 -> 19

**Breaking Changes**:
- `forwardRef` deprecated
- `ref` como prop normal
- Hooks asyncronos

**Migracao para componentes shadcn**:
```typescript
// ANTES (React 18)
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, ...props }, ref) => (
    <button ref={ref} className={className} {...props} />
  )
);

// DEPOIS (React 19)
function Button({ className, ref, ...props }: ButtonProps) {
  return <button ref={ref} className={className} {...props} />;
}
```

---

## Workflow de Update

```typescript
async function updateA2UIProject(target?: string) {
  // 1. Verificar versoes atuais
  const current = await getCurrentVersions();
  console.log('Versoes atuais:', current);

  // 2. Verificar versoes disponiveis
  const available = await getAvailableUpdates();
  console.log('Updates disponiveis:', available);

  // 3. Criar backup
  await createBackup();

  // 4. Aplicar updates
  for (const update of available) {
    if (target && update.name !== target) continue;

    console.log(`Atualizando ${update.name}...`);

    // 4.1. Atualizar dependencia
    await exec(`npm install ${update.package}@${update.version}`);

    // 4.2. Rodar migracao se houver
    if (update.migration) {
      await update.migration();
    }

    // 4.3. Validar
    const valid = await validateUpdate(update);
    if (!valid) {
      console.log(`Falha na atualizacao de ${update.name}. Revertendo...`);
      await restoreBackup();
      return;
    }
  }

  // 5. Limpar backup se tudo ok
  await cleanupBackup();

  console.log('Atualizacao concluida com sucesso!');
}
```

## Verificacao de Versoes

```typescript
async function getCurrentVersions() {
  const pkg = await readJson('package.json');

  return {
    a2ui: pkg.dependencies['@a2ui-bridge/core'] || pkg.dependencies['@zhama/a2ui'],
    shadcn: 'Verificar via components.json style',
    tailwind: pkg.devDependencies['tailwindcss'],
    nextjs: pkg.dependencies['next'],
    react: pkg.dependencies['react'],
  };
}

async function getAvailableUpdates() {
  const current = await getCurrentVersions();

  // Verificar npm para ultimas versoes
  // Comparar e retornar lista de updates
}
```

## Comandos Relacionados

- `/a2ui-update` - Verificar e aplicar updates
- `/a2ui-update-check` - Apenas verificar
- `/a2ui-migrate-a2ui` - Migrar A2UI
- `/a2ui-migrate-shadcn` - Migrar shadcn
- `/a2ui-migrate-tailwind` - Migrar Tailwind
