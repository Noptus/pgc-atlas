"""
Dataset listing and metadata endpoints.
"""

from fastapi import APIRouter

from pgc_explorer.config import PGC_DATASETS

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("/")
async def list_datasets():
    """List all 12 PGC psychiatric disorder datasets."""
    return [
        {
            "id": key,
            "hf_id": meta.hf_id,
            "display_name": meta.display_name,
            "approx_rows": meta.approx_rows,
            "description": meta.description,
            "subsets": meta.subsets,
        }
        for key, meta in PGC_DATASETS.items()
    ]


@router.get("/{disorder}")
async def get_dataset(disorder: str):
    """Get metadata for a specific disorder."""
    meta = PGC_DATASETS.get(disorder)
    if meta is None:
        return {"error": f"Unknown disorder: {disorder}"}
    return {
        "id": disorder,
        "hf_id": meta.hf_id,
        "display_name": meta.display_name,
        "approx_rows": meta.approx_rows,
        "description": meta.description,
        "subsets": meta.subsets,
    }


@router.get("/{disorder}/subsets")
async def list_subsets(disorder: str):
    """List available subsets (study cohorts) for a disorder."""
    meta = PGC_DATASETS.get(disorder)
    if meta is None:
        return {"error": f"Unknown disorder: {disorder}"}
    return {"disorder": disorder, "subsets": meta.subsets}
