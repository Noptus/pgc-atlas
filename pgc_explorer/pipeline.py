"""
Data augmentation pipeline for enriching GWAS summary statistics.

Orchestrates: column harmonisation -> significance filtering -> gene annotation
-> LD clumping -> cross-trait correlation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

import pandas as pd

from .config import SIGNIFICANCE_THRESHOLD, SUGGESTIVE_THRESHOLD
from .gene_annotator import EnsemblAnnotator
from .ld_scores import ld_clump

logger = logging.getLogger(__name__)


@dataclass
class PipelineStep:
    """A single augmentation step."""
    name: str
    fn: Callable[[pd.DataFrame], pd.DataFrame]
    description: str = ""
    enabled: bool = True


class DataAugmentationPipeline:
    """Orchestrates sequential enrichment of GWAS summary statistics.

    Usage::

        pipe = DataAugmentationPipeline()
        pipe.add_step("filter_significant", filter_significant)
        pipe.add_step("annotate_genes", annotate_with_genes)
        enriched = pipe.run(raw_df)
    """

    def __init__(self) -> None:
        self.steps: List[PipelineStep] = []
        self._log: List[dict] = []

    def add_step(
        self,
        name: str,
        fn: Callable[[pd.DataFrame], pd.DataFrame],
        description: str = "",
        enabled: bool = True,
    ) -> "DataAugmentationPipeline":
        self.steps.append(PipelineStep(name=name, fn=fn, description=description, enabled=enabled))
        return self

    def run(self, df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
        """Execute all enabled steps in order."""
        result = df.copy()
        for step in self.steps:
            if not step.enabled:
                continue
            n_before = len(result)
            if verbose:
                logger.info("Running step: %s (%s)", step.name, step.description)
            result = step.fn(result)
            self._log.append({
                "step": step.name,
                "rows_before": n_before,
                "rows_after": len(result),
            })
        return result

    @property
    def log(self) -> List[dict]:
        return list(self._log)


def default_pipeline(annotator: Optional[EnsemblAnnotator] = None) -> DataAugmentationPipeline:
    """Create a pipeline with standard enrichment steps."""
    pipe = DataAugmentationPipeline()

    pipe.add_step(
        "filter_significant",
        lambda df: df[df["pval"] <= SUGGESTIVE_THRESHOLD] if "pval" in df.columns else df,
        description=f"Keep variants with p <= {SUGGESTIVE_THRESHOLD}",
    )

    pipe.add_step(
        "ld_clump",
        lambda df: ld_clump(df, p_col="pval", chr_col="chr", pos_col="bp"),
        description="LD clumping (distance-based, 500 kb window)",
    )

    if annotator is None:
        annotator = EnsemblAnnotator()

    def _annotate(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        genes = annotator.annotate_variants(
            list(zip(df["chr"], df["bp"])) if "chr" in df.columns else []
        )
        df = df.copy()
        df["nearest_gene"] = [g.symbol if g else None for g in genes]
        df["gene_distance"] = [g.distance if g else None for g in genes]
        return df

    pipe.add_step(
        "annotate_genes",
        _annotate,
        description="Annotate nearest gene via Ensembl REST",
    )

    return pipe
