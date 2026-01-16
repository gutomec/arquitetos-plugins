---
name: data-profiling
description: Tecnicas avancadas de profiling automatico de dados para entender estrutura, qualidade e caracteristicas de qualquer dataset.
---

# Data Profiling

Guia completo para profiling automatico de dados.

## Conceitos Fundamentais

### O que e Data Profiling?

Processo de examinar dados para coletar estatisticas e informacoes sobre:
- Estrutura e schema
- Qualidade e completude
- Distribuicoes e padroes
- Anomalias e outliers
- Relacoes entre variaveis

## Niveis de Profiling

### Nivel 1: Schema Discovery
```python
import polars as pl

def schema_profile(df: pl.DataFrame) -> dict:
    return {
        "n_rows": df.height,
        "n_columns": df.width,
        "columns": [
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "nullable": df[col].null_count() > 0
            }
            for col in df.columns
        ],
        "memory_mb": df.estimated_size("mb")
    }
```

### Nivel 2: Estatisticas Basicas
```python
def basic_stats(df: pl.DataFrame) -> dict:
    numeric_cols = df.select(pl.col(pl.NUMERIC_DTYPES)).columns
    return {
        col: {
            "count": df[col].count(),
            "null_count": df[col].null_count(),
            "null_pct": df[col].null_count() / df.height * 100,
            "unique": df[col].n_unique(),
            "mean": df[col].mean() if col in numeric_cols else None,
            "std": df[col].std() if col in numeric_cols else None
        }
        for col in df.columns
    }
```

### Nivel 3: Distribuicoes
```python
def distribution_profile(series: pl.Series) -> dict:
    if series.dtype in pl.NUMERIC_DTYPES:
        return {
            "min": series.min(),
            "q1": series.quantile(0.25),
            "median": series.median(),
            "q3": series.quantile(0.75),
            "max": series.max(),
            "iqr": series.quantile(0.75) - series.quantile(0.25),
            "range": series.max() - series.min(),
            "skewness": calculate_skewness(series),
            "histogram": create_histogram(series, bins=20)
        }
    else:
        return {
            "unique_values": series.unique().to_list()[:100],
            "value_counts": series.value_counts().head(20).to_dict()
        }
```

### Nivel 4: Qualidade
```python
def quality_profile(df: pl.DataFrame) -> dict:
    return {
        "completeness": {
            col: 1 - (df[col].null_count() / df.height)
            for col in df.columns
        },
        "uniqueness": {
            col: df[col].n_unique() / df.height
            for col in df.columns
        },
        "duplicates": {
            "total_duplicates": df.is_duplicated().sum(),
            "duplicate_pct": df.is_duplicated().sum() / df.height * 100
        },
        "quality_score": calculate_overall_quality(df)
    }
```

## Deteccao Automatica de Tipos

```python
def infer_semantic_type(series: pl.Series) -> str:
    name = series.name.lower()
    dtype = series.dtype
    n_unique = series.n_unique()
    n_total = len(series)

    # Por nome da coluna
    if any(x in name for x in ["id", "codigo", "code"]):
        return "identifier"
    if any(x in name for x in ["email", "mail"]):
        return "email"
    if any(x in name for x in ["telefone", "phone", "celular"]):
        return "phone"
    if any(x in name for x in ["cpf", "cnpj", "ssn"]):
        return "document"
    if any(x in name for x in ["cep", "zip", "postal"]):
        return "postal_code"

    # Por tipo de dado
    if dtype in [pl.Date, pl.Datetime]:
        return "datetime"
    if dtype == pl.Boolean:
        return "boolean"

    # Por cardinalidade
    if dtype in pl.NUMERIC_DTYPES:
        if n_unique == n_total:
            return "identifier"
        if n_unique <= 2:
            return "binary"
        return "numeric"

    if dtype == pl.Utf8:
        if n_unique < 20:
            return "categorical_low"
        if n_unique < 100:
            return "categorical_high"
        if n_unique == n_total:
            return "identifier"
        return "text"

    return "unknown"
```

## Deteccao de Outliers

```python
def detect_outliers_iqr(series: pl.Series) -> dict:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = series.filter(
        (series < lower_bound) | (series > upper_bound)
    )

    return {
        "method": "IQR",
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "n_outliers": len(outliers),
        "pct_outliers": len(outliers) / len(series) * 100,
        "outlier_values": outliers.to_list()[:10]
    }

def detect_outliers_zscore(series: pl.Series, threshold: float = 3.0) -> dict:
    mean = series.mean()
    std = series.std()
    z_scores = (series - mean) / std

    outliers = series.filter(z_scores.abs() > threshold)

    return {
        "method": "Z-Score",
        "threshold": threshold,
        "n_outliers": len(outliers),
        "pct_outliers": len(outliers) / len(series) * 100
    }
```

## Analise de Correlacoes

```python
def correlation_analysis(df: pl.DataFrame) -> dict:
    numeric_df = df.select(pl.col(pl.NUMERIC_DTYPES))

    if numeric_df.width < 2:
        return {"error": "Menos de 2 colunas numericas"}

    corr_matrix = numeric_df.to_pandas().corr()

    # Encontrar correlacoes fortes
    strong_correlations = []
    for i, col1 in enumerate(corr_matrix.columns):
        for j, col2 in enumerate(corr_matrix.columns):
            if i < j:
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.7:
                    strong_correlations.append({
                        "col1": col1,
                        "col2": col2,
                        "correlation": round(corr, 3),
                        "strength": "muito forte" if abs(corr) > 0.9
                                   else "forte" if abs(corr) > 0.8
                                   else "moderada"
                    })

    return {
        "matrix": corr_matrix.to_dict(),
        "strong_correlations": strong_correlations
    }
```

## Score de Qualidade

```python
def calculate_quality_score(df: pl.DataFrame) -> float:
    scores = []

    # Completude (peso 40%)
    null_ratio = sum(df[col].null_count() for col in df.columns) / (df.height * df.width)
    completeness = (1 - null_ratio) * 100
    scores.append(completeness * 0.4)

    # Unicidade (peso 20%)
    duplicate_ratio = df.is_duplicated().sum() / df.height
    uniqueness = (1 - duplicate_ratio) * 100
    scores.append(uniqueness * 0.2)

    # Consistencia de tipos (peso 20%)
    type_consistency = check_type_consistency(df) * 100
    scores.append(type_consistency * 0.2)

    # Validade (peso 20%)
    validity = check_validity(df) * 100
    scores.append(validity * 0.2)

    return round(sum(scores), 1)
```

## Relatorio Automatico

```python
def generate_profile_report(df: pl.DataFrame) -> str:
    profile = {
        "schema": schema_profile(df),
        "stats": basic_stats(df),
        "quality": quality_profile(df),
        "correlations": correlation_analysis(df)
    }

    report = f"""
# Perfil do Dataset

## Visao Geral
- Linhas: {profile['schema']['n_rows']:,}
- Colunas: {profile['schema']['n_columns']}
- Memoria: {profile['schema']['memory_mb']:.2f} MB
- Qualidade: {profile['quality']['quality_score']}%

## Colunas
{format_columns(profile['stats'])}

## Qualidade
{format_quality(profile['quality'])}

## Correlacoes Fortes
{format_correlations(profile['correlations'])}
    """

    return report
```
