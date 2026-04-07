"""
Configuration constants for PGC GWAS Explorer.

Central registry of the 12 PGC HuggingFace datasets, column-name
mappings used for harmonisation, and tuneable defaults (cache sizes,
significance thresholds, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Dataset registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DatasetMeta:
    """Metadata for a single PGC HuggingFace dataset."""

    hf_id: str
    disorder: str
    display_name: str
    approx_rows: str
    description: str
    subsets: List[str] = field(default_factory=list)


PGC_DATASETS: Dict[str, DatasetMeta] = {
    "adhd": DatasetMeta(
        hf_id="OpenMed/pgc-adhd",
        disorder="adhd",
        display_name="ADHD",
        approx_rows="31.2M",
        description="Attention-Deficit/Hyperactivity Disorder GWAS summary statistics",
        subsets=["adhd2010", "adhd2019", "adhd2023"],
    ),
    "anxiety": DatasetMeta(
        hf_id="OpenMed/pgc-anxiety",
        disorder="anxiety",
        display_name="Anxiety Disorders",
        approx_rows="27.5M",
        description="Anxiety Disorders GWAS summary statistics",
        subsets=[],
    ),
    "autism": DatasetMeta(
        hf_id="OpenMed/pgc-autism",
        disorder="autism",
        display_name="Autism Spectrum Disorder",
        approx_rows="18.6M",
        description="Autism Spectrum Disorder GWAS summary statistics",
        subsets=[],
    ),
    "bipolar": DatasetMeta(
        hf_id="OpenMed/pgc-bipolar",
        disorder="bipolar",
        display_name="Bipolar Disorder",
        approx_rows="74.4M",
        description="Bipolar Disorder GWAS summary statistics",
        subsets=[],
    ),
    "cross-disorder": DatasetMeta(
        hf_id="OpenMed/pgc-cross-disorder",
        disorder="cross-disorder",
        display_name="Cross-Disorder",
        approx_rows="63.3M",
        description="Cross-Disorder GWAS summary statistics",
        subsets=[],
    ),
    "eating-disorders": DatasetMeta(
        hf_id="OpenMed/pgc-eating-disorders",
        disorder="eating-disorders",
        display_name="Eating Disorders",
        approx_rows="10.6M",
        description="Eating Disorders GWAS summary statistics",
        subsets=[],
    ),
    "mdd": DatasetMeta(
        hf_id="OpenMed/pgc-mdd",
        disorder="mdd",
        display_name="Major Depressive Disorder",
        approx_rows="179M",
        description="Major Depressive Disorder GWAS summary statistics",
        subsets=[],
    ),
    "ocd-tourette": DatasetMeta(
        hf_id="OpenMed/pgc-ocd-tourette",
        disorder="ocd-tourette",
        display_name="OCD & Tourette Syndrome",
        approx_rows="36.5M",
        description="OCD and Tourette Syndrome GWAS summary statistics",
        subsets=[],
    ),
    "other": DatasetMeta(
        hf_id="OpenMed/pgc-other",
        disorder="other",
        display_name="Other Phenotypes",
        approx_rows="40.9M",
        description="Other psychiatric phenotypes GWAS summary statistics",
        subsets=[],
    ),
    "ptsd": DatasetMeta(
        hf_id="OpenMed/pgc-ptsd",
        disorder="ptsd",
        display_name="PTSD",
        approx_rows="128M",
        description="Post-Traumatic Stress Disorder GWAS summary statistics",
        subsets=[],
    ),
    "schizophrenia": DatasetMeta(
        hf_id="OpenMed/pgc-schizophrenia",
        disorder="schizophrenia",
        display_name="Schizophrenia",
        approx_rows="91.4M",
        description="Schizophrenia GWAS summary statistics",
        subsets=[],
    ),
    "substance-use": DatasetMeta(
        hf_id="OpenMed/pgc-substance-use",
        disorder="substance-use",
        display_name="Substance Use Disorders",
        approx_rows="214M",
        description="Substance Use Disorders GWAS summary statistics",
        subsets=[],
    ),
}

# ---------------------------------------------------------------------------
# Column harmonisation maps
# ---------------------------------------------------------------------------

# Each key is the *canonical* column name; values are known aliases found
# across the 12 datasets (case-insensitive matching is applied at runtime).

COLUMN_MAP: Dict[str, List[str]] = {
    "snp": ["snpid", "snp", "rsid", "rs", "markername", "marker", "variant_id", "id"],
    "chr": [
        "chromosome", "chr", "hg18chr", "hg19chr", "chrom", "#chrom",
        "chr_id", "chrom_id",
    ],
    "bp": ["bp", "pos", "position", "base_pair_location", "bpos", "bp_hg19", "bp_hg18"],
    "a1": ["a1", "allele1", "effect_allele", "alt", "ref", "a1_effect"],
    "a2": ["a2", "allele2", "other_allele", "ref", "alt", "a2_other"],
    "effect": [
        "beta", "or", "odds_ratio", "log_or", "zscore", "z", "effect",
        "effect_size", "b",
    ],
    "se": ["se", "stderr", "standard_error", "se_beta"],
    "pval": [
        "pval", "p", "p_value", "pvalue", "p-value", "p.value",
        "p_val",
    ],
    "n": ["n", "neff", "n_eff", "n_total", "n_samples", "samplesize", "totaln", "nstudies"],
    "maf": ["maf", "freq", "frq", "eaf", "effect_allele_frequency", "a1freq"],
}

# Canonical column order for harmonised DataFrames.
CANONICAL_COLUMNS = ["snp", "chr", "bp", "a1", "a2", "effect", "se", "pval", "n", "maf"]

# ---------------------------------------------------------------------------
# Significance thresholds
# ---------------------------------------------------------------------------

GENOME_WIDE_SIGNIFICANCE: float = 5e-8
SUGGESTIVE_SIGNIFICANCE: float = 1e-5

# ---------------------------------------------------------------------------
# Paths & caching
# ---------------------------------------------------------------------------

CACHE_DIR: Path = Path.home() / ".cache" / "pgc_explorer"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DISK_CACHE_SIZE_LIMIT: int = 4 * 1024**3  # 4 GiB

# ---------------------------------------------------------------------------
# Ensembl REST API
# ---------------------------------------------------------------------------

ENSEMBL_REST_BASE: str = "https://rest.ensembl.org"
ENSEMBL_RATE_LIMIT: int = 15  # requests per second

# ---------------------------------------------------------------------------
# Chromosome metadata (GRCh37 lengths for plotting)
# ---------------------------------------------------------------------------

CHR_LENGTHS_GRCH37: Dict[str, int] = {
    "1": 249250621, "2": 243199373, "3": 198022430,
    "4": 191154276, "5": 180915260, "6": 171115067,
    "7": 159138663, "8": 146364022, "9": 141213431,
    "10": 135534747, "11": 135006516, "12": 133851895,
    "13": 115169878, "14": 107349540, "15": 102531392,
    "16": 90354753, "17": 81195210, "18": 78077248,
    "19": 59128983, "20": 63025520, "21": 48129895,
    "22": 51304566,
}

# Ordered chromosome labels for plotting
CHR_ORDER: List[str] = [str(i) for i in range(1, 23)]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_dataset_meta(disorder: str) -> Optional[DatasetMeta]:
    """Return metadata for a disorder key, or ``None`` if unknown."""
    return PGC_DATASETS.get(disorder)


def list_disorders() -> List[str]:
    """Return a sorted list of available disorder keys."""
    return sorted(PGC_DATASETS.keys())


# ---------------------------------------------------------------------------
# Convenience aliases used by plot modules
# ---------------------------------------------------------------------------

SIGNIFICANCE_THRESHOLD: float = GENOME_WIDE_SIGNIFICANCE
SUGGESTIVE_THRESHOLD: float = SUGGESTIVE_SIGNIFICANCE
CHROMOSOME_LENGTHS: Dict[int, int] = {int(k): v for k, v in CHR_LENGTHS_GRCH37.items()}
DISORDERS = PGC_DATASETS
