"""
Data export endpoint.
"""

from fastapi import APIRouter
from fastapi.responses import Response

from api.models import ExportRequest
from pgc_explorer.data_loader import PGCDataLoader
from pgc_explorer.export import export_data

router = APIRouter(prefix="/api/export", tags=["export"])

_loader = PGCDataLoader()

MEDIA_TYPES = {
    "csv": "text/csv",
    "tsv": "text/tab-separated-values",
    "json": "application/json",
    "parquet": "application/octet-stream",
    "bed": "text/plain",
}


@router.post("/")
async def export_variants(req: ExportRequest):
    """Export filtered GWAS data in the requested format."""
    df = _loader.load_region(
        req.disorder,
        req.chromosome or 1,
        0,
        300_000_000,
        subset=req.subset,
    )

    if df is None or df.empty:
        return Response(content=b"", media_type="text/plain")

    data = export_data(
        df,
        fmt=req.format,
        significant_only=req.significant_only,
        pval_threshold=req.pval_threshold,
        columns=req.columns,
    )

    ext = req.format
    return Response(
        content=data,
        media_type=MEDIA_TYPES.get(ext, "application/octet-stream"),
        headers={
            "Content-Disposition": f"attachment; filename=pgc_{req.disorder}.{ext}"
        },
    )
