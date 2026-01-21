# =============================================================================
# TACTIC EVENT HISTORY - Flexible Fields Diagnostic
# =============================================================================
# Purpose: Investigate the ADDNL_DECISN_DATA1/2/3 fields and Layer 1 metadata
#          in tactic_evnt_hist for VVD campaigns
#
# IMPORTANT: Uses partition filtering - UPDATE PARTITION CONFIG BELOW
# =============================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, lit, length,
    when, trim, lower, substring, min as spark_min, max as spark_max, expr
)

# -----------------------------------------------------------------------------
# CONFIGURATION - UPDATE THESE VALUES
# -----------------------------------------------------------------------------

# Tactic Event History - Hive table
HIVE_TABLE = "prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist"

# Partition filter - NARROW RANGE for one deployment
PARTITION_COLUMN = "evnt_strt_dt"
PARTITION_START = "2025-10-01"  # Adjust based on known deployment
PARTITION_END = "2025-12-31"    # Narrow window

# Focus on ONE campaign for diagnostic (change as needed)
VVD_MNEMONICS = ['VDA']  # VDA = Black Friday / Cyber Monday

# -----------------------------------------------------------------------------
# INITIALIZE SPARK
# -----------------------------------------------------------------------------

spark = SparkSession.builder \
    .appName("Tactic Event History Diagnostic") \
    .enableHiveSupport() \
    .getOrCreate()

print("=" * 80)
print("TACTIC EVENT HISTORY - FLEXIBLE FIELDS DIAGNOSTIC")
print(f"Partition filter: {PARTITION_COLUMN} BETWEEN {PARTITION_START} AND {PARTITION_END}")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA WITH PARTITION FILTER
# -----------------------------------------------------------------------------

print("\n[1] Loading data with partition filter...")
print(f"    Table: {HIVE_TABLE}")
print(f"    Filter: {PARTITION_COLUMN} BETWEEN '{PARTITION_START}' AND '{PARTITION_END}'")

df = spark.table(HIVE_TABLE) \
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

print("\n    Checking for expected key fields...")

layer1_fields = [
    "TACTIC_ID", "TACTIC_EVNT_ID",
    "RPT_GRP_CD", "TST_GRP_CD", "TREATMT_MN",
    "TREATMT_STRT_DT", "TREATMT_END_DT",
    "TACTIC_CELL_CD"
]

flexible_fields = ["ADDNL_DECISN_DATA1", "ADDNL_DECISN_DATA2", "ADDNL_DECISN_DATA3"]

all_key_fields = layer1_fields + flexible_fields
existing = [f for f in all_key_fields if f in df.columns]
missing = [f for f in all_key_fields if f not in df.columns]

print(f"    Found: {existing}")
if missing:
    print(f"    MISSING: {missing}")

# -----------------------------------------------------------------------------
# STEP 3: FILTER FOR VVD CAMPAIGNS
# -----------------------------------------------------------------------------

print("\n[3] Filtering for VVD campaigns (last 3 chars of TACTIC_ID)...")

# First show sample TACTIC_ID values to understand the format
print("\n    Sample TACTIC_ID values:")
df.select("TACTIC_ID").distinct().orderBy("TACTIC_ID").show(50, truncate=False)

# Filter by last 3 characters using endswith
vvd_filter = None
for mnemonic in VVD_MNEMONICS:
    condition = col("TACTIC_ID").endswith(mnemonic)
    vvd_filter = condition if vvd_filter is None else (vvd_filter | condition)

df_vvd = df.filter(vvd_filter)
vvd_count = df_vvd.count()
print(f"\n    VVD records (filtered by last 3 chars): {vvd_count:,}")

if vvd_count == 0:
    print("\n    WARNING: No VVD records found!")
    print("    Check the TACTIC_ID format above - mnemonics might be in different position")

# -----------------------------------------------------------------------------
# STEP 4: FLEXIBLE FIELDS ANALYSIS (ADDNL_DECISN_DATA1/2/3)
# -----------------------------------------------------------------------------

print("\n[4] Analyzing FLEXIBLE FIELDS (ADDNL_DECISN_DATA1/2/3)...")

existing_flex = [f for f in flexible_fields if f in df.columns]
print(f"    Fields found: {existing_flex}")

for field in existing_flex:
    print(f"\n    === {field} ===")

    if vvd_count > 0:
        stats = df_vvd.agg(
            count("*").alias("total"),
            count(when(col(field).isNotNull(), 1)).alias("not_null"),
            count(when(
                (col(field).isNotNull()) &
                (trim(col(field)) != ""), 1
            )).alias("not_empty"),
            countDistinct(field).alias("distinct")
        ).collect()[0]

        print(f"    Total:     {stats['total']:,}")
        print(f"    NOT NULL:  {stats['not_null']:,}")
        print(f"    NOT EMPTY: {stats['not_empty']:,}")
        print(f"    Distinct:  {stats['distinct']:,}")

        # Check for JSON-like content
        if stats['not_null'] > 0:
            json_check = df_vvd.filter(col(field).isNotNull()).agg(
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
        ).select("tactic_id", field).distinct().show(15, truncate=100)

