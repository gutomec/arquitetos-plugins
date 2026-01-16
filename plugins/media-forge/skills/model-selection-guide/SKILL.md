---
name: model-selection-guide
description: Guia completo para selecao do modelo ideal de geracao de imagem ou video. Use quando precisar decidir qual modelo usar para cada caso.
allowed-tools:
  - Read
---

# Guia de Selecao de Modelos

Referencia completa para escolher o modelo certo para cada tarefa de geracao de midia.

---

## Modelos de Imagem

### Imagen 4 (Google)
*O rei do fotorrealismo*

| Aspecto | Avaliacao |
|---------|-----------|
| Fotorrealismo | ***** |
| Texto em imagem | *** |
| Velocidade | **** |
| Custo | $0.04/img |
| Resolucao max | 4K |

*Use quando*:
- Precisa de fotos realistas de pessoas
- Quer qualidade fotografica profissional
- Necessita de iluminacao natural convincente
- Trabalha com retratos ou produtos

*Evite quando*:
- Precisa de texto preciso na imagem
- Quer estilos muito artisticos/abstratos
- Tem orcamento muito limitado

### FLUX Kontext Pro
*Mestre da tipografia*

| Aspecto | Avaliacao |
|---------|-----------|
| Fotorrealismo | **** |
| Texto em imagem | ***** |
| Velocidade | **** |
| Resolucao max | 2K |

*Use quando*:
- Precisa de texto renderizado perfeitamente
- Cria banners, posters, marketing
- Quer aderencia precisa ao prompt
- Trabalha com design grafico

*Evite quando*:
- Precisa de resolucao 4K
- Quer estilo muito artistico

### Ideogram V3
*Especialista em design*

| Aspecto | Avaliacao |
|---------|-----------|
| Fotorrealismo | *** |
| Texto em imagem | ***** |
| Design grafico | ***** |
| Velocidade | **** |

*Use quando*:
- Cria logos e branding
- Precisa de texto 100% legivel
- Trabalha com design profissional
- Faz materiais de marketing

*Evite quando*:
- Precisa de fotorrealismo extremo
- Quer estilos artisticos organicos

### Recraft V3
*Artista digital*

| Aspecto | Avaliacao |
|---------|-----------|
| Ilustracao | ***** |
| Estilos artisticos | ***** |
| Consistencia | **** |
| Versatilidade | **** |

*Use quando*:
- Cria ilustracoes editoriais
- Quer estilos artisticos especificos
- Trabalha com arte conceitual
- Precisa de ilustracoes para livros

*Evite quando*:
- Precisa de fotorrealismo
- Quer texto preciso

### Nano Banana Pro (Gemini)
*Canivete suico*

| Aspecto | Avaliacao |
|---------|-----------|
| Versatilidade | ***** |
| Resolucao | ***** (ate 4K) |
| Edicao iterativa | ***** |
| Custo | Moderado |

*Use quando*:
- Quer iterar rapidamente
- Precisa de alta resolucao
- Trabalha com edicao continua
- Quer flexibilidade de estilos

*Evite quando*:
- Precisa de texto perfeito
- Tem caso muito especifico

### DALL-E 3 (OpenAI)
*Criativo e interpretativo*

| Aspecto | Avaliacao |
|---------|-----------|
| Criatividade | ***** |
| Interpretacao | ***** |
| Conceitos abstratos | ***** |
| Rate limits | ** (restrito) |

*Use quando*:
- Quer interpretacao criativa do prompt
- Trabalha com conceitos abstratos
- Precisa de consistencia de personagens
- Quer ideias inesperadas

*Evite quando*:
- Precisa de muitas imagens rapido
- Quer controle preciso do output

### Stable Diffusion 3.5
*Workhouse acessivel*

| Aspecto | Avaliacao |
|---------|-----------|
| Qualidade | **** |
| Velocidade | ***** |
| Custo | $ (mais barato) |
| Customizacao | **** |

*Use quando*:
- Tem orcamento limitado
- Precisa de muitas imagens
- Quer prototipagem rapida
- Trabalha com volume alto

*Evite quando*:
- Precisa de maxima qualidade
- Quer texto em imagem

---

## Modelos de Video (Text-to-Video)

### Veo 3 (Google DeepMind)
*O mais avancado com audio*

| Aspecto | Avaliacao |
|---------|-----------|
| Qualidade visual | ***** |
| Audio nativo | ***** |
| Duracao | ate 30s |
| Resolucao | ate 4K |
| Custo | $$$ |

*Use quando*:
- Precisa de video com dialogo
- Quer efeitos sonoros sincronizados
- Trabalha com conteudo narrativo
- Faz videos para social media com audio

*Evite quando*:
- Nao precisa de audio
- Tem orcamento limitado
- Quer apenas movimento simples

