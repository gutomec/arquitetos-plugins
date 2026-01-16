---
description: Gera uma ou mais imagens a partir de um prompt de texto
---

# /gerar-imagem

## Objetivo

Gerar imagens de alta qualidade usando os melhores modelos de 2026 (Imagen 4, FLUX, Nano Banana, DALL-E 3).

## Uso

```
/gerar-imagem $ARGUMENTS
```

## Exemplos

```
/gerar-imagem um gato laranja dormindo em uma almofada
/gerar-imagem poster para festival de musica com texto "SUMMER FEST 2026"
/gerar-imagem --modelo flux --tamanho 16:9 paisagem de montanhas ao por do sol
/gerar-imagem --quantidade 4 variações de logo para startup tech
```

## Parametros

| Parametro | Descricao | Valores |
|-----------|-----------|---------|
| --modelo | Modelo a usar | imagen4, flux, ideogram, recraft, nanobananapro, dalle3 |
| --tamanho | Aspect ratio | 1:1, 16:9, 9:16, 4:3, 3:4 |
| --quantidade | Numero de imagens | 1-10 |
| --qualidade | Nivel de qualidade | fast, standard, ultra |
| --saida | Caminho de saida | /path/to/output |

## Instrucoes de Processamento

1. *Parse dos argumentos*:
   - Extrair prompt principal
   - Identificar flags (--modelo, --tamanho, etc)
   - Definir valores padrao para parametros nao informados

2. *Selecao de modelo* (se nao especificado):
   - Texto na imagem? -> Ideogram V3 ou FLUX Kontext
   - Fotorrealismo? -> Imagen 4
   - Ilustracao? -> Recraft V3
   - Caso geral? -> Imagen 4 (padrao)

3. *Construcao do prompt*:
   - Otimizar prompt para o modelo escolhido
   - Adicionar modificadores de qualidade
   - Preparar negative prompt se apropriado

4. *Geracao*:
   - Chamar a tool MCP apropriada
   - Se quantidade > 1, usar batch-processor

5. *Entrega*:
   - Salvar imagem(ns) no caminho especificado ou diretorio atual
   - Reportar resultado com caminho dos arquivos

## Mapeamento de Tools

| Modelo | Tool MCP |
|--------|----------|
| imagen4 | mcp__fal-video__imagen4 |
| flux | mcp__fal-video__flux_kontext |
| flux_dev | mcp__fal-video__flux_dev |
| ideogram | mcp__fal-video__ideogram_v3 |
| recraft | mcp__fal-video__recraft_v3 |
| nanobananapro | mcp__nano-banana-pro__generate_image |
| dalle3 | mcp__dalle3__generate_image |
| sd35 | mcp__fal-video__stable_diffusion_35 |

## Valores Padrao

- Modelo: imagen4
- Tamanho: 1:1
- Quantidade: 1
- Qualidade: standard
- Saida: diretorio atual

## Exemplo de Execucao Interna

```javascript
// Usuario: /gerar-imagem um gato laranja dormindo

// 1. Parse
const prompt = "um gato laranja dormindo";
const modelo = "imagen4"; // padrao
const tamanho = "1:1"; // padrao

// 2. Otimizar prompt para Imagen 4
const optimizedPrompt = `
  Orange tabby cat sleeping peacefully,
  soft fur texture, cozy indoor setting,
  warm natural lighting, professional photography,
  high resolution, sharp focus
`;

// 3. Gerar
mcp__fal-video__imagen4({
  prompt: optimizedPrompt,
  image_size: "square_hd",
  num_images: 1
});

// 4. Reportar
"Imagem gerada: ./gato_laranja_001.png"
```

## Tratamento de Erros

| Erro | Acao |
|------|------|
| Rate limit | Aguardar e retry |
| Content policy | Sugerir reformulacao do prompt |
| Timeout | Retry com modelo mais rapido |
| Modelo indisponivel | Usar fallback |
