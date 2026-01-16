# Command: /a2ui-analyze

## Metadata

```yaml
name: a2ui-analyze
description: Analisa projeto A2UI + shadcn para identificar problemas e oportunidades
usage: /a2ui-analyze [--level=quick|full|deep] [--focus=protocol|adapters|theme|all]
```

## Prompt

Voce e o A2UI Project Analyzer. Analise o projeto atual para identificar problemas, inconsistencias e oportunidades de melhoria.

## Instrucoes

### 1. Determinar Nivel de Analise

- **quick** (default): Verificacoes essenciais (< 1 min)
- **full**: Analise completa de todos os aspectos
- **deep**: Analise profunda com sugestoes de otimizacao

### 2. Verificacoes por Nivel

**Quick (Level 1):**
```typescript
const quickChecks = [
  'components.json existe',
  'package.json tem @a2ui-bridge/*',
  'app/globals.css tem CSS variables',
  'app/providers.tsx configura A2UIBridgeProvider',
];
```

**Full (Level 2):**
- Todas as verificacoes de Level 1
- Analise de protocolo A2UI
- Validacao de adapters
- Verificacao de theming
- Performance basica

**Deep (Level 3):**
- Todas as verificacoes anteriores
- Analise de seguranca
- Bundle size
- Acessibilidade
- Boas praticas
- Comparacao com setup ideal

### 3. Focos Especificos

**--focus=protocol:**
- Estrutura de mensagens A2UI
- IDs unicos
- Adjacency list
- usageHints validos
- Data binding correto

**--focus=adapters:**
- Registro no catalogo
- mapProps implementado
- extractValue para text
- renderChild para children
- onAction para eventos

**--focus=theme:**
- CSS variables completas
- Dark mode configurado
- OKLCH format
- A2UI mapping
- usageHint styles

### 4. Gerar Relatorio

**Formato Quick:**
```markdown
# Analise Rapida A2UI

Status: OK | WARNING | CRITICAL

| Area | Status |
|------|--------|
| Estrutura | OK |
| Deps | OK |
| Config | 1 warning |

[Detalhes se houver problemas]
```

**Formato Full/Deep:**
```markdown
# Relatorio de Analise A2UI

## Resumo Executivo
- Status: [STATUS]
- Arquivos analisados: [N]
- Criticos: [N]
- Alertas: [N]

## Problemas Criticos
[Lista detalhada]

## Alertas
[Lista detalhada]

## Recomendacoes
[Lista priorizada]
```

## Exemplos

```
/a2ui-analyze
/a2ui-analyze --level=full
/a2ui-analyze --focus=protocol
/a2ui-analyze --level=deep --focus=adapters
```

## Agente

Usar: `a2ui-analyzer`

## Skill

Invocar: `a2ui-analyze` com level apropriado
