# Skill: A2UI + shadcn Designer

## Metadata

```yaml
name: a2ui-design
version: 1.0.0
description: Cria e customiza temas visuais para projetos A2UI + shadcn com foco em design system coeso
trigger: Quando usuario pede para criar tema, customizar cores, design, visual, dark mode
```

## Progressive Disclosure

### Level 1: Quick Theme

**Trigger**: "mudar cor primaria", "tema azul", "customizacao simples"

**Acao**:
1. Identificar cor desejada
2. Gerar paleta automatica
3. Aplicar em globals.css

---

### Level 2: Full Theme

**Trigger**: "criar tema", "design system", "customizacao completa"

**Acao**:
1. Coletar requisitos (cores, tipografia, espacamento)
2. Gerar paleta completa (light + dark)
3. Criar mapeamento A2UI
4. Configurar usageHints

---

### Level 3: Brand Theme

**Trigger**: "tema da marca", "identidade visual", "brand guidelines"

**Acao**:
1. Analisar brand guidelines
2. Extrair cores e tipografia
3. Criar design tokens
4. Implementar tema completo
5. Documentar uso

---

## Geracao de Paletas OKLCH

### Cor Primaria -> Paleta Completa

```typescript
interface ColorPalette {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string; // Base
  600: string;
  700: string;
  800: string;
  900: string;
  950: string;
}

function generateOklchPalette(baseHue: number, baseChroma: number): ColorPalette {
  return {
    50:  `oklch(0.97 ${(baseChroma * 0.08).toFixed(3)} ${baseHue})`,
    100: `oklch(0.93 ${(baseChroma * 0.20).toFixed(3)} ${baseHue})`,
    200: `oklch(0.87 ${(baseChroma * 0.40).toFixed(3)} ${baseHue})`,
    300: `oklch(0.75 ${(baseChroma * 0.60).toFixed(3)} ${baseHue})`,
    400: `oklch(0.62 ${(baseChroma * 0.80).toFixed(3)} ${baseHue})`,
    500: `oklch(0.49 ${baseChroma.toFixed(3)} ${baseHue})`, // Base
    600: `oklch(0.42 ${(baseChroma * 0.90).toFixed(3)} ${baseHue})`,
    700: `oklch(0.35 ${(baseChroma * 0.75).toFixed(3)} ${baseHue})`,
    800: `oklch(0.28 ${(baseChroma * 0.58).toFixed(3)} ${baseHue})`,
    900: `oklch(0.22 ${(baseChroma * 0.42).toFixed(3)} ${baseHue})`,
    950: `oklch(0.15 ${(baseChroma * 0.25).toFixed(3)} ${baseHue})`,
  };
}
```

### Cores Pre-definidas

| Cor | Hue | Chroma | OKLCH Base |
|-----|-----|--------|------------|
| Red | 27 | 0.245 | `oklch(0.577 0.245 27)` |
| Orange | 41 | 0.222 | `oklch(0.646 0.222 41)` |
| Yellow | 84 | 0.189 | `oklch(0.828 0.189 84)` |
| Green | 142 | 0.200 | `oklch(0.600 0.200 142)` |
| Teal | 185 | 0.118 | `oklch(0.600 0.118 185)` |
| Blue | 244 | 0.200 | `oklch(0.500 0.200 244)` |
| Indigo | 264 | 0.243 | `oklch(0.488 0.243 264)` |
| Purple | 304 | 0.265 | `oklch(0.627 0.265 304)` |
| Pink | 350 | 0.230 | `oklch(0.650 0.230 350)` |

---

## Templates de Tema

### Tema Minimal (Neutral)

```css
:root {
  /* Background */
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);

  /* Cards */
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);

  /* Popover */
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);

  /* Primary - Neutral/Slate */
  --primary: oklch(0.205 0 0);
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
  --ring: oklch(0.708 0 0);

  /* Radius */
  --radius: 0.5rem;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.396 0.141 27);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(0.269 0 0);
  --input: oklch(0.269 0 0);
  --ring: oklch(0.439 0 0);
}
```

### Tema Vibrant (Colorido)

```css
:root {
  /* Gradients de fundo sutis */
  --background: oklch(0.99 0.005 264);
  --foreground: oklch(0.145 0.02 264);

  /* Primary - Indigo vibrante */
  --primary: oklch(0.55 0.28 264);
  --primary-foreground: oklch(0.99 0.01 264);

  /* Secondary - Teal */
  --secondary: oklch(0.90 0.05 185);
  --secondary-foreground: oklch(0.30 0.08 185);

  /* Accent - Purple */
  --accent: oklch(0.85 0.08 304);
  --accent-foreground: oklch(0.30 0.15 304);

  /* Success */
  --success: oklch(0.60 0.18 142);
  --success-foreground: oklch(0.99 0 0);

  /* Warning */
  --warning: oklch(0.75 0.18 84);
  --warning-foreground: oklch(0.20 0.05 84);

  /* Destructive */
  --destructive: oklch(0.58 0.25 27);
  --destructive-foreground: oklch(0.99 0 0);
}
```

