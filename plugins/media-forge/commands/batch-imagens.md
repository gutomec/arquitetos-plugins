---
description: Gera multiplas imagens em paralelo a partir de uma lista de prompts
---

# /batch-imagens

## Objetivo

Gerar multiplas imagens de forma eficiente e paralela, respeitando rate limits e oferecendo progresso em tempo real.

## Uso

```
/batch-imagens $ARGUMENTS
```

## Formatos de Entrada

### 1. Lista inline (separada por |)
```
/batch-imagens gato dormindo | cachorro correndo | passaro voando
```

### 2. Arquivo de prompts
```
/batch-imagens --arquivo prompts.txt
```

### 3. Variacoes de tema
```
/batch-imagens --tema "um gato" --variacoes "dormindo, brincando, comendo, olhando pela janela"
```

### 4. Grid de combinacoes
```
/batch-imagens --sujeitos "gato, cachorro" --estilos "realista, cartoon, aquarela"
```

## Parametros

| Parametro | Descricao | Valores |
|-----------|-----------|---------|
| --arquivo | Arquivo com prompts (1 por linha) | /path/to/file.txt |
| --tema | Tema base para variacoes | "texto do tema" |
| --variacoes | Lista de variacoes | "var1, var2, var3" |
| --sujeitos | Lista de sujeitos para grid | "s1, s2, s3" |
| --estilos | Lista de estilos para grid | "e1, e2, e3" |
| --modelo | Modelo a usar | imagen4, flux, etc |
| --tamanho | Aspect ratio | 1:1, 16:9, 9:16 |
| --paralelo | Max requisicoes paralelas | 1-10 |
| --saida | Diretorio de saida | /path/to/dir |

## Instrucoes de Processamento

1. *Parse da entrada*:
   - Identificar formato de entrada (inline, arquivo, tema, grid)
   - Extrair lista de prompts
   - Contar total de imagens

2. *Validacao*:
   - Verificar numero de itens (avisar se > 20)
   - Estimar tempo e custo
   - Confirmar com usuario se necessario

3. *Planejamento*:
   - Determinar modelo e configuracoes
   - Calcular batches respeitando rate limits
   - Criar lista de tarefas

4. *Execucao paralela*:
   - Usar TodoWrite para rastrear progresso
   - Disparar requisicoes em paralelo (respeitando limite)
   - Tratar erros com retry/fallback
   - Reportar progresso em tempo real

5. *Finalizacao*:
   - Coletar todos os resultados
   - Gerar relatorio final
   - Listar arquivos criados

## Limites de Paralelismo

| Modelo | Max Paralelo | Rate Limit |
|--------|--------------|------------|
| imagen4 | 5 | 60/min |
| flux | 10 | 120/min |
| ideogram | 5 | 60/min |
| recraft | 8 | 100/min |
| dalle3 | 3 | 15/min |
| nanobananapro | 8 | ~80/min |

## Exemplos de Uso

### Exemplo 1: Lista Simples
```
/batch-imagens gato laranja | cachorro golden | coelho branco
```
*Resultado*: 3 imagens geradas em paralelo

### Exemplo 2: Arquivo de Prompts
```
# prompts.txt
Logo para empresa de tecnologia
Ilustracao de mascote fofo
Banner para e-commerce
```
```
/batch-imagens --arquivo prompts.txt --modelo ideogram
```

### Exemplo 3: Variacoes de Tema
```
/batch-imagens --tema "smartphone moderno" --variacoes "frente, costas, lateral, em uso" --modelo imagen4
```
*Resultado*: 4 imagens do mesmo produto em angulos diferentes

### Exemplo 4: Grid de Combinacoes
```
/batch-imagens --sujeitos "gato, cachorro, coelho" --estilos "fotorrealista, cartoon, pixel art" --modelo flux
```
*Resultado*: 9 imagens (3 sujeitos x 3 estilos)

## Formato de Progresso

```
[BATCH] Iniciando geracao de 10 imagens com Imagen 4
[BATCH] Paralelismo: 5 | Rate limit: 60/min

[1/10] ⏳ Gerando: "Gato dormindo"
[2/10] ⏳ Gerando: "Cachorro correndo"
[3/10] ⏳ Gerando: "Passaro voando"
[4/10] ⏳ Gerando: "Peixe nadando"
[5/10] ⏳ Gerando: "Coelho pulando"

[1/10] ✓ Completo: output_001_gato.png (2.3s)
[2/10] ✓ Completo: output_002_cachorro.png (2.1s)
[3/10] ✗ Erro: Rate limit - retry em 5s
[3/10] ✓ Completo (retry): output_003_passaro.png (8.2s)
...

[BATCH] Completo!
- Total: 10
- Sucesso: 9 (90%)
- Falha: 1 (10%)
- Tempo: 45s
```

## Formato de Relatorio Final

```markdown
## Resultado do Batch

**Configuracao**
- Modelo: imagen4
- Tamanho: 1:1
- Total: 10 imagens

**Resumo**
- Sucesso: 9 (90%)
- Falha: 1
- Tempo total: 45 segundos
- Tempo medio: 4.5s/imagem
- Custo estimado: ~$0.40

**Arquivos Gerados**
1. ✓ output_001_gato.png
2. ✓ output_002_cachorro.png
3. ✓ output_003_passaro.png
...

**Falhas**
- Item 7: "cena complexa demais"
  Erro: Content policy
  Sugestao: Simplificar prompt
```

## Tratamento de Erros

| Erro | Acao |
|------|------|
| Rate limit | Aguardar e retry automatico |
| Content policy | Pular item, reportar no final |
| Timeout | Retry ate 3x, depois fallback |
| Modelo indisponivel | Usar modelo fallback |

## Fallbacks

| Modelo Principal | Fallback 1 | Fallback 2 |
|------------------|------------|------------|
| imagen4 | flux_dev | sd35 |
| flux | ideogram | recraft |
| ideogram | flux | recraft |
