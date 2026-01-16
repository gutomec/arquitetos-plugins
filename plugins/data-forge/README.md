# Data Forge

O sistema de analise de dados e estatistica mais avancado do universo.

## Instalacao

```bash
# Adicionar marketplace (se ainda nao adicionou)
/plugin marketplace add gutomec/arquitetos-plugins

# Instalar plugin
/plugin install data-forge@arquitetos-plugins
```

## Capacidades

- *Conexao Universal*: CSV, Excel, Parquet, PostgreSQL, MySQL, SQLite, SQL Server
- *Profiling Automatico*: Schema, tipos, estatisticas, qualidade
- *Analise Estatistica*: Testes de hipotese, correlacoes, regressoes, clustering
- *Insights Automaticos*: Geracao de insights actionaveis
- *Linguagem Natural*: Faca perguntas em portugues sobre seus dados

## Comandos

| Comando | Descricao |
|---------|-----------|
| `/analisar-dados` | Analisa arquivo ou diretorio |
| `/conectar-banco` | Conecta a database |
| `/perfil-dados` | Gera perfil detalhado |
| `/estatisticas` | Executa analises estatisticas |
| `/perguntar-dados` | Pergunta em linguagem natural |
| `/exportar-analise` | Exporta resultados |

## Exemplos de Uso

### Analisar CSVs
```bash
/analisar-dados ./vendas.csv
/analisar-dados ./data/ --linhas 100
```

### Conectar a Banco
```bash
/conectar-banco postgresql://user:pass@host:5432/database
/conectar-banco sqlite:///./local.db
```

### Fazer Perguntas
```bash
/perguntar-dados "Qual o valor medio das vendas?"
/perguntar-dados "Qual regiao vende mais?"
/perguntar-dados "As vendas estao crescendo?"
```

### Estatisticas Avancadas
```bash
/estatisticas comparar --variavel valor --grupo regiao
/estatisticas correlacao --x preco --y quantidade
/estatisticas clustering --features "idade,renda,frequencia"
```

## Agentes

| Agente | Especialidade |
|--------|---------------|
| `data-orchestrator` | Coordena o processo de analise |
| `data-connector` | Conecta a fontes de dados |
| `data-profiler` | Gera perfis e estatisticas |
| `data-scientist` | Executa analises avancadas |
| `data-storyteller` | Traduz dados em narrativas |

## O Agente se Auto-Transforma

Ao analisar seus dados, o Data Forge:

1. *Entende o contexto*: Identifica tipo de dados (vendas, clientes, financeiro)
2. *Adapta a analise*: Sugere metricas relevantes para o dominio
3. *Gera insights*: Produz descobertas actionaveis automaticamente
4. *Responde perguntas*: Funciona como um cientista de dados especialista

## Stack Tecnica

- *Polars*: DataFrames de alta performance
- *Pandas*: Compatibilidade universal
- *SciPy/Statsmodels*: Analises estatisticas
- *SQLAlchemy*: Conexao multi-banco
- *ydata-profiling*: EDA automatizado

## Dependencias Python

```bash
pip install polars pandas numpy scipy statsmodels scikit-learn \
            sqlalchemy psycopg2-binary pymysql openpyxl pyarrow \
            ydata-profiling sweetviz
```

## Licenca

MIT
