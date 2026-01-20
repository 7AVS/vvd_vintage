"""
TACTIC_EVNT_HIST Diagnostic Script (Source Table)
==================================================

This script investigates the SOURCE tactic_evnt_hist table to understand:
- Key fields for Layer 1 (Experiment Metadata)
- Report Group codes (RPT_GRP_CD) - segment identification
- Test Group codes (TST_GRP_CD) - test vs control
- Treatment meaning (TREATMT_MN)
- Additional decision data fields (flexible fields)
- Tactic cell codes

This is the SOURCE TABLE, not the user directory parquet.

Source: prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist

Usage:
    from vintage_framework.diagnostics.diagnose_tactic_evnt_hist import run_tactic_evnt_diagnostics
    results = run_tactic_evnt_diagnostics(spark)
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from typing import Dict, Any, List


def run_tactic_evnt_diagnostics(
    spark: SparkSession,
    mne_prefixes: List[str] = None
) -> Dict[str, Any]:
    """
    Run comprehensive diagnostics on source TACTIC_EVNT_HIST table.

    Args:
        spark: Active SparkSession
        mne_prefixes: List of MNE prefixes to focus on (default: VVD campaigns)

    Returns:
        Dictionary with diagnostic results
    """
    print("="*70)
    print("TACTIC_EVNT_HIST DIAGNOSTICS (Source Table)")
    print("="*70)

    # Default to VVD campaigns
    if mne_prefixes is None:
        mne_prefixes = ["VCN", "VDA", "VDT", "VUI", "VUT", "VAW"]

    # Source table - try Hive table name first
    table_name = "prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist"

    results = {
        "table": table_name,
        "success": False,
        "schema": None,
        "layer1_fields": {},
        "segmentation_analysis": {},
        "data_quality": {}
    }

    try:
        print(f"\n[1] Loading from: {table_name}")
        df = spark.table(table_name)
        results["success"] = True

        # Total records
        total = df.count()
        results["total_records"] = total
        print(f"    Total records: {total:,}")

        # =====================================================================
        # SCHEMA ANALYSIS
        # =====================================================================
        print("\n" + "="*70)
        print("[2] SCHEMA - Key Fields for Layer 1 (Experiment Metadata)")
        print("="*70)

        # Key fields per documentation
        layer1_fields = [
            "tactic_evnt_id",       # Client linkage
            "tactic_id",            # Tactic identifier
            "rpt_grp_cd",           # CRITICAL: Report group (segments)
            "tst_grp_cd",           # CRITICAL: Test group (test vs control)
            "treatmt_mn",           # CRITICAL: Treatment meaning
            "treatmt_strt_dt",      # Treatment start date
            "treatmt_end_dt",       # Treatment end date
            "tactic_cell_cd",       # Tactic cell code
            "addnl_decisn_data1",   # Flexible field 1
            "addnl_decisn_data2",   # Flexible field 2
            "addnl_decisn_data3",   # Flexible field 3
            "strtgy_src_cd",        # Strategy source code
            "trgt_typ_cd",          # Target type code
            "bus_mkt_id",           # Business market ID
            "selt_affinity_mdl_scor" # Model score
        ]

        available_fields = [f.lower() for f in df.columns]
        print("\nField Availability:")
        print("-" * 60)
        for field in layer1_fields:
            status = "PRESENT" if field.lower() in available_fields else "MISSING"
            actual_name = field if field.lower() in available_fields else "N/A"
            print(f"    {field:<25s} : {status}")
            results["layer1_fields"][field] = field.lower() in available_fields

        # Print full schema
        print("\n    Full Schema:")
        df.printSchema()

        # =====================================================================
        # VVD CAMPAIGN FILTER
        # =====================================================================
        print("\n" + "="*70)
        print("[3] VVD CAMPAIGN DISTRIBUTION")
        print("="*70)

        # Build filter for VVD campaigns
        vvd_filter = None
        for prefix in mne_prefixes:
            condition = F.col("tactic_id").startswith(prefix)
            vvd_filter = condition if vvd_filter is None else vvd_filter | condition

        df_vvd = df.filter(vvd_filter) if vvd_filter else df
        vvd_count = df_vvd.count()
        print(f"\n    VVD records (prefixes: {', '.join(mne_prefixes)}): {vvd_count:,}")

        # Distribution by prefix
        print("\n    Distribution by campaign prefix:")
        for prefix in mne_prefixes:
            prefix_count = df.filter(F.col("tactic_id").startswith(prefix)).count()
            print(f"        {prefix}: {prefix_count:,}")

        if vvd_count == 0:
            print("\n    WARNING: No VVD records found. Showing all data instead.")
            df_vvd = df.limit(100000)

        # =====================================================================
        # RPT_GRP_CD ANALYSIS (Segments)
        # =====================================================================
        print("\n" + "="*70)
        print("[4] RPT_GRP_CD ANALYSIS (Segment Codes)")
        print("="*70)

        if "rpt_grp_cd" in available_fields:
            rpt_grp_dist = df_vvd.groupBy(
                F.substring("tactic_id", 1, 3).alias("campaign"),
                "rpt_grp_cd"
            ).agg(
                F.count("*").alias("record_count"),
                F.countDistinct("tactic_evnt_id").alias("unique_clients")
            ).orderBy("campaign", "rpt_grp_cd")

            print("\n    RPT_GRP_CD by Campaign:")
            rpt_grp_dist.show(50, truncate=False)
            results["segmentation_analysis"]["rpt_grp_cd"] = rpt_grp_dist.toPandas().to_dict()
        else:
            print("    RPT_GRP_CD not found in schema")

        # =====================================================================
        # TST_GRP_CD ANALYSIS (Test vs Control)
        # =====================================================================
        print("\n" + "="*70)
        print("[5] TST_GRP_CD ANALYSIS (Test vs Control)")
        print("="*70)

        if "tst_grp_cd" in available_fields:
            tst_grp_dist = df_vvd.groupBy(
                F.substring("tactic_id", 1, 3).alias("campaign"),
                "tst_grp_cd"
            ).agg(
                F.count("*").alias("record_count"),
                F.countDistinct("tactic_evnt_id").alias("unique_clients")
            ).orderBy("campaign", "tst_grp_cd")

            print("\n    TST_GRP_CD by Campaign:")
            tst_grp_dist.show(50, truncate=False)
            results["segmentation_analysis"]["tst_grp_cd"] = tst_grp_dist.toPandas().to_dict()

            # Check if TG4 is consistently Test
            print("\n    Is TG4 the Test group across all campaigns?")
            tg4_check = df_vvd.filter(F.col("tst_grp_cd") == "TG4").groupBy(
                F.substring("tactic_id", 1, 3).alias("campaign")
            ).count()
            tg4_check.show(10)
        else:
            print("    TST_GRP_CD not found in schema")

        # =====================================================================
        # TREATMT_MN ANALYSIS (Treatment Meaning)
        # =====================================================================
        print("\n" + "="*70)
        print("[6] TREATMT_MN ANALYSIS (Treatment Meaning)")
        print("="*70)

        if "treatmt_mn" in available_fields:
            treatmt_dist = df_vvd.groupBy(
                F.substring("tactic_id", 1, 3).alias("campaign"),
                "treatmt_mn"
            ).agg(
                F.count("*").alias("record_count")
            ).orderBy("campaign", "treatmt_mn")

            print("\n    Treatment Meaning by Campaign:")
            treatmt_dist.show(50, truncate=False)
        else:
            print("    TREATMT_MN not found in schema")

        # =====================================================================
        # TACTIC_CELL_CD ANALYSIS
        # =====================================================================
        print("\n" + "="*70)
        print("[7] TACTIC_CELL_CD ANALYSIS")
        print("="*70)

        if "tactic_cell_cd" in available_fields:
            cell_dist = df_vvd.groupBy(
                F.substring("tactic_id", 1, 3).alias("campaign"),
                "tactic_cell_cd"
            ).agg(
                F.count("*").alias("record_count")
            ).orderBy("campaign", "tactic_cell_cd")

            print("\n    TACTIC_CELL_CD by Campaign (top 50):")
            cell_dist.show(50, truncate=False)
        else:
            print("    TACTIC_CELL_CD not found in schema")

        # =====================================================================
        # ADDITIONAL DECISION DATA FIELDS (Flexible Fields)
        # =====================================================================
        print("\n" + "="*70)
        print("[8] ADDNL_DECISN_DATA FIELDS (Flexible Fields)")
        print("="*70)

        for field in ["addnl_decisn_data1", "addnl_decisn_data2", "addnl_decisn_data3"]:
            if field in available_fields:
                populated = df_vvd.filter(
                    (F.col(field).isNotNull()) &
                    (F.trim(F.col(field)) != "")
                ).count()

                pct = populated / vvd_count * 100 if vvd_count > 0 else 0
                print(f"\n    {field}:")
                print(f"        Populated: {populated:,} ({pct:.1f}%)")

                if populated > 0:
                    # Sample values
                    samples = df_vvd.filter(F.col(field).isNotNull()) \
                        .select(field).distinct().limit(10).collect()
                    print(f"        Sample values:")
                    for s in samples[:5]:
                        val = str(s[field])[:60]
                        print(f"            {val}")
            else:
                print(f"\n    {field}: NOT FOUND")

        # =====================================================================
        # DATE RANGE ANALYSIS
        # =====================================================================
        print("\n" + "="*70)
        print("[9] DATE RANGE ANALYSIS")
        print("="*70)

        for date_field in ["treatmt_strt_dt", "treatmt_end_dt", "evnt_strt_dt"]:
            if date_field in available_fields:
                date_range = df_vvd.filter(F.col(date_field).isNotNull()).agg(
                    F.min(date_field).alias("min_date"),
                    F.max(date_field).alias("max_date"),
                    F.count("*").alias("non_null_count")
                ).collect()[0]

                print(f"\n    {date_field}:")
                print(f"        Min: {date_range['min_date']}")
                print(f"        Max: {date_range['max_date']}")
                print(f"        Non-null: {date_range['non_null_count']:,}")

        # =====================================================================
        # CROSS-TAB: RPT_GRP_CD x TST_GRP_CD
        # =====================================================================
        print("\n" + "="*70)
        print("[10] CROSS-TAB: RPT_GRP_CD x TST_GRP_CD (per campaign)")
        print("="*70)

        if "rpt_grp_cd" in available_fields and "tst_grp_cd" in available_fields:
            for prefix in mne_prefixes[:3]:  # Limit to first 3 for readability
                df_prefix = df_vvd.filter(F.col("tactic_id").startswith(prefix))
                if df_prefix.count() > 0:
                    print(f"\n    {prefix} Campaign:")
                    crosstab = df_prefix.groupBy("rpt_grp_cd", "tst_grp_cd").agg(
                        F.count("*").alias("count")
                    ).orderBy("rpt_grp_cd", "tst_grp_cd")
                    crosstab.show(30, truncate=False)

        # =====================================================================
        # SAMPLE RECORDS
        # =====================================================================
        print("\n" + "="*70)
        print("[11] SAMPLE RECORDS")
        print("="*70)

        sample_cols = [c for c in layer1_fields if c.lower() in available_fields]
        if sample_cols:
            print("\n    Sample records with Layer 1 fields:")
            df_vvd.select(sample_cols).show(10, truncate=50)

        print("\n" + "="*70)
        print("TACTIC_EVNT_HIST DIAGNOSTICS COMPLETE")
        print("="*70)

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        results["error"] = str(e)

        # Try alternative access method
        print("\n    Attempting alternative access via Hive SQL...")
        try:
            df = spark.sql(f"SELECT * FROM {table_name} LIMIT 10")
            print("    Alternative access successful. Schema:")
            df.printSchema()
        except Exception as e2:
            print(f"    Alternative also failed: {str(e2)}")

    return results


def compare_tactic_sources(
    spark: SparkSession,
    user_parquet_path: str = "/user/427966379/tactic.parquet"
) -> Dict[str, Any]:
    """
    Compare the source TACTIC_EVNT_HIST with user's tactic.parquet.

    Helps understand if the parquet is a subset/transformation of source.

    Args:
        spark: Active SparkSession
        user_parquet_path: Path to user's tactic parquet

    Returns:
        Dictionary with comparison results
    """
    print("\n" + "="*70)
    print("TACTIC SOURCE COMPARISON")
    print("="*70)

    results = {}

    # Load user parquet
    print("\n[1] User's tactic.parquet:")
    try:
        user_df = spark.read.parquet(user_parquet_path)
        user_count = user_df.count()
        user_cols = set(user_df.columns)
        print(f"    Records: {user_count:,}")
        print(f"    Columns: {len(user_cols)}")
        results["user_parquet"] = {"count": user_count, "columns": list(user_cols)}
    except Exception as e:
        print(f"    ERROR: {str(e)}")
        results["user_parquet"] = {"error": str(e)}

    # Load source table
    print("\n[2] Source TACTIC_EVNT_HIST:")
    table_name = "prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist"
    try:
        source_df = spark.table(table_name)
        source_count = source_df.count()
        source_cols = set([c.lower() for c in source_df.columns])
        print(f"    Records: {source_count:,}")
        print(f"    Columns: {len(source_cols)}")
        results["source_table"] = {"count": source_count, "columns": list(source_cols)}

        # Compare columns
        print("\n[3] Column Comparison:")
        user_cols_lower = set([c.lower() for c in user_cols])

        common = user_cols_lower & source_cols
        only_user = user_cols_lower - source_cols
        only_source = source_cols - user_cols_lower

        print(f"    Common columns: {len(common)}")
        print(f"    Only in user parquet: {len(only_user)}")
        if only_user:
            print(f"        {only_user}")
        print(f"    Only in source: {len(only_source)}")
        if only_source and len(only_source) <= 20:
            print(f"        {only_source}")

    except Exception as e:
        print(f"    ERROR: {str(e)}")
        results["source_table"] = {"error": str(e)}

    return results


# Main execution
if __name__ == "__main__":
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("Tactic EVNT HIST Diagnostics").getOrCreate()
    results = run_tactic_evnt_diagnostics(spark)
