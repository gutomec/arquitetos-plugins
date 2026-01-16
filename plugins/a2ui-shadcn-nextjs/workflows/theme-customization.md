# Workflow: Theme Customization

## Metadata

```yaml
name: a2ui-theme-customization
description: Workflow completo para customizacao de temas A2UI + shadcn
trigger: /a2ui-design ou quando usuario quer customizar visual
version: 1.0.0
```

## Diagrama

```
┌─────────────────┐
│  1. Coletar     │
│   Preferencias  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Analisar    │
│   Tema Atual    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Gerar       │
│   Paleta OKLCH  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. Preview     │
│   (Aprovar)     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Approve│ │Adjust │──┐
└───┬───┘ └───────┘  │
    │        ▲       │
    │        └───────┘
    ▼
┌─────────────────┐
│  5. Gerar CSS   │
│   Variables     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. Dark Mode   │
│   Automatico    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  7. A2UI        │
│   Mapping       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  8. usageHint   │
│   Styles        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  9. Aplicar     │
│   globals.css   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 10. Validar     │
│   e Entregar    │
└─────────────────┘
```

## Etapas Detalhadas

### Etapa 1: Coletar Preferencias

**Agente**: theme-designer

**Perguntas**:
1. Cor primaria? (nome ou hex)
2. Estilo? (minimal/vibrant/brand)
3. Fonte? (inter/geist/system)
4. Bordas? (sharp/rounded/pill)

**Deteccao automatica**:
- Analisar logo/brand se disponivel
- Sugerir cores complementares
- Manter consistencia com existente

### Etapa 2: Analisar Tema Atual

**Agente**: theme-designer

**Verificar**:
```bash
# CSS variables atuais
grep "^  --" app/globals.css

# Formato de cores
grep "oklch\|hsl\|rgb\|#" app/globals.css

# Dark mode
grep -A20 ".dark" app/globals.css
```

**Output**:
```yaml
formato_atual: oklch | hsl | hex
tem_dark_mode: true | false
variaveis_definidas: [lista]
variaveis_faltando: [lista]
```

### Etapa 3: Gerar Paleta OKLCH

**Agente**: theme-designer

**Algoritmo**:
```typescript
function generateOklchPalette(baseColor: string): ColorPalette {
  // 1. Converter para OKLCH se necessario
  const { L, C, H } = toOklch(baseColor);

  // 2. Gerar escala
  return {
    50:  `oklch(0.97 ${C * 0.08} ${H})`,
    100: `oklch(0.93 ${C * 0.20} ${H})`,
    200: `oklch(0.87 ${C * 0.40} ${H})`,
    300: `oklch(0.75 ${C * 0.60} ${H})`,
    400: `oklch(0.62 ${C * 0.80} ${H})`,
    500: `oklch(0.49 ${C} ${H})`,        // Base
    600: `oklch(0.42 ${C * 0.90} ${H})`,
    700: `oklch(0.35 ${C * 0.75} ${H})`,
    800: `oklch(0.28 ${C * 0.58} ${H})`,
    900: `oklch(0.22 ${C * 0.42} ${H})`,
    950: `oklch(0.15 ${C * 0.25} ${H})`,
  };
}
```

### Etapa 4: Preview

**Agente**: theme-designer

**Gerar preview visual**:
```markdown
## Preview da Paleta

### Primary
| Shade | OKLCH | Cor |
|-------|-------|-----|
| 50  | oklch(0.97 0.019 264) | [preview] |
| 500 | oklch(0.49 0.243 264) | [preview] |
| 950 | oklch(0.15 0.061 264) | [preview] |

### Componentes
[Mostrar Button, Card, Input com novo tema]

Aprovar? [S] para continuar, [A] para ajustar
```

### Etapa 5: Gerar CSS Variables

**Agente**: theme-designer

