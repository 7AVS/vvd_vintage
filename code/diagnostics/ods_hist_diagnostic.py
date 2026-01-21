# =============================================================================
# ODS HIST - JSON Field Diagnostic (Alternative ODS table)
# =============================================================================
# Purpose: Investigate the ODS_HIST table (different from ODS_MR_HIST)
#          Looking for experiment metadata fields
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

# ODS HIST - Hive table (the OTHER ODS table)
HIVE_DATABASE = "prod_x610_crm"
HIVE_TABLE = "ods_hist"

# Partition filter - NARROW RANGE for one deployment
PARTITION_COLUMN = "effectdate"
PARTITION_START = "2025-10-01"  # Adjust based on known deployment
PARTITION_END = "2025-12-31"    # Narrow window

# Focus on ONE campaign for diagnostic (change as needed)
VVD_MNEMONICS = ['VDA']  # VDA = Black Friday / Cyber Monday

# -----------------------------------------------------------------------------
# INITIALIZE SPARK
# -----------------------------------------------------------------------------

spark = SparkSession.builder \
    .appName("ODS JSON Field Diagnostic") \
    .enableHiveSupport() \
    .getOrCreate()

print("=" * 80)
print("ODS HIST - JSON FIELD DIAGNOSTIC")
print(f"Table: {HIVE_DATABASE}.{HIVE_TABLE}")
print(f"Partition filter: {PARTITION_COLUMN} BETWEEN {PARTITION_START} AND {PARTITION_END}")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA FROM HIVE TABLE WITH PARTITION FILTER
# -----------------------------------------------------------------------------

print("\n[1] Loading ODS HIST data...")
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
# STEP 2: CHECK SCHEMA - SHOW ACTUAL COLUMNS FIRST
# -----------------------------------------------------------------------------

print("\n[2] Checking schema...")
print("\n    ACTUAL COLUMNS IN TABLE:")
for c in df.columns:
    print(f"      - {c}")

# Key fields we're looking for (UPPERCASE based on Hive)
key_fields = [
    "PROD_MN",            # Campaign mnemonic (VCN, VDA, etc.)
    "TACTIC_ID",
    "CLNT_ID",
    "CHNL_CD",
    "TREATMT_ADNL_DTL",   # THE JSON FIELD - main interest
    "TREATMT_DTL",        # 150 byte field
    "TREATMT_DTL_EN",
    "TREATMT_DTL_FR",
    "OFFR_STRT_DT",
    "OFFR_END_DT"
]

print("\n    Checking for expected key fields...")
existing = [f for f in key_fields if f in df.columns]
missing = [f for f in key_fields if f not in df.columns]

print(f"    Found: {existing}")
if missing:
    print(f"    MISSING: {missing}")

# -----------------------------------------------------------------------------
# STEP 3: FILTER FOR VVD CAMPAIGNS USING PROD_MN
# -----------------------------------------------------------------------------

print("\n[3] Filtering for VVD campaigns using PROD_MN...")

# First check what PROD_MN values exist
print("\n    All distinct PROD_MN values in partition:")
df.select("PROD_MN").distinct().orderBy("PROD_MN").show(100, truncate=False)

# Filter using PROD_MN (the mnemonic field)
df_vvd = df.filter(col("PROD_MN").isin(VVD_MNEMONICS))
vvd_count = df_vvd.count()
print(f"\n    VVD records (filtered by PROD_MN): {vvd_count:,}")

if vvd_count == 0:
    print("\n    WARNING: No VVD records found with mnemonics:", VVD_MNEMONICS)
    print("    Check the PROD_MN values above - mnemonics might be different")

# -----------------------------------------------------------------------------
# STEP 4: JSON FIELD (TREATMT_ADNL_DTL) ANALYSIS
# -----------------------------------------------------------------------------

print("\n[4] Analyzing TREATMT_ADNL_DTL (JSON field)...")

