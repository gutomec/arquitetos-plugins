# Skill: A2UI Project Analyzer

## Metadata

```yaml
name: a2ui-analyze
version: 1.0.0
description: Analisa projetos A2UI + shadcn para identificar problemas, inconsistencias e oportunidades de melhoria
trigger: Quando usuario pede para analisar, revisar, verificar, auditar projeto A2UI
```

## Progressive Disclosure

### Level 1: Quick Check (Default)

**Trigger**: "analise rapida", "verificar projeto", "ta tudo certo?"

**Acao**:
1. Verificar arquivos essenciais existem
2. Verificar dependencias instaladas
3. Verificar configuracao basica

**Output resumido**:
```
Status: OK | WARNING | CRITICAL

Arquivos essenciais: OK
Dependencias: OK
Configuracao: 1 warning
```

---

### Level 2: Full Analysis

**Trigger**: "analise completa", "auditoria", "revisao profunda"

**Acao**:
1. Analise de estrutura de projeto
2. Analise de protocolo A2UI
3. Analise de adapters
4. Analise de theming
5. Analise de performance
6. Analise de seguranca

**Output detalhado**: Relatorio completo com todos os findings.

---

### Level 3: Specific Analysis

**Trigger**: "analise X especificamente" (protocolo, adapters, theme, etc)

**Acao**: Focar na area especifica solicitada.

---

## Checklist de Analise

### 1. Estrutura do Projeto

```typescript
const projectStructureChecks = [
  'components.json existe',
  'package.json tem dependencias A2UI',
  'tailwind.config.ts configurado',
  'app/globals.css tem CSS variables',
  'app/providers.tsx configura providers',
  'adapters/ tem catalogo',
];
```

### 2. Dependencias

```typescript
const requiredDeps = [
  '@a2ui-bridge/core',
  '@a2ui-bridge/react',
  '@a2ui-bridge/react-shadcn',
  // ou
  '@zhama/a2ui',
  // ou
  '@xpert-ai/a2ui-react',
];

const shadcnDeps = [
  'tailwindcss',
  'tailwind-merge',
  'clsx',
  'class-variance-authority',
  '@radix-ui/*',
];
```

### 3. Protocolo A2UI

**Verificar em arquivos que geram A2UI JSON:**

```typescript
const protocolChecks = [
  // Estrutura de mensagens
  'surfaceUpdate tem surfaceId',
  'surfaceUpdate tem components array',
  'components tem id unico',
  'components tem component object',

  // Componentes
  'Componentes usam nomes do catalogo',
  'children referenciam IDs existentes',
  'usageHints usam valores validos',

  // Data binding
  'text usa literalString ou path',
  'path usa JSON Pointer valido',

  // Actions
  'action tem name',
  'context e array de {key, value}',
];
```

### 4. Adapters

```typescript
const adapterChecks = [
  // Registro
  'Catalogo exporta todos adapters',
  'Surface recebe components prop',

  // Implementacao
  'createAdapter usado corretamente',
  'mapProps implementado',
  'extractValue usado para text',
  'renderChild usado para children',
  'onAction chamado para events',

  // TypeScript
  'Props A2UI tipadas',
  'Props shadcn tipadas',
];
```

### 5. Theming

```typescript
const themeChecks = [
  // CSS Variables
  ':root define todas as variaveis',
  '.dark define variaveis dark mode',
  'Variaveis usam OKLCH (recomendado)',

  // A2UI mapping
  '--a2ui-* mapeiam para --shadcn',
  'usageHint styles definidos',

  // Provider
  'ThemeProvider configurado',
  'attribute="class" presente',
  'enableSystem para preferencia do sistema',
];
```

### 6. Performance

```typescript
const performanceChecks = [
  // Streaming
  'API retorna stream JSONL',
  'Content-Type: application/x-ndjson',
  'Mensagens processadas incrementalmente',

  // Bundle
  'Imports especificos (nao import *)',
  'Dynamic imports onde apropriado',

  // Rendering
  'Componentes usam memo se necessario',
  'Keys unicos em listas',
];
```

### 7. Seguranca

```typescript
const securityChecks = [
  // A2UI
  'Catalogo restrito (sem componentes arbitrarios)',
  'JSON validado antes de processar',
  'Sem eval ou execucao de codigo',

  // Input
  'User input sanitizado',
  'Sem interpolacao direta de dados',

  // API
  'Rate limiting implementado',
  'Autenticacao se necessario',
];
```

## Implementacao

### Funcao Principal

