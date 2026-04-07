"""
LD score utilities.

Provides basic LD-clumping logic for identifying independent loci from
GWAS summary statistics, and helpers for working with LD score regression
output files.

Note: True LD computation requires genotype data (e.g. 1000 Genomes
reference panels).  This module implements *distance-based* clumping as a
lightweight proxy that does not require external genotype files.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from pgc_explorer.config import GENOME_WIDE_SIGNIFICANCE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Locus:
    """A clumped independent locus."""

    lead_snp: str
    chromosome: str
    position: int
    pval: float
    n_support: int = 0
    start: int = 0
    end: int = 0
    genes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "lead_snp": self.lead_snp,
            "chromosome": self.chromosome,
            "position": self.position,
            "pval": self.pval,
            "n_support": self.n_support,
            "start": self.start,
            "end": self.end,
            "genes": self.genes,
        }


# ---------------------------------------------------------------------------
# Distance-based clumping
# ---------------------------------------------------------------------------


def clump_by_distance(
    df: pd.DataFrame,
    pval_col: str = "pval",
    chr_col: str = "chr",
    bp_col: str = "bp",
    snp_col: str = "snp",
    pval_threshold: float = GENOME_WIDE_SIGNIFICANCE,
    clump_kb: int = 500,
) -> List[Locus]:
    """Perform greedy distance-based clumping.

    Algorithm:
    1. Filter to variants with p-value < *pval_threshold*.
    2. Sort by p-value (ascending).
    3. The most significant variant becomes a lead SNP.
    4. All variants within *clump_kb* kb on the same chromosome are assigned
       to that locus and removed from the pool.
    5. Repeat until no variants remain.

    Parameters
    ----------
    df:
        Harmonised GWAS DataFrame.
    pval_threshold:
        Only variants below this p-value are considered.
    clump_kb:
        Clumping window in kilobases.

    Returns
    -------
    List of ``Locus`` objects ordered by p-value.
    """
    required = {pval_col, chr_col, bp_col}
    if not required.issubset(df.columns):
        logger.warning("Missing columns for clumping: %s", required - set(df.columns))
        return []

    sig = df.loc[df[pval_col] < pval_threshold].copy()
    if sig.empty:
        return []

    sig = sig.sort_values(pval_col).reset_index(drop=True)
    window = clump_kb * 1000
    used = np.zeros(len(sig), dtype=bool)
    loci: List[Locus] = []

    for i in range(len(sig)):
        if used[i]:
            continue
        lead = sig.iloc[i]
        lead_chr = str(lead[chr_col])
        lead_bp = int(lead[bp_col])
        lead_pval = float(lead[pval_col])
        lead_snp = str(lead.get(snp_col, f"chr{lead_chr}:{lead_bp}"))

        # Mark support variants.
        same_chr = sig[chr_col].astype(str) == lead_chr
        within = (sig[bp_col] - lead_bp).abs() <= window
        mask = same_chr & within & ~used
        support_idx = sig.index[mask]

        used[support_idx] = True
        positions = sig.loc[support_idx, bp_col]

        loci.append(
            Locus(
                lead_snp=lead_snp,
                chromosome=lead_chr,
                position=lead_bp,
                pval=lead_pval,
                n_support=int(mask.sum()) - 1,  # exclude lead itself
                start=int(positions.min()),
                end=int(positions.max()),
            )
        )

    logger.info("Clumping yielded %d independent loci", len(loci))
    return loci


# ---------------------------------------------------------------------------
# LD score file parser (for LDSC regression output)
# ---------------------------------------------------------------------------


def parse_ldsc_log(path: str) -> Dict[str, float]:
    """Parse key statistics from an LD Score Regression log file.

    Returns a dict with keys like ``h2``, ``h2_se``, ``lambda_gc``,
    ``mean_chi2``, ``intercept``, ``intercept_se``, ``ratio``.
    """
    import re

    results: Dict[str, float] = {}
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("Total Observed scale h2:"):
                    m = re.search(r"h2:\s*([\d.eE+-]+)\s*\(([\d.eE+-]+)\)", line)
                    if m:
                        results["h2"] = float(m.group(1))
                        results["h2_se"] = float(m.group(2))
                elif line.startswith("Lambda GC:"):
                    results["lambda_gc"] = float(line.split(":")[1].strip())
                elif line.startswith("Mean Chi^2:"):
                    results["mean_chi2"] = float(line.split(":")[1].strip())
                elif line.startswith("Intercept:"):
                    m = re.search(r"Intercept:\s*([\d.eE+-]+)\s*\(([\d.eE+-]+)\)", line)
                    if m:
                        results["intercept"] = float(m.group(1))
                        results["intercept_se"] = float(m.group(2))
                elif line.startswith("Ratio"):
                    m = re.search(r"Ratio.*:\s*([\d.eE+-]+)", line)
                    if m:
                        results["ratio"] = float(m.group(1))
    except FileNotFoundError:
        logger.error("LDSC log not found: %s", path)

    return results
