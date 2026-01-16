---
name: data-cleaning
description: Padroes e tecnicas de limpeza e tratamento de dados para garantir qualidade e consistencia.
---

# Data Cleaning

Guia de limpeza e tratamento de dados.

## Estrategias de Tratamento

### Missing Values

```python
import polars as pl
import numpy as np

class MissingValueHandler:

    @staticmethod
    def analyze_missing(df: pl.DataFrame) -> dict:
        """Analisa padroes de missing values"""
        missing = {
            col: {
                "count": df[col].null_count(),
                "percentage": df[col].null_count() / df.height * 100
            }
            for col in df.columns
        }

        return {
            "by_column": missing,
            "total_missing": sum(m["count"] for m in missing.values()),
            "complete_rows": df.drop_nulls().height,
            "complete_row_pct": df.drop_nulls().height / df.height * 100
        }

    @staticmethod
    def handle_missing(df: pl.DataFrame, column: str, strategy: str, value=None):
        """Trata missing values com diferentes estrategias"""
        if strategy == "drop":
            return df.drop_nulls(subset=[column])

        elif strategy == "mean":
            fill_value = df[column].mean()
            return df.with_columns(pl.col(column).fill_null(fill_value))

        elif strategy == "median":
            fill_value = df[column].median()
            return df.with_columns(pl.col(column).fill_null(fill_value))

        elif strategy == "mode":
            fill_value = df[column].mode().first()
            return df.with_columns(pl.col(column).fill_null(fill_value))

        elif strategy == "constant":
            return df.with_columns(pl.col(column).fill_null(value))

        elif strategy == "forward_fill":
            return df.with_columns(pl.col(column).forward_fill())

        elif strategy == "backward_fill":
            return df.with_columns(pl.col(column).backward_fill())

        elif strategy == "interpolate":
            return df.with_columns(pl.col(column).interpolate())

        else:
            raise ValueError(f"Estrategia desconhecida: {strategy}")

    @staticmethod
    def recommend_strategy(df: pl.DataFrame, column: str) -> str:
        """Recomenda estrategia baseada no tipo e distribuicao"""
        dtype = df[column].dtype
        missing_pct = df[column].null_count() / df.height * 100

        if missing_pct > 50:
            return "drop_column"  # Considerar remover coluna

        if dtype in pl.NUMERIC_DTYPES:
            # Verificar se distribuicao e simetrica
            skew = abs(df[column].drop_nulls().skew())
            if skew < 0.5:
                return "mean"
            else:
                return "median"

        elif dtype == pl.Utf8:
            n_unique = df[column].n_unique()
            if n_unique < 20:
                return "mode"
            else:
                return "constant"  # com "DESCONHECIDO"

        elif dtype in [pl.Date, pl.Datetime]:
            return "interpolate"

        return "drop"
```

### Outliers

```python
class OutlierHandler:

    @staticmethod
    def detect_iqr(series: pl.Series, multiplier: float = 1.5) -> pl.Series:
        """Detecta outliers usando IQR"""
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr

        return (series < lower) | (series > upper)

    @staticmethod
    def detect_zscore(series: pl.Series, threshold: float = 3.0) -> pl.Series:
        """Detecta outliers usando Z-score"""
        z_scores = (series - series.mean()) / series.std()
        return z_scores.abs() > threshold

    @staticmethod
    def handle_outliers(df: pl.DataFrame, column: str, strategy: str):
        """Trata outliers com diferentes estrategias"""
        outlier_mask = OutlierHandler.detect_iqr(df[column])

        if strategy == "remove":
            return df.filter(~outlier_mask)

        elif strategy == "cap":
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            return df.with_columns(
                pl.col(column).clip(lower, upper)
            )

        elif strategy == "winsorize":
            lower_pct = df[column].quantile(0.05)
            upper_pct = df[column].quantile(0.95)
            return df.with_columns(
                pl.col(column).clip(lower_pct, upper_pct)
            )

        elif strategy == "null":
            return df.with_columns(
                pl.when(outlier_mask)
                .then(None)
                .otherwise(pl.col(column))
                .alias(column)
            )

        elif strategy == "log_transform":
            return df.with_columns(
                pl.col(column).log1p()
            )

        return df
```

### Duplicatas