**Template**:
```css
:root {
  /* Background */
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);

  /* Primary */
  --primary: ${primary.500};
  --primary-foreground: oklch(0.985 0 0);

  /* Secondary */
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);

  /* Muted */
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);

  /* Accent */
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);

  /* Destructive */
  --destructive: oklch(0.577 0.245 27);
  --destructive-foreground: oklch(0.985 0 0);

  /* Borders */
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: ${primary.500};

  /* Radius */
  --radius: ${radius};
}
```

### Etapa 6: Dark Mode Automatico

**Agente**: theme-designer

**Inversao inteligente**:
```typescript
function generateDarkTheme(lightVars: CSSVariables): CSSVariables {
  return {
    '--background': invertLightness(lightVars['--foreground']),
    '--foreground': invertLightness(lightVars['--background']),
    '--card': adjustLightness(lightVars['--background'], -0.85),
    '--primary': adjustChroma(lightVars['--primary'], 0.9),
    // ...
  };
}
```

### Etapa 7: A2UI Mapping

**Agente**: theme-designer

**Gerar mapeamento**:
```css
:root {
  /* A2UI Mapping */
  --a2ui-color-primary: var(--primary);
  --a2ui-color-primary-foreground: var(--primary-foreground);
  --a2ui-color-secondary: var(--secondary);
  --a2ui-color-secondary-foreground: var(--secondary-foreground);
  --a2ui-color-background: var(--background);
  --a2ui-color-foreground: var(--foreground);
  --a2ui-color-surface: var(--card);
  --a2ui-color-surface-foreground: var(--card-foreground);
  --a2ui-color-muted: var(--muted);
  --a2ui-color-muted-foreground: var(--muted-foreground);
  --a2ui-color-accent: var(--accent);
  --a2ui-color-accent-foreground: var(--accent-foreground);
  --a2ui-color-destructive: var(--destructive);
  --a2ui-color-destructive-foreground: var(--destructive-foreground);
  --a2ui-color-border: var(--border);
  --a2ui-color-input: var(--input);
  --a2ui-color-ring: var(--ring);
}
```

### Etapa 8: usageHint Styles

**Agente**: theme-designer

**Gerar estilos semanticos**:
```css
/* Typography Hints */
[data-usage-hint="h1"] {
  font-size: var(--a2ui-text-4xl, 2.25rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.025em;
}

[data-usage-hint="h2"] {
  font-size: var(--a2ui-text-3xl, 1.875rem);
  font-weight: 600;
  line-height: 1.2;
}

/* ... h3, h4, h5, body, caption */

/* State Hints */
[data-state="disabled"] {
  opacity: 0.5;
  pointer-events: none;
}

[data-state="loading"] {
  cursor: wait;
}

[data-state="error"] {
  border-color: var(--a2ui-color-destructive);
}
```

### Etapa 9: Aplicar globals.css

**Agente**: theme-designer

**Processo**:
1. Backup do globals.css atual
2. Gerar novo globals.css completo
3. Salvar arquivo

```css
@import "tailwindcss";
@import "tw-animate-css";

:root {
  ${lightVariables}
  ${a2uiMapping}
}

.dark {
  ${darkVariables}
}

${usageHintStyles}
```

### Etapa 10: Validar e Entregar

**Agente**: a2ui-analyzer

**Validacoes**:
```bash
# Build
npm run build

# Dev server
npm run dev &
sleep 5
curl http://localhost:3000
```

**Output**:
```markdown
# Tema Aplicado com Sucesso!

## Cores Principais
- Primary: ${primary}
- Background: ${background}

## Arquivos Modificados
- `app/globals.css`

## Preview
Acesse: http://localhost:3000

## Ajustes
- Dark mode: `/a2ui-design dark`
- Apenas cores: `/a2ui-design colors --color=nova-cor`

## Backup
Disponivel em: `app/globals.css.bak`
```

## Presets Disponiveis

### Minimal
```yaml
primary: neutral (sem chroma)
style: clean, monocromatico
radius: 0.5rem
```

### Vibrant
```yaml
primary: indigo (alto chroma)
style: colorido, gradientes sutis
radius: 0.75rem
```

### Brand
```yaml
primary: extraido de brand guidelines
style: consistente com identidade
radius: variavel
```
