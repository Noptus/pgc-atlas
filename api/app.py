"""
FastAPI application — PGC GWAS Explorer API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import datasets, variants, plots, export

app = FastAPI(
    title="PGC GWAS Explorer API",
    description=(
        "Interactive API for exploring ~1 billion rows of Psychiatric Genomics "
        "Consortium GWAS summary statistics across 12 psychiatric disorders."
    ),
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(variants.router)
app.include_router(plots.router)
app.include_router(export.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "pgc-gwas-explorer"}


@app.get("/api/stats/overview")
async def overview():
    from pgc_explorer.config import PGC_DATASETS
    total = sum(
        float(m.approx_rows.rstrip("M")) * 1e6
        for m in PGC_DATASETS.values()
    )
    return {
        "total_variants": f"~{total/1e9:.1f}B",
        "disorders": len(PGC_DATASETS),
        "datasets": [
            {"id": k, "name": m.display_name, "rows": m.approx_rows}
            for k, m in PGC_DATASETS.items()
        ],
    }