if "TREATMT_ADNL_DTL" in df.columns and vvd_count > 0:

    json_stats = df_vvd.agg(
        count("*").alias("total_records"),
        count(when(col("TREATMT_ADNL_DTL").isNotNull(), 1)).alias("json_not_null"),
        count(when(
            (col("TREATMT_ADNL_DTL").isNotNull()) &
            (trim(col("TREATMT_ADNL_DTL")) != ""), 1
        )).alias("json_not_empty"),
        countDistinct("TREATMT_ADNL_DTL").alias("distinct_values")
    ).collect()[0]

    print(f"    Total VVD records:    {json_stats['total_records']:,}")
    print(f"    JSON NOT NULL:        {json_stats['json_not_null']:,}")
    print(f"    JSON NOT EMPTY:       {json_stats['json_not_empty']:,}")
    print(f"    Distinct values:      {json_stats['distinct_values']:,}")

    # Sample values
    print("\n    Sample JSON values:")
    print("    " + "-" * 70)

    df_vvd.filter(
        (col("TREATMT_ADNL_DTL").isNotNull()) &
        (trim(col("TREATMT_ADNL_DTL")) != "")
    ).select(
        "TACTIC_ID",
        "TREATMT_ADNL_DTL"
    ).distinct().show(20, truncate=False)

    # Check for expected JSON structure
    print("\n    Checking for JSON structure markers...")

    df_json_markers = df_vvd.filter(col("TREATMT_ADNL_DTL").isNotNull()).agg(
        count("*").alias("total"),
        count(when(col("TREATMT_ADNL_DTL").contains("{"), 1)).alias("has_brace"),
        count(when(col("TREATMT_ADNL_DTL").contains("Experiments"), 1)).alias("has_Experiments"),
        count(when(col("TREATMT_ADNL_DTL").contains("type"), 1)).alias("has_type"),
        count(when(col("TREATMT_ADNL_DTL").contains("Test"), 1)).alias("has_Test"),
        count(when(col("TREATMT_ADNL_DTL").contains("Control"), 1)).alias("has_Control")
    ).collect()[0]

    print(f"    Contains '{{':           {df_json_markers['has_brace']:,}")
    print(f"    Contains 'Experiments':  {df_json_markers['has_Experiments']:,}")
    print(f"    Contains 'type':         {df_json_markers['has_type']:,}")
    print(f"    Contains 'Test':         {df_json_markers['has_Test']:,}")
    print(f"    Contains 'Control':      {df_json_markers['has_Control']:,}")

elif "TREATMT_ADNL_DTL" not in df.columns:
    print("    ERROR: TREATMT_ADNL_DTL field not found!")
    print("    Available columns:", df.columns)

# -----------------------------------------------------------------------------
# STEP 5: 150-BYTE FIELD (TREATMT_DTL) ANALYSIS
# -----------------------------------------------------------------------------

print("\n[5] Analyzing TREATMT_DTL (150-byte field)...")

if "TREATMT_DTL" in df.columns and vvd_count > 0:

    dtl_stats = df_vvd.agg(
        count(when(col("TREATMT_DTL").isNotNull(), 1)).alias("not_null"),
        count(when(
            (col("TREATMT_DTL").isNotNull()) &
            (trim(col("TREATMT_DTL")) != ""), 1
        )).alias("not_empty"),
        countDistinct("TREATMT_DTL").alias("distinct")
    ).collect()[0]

    print(f"    NOT NULL:  {dtl_stats['not_null']:,}")
    print(f"    NOT EMPTY: {dtl_stats['not_empty']:,}")
    print(f"    Distinct:  {dtl_stats['distinct']:,}")

    print("\n    Distinct TREATMT_DTL values:")
    df_vvd.filter(col("TREATMT_DTL").isNotNull()).select(
        "TREATMT_DTL"
    ).distinct().show(30, truncate=False)

# -----------------------------------------------------------------------------
# STEP 6: BREAKDOWN BY CAMPAIGN
# -----------------------------------------------------------------------------

print("\n[6] Field population by campaign (PROD_MN)...")

if vvd_count > 0:
    df_vvd.groupBy("PROD_MN").agg(
        count("*").alias("total"),
        count(when(col("TREATMT_ADNL_DTL").isNotNull(), 1)).alias("json_filled"),
        count(when(col("TREATMT_DTL").isNotNull(), 1)).alias("dtl_filled")
    ).orderBy("PROD_MN").show()

# -----------------------------------------------------------------------------
# STEP 7: SAMPLE RECORDS
# -----------------------------------------------------------------------------

print("\n[7] Sample complete records...")

if vvd_count > 0:
    sample_cols = [c for c in ["PROD_MN", "TACTIC_ID", "CLNT_ID", "CHNL_CD",
                                "TREATMT_ADNL_DTL", "TREATMT_DTL",
                                "OFFR_STRT_DT"] if c in df.columns]

    df_vvd.select(sample_cols).show(5, truncate=False)

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
