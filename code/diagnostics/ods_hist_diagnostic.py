# =============================================================================
# ODS HIST - JSON Field Diagnostic
# =============================================================================
# Purpose: Investigate the ODS_HIST table for experiment metadata
#          Focus on the large varchar fields:
#          - TREATMT_ADNL_DTL (varchar 8000) - JSON field
#          - TREATMT_DTL (varchar 4000) - Treatment detail
# =============================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, lit, length, avg, max as spark_max,
    when, trim, lower, substring, get_json_object, expr
)

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

HIVE_DATABASE = "prod_x610_crm"
HIVE_TABLE = "ods_hist"

# Partition filter
PARTITION_COLUMN = "effectdate"
PARTITION_START = "2025-10-01"
PARTITION_END = "2025-12-31"

# Campaign filter
VVD_MNEMONICS = ['VDA']

# -----------------------------------------------------------------------------
# INITIALIZE SPARK
# -----------------------------------------------------------------------------

spark = SparkSession.builder \
    .appName("ODS HIST JSON Diagnostic") \
    .enableHiveSupport() \
    .getOrCreate()

print("=" * 80)
print("ODS HIST - JSON FIELD DIAGNOSTIC")
print(f"Table: {HIVE_DATABASE}.{HIVE_TABLE}")
print(f"Filter: {PARTITION_COLUMN} BETWEEN '{PARTITION_START}' AND '{PARTITION_END}'")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD DATA - BYPASS HIVE TABLE, READ PARQUET DIRECTLY
# -----------------------------------------------------------------------------

print("\n[1] Loading data...")

# The Hive table has backup folders causing conflicts
# So we read the parquet files directly from a specific partition
# Path format: /prod/01347/app/ls20/data/sparkjobdata/effectDate=YYYY-MM-DD

# Try reading directly from parquet path with specific partition
PARQUET_BASE_PATH = "/prod/01347/app/ls20/data/sparkjobdata"

# Read a specific partition to avoid the backup folder issue
# Using a single recent date first to test
TEST_PARTITION = "2025-11-01"  # Adjust if needed
PARQUET_PATH = f"{PARQUET_BASE_PATH}/effectDate={TEST_PARTITION}"

print(f"    Reading directly from: {PARQUET_PATH}")
print(f"    (Bypassing Hive table due to backup folder conflicts)")

try:
    df = spark.read.parquet(PARQUET_PATH)
    record_count = df.count()
    print(f"    Records: {record_count:,}")
except Exception as e:
    print(f"    ERROR reading parquet: {e}")
    print("\n    Trying alternative: list available partitions...")

    # Try to list what effectDate partitions exist (excluding odsbackup)
    try:
        import subprocess
        result = subprocess.run(
            ['hdfs', 'dfs', '-ls', PARQUET_BASE_PATH],
            capture_output=True, text=True, timeout=30
        )
        print("\n    Available directories:")
        for line in result.stdout.split('\n'):
            if 'effectDate=' in line and 'odsbackup' not in line:
                print(f"      {line.split()[-1] if line.split() else ''}")
    except:
        pass
    raise

# -----------------------------------------------------------------------------
# STEP 2: SHOW ACTUAL SCHEMA
# -----------------------------------------------------------------------------

print("\n[2] Actual columns in table:")
for c in df.columns:
    print(f"      - {c}")

# Identify the JSON field name (could be uppercase or lowercase)
json_field = None
dtl_field = None
prod_field = None

for c in df.columns:
    if c.upper() == "TREATMT_ADNL_DTL":
        json_field = c
    if c.upper() == "TREATMT_DTL":
        dtl_field = c
    if c.upper() == "PROD_MN":
        prod_field = c

print(f"\n    JSON field found as: {json_field}")
print(f"    DTL field found as: {dtl_field}")
print(f"    PROD_MN field found as: {prod_field}")

# -----------------------------------------------------------------------------
# STEP 3: FILTER FOR VVD
# -----------------------------------------------------------------------------

print("\n[3] Filtering for VVD campaigns...")

if prod_field:
    print(f"\n    Distinct {prod_field} values:")
    df.select(prod_field).distinct().orderBy(prod_field).show(100, truncate=False)

    df_vvd = df.filter(col(prod_field).isin(VVD_MNEMONICS))
    vvd_count = df_vvd.count()
    print(f"\n    VVD records: {vvd_count:,}")
else:
    print("    WARNING: PROD_MN field not found!")
    vvd_count = 0
    df_vvd = df.limit(0)

# -----------------------------------------------------------------------------
# STEP 4: JSON FIELD ANALYSIS (TREATMT_ADNL_DTL - varchar 8000)
# -----------------------------------------------------------------------------

print("\n[4] Analyzing JSON field (TREATMT_ADNL_DTL - varchar 8000)...")

