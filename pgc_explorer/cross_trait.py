"""
Cross-trait correlation analysis for GWAS summary statistics.

Computes genetic correlations between pairs of psychiatric disorders using
shared significant loci and effect-size concordance.
"""

from __future__ import annotations

import itertools
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from .config import DISORDERS, SIGNIFICANCE_THRESHOLD

logger = logging.getLogger(__name__)


def compute_sign_concordance(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    snp_col: str = "snp",
    effect_col: str = "effect",
    pval_col: str = "pval",
    threshold: float = SIGNIFICANCE_THRESHOLD,
) -> Dict[str, float]:
    """Compute sign concordance of effect sizes for shared significant SNPs.

    Returns dict with concordance rate, n_shared, binomial p-value.
    """
    sig1 = set(df1.loc[df1[pval_col] <= threshold, snp_col])
    sig2 = set(df2.loc[df2[pval_col] <= threshold, snp_col])
    shared = sig1 & sig2

    if len(shared) < 2:
        return {"concordance": float("nan"), "n_shared": len(shared), "pvalue": 1.0}

    merged = pd.merge(
        df1[df1[snp_col].isin(shared)][[snp_col, effect_col]],
        df2[df2[snp_col].isin(shared)][[snp_col, effect_col]],
        on=snp_col,
        suffixes=("_1", "_2"),
    )

    same_sign = (merged[f"{effect_col}_1"] * merged[f"{effect_col}_2"]) > 0
    concordance = same_sign.mean()
    n = len(merged)

    # Binomial test: is concordance significantly different from 0.5?
    binom_p = stats.binom_test(int(same_sign.sum()), n, 0.5)

    return {"concordance": concordance, "n_shared": n, "pvalue": binom_p}


def effect_correlation(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    snp_col: str = "snp",
    effect_col: str = "effect",
) -> Dict[str, float]:
    """Pearson correlation of effect sizes for shared variants."""
    merged = pd.merge(
        df1[[snp_col, effect_col]],
        df2[[snp_col, effect_col]],
        on=snp_col,
        suffixes=("_1", "_2"),
    )

    if len(merged) < 3:
        return {"r": float("nan"), "pvalue": 1.0, "n": len(merged)}

    r, p = stats.pearsonr(merged[f"{effect_col}_1"], merged[f"{effect_col}_2"])
    return {"r": r, "pvalue": p, "n": len(merged)}


def cross_trait_matrix(
    datasets: Dict[str, pd.DataFrame],
    method: str = "correlation",
) -> pd.DataFrame:
    """Build a correlation matrix across all disorder pairs.

    Parameters
    ----------
    datasets : dict mapping disorder name -> DataFrame (harmonised)
    method : "correlation" or "concordance"

    Returns
    -------
    pd.DataFrame with disorders as both index and columns
    """
    names = sorted(datasets.keys())
    n = len(names)
    mat = np.eye(n)

    for i, j in itertools.combinations(range(n), 2):
        if method == "correlation":
            result = effect_correlation(datasets[names[i]], datasets[names[j]])
            val = result["r"]
        else:
            result = compute_sign_concordance(datasets[names[i]], datasets[names[j]])
            val = result["concordance"]
        mat[i, j] = val
        mat[j, i] = val

    return pd.DataFrame(mat, index=names, columns=names)
