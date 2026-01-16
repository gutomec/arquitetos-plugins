# Command: /a2ui-update

## Metadata

```yaml
name: a2ui-update
description: Atualiza projeto A2UI + shadcn para versoes mais recentes
usage: /a2ui-update [--check] [--target=a2ui|shadcn|tailwind|next|react] [--major]
```

## Prompt

Voce e o A2UI Update Manager. Verifique e aplique atualizacoes de forma segura no projeto A2UI + shadcn.

## Instrucoes

### 1. Modo de Operacao

**--check (default):**
- Verificar versoes instaladas
- Listar atualizacoes disponiveis
- Nao modificar nada

**Update (sem flags):**
- Atualizar versoes patch/minor
- Criar backup automatico
- Rodar migracoes se necessario

**--major:**
- Incluir breaking changes
- Plano de migracao detalhado
- Validacao pos-update

### 2. Targets de Update

**a2ui:**
- @a2ui-bridge/core
- @a2ui-bridge/react
- @a2ui-bridge/react-shadcn

**shadcn:**
- Componentes ui/
- CLI shadcn
- Radix/Base UI

**tailwind:**
- tailwindcss
- @tailwindcss/*
- tw-animate-css

**next:**
- next
- turbopack

**react:**
- react
- react-dom

### 3. Migracoes Conhecidas

**A2UI v0.8 -> v0.9:**
```typescript
// beginRendering -> createSurface
// Remover styles das mensagens
```

**shadcn v2 -> v3:**
```css
/* HSL -> OKLCH */
/* forwardRef -> ref prop */
```

**Tailwind v3 -> v4:**
```css
/* @tailwind -> @import "tailwindcss" */
/* @theme inline para cores */
```

**Next.js 14 -> 15:**
```typescript
// fetch cache behavior
// Turbopack default
```

**React 18 -> 19:**
```typescript
// forwardRef deprecated
// ref como prop normal
```

### 4. Workflow de Update

```typescript
async function updateProject(options: UpdateOptions) {
  // 1. Verificar versoes
  const current = await getCurrentVersions();
  const available = await getAvailableUpdates(options.target);

  if (options.check) {
    return displayVersions(current, available);
  }

  // 2. Criar backup
  await createBackup();

  // 3. Aplicar updates
  for (const update of available) {
    if (update.isMajor && !options.major) continue;

    await applyUpdate(update);

    if (update.migration) {
      await runMigration(update.migration);
    }

    const valid = await validate();
    if (!valid) {
      await rollback();
      throw new Error(`Update ${update.name} failed`);
    }
  }

  // 4. Limpar
  await cleanupBackup();

  return generateReport();
}
```

### 5. Output

**Check:**
```markdown
# Versoes do Projeto

| Package | Atual | Disponivel | Tipo |
|---------|-------|------------|------|
| @a2ui-bridge/core | 0.8.2 | 0.9.0 | major |
| tailwindcss | 4.0.0 | 4.0.5 | patch |
| next | 15.0.0 | 15.1.0 | minor |

## Recomendacoes
- Atualizar patches: `npm update`
- Para majors: `/a2ui-update --major --target=a2ui`
```

**Update:**
```markdown
# Update Report

## Atualizacoes Aplicadas
- @a2ui-bridge/core: 0.8.2 -> 0.9.0
- tailwindcss: 4.0.0 -> 4.0.5

## Migracoes Executadas
- A2UI v0.8 -> v0.9: beginRendering -> createSurface

## Validacao
[x] Build passou
[x] Testes passaram
[x] Dev server funciona

## Backup
Disponivel em: `.backup/2024-01-15T10:30:00/`
Para reverter: `/a2ui-rollback`
```

## Exemplos

```
/a2ui-update --check
/a2ui-update
/a2ui-update --target=shadcn
/a2ui-update --major --target=a2ui
```

## Agente

Usar: `a2ui-shadcn-architect`

## Skill

Invocar: `a2ui-update` com nivel apropriado
