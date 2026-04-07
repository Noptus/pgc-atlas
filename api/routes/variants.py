"""
Variant search and filtering endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Query

from pgc_explorer.config import PGC_DATASETS
from pgc_explorer.data_loader import PGCDataLoader

router = APIRouter(prefix="/api/variants", tags=["variants"])

_loader = PGCDataLoader()


@router.get("/search")
async def search_variant(
    snp: str = Query(..., description="SNP rsID to search for"),
    disorder: Optional[str] = Query(None, description="Limit search to this disorder"),
):
    """Search for a specific variant across datasets."""
    disorders = [disorder] if disorder else list(PGC_DATASETS.keys())
    results = []

    for d in disorders:
        try:
            df = _loader.search_snp(d, snp)
            if df is not None and not df.empty:
                results.extend(df.assign(disorder=d).to_dict("records"))
        except Exception:
            continue

    return {"query": snp, "results": results, "count": len(results)}


@router.get("/region")
async def query_region(
    chr: int = Query(..., ge=1, le=22),
    start: int = Query(..., ge=0),
    end: int = Query(...),
    disorder: str = Query(...),
    subset: Optional[str] = None,
    limit: int = Query(1000, le=10000),
):
    """Query variants in a genomic region."""
    try:
        df = _loader.load_region(disorder, chr, start, end, subset=subset)
        if df is not None:
            df = df.head(limit)
            return {"variants": df.to_dict("records"), "count": len(df)}
    except Exception as e:
        return {"error": str(e)}

    return {"variants": [], "count": 0}