---

## Mapeamento A2UI

### CSS Variables Unificadas

```css
:root {
  /* ===== shadcn base ===== */
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.488 0.243 264);
  /* ... */

  /* ===== A2UI Mapping ===== */
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

  /* ===== A2UI Typography ===== */
  --a2ui-font-sans: var(--font-inter), ui-sans-serif, system-ui, sans-serif;
  --a2ui-font-mono: ui-monospace, 'Fira Code', monospace;

  --a2ui-text-xs: 0.75rem;
  --a2ui-text-sm: 0.875rem;
  --a2ui-text-base: 1rem;
  --a2ui-text-lg: 1.125rem;
  --a2ui-text-xl: 1.25rem;
  --a2ui-text-2xl: 1.5rem;
  --a2ui-text-3xl: 1.875rem;
  --a2ui-text-4xl: 2.25rem;
  --a2ui-text-5xl: 3rem;

  /* ===== A2UI Spacing ===== */
  --a2ui-space-0: 0;
  --a2ui-space-1: 0.25rem;
  --a2ui-space-2: 0.5rem;
  --a2ui-space-3: 0.75rem;
  --a2ui-space-4: 1rem;
  --a2ui-space-5: 1.25rem;
  --a2ui-space-6: 1.5rem;
  --a2ui-space-8: 2rem;
  --a2ui-space-10: 2.5rem;
  --a2ui-space-12: 3rem;
  --a2ui-space-16: 4rem;

  /* ===== A2UI Radius ===== */
  --a2ui-radius-none: 0;
  --a2ui-radius-sm: calc(var(--radius) - 4px);
  --a2ui-radius-md: var(--radius);
  --a2ui-radius-lg: calc(var(--radius) + 4px);
  --a2ui-radius-xl: calc(var(--radius) + 8px);
  --a2ui-radius-full: 9999px;
}
```

### usageHint Styles

```css
/* ===== Typography Hints ===== */
[data-usage-hint="h1"] {
  font-size: var(--a2ui-text-4xl);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.025em;
  color: var(--a2ui-color-foreground);
}

[data-usage-hint="h2"] {
  font-size: var(--a2ui-text-3xl);
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: var(--a2ui-color-foreground);
}

[data-usage-hint="h3"] {
  font-size: var(--a2ui-text-2xl);
  font-weight: 600;
  line-height: 1.3;
  color: var(--a2ui-color-foreground);
}

[data-usage-hint="h4"] {
  font-size: var(--a2ui-text-xl);
  font-weight: 600;
  line-height: 1.4;
  color: var(--a2ui-color-foreground);
}

[data-usage-hint="h5"] {
  font-size: var(--a2ui-text-lg);
  font-weight: 600;
  line-height: 1.4;
  color: var(--a2ui-color-foreground);
}

[data-usage-hint="body"] {
  font-size: var(--a2ui-text-base);
  font-weight: 400;
  line-height: 1.6;
  color: var(--a2ui-color-foreground);
}

[data-usage-hint="caption"] {
  font-size: var(--a2ui-text-sm);
  font-weight: 400;
  line-height: 1.5;
  color: var(--a2ui-color-muted-foreground);
}

/* ===== State Hints ===== */
[data-state="disabled"] {
  opacity: 0.5;
  pointer-events: none;
  cursor: not-allowed;
}

[data-state="loading"] {
  cursor: wait;
}

[data-state="error"] {
  border-color: var(--a2ui-color-destructive);
}

[data-state="success"] {
  border-color: var(--success, oklch(0.6 0.18 142));
}
```

---

## Workflow de Design

```typescript
async function createA2UITheme(options: ThemeOptions) {
  // 1. Gerar paleta de cores
  const palette = generateOklchPalette(
    options.primaryHue,
    options.primaryChroma
  );

  // 2. Gerar variaveis CSS
  const cssVars = generateCSSVariables({
    primary: palette[500],
    secondary: options.secondary || generateNeutral(),
    // ...
  });

  // 3. Gerar versao dark
  const darkVars = generateDarkVariables(cssVars);

  // 4. Gerar mapeamento A2UI
  const a2uiMapping = generateA2UIMapping(cssVars);

  // 5. Gerar estilos de usageHint
  const usageHintStyles = generateUsageHintStyles(options.typography);

  // 6. Compilar globals.css
  const globalsCSS = `
@import "tailwindcss";
@import "tw-animate-css";

:root {
${cssVars}
${a2uiMapping}
}

.dark {
${darkVars}
}

${usageHintStyles}
`;

  // 7. Salvar
  await writeFile('app/globals.css', globalsCSS);

  return { palette, cssVars, darkVars };
}
```

## Comandos Relacionados

- `/a2ui-design-theme` - Criar tema completo
- `/a2ui-design-colors` - Apenas cores
- `/a2ui-design-typography` - Apenas tipografia
- `/a2ui-design-dark` - Ajustar dark mode
