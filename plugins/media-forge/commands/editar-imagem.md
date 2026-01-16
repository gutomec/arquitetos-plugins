---
description: Edita ou modifica uma imagem existente usando IA
---

# /editar-imagem

## Objetivo

Modificar, melhorar ou transformar imagens existentes usando ferramentas de edicao por IA (Nano Banana Pro, DALL-E 3 Edit).

## Uso

```
/editar-imagem <caminho_da_imagem> $ARGUMENTS
```

## Exemplos

```
/editar-imagem ./foto.jpg remover pessoa no fundo
/editar-imagem ./produto.png trocar fundo para gradiente azul
/editar-imagem ./retrato.jpg fazer a pessoa sorrir
/editar-imagem ./logo.png --referencia estilo.jpg aplicar estilo da referencia
/editar-imagem ./foto_antiga.jpg restaurar e melhorar qualidade
```

## Parametros

| Parametro | Descricao | Valores |
|-----------|-----------|---------|
| <caminho> | Caminho da imagem (obrigatorio) | /path/to/image |
| --referencia | Imagem de referencia para estilo | /path/to/ref |
| --fundo | Tipo de fundo | transparent, solid, auto |
| --saida | Caminho de saida | /path/to/output |
| --modelo | Ferramenta de edicao | nanobananapro, dalle3 |

## Instrucoes de Processamento

1. *Validar entrada*:
   - Verificar se imagem existe
   - Ler imagem como base64 ou obter path
   - Verificar referencia se fornecida

2. *Analisar intencao*:
   - Remocao de elementos? -> edit_image
   - Adicao de elementos? -> edit_image
   - Mudanca de estilo? -> edit_image + referencia
   - Melhoria de qualidade? -> edit_image
   - Troca de fundo? -> edit_image com background param

3. *Selecao de ferramenta*:
   - Edicao simples -> Nano Banana Pro
   - Com referencia -> Nano Banana Pro (suporta multiplas imagens)
   - Fundo transparente -> DALL-E 3 Edit
   - Edicao iterativa -> Nano Banana (continue_editing)

4. *Construcao do prompt*:
   - Descrever mudanca desejada claramente
   - Ser especifico sobre O QUE mudar
   - Mencionar o que MANTER

5. *Execucao*:
   - Chamar tool apropriada
   - Para iteracoes, usar continue_editing

6. *Entrega*:
   - Salvar resultado
   - Oferecer refinamentos adicionais

## Mapeamento de Tools

| Caso de Uso | Tool MCP |
|-------------|----------|
| Edicao geral | mcp__nano-banana-pro__edit_image |
| Edicao iterativa | mcp__nano-banana__continue_editing |
| Fundo transparente | mcp__dalle3__edit_image |
| Descrever imagem | mcp__nano-banana-pro__describe_image |

## Tipos de Edicao

### Remocao de Elementos
```
/editar-imagem ./foto.jpg remover a pessoa de vermelho no canto esquerdo
/editar-imagem ./produto.png remover marca dagua
/editar-imagem ./paisagem.jpg remover os carros estacionados
```

### Adicao de Elementos
```
/editar-imagem ./sala.jpg adicionar uma planta no canto direito
/editar-imagem ./retrato.png adicionar oculos de sol
/editar-imagem ./ceu.jpg adicionar passaros voando
```

### Modificacao de Elementos
```
/editar-imagem ./carro.jpg mudar cor do carro para vermelho
/editar-imagem ./pessoa.png fazer a pessoa parecer mais velha
/editar-imagem ./dia.jpg transformar cena de dia em noite
```

### Troca de Fundo
```
/editar-imagem ./produto.png --fundo transparent remover fundo
/editar-imagem ./retrato.jpg trocar fundo para escritorio moderno
/editar-imagem ./modelo.png substituir fundo por praia tropical
```

### Melhoria de Qualidade
```
/editar-imagem ./foto_antiga.jpg restaurar e melhorar qualidade
/editar-imagem ./baixa_res.png aumentar resolucao e nitidez
/editar-imagem ./escura.jpg corrigir iluminacao
```

### Transferencia de Estilo
```
/editar-imagem ./foto.jpg --referencia estilo_vangogh.jpg aplicar estilo artistico
/editar-imagem ./retrato.png --referencia anime.jpg converter para estilo anime
```

## Exemplo de Execucao

### Remocao Simples
```javascript
// Usuario: /editar-imagem ./foto.jpg remover pessoa no fundo

mcp__nano-banana-pro__edit_image({
  images: [{ data: base64Image, mimeType: "image/jpeg" }],
  prompt: "Remove the person standing in the background, keep everything else exactly the same, fill the area naturally with the surrounding environment",
  outputPath: "./foto_editada.jpg"
});
```

### Com Referencia de Estilo
```javascript
// Usuario: /editar-imagem ./foto.jpg --referencia estilo.jpg aplicar estilo

mcp__nano-banana-pro__edit_image({
  images: [
    { data: base64MainImage, mimeType: "image/jpeg" },
    { data: base64StyleRef, mimeType: "image/jpeg" }
  ],
  prompt: "Apply the artistic style from the second image to the first image, maintaining the composition and subject of the first image",
  outputPath: "./foto_estilizada.jpg"
});
```

### Fundo Transparente
```javascript
// Usuario: /editar-imagem ./produto.png remover fundo

mcp__dalle3__edit_image({
  inputImages: ["./produto.png"],
  prompt: "Remove the background completely, keep only the product with clean edges",
  background: "transparent",
  outputPath: "./produto_nobg.png"
});
```

## Edicao Iterativa

Para fazer multiplas edicoes na mesma imagem:

```
# Primeira edicao
/editar-imagem ./foto.jpg mudar cor do carro para azul

# Continuar editando a ultima imagem
/editar-imagem --continuar adicionar reflexo no carro

# Continuar novamente
/editar-imagem --continuar melhorar iluminacao geral
```

Internamente usa `mcp__nano-banana__continue_editing`.

## Dicas para Melhores Resultados

1. *Seja especifico*:
   - "remover a pessoa de camisa vermelha no canto esquerdo"
   - NAO: "remover pessoa"

2. *Mencione o que manter*:
   - "mudar cor do carro, manter todo o resto igual"

3. *Para remocoes*:
   - Descreva como preencher a area: "preencher com o ambiente ao redor"

4. *Para adicoes*:
   - Especifique posicao: "no canto inferior direito"
   - Especifique tamanho: "pequena planta"

5. *Para estilo*:
   - Forneca referencia quando possivel
   - Seja especifico sobre o estilo desejado
