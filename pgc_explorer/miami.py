"""
Miami plot — bidirectional Manhattan comparing two GWAS datasets.
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd

from .config import CHROMOSOME_LENGTHS, SIGNIFICANCE_THRESHOLD


def prepare_miami_data(
    df_top: pd.DataFrame,
    df_bottom: pd.DataFrame,
    label_top: str = "Disorder 1",
    label_bottom: str = "Disorder 2",
    color_top: str = "#3B82F6",
    color_bottom: str = "#10B981",
    chr_col: str = "chr",
    pos_col: str = "bp",
    pval_col: str = "pval",
    snp_col: str = "snp",
    max_points: int = 80_000,
) -> Dict[str, Any]:
    """Generate Miami plot data for two GWAS datasets.

    Top panel shows disorder 1 (positive y), bottom shows disorder 2 (negative y).
    """
    chr_offsets = {}
    running = 0
    for c in range(1, 23):
        chr_offsets[c] = running
        running += CHROMOSOME_LENGTHS.get(c, 250_000_000)

    def _process(df, max_pts):
        df = df.dropna(subset=[pval_col])
        df = df[df[pval_col] > 0].copy()
        if len(df) > max_pts:
            sig = df[df[pval_col] <= 1e-5]
            nonsig = df[df[pval_col] > 1e-5].sample(n=min(max_pts, len(df[df[pval_col] > 1e-5])), random_state=42)
            df = pd.concat([sig, nonsig])
        df["x"] = df[pos_col] + df[chr_col].map(chr_offsets)
        df["y"] = -np.log10(df[pval_col].clip(lower=1e-300))
        return df

    top = _process(df_top, max_points)
    bottom = _process(df_bottom, max_points)

    traces = [
        {
            "type": "scattergl",
            "mode": "markers",
            "x": top["x"].tolist(),
            "y": top["y"].tolist(),
            "marker": {
                "color": [("#EF4444" if p <= SIGNIFICANCE_THRESHOLD else color_top) for p in top[pval_col]],
                "size": 3,
                "opacity": 0.6,
            },
            "name": label_top,
            "hovertemplate": f"{label_top}<br>%{{text}}<extra></extra>",
            "text": [f"{s} chr{c}:{p:,} P={pv:.2e}" for s, c, p, pv in zip(top.get(snp_col, [""]*len(top)), top[chr_col], top[pos_col], top[pval_col])],
        },
        {
            "type": "scattergl",
            "mode": "markers",
            "x": bottom["x"].tolist(),
            "y": (-bottom["y"]).tolist(),
            "marker": {
                "color": [("#EF4444" if p <= SIGNIFICANCE_THRESHOLD else color_bottom) for p in bottom[pval_col]],
                "size": 3,
                "opacity": 0.6,
            },
            "name": label_bottom,
            "hovertemplate": f"{label_bottom}<br>%{{text}}<extra></extra>",
            "text": [f"{s} chr{c}:{p:,} P={pv:.2e}" for s, c, p, pv in zip(bottom.get(snp_col, [""]*len(bottom)), bottom[chr_col], bottom[pos_col], bottom[pval_col])],
        },
    ]

    tick_vals = [chr_offsets[c] + CHROMOSOME_LENGTHS.get(c, 250_000_000) // 2 for c in range(1, 23)]
    tick_text = [str(c) for c in range(1, 23)]

    max_y = max(top["y"].max(), bottom["y"].max()) + 1

    layout = {
        "xaxis": {"tickvals": tick_vals, "ticktext": tick_text, "title": "Chromosome", "showgrid": False},
        "yaxis": {"title": f"-log₁₀(p)  ↑ {label_top}  |  ↓ {label_bottom}", "range": [-max_y, max_y], "zeroline": True, "zerolinecolor": "#475569"},
        "shapes": [
            {"type": "line", "x0": 0, "x1": running, "y0": -np.log10(SIGNIFICANCE_THRESHOLD), "y1": -np.log10(SIGNIFICANCE_THRESHOLD), "line": {"color": "#EF4444", "width": 1, "dash": "dash"}},
            {"type": "line", "x0": 0, "x1": running, "y0": np.log10(SIGNIFICANCE_THRESHOLD), "y1": np.log10(SIGNIFICANCE_THRESHOLD), "line": {"color": "#EF4444", "width": 1, "dash": "dash"}},
        ],
        "hovermode": "closest",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#E2E8F0"},
    }

    return {"traces": traces, "layout": layout}
