# =============================================================================
# ODS MR HIST - JSON Field Diagnostic
# =============================================================================
# Purpose: Investigate what's in the treatmt_adnl_dtl (JSON) field
#          and the treatmt_dtl (150-byte) fields for VVD campaigns
#
# Goal: Understand if experiment metadata is already populated so we can
#       parse it instead of hardcoding lookups
# =============================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, lit, length,
    when, isnotnull, trim, lower, substring
)

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

# ODS MR HIST table path (use latest partition - update date as needed)
ODS_PATH = "/prod/01347/app/LS20/data/SparkJobData/effectDate=2026-01-20"

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
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA
# -----------------------------------------------------------------------------

print("\n[1] Loading ODS MR HIST data...")
df = spark.read.parquet(ODS_PATH)
print(f"    Total records in partition: {df.count():,}")

# -----------------------------------------------------------------------------
# STEP 2: FILTER FOR VVD CAMPAIGNS
# -----------------------------------------------------------------------------

print("\n[2] Filtering for VVD campaigns...")

# Build filter condition for VVD prefixes
vvd_filter = None
for prefix in VVD_PREFIXES:
    condition = col("tactic_id").startswith(prefix)
    if vvd_filter is None:
        vvd_filter = condition
    else:
        vvd_filter = vvd_filter | condition

df_vvd = df.filter(vvd_filter)
vvd_count = df_vvd.count()
print(f"    VVD records found: {vvd_count:,}")

if vvd_count == 0:
    print("\n    WARNING: No VVD records found with prefixes: ", VVD_PREFIXES)
    print("    Let's check what tactic_id values exist...")
    df.select("tactic_id").distinct().show(50, truncate=False)
    # Try alternative - look for 'VVD' anywhere in tactic_id
    df_vvd_alt = df.filter(col("tactic_id").contains("VVD") | col("tactic_id").contains("vvd"))
    print(f"    Records containing 'VVD': {df_vvd_alt.count():,}")

# -----------------------------------------------------------------------------
# STEP 3: EXAMINE THE KEY FIELDS
# -----------------------------------------------------------------------------

print("\n[3] Examining treatment detail fields...")

# Select the key fields we care about
key_fields = [
    "tactic_id",
    "clnt_id",
    "chnl_cd",
    "treatmt_adnl_dtl",   # THE JSON FIELD
    "treatmt_dtl",        # 150 byte field
    "treatmt_dtl_en",     # English
    "treatmt_dtl_fr",     # French
    "offr_strt_dt",
    "offr_end_dt"
]

# Check which fields exist in the dataframe
existing_fields = [f for f in key_fields if f in df.columns]
missing_fields = [f for f in key_fields if f not in df.columns]

print(f"    Fields found: {existing_fields}")
if missing_fields:
    print(f"    Fields MISSING: {missing_fields}")

# -----------------------------------------------------------------------------
# STEP 4: JSON FIELD (treatmt_adnl_dtl) ANALYSIS
# -----------------------------------------------------------------------------

print("\n[4] Analyzing treatmt_adnl_dtl (JSON field)...")

