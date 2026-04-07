"""
Export utilities — convert filtered GWAS data to various formats.
"""

from __future__ import annotations

import io
from typing import Literal, Optional

import pandas as pd


def export_data(
    df: pd.DataFrame,
    fmt: Literal["csv", "tsv", "json", "parquet", "bed"] = "csv",
    significant_only: bool = False,
    pval_threshold: float = 5e-8,
    columns: Optional[list] = None,
) -> bytes:
    """Export DataFrame to the requested format.

    Parameters
    ----------
    df : GWAS summary statistics DataFrame
    fmt : output format
    significant_only : if True, filter to genome-wide significant variants
    pval_threshold : threshold when significant_only is True
    columns : subset of columns to include

    Returns
    -------
    bytes : serialized data
    """
    if significant_only and "pval" in df.columns:
        df = df[df["pval"] <= pval_threshold]

    if columns:
        df = df[[c for c in columns if c in df.columns]]

    buf = io.BytesIO()

    if fmt == "csv":
        df.to_csv(buf, index=False)
    elif fmt == "tsv":
        df.to_csv(buf, index=False, sep="\t")
    elif fmt == "json":
        buf.write(df.to_json(orient="records", indent=2).encode())
    elif fmt == "parquet":
        df.to_parquet(buf, index=False)
    elif fmt == "bed":
        # BED format: chr, start, end, name, score
        bed = pd.DataFrame({
            "chr": "chr" + df["chr"].astype(str),
            "start": df["bp"] - 1,
            "end": df["bp"],
            "name": df.get("snp", pd.Series(["."]*len(df))),
            "score": df.get("pval", pd.Series([0.0]*len(df))).apply(lambda p: min(1000, int(-10 * (p if p > 0 else 1e-300)))),
        })
        bed.to_csv(buf, index=False, sep="\t", header=False)

    buf.seek(0)
    return buf.read()
