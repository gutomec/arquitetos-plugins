---
name: conectar-banco
description: Conecta a banco de dados e lista tabelas disponiveis para analise.
---

# /conectar-banco

Conecta a bancos de dados SQL para analise.

## Uso

```
/conectar-banco <connection_string>
/conectar-banco --tipo <postgres|mysql|sqlite|sqlserver> --host <host> --db <database>
```

## Bancos Suportados

| Banco | Connection String |
|-------|-------------------|
| PostgreSQL | `postgresql://user:pass@host:5432/database` |
| MySQL | `mysql+pymysql://user:pass@host:3306/database` |
| SQLite | `sqlite:///caminho/arquivo.db` |
| SQL Server | `mssql+pyodbc://user:pass@host/database?driver=ODBC+Driver+17` |

## Exemplos

```bash
# PostgreSQL
/conectar-banco postgresql://admin:senha123@localhost:5432/vendas

# MySQL
/conectar-banco mysql+pymysql://root:pass@db.example.com:3306/analytics

# SQLite local
/conectar-banco sqlite:///./data/local.db

# Usando variaveis de ambiente
/conectar-banco $DATABASE_URL
```

## Parametros Alternativos

```bash
/conectar-banco --tipo postgres --host localhost --porta 5432 --db vendas --user admin
```

| Parametro | Descricao |
|-----------|-----------|
| `--tipo` | postgres, mysql, sqlite, sqlserver |
| `--host` | Hostname ou IP |
| `--porta` | Porta (default varia por tipo) |
| `--db` | Nome do database |
| `--user` | Usuario |
| `--schema` | Schema especifico (opcional) |

## Seguranca

- Senhas podem ser passadas via variavel de ambiente
- Credenciais NUNCA sao logadas
- Use `$DB_PASSWORD` no lugar da senha real

```bash
export DB_PASSWORD="minha_senha_secreta"
/conectar-banco postgresql://admin:$DB_PASSWORD@host/db
```

## Output

Apos conexao bem-sucedida:
- Lista de schemas disponiveis
- Lista de tabelas por schema
- Contagem de registros por tabela
- Relacionamentos identificados (FK)
- Sugestao de tabelas para analisar
