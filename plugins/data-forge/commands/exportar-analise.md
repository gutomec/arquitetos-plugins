---
name: exportar-analise
description: Exporta resultados de analises em diversos formatos (CSV, Excel, HTML, JSON, Markdown).
---

# /exportar-analise

Exporta resultados e relatorios de analise.

## Uso

```
/exportar-analise <formato> [opcoes]
/exportar-analise <formato> --output <caminho>
```

## Formatos Suportados

| Formato | Extensao | Uso |
|---------|----------|-----|
| csv | .csv | Dados tabulares |
| excel | .xlsx | Relatorios formatados |
| json | .json | Integracao com APIs |
| html | .html | Relatorios visuais |
| markdown | .md | Documentacao |
| parquet | .parquet | Big data / performance |

## Exemplos

```bash
# Exportar dados processados
/exportar-analise csv --output ./resultados/dados_limpos.csv

# Relatorio completo em HTML
/exportar-analise html --output ./relatorios/analise_vendas.html

# Perfil em JSON para API
/exportar-analise json --output ./api/perfil.json

# Excel com multiplas abas
/exportar-analise excel --output ./reports/completo.xlsx --multiplas-abas
```

## Opcoes

| Opcao | Descricao |
|-------|-----------|
| `--output` | Caminho do arquivo de saida |
| `--incluir-dados` | Incluir dataset original |
| `--incluir-perfil` | Incluir profiling |
| `--incluir-estatisticas` | Incluir analises estatisticas |
| `--incluir-visualizacoes` | Incluir graficos (HTML/Excel) |
| `--multiplas-abas` | Separar em abas (Excel) |
| `--comprimir` | Gerar arquivo .zip |

## Tipos de Exportacao

### 1. Dados Processados
```bash
# Dataset limpo e tratado
/exportar-analise csv --output dados_tratados.csv --incluir-dados
```

### 2. Relatorio de Profiling
```bash
# Perfil completo em HTML interativo
/exportar-analise html --output perfil.html --incluir-perfil
```

### 3. Resultados Estatisticos
```bash
# Todas as analises em JSON
/exportar-analise json --output stats.json --incluir-estatisticas
```

### 4. Relatorio Executivo
```bash
# Relatorio completo formatado
/exportar-analise excel --output relatorio_executivo.xlsx \
  --incluir-perfil \
  --incluir-estatisticas \
  --multiplas-abas
```

### 5. Documentacao
```bash
# Markdown para README ou wiki
/exportar-analise markdown --output ANALISE.md
```

## Estrutura do Excel Multi-Abas

```
relatorio.xlsx
├── Resumo Executivo
├── Dados Originais
├── Perfil de Colunas
├── Estatisticas Descritivas
├── Correlacoes
├── Analises Especificas
└── Recomendacoes
```

## Estrutura do HTML

```html
relatorio.html
├── Header com metricas-chave
├── Perfil interativo
├── Graficos de distribuicao
├── Tabelas de estatisticas
├── Heatmap de correlacoes
└── Conclusoes e recomendacoes
```

## Output

```
Exportacao concluida com sucesso!

Arquivo: ./relatorios/analise_vendas.xlsx
Tamanho: 2.3 MB
Conteudo:
  - 5 abas
  - 50.000 registros
  - 15 graficos
  - Perfil de 12 colunas

Abrir arquivo? [S/n]
```
