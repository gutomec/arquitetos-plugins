---
name: insight-generation
description: Tecnicas para geracao automatica de insights actionaveis a partir de dados.
---

# Insight Generation

Como gerar insights automaticos e actionaveis.

## Framework de Insights

### Tipos de Insights

| Tipo | Descricao | Exemplo |
|------|-----------|---------|
| Descritivo | O que aconteceu? | "Vendas cairam 15% em marco" |
| Diagnostico | Por que aconteceu? | "Queda concentrada em produtos da categoria X" |
| Preditivo | O que vai acontecer? | "Tendencia sugere recuperacao em 2 meses" |
| Prescritivo | O que fazer? | "Aumentar promocoes na categoria X" |

### Estrutura de um Insight

```python
@dataclass
class Insight:
    title: str              # Titulo conciso
    description: str        # Descricao em 1-2 frases
    evidence: dict          # Dados que suportam
    confidence: float       # 0-1, nivel de confianca
    impact: str            # alto, medio, baixo
    actionable: bool       # Se ha acao clara
    recommendations: list  # Lista de acoes sugeridas
```

## Deteccao Automatica de Insights

### 1. Insights de Distribuicao

```python
def distribution_insights(df: pl.DataFrame, column: str) -> list:
    insights = []
    series = df[column].drop_nulls()

    # Verificar assimetria
    skew = series.skew()
    if abs(skew) > 1:
        direction = "direita" if skew > 0 else "esquerda"
        insights.append(Insight(
            title=f"Distribuicao assimetrica em {column}",
            description=f"A distribuicao de {column} e fortemente assimetrica para {direction} (skew={skew:.2f})",
            evidence={"skewness": skew},
            confidence=0.9,
            impact="medio",
            actionable=True,
            recommendations=[
                f"Considerar transformacao logaritmica para {column}",
                "Usar mediana ao inves de media para resumir"
            ]
        ))

    # Verificar outliers extremos
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    outlier_pct = ((series < q1 - 3*iqr) | (series > q3 + 3*iqr)).sum() / len(series) * 100
    if outlier_pct > 1:
        insights.append(Insight(
            title=f"Outliers significativos em {column}",
            description=f"{outlier_pct:.1f}% dos valores sao outliers extremos",
            evidence={"outlier_percentage": outlier_pct},
            confidence=0.95,
            impact="alto",
            actionable=True,
            recommendations=[
                "Investigar causa dos valores extremos",
                "Considerar tratamento ou remocao"
            ]
        ))

    return insights
```

### 2. Insights de Tendencia

```python
def trend_insights(df: pl.DataFrame, date_col: str, value_col: str) -> list:
    insights = []

    # Calcular tendencia
    df_sorted = df.sort(date_col)
    values = df_sorted[value_col].to_numpy()
    x = np.arange(len(values))

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

    if p_value < 0.05:
        direction = "crescente" if slope > 0 else "decrescente"
        change_pct = (slope * len(values)) / values.mean() * 100

        insights.append(Insight(
            title=f"Tendencia {direction} em {value_col}",
            description=f"{value_col} apresenta tendencia {direction} de {abs(change_pct):.1f}% no periodo",
            evidence={
                "slope": slope,
                "r_squared": r_value**2,
                "p_value": p_value
            },
            confidence=min(r_value**2, 0.95),
            impact="alto" if abs(change_pct) > 20 else "medio",
            actionable=True,
            recommendations=[
                f"Investigar fatores que {'impulsionam' if slope > 0 else 'prejudicam'} {value_col}",
                f"Projetar valores futuros baseado na tendencia"
            ]
        ))

    return insights
```

### 3. Insights de Comparacao

