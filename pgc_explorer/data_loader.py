"""
HuggingFace dataset loader with streaming support and column harmonisation.

Handles the diversity of column names found across the 12 PGC datasets by
normalising them to a canonical schema (see ``pgc_explorer.config``).

Large datasets are streamed via the HuggingFace ``datasets`` library so that
memory footprint stays bounded; only the requested slice (chromosome, region,
or top-N by p-value) is materialised as a pandas DataFrame.
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from datasets import load_dataset, Dataset, IterableDataset

from pgc_explorer.config import (
    CACHE_DIR,
    CANONICAL_COLUMNS,
    COLUMN_MAP,
    DISK_CACHE_SIZE_LIMIT,
    PGC_DATASETS,
    DatasetMeta,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column harmonisation
# ---------------------------------------------------------------------------


def _build_reverse_map() -> Dict[str, str]:
    """Create a lowercased alias -> canonical name lookup dictionary."""
    rev: Dict[str, str] = {}
    for canonical, aliases in COLUMN_MAP.items():
        for alias in aliases:
            key = alias.strip().lower()
            # First mapping wins (most common alias listed first).
            if key not in rev:
                rev[key] = canonical
    return rev


_REVERSE_COLUMN_MAP: Dict[str, str] = _build_reverse_map()


def harmonise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns in *df* to the canonical schema.

    Unknown columns are kept as-is.  If multiple source columns map to the
    same canonical name the first match (left-to-right) wins.

    Returns a **new** DataFrame — the original is not mutated.
    """
    rename: Dict[str, str] = {}
    seen_canonical: set[str] = set()
    for col in df.columns:
        canonical = _REVERSE_COLUMN_MAP.get(col.strip().lower())
        if canonical and canonical not in seen_canonical:
            rename[col] = canonical
            seen_canonical.add(canonical)

    df = df.rename(columns=rename)

    # Normalise chromosome column to string without "chr" prefix.
    if "chr" in df.columns:
        df["chr"] = (
            df["chr"]
            .astype(str)
            .str.strip()
            .str.replace(r"^chr", "", regex=True)
            .str.upper()
            .str.replace("X", "23")
            .str.replace("Y", "24")
        )

    # Coerce numeric columns.
    for col in ("bp", "effect", "se", "pval", "n", "maf"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# Parquet cache helpers
# ---------------------------------------------------------------------------


def _cache_key(disorder: str, subset: Optional[str], extra: str = "") -> str:
    raw = f"{disorder}:{subset or 'default'}:{extra}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _parquet_path(disorder: str, subset: Optional[str], tag: str = "") -> Path:
    key = _cache_key(disorder, subset, tag)
    return CACHE_DIR / f"{disorder}_{key}.parquet"


# ---------------------------------------------------------------------------
# Streaming loader
# ---------------------------------------------------------------------------


class PGCDataLoader:
    """Load PGC datasets from HuggingFace with streaming & caching."""

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, pd.DataFrame] = {}

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @staticmethod
    def available_disorders() -> List[str]:
        """Return list of registered disorder keys."""
        return sorted(PGC_DATASETS.keys())

    @staticmethod
    def dataset_meta(disorder: str) -> DatasetMeta:
        """Return metadata for *disorder* or raise ``KeyError``."""
        if disorder not in PGC_DATASETS:
            raise KeyError(f"Unknown disorder: {disorder!r}. "
                           f"Available: {sorted(PGC_DATASETS)}")
        return PGC_DATASETS[disorder]

    # ------------------------------------------------------------------
    # Core streaming load
    # ------------------------------------------------------------------

    def stream_dataset(
        self,
        disorder: str,
        subset: Optional[str] = None,
        split: str = "train",
    ) -> IterableDataset:
        """Return a HuggingFace ``IterableDataset`` (streamed, lazy).

        Parameters
        ----------
        disorder:
            Key from ``PGC_DATASETS`` (e.g. ``"schizophrenia"``).
        subset:
            Optional configuration / subset name recognised by the HF
            dataset (e.g. ``"adhd2019"`` for the ADHD dataset).
        split:
            HF split — almost always ``"train"`` for summary-stat repos.
        """
        meta = self.dataset_meta(disorder)
        logger.info("Streaming %s (subset=%s) …", meta.hf_id, subset)
        ds = load_dataset(
            meta.hf_id,
            name=subset,
            split=split,
            streaming=True,
        )
        return ds

    # ------------------------------------------------------------------
    # Materialised (pandas) load with caching
    # ------------------------------------------------------------------

    def load_region(
        self,
        disorder: str,
        chromosome: Union[str, int],
        start: Optional[int] = None,
        end: Optional[int] = None,
        subset: Optional[str] = None,
        limit: int = 500_000,
    ) -> pd.DataFrame:
        """Stream and materialise variants in a genomic region.

        Parameters
        ----------
        disorder:
            Key into ``PGC_DATASETS``.
        chromosome:
            Chromosome number (e.g. ``6`` or ``"6"``).
        start, end:
            Optional base-pair range (inclusive).
        subset:
            Optional HF subset name.
        limit:
            Safety cap on rows materialised.

        Returns a harmonised pandas DataFrame.
        """
        chrom_str = str(chromosome).replace("chr", "").upper()

        tag = f"chr{chrom_str}_{start or 0}_{end or 0}"
        cache_path = _parquet_path(disorder, subset, tag)

        if cache_path.exists():
            logger.info("Cache hit: %s", cache_path)
            return pd.read_parquet(cache_path)

        ds = self.stream_dataset(disorder, subset=subset)
        rows: list[dict[str, Any]] = []
        for record in ds:
            row = dict(record)
            # Quick pre-harmonise check for chromosome to filter early.
            chr_val = self._extract_chr(row)
            if chr_val != chrom_str:
                continue
            # Position filter
            bp_val = self._extract_bp(row)
            if bp_val is not None:
                if start is not None and bp_val < start:
                    continue
                if end is not None and bp_val > end:
                    continue
            rows.append(row)
            if len(rows) >= limit:
                break

        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(columns=CANONICAL_COLUMNS)
        df = harmonise_columns(df)

        # Persist to cache.
        try:
            df.to_parquet(cache_path, index=False)
        except Exception:
            logger.warning("Failed to write cache file %s", cache_path, exc_info=True)

        return df

    def load_top_hits(
        self,
        disorder: str,
        subset: Optional[str] = None,
        pval_threshold: float = 5e-8,
        limit: int = 100_000,
    ) -> pd.DataFrame:
        """Stream and return variants below *pval_threshold*.

        Useful for Manhattan plot generation where only significant hits need
        to be displayed at full resolution.
        """
        tag = f"top_{pval_threshold}"
        cache_path = _parquet_path(disorder, subset, tag)
        if cache_path.exists():
            return pd.read_parquet(cache_path)

        ds = self.stream_dataset(disorder, subset=subset)
        rows: list[dict[str, Any]] = []
        for record in ds:
            row = dict(record)
            pval = self._extract_pval(row)
            if pval is not None and pval < pval_threshold:
                rows.append(row)
            if len(rows) >= limit:
                break

        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(columns=CANONICAL_COLUMNS)
        df = harmonise_columns(df)

        try:
            df.to_parquet(cache_path, index=False)
        except Exception:
            logger.warning("Failed to write cache file %s", cache_path, exc_info=True)

        return df

    def search_snp(
        self,
        snp_id: str,
        disorder: Optional[str] = None,
        subset: Optional[str] = None,
        limit: int = 500,
    ) -> pd.DataFrame:
        """Search for a specific SNP (e.g. ``rs1234``) across one or all disorders.

        If *disorder* is ``None`` the search iterates over every dataset
        (streaming) which can be slow — prefer specifying the disorder.
        """
        snp_id_lower = snp_id.strip().lower()
        disorders = [disorder] if disorder else sorted(PGC_DATASETS.keys())

        all_rows: list[dict[str, Any]] = []
        for d in disorders:
            ds = self.stream_dataset(d, subset=subset)
            for record in ds:
                row = dict(record)
                snp_val = self._extract_snp(row)
                if snp_val and snp_val.lower() == snp_id_lower:
                    row["_disorder"] = d
                    all_rows.append(row)
                    if len(all_rows) >= limit:
                        break
            if len(all_rows) >= limit:
                break

        df = pd.DataFrame(all_rows)
        if df.empty:
            return pd.DataFrame(columns=[*CANONICAL_COLUMNS, "_disorder"])
        return harmonise_columns(df)

    def load_sampled(
        self,
        disorder: str,
        subset: Optional[str] = None,
        n_samples: int = 200_000,
        seed: int = 42,
    ) -> pd.DataFrame:
        """Load a random-ish sample of *n_samples* rows for overview plots.

        Because HF streaming does not support true random sampling we take
        every k-th row for a roughly uniform sample.
        """
        tag = f"sampled_{n_samples}_{seed}"
        cache_path = _parquet_path(disorder, subset, tag)
        if cache_path.exists():
            return pd.read_parquet(cache_path)

        ds = self.stream_dataset(disorder, subset=subset)
        rows: list[dict[str, Any]] = []
        rng = np.random.default_rng(seed)
        # Accept each row with probability n_samples / estimated_total.
        # We use a generous cap; if the dataset is smaller we just take all.
        accept_prob = min(1.0, n_samples / 1_000_000)
        for record in ds:
            if rng.random() < accept_prob:
                rows.append(dict(record))
            if len(rows) >= n_samples:
                break

        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(columns=CANONICAL_COLUMNS)
        df = harmonise_columns(df)

        try:
            df.to_parquet(cache_path, index=False)
        except Exception:
            logger.warning("Failed to write cache file %s", cache_path, exc_info=True)

        return df

    # ------------------------------------------------------------------
    # Private extraction helpers (work on raw dicts before harmonisation)
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_chr(row: Dict[str, Any]) -> Optional[str]:
        for key in ("chromosome", "chr", "hg18chr", "hg19chr", "CHR", "chrom", "#chrom"):
            val = row.get(key)
            if val is not None:
                return str(val).replace("chr", "").strip().upper()
        return None

    @staticmethod
    def _extract_bp(row: Dict[str, Any]) -> Optional[int]:
        for key in ("bp", "BP", "pos", "position", "base_pair_location", "bpos"):
            val = row.get(key)
            if val is not None:
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return None
        return None

    @staticmethod
    def _extract_pval(row: Dict[str, Any]) -> Optional[float]:
        for key in ("pval", "P", "p", "p_value", "pvalue", "p-value"):
            val = row.get(key)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None
        return None

    @staticmethod
    def _extract_snp(row: Dict[str, Any]) -> Optional[str]:
        for key in ("snpid", "SNP", "snp", "rsid", "RSID", "markername", "variant_id"):
            val = row.get(key)
            if val is not None:
                return str(val).strip()
        return None