### Kling 2.1 Master
*Fluidez de movimento*

| Aspecto | Avaliacao |
|---------|-----------|
| Movimento | ***** |
| Consistencia | ***** |
| Pessoas | ***** |
| Fisica | **** |

*Use quando*:
- Precisa de movimentos complexos
- Trabalha com pessoas em acao
- Quer fisica realista
- Faz videos cinematicos

*Evite quando*:
- Precisa de audio nativo
- Quer apenas animacao simples

### Luma Ray 2
*Qualidade cinematica*

| Aspecto | Avaliacao |
|---------|-----------|
| Estetica | ***** |
| Transicoes | ***** |
| Atmosfera | ***** |
| Velocidade | *** |

*Use quando*:
- Quer visual artistico
- Trabalha com atmosferas oniricas
- Precisa de transicoes elegantes
- Faz videos artisticos

*Evite quando*:
- Precisa de velocidade
- Quer acoes muito dinamicas

### Pixverse V4.5
*Especialista vertical*

| Aspecto | Avaliacao |
|---------|-----------|
| Videos 9:16 | ***** |
| Social media | ***** |
| Velocidade | **** |
| Custo | $$ |

*Use quando*:
- Cria Reels/TikTok/Shorts
- Trabalha com formato vertical
- Precisa de producao rapida
- Faz conteudo social media

*Evite quando*:
- Precisa de formato horizontal
- Quer maxima qualidade

### Magi
*Rapido e criativo*

| Aspecto | Avaliacao |
|---------|-----------|
| Velocidade | ***** |
| Criatividade | **** |
| Custo | $ |
| Duracao | 5-15s |

*Use quando*:
- Precisa de prototipo rapido
- Tem orcamento limitado
- Quer experimentar ideias
- Trabalha com volume

*Evite quando*:
- Precisa de maxima qualidade
- Quer videos longos

---

## Modelos Image-to-Video

### Kling 2.1 Master I2V
*Premium para animacao*

| Aspecto | Avaliacao |
|---------|-----------|
| Qualidade | ***** |
| Movimento | ***** |
| Consistencia | ***** |
| Custo | $$$ |

*Use quando*:
- Quer animacao de alta qualidade
- Trabalha com retratos
- Precisa de movimentos complexos
- Faz conteudo profissional

### Luma Ray 2 I2V
*Elegancia e fluidez*

| Aspecto | Avaliacao |
|---------|-----------|
| Transicoes | ***** |
| Estetica | ***** |
| Suavidade | ***** |

*Use quando*:
- Quer movimento sutil e elegante
- Trabalha com arte/fotografia
- Precisa de animacao suave

### LTX Video
*Velocidade maxima*

| Aspecto | Avaliacao |
|---------|-----------|
| Velocidade | ***** |
| Qualidade | *** |
| Custo | $ |

*Use quando*:
- Precisa de resultado rapido
- Trabalha com volume alto
- Faz prototipagem

---

## Matriz de Decisao Rapida

### Por Caso de Uso - Imagem

| Caso | Modelo 1 | Modelo 2 |
|------|----------|----------|
| Foto de pessoa | Imagen 4 | Nano Banana Pro |
| Produto e-commerce | Imagen 4 | FLUX Dev |
| Poster com texto | Ideogram V3 | FLUX Kontext |
| Logo/branding | Ideogram V3 | Recraft V3 |
| Ilustracao | Recraft V3 | DALL-E 3 |
| Arte conceitual | DALL-E 3 | Recraft V3 |
| Prototipo rapido | SD 3.5 | Magi |

### Por Caso de Uso - Video

| Caso | Modelo 1 | Modelo 2 |
|------|----------|----------|
| Video com dialogo | Veo 3 | - |
| Video com musica | Veo 3 | - |
| Acao dinamica | Kling Master | Luma Ray 2 |
| Reel/TikTok | Pixverse | Veo 3 (vertical) |
| Video artistico | Luma Ray 2 | Kling Master |
| Animacao de foto | Kling I2V | Luma Ray 2 I2V |
| Prototipo rapido | Magi | LTX Video |

---

## Custos Estimados

### Imagem (por unidade)
| Modelo | Custo |
|--------|-------|
| Imagen 4 Fast | $0.02 |
| Imagen 4 | $0.04 |
| Imagen 4 Ultra | $0.06 |
| FLUX | ~$0.03 |
| SD 3.5 | ~$0.01 |
| DALL-E 3 | ~$0.04 |

### Video (por unidade)
| Modelo | Custo (5s) |
|--------|------------|
| Veo 3 | ~$0.10 |
| Kling Master | ~$0.08 |
| Luma Ray 2 | ~$0.06 |
| Pixverse | ~$0.04 |
| Magi | ~$0.02 |
