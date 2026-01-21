# =============================================================================
# TACTIC EVENT HISTORY - Flexible Fields Diagnostic
# =============================================================================
# Purpose: Investigate the addnl_decisn_data1/2/3 fields and other metadata
#          fields in the tactic_evnt_hist table for VVD campaigns
#
# Goal: Understand what experiment metadata is available so we can leverage
#       it for vintage curve building without hardcoding
# =============================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, lit, length,
    when, trim, lower, substring
)

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

# Tactic Event History table
TACTIC_TABLE = "prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist"

# Alternative: If Hive table doesn't work, try parquet path
# TACTIC_PATH = "/prod/yg80/..."  # Update if needed

# VVD campaign prefixes
VVD_PREFIXES = ['VCN', 'VDA', 'VDT', 'VUI', 'VUT', 'VAW']

# -----------------------------------------------------------------------------
# INITIALIZE SPARK
# -----------------------------------------------------------------------------

spark = SparkSession.builder \
    .appName("Tactic Event History Diagnostic") \
    .enableHiveSupport() \
    .getOrCreate()

print("=" * 80)
print("TACTIC EVENT HISTORY - FLEXIBLE FIELDS DIAGNOSTIC")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA
# -----------------------------------------------------------------------------

print("\n[1] Loading Tactic Event History data...")

try:
    df = spark.table(TACTIC_TABLE)
    print(f"    Loaded from Hive table: {TACTIC_TABLE}")
except Exception as e:
    print(f"    ERROR loading Hive table: {e}")
    print("    Try updating TACTIC_PATH and using spark.read.parquet()")
    raise

# Get record count (sample if very large)
total_count = df.count()
print(f"    Total records: {total_count:,}")

# -----------------------------------------------------------------------------
# STEP 2: FILTER FOR VVD CAMPAIGNS
# -----------------------------------------------------------------------------

print("\n[2] Filtering for VVD campaigns...")

# Build filter for VVD prefixes
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
    print("\n    WARNING: No VVD records found!")
    print("    Checking what tactic_id values exist...")
    df.select("tactic_id").distinct().orderBy("tactic_id").show(100, truncate=False)

# -----------------------------------------------------------------------------
# STEP 3: EXAMINE LAYER 1 KEY FIELDS
# -----------------------------------------------------------------------------

print("\n[3] Layer 1 Key Fields Analysis...")

layer1_fields = [
    "tactic_id",
    "rpt_grp_cd",       # Report Group Code - segment
    "tst_grp_cd",       # Test Group Code - test vs control
    "treatmt_mn",       # Treatment Mnemonic
    "treatmt_strt_dt",  # Treatment Start Date
    "treatmt_end_dt",   # Treatment End Date
    "tactic_cell_cd",   # Tactic Cell Code
]

existing_l1 = [f for f in layer1_fields if f in df.columns]
print(f"    Layer 1 fields found: {existing_l1}")

# Show distinct values for each
for field in existing_l1:
    if field != "treatmt_strt_dt" and field != "treatmt_end_dt":
        print(f"\n    --- {field} ---")
        df_vvd.groupBy(field).agg(
            count("*").alias("count")
        ).orderBy(col("count").desc()).show(20, truncate=False)

# -----------------------------------------------------------------------------
# STEP 4: FLEXIBLE FIELDS (addnl_decisn_data1/2/3) ANALYSIS
# -----------------------------------------------------------------------------

print("\n[4] Analyzing FLEXIBLE FIELDS (addnl_decisn_data1/2/3)...")

flexible_fields = ["addnl_decisn_data1", "addnl_decisn_data2", "addnl_decisn_data3"]
existing_flex = [f for f in flexible_fields if f in df.columns]

print(f"    Flexible fields found: {existing_flex}")

for field in existing_flex:
    print(f"\n    === {field} ===")

    # Stats
    stats = df_vvd.select(
        count("*").alias("total"),
        count(when(col(field).isNotNull(), 1)).alias("not_null"),
        count(when(trim(col(field)) != "", 1)).alias("not_empty"),
        countDistinct(field).alias("distinct")
    ).collect()[0]

    print(f"    NOT NULL:  {stats['not_null']:,} / {stats['total']:,}")
    print(f"    NOT EMPTY: {stats['not_empty']:,}")
    print(f"    Distinct:  {stats['distinct']:,}")

    # Check if JSON-like
    json_check = df_vvd.filter(col(field).isNotNull()).select(
        count(when(col(field).contains("{"), 1)).alias("has_brace"),
        count(when(col(field).contains("Experiment"), 1)).alias("has_experiment"),
        count(when(col(field).contains("Test"), 1)).alias("has_test")
    ).collect()[0]

    print(f"    Contains '{{':         {json_check['has_brace']:,}")
    print(f"    Contains 'Experiment': {json_check['has_experiment']:,}")
    print(f"    Contains 'Test':       {json_check['has_test']:,}")

    # Sample values
    print(f"\n    Sample {field} values:")
    df_vvd.filter(
        (col(field).isNotNull()) &
        (trim(col(field)) != "")
    ).select(
        "tactic_id",
        field
    ).distinct().show(15, truncate=100)

