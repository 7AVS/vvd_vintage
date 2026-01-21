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

# ODS MR HIST - Use specific partition date
# Format: /prod/01347/app/LS20/data/SparkJobData/effectDate=YYYY-MM-DD
PARTITION_DATE = "2026-01-20"  # UPDATE THIS to latest available date
ODS_PATH = f"/prod/01347/app/LS20/data/SparkJobData/effectDate={PARTITION_DATE}"

# VVD campaign prefixes to filter for
VVD_PREFIXES = ['VCN', 'VDA', 'VDT', 'VUI', 'VUT', 'VAW']

# -----------------------------------------------------------------------------
# INITIALIZE SPARK
# -----------------------------------------------------------------------------

spark = SparkSession.builder \
    .appName("ODS JSON Field Diagnostic") \
    .getOrCreate()

print("=" * 80)
print("ODS MR HIST - JSON FIELD DIAGNOSTIC")
print(f"Partition: effectDate={PARTITION_DATE}")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA FROM SPECIFIC PARTITION
# -----------------------------------------------------------------------------

print("\n[1] Loading ODS MR HIST data from partition...")
print(f"    Path: {ODS_PATH}")

try:
    df = spark.read.parquet(ODS_PATH)
    record_count = df.count()
    print(f"    Records in partition: {record_count:,}")
except Exception as e:
    print(f"    ERROR: {e}")
    print("\n    Trying to list available partitions...")
    # Try to list what partitions exist
    try:
        import subprocess
        result = subprocess.run(['hdfs', 'dfs', '-ls', '/prod/01347/app/LS20/data/SparkJobData/'],
                                capture_output=True, text=True)
        print(result.stdout[-2000:])  # Last 2000 chars
    except:
        print("    Could not list partitions. Check the path manually.")
    raise

# -----------------------------------------------------------------------------
# STEP 2: CHECK SCHEMA - What fields exist?
# -----------------------------------------------------------------------------

print("\n[2] Checking schema for key fields...")

key_fields = [
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
# STEP 3: FILTER FOR VVD CAMPAIGNS
# -----------------------------------------------------------------------------

print("\n[3] Filtering for VVD campaigns...")

# Build filter for VVD prefixes
vvd_filter = None
for prefix in VVD_PREFIXES:
    condition = col("tactic_id").startswith(prefix)
    vvd_filter = condition if vvd_filter is None else (vvd_filter | condition)

df_vvd = df.filter(vvd_filter)
vvd_count = df_vvd.count()
print(f"    VVD records: {vvd_count:,}")

if vvd_count == 0:
    print("\n    WARNING: No VVD records found with standard prefixes!")
    print("    Showing sample tactic_id values from this partition:")
    df.select("tactic_id").distinct().orderBy("tactic_id").show(50, truncate=False)

    # Try broader search
    print("\n    Trying broader search for 'V' prefix or 'VVD' anywhere...")
    df_v = df.filter(col("tactic_id").startswith("V"))
    print(f"    Records starting with 'V': {df_v.count():,}")
    df_v.select("tactic_id").distinct().show(30, truncate=False)

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

print("\n[6] Field population by campaign...")

if vvd_count > 0:
    df_vvd.withColumn(
        "campaign", substring("tactic_id", 1, 3)
    ).groupBy("campaign").agg(
        count("*").alias("total"),
        count(when(col("treatmt_adnl_dtl").isNotNull(), 1)).alias("json_filled"),
        count(when(col("treatmt_dtl").isNotNull(), 1)).alias("dtl_filled")
    ).orderBy("campaign").show()

# -----------------------------------------------------------------------------
# STEP 7: SAMPLE RECORDS
# -----------------------------------------------------------------------------

print("\n[7] Sample complete records...")

if vvd_count > 0:
    sample_cols = [c for c in ["tactic_id", "clnt_id", "chnl_cd",
                                "treatmt_adnl_dtl", "treatmt_dtl",
                                "offr_strt_dt"] if c in df.columns]

    df_vvd.select(sample_cols).show(5, truncate=False)

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