if json_field and vvd_count > 0:

    # Basic stats
    json_stats = df_vvd.agg(
        count("*").alias("total"),
        count(when(col(json_field).isNotNull(), 1)).alias("not_null"),
        count(when(
            (col(json_field).isNotNull()) &
            (trim(col(json_field)) != ""), 1
        )).alias("not_empty"),
        countDistinct(json_field).alias("distinct")
    ).collect()[0]

    print(f"    Total records:     {json_stats['total']:,}")
    print(f"    NOT NULL:          {json_stats['not_null']:,}")
    print(f"    NOT EMPTY:         {json_stats['not_empty']:,}")
    print(f"    Distinct values:   {json_stats['distinct']:,}")

    # Field length analysis (how much of 8000 chars is used?)
    if json_stats['not_empty'] > 0:
        len_stats = df_vvd.filter(
            (col(json_field).isNotNull()) &
            (trim(col(json_field)) != "")
        ).agg(
            avg(length(col(json_field))).alias("avg_len"),
            spark_max(length(col(json_field))).alias("max_len")
        ).collect()[0]

        print(f"\n    Average length:    {len_stats['avg_len']:.0f} chars")
        print(f"    Max length:        {len_stats['max_len']} chars (out of 8000)")

    # Check for JSON markers
    print("\n    Checking for JSON structure...")

    markers = df_vvd.filter(col(json_field).isNotNull()).agg(
        count(when(col(json_field).contains("{"), 1)).alias("has_brace"),
        count(when(col(json_field).contains("["), 1)).alias("has_bracket"),
        count(when(col(json_field).contains("Experiments"), 1)).alias("has_Experiments"),
        count(when(col(json_field).contains("type"), 1)).alias("has_type"),
        count(when(col(json_field).contains("Test"), 1)).alias("has_Test"),
        count(when(col(json_field).contains("Control"), 1)).alias("has_Control"),
        count(when(col(json_field).contains("metric"), 1)).alias("has_metric")
    ).collect()[0]

    print(f"    Contains '{{':           {markers['has_brace']:,}")
    print(f"    Contains '[':            {markers['has_bracket']:,}")
    print(f"    Contains 'Experiments':  {markers['has_Experiments']:,}")
    print(f"    Contains 'type':         {markers['has_type']:,}")
    print(f"    Contains 'Test':         {markers['has_Test']:,}")
    print(f"    Contains 'Control':      {markers['has_Control']:,}")
    print(f"    Contains 'metric':       {markers['has_metric']:,}")

    # Show sample JSON content
    print("\n    Sample JSON content (first 20 non-empty):")
    print("    " + "-" * 70)

    df_vvd.filter(
        (col(json_field).isNotNull()) &
        (trim(col(json_field)) != "")
    ).select(json_field).distinct().show(20, truncate=False)

    # If it looks like JSON, try to extract keys
    if markers['has_brace'] > 0:
        print("\n    Attempting to parse as JSON...")
        print("    Trying to extract common keys: 'Experiments', 'type', 'test_group'")

        try:
            df_vvd.filter(col(json_field).contains("{")).select(
                col(json_field),
                get_json_object(col(json_field), "$.Experiments").alias("Experiments"),
                get_json_object(col(json_field), "$.type").alias("type"),
                get_json_object(col(json_field), "$.test_group").alias("test_group")
            ).filter(
                col("Experiments").isNotNull() |
                col("type").isNotNull() |
                col("test_group").isNotNull()
            ).show(10, truncate=False)
        except Exception as e:
            print(f"    JSON parsing failed: {e}")

elif not json_field:
    print("    ERROR: TREATMT_ADNL_DTL field not found in table!")

# -----------------------------------------------------------------------------
# STEP 5: TREATMENT DETAIL FIELD (TREATMT_DTL - varchar 4000)
# -----------------------------------------------------------------------------

print("\n[5] Analyzing TREATMT_DTL field (varchar 4000)...")

if dtl_field and vvd_count > 0:

    dtl_stats = df_vvd.agg(
        count(when(col(dtl_field).isNotNull(), 1)).alias("not_null"),
        count(when(
            (col(dtl_field).isNotNull()) &
            (trim(col(dtl_field)) != ""), 1
        )).alias("not_empty"),
        countDistinct(dtl_field).alias("distinct")
    ).collect()[0]

    print(f"    NOT NULL:          {dtl_stats['not_null']:,}")
    print(f"    NOT EMPTY:         {dtl_stats['not_empty']:,}")
    print(f"    Distinct values:   {dtl_stats['distinct']:,}")

    if dtl_stats['not_empty'] > 0:
        len_stats = df_vvd.filter(
            (col(dtl_field).isNotNull()) &
            (trim(col(dtl_field)) != "")
        ).agg(
            avg(length(col(dtl_field))).alias("avg_len"),
            spark_max(length(col(dtl_field))).alias("max_len")
        ).collect()[0]

        print(f"    Average length:    {len_stats['avg_len']:.0f} chars")
        print(f"    Max length:        {len_stats['max_len']} chars (out of 4000)")

    print("\n    Sample TREATMT_DTL values:")
    df_vvd.filter(col(dtl_field).isNotNull()).select(
        dtl_field
    ).distinct().show(20, truncate=False)

# -----------------------------------------------------------------------------
# STEP 6: COMBINED VIEW - All treatment fields
# -----------------------------------------------------------------------------

print("\n[6] Combined view of treatment fields...")

if vvd_count > 0:
    sample_cols = []
    for c in [prod_field, "TACTIC_ID", "tactic_id", json_field, dtl_field]:
        if c and c in df.columns:
            sample_cols.append(c)

    if sample_cols:
        df_vvd.select(sample_cols).show(10, truncate=100)

# -----------------------------------------------------------------------------
# STEP 7: SCHEMA PRINTOUT
# -----------------------------------------------------------------------------

print("\n[7] Full schema for reference:")
df.printSchema()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print("""
WHAT TO LOOK FOR:
1. Is TREATMT_ADNL_DTL populated? (not_empty > 0)
2. Does it contain JSON? (has_brace > 0)
3. What keys are in the JSON? (Experiments, type, Test, Control)
4. How much of the 8000 char capacity is used?
5. Is TREATMT_DTL (4000 char) also useful?
""")
