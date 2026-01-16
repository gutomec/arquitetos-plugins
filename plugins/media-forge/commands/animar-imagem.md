---
description: Transforma uma imagem estatica em video animado
---

# /animar-imagem

## Objetivo

Transformar uma imagem existente em video animado usando modelos de Image-to-Video (Kling I2V, Luma Ray 2, LTX Video).

## Uso

```
/animar-imagem <caminho_da_imagem> $ARGUMENTS
```

## Exemplos

```
/animar-imagem ./foto.png pessoa sorrindo e acenando
/animar-imagem /path/to/retrato.jpg --modelo kling vento suave no cabelo
/animar-imagem ./paisagem.png --duracao 10 nuvens se movendo lentamente
/animar-imagem ./produto.jpg camera fazendo orbita ao redor do produto
```

## Parametros

| Parametro | Descricao | Valores |
|-----------|-----------|---------|
| <caminho> | Caminho da imagem (obrigatorio) | /path/to/image |
| --modelo | Modelo I2V a usar | kling, luma, ltx, pixverse, wan, vidu, hunyuan |
| --duracao | Duracao em segundos | 5, 10 |
| --formato | Aspect ratio do video | 16:9, 9:16, 1:1 |
| --saida | Caminho de saida | /path/to/output |

## Instrucoes de Processamento

1. *Validar imagem*:
   - Verificar se arquivo existe
   - Verificar formato suportado (PNG, JPG, WEBP)
   - Obter URL ou base64 da imagem

2. *Parse dos argumentos*:
   - Extrair caminho da imagem
   - Extrair descricao do movimento desejado
   - Identificar flags de configuracao

3. *Selecao de modelo* (se nao especificado):
   - Retrato/pessoa? -> Kling I2V (melhor para rostos)
   - Paisagem/cena? -> Luma Ray 2 I2V
   - Precisa ser rapido? -> LTX Video
   - Animacao complexa? -> Wan Pro I2V

4. *Construcao do prompt*:
   - Descrever movimento desejado
   - Especificar elementos a animar
   - Definir intensidade do movimento

5. *Geracao*:
   - Fazer upload da imagem se necessario
   - Chamar tool MCP apropriada

6. *Entrega*:
   - Salvar video
   - Reportar resultado

## Mapeamento de Tools

| Modelo | Tool MCP | Qualidade | Velocidade |
|--------|----------|-----------|------------|
| kling | mcp__fal-video__kling_master_image | ***** | *** |
| luma | mcp__fal-video__luma_ray2_image | ***** | *** |
| ltx | mcp__fal-video__ltx_video | *** | ***** |
| pixverse | mcp__fal-video__pixverse_image | **** | **** |
| wan | mcp__fal-video__wan_pro_image | **** | *** |
| vidu | mcp__fal-video__vidu_image | **** | **** |
| hunyuan | mcp__fal-video__hunyuan_image | *** | **** |

## Valores Padrao

- Modelo: kling (para retratos) ou luma (para cenas)
- Duracao: 5 segundos
- Formato: detectado da imagem ou 16:9
- Saida: mesmo diretorio da imagem original

## Template de Prompt para Animacao

### Retratos/Pessoas
```
Subtle natural movements:
- gentle eye blink
- soft smile forming
- slight head turn
- hair moving with breeze
- natural breathing motion
```

### Paisagens/Natureza
```
Environmental motion:
- clouds drifting slowly
- water rippling
- leaves rustling
- light changing gradually
- birds flying in distance
```

### Produtos
```
Showcase motion:
- camera orbiting around product
- gentle rotation
- light reflection changing
- zoom in to details
```

## Exemplo de Execucao

```javascript
// Usuario: /animar-imagem ./retrato.jpg pessoa sorrindo suavemente

// 1. Validar imagem
const imagePath = "./retrato.jpg";
// verificar existencia...

// 2. Preparar imagem (upload ou URL)
const imageUrl = await uploadToStorage(imagePath);

// 3. Construir prompt
const prompt = `
  Subtle natural portrait animation:
  gentle smile forming on face,
  soft eye movement with natural blink,
  very slight head turn to the side,
  hair moving gently as if light breeze,
  warm natural lighting maintained
`;

// 4. Gerar com Kling I2V
mcp__fal-video__kling_master_image({
  image_url: imageUrl,
  prompt: prompt,
  duration: "5",
  aspect_ratio: "16:9"
});

// 5. Reportar
"Video gerado: ./retrato_animated.mp4"
```

## Dicas para Melhores Resultados

1. *Movimentos sutis funcionam melhor*:
   - "gentle smile" > "big laugh"
   - "slight head turn" > "spinning around"

2. *Seja especifico sobre O QUE animar*:
   - "eyes blinking, mouth forming smile"
   - "clouds moving, water rippling"

3. *Mantenha consistencia*:
   - O modelo tenta manter o visual da imagem original
   - Mudancas drasticas podem parecer estranhas

4. *Para retratos*: Kling I2V e o melhor

5. *Para paisagens*: Luma Ray 2 cria atmosferas lindas

## Casos de Uso Comuns

### Foto de Perfil Animada
```
/animar-imagem ./profile.jpg --modelo kling --duracao 5
olhos piscando naturalmente, leve sorriso, movimento sutil de cabeca
```

### Paisagem Viva
```
/animar-imagem ./sunset.jpg --modelo luma --duracao 10
nuvens se movendo lentamente, reflexo da luz na agua mudando gradualmente
```

### Produto 360
```
/animar-imagem ./produto.png --modelo wan
camera fazendo orbita suave ao redor do produto, iluminacao variando
```
