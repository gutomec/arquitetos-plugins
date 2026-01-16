---
name: analisar-dados
description: Analisa arquivos CSV, Excel ou diretorio de dados. Gera perfil completo, estatisticas e insights automaticos.
---

# /analisar-dados

Analise automatica de dados com profiling completo e insights.

## Uso

```
/analisar-dados <caminho>
/analisar-dados <caminho> --linhas <N>
/analisar-dados <caminho> --formato <csv|excel|parquet>
```

## Parametros

| Parametro | Descricao | Default |
|-----------|-----------|---------|
| `<caminho>` | Arquivo ou diretorio | obrigatorio |
| `--linhas` | Numero de linhas para amostra | 50 |
| `--formato` | Formato dos arquivos | auto-detect |
| `--encoding` | Encoding dos arquivos | utf-8 |
| `--separador` | Separador CSV | auto-detect |

## Exemplos

```bash
# Arquivo unico
/analisar-dados ./vendas.csv

# Diretorio inteiro
/analisar-dados ./data/

# Excel especifico
/analisar-dados ./relatorio.xlsx --linhas 100

# CSV com separador diferente
/analisar-dados ./dados.csv --separador ";"
```

## O que sera analisado

1. *Schema*: Colunas, tipos, tamanho
2. *Qualidade*: Missing values, duplicatas, outliers
3. *Estatisticas*: Media, mediana, distribuicao
4. *Categorias*: Valores unicos, frequencias
5. *Sugestoes*: Analises recomendadas

## Fluxo

```
[Entrada] -> [Data Connector] -> [Data Profiler] -> [Data Storyteller]
                   |                    |                    |
              Conecta/Le        Analisa Schema       Gera Relatorio
                              Estatisticas          Recomendacoes
```

## Output

Relatorio completo com:
- Visao geral do dataset
- Perfil de cada coluna
- Problemas de qualidade identificados
- Analises estatisticas sugeridas
- Proximos passos recomendados
