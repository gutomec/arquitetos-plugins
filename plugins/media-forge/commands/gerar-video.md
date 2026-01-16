---
description: Gera um video a partir de um prompt de texto usando Veo 3, Kling ou outros modelos
---

# /gerar-video

## Objetivo

Gerar videos de alta qualidade usando os melhores modelos de 2026 (Veo 3 com audio, Kling 2.1 Master, Luma Ray 2).

## Uso

```
/gerar-video $ARGUMENTS
```

## Exemplos

```
/gerar-video uma cidade futurista a noite com carros voadores
/gerar-video --audio cena de cafe com conversa entre duas pessoas
/gerar-video --modelo kling --duracao 10 bailarina executando pirueta
/gerar-video --vertical pessoa dancando para um reel de instagram
```

## Parametros

| Parametro | Descricao | Valores |
|-----------|-----------|---------|
| --modelo | Modelo a usar | veo3, kling, luma, pixverse, magi |
| --duracao | Duracao em segundos | 5, 10, 15, 30 |
| --formato | Aspect ratio | 16:9, 9:16, 1:1 |
| --audio | Incluir audio nativo (Veo 3) | flag boolean |
| --vertical | Formato vertical | flag boolean |
| --saida | Caminho de saida | /path/to/output |

## Instrucoes de Processamento

1. *Parse dos argumentos*:
   - Extrair prompt principal
   - Identificar flags de configuracao
   - Definir valores padrao

2. *Selecao de modelo* (se nao especificado):
   - Precisa de audio/dialogo? -> Veo 3
   - Movimento complexo? -> Kling 2.1 Master
   - Video vertical? -> Pixverse V4.5 ou Veo 3
   - Video artistico? -> Luma Ray 2
   - Prototipo rapido? -> Magi

3. *Construcao do prompt*:
   - Descrever cena completamente
   - Incluir movimento de camera
   - Se Veo 3: adicionar elementos de audio
   - Especificar atmosfera e iluminacao

4. *Geracao*:
   - Chamar tool MCP do modelo escolhido
   - Aguardar processamento (videos demoram mais)

5. *Entrega*:
   - Salvar video no caminho especificado
   - Reportar resultado

## Mapeamento de Tools

| Modelo | Tool MCP | Audio |
|--------|----------|-------|
| veo3 | mcp__fal-video__veo3 | Sim |
| kling | mcp__fal-video__kling_master_text | Nao |
| luma | mcp__fal-video__luma_ray2 | Nao |
| pixverse | mcp__fal-video__pixverse_text | Nao |
| magi | mcp__fal-video__magi | Nao |
| wan | mcp__fal-video__wan_pro_text | Nao |
| vidu | mcp__fal-video__vidu_text | Nao |

## Valores Padrao

- Modelo: veo3 (se audio mencionado) ou kling
- Duracao: 5 segundos
- Formato: 16:9
- Saida: diretorio atual

## Template de Prompt para Video

```
[CENA/AMBIENTE detalhado],
[SUJEITO] [executando ACAO],
[MOVIMENTO DE CAMERA: tracking/pan/static/etc],
[ILUMINACAO e ATMOSFERA],
[SE VEO3: sons ambiente, musica, dialogos],
[RITMO: lento/medio/dinamico]
```

## Exemplo de Execucao - Veo 3 com Audio

```javascript
// Usuario: /gerar-video --audio cena de cafe com conversa

const prompt = `
  Cozy coffee shop interior with warm lighting,
  two friends sitting at a wooden table having coffee,
  gentle camera pan across the scene,
  soft afternoon sunlight through window,
  ambient coffee shop sounds, soft jazz music playing,
  one person laughs and says "That's so funny",
  relaxed friendly atmosphere
`;

mcp__fal-video__veo3({
  prompt: prompt,
  aspect_ratio: "16:9",
  duration: 10
});
```

## Exemplo de Execucao - Kling para Acao

```javascript
// Usuario: /gerar-video bailarina executando pirueta

const prompt = `
  Professional ballet studio with mirrors,
  elegant ballerina in white tutu,
  executing a perfect pirouette with extended arms,
  slow motion capture of the spin,
  orbiting camera following the movement,
  dramatic spotlight with soft rim lighting,
  graceful artistic atmosphere
`;

mcp__fal-video__kling_master_text({
  prompt: prompt,
  aspect_ratio: "16:9",
  duration: 5
});
```

## Dicas para Melhores Resultados

1. *Seja especifico com movimento*: nao apenas "pessoa andando", mas "pessoa caminhando lentamente da esquerda para direita"

2. *Descreva a camera*: "tracking shot following subject" ou "static wide shot"

3. *Para Veo 3 com audio*: inclua descricao de sons
   - "with birds chirping"
   - "soft piano music playing"
   - "character says '...'"

4. *Duracao apropriada*:
   - Acao simples: 5s
   - Cena com desenvolvimento: 10s
   - Narrativa: 15-30s
