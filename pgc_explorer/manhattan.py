"""
Manhattan plot data generation for Plotly.js consumption.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .config import CHROMOSOME_LENGTHS, SIGNIFICANCE_THRESHOLD, SUGGESTIVE_THRESHOLD


def prepare_manhattan_data(
    df: pd.DataFrame,
    chr_col: str = "chr",
    pos_col: str = "bp",
    pval_col: str = "pval",
    snp_col: str = "snp",
    effect_col: str = "effect",
    max_points: int = 100_000,
    color_even: str = "#3B82F6",
    color_odd: str = "#93C5FD",
    color_sig: str = "#EF4444",
) -> Dict[str, Any]:
    """Transform GWAS data into Plotly-ready Manhattan plot traces.

    Returns a dict with 'traces' (list of Plotly trace dicts) and 'layout'.
    """
    df = df.copy()
    df = df.dropna(subset=[pval_col])
    df = df[df[pval_col] > 0]

    # Downsample non-significant variants for performance
    sig_mask = df[pval_col] <= SUGGESTIVE_THRESHOLD
    sig_df = df[sig_mask]
    nonsig_df = df[~sig_mask]

    if len(nonsig_df) > max_points:
        nonsig_df = nonsig_df.sample(n=max_points, random_state=42)

    df = pd.concat([sig_df, nonsig_df]).sort_values([chr_col, pos_col])

    # Compute cumulative positions
    chr_offsets = {}
    running = 0
    for c in range(1, 23):
        chr_offsets[c] = running
        running += CHROMOSOME_LENGTHS.get(c, 250_000_000)

    df["x"] = df[pos_col] + df[chr_col].map(chr_offsets)
    df["y"] = -np.log10(df[pval_col].clip(lower=1e-300))

    traces = []
    for chrom in sorted(df[chr_col].unique()):
        mask = df[chr_col] == chrom
        cdata = df[mask]
        color = color_even if chrom % 2 == 0 else color_odd

        # Override color for significant hits
        colors = [color_sig if p <= SIGNIFICANCE_THRESHOLD else color for p in cdata[pval_col]]

        trace = {
            "type": "scattergl",
            "mode": "markers",
            "x": cdata["x"].tolist(),
            "y": cdata["y"].tolist(),
            "marker": {"color": colors, "size": 3, "opacity": 0.7},
            "text": [
                f"SNP: {s}<br>Chr{c}:{p:,}<br>P={pv:.2e}"
                for s, c, p, pv in zip(
                    cdata.get(snp_col, [""] * len(cdata)),
                    cdata[chr_col],
                    cdata[pos_col],
                    cdata[pval_col],
                )
            ],
            "hoverinfo": "text",
            "name": f"Chr {chrom}",
            "showlegend": False,
        }
        traces.append(trace)

    # Tick positions (center of each chromosome)
    tick_vals = []
    tick_text = []
    for c in range(1, 23):
        tick_vals.append(chr_offsets[c] + CHROMOSOME_LENGTHS.get(c, 250_000_000) // 2)
        tick_text.append(str(c))

    layout = {
        "xaxis": {
            "tickvals": tick_vals,
            "ticktext": tick_text,
            "title": "Chromosome",
            "showgrid": False,
        },
        "yaxis": {"title": "-log₁₀(p-value)", "zeroline": False},
        "shapes": [
            {
                "type": "line", "x0": 0, "x1": running,
                "y0": -np.log10(SIGNIFICANCE_THRESHOLD),
                "y1": -np.log10(SIGNIFICANCE_THRESHOLD),
                "line": {"color": "#EF4444", "width": 1, "dash": "dash"},
            },
            {
                "type": "line", "x0": 0, "x1": running,
                "y0": -np.log10(SUGGESTIVE_THRESHOLD),
                "y1": -np.log10(SUGGESTIVE_THRESHOLD),
                "line": {"color": "#F59E0B", "width": 1, "dash": "dot"},
            },
        ],
        "hovermode": "closest",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#E2E8F0"},
        "margin": {"l": 60, "r": 20, "t": 40, "b": 60},
    }

    return {"traces": traces, "layout": layout}
