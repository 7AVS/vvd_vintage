# =============================================================================
# ODS MR HIST - JSON Field Diagnostic
# =============================================================================
# Purpose: Investigate what's in the treatmt_adnl_dtl (JSON) field
#          and the treatmt_dtl (150-byte) fields for VVD campaigns
#
# IMPORTANT: Uses partition filtering on effectdate
# =============================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, lit, length,
    when, trim, lower, substring
)

# -----------------------------------------------------------------------------
# CONFIGURATION - UPDATE THESE VALUES
# -----------------------------------------------------------------------------

# ODS MR HIST - Hive table
HIVE_DATABASE = "prod_x610_crm"
HIVE_TABLE = "ods_mr_hist"

# Partition filter (date range to capture older campaigns)
PARTITION_COLUMN = "effectdate"
PARTITION_START = "2024-01-01"
PARTITION_END = "2026-12-31"

# VVD campaign mnemonics (use prod_mn field to filter)
VVD_MNEMONICS = ['VCN', 'VDA', 'VDT', 'VUI', 'VUT', 'VAW']

# -----------------------------------------------------------------------------
# INITIALIZE SPARK
# -----------------------------------------------------------------------------

spark = SparkSession.builder \
    .appName("ODS JSON Field Diagnostic") \
    .enableHiveSupport() \
    .getOrCreate()

print("=" * 80)
print("ODS MR HIST - JSON FIELD DIAGNOSTIC")
print(f"Table: {HIVE_DATABASE}.{HIVE_TABLE}")
print(f"Partition filter: {PARTITION_COLUMN} BETWEEN {PARTITION_START} AND {PARTITION_END}")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA FROM HIVE TABLE WITH PARTITION FILTER
# -----------------------------------------------------------------------------

print("\n[1] Loading ODS MR HIST data...")
print(f"    Table: {HIVE_DATABASE}.{HIVE_TABLE}")
print(f"    Filter: {PARTITION_COLUMN} BETWEEN '{PARTITION_START}' AND '{PARTITION_END}'")

df = spark.table(f"{HIVE_DATABASE}.{HIVE_TABLE}") \
    .filter(
        (col(PARTITION_COLUMN) >= PARTITION_START) &
        (col(PARTITION_COLUMN) <= PARTITION_END)
    )

record_count = df.count()
print(f"    Records: {record_count:,}")

# -----------------------------------------------------------------------------
# STEP 2: CHECK SCHEMA - What fields exist?
# -----------------------------------------------------------------------------

print("\n[2] Checking schema for key fields...")

key_fields = [
    "prod_mn",            # Campaign mnemonic (VCN, VDA, etc.)
    "tactic_id",
    "clnt_id",
    "chnl_cd",
    "treatmt_adnl_dtl",   # THE JSON FIELD - main interest
    "treatmt_dtl",        # 150 byte field
    "treatmt_dtl_en",
    "treatmt_dtl_fr",
    "offr_strt_dt",
    "offr_end_dt"
]

existing = [f for f in key_fields if f in df.columns]
missing = [f for f in key_fields if f not in df.columns]

print(f"    Found: {existing}")
if missing:
    print(f"    MISSING: {missing}")

# -----------------------------------------------------------------------------
# STEP 3: FILTER FOR VVD CAMPAIGNS USING prod_mn
# -----------------------------------------------------------------------------

print("\n[3] Filtering for VVD campaigns using prod_mn...")

# First check what prod_mn values exist
print("\n    All distinct prod_mn values in partition:")
df.select("prod_mn").distinct().orderBy("prod_mn").show(100, truncate=False)

# Filter using prod_mn (the mnemonic field)
df_vvd = df.filter(col("prod_mn").isin(VVD_MNEMONICS))
vvd_count = df_vvd.count()
print(f"\n    VVD records (filtered by prod_mn): {vvd_count:,}")

if vvd_count == 0:
    print("\n    WARNING: No VVD records found with mnemonics:", VVD_MNEMONICS)
    print("    Check the prod_mn values above - mnemonics might be different")

# -----------------------------------------------------------------------------
# STEP 4: JSON FIELD (treatmt_adnl_dtl) ANALYSIS
# -----------------------------------------------------------------------------

print("\n[4] Analyzing treatmt_adnl_dtl (JSON field)...")

