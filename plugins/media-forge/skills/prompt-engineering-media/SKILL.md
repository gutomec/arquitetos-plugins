---
name: prompt-engineering-media
description: Tecnicas avancadas de engenharia de prompts para geracao de imagens e videos. Use quando precisar criar prompts otimizados para cada modelo.
allowed-tools:
  - Read
  - Write
---

# Prompt Engineering para Midia

Guia completo de engenharia de prompts para modelos de geracao de imagem e video.

## Estrutura Universal de Prompt

### Formula Base
```
[SUJEITO] + [ACAO/ESTADO] + [AMBIENTE] + [ILUMINACAO] + [ESTILO] + [TECNICOS]
```

### Exemplo Aplicado
```
A young woman (SUJEITO)
reading a book while sitting on a bench (ACAO)
in a cozy autumn park with falling leaves (AMBIENTE)
golden hour sunlight filtering through trees (ILUMINACAO)
cinematic photography style (ESTILO)
shot on 85mm lens, shallow depth of field (TECNICOS)
```

---

## Prompts por Modelo

### Imagen 4 (Fotorrealismo)

*Estrutura otimizada*:
```
[Sujeito detalhado], [pose/acao], [ambiente com detalhes],
[iluminacao especifica], [estilo fotografico],
[especificacoes de camera]
```

*Palavras-chave de qualidade*:
- "professional photography"
- "high resolution"
- "sharp focus"
- "detailed textures"
- "natural lighting"

*Termos de camera*:
- "shot on Canon EOS R5"
- "85mm portrait lens"
- "f/1.8 aperture"
- "shallow depth of field"
- "bokeh background"

*Exemplo completo*:
```
Professional headshot of a confident businessman in his 40s,
wearing a navy blue suit, slight smile, direct eye contact,
modern minimalist office background with soft blur,
soft natural window light from the left side,
corporate photography style, shot on Sony A7R IV with 85mm lens,
f/2.0 aperture, subtle rim lighting
```

### FLUX Kontext (Texto em Imagem)

*Estrutura otimizada*:
```
[Tipo de design], texto "[TEXTO EXATO]" [posicao],
[estilo tipografico], [cores e fundo], [composicao]
```

*Palavras-chave para texto*:
- "crisp typography"
- "legible text"
- "centered text"
- "bold lettering"
- "clean font rendering"

*Exemplo completo*:
```
Modern promotional poster design, bold text "SUMMER SALE 50% OFF"
centered in upper third, sans-serif white typography with subtle shadow,
vibrant gradient background from orange to pink,
minimalist composition with ample negative space,
professional marketing material aesthetic
```

### Ideogram V3 (Design Grafico)

*Estrutura otimizada*:
```
[Tipo de material], "[TEXTO]", [estilo de design],
[paleta de cores], [elementos graficos], [formato]
```

*Palavras-chave*:
- "clean design"
- "vector style"
- "brand identity"
- "professional layout"
- "balanced composition"

*Exemplo completo*:
```
Tech startup logo design, text "NEXUS" in modern geometric font,
abstract interlocking shapes forming an N pattern,
gradient from electric blue (#0066FF) to purple (#9933FF),
minimalist vector style, centered on white background,
scalable brand identity design
```

### Recraft V3 (Ilustracao)

*Estrutura otimizada*:
```
[Estilo artistico], [sujeito], [cena/composicao],
[paleta de cores], [mood/atmosfera], [detalhes de textura]
```

*Estilos disponiveis*:
- "digital illustration"
- "editorial illustration"
- "children's book style"
- "concept art"
- "flat vector"
- "isometric"

*Exemplo completo*:
```
Whimsical children's book illustration style,
a curious fox exploring a magical forest,
surrounded by glowing mushrooms and floating fireflies,
warm autumn color palette with soft oranges and deep greens,
dreamy enchanted atmosphere,
soft watercolor textures with clean linework
```

### Veo 3 (Video com Audio)

*Estrutura otimizada*:
```
[Cena/ambiente], [sujeito] [acao principal],
[movimento de camera], [iluminacao/mood],
[elementos de audio: dialogo, sons, musica],
[duracao/ritmo do video]
```

*Palavras-chave de audio*:
- "with ambient sounds"
- "background music playing"
- "character says '...'"
- "sound of [acao]"
- "voice narrating"

*Exemplo completo*:
```
Cozy coffee shop interior with warm wood tones,
a young barista carefully preparing a latte art,
smooth tracking shot following the cup,
soft morning light through large windows,
gentle acoustic guitar music in background,
sound of milk steaming and cup clinking,
peaceful relaxed mood, medium paced
```

### Kling 2.1 Master (Movimento Fluido)

*Estrutura otimizada*:
```
[Cena dinamica], [sujeito em movimento],
[tipo de movimento especifico], [camera work],
[iluminacao dramatica], [atmosfera]
```

*Palavras-chave de movimento*:
- "fluid motion"
- "slow motion capture"
- "dynamic action"
- "smooth transition"
- "natural movement"

*Exemplo completo*:
```
Professional dance studio with mirrors,
ballet dancer executing a graceful pirouette,
elegant slow motion spin with flowing dress,
orbiting camera capturing multiple angles,
dramatic spotlight with soft edge lighting,
artistic cinematic atmosphere
```

---

## Negative Prompts

### Para Fotorrealismo
```
blurry, out of focus, low quality, low resolution, grainy,
distorted, deformed, ugly, bad anatomy, bad proportions,
extra limbs, mutated hands, poorly drawn face, watermark,
text, signature, jpeg artifacts, oversaturated
```

### Para Ilustracao
```
photorealistic, 3D render, photograph, blurry, low quality,
amateur, inconsistent style, messy linework, muddy colors,
generic, clipart style, stock image
```

### Para Design/Texto
```
cluttered, busy background, unprofessional, low resolution,
pixelated, misspelled text, illegible, poor typography,
unbalanced composition, too many elements
```

### Para Video
```
static, frozen, jerky motion, glitchy, low framerate,
inconsistent, morphing faces, warping, artifacting,
abrupt cuts, unnatural movement
```

---

## Modificadores de Qualidade

### Resolucao e Detalhe
- "8K resolution"
- "highly detailed"
- "intricate details"
- "sharp focus"
- "crystal clear"

### Iluminacao
- "soft natural light"
- "golden hour"
- "studio lighting"
- "dramatic shadows"
- "rim lighting"
- "backlit"

### Atmosfera
- "cinematic"
- "ethereal"
- "moody"
- "vibrant"
- "serene"
- "epic"

### Composicao
- "rule of thirds"
- "centered composition"
- "symmetrical"
- "dynamic angle"
- "bird's eye view"
- "worm's eye view"

---

## Templates Prontos

### Retrato Profissional
```
Professional portrait of [PESSOA], [idade/caracteristicas],
[roupa/estilo], [expressao], [fundo],
studio lighting with soft fill, shot on 85mm lens,
high-end commercial photography style
```

### Produto E-commerce
```
Product photography of [PRODUTO], [angulo],
on [superficie/fundo], [iluminacao],
clean white background, commercial catalog style,
high resolution with perfect focus
```

### Paisagem Cinematica
```
Cinematic landscape of [LOCAL], [hora do dia],
[condicoes climaticas], [elementos em primeiro plano],
epic wide angle shot, dramatic lighting,
film photography aesthetic
```

### Video Promocional
```
[Cena/local], [acao principal],
[movimento de camera], [iluminacao],
[musica/som ambiente], professional commercial style,
smooth transitions, engaging pace
```
