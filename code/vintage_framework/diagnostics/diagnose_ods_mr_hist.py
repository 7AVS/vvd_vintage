"""
ODS MR HIST Diagnostic Script
=============================

This script investigates the ODS_MR_HIST table to understand:
- What fields are available for Layer 1 (Experiment Metadata)
- What's in the treatmt_adnl_dtl JSON field (contextual information)
- Treatment details and codes
- Channel codes and their distribution
- Data quality and coverage

Run this in Jupyter to explore before building the modular pipeline.

Usage:
    from vintage_framework.diagnostics.diagnose_ods_mr_hist import run_ods_diagnostics
    results = run_ods_diagnostics(spark)
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from typing import Dict, Any, List
import json


def run_ods_diagnostics(
    spark: SparkSession,
    partition_date: str = None,
    mne_filter: str = None
) -> Dict[str, Any]:
    """
    Run comprehensive diagnostics on ODS_MR_HIST table.

    Args:
        spark: Active SparkSession
        partition_date: Specific partition date (e.g., "2026-01-20"), or None for latest
        mne_filter: Optional filter for specific MNE (e.g., "VCN%")

    Returns:
        Dictionary with diagnostic results
    """
    print("="*70)
    print("ODS_MR_HIST DIAGNOSTICS")
    print("="*70)

    # Path configuration
    base_path = "/prod/01347/app/LS20/data/SparkJobData"

    results = {
        "table": "ods_mr_hist",
        "path": base_path,
        "success": False,
        "schema": None,
        "layer1_fields": {},
        "json_field_analysis": {},
        "data_quality": {}
    }

    try:
        # Load data
        if partition_date:
            data_path = f"{base_path}/effectDate={partition_date}"
            print(f"\n[1] Loading specific partition: {data_path}")
        else:
            # Use latest available - you may need to adjust this
            data_path = f"{base_path}/effectDate=2026-01-20"
            print(f"\n[1] Loading partition: {data_path}")

        df = spark.read.parquet(data_path)
        results["success"] = True
        results["partition_date"] = partition_date or "2026-01-20"

        # Total records
        total = df.count()
        results["total_records"] = total
        print(f"    Total records: {total:,}")

        # =====================================================================
        # SCHEMA ANALYSIS
        # =====================================================================
        print("\n" + "="*70)
        print("[2] SCHEMA - Key Fields for Layer 1")
        print("="*70)

        # Key fields we care about for Layer 1/Experiment Metadata
        layer1_fields = [
            "tactic_id",
            "clnt_id",
            "chnl_cd",
            "offr_strt_dt",
            "offr_end_dt",
            "treatmt_dtl",
            "treatmt_dtl_en",
            "treatmt_dtl_fr",
            "treatmt_adnl_dtl",  # THE JSON FIELD
            "trgt_typ_cd",
            "prod_mn",
            "campgn_cd"
        ]

        available_fields = df.columns
        print("\nField Availability:")
        print("-" * 50)
        for field in layer1_fields:
            status = "PRESENT" if field in available_fields else "MISSING"
            print(f"    {field:25s} : {status}")
            results["layer1_fields"][field] = field in available_fields

        # =====================================================================
        # JSON FIELD ANALYSIS (treatmt_adnl_dtl)
        # =====================================================================
        print("\n" + "="*70)
        print("[3] JSON FIELD ANALYSIS (treatmt_adnl_dtl)")
        print("="*70)

        if "treatmt_adnl_dtl" in available_fields:
            # Check how many records have this field populated
            json_populated = df.filter(
                (F.col("treatmt_adnl_dtl").isNotNull()) &
                (F.trim(F.col("treatmt_adnl_dtl")) != "")
            )
            json_count = json_populated.count()

            print(f"\n    Records with treatmt_adnl_dtl populated: {json_count:,} ({json_count/total*100:.2f}%)")
            results["json_field_analysis"]["populated_count"] = json_count
            results["json_field_analysis"]["populated_pct"] = json_count/total*100

            if json_count > 0:
                # Sample the JSON content
                print("\n    Sample JSON content (first 20 unique values):")
                print("-" * 50)
                json_samples = json_populated.select("tactic_id", "treatmt_adnl_dtl") \
                    .distinct() \
                    .limit(20) \
                    .collect()

                for row in json_samples:
                    tactic = row["tactic_id"][:20] if row["tactic_id"] else "NULL"
                    json_val = row["treatmt_adnl_dtl"][:100] if row["treatmt_adnl_dtl"] else "NULL"
                    print(f"\n    TACTIC: {tactic}")
                    print(f"    JSON:   {json_val}...")

                results["json_field_analysis"]["samples"] = [
                    {"tactic_id": r["tactic_id"], "json": r["treatmt_adnl_dtl"]}
                    for r in json_samples
                ]

                # Check JSON structure (is it valid JSON?)
                print("\n    Attempting to parse JSON structure...")
                try:
                    sample_json = json_samples[0]["treatmt_adnl_dtl"]
                    parsed = json.loads(sample_json)
                    print(f"    Valid JSON: YES")
                    print(f"    Keys found: {list(parsed.keys())}")
                    results["json_field_analysis"]["valid_json"] = True
                    results["json_field_analysis"]["json_keys"] = list(parsed.keys())
                except:
                    print(f"    Valid JSON: NO (may be plain text or different format)")
                    results["json_field_analysis"]["valid_json"] = False
            else:
                print("    WARNING: JSON field is NOT populated in this data")
                results["json_field_analysis"]["valid_json"] = None
        else:
            print("    WARNING: treatmt_adnl_dtl field NOT FOUND in schema")

        # =====================================================================
        # TREATMENT DETAIL FIELDS
        # =====================================================================
        print("\n" + "="*70)
        print("[4] TREATMENT DETAIL FIELDS")
        print("="*70)

        for field in ["treatmt_dtl", "treatmt_dtl_en", "treatmt_dtl_fr"]:
            if field in available_fields:
                populated = df.filter(
                    (F.col(field).isNotNull()) &
                    (F.trim(F.col(field)) != "")
                ).count()
                print(f"\n    {field}:")
                print(f"        Populated: {populated:,} ({populated/total*100:.2f}%)")

                # Sample values
                samples = df.filter(F.col(field).isNotNull()) \
                    .select(field).distinct().limit(10).collect()
                print(f"        Sample values:")
                for s in samples[:5]:
                    val = s[field][:80] if s[field] else "NULL"
                    print(f"            {val}")

        # =====================================================================
        # TACTIC ID ANALYSIS (for VVD campaigns)
        # =====================================================================
        print("\n" + "="*70)
        print("[5] TACTIC ID ANALYSIS")
        print("="*70)

        # Look for VVD-related tactics
        vvd_prefixes = ["VCN", "VDA", "VDT", "VUI", "VUT", "VAW"]

        print("\n    VVD Campaign Distribution:")
        print("-" * 50)

        for prefix in vvd_prefixes:
            if mne_filter and prefix not in mne_filter:
                continue

            vvd_count = df.filter(F.col("tactic_id").startswith(prefix)).count()
            print(f"    {prefix}: {vvd_count:,} records")

        # Unique tactic IDs for VVD
        print("\n    Unique TACTIC_IDs starting with VVD prefixes:")
        vvd_tactics = df.filter(
            F.col("tactic_id").rlike("^(VCN|VDA|VDT|VUI|VUT|VAW)")
        ).select("tactic_id").distinct().limit(30).collect()

        for t in vvd_tactics:
            print(f"        {t['tactic_id']}")

        # =====================================================================
        # CHANNEL CODE ANALYSIS
        # =====================================================================
        print("\n" + "="*70)
        print("[6] CHANNEL CODE ANALYSIS (chnl_cd)")
        print("="*70)

        if "chnl_cd" in available_fields:
            chnl_dist = df.groupBy("chnl_cd").agg(
                F.count("*").alias("record_count"),
                F.countDistinct("clnt_id").alias("unique_clients")
            ).orderBy(F.desc("record_count"))

            print("\n    Channel Code Distribution:")
            chnl_dist.show(20, truncate=False)
            results["channel_distribution"] = chnl_dist.toPandas().to_dict()

        # =====================================================================
        # DATE RANGE ANALYSIS
        # =====================================================================
        print("\n" + "="*70)
        print("[7] DATE RANGE ANALYSIS")
        print("="*70)

        for date_field in ["offr_strt_dt", "offr_end_dt"]:
            if date_field in available_fields:
                date_range = df.filter(F.col(date_field).isNotNull()).agg(
                    F.min(date_field).alias("min_date"),
                    F.max(date_field).alias("max_date"),
                    F.count("*").alias("non_null_count")
                ).collect()[0]

                print(f"\n    {date_field}:")
                print(f"        Min: {date_range['min_date']}")
                print(f"        Max: {date_range['max_date']}")
                print(f"        Non-null records: {date_range['non_null_count']:,}")

        # =====================================================================
        # SAMPLE RECORDS
        # =====================================================================
        print("\n" + "="*70)
        print("[8] SAMPLE RECORDS (Layer 1 Fields)")
        print("="*70)

        sample_cols = [c for c in layer1_fields if c in available_fields]

        # Filter to VVD if possible
        vvd_sample = df.filter(F.col("tactic_id").rlike("^(VCN|VDA|VDT|VUI|VUT|VAW)"))
        if vvd_sample.count() > 0:
            print("\n    VVD Campaign Samples:")
            vvd_sample.select(sample_cols).show(10, truncate=50)
        else:
            print("\n    General Samples (no VVD found):")
            df.select(sample_cols).show(10, truncate=50)

        print("\n" + "="*70)
        print("ODS_MR_HIST DIAGNOSTICS COMPLETE")
        print("="*70)

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        results["error"] = str(e)

    return results


def investigate_json_field(
    spark: SparkSession,
    partition_date: str = "2026-01-20",
    tactic_filter: str = None
) -> DataFrame:
    """
    Deep dive into the treatmt_adnl_dtl JSON field.

    Args:
        spark: Active SparkSession
        partition_date: Partition to query
        tactic_filter: Optional tactic_id filter (e.g., "VCN%")

    Returns:
        DataFrame with JSON field analysis
    """
    print("\n" + "="*70)
    print("JSON FIELD DEEP DIVE (treatmt_adnl_dtl)")
    print("="*70)

    base_path = "/prod/01347/app/LS20/data/SparkJobData"
    data_path = f"{base_path}/effectDate={partition_date}"

    df = spark.read.parquet(data_path)

    # Filter if specified
    if tactic_filter:
        df = df.filter(F.col("tactic_id").like(tactic_filter))
        print(f"\n    Filtered to tactic_id LIKE '{tactic_filter}'")

    # Filter to records with JSON
    json_df = df.filter(
        (F.col("treatmt_adnl_dtl").isNotNull()) &
        (F.trim(F.col("treatmt_adnl_dtl")) != "")
    )

    total = json_df.count()
    print(f"    Records with JSON: {total:,}")

    if total > 0:
        # Show all unique JSON values with their tactic IDs
        print("\n    Unique JSON values by tactic:")
        print("-" * 70)

        unique_json = json_df.select(
            "tactic_id",
            "treatmt_adnl_dtl",
            "treatmt_dtl"
        ).distinct().orderBy("tactic_id")

        unique_json.show(50, truncate=100)

        return unique_json
    else:
        print("    No records found with JSON field populated")
        return None


def check_contextual_fields(
    spark: SparkSession,
    partition_date: str = "2026-01-20",
    tactic_prefix: str = "VCN"
) -> Dict[str, Any]:
    """
    Check what contextual information is available for a specific campaign.

    This helps answer: "Does Martech populate the contextual info we need?"

    Args:
        spark: Active SparkSession
        partition_date: Partition to query
        tactic_prefix: Campaign prefix (e.g., "VCN", "VDA")

    Returns:
        Dictionary with contextual field analysis
    """
    print("\n" + "="*70)
    print(f"CONTEXTUAL FIELDS CHECK: {tactic_prefix}")
    print("="*70)

    base_path = "/prod/01347/app/LS20/data/SparkJobData"
    data_path = f"{base_path}/effectDate={partition_date}"

    df = spark.read.parquet(data_path)
    df = df.filter(F.col("tactic_id").startswith(tactic_prefix))

    total = df.count()
    print(f"\n    Total records for {tactic_prefix}: {total:,}")

    results = {"campaign": tactic_prefix, "total_records": total, "fields": {}}

    if total == 0:
        print("    No records found")
        return results

    # Check each contextual field
    contextual_fields = [
        ("treatmt_adnl_dtl", "JSON experiment metadata"),
        ("treatmt_dtl", "Treatment detail"),
        ("treatmt_dtl_en", "Treatment detail (English)"),
        ("chnl_cd", "Channel code"),
        ("trgt_typ_cd", "Target type code"),
        ("prod_mn", "Product mnemonic"),
        ("campgn_cd", "Campaign code"),
        ("delvry_mthd_cd", "Delivery method code")
    ]

    print("\n    Contextual Field Population:")
    print("-" * 60)
    print(f"    {'Field':<25} {'Populated':<15} {'Unique Values':<15}")
    print("-" * 60)

    for field, description in contextual_fields:
        if field in df.columns:
            populated = df.filter(
                (F.col(field).isNotNull()) &
                (F.trim(F.col(field).cast("string")) != "")
            ).count()
            unique = df.select(field).distinct().count()

            pct = populated / total * 100
            print(f"    {field:<25} {populated:>10,} ({pct:>5.1f}%)  {unique:>10,}")

            results["fields"][field] = {
                "populated": populated,
                "populated_pct": pct,
                "unique_values": unique
            }

            # Show unique values if not too many
            if unique <= 10 and unique > 0:
                values = df.select(field).distinct().collect()
                print(f"        Values: {[v[field] for v in values]}")
        else:
            print(f"    {field:<25} {'MISSING':<15}")

    return results


# Main execution
if __name__ == "__main__":
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("ODS MR HIST Diagnostics").getOrCreate()
    results = run_ods_diagnostics(spark)