# -----------------------------------------------------------------------------
# STEP 5: TEST GROUP ANALYSIS
# -----------------------------------------------------------------------------

print("\n[5] Test Group (tst_grp_cd) Analysis...")

if "tst_grp_cd" in df.columns:
    print("\n    Test Group codes by campaign:")
    df_vvd.withColumn(
        "campaign", substring("tactic_id", 1, 3)
    ).groupBy("campaign", "tst_grp_cd").agg(
        count("*").alias("count")
    ).orderBy("campaign", "tst_grp_cd").show(50)

    # Which is Test vs Control?
    print("\n    Is TG4 always the Test group? Check distribution:")
    df_vvd.groupBy("tst_grp_cd").agg(
        count("*").alias("total"),
        countDistinct("tactic_evnt_id").alias("unique_clients")
    ).orderBy("tst_grp_cd").show()

# -----------------------------------------------------------------------------
# STEP 6: REPORT GROUP (SEGMENT) ANALYSIS
# -----------------------------------------------------------------------------

print("\n[6] Report Group (rpt_grp_cd) Analysis - SEGMENTS...")

if "rpt_grp_cd" in df.columns:
    print("\n    Report Group codes by campaign:")
    df_vvd.withColumn(
        "campaign", substring("tactic_id", 1, 3)
    ).groupBy("campaign", "rpt_grp_cd").agg(
        count("*").alias("count")
    ).orderBy("campaign", "rpt_grp_cd").show(50)

# -----------------------------------------------------------------------------
# STEP 7: CHANNEL ANALYSIS
# -----------------------------------------------------------------------------

print("\n[7] Channel Analysis...")

# Check for channel-related fields
channel_fields = [f for f in df.columns if 'chnl' in f.lower() or 'channel' in f.lower()]
print(f"    Channel-related fields: {channel_fields}")

for field in channel_fields[:3]:  # First 3 channel fields
    print(f"\n    --- {field} by campaign ---")
    df_vvd.withColumn(
        "campaign", substring("tactic_id", 1, 3)
    ).groupBy("campaign", field).agg(
        count("*").alias("count")
    ).orderBy("campaign", field).show(30)

# -----------------------------------------------------------------------------
# STEP 8: DATE RANGE ANALYSIS
# -----------------------------------------------------------------------------

print("\n[8] Treatment Date Ranges...")

if "treatmt_strt_dt" in df.columns:
    df_vvd.withColumn(
        "campaign", substring("tactic_id", 1, 3)
    ).groupBy("campaign").agg(
        count("*").alias("records"),
        col("treatmt_strt_dt").cast("string").alias("min_start"),  # workaround
        col("treatmt_strt_dt").cast("string").alias("max_start")
    ).show()

    # Better approach - use SQL
    df_vvd.createOrReplaceTempView("vvd_tactic")
    spark.sql("""
        SELECT
            SUBSTRING(tactic_id, 1, 3) as campaign,
            COUNT(*) as records,
            MIN(treatmt_strt_dt) as earliest_treatment,
            MAX(treatmt_strt_dt) as latest_treatment
        FROM vvd_tactic
        GROUP BY SUBSTRING(tactic_id, 1, 3)
        ORDER BY campaign
    """).show()

# -----------------------------------------------------------------------------
# STEP 9: FULL SAMPLE WITH ALL KEY FIELDS
# -----------------------------------------------------------------------------

print("\n[9] Full sample records...")
print("=" * 80)

sample_fields = [
    "tactic_id", "tactic_evnt_id", "rpt_grp_cd", "tst_grp_cd",
    "treatmt_mn", "treatmt_strt_dt",
    "addnl_decisn_data1", "addnl_decisn_data2"
]
sample_fields = [f for f in sample_fields if f in df.columns]

df_vvd.select(sample_fields).show(10, truncate=50)

# -----------------------------------------------------------------------------
# STEP 10: SCHEMA REFERENCE
# -----------------------------------------------------------------------------

print("\n[10] Full schema for reference:")
print("=" * 80)
df.printSchema()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print("""
NEXT STEPS:
1. If addnl_decisn_data fields contain useful metadata -> parse them
2. If treatmt_adnl_dtl (ODS) has JSON experiment info -> parse it
3. If neither has structured data -> need to hardcode from design docs
""")
