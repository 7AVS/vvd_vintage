# =============================================================================
# TACTIC EVENT HISTORY - Flexible Fields Diagnostic
# =============================================================================
# Purpose: Investigate the addnl_decisn_data1/2/3 fields and Layer 1 metadata
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
    "tactic_id", "tactic_evnt_id",
    "rpt_grp_cd", "tst_grp_cd", "treatmt_mn",
    "treatmt_strt_dt", "treatmt_end_dt",
    "tactic_cell_cd"
]

flexible_fields = ["addnl_decisn_data1", "addnl_decisn_data2", "addnl_decisn_data3"]

all_key_fields = layer1_fields + flexible_fields
existing = [f for f in all_key_fields if f in df.columns]
missing = [f for f in all_key_fields if f not in df.columns]

print(f"    Found: {existing}")
if missing:
    print(f"    MISSING: {missing}")

# -----------------------------------------------------------------------------
# STEP 3: FILTER FOR VVD CAMPAIGNS
# -----------------------------------------------------------------------------

print("\n[3] Filtering for VVD campaigns (last 3 chars of tactic_id)...")

# First show sample tactic_id values to understand the format
print("\n    Sample tactic_id values:")
df.select("tactic_id").distinct().orderBy("tactic_id").show(30, truncate=False)

# Filter by last 3 characters using endswith
vvd_filter = None
for mnemonic in VVD_MNEMONICS:
    condition = col("tactic_id").endswith(mnemonic)
    vvd_filter = condition if vvd_filter is None else (vvd_filter | condition)

df_vvd = df.filter(vvd_filter)
vvd_count = df_vvd.count()
print(f"\n    VVD records (filtered by last 3 chars): {vvd_count:,}")

if vvd_count == 0:
    print("\n    WARNING: No VVD records found!")
    print("    Check the tactic_id format above - mnemonics might be in different position")

# -----------------------------------------------------------------------------
# STEP 4: FLEXIBLE FIELDS ANALYSIS (addnl_decisn_data1/2/3)
# -----------------------------------------------------------------------------

print("\n[4] Analyzing FLEXIBLE FIELDS (addnl_decisn_data1/2/3)...")

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

    # Test Group (tst_grp_cd)
    if "tst_grp_cd" in df.columns:
        print("\n    --- tst_grp_cd (Test vs Control) ---")
        df_vvd.groupBy("tst_grp_cd").agg(
            count("*").alias("count")
        ).orderBy(col("count").desc()).show(20)

    # Report Group (rpt_grp_cd)
    if "rpt_grp_cd" in df.columns:
        print("\n    --- rpt_grp_cd (Segments) ---")
        df_vvd.groupBy("rpt_grp_cd").agg(
            count("*").alias("count")
        ).orderBy(col("count").desc()).show(20)

    # Treatment Mnemonic
    if "treatmt_mn" in df.columns:
        print("\n    --- treatmt_mn (Treatment) ---")
        df_vvd.groupBy("treatmt_mn").agg(
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

    if "tst_grp_cd" in df.columns:
        agg_cols.append(countDistinct("tst_grp_cd").alias("tst_grps"))
    if "rpt_grp_cd" in df.columns:
        agg_cols.append(countDistinct("rpt_grp_cd").alias("rpt_grps"))

    df_vvd.withColumn(
        "campaign", expr("right(tactic_id, 3)")
    ).groupBy("campaign").agg(*agg_cols).orderBy("campaign").show()

# -----------------------------------------------------------------------------
# STEP 7: CROSS-TAB: CAMPAIGN x TEST GROUP
# -----------------------------------------------------------------------------

print("\n[7] Campaign x Test Group cross-tab...")

if vvd_count > 0 and "tst_grp_cd" in df.columns:
    df_vvd.withColumn(
        "campaign", expr("right(tactic_id, 3)")
    ).groupBy("campaign", "tst_grp_cd").agg(
        count("*").alias("count")
    ).orderBy("campaign", "tst_grp_cd").show(50)

# -----------------------------------------------------------------------------
# STEP 8: DATE RANGES
# -----------------------------------------------------------------------------

print("\n[8] Treatment date ranges by campaign...")

if vvd_count > 0 and "treatmt_strt_dt" in df.columns:
    df_vvd.withColumn(
        "campaign", expr("right(tactic_id, 3)")
    ).groupBy("campaign").agg(
        count("*").alias("records"),
        spark_min("treatmt_strt_dt").alias("earliest"),
        spark_max("treatmt_strt_dt").alias("latest")
    ).orderBy("campaign").show()

# -----------------------------------------------------------------------------
# STEP 9: SAMPLE RECORDS
# -----------------------------------------------------------------------------

print("\n[9] Sample complete records...")

if vvd_count > 0:
    sample_cols = [c for c in [
        "tactic_id", "tactic_evnt_id", "tst_grp_cd", "rpt_grp_cd",
        "treatmt_mn", "treatmt_strt_dt",
        "addnl_decisn_data1", "addnl_decisn_data2"
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
2. What tst_grp_cd values exist? (Which is Test vs Control?)
3. What rpt_grp_cd values exist? (Segment codes)
4. Is there any JSON structure in the flexible fields?
""")
