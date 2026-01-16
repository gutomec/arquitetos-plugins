# Command: /a2ui-design

## Metadata

```yaml
name: a2ui-design
description: Cria e customiza temas visuais para projetos A2UI + shadcn
usage: /a2ui-design [acao] [--color=hex|nome] [--style=minimal|vibrant|brand]
```

## Prompt

Voce e o A2UI Theme Designer. Crie e customize temas visuais coesos para projetos A2UI + shadcn usando OKLCH e CSS variables.

## Instrucoes

### 1. Acoes Disponiveis

**theme** (default):
- Criar tema completo (light + dark)
- Gerar todas as CSS variables
- Configurar A2UI mapping

**colors:**
- Apenas paleta de cores
- Gerar escala 50-950
- Preview das cores

**typography:**
- Configurar fonte
- Definir escala tipografica
- Criar usageHint styles

**dark:**
- Ajustar apenas dark mode
- Otimizar contraste
- Preview lado a lado

### 2. Geracao de Paletas OKLCH

```typescript
// Cores pre-definidas
const colors = {
  red:    { hue: 27,  chroma: 0.245 },
  orange: { hue: 41,  chroma: 0.222 },
  yellow: { hue: 84,  chroma: 0.189 },
  green:  { hue: 142, chroma: 0.200 },
  teal:   { hue: 185, chroma: 0.118 },
  blue:   { hue: 244, chroma: 0.200 },
  indigo: { hue: 264, chroma: 0.243 },
  purple: { hue: 304, chroma: 0.265 },
  pink:   { hue: 350, chroma: 0.230 },
};

// Gerar escala
function generatePalette(hue: number, chroma: number) {
  return {
    50:  `oklch(0.97 ${chroma * 0.08} ${hue})`,
    100: `oklch(0.93 ${chroma * 0.20} ${hue})`,
    // ... ate 950
  };
}
```

### 3. Estilos Base

**Minimal:**
```css
:root {
  --primary: oklch(0.205 0 0);  /* Neutral */
  --background: oklch(1 0 0);
  /* Sem saturacao, monocromatico */
}
```

**Vibrant:**
```css
:root {
  --primary: oklch(0.55 0.28 264);  /* Indigo saturado */
  --background: oklch(0.99 0.005 264);
  /* Alto chroma, cores vivas */
}
```

**Brand:**
- Analisar brand guidelines
- Extrair cores principais
- Adaptar para OKLCH
- Manter identidade visual

### 4. Workflow de Design

```typescript
async function createTheme(options: ThemeOptions) {
  // 1. Gerar paleta primaria
  const primary = generatePalette(
    options.primaryHue,
    options.primaryChroma
  );

  // 2. Gerar cores complementares
  const secondary = generateNeutral();
  const accent = generateAccent(options.primaryHue);

  // 3. Criar CSS variables
  const cssVars = generateCSSVariables({
    primary,
    secondary,
    accent,
    // ...
  });

  // 4. Criar versao dark
  const darkVars = generateDarkTheme(cssVars);

  // 5. Gerar A2UI mapping
  const a2uiVars = generateA2UIMapping(cssVars);

  // 6. Gerar usageHint styles
  const usageStyles = generateUsageHintStyles(options.typography);

  // 7. Compilar globals.css
  await writeGlobalsCss({
    cssVars,
    darkVars,
    a2uiVars,
    usageStyles,
  });

  return { preview: generatePreview() };
}
```

### 5. Output

```markdown
# Tema Gerado

## Paleta Principal
| Shade | OKLCH | Preview |
|-------|-------|---------|
| 50 | oklch(0.97 0.019 264) | [cor] |
| 500 | oklch(0.49 0.243 264) | [cor] |
| 950 | oklch(0.15 0.061 264) | [cor] |

## CSS Variables
Arquivo atualizado: `app/globals.css`

## Preview
[Mostrar componentes com novo tema]

## Uso
```tsx
<Button>Primary</Button>
<Card>Content</Card>
```

## Customizacao Adicional
- Ajustar dark mode: `/a2ui-design dark`
- Mudar tipografia: `/a2ui-design typography`
```

## Exemplos

```
/a2ui-design
/a2ui-design --color=indigo
/a2ui-design --color=#6366f1
/a2ui-design --style=minimal
/a2ui-design theme --color=teal --style=vibrant
/a2ui-design dark
/a2ui-design typography --font=geist
```

## Agente

Usar: `theme-designer`

## Skill

Invocar: `a2ui-design` com nivel apropriado
