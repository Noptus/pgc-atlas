"""
Pydantic models for API request/response schemas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DatasetInfo(BaseModel):
    id: str
    hf_id: str
    display_name: str
    approx_rows: str
    description: str
    subsets: List[str]


class VariantRecord(BaseModel):
    snp: Optional[str] = None
    chr: Optional[int] = None
    bp: Optional[int] = None
    a1: Optional[str] = None
    a2: Optional[str] = None
    effect: Optional[float] = None
    se: Optional[float] = None
    pval: Optional[float] = None
    n: Optional[int] = None
    maf: Optional[float] = None
    nearest_gene: Optional[str] = None


class PlotData(BaseModel):
    traces: List[Dict[str, Any]]
    layout: Dict[str, Any]


class SummaryStats(BaseModel):
    disorder: str
    total_variants: int
    significant_variants: int
    top_snps: List[VariantRecord]
    lambda_gc: Optional[float] = None
    mean_chi2: Optional[float] = None


class ExportRequest(BaseModel):
    disorder: str
    subset: Optional[str] = None
    format: str = "csv"
    significant_only: bool = False
    pval_threshold: float = 5e-8
    chromosome: Optional[int] = None
    columns: Optional[List[str]] = None


class RegionQuery(BaseModel):
    chr: int
    start: int
    end: int
    disorder: str
    subset: Optional[str] = None
