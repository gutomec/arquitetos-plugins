---
name: perguntar-dados
description: Faz perguntas em linguagem natural sobre os dados carregados e recebe respostas com analises automaticas.
---

# /perguntar-dados

Pergunte qualquer coisa sobre seus dados em linguagem natural.

## Uso

```
/perguntar-dados <pergunta>
```

## Exemplos de Perguntas

### Estatisticas Basicas
```bash
/perguntar-dados "Qual o valor medio das vendas?"
/perguntar-dados "Quantos clientes unicos temos?"
/perguntar-dados "Qual o produto mais vendido?"
```

### Comparacoes
```bash
/perguntar-dados "Qual regiao vende mais?"
/perguntar-dados "Homens ou mulheres compram mais?"
/perguntar-dados "Vendas de 2024 foram maiores que 2023?"
```

### Tendencias
```bash
/perguntar-dados "As vendas estao crescendo?"
/perguntar-dados "Qual o mes com maior faturamento?"
/perguntar-dados "Existe sazonalidade nas vendas?"
```

### Correlacoes
```bash
/perguntar-dados "Preco afeta a quantidade vendida?"
/perguntar-dados "Idade e renda estao relacionados?"
/perguntar-dados "O que influencia o ticket medio?"
```

### Anomalias
```bash
/perguntar-dados "Existem outliers nos valores?"
/perguntar-dados "Quais clientes tem comportamento atipico?"
/perguntar-dados "Tem dados faltando?"
```

### Segmentacao
```bash
/perguntar-dados "Como posso segmentar os clientes?"
/perguntar-dados "Quais sao os perfis de compradores?"
/perguntar-dados "Agrupe os produtos por similaridade"
```

## Como Funciona

1. A pergunta e interpretada pelo Data Storyteller
2. Identificamos as colunas e analises relevantes
3. Executamos a analise apropriada
4. Traduzimos o resultado em linguagem natural

## Tipos de Resposta

### Resposta Numerica
```
Pergunta: "Qual o valor medio das vendas?"
Resposta: O valor medio das vendas e R$ 245,50 (std: R$ 89,32).
          50% das vendas ficam entre R$ 180 e R$ 300.
```

### Resposta Comparativa
```
Pergunta: "Qual regiao vende mais?"
Resposta: A regiao Sudeste lidera com R$ 5.2M (52% do total),
          seguida por Sul com R$ 2.8M (28%) e Norte com R$ 2.0M (20%).
          A diferenca entre Sudeste e as demais e estatisticamente
          significativa (p < 0.001).
```

### Resposta Temporal
```
Pergunta: "As vendas estao crescendo?"
Resposta: Sim, as vendas apresentam tendencia de crescimento de
          8.5% ao mes nos ultimos 12 meses (R²=0.87).
          Projecao para proximo mes: R$ 1.2M.
```

### Resposta de Insight
```
Pergunta: "O que influencia o ticket medio?"
Resposta: Analisando os dados, os principais fatores sao:
          1. Categoria do produto (35% de influencia)
          2. Regiao do cliente (25%)
          3. Dia da semana (15%)
          4. Canal de venda (12%)
          Modelo de regressao: R² = 0.72
```

## Dicas

- Seja especifico: "valor de vendas" ao inves de "vendas"
- Use nomes de colunas quando souber
- Pergunte uma coisa por vez para respostas mais precisas
- Pergunte "por que" para obter analises mais profundas
