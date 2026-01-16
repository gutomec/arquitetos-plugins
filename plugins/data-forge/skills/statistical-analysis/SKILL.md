---
name: statistical-analysis
description: Metodos e testes estatisticos para analise de dados, incluindo testes de hipotese, correlacoes, regressoes e mais.
---

# Statistical Analysis

Guia completo de analises estatisticas.

## Testes de Hipotese

### Quando Usar Cada Teste

| Situacao | Teste | Funcao |
|----------|-------|--------|
| Comparar 2 medias (amostras independentes) | t-test independente | `ttest_ind` |
| Comparar 2 medias (mesma amostra) | t-test pareado | `ttest_rel` |
| Comparar 3+ medias | ANOVA | `f_oneway` |
| Comparar proporcoes | Chi-squared | `chi2_contingency` |
| Testar normalidade | Shapiro-Wilk | `shapiro` |
| Comparar distribuicoes | Mann-Whitney U | `mannwhitneyu` |
| Correlacao | Pearson/Spearman | `pearsonr`, `spearmanr` |

### Implementacao

```python
from scipy import stats
import numpy as np

class StatisticalTests:

    @staticmethod
    def t_test(group1: np.ndarray, group2: np.ndarray, paired: bool = False):
        """Compara medias de dois grupos"""
        if paired:
            stat, pvalue = stats.ttest_rel(group1, group2)
            test_name = "t-test pareado"
        else:
            stat, pvalue = stats.ttest_ind(group1, group2)
            test_name = "t-test independente"

        return {
            "test": test_name,
            "statistic": round(stat, 4),
            "p_value": round(pvalue, 6),
            "significant": pvalue < 0.05,
            "effect_size": StatisticalTests.cohens_d(group1, group2),
            "interpretation": StatisticalTests.interpret_pvalue(pvalue)
        }

    @staticmethod
    def anova(*groups):
        """Compara medias de 3+ grupos"""
        stat, pvalue = stats.f_oneway(*groups)

        return {
            "test": "ANOVA one-way",
            "statistic": round(stat, 4),
            "p_value": round(pvalue, 6),
            "significant": pvalue < 0.05,
            "interpretation": StatisticalTests.interpret_pvalue(pvalue),
            "post_hoc": "Realizar Tukey HSD se significativo"
        }

    @staticmethod
    def chi_squared(contingency_table: np.ndarray):
        """Teste de independencia para variaveis categoricas"""
        chi2, pvalue, dof, expected = stats.chi2_contingency(contingency_table)

        return {
            "test": "Chi-squared",
            "statistic": round(chi2, 4),
            "p_value": round(pvalue, 6),
            "degrees_of_freedom": dof,
            "significant": pvalue < 0.05,
            "interpretation": StatisticalTests.interpret_pvalue(pvalue)
        }

    @staticmethod
    def normality_test(data: np.ndarray):
        """Testa se dados seguem distribuicao normal"""
        if len(data) < 50:
            stat, pvalue = stats.shapiro(data)
            test_name = "Shapiro-Wilk"
        else:
            stat, pvalue = stats.normaltest(data)
            test_name = "D'Agostino-Pearson"

        return {
            "test": test_name,
            "statistic": round(stat, 4),
            "p_value": round(pvalue, 6),
            "is_normal": pvalue > 0.05,
            "interpretation": "Distribuicao normal" if pvalue > 0.05
                            else "Distribuicao nao-normal"
        }

    @staticmethod
    def cohens_d(group1, group2):
        """Calcula tamanho do efeito (Cohen's d)"""
        n1, n2 = len(group1), len(group2)
        var1, var2 = group1.var(), group2.var()
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        d = (group1.mean() - group2.mean()) / pooled_std

        magnitude = "pequeno" if abs(d) < 0.5 else \
                   "medio" if abs(d) < 0.8 else "grande"

        return {"d": round(d, 3), "magnitude": magnitude}

    @staticmethod
    def interpret_pvalue(p):
        if p < 0.001:
            return "Altamente significativo (p < 0.001)"
        elif p < 0.01:
            return "Muito significativo (p < 0.01)"
        elif p < 0.05:
            return "Significativo (p < 0.05)"
        elif p < 0.1:
            return "Marginalmente significativo (p < 0.1)"
        else:
            return "Nao significativo (p >= 0.1)"
```

## Correlacao e Regressao

