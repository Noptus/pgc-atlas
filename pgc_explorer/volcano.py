"""
Volcano plot data generation — effect size vs significance.
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd

from .config import SIGNIFICANCE_THRESHOLD


def prepare_volcano_data(
    df: pd.DataFrame,
    effect_col: str = "effect",
    pval_col: str = "pval",
    snp_col: str = "snp",
    effect_threshold: float = 0.1,
    color_up: str = "#EF4444",
    color_down: str = "#3B82F6",
    color_ns: str = "#6B7280",
    max_points: int = 60_000,
) -> Dict[str, Any]:
    """Generate volcano plot: x = effect size, y = -log10(p).

    Points are colored by significance + direction.
    """
    df = df.dropna(subset=[pval_col, effect_col]).copy()
    df = df[df[pval_col] > 0]

    if len(df) > max_points:
        sig = df[df[pval_col] <= 1e-4]
        nonsig = df[df[pval_col] > 1e-4].sample(n=min(max_points, len(df[df[pval_col] > 1e-4])), random_state=42)
        df = pd.concat([sig, nonsig])

    x = df[effect_col].values
    y = -np.log10(df[pval_col].values.clip(min=1e-300))
    sig = df[pval_col].values <= SIGNIFICANCE_THRESHOLD

    colors = []
    for i in range(len(df)):
        if sig[i] and x[i] > effect_threshold:
            colors.append(color_up)
        elif sig[i] and x[i] < -effect_threshold:
            colors.append(color_down)
        else:
            colors.append(color_ns)

    traces = [{
        "type": "scattergl",
        "mode": "markers",
        "x": x.tolist(),
        "y": y.tolist(),
        "marker": {"color": colors, "size": 3, "opacity": 0.6},
        "text": [f"{s}<br>Effect={e:.4f}<br>P={p:.2e}" for s, e, p in zip(df.get(snp_col, [""]*len(df)), df[effect_col], df[pval_col])],
        "hoverinfo": "text",
        "showlegend": False,
    }]

    layout = {
        "xaxis": {"title": "Effect Size (beta/log OR)", "zeroline": True, "zerolinecolor": "#475569"},
        "yaxis": {"title": "-log₁₀(p-value)"},
        "shapes": [
            {"type": "line", "x0": -abs(x).max()-0.1, "x1": abs(x).max()+0.1, "y0": -np.log10(SIGNIFICANCE_THRESHOLD), "y1": -np.log10(SIGNIFICANCE_THRESHOLD), "line": {"color": "#EF4444", "width": 1, "dash": "dash"}},
        ],
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#E2E8F0"},
        "margin": {"l": 60, "r": 20, "t": 40, "b": 60},
    }

    return {"traces": traces, "layout": layout}
