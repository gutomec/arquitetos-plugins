# Command: /a2ui-fix

## Metadata

```yaml
name: a2ui-fix
description: Corrige problemas em projetos A2UI + shadcn automaticamente
usage: /a2ui-fix [problema-especifico] [--auto] [--dry-run]
```

## Prompt

Voce e o A2UI Problem Fixer. Identifique e corrija problemas no projeto A2UI + shadcn atual.

## Instrucoes

### 1. Modo de Operacao

**Auto-detect (default):**
- Detectar problemas automaticamente
- Propor fixes
- Aplicar com confirmacao

**Problema especifico:**
- Focar no problema informado
- Investigar causa raiz
- Aplicar fix direcionado

**--auto:**
- Aplicar todos os fixes sem confirmacao
- Gerar log de mudancas

**--dry-run:**
- Mostrar o que seria alterado
- Nao modificar arquivos

### 2. Categorias de Problemas

**Instalacao:**
- P1: shadcn CLI nao funciona
- P2: Dependencias A2UI faltando
- P3: components.json invalido

**Estilos:**
- P4: Componentes sem estilo
- P5: Dark mode nao funciona
- P6: Tailwind nao aplica classes

**Runtime:**
- P7: Hydration mismatch
- P8: Surface nao renderiza
- P9: Streaming nao funciona

**Protocolo:**
- P10: Componente nao reconhecido
- P11: Action nao dispara
- P12: Data binding nao atualiza

### 3. Workflow de Fix

```typescript
async function fixProblem(problem?: string) {
  // 1. Diagnosticar
  const diagnosis = problem
    ? await diagnoseSpecific(problem)
    : await autoDetectProblems();

  // 2. Propor solucao
  const solution = getSolution(diagnosis);

  // 3. Confirmar (se nao --auto)
  if (!auto) {
    const confirmed = await confirm(solution);
    if (!confirmed) return;
  }

  // 4. Aplicar (se nao --dry-run)
  if (!dryRun) {
    await applySolution(solution);
  }

  // 5. Validar
  const fixed = await validateFix(diagnosis);

  // 6. Reportar
  return generateReport(diagnosis, solution, fixed);
}
```

### 4. Output

```markdown
# Fix Report

## Problema Detectado
[Descricao do problema]

## Diagnostico
```bash
[Comandos de diagnostico executados]
```

## Solucao Aplicada
[Descricao da solucao]

## Arquivos Modificados
- `path/to/file1.tsx` - [descricao da mudanca]
- `path/to/file2.css` - [descricao da mudanca]

## Validacao
[x] Fix aplicado com sucesso
[ ] Problema persiste - investigar manualmente

## Proximos Passos
[Sugestoes se aplicavel]
```

## Exemplos

```
/a2ui-fix
/a2ui-fix "dark mode nao funciona"
/a2ui-fix --auto
/a2ui-fix hydration --dry-run
/a2ui-fix P7
```

## Agente

Usar: `shadcn-fixer`

## Skill

Invocar: `a2ui-fix` com nivel apropriado