if "treatmt_adnl_dtl" in df.columns and vvd_count > 0:

    json_stats = df_vvd.agg(
        count("*").alias("total_records"),
        count(when(col("treatmt_adnl_dtl").isNotNull(), 1)).alias("json_not_null"),
        count(when(
            (col("treatmt_adnl_dtl").isNotNull()) &
            (trim(col("treatmt_adnl_dtl")) != ""), 1
        )).alias("json_not_empty"),
        countDistinct("treatmt_adnl_dtl").alias("distinct_values")
    ).collect()[0]

    print(f"    Total VVD records:    {json_stats['total_records']:,}")
    print(f"    JSON NOT NULL:        {json_stats['json_not_null']:,}")
    print(f"    JSON NOT EMPTY:       {json_stats['json_not_empty']:,}")
    print(f"    Distinct values:      {json_stats['distinct_values']:,}")

    # Sample values
    print("\n    Sample JSON values:")
    print("    " + "-" * 70)

    df_vvd.filter(
        (col("treatmt_adnl_dtl").isNotNull()) &
        (trim(col("treatmt_adnl_dtl")) != "")
    ).select(
        "tactic_id",
        "treatmt_adnl_dtl"
    ).distinct().show(20, truncate=False)

    # Check for expected JSON structure
    print("\n    Checking for JSON structure markers...")

    df_json_markers = df_vvd.filter(col("treatmt_adnl_dtl").isNotNull()).agg(
        count("*").alias("total"),
        count(when(col("treatmt_adnl_dtl").contains("{"), 1)).alias("has_brace"),
        count(when(col("treatmt_adnl_dtl").contains("Experiments"), 1)).alias("has_Experiments"),
        count(when(col("treatmt_adnl_dtl").contains("type"), 1)).alias("has_type"),
        count(when(col("treatmt_adnl_dtl").contains("Test"), 1)).alias("has_Test"),
        count(when(col("treatmt_adnl_dtl").contains("Control"), 1)).alias("has_Control")
    ).collect()[0]

    print(f"    Contains '{{':           {df_json_markers['has_brace']:,}")
    print(f"    Contains 'Experiments':  {df_json_markers['has_Experiments']:,}")
    print(f"    Contains 'type':         {df_json_markers['has_type']:,}")
    print(f"    Contains 'Test':         {df_json_markers['has_Test']:,}")
    print(f"    Contains 'Control':      {df_json_markers['has_Control']:,}")

elif "treatmt_adnl_dtl" not in df.columns:
    print("    ERROR: treatmt_adnl_dtl field not found!")
    print("    Available columns:", df.columns)

# -----------------------------------------------------------------------------
# STEP 5: 150-BYTE FIELD (treatmt_dtl) ANALYSIS
# -----------------------------------------------------------------------------

print("\n[5] Analyzing treatmt_dtl (150-byte field)...")

if "treatmt_dtl" in df.columns and vvd_count > 0:

    dtl_stats = df_vvd.agg(
        count(when(col("treatmt_dtl").isNotNull(), 1)).alias("not_null"),
        count(when(
            (col("treatmt_dtl").isNotNull()) &
            (trim(col("treatmt_dtl")) != ""), 1
        )).alias("not_empty"),
        countDistinct("treatmt_dtl").alias("distinct")
    ).collect()[0]

    print(f"    NOT NULL:  {dtl_stats['not_null']:,}")
    print(f"    NOT EMPTY: {dtl_stats['not_empty']:,}")
    print(f"    Distinct:  {dtl_stats['distinct']:,}")

    print("\n    Distinct treatmt_dtl values:")
    df_vvd.filter(col("treatmt_dtl").isNotNull()).select(
        "treatmt_dtl"
    ).distinct().show(30, truncate=False)

# -----------------------------------------------------------------------------
# STEP 6: BREAKDOWN BY CAMPAIGN
# -----------------------------------------------------------------------------

print("\n[6] Field population by campaign (prod_mn)...")

if vvd_count > 0:
    df_vvd.groupBy("prod_mn").agg(
        count("*").alias("total"),
        count(when(col("treatmt_adnl_dtl").isNotNull(), 1)).alias("json_filled"),
        count(when(col("treatmt_dtl").isNotNull(), 1)).alias("dtl_filled")
    ).orderBy("prod_mn").show()

# -----------------------------------------------------------------------------
# STEP 7: SAMPLE RECORDS
# -----------------------------------------------------------------------------

print("\n[7] Sample complete records...")

if vvd_count > 0:
    sample_cols = [c for c in ["prod_mn", "tactic_id", "clnt_id", "chnl_cd",
                                "treatmt_adnl_dtl", "treatmt_dtl",
                                "offr_strt_dt"] if c in df.columns]

    df_vvd.select(sample_cols).show(5, truncate=False)

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
