# Workflow: Diagnose and Fix

## Metadata

```yaml
name: a2ui-diagnose-fix
description: Workflow para diagnosticar e corrigir problemas em projetos A2UI
trigger: /a2ui-fix ou quando usuario reporta erro/problema
version: 1.0.0
```

## Diagrama

```
┌─────────────────┐
│  1. Coletar     │
│    Sintomas     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Auto-Detect │
│    Problemas    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Categorizar │
│    Problema     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Install│ │Styles │ ...
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│  4. Diagnostico │
│    Especifico   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. Propor Fix  │
│  (Confirmar)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. Aplicar Fix │
│    (Backup)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  7. Validar     │
│   Correcao      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│  OK   │ │ Fail  │
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│Report │ │Rollback│
└───────┘ │+ Deep │
          │ Debug │
          └───────┘
```

## Etapas Detalhadas

### Etapa 1: Coletar Sintomas

**Agente**: shadcn-fixer

**Inputs**:
- Descricao do usuario (se fornecida)
- Mensagens de erro (se fornecidas)
- Comportamento observado

**Categorizacao inicial**:
```typescript
type ProblemCategory =
  | 'installation'  // CLI, deps, config
  | 'styles'        // CSS, theme, dark mode
  | 'runtime'       // hydration, render, streaming
  | 'protocol'      // A2UI messages, adapters, actions
  | 'unknown';      // Precisa investigacao
```

### Etapa 2: Auto-Detect Problemas

**Agente**: a2ui-analyzer

**Verificacoes**:
```bash
# Estrutura
ls -la components.json package.json app/globals.css

# Dependencias
grep "@a2ui" package.json
grep "tailwindcss" package.json

# Configuracao
grep ":root" app/globals.css
grep "ThemeProvider" app/
grep "A2UIBridgeProvider" app/

# Erros
npm run build 2>&1 | head -50
```

### Etapa 3: Categorizar Problema

**Agente**: shadcn-fixer

**Mapa de Problemas**:

| Sintoma | Categoria | Problema |
|---------|-----------|----------|
| command not found: shadcn | installation | P1 |
| Module not found: @a2ui | installation | P2 |
| Could not find components.json | installation | P3 |
| Componentes sem estilo | styles | P4 |
| Dark mode nao funciona | styles | P5 |
| Classes Tailwind ignoradas | styles | P6 |
| Hydration failed | runtime | P7 |
| Surface em branco | runtime | P8 |
| UI nao atualiza | runtime | P9 |
| Unknown component | protocol | P10 |
| Action nao dispara | protocol | P11 |
| Data binding quebrado | protocol | P12 |

### Etapa 4: Diagnostico Especifico

**Agente**: shadcn-fixer

**Para cada problema, executar comandos de diagnostico**:

```typescript
const diagnostics: Record<string, string[]> = {
  P1: ['which shadcn', 'npm list shadcn'],
  P4: ['grep "globals.css" app/layout.tsx', 'grep ":root" app/globals.css'],
  P5: ['grep "ThemeProvider" app/', 'grep ".dark" app/globals.css'],
  P7: ['grep -r "window\\." components/', 'grep -r "document\\." components/'],
  P8: ['grep "A2UIBridgeProvider" app/', 'grep "components=" app/'],
  // ...
};
```

### Etapa 5: Propor Fix

**Agente**: shadcn-fixer

**Formato**:
```markdown
## Problema Detectado: P${N}

**Descricao**: [descricao]

**Causa**: [causa raiz]

**Fix Proposto**:
[codigo ou comandos]

**Arquivos Afetados**:
- file1.tsx
- file2.css

Confirmar aplicacao? [S/n]
```

### Etapa 6: Aplicar Fix

**Agente**: shadcn-fixer

**Processo**:
1. Criar backup dos arquivos afetados
2. Aplicar mudancas
3. Salvar log de alteracoes

```bash
# Backup
cp file.tsx file.tsx.bak

# Aplicar fix
[editar arquivo]

# Log
echo "$(date): Fixed P${N} in file.tsx" >> .a2ui-fix.log
```

### Etapa 7: Validar Correcao

**Agente**: a2ui-analyzer

**Verificacoes pos-fix**:
```bash
# Build
npm run build

# Se necessario, verificacao especifica
npm run dev &
curl -s http://localhost:3000 | grep -q "expected"
```

### Etapa 8a: Sucesso - Report

**Output**:
```markdown
# Fix Report

## Problema
P${N}: [descricao]

## Solucao Aplicada
[descricao da solucao]

## Arquivos Modificados
- `path/file.tsx` - [mudanca]

## Validacao
[x] Build passou
[x] Verificacao especifica passou

## Backup
Disponivel em: `path/file.tsx.bak`
```

### Etapa 8b: Falha - Rollback + Deep Debug

**Agente**: a2ui-analyzer (Level 3)

**Acoes**:
1. Restaurar backup
2. Executar analise profunda
3. Investigar causas alternativas
4. Propor solucao manual ou escalacao

```markdown
# Fix Falhou

## Problema Persiste
O fix aplicado nao resolveu o problema.

## Backup Restaurado
Arquivos originais restaurados.

## Investigacao Profunda
[resultados da analise]

## Proximos Passos
1. [sugestao 1]
2. [sugestao 2]
3. Considerar: `/a2ui-analyze --level=deep`
```

## Casos Especiais

### Multiplos Problemas

Se detectados multiplos problemas:
1. Ordenar por criticidade
2. Fixar um por vez
3. Validar apos cada fix
4. Continuar ate resolver todos

### Problema Desconhecido

Se problema nao se encaixa em nenhuma categoria:
1. Coletar mais informacoes do usuario
2. Analisar logs e erros
3. Comparar com setup de referencia
4. Propor investigacao manual

## Metricas

Rastrear para melhoria continua:
- Tempo medio de resolucao por categoria
- Taxa de sucesso por problema
- Problemas mais frequentes
- Eficacia dos fixes