```python
class CorrelationRegression:

    @staticmethod
    def correlation(x: np.ndarray, y: np.ndarray, method: str = "pearson"):
        """Calcula correlacao entre duas variaveis"""
        if method == "pearson":
            corr, pvalue = stats.pearsonr(x, y)
        elif method == "spearman":
            corr, pvalue = stats.spearmanr(x, y)
        elif method == "kendall":
            corr, pvalue = stats.kendalltau(x, y)

        strength = "muito forte" if abs(corr) > 0.9 else \
                  "forte" if abs(corr) > 0.7 else \
                  "moderada" if abs(corr) > 0.5 else \
                  "fraca" if abs(corr) > 0.3 else "muito fraca"

        direction = "positiva" if corr > 0 else "negativa"

        return {
            "method": method,
            "correlation": round(corr, 4),
            "p_value": round(pvalue, 6),
            "significant": pvalue < 0.05,
            "strength": strength,
            "direction": direction,
            "interpretation": f"Correlacao {strength} {direction}"
        }

    @staticmethod
    def linear_regression(X: np.ndarray, y: np.ndarray):
        """Regressao linear simples ou multipla"""
        import statsmodels.api as sm

        X_with_const = sm.add_constant(X)
        model = sm.OLS(y, X_with_const).fit()

        return {
            "r_squared": round(model.rsquared, 4),
            "adj_r_squared": round(model.rsquared_adj, 4),
            "f_statistic": round(model.fvalue, 4),
            "f_pvalue": round(model.f_pvalue, 6),
            "coefficients": {
                name: {
                    "value": round(coef, 4),
                    "std_err": round(se, 4),
                    "t_stat": round(t, 4),
                    "p_value": round(p, 6),
                    "significant": p < 0.05
                }
                for name, coef, se, t, p in zip(
                    ["const"] + list(range(X.shape[1] if len(X.shape) > 1 else 1)),
                    model.params,
                    model.bse,
                    model.tvalues,
                    model.pvalues
                )
            },
            "residuals": {
                "mean": round(model.resid.mean(), 6),
                "std": round(model.resid.std(), 4)
            }
        }
```

## Analise de Variancia

```python
class VarianceAnalysis:

    @staticmethod
    def one_way_anova(df, numeric_col: str, group_col: str):
        """ANOVA de um fator"""
        groups = [
            df.filter(pl.col(group_col) == val)[numeric_col].to_numpy()
            for val in df[group_col].unique().to_list()
        ]

        stat, pvalue = stats.f_oneway(*groups)

        # Calcular eta-squared (tamanho do efeito)
        all_data = np.concatenate(groups)
        grand_mean = all_data.mean()
        ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
        ss_total = sum((all_data - grand_mean)**2)
        eta_squared = ss_between / ss_total

        return {
            "test": "ANOVA one-way",
            "f_statistic": round(stat, 4),
            "p_value": round(pvalue, 6),
            "significant": pvalue < 0.05,
            "eta_squared": round(eta_squared, 4),
            "effect_size": "grande" if eta_squared > 0.14 else
                          "medio" if eta_squared > 0.06 else "pequeno",
            "group_means": {
                val: round(df.filter(pl.col(group_col) == val)[numeric_col].mean(), 4)
                for val in df[group_col].unique().to_list()
            }
        }

    @staticmethod
    def tukey_hsd(df, numeric_col: str, group_col: str):
        """Post-hoc Tukey HSD para comparacoes multiplas"""
        from statsmodels.stats.multicomp import pairwise_tukeyhsd

        result = pairwise_tukeyhsd(
            df[numeric_col].to_numpy(),
            df[group_col].to_numpy()
        )

        return {
            "comparisons": [
                {
                    "group1": str(row[0]),
                    "group2": str(row[1]),
                    "diff": round(row[2], 4),
                    "p_adj": round(row[3], 6),
                    "significant": row[4]
                }
                for row in result.summary().data[1:]
            ]
        }
```

## Interpretacao de Resultados

### Niveis de Significancia

| P-valor | Interpretacao | Simbolo |
|---------|---------------|---------|
| p < 0.001 | Altamente significativo | *** |
| p < 0.01 | Muito significativo | ** |
| p < 0.05 | Significativo | * |
| p < 0.1 | Marginalmente significativo | . |
| p >= 0.1 | Nao significativo | ns |

### Tamanhos de Efeito

| Medida | Pequeno | Medio | Grande |
|--------|---------|-------|--------|
| Cohen's d | 0.2 | 0.5 | 0.8 |
| Eta-squared | 0.01 | 0.06 | 0.14 |
| R-squared | 0.02 | 0.13 | 0.26 |
| Correlacao | 0.1 | 0.3 | 0.5 |

### Template de Relatorio

```markdown
## Resultado da Analise Estatistica

### Teste Realizado
- Tipo: {nome_do_teste}
- Variavel dependente: {variavel}
- Grupos/Fatores: {grupos}

### Resultados
| Metrica | Valor |
|---------|-------|
| Estatistica | {valor} |
| P-valor | {p_value} |
| Tamanho do efeito | {effect_size} |

### Interpretacao
{interpretacao_em_linguagem_natural}

### Conclusao
{conclusao_pratica}
```