# -----------------------------------------------------------------------------
# STEP 5: LAYER 1 KEY FIELDS ANALYSIS
# -----------------------------------------------------------------------------

print("\n[5] Layer 1 Key Fields Analysis...")

if vvd_count > 0:

    # Test Group (TST_GRP_CD)
    if "TST_GRP_CD" in df.columns:
        print("\n    --- TST_GRP_CD (Test vs Control) ---")
        df_vvd.groupBy("TST_GRP_CD").agg(
            count("*").alias("count")
        ).orderBy(col("count").desc()).show(20)

    # Report Group (RPT_GRP_CD)
    if "RPT_GRP_CD" in df.columns:
        print("\n    --- RPT_GRP_CD (Segments) ---")
        df_vvd.groupBy("RPT_GRP_CD").agg(
            count("*").alias("count")
        ).orderBy(col("count").desc()).show(20)

    # Treatment Mnemonic
    if "TREATMT_MN" in df.columns:
        print("\n    --- TREATMT_MN (Treatment) ---")
        df_vvd.groupBy("TREATMT_MN").agg(
            count("*").alias("count")
        ).orderBy(col("count").desc()).show(20)

# -----------------------------------------------------------------------------
# STEP 6: BREAKDOWN BY CAMPAIGN
# -----------------------------------------------------------------------------

print("\n[6] Breakdown by VVD campaign...")

if vvd_count > 0:
    agg_cols = [count("*").alias("total")]

    for field in existing_flex:
        agg_cols.append(
            count(when(col(field).isNotNull(), 1)).alias(f"{field[:10]}_filled")
        )

    if "TST_GRP_CD" in df.columns:
        agg_cols.append(countDistinct("TST_GRP_CD").alias("tst_grps"))
    if "RPT_GRP_CD" in df.columns:
        agg_cols.append(countDistinct("RPT_GRP_CD").alias("rpt_grps"))

    df_vvd.withColumn(
        "campaign", expr("right(TACTIC_ID, 3)")
    ).groupBy("campaign").agg(*agg_cols).orderBy("campaign").show()

# -----------------------------------------------------------------------------
# STEP 7: CROSS-TAB: CAMPAIGN x TEST GROUP
# -----------------------------------------------------------------------------

print("\n[7] Campaign x Test Group cross-tab...")

if vvd_count > 0 and "TST_GRP_CD" in df.columns:
    df_vvd.withColumn(
        "campaign", expr("right(TACTIC_ID, 3)")
    ).groupBy("campaign", "TST_GRP_CD").agg(
        count("*").alias("count")
    ).orderBy("campaign", "TST_GRP_CD").show(50)

# -----------------------------------------------------------------------------
# STEP 8: DATE RANGES
# -----------------------------------------------------------------------------

print("\n[8] Treatment date ranges by campaign...")

if vvd_count > 0 and "TREATMT_STRT_DT" in df.columns:
    df_vvd.withColumn(
        "campaign", expr("right(TACTIC_ID, 3)")
    ).groupBy("campaign").agg(
        count("*").alias("records"),
        spark_min("TREATMT_STRT_DT").alias("earliest"),
        spark_max("TREATMT_STRT_DT").alias("latest")
    ).orderBy("campaign").show()

# -----------------------------------------------------------------------------
# STEP 9: SAMPLE RECORDS
# -----------------------------------------------------------------------------

print("\n[9] Sample complete records...")

if vvd_count > 0:
    sample_cols = [c for c in [
        "TACTIC_ID", "TACTIC_EVNT_ID", "TST_GRP_CD", "RPT_GRP_CD",
        "TREATMT_MN", "TREATMT_STRT_DT",
        "ADDNL_DECISN_DATA1", "ADDNL_DECISN_DATA2"
    ] if c in df.columns]

    df_vvd.select(sample_cols).show(10, truncate=50)

# -----------------------------------------------------------------------------
# STEP 10: SCHEMA
# -----------------------------------------------------------------------------

print("\n[10] Full schema:")
print("=" * 80)
df.printSchema()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print("""
KEY FINDINGS TO LOOK FOR:
1. Are addnl_decisn_data fields populated with experiment metadata?
2. What TST_GRP_CD values exist? (Which is Test vs Control?)
3. What RPT_GRP_CD values exist? (Segment codes)
4. Is there any JSON structure in the flexible fields?
""")
