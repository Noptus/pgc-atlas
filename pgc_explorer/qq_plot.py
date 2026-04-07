"""
QQ plot data generation for GWAS p-values.
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd


def prepare_qq_data(
    df: pd.DataFrame,
    pval_col: str = "pval",
    max_points: int = 50_000,
    color: str = "#3B82F6",
) -> Dict[str, Any]:
    """Generate QQ plot data comparing observed vs expected p-values.

    Returns Plotly-ready traces and layout.
    """
    pvals = df[pval_col].dropna()
    pvals = pvals[pvals > 0].sort_values()

    if len(pvals) > max_points:
        # Keep all significant + subsample the rest
        sig = pvals[pvals < 1e-4]
        nonsig = pvals[pvals >= 1e-4].sample(n=min(max_points, len(pvals[pvals >= 1e-4])), random_state=42)
        pvals = pd.concat([sig, nonsig]).sort_values()

    n = len(pvals)
    expected = -np.log10(np.arange(1, n + 1) / (n + 1))
    observed = -np.log10(pvals.values)

    # Genomic inflation factor (lambda)
    median_chi2 = np.median((-np.log10(df[pval_col].dropna().values.clip(min=1e-300))) * 2 * np.log(10))
    # Approximate: lambda = median(chi2) / 0.4549
    # More accurate: use scipy
    from scipy import stats as sp_stats
    chi2_vals = sp_stats.chi2.ppf(1 - df[pval_col].dropna().values.clip(min=1e-300, max=1-1e-10), df=1)
    lambda_gc = float(np.median(chi2_vals) / sp_stats.chi2.ppf(0.5, df=1))

    max_val = max(float(expected.max()), float(observed.max())) + 0.5

    traces = [
        {
            "type": "scattergl",
            "mode": "markers",
            "x": expected.tolist(),
            "y": observed.tolist(),
            "marker": {"color": color, "size": 3, "opacity": 0.6},
            "name": "Observed",
            "hovertemplate": "Expected: %{x:.2f}<br>Observed: %{y:.2f}<extra></extra>",
        },
        {
            "type": "scatter",
            "mode": "lines",
            "x": [0, max_val],
            "y": [0, max_val],
            "line": {"color": "#EF4444", "width": 1, "dash": "dash"},
            "name": "Expected",
            "showlegend": False,
        },
    ]

    layout = {
        "xaxis": {"title": "Expected -log₁₀(p)", "range": [0, max_val]},
        "yaxis": {"title": "Observed -log₁₀(p)", "range": [0, max_val]},
        "annotations": [
            {
                "x": 0.05,
                "y": 0.95,
                "xref": "paper",
                "yref": "paper",
                "text": f"λ<sub>GC</sub> = {lambda_gc:.3f}",
                "showarrow": False,
                "font": {"size": 14, "color": "#E2E8F0"},
            }
        ],
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#E2E8F0"},
        "margin": {"l": 60, "r": 20, "t": 40, "b": 60},
    }

    return {"traces": traces, "layout": layout, "lambda_gc": lambda_gc}
