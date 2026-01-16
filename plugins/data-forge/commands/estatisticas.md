---
name: estatisticas
description: Executa analises estatisticas avancadas como testes de hipotese, correlacoes, regressoes e clustering.
---

# /estatisticas

Analises estatisticas avancadas.

## Uso

```
/estatisticas <tipo> [parametros]
```

## Tipos de Analise

### Comparacao de Grupos
```bash
# t-test: comparar 2 grupos
/estatisticas comparar --variavel valor --grupo regiao

# ANOVA: comparar 3+ grupos
/estatisticas comparar --variavel receita --grupo categoria
```

### Correlacao
```bash
# Correlacao entre duas variaveis
/estatisticas correlacao --x idade --y renda

# Matriz de correlacao completa
/estatisticas correlacao --todas-numericas
```

### Regressao
```bash
# Regressao linear simples
/estatisticas regressao --target vendas --features "preco,marketing"

# Regressao com todas as variaveis
/estatisticas regressao --target receita --auto-features
```

### Teste de Normalidade
```bash
/estatisticas normalidade --variavel valor
```

### Clustering
```bash
# K-means automatico
/estatisticas clustering --features "idade,renda,frequencia"

# Especificar numero de clusters
/estatisticas clustering --features "idade,renda" --clusters 4
```

### Serie Temporal
```bash
/estatisticas tendencia --data data_venda --valor receita
/estatisticas sazonalidade --data mes --valor vendas
```

## Parametros Globais

| Parametro | Descricao |
|-----------|-----------|
| `--confianca` | Nivel de confianca (default: 0.95) |
| `--exportar` | Formato de saida (json, csv, html) |
| `--visualizar` | Gerar grafico (quando possivel) |

## Exemplos Praticos

```bash
# Vendas diferem por regiao?
/estatisticas comparar --variavel valor_venda --grupo regiao

# Preco e quantidade estao relacionados?
/estatisticas correlacao --x preco --y quantidade

# O que influencia a receita?
/estatisticas regressao --target receita --auto-features

# Segmentar clientes
/estatisticas clustering --features "recencia,frequencia,valor" --clusters 4

# Tendencia de vendas
/estatisticas tendencia --data mes --valor total_vendas
```

## Output

```markdown
## Analise: Comparacao de Grupos

### Configuracao
- Variavel: valor_venda
- Grupos: regiao (3 niveis)
- Teste: ANOVA

### Resultados
| Estatistica | Valor |
|-------------|-------|
| F-statistic | 15.42 |
| P-valor | 0.0001 |
| Significativo | Sim |

### Interpretacao
Existe diferenca estatisticamente significativa no valor
de venda entre as regioes (F=15.42, p<0.001).

### Medias por Grupo
| Regiao | Media | Std |
|--------|-------|-----|
| Sul | 250 | 45 |
| Sudeste | 320 | 52 |
| Norte | 180 | 38 |

### Conclusao
A regiao Sudeste apresenta valor medio 28% superior
as demais regioes.
```
