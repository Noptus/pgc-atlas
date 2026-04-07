"""
Plot data endpoints — return Plotly-ready JSON for frontend rendering.
"""

from typing import Optional

from fastapi import APIRouter, Query

from pgc_explorer.data_loader import PGCDataLoader
from pgc_explorer.manhattan import prepare_manhattan_data
from pgc_explorer.qq_plot import prepare_qq_data
from pgc_explorer.miami import prepare_miami_data
from pgc_explorer.volcano import prepare_volcano_data

router = APIRouter(prefix="/api/plots", tags=["plots"])

_loader = PGCDataLoader()


@router.get("/manhattan/{disorder}")
async def manhattan_plot(
    disorder: str,
    subset: Optional[str] = None,
    max_points: int = Query(100000, le=500000),
):
    """Generate Manhattan plot data for a disorder."""
    df = _loader.load_top_hits(disorder, n=max_points, subset=subset)
    if df is None or df.empty:
        return {"traces": [], "layout": {}}
    return prepare_manhattan_data(df, max_points=max_points)


@router.get("/qq/{disorder}")
async def qq_plot(
    disorder: str,
    subset: Optional[str] = None,
    max_points: int = Query(50000, le=200000),
):
    """Generate QQ plot data."""
    df = _loader.load_top_hits(disorder, n=max_points, subset=subset)
    if df is None or df.empty:
        return {"traces": [], "layout": {}}
    return prepare_qq_data(df, max_points=max_points)


@router.get("/miami")
async def miami_plot(
    disorder1: str = Query(...),
    disorder2: str = Query(...),
    subset1: Optional[str] = None,
    subset2: Optional[str] = None,
    max_points: int = Query(80000, le=300000),
):
    """Generate Miami plot comparing two disorders."""
    df1 = _loader.load_top_hits(disorder1, n=max_points, subset=subset1)
    df2 = _loader.load_top_hits(disorder2, n=max_points, subset=subset2)

    if df1 is None or df2 is None:
        return {"traces": [], "layout": {}}

    from pgc_explorer.config import PGC_DATASETS
    label1 = PGC_DATASETS.get(disorder1, type("", (), {"display_name": disorder1})).display_name
    label2 = PGC_DATASETS.get(disorder2, type("", (), {"display_name": disorder2})).display_name

    return prepare_miami_data(df1, df2, label_top=label1, label_bottom=label2)


@router.get("/volcano/{disorder}")
async def volcano_plot(
    disorder: str,
    subset: Optional[str] = None,
    max_points: int = Query(60000, le=200000),
):
    """Generate volcano plot data."""
    df = _loader.load_top_hits(disorder, n=max_points, subset=subset)
    if df is None or df.empty:
        return {"traces": [], "layout": {}}
    return prepare_volcano_data(df, max_points=max_points)