```python
def comparison_insights(df: pl.DataFrame, numeric_col: str, group_col: str) -> list:
    insights = []

    # Calcular estatisticas por grupo
    group_stats = df.group_by(group_col).agg([
        pl.col(numeric_col).mean().alias("mean"),
        pl.col(numeric_col).std().alias("std"),
        pl.col(numeric_col).count().alias("count")
    ])

    # Encontrar maior e menor
    max_group = group_stats.sort("mean", descending=True).row(0)
    min_group = group_stats.sort("mean").row(0)

    diff_pct = (max_group[1] - min_group[1]) / min_group[1] * 100

    if diff_pct > 20:
        insights.append(Insight(
            title=f"Diferenca significativa entre grupos em {numeric_col}",
            description=f"{max_group[0]} tem {numeric_col} {diff_pct:.0f}% maior que {min_group[0]}",
            evidence={
                "top_group": {"name": max_group[0], "mean": max_group[1]},
                "bottom_group": {"name": min_group[0], "mean": min_group[1]},
                "difference_pct": diff_pct
            },
            confidence=0.85,
            impact="alto",
            actionable=True,
            recommendations=[
                f"Investigar por que {max_group[0]} performa melhor",
                f"Aplicar melhores praticas de {max_group[0]} em {min_group[0]}"
            ]
        ))

    return insights
```

### 4. Insights de Correlacao

```python
def correlation_insights(df: pl.DataFrame, col1: str, col2: str) -> list:
    insights = []

    corr, pvalue = stats.pearsonr(
        df[col1].drop_nulls().to_numpy(),
        df[col2].drop_nulls().to_numpy()
    )

    if abs(corr) > 0.7 and pvalue < 0.05:
        direction = "positiva" if corr > 0 else "negativa"
        strength = "muito forte" if abs(corr) > 0.9 else "forte"

        insights.append(Insight(
            title=f"Correlacao {strength} entre {col1} e {col2}",
            description=f"Existe correlacao {direction} {strength} (r={corr:.2f}, p={pvalue:.4f})",
            evidence={
                "correlation": corr,
                "p_value": pvalue
            },
            confidence=0.9,
            impact="alto",
            actionable=True,
            recommendations=[
                f"{'Aumentar' if corr > 0 else 'Reduzir'} {col1} pode impactar {col2}",
                "Investigar relacao de causalidade"
            ]
        ))

    return insights
```

### 5. Insights de Anomalia

```python
def anomaly_insights(df: pl.DataFrame, date_col: str, value_col: str) -> list:
    insights = []

    # Calcular baseline
    mean = df[value_col].mean()
    std = df[value_col].std()

    # Encontrar anomalias
    anomalies = df.filter(
        (pl.col(value_col) > mean + 3*std) |
        (pl.col(value_col) < mean - 3*std)
    )

    if anomalies.height > 0:
        insights.append(Insight(
            title=f"Anomalias detectadas em {value_col}",
            description=f"Encontradas {anomalies.height} anomalias que desviam mais de 3 desvios padrao",
            evidence={
                "anomaly_count": anomalies.height,
                "anomaly_dates": anomalies[date_col].to_list()[:5],
                "anomaly_values": anomalies[value_col].to_list()[:5]
            },
            confidence=0.95,
            impact="alto",
            actionable=True,
            recommendations=[
                "Investigar eventos nessas datas",
                "Verificar se sao erros de dados ou eventos reais"
            ]
        ))

    return insights
```

## Priorizacao de Insights

```python
def prioritize_insights(insights: list) -> list:
    """Ordena insights por relevancia"""

    def score(insight: Insight) -> float:
        impact_scores = {"alto": 3, "medio": 2, "baixo": 1}
        return (
            insight.confidence * 0.3 +
            impact_scores.get(insight.impact, 1) / 3 * 0.4 +
            (1 if insight.actionable else 0) * 0.3
        )

    return sorted(insights, key=score, reverse=True)
```

## Template de Relatorio

```python
def generate_insight_report(insights: list) -> str:
    report = "# Principais Insights\n\n"

    prioritized = prioritize_insights(insights)

    for i, insight in enumerate(prioritized[:10], 1):
        report += f"""
## {i}. {insight.title}

{insight.description}

**Confianca:** {insight.confidence*100:.0f}% | **Impacto:** {insight.impact}

### Evidencias
{format_evidence(insight.evidence)}

### Recomendacoes
{"".join(f"- {r}\n" for r in insight.recommendations)}

---
"""

    return report
```

## Insights Automaticos por Dominio

### E-commerce
- Produtos mais vendidos vs menos vendidos
- Sazonalidade de vendas
- Ticket medio por categoria
- Taxa de conversao por canal

### Financeiro
- Tendencias de receita/despesa
- Concentracao de clientes
- Inadimplencia por segmento
- Margem por produto

### RH
- Turnover por departamento
- Satisfacao vs performance
- Tempo medio de contratacao
- Absenteismo por periodo
