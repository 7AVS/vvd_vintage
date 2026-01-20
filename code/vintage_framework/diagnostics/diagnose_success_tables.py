"""
Success Tables Diagnostic Script
================================

This script investigates the success tables to understand:
- Schema and available fields
- Date ranges and data coverage
- Filter effectiveness
- Data quality issues

Run this in Jupyter to verify success table configuration.

Usage:
    from vintage_framework.diagnostics.diagnose_success_tables import run_success_diagnostics
    results = run_success_diagnostics(spark)
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from typing import Dict, Any, List


def run_success_diagnostics(
    spark: SparkSession,
    years: List[str] = ["2025", "2026"]
) -> Dict[str, Any]:
    """
    Run diagnostics on all success tables.

    Args:
        spark: Active SparkSession
        years: Years to include

    Returns:
        Dictionary with diagnostic results
    """
    print("="*60)
    print("SUCCESS TABLES DIAGNOSTICS")
    print("="*60)

    results = {}

    # 1. VISA_DR_CRD (Acquisition/Activation)
    results["visa_dr_crd"] = diagnose_visa_dr_crd(spark, years)

    # 2. POS_TXN (Usage)
    results["pos_txn"] = diagnose_pos_txn(spark, years)

    # 3. Token (Tokenization)
    results["token"] = diagnose_token(spark)

    return results


def diagnose_visa_dr_crd(
    spark: SparkSession,
    years: List[str] = ["2025", "2026"]
) -> Dict[str, Any]:
    """
    Diagnose DDWTA_VISA_DR_CRD table (Acquisition/Activation).
    """
    print("\n" + "-"*60)
    print("DDWTA_VISA_DR_CRD (Acquisition/Activation)")
    print("-"*60)

    base_path = "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT="
    paths = [f"{base_path}{year}*" for year in years]

    results = {"table": "DDWTA_VISA_DR_CRD", "success": False}

    try:
        df = spark.read.parquet(*paths)
        results["success"] = True

        # Schema
        print("\n[1] Schema (key fields):")
        key_fields = ["CLNT_NO", "ISS_DT", "ACTV_DT", "STS_CD", "SRVC_ID", "VISA_DR_CRD_BRND_CD"]
        for field in key_fields:
            if field in df.columns:
                print(f"    {field}: present")
            else:
                print(f"    {field}: MISSING")

        # Total records
        total = df.count()
        results["total_records"] = total
        print(f"\n[2] Total records: {total:,}")

        # Filter to VVD (SRVC_ID = 36)
        vvd_df = df.filter(F.col("SRVC_ID") == 36)
        vvd_count = vvd_df.count()
        print(f"    VVD records (SRVC_ID=36): {vvd_count:,}")

        # Further filter by status
        vvd_valid = vvd_df.filter(F.col("STS_CD").isin(["06", "08"]))
        valid_count = vvd_valid.count()
        print(f"    Valid status (06, 08): {valid_count:,}")

        # Date range
        print("\n[3] ISS_DT range (VVD, valid status):")
        iss_range = vvd_valid.filter(F.col("ISS_DT").isNotNull()).agg(
            F.min("ISS_DT").alias("min_iss_dt"),
            F.max("ISS_DT").alias("max_iss_dt"),
            F.count("*").alias("with_iss_dt")
        ).collect()[0]
        print(f"    Min: {iss_range['min_iss_dt']}")
        print(f"    Max: {iss_range['max_iss_dt']}")
        print(f"    Records with ISS_DT: {iss_range['with_iss_dt']:,}")

        print("\n[4] ACTV_DT range (VVD, valid status):")
        actv_range = vvd_valid.filter(F.col("ACTV_DT").isNotNull()).agg(
            F.min("ACTV_DT").alias("min_actv_dt"),
            F.max("ACTV_DT").alias("max_actv_dt"),
            F.count("*").alias("with_actv_dt")
        ).collect()[0]
        print(f"    Min: {actv_range['min_actv_dt']}")
        print(f"    Max: {actv_range['max_actv_dt']}")
        print(f"    Records with ACTV_DT: {actv_range['with_actv_dt']:,}")

        # Card type distribution
        print("\n[5] Card Type Distribution (VISA_DR_CRD_BRND_CD):")
        card_type = vvd_valid.groupBy("VISA_DR_CRD_BRND_CD").count().orderBy("VISA_DR_CRD_BRND_CD")
        card_type.show()

        results["vvd_valid_count"] = valid_count
        results["date_range"] = {
            "iss_dt": {"min": str(iss_range['min_iss_dt']), "max": str(iss_range['max_iss_dt'])},
            "actv_dt": {"min": str(actv_range['min_actv_dt']), "max": str(actv_range['max_actv_dt'])}
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        results["error"] = str(e)

    return results


def diagnose_pos_txn(
    spark: SparkSession,
    years: List[str] = ["2025", "2026"]
) -> Dict[str, Any]:
    """
    Diagnose DDWTA_T_PT_OF_SALE_TXN table (Usage).
    """
    print("\n" + "-"*60)
    print("DDWTA_T_PT_OF_SALE_TXN (Usage)")
    print("-"*60)

    base_path = "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT="
    paths = [f"{base_path}{year}*" for year in years]

    results = {"table": "DDWTA_T_PT_OF_SALE_TXN", "success": False}

    try:
        df = spark.read.parquet(*paths)
        results["success"] = True

        # Schema
        print("\n[1] Schema (key fields):")
        key_fields = ["CLNT_CRD_NO", "TXN_DT", "SRVC_CD", "TXN_TP", "MSG_TP", "AMT1", "POS_ENTRY_MODE_CD_NON_EMV"]
        for field in key_fields:
            if field in df.columns:
                print(f"    {field}: present")
            else:
                print(f"    {field}: MISSING")

        # Total records (sample - full count may be expensive)
        print("\n[2] Record count (sampled):")
        # Use approximation for large tables
        approx_count = df.rdd.countApprox(timeout=30, confidence=0.95)
        print(f"    Approximate total: {approx_count:,}")

        # Filter to VVD (SRVC_CD = 36)
        vvd_df = df.filter(F.col("SRVC_CD") == 36)

        # Apply transaction type filters
        txn_filter = (
            ((F.col("TXN_TP") == 10) & (F.col("MSG_TP") == "0210")) |
            ((F.col("TXN_TP") == 13) & (F.col("MSG_TP") == "0210")) |
            ((F.col("TXN_TP") == 12) & (F.col("MSG_TP") == "0220"))
        )
        vvd_purchase = vvd_df.filter(txn_filter & (F.col("AMT1") > 0))

        print("\n[3] VVD purchase transactions:")
        vvd_purchase_count = vvd_purchase.count()
        print(f"    Count: {vvd_purchase_count:,}")

        # Date range
        print("\n[4] TXN_DT range:")
        txn_range = vvd_purchase.agg(
            F.min("TXN_DT").alias("min_txn_dt"),
            F.max("TXN_DT").alias("max_txn_dt")
        ).collect()[0]
        print(f"    Min: {txn_range['min_txn_dt']}")
        print(f"    Max: {txn_range['max_txn_dt']}")

        # TXN_TP x MSG_TP distribution
        print("\n[5] TXN_TP x MSG_TP distribution (VVD):")
        txn_dist = vvd_df.filter(F.col("AMT1") > 0).groupBy("TXN_TP", "MSG_TP").count().orderBy("TXN_TP", "MSG_TP")
        txn_dist.show(20)

        results["vvd_purchase_count"] = vvd_purchase_count

    except Exception as e:
        print(f"ERROR: {str(e)}")
        results["error"] = str(e)

    return results


def diagnose_token(
    spark: SparkSession,
    token_path: str = "/user/427966379/token.parquet"
) -> Dict[str, Any]:
    """
    Diagnose Token parquet (Tokenization).
    """
    print("\n" + "-"*60)
    print("TOKEN PARQUET (Tokenization)")
    print("-"*60)

    results = {"table": "token.parquet", "success": False}

    try:
        df = spark.read.parquet(token_path)
        results["success"] = True

        # Schema
        print("\n[1] Schema:")
        df.printSchema()

        # Total records
        total = df.count()
        results["total_records"] = total
        print(f"\n[2] Total records: {total:,}")

        # Unique clients
        unique_clients = df.select("CLNT_NO").distinct().count()
        print(f"    Unique clients: {unique_clients:,}")

        # Date range
        print("\n[3] TXN_DT range:")
        txn_range = df.agg(
            F.min("TXN_DT").alias("min_txn_dt"),
            F.max("TXN_DT").alias("max_txn_dt")
        ).collect()[0]
        print(f"    Min: {txn_range['min_txn_dt']}")
        print(f"    Max: {txn_range['max_txn_dt']}")

        # Sample records
        print("\n[4] Sample records:")
        df.show(10)

        results["unique_clients"] = unique_clients
        results["date_range"] = {
            "min": str(txn_range['min_txn_dt']),
            "max": str(txn_range['max_txn_dt'])
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        results["error"] = str(e)

    return results


def validate_join_keys(
    spark: SparkSession,
    tactic_path: str = "/user/427966379/tactic.parquet",
    mne: str = "VCN"
) -> Dict[str, Any]:
    """
    Validate that join keys match between tactic and success tables.

    Checks:
    - CLNT_NO format consistency
    - Date range overlap
    - Sample join success rate
    """
    print("\n" + "="*60)
    print(f"JOIN KEY VALIDATION: {mne}")
    print("="*60)

    results = {}

    # Load tactic
    tactic = spark.read.parquet(tactic_path)
    tactic_mne = tactic.filter(F.col("MNE") == mne)

    # Get CLNT_NO samples
    print("\n[1] CLNT_NO format (tactic):")
    tactic_sample = tactic_mne.select("CLNT_NO").limit(10).collect()
    for row in tactic_sample[:5]:
        print(f"    {row['CLNT_NO']}")

    # Check CLNT_NO data type
    clnt_dtype = dict(tactic_mne.dtypes).get("CLNT_NO", "unknown")
    print(f"    Data type: {clnt_dtype}")

    # Load success table based on MNE
    if mne in ["VCN", "VDA", "VDT"]:
        print("\n[2] Loading VISA_DR_CRD for comparison...")
        base_path = "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT="
        success = spark.read.parquet(f"{base_path}2025*", f"{base_path}2026*")
        success = success.filter(
            (F.col("SRVC_ID") == 36) &
            (F.col("STS_CD").isin(["06", "08"]))
        )

        print("    CLNT_NO format (success):")
        success_sample = success.select("CLNT_NO").limit(10).collect()
        for row in success_sample[:5]:
            print(f"    {row['CLNT_NO']}")

        success_clnt_dtype = dict(success.dtypes).get("CLNT_NO", "unknown")
        print(f"    Data type: {success_clnt_dtype}")

        # Test join
        print("\n[3] Testing join (first 1000 tactic records):")
        tactic_sample = tactic_mne.limit(1000)
        joined = tactic_sample.join(
            success.select("CLNT_NO").distinct(),
            on="CLNT_NO",
            how="inner"
        )
        match_count = joined.count()
        print(f"    Tactic sample: 1000")
        print(f"    Matched in success: {match_count}")
        print(f"    Match rate: {match_count/10:.1f}%")

        results["match_rate"] = match_count / 10

    return results


# Main execution
if __name__ == "__main__":
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("Success Table Diagnostics").getOrCreate()
    results = run_success_diagnostics(spark)