```python
class DuplicateHandler:

    @staticmethod
    def analyze_duplicates(df: pl.DataFrame, subset: list = None) -> dict:
        """Analisa duplicatas no dataset"""
        if subset:
            dup_mask = df.select(subset).is_duplicated()
        else:
            dup_mask = df.is_duplicated()

        return {
            "total_duplicates": dup_mask.sum(),
            "duplicate_percentage": dup_mask.sum() / df.height * 100,
            "unique_rows": df.height - dup_mask.sum(),
            "sample_duplicates": df.filter(dup_mask).head(5).to_dict()
        }

    @staticmethod
    def remove_duplicates(df: pl.DataFrame, subset: list = None, keep: str = "first"):
        """Remove duplicatas"""
        if keep == "first":
            return df.unique(subset=subset, keep="first")
        elif keep == "last":
            return df.unique(subset=subset, keep="last")
        elif keep == "none":
            return df.unique(subset=subset, keep="none")
        return df
```

### Padronizacao de Texto

```python
class TextCleaner:

    @staticmethod
    def clean_text(df: pl.DataFrame, column: str, operations: list) -> pl.DataFrame:
        """Aplica operacoes de limpeza em coluna de texto"""
        expr = pl.col(column)

        for op in operations:
            if op == "lowercase":
                expr = expr.str.to_lowercase()
            elif op == "uppercase":
                expr = expr.str.to_uppercase()
            elif op == "strip":
                expr = expr.str.strip_chars()
            elif op == "remove_accents":
                expr = expr.str.replace_all(r"[áàâã]", "a")
                expr = expr.str.replace_all(r"[éèê]", "e")
                expr = expr.str.replace_all(r"[íì]", "i")
                expr = expr.str.replace_all(r"[óòôõ]", "o")
                expr = expr.str.replace_all(r"[úù]", "u")
                expr = expr.str.replace_all(r"[ç]", "c")
            elif op == "remove_special":
                expr = expr.str.replace_all(r"[^a-zA-Z0-9\s]", "")
            elif op == "normalize_spaces":
                expr = expr.str.replace_all(r"\s+", " ")

        return df.with_columns(expr)

    @staticmethod
    def standardize_categories(df: pl.DataFrame, column: str, mapping: dict):
        """Padroniza valores categoricos"""
        for old_values, new_value in mapping.items():
            if isinstance(old_values, tuple):
                for old in old_values:
                    df = df.with_columns(
                        pl.when(pl.col(column).str.to_lowercase() == old.lower())
                        .then(pl.lit(new_value))
                        .otherwise(pl.col(column))
                        .alias(column)
                    )
        return df
```

### Tipos de Dados

```python
class TypeConverter:

    @staticmethod
    def convert_types(df: pl.DataFrame, type_mapping: dict) -> pl.DataFrame:
        """Converte tipos de colunas"""
        for column, target_type in type_mapping.items():
            if target_type == "int":
                df = df.with_columns(pl.col(column).cast(pl.Int64))
            elif target_type == "float":
                df = df.with_columns(pl.col(column).cast(pl.Float64))
            elif target_type == "str":
                df = df.with_columns(pl.col(column).cast(pl.Utf8))
            elif target_type == "date":
                df = df.with_columns(pl.col(column).str.to_date())
            elif target_type == "datetime":
                df = df.with_columns(pl.col(column).str.to_datetime())
            elif target_type == "bool":
                df = df.with_columns(pl.col(column).cast(pl.Boolean))

        return df

    @staticmethod
    def parse_dates(df: pl.DataFrame, column: str, format: str = None):
        """Converte strings para datas"""
        if format:
            return df.with_columns(
                pl.col(column).str.strptime(pl.Date, format)
            )
        else:
            # Tentar formatos comuns
            return df.with_columns(
                pl.col(column).str.to_date()
            )
```

## Pipeline de Limpeza

```python
class DataCleaningPipeline:

    def __init__(self):
        self.steps = []
        self.log = []

    def add_step(self, name: str, func, **kwargs):
        self.steps.append({"name": name, "func": func, "kwargs": kwargs})
        return self

    def run(self, df: pl.DataFrame) -> pl.DataFrame:
        result = df.clone()

        for step in self.steps:
            before_rows = result.height
            result = step["func"](result, **step["kwargs"])
            after_rows = result.height

            self.log.append({
                "step": step["name"],
                "rows_before": before_rows,
                "rows_after": after_rows,
                "rows_removed": before_rows - after_rows
            })

        return result

    def get_report(self) -> str:
        report = "## Relatorio de Limpeza\n\n"
        for entry in self.log:
            report += f"- {entry['step']}: {entry['rows_removed']} linhas removidas\n"
        return report


# Exemplo de uso
pipeline = DataCleaningPipeline()
pipeline.add_step("remove_duplicates", DuplicateHandler.remove_duplicates)
pipeline.add_step("handle_missing_idade", MissingValueHandler.handle_missing,
                  column="idade", strategy="median")
pipeline.add_step("cap_outliers_valor", OutlierHandler.handle_outliers,
                  column="valor", strategy="cap")

clean_df = pipeline.run(df)
print(pipeline.get_report())
```