```typescript
async function analyzeA2UIProject(level: 1 | 2 | 3 = 1): Promise<AnalysisReport> {
  const report: AnalysisReport = {
    status: 'OK',
    summary: [],
    critical: [],
    warnings: [],
    info: [],
    recommendations: [],
  };

  // Level 1: Quick checks
  await checkProjectStructure(report);
  await checkDependencies(report);
  await checkBasicConfig(report);

  if (level >= 2) {
    // Level 2: Full analysis
    await analyzeProtocol(report);
    await analyzeAdapters(report);
    await analyzeTheming(report);
    await analyzePerformance(report);
    await analyzeSecurity(report);
  }

  // Determinar status final
  if (report.critical.length > 0) {
    report.status = 'CRITICAL';
  } else if (report.warnings.length > 0) {
    report.status = 'WARNING';
  }

  return report;
}
```

### Verificar Estrutura

```typescript
async function checkProjectStructure(report: AnalysisReport) {
  const requiredFiles = [
    'components.json',
    'package.json',
    'tailwind.config.ts',
    'app/globals.css',
    'app/layout.tsx',
  ];

  for (const file of requiredFiles) {
    const exists = await fileExists(file);
    if (!exists) {
      report.critical.push({
        type: 'MISSING_FILE',
        file,
        message: `Arquivo obrigatorio ausente: ${file}`,
        solution: `Criar ${file} ou rodar npx shadcn@latest init`,
      });
    }
  }
}
```

### Verificar Protocolo

```typescript
async function analyzeProtocol(report: AnalysisReport) {
  // Buscar arquivos que podem conter A2UI JSON
  const files = await glob('**/*.{ts,tsx,json}');

  for (const file of files) {
    const content = await readFile(file);

    // Procurar patterns problematicos
    if (content.includes('fontSize') && content.includes('surfaceUpdate')) {
      report.warnings.push({
        type: 'VISUAL_STYLE_IN_PROTOCOL',
        file,
        message: 'Possivel estilo visual no JSON A2UI',
        solution: 'Use usageHints ao inves de propriedades visuais',
      });
    }

    // Verificar IDs duplicados
    const idMatches = content.match(/"id":\s*"([^"]+)"/g);
    if (idMatches) {
      const ids = idMatches.map(m => m.match(/"([^"]+)"$/)?.[1]);
      const duplicates = ids.filter((id, i) => ids.indexOf(id) !== i);
      if (duplicates.length > 0) {
        report.critical.push({
          type: 'DUPLICATE_IDS',
          file,
          message: `IDs duplicados encontrados: ${duplicates.join(', ')}`,
          solution: 'IDs devem ser unicos dentro de cada surface',
        });
      }
    }
  }
}
```

## Output Format

### Level 1 (Resumido)

```markdown
# Analise Rapida A2UI

Status: OK

| Area | Status |
|------|--------|
| Estrutura | OK |
| Dependencias | OK |
| Configuracao | OK |

Projeto pronto para uso.
```

### Level 2 (Detalhado)

```markdown
# Relatorio de Analise A2UI

## Resumo Executivo

- **Status**: WARNING
- **Arquivos analisados**: 47
- **Criticos**: 0
- **Alertas**: 3
- **Informacoes**: 5

## Problemas Criticos

Nenhum problema critico encontrado.

## Alertas

### 1. [WARNING] Possivel estilo visual no protocolo

- **Arquivo**: app/api/agent/route.ts:45
- **Descricao**: Encontrado `fontSize` em mensagem A2UI
- **Impacto**: Estilos visuais sao ignorados pelo renderer
- **Solucao**: Substituir por `usageHint: "h1"`

### 2. [WARNING] CSS variable A2UI nao mapeada

- **Arquivo**: app/globals.css
- **Descricao**: `--a2ui-color-success` nao definida
- **Solucao**: Adicionar mapeamento para var(--success)

### 3. [WARNING] Adapter sem tipagem

- **Arquivo**: adapters/CustomAdapter.ts
- **Descricao**: Props A2UI nao tipadas
- **Solucao**: Adicionar interface A2UICustomProps

## Boas Praticas Seguidas

- [x] Catalogo de componentes restrito
- [x] Streaming JSONL implementado
- [x] ThemeProvider configurado
- [x] Dark mode funcional
- [x] CSS variables unificadas

## Recomendacoes

1. Adicionar testes para adapters customizados
2. Implementar validacao de JSON A2UI
3. Adicionar error boundary para Surface
4. Considerar lazy loading de adapters

## Proximos Passos

1. Corrigir alertas identificados
2. Rodar analise novamente
3. Implementar recomendacoes
```

## Comandos Relacionados

- `/a2ui-analyze` - Executar analise
- `/a2ui-analyze-protocol` - Focar em protocolo
- `/a2ui-analyze-adapters` - Focar em adapters
- `/a2ui-analyze-theme` - Focar em theming