if "treatmt_adnl_dtl" in df.columns:
    # Overall population stats
    json_stats = df_vvd.select(
        count("*").alias("total_records"),
        count(when(col("treatmt_adnl_dtl").isNotNull(), 1)).alias("json_not_null"),
        count(when(trim(col("treatmt_adnl_dtl")) != "", 1)).alias("json_not_empty"),
        countDistinct("treatmt_adnl_dtl").alias("distinct_json_values")
    ).collect()[0]

    print(f"    Total VVD records:        {json_stats['total_records']:,}")
    print(f"    JSON field NOT NULL:      {json_stats['json_not_null']:,}")
    print(f"    JSON field NOT EMPTY:     {json_stats['json_not_empty']:,}")
    print(f"    Distinct JSON values:     {json_stats['distinct_json_values']:,}")

    # Show sample JSON values
    print("\n    Sample JSON values (first 20):")
    print("    " + "-" * 70)

    df_vvd.filter(
        (col("treatmt_adnl_dtl").isNotNull()) &
        (trim(col("treatmt_adnl_dtl")) != "")
    ).select(
        "tactic_id",
        "treatmt_adnl_dtl"
    ).distinct().show(20, truncate=100)

    # Check JSON structure - does it contain expected keys?
    print("\n    Checking for expected JSON keys ('Experiments', 'type', etc.)...")

    df_json_check = df_vvd.filter(col("treatmt_adnl_dtl").isNotNull()).select(
        count("*").alias("total"),
        count(when(col("treatmt_adnl_dtl").contains("Experiments"), 1)).alias("has_Experiments"),
        count(when(col("treatmt_adnl_dtl").contains("type"), 1)).alias("has_type"),
        count(when(col("treatmt_adnl_dtl").contains("Test"), 1)).alias("has_Test"),
        count(when(col("treatmt_adnl_dtl").contains("Control"), 1)).alias("has_Control"),
        count(when(col("treatmt_adnl_dtl").contains("{"), 1)).alias("has_json_brace")
    ).collect()[0]

    print(f"    Records with 'Experiments': {df_json_check['has_Experiments']:,}")
    print(f"    Records with 'type':        {df_json_check['has_type']:,}")
    print(f"    Records with 'Test':        {df_json_check['has_Test']:,}")
    print(f"    Records with 'Control':     {df_json_check['has_Control']:,}")
    print(f"    Records with '{{':          {df_json_check['has_json_brace']:,}")

else:
    print("    ERROR: treatmt_adnl_dtl field not found in schema!")

# -----------------------------------------------------------------------------
# STEP 5: 150-BYTE FIELDS ANALYSIS
# -----------------------------------------------------------------------------

print("\n[5] Analyzing treatmt_dtl (150-byte field)...")

if "treatmt_dtl" in df.columns:
    dtl_stats = df_vvd.select(
        count("*").alias("total"),
        count(when(col("treatmt_dtl").isNotNull(), 1)).alias("not_null"),
        count(when(trim(col("treatmt_dtl")) != "", 1)).alias("not_empty"),
        countDistinct("treatmt_dtl").alias("distinct_values")
    ).collect()[0]

    print(f"    Records NOT NULL:     {dtl_stats['not_null']:,}")
    print(f"    Records NOT EMPTY:    {dtl_stats['not_empty']:,}")
    print(f"    Distinct values:      {dtl_stats['distinct_values']:,}")

    # Show distinct values
    print("\n    Distinct treatmt_dtl values:")
    print("    " + "-" * 70)
    df_vvd.filter(col("treatmt_dtl").isNotNull()).select(
        "treatmt_dtl"
    ).distinct().show(30, truncate=150)

# -----------------------------------------------------------------------------
# STEP 6: BREAKDOWN BY CAMPAIGN
# -----------------------------------------------------------------------------

print("\n[6] JSON field population by campaign...")

df_vvd.withColumn(
    "campaign", substring("tactic_id", 1, 3)
).groupBy("campaign").agg(
    count("*").alias("total_records"),
    count(when(col("treatmt_adnl_dtl").isNotNull(), 1)).alias("json_populated"),
    count(when(col("treatmt_dtl").isNotNull(), 1)).alias("dtl_populated")
).orderBy("campaign").show()

# -----------------------------------------------------------------------------
# STEP 7: FULL SAMPLE OUTPUT
# -----------------------------------------------------------------------------

print("\n[7] Full sample records with all treatment fields...")
print("=" * 80)

# Get a few complete records to see everything
sample_fields = ["tactic_id", "clnt_id", "chnl_cd", "treatmt_adnl_dtl", "treatmt_dtl", "offr_strt_dt"]
sample_fields = [f for f in sample_fields if f in df.columns]

df_vvd.filter(
    col("treatmt_adnl_dtl").isNotNull()
).select(sample_fields).show(10, truncate=False)

# -----------------------------------------------------------------------------
# STEP 8: SCHEMA REFERENCE
# -----------------------------------------------------------------------------

print("\n[8] Full schema for reference:")
print("=" * 80)
df.printSchema()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
