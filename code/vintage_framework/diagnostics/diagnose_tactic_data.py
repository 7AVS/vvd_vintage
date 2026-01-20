"""
Tactic Data Diagnostic Script
=============================

This script investigates the tactic data to understand:
- What fields are available
- What values exist for segmentation fields (RPT_GRP_CD, TACTIC_CELL_CD, etc.)
- Distribution of clients across dimensions
- Data quality issues

Run this in Jupyter to explore the data before building vintage curves.

Usage:
    from vintage_framework.diagnostics.diagnose_tactic_data import run_tactic_diagnostics
    results = run_tactic_diagnostics(spark)
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from typing import Dict, Any, List
import pandas as pd


def run_tactic_diagnostics(
    spark: SparkSession,
    tactic_path: str = "/user/427966379/tactic.parquet",
    mnes: List[str] = None
) -> Dict[str, Any]:
    """
    Run comprehensive diagnostics on tactic data.

    Args:
        spark: Active SparkSession
        tactic_path: Path to tactic parquet file
        mnes: Optional list of MNEs to focus on (default: all VVD)

    Returns:
        Dictionary with diagnostic results
    """
    print("="*60)
    print("TACTIC DATA DIAGNOSTICS")
    print("="*60)

    # Load data
    print(f"\n[1] Loading tactic data from: {tactic_path}")
    tactic = spark.read.parquet(tactic_path)

    # Default MNEs if not specified
    if mnes is None:
        mnes = ["VCN", "VDA", "VDT", "VUI", "VUT", "VAW"]

    results = {
        "total_records": 0,
        "schema": None,
        "mne_summary": None,
        "segmentation_fields": {},
        "data_quality": {}
    }

    # Schema
    print("\n[2] Schema:")
    print("-" * 40)
    tactic.printSchema()
    results["schema"] = tactic.schema.simpleString()

    # Total records
    total = tactic.count()
    results["total_records"] = total
    print(f"\n[3] Total records: {total:,}")

    # Filter to VVD campaigns
    tactic_vvd = tactic.filter(F.col("MNE").isin(mnes))
    vvd_count = tactic_vvd.count()
    print(f"    VVD records ({', '.join(mnes)}): {vvd_count:,}")

    # MNE Summary
    print("\n[4] MNE Distribution:")
    print("-" * 40)
    mne_summary = tactic_vvd.groupBy("MNE").agg(
        F.count("*").alias("total_records"),
        F.countDistinct("CLNT_NO").alias("unique_clients"),
        F.countDistinct("TACTIC_ID").alias("unique_tactics"),
        F.min("TREATMT_STRT_DT").alias("earliest_date"),
        F.max("TREATMT_STRT_DT").alias("latest_date")
    ).orderBy("MNE")
    mne_summary.show(truncate=False)
    results["mne_summary"] = mne_summary.toPandas()

    # Segmentation Fields Investigation
    print("\n[5] Segmentation Fields:")
    print("-" * 40)

    seg_fields = ["TST_GRP_CD", "RPT_GRP_CD", "TACTIC_CELL_CD", "STRTGY_SRC_CD", "TRGT_TYP_CD", "CHANNEL"]

    for field in seg_fields:
        if field in tactic_vvd.columns:
            print(f"\n--- {field} ---")
            field_summary = tactic_vvd.groupBy("MNE", field).agg(
                F.count("*").alias("record_count"),
                F.countDistinct("CLNT_NO").alias("unique_clients")
            ).orderBy("MNE", field)
            field_summary.show(50, truncate=False)

            results["segmentation_fields"][field] = field_summary.toPandas()
        else:
            print(f"\n--- {field} --- NOT FOUND IN DATA")

    # Data Quality Checks
    print("\n[6] Data Quality Checks:")
    print("-" * 40)

    # Check for nulls in key fields
    key_fields = ["CLNT_NO", "TREATMT_STRT_DT", "TREATMT_END_DT", "TST_GRP_CD", "MNE"]
    null_counts = {}

    for field in key_fields:
        if field in tactic_vvd.columns:
            null_count = tactic_vvd.filter(F.col(field).isNull()).count()
            null_counts[field] = null_count
            print(f"    {field}: {null_count:,} nulls ({null_count/vvd_count*100:.2f}%)")

    results["data_quality"]["null_counts"] = null_counts

    # Check measurement window distribution
    print("\n[7] Measurement Window Distribution:")
    print("-" * 40)
    window_dist = tactic_vvd.withColumn(
        "WINDOW_DAYS",
        F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT"))
    ).groupBy("MNE", "WINDOW_DAYS").agg(
        F.count("*").alias("count")
    ).orderBy("MNE", "WINDOW_DAYS")
    window_dist.show(50, truncate=False)
    results["data_quality"]["window_distribution"] = window_dist.toPandas()

    # Check test group distribution by MNE
    print("\n[8] Test Group Distribution by MNE:")
    print("-" * 40)
    test_group_dist = tactic_vvd.groupBy("MNE", "TST_GRP_CD").agg(
        F.count("*").alias("records"),
        F.countDistinct("CLNT_NO").alias("unique_clients")
    ).orderBy("MNE", "TST_GRP_CD")
    test_group_dist.show(50, truncate=False)
    results["data_quality"]["test_group_distribution"] = test_group_dist.toPandas()

    # Year distribution
    print("\n[9] Year Distribution:")
    print("-" * 40)
    year_dist = tactic_vvd.withColumn(
        "YEAR",
        F.year(F.col("TREATMT_STRT_DT"))
    ).groupBy("MNE", "YEAR").agg(
        F.count("*").alias("records")
    ).orderBy("MNE", "YEAR")
    year_dist.show(truncate=False)
    results["data_quality"]["year_distribution"] = year_dist.toPandas()

    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60)

    return results


def investigate_segment_codes(
    spark: SparkSession,
    tactic_path: str = "/user/427966379/tactic.parquet",
    mne: str = "VCN"
) -> DataFrame:
    """
    Deep dive into segment codes for a specific campaign.

    Use this to understand what RPT_GRP_CD values mean.

    Args:
        spark: Active SparkSession
        tactic_path: Path to tactic parquet
        mne: Campaign to investigate

    Returns:
        DataFrame with segment analysis
    """
    print(f"\n{'='*60}")
    print(f"SEGMENT CODE INVESTIGATION: {mne}")
    print(f"{'='*60}")

    tactic = spark.read.parquet(tactic_path)
    tactic_mne = tactic.filter(F.col("MNE") == mne)

    # Cross-tab: RPT_GRP_CD vs TST_GRP_CD
    print("\n[1] RPT_GRP_CD x TST_GRP_CD Cross-tabulation:")
    print("-" * 40)

    if "RPT_GRP_CD" in tactic_mne.columns:
        crosstab = tactic_mne.groupBy("RPT_GRP_CD", "TST_GRP_CD").agg(
            F.count("*").alias("count"),
            F.countDistinct("CLNT_NO").alias("unique_clients")
        ).orderBy("RPT_GRP_CD", "TST_GRP_CD")
        crosstab.show(100, truncate=False)
    else:
        print("RPT_GRP_CD not available")

    # Cross-tab: TACTIC_CELL_CD vs TST_GRP_CD
    print("\n[2] TACTIC_CELL_CD x TST_GRP_CD Cross-tabulation:")
    print("-" * 40)

    if "TACTIC_CELL_CD" in tactic_mne.columns:
        crosstab2 = tactic_mne.groupBy("TACTIC_CELL_CD", "TST_GRP_CD").agg(
            F.count("*").alias("count"),
            F.countDistinct("CLNT_NO").alias("unique_clients")
        ).orderBy("TACTIC_CELL_CD", "TST_GRP_CD")
        crosstab2.show(100, truncate=False)
    else:
        print("TACTIC_CELL_CD not available")

    # Sample records
    print("\n[3] Sample Records with Segment Fields:")
    print("-" * 40)
    sample_cols = ["CLNT_NO", "MNE", "TST_GRP_CD", "RPT_GRP_CD", "TACTIC_CELL_CD",
                   "TREATMT_STRT_DT", "TREATMT_END_DT", "CHANNEL"]
    available_cols = [c for c in sample_cols if c in tactic_mne.columns]
    tactic_mne.select(available_cols).show(20, truncate=False)

    return tactic_mne


def check_client_overlap(
    spark: SparkSession,
    tactic_path: str = "/user/427966379/tactic.parquet",
    mnes: List[str] = None
) -> Dict[str, Any]:
    """
    Check if clients appear in multiple campaigns/cohorts.

    This helps understand if there's experiment contamination.

    Args:
        spark: Active SparkSession
        tactic_path: Path to tactic parquet
        mnes: List of MNEs to check

    Returns:
        Dictionary with overlap analysis
    """
    print("\n" + "="*60)
    print("CLIENT OVERLAP ANALYSIS")
    print("="*60)

    if mnes is None:
        mnes = ["VCN", "VDA", "VDT", "VUI", "VUT", "VAW"]

    tactic = spark.read.parquet(tactic_path)
    tactic = tactic.filter(F.col("MNE").isin(mnes))

    results = {}

    # Clients appearing in multiple MNEs
    print("\n[1] Clients appearing in multiple campaigns:")
    print("-" * 40)
    client_mne_count = tactic.groupBy("CLNT_NO").agg(
        F.countDistinct("MNE").alias("mne_count"),
        F.collect_set("MNE").alias("campaigns")
    )

    multi_mne = client_mne_count.filter(F.col("mne_count") > 1)
    multi_mne_count = multi_mne.count()
    total_clients = client_mne_count.count()

    print(f"    Total unique clients: {total_clients:,}")
    print(f"    Clients in multiple campaigns: {multi_mne_count:,} ({multi_mne_count/total_clients*100:.2f}%)")

    results["multi_campaign_clients"] = multi_mne_count
    results["total_clients"] = total_clients

    # Distribution of overlap
    print("\n[2] Overlap distribution:")
    overlap_dist = client_mne_count.groupBy("mne_count").count().orderBy("mne_count")
    overlap_dist.show()
    results["overlap_distribution"] = overlap_dist.toPandas()

    # Clients appearing in multiple cohorts (same MNE)
    print("\n[3] Clients appearing in multiple cohorts (same campaign):")
    print("-" * 40)

    for mne in mnes:
        tactic_mne = tactic.filter(F.col("MNE") == mne)

        client_cohort_count = tactic_mne.withColumn(
            "COHORT", F.date_format(F.col("TREATMT_STRT_DT"), "yyyy-MM")
        ).groupBy("CLNT_NO").agg(
            F.countDistinct("COHORT").alias("cohort_count")
        )

        multi_cohort = client_cohort_count.filter(F.col("cohort_count") > 1)
        multi_cohort_count = multi_cohort.count()
        total_in_mne = client_cohort_count.count()

        if total_in_mne > 0:
            print(f"    {mne}: {multi_cohort_count:,} clients in multiple cohorts ({multi_cohort_count/total_in_mne*100:.2f}%)")

    return results


# Main execution
if __name__ == "__main__":
    # This would typically be run in Jupyter
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("Tactic Diagnostics").getOrCreate()
    results = run_tactic_diagnostics(spark)
