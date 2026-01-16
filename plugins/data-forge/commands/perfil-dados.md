---
name: perfil-dados
description: Gera perfil detalhado de um dataset ja carregado com estatisticas completas.
---

# /perfil-dados

Gera relatorio de profiling detalhado para dataset.

## Uso

```
/perfil-dados
/perfil-dados <tabela_ou_arquivo>
/perfil-dados --completo
/perfil-dados --exportar <formato>
```

## Parametros

| Parametro | Descricao | Default |
|-----------|-----------|---------|
| `<fonte>` | Tabela ou arquivo especifico | dataset atual |
| `--completo` | Analise completa (mais lento) | amostra |
| `--colunas` | Colunas especificas | todas |
| `--exportar` | html, json, markdown | terminal |

## Exemplos

```bash
# Perfil do dataset atual
/perfil-dados

# Tabela especifica
/perfil-dados clientes

# Perfil completo exportado
/perfil-dados vendas --completo --exportar html

# Apenas algumas colunas
/perfil-dados --colunas "nome,idade,valor"
```

## Metricas Geradas

### Por Dataset
- Total de linhas e colunas
- Uso de memoria
- Score de qualidade (0-100)
- Linhas duplicadas
- Linhas completas

### Por Coluna Numerica
- Count, Mean, Std, Min, Max
- Quartis (25%, 50%, 75%)
- Skewness, Kurtosis
- Zeros, Negativos
- Outliers (IQR method)

### Por Coluna Categorica
- Valores unicos
- Moda (mais frequente)
- Distribuicao de frequencias
- Lista de todos os valores (se < 50)

### Por Coluna Data
- Data minima e maxima
- Range em dias
- Datas futuras (anomalia)
- Gaps temporais

### Qualidade
- % Missing por coluna
- Colunas com alta cardinalidade
- Possives IDs
- Colunas constantes (mesmo valor)

## Output

```markdown
## Perfil: vendas.csv

### Visao Geral
| Metrica | Valor |
|---------|-------|
| Linhas | 50.000 |
| Colunas | 12 |
| Memoria | 15.2 MB |
| Qualidade | 94.5% |
| Duplicatas | 0 |

### Colunas

#### valor (Numerico)
| Estatistica | Valor |
|-------------|-------|
| Count | 50.000 |
| Mean | 245.50 |
| Std | 89.32 |
| Min | 10.00 |
| 25% | 180.00 |
| 50% | 235.00 |
| 75% | 300.00 |
| Max | 1250.00 |
| Outliers | 127 (0.25%) |

#### status (Categorico)
| Valor | Count | % |
|-------|-------|---|
| aprovado | 35.000 | 70% |
| pendente | 10.000 | 20% |
| cancelado | 5.000 | 10% |
```
