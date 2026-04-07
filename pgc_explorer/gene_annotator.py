"""
Gene annotation via the Ensembl REST API.

Provides utilities to annotate GWAS variants with their nearest gene,
overlapping genes, and basic gene metadata (symbol, biotype, description).
Results are cached to disk to minimise repeat HTTP calls.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx
import pandas as pd

from pgc_explorer.config import ENSEMBL_RATE_LIMIT, ENSEMBL_REST_BASE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class GeneInfo:
    """Minimal gene record returned by Ensembl."""

    gene_id: str
    symbol: str
    biotype: str
    description: str
    chromosome: str
    start: int
    end: int
    strand: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gene_id": self.gene_id,
            "symbol": self.symbol,
            "biotype": self.biotype,
            "description": self.description,
            "chromosome": self.chromosome,
            "start": self.start,
            "end": self.end,
            "strand": self.strand,
        }


# ---------------------------------------------------------------------------
# Rate-limited Ensembl client
# ---------------------------------------------------------------------------


class EnsemblClient:
    """Thin async wrapper around the Ensembl REST API with rate limiting."""

    def __init__(
        self,
        base_url: str = ENSEMBL_REST_BASE,
        requests_per_second: int = ENSEMBL_RATE_LIMIT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._min_interval = 1.0 / requests_per_second
        self._last_request: float = 0.0
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=30.0,
            )
        return self._client

    async def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = time.monotonic()

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Issue a rate-limited GET and return the parsed JSON body."""
        await self._throttle()
        client = await self._get_client()
        resp = await client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, json_body: Any) -> Any:
        """Issue a rate-limited POST and return the parsed JSON body."""
        await self._throttle()
        client = await self._get_client()
        resp = await client.post(path, json=json_body)
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# ---------------------------------------------------------------------------
# Annotator
# ---------------------------------------------------------------------------


class GeneAnnotator:
    """Annotate GWAS variants with overlapping / nearest genes from Ensembl.

    Usage::

        annotator = GeneAnnotator()
        df = await annotator.annotate(df)  # adds 'nearest_gene' column
        await annotator.close()
    """

    def __init__(self, client: Optional[EnsemblClient] = None) -> None:
        self.client = client or EnsemblClient()
        self._gene_cache: Dict[str, List[GeneInfo]] = {}

    async def close(self) -> None:
        await self.client.close()

    # ------------------------------------------------------------------
    # Region overlap query
    # ------------------------------------------------------------------

    async def genes_in_region(
        self,
        chromosome: str,
        start: int,
        end: int,
        species: str = "human",
    ) -> List[GeneInfo]:
        """Return protein-coding genes overlapping a region.

        Results are cached by ``chr:start-end``.
        """
        cache_key = f"{chromosome}:{start}-{end}"
        if cache_key in self._gene_cache:
            return self._gene_cache[cache_key]

        path = f"/overlap/region/{species}/{chromosome}:{start}-{end}"
        try:
            data = await self.client.get(path, params={"feature": "gene"})
        except httpx.HTTPStatusError as exc:
            logger.warning("Ensembl error for %s: %s", cache_key, exc)
            return []

        genes: List[GeneInfo] = []
        for entry in data:
            genes.append(
                GeneInfo(
                    gene_id=entry.get("gene_id", entry.get("id", "")),
                    symbol=entry.get("external_name", ""),
                    biotype=entry.get("biotype", ""),
                    description=entry.get("description", ""),
                    chromosome=str(entry.get("seq_region_name", chromosome)),
                    start=int(entry.get("start", 0)),
                    end=int(entry.get("end", 0)),
                    strand=int(entry.get("strand", 0)),
                )
            )

        self._gene_cache[cache_key] = genes
        return genes

    # ------------------------------------------------------------------
    # Nearest gene for a single position
    # ------------------------------------------------------------------

    async def nearest_gene(
        self,
        chromosome: str,
        position: int,
        window: int = 500_000,
    ) -> Optional[GeneInfo]:
        """Return the nearest protein-coding gene within *window* bp."""
        start = max(1, position - window)
        end = position + window
        genes = await self.genes_in_region(chromosome, start, end)

        protein_coding = [g for g in genes if g.biotype == "protein_coding"]
        if not protein_coding:
            protein_coding = genes  # fall back to all biotypes

        if not protein_coding:
            return None

        def _distance(g: GeneInfo) -> int:
            if g.start <= position <= g.end:
                return 0
            return min(abs(position - g.start), abs(position - g.end))

        return min(protein_coding, key=_distance)

    # ------------------------------------------------------------------
    # Batch annotation on a DataFrame
    # ------------------------------------------------------------------

    async def annotate(
        self,
        df: pd.DataFrame,
        chr_col: str = "chr",
        bp_col: str = "bp",
        window: int = 500_000,
        max_queries: int = 200,
    ) -> pd.DataFrame:
        """Add ``nearest_gene`` and ``nearest_gene_id`` columns to *df*.

        Only the first *max_queries* unique loci (by 1 Mb windows) are
        queried to respect rate limits.  The DataFrame is returned with the
        new columns; unmatched rows get ``None``.
        """
        df = df.copy()
        df["nearest_gene"] = None
        df["nearest_gene_id"] = None

        if chr_col not in df.columns or bp_col not in df.columns:
            logger.warning("Cannot annotate: missing %s or %s columns", chr_col, bp_col)
            return df

        # Deduplicate queries by rounding to Mb windows.
        seen: set[str] = set()
        queries: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            chrom = str(row[chr_col])
            bp = row[bp_col]
            if pd.isna(bp):
                continue
            bp_int = int(bp)
            bucket = f"{chrom}:{bp_int // 1_000_000}"
            if bucket in seen:
                continue
            seen.add(bucket)
            queries.append({"chr": chrom, "bp": bp_int})
            if len(queries) >= max_queries:
                break

        # Execute queries.
        gene_map: Dict[str, GeneInfo] = {}
        for q in queries:
            gene = await self.nearest_gene(q["chr"], q["bp"], window=window)
            if gene:
                gene_map[f"{q['chr']}:{q['bp']}"] = gene

        # Map back to DataFrame rows.
        for idx, row in df.iterrows():
            chrom = str(row[chr_col])
            bp = row[bp_col]
            if pd.isna(bp):
                continue
            key = f"{chrom}:{int(bp)}"
            gene = gene_map.get(key)
            if gene:
                df.at[idx, "nearest_gene"] = gene.symbol
                df.at[idx, "nearest_gene_id"] = gene.gene_id

        return df
