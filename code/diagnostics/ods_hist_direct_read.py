# =============================================================================
# ODS HIST - Direct Parquet Read (bypassing broken Hive table)
# =============================================================================
# The Hive table has backup folders causing conflicts.
# We read directly from a specific effectDate partition.
# =============================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, trim, length, avg, max as spark_max, countDistinct

spark = SparkSession.builder \
    .appName("ODS HIST Direct Read") \
    .enableHiveSupport() \
    .getOrCreate()

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

# Base path (from the error message we can see the structure)
BASE_PATH = "/prod/01347/app/ls20/data/sparkjobdata"

# Pick a specific effectDate partition (adjust as needed)
EFFECTDATE = "2025-11-01"

# Full path to one partition
PARTITION_PATH = f"{BASE_PATH}/effectDate={EFFECTDATE}"

# Campaign filter
VVD_MNEMONICS = ['VDA']

print("=" * 70)
print("ODS HIST - DIRECT PARQUET READ")
print(f"Path: {PARTITION_PATH}")
print("=" * 70)

# -----------------------------------------------------------------------------
# STEP 1: READ FROM SPECIFIC PARTITION
# -----------------------------------------------------------------------------

print("\n[1] Reading from partition...")

try:
    df = spark.read.parquet(PARTITION_PATH)
    record_count = df.count()
    print(f"    SUCCESS! Records: {record_count:,}")
except Exception as e:
    print(f"    ERROR: {e}")
    print("\n    Let's try to find valid partitions...")

    # List directories to find valid effectDate partitions
    try:
        # Use spark to list files
        from subprocess import run, PIPE
        result = run(['hdfs', 'dfs', '-ls', BASE_PATH], capture_output=True, text=True, timeout=30)

        print("\n    Directories found (excluding odsbackup):")
        for line in result.stdout.split('\n'):
            if 'effectDate=' in line and 'odsbackup' not in line.lower():
                path = line.split()[-1] if line.split() else ''
                print(f"      {path}")
    except Exception as e2:
        print(f"    Could not list directories: {e2}")

    raise SystemExit("Cannot read data - check partition path")

# -----------------------------------------------------------------------------
# STEP 2: SHOW SCHEMA
# -----------------------------------------------------------------------------

print("\n[2] Schema:")
for c in df.columns:
    print(f"      - {c}")

# -----------------------------------------------------------------------------
# STEP 3: FILTER FOR VVD
# -----------------------------------------------------------------------------

print("\n[3] Filtering for VVD campaigns...")

# Find the prod_mn/prod_nm column (schema showed prod_nm)
prod_col = None
for c in df.columns:
    if c.lower() in ['prod_mn', 'prod_nm']:
        prod_col = c
        break

if prod_col:
    print(f"    Using column: {prod_col}")
    print(f"\n    Distinct {prod_col} values:")
    df.select(prod_col).distinct().orderBy(prod_col).show(50, truncate=False)

    df_vvd = df.filter(col(prod_col).isin(VVD_MNEMONICS))
    vvd_count = df_vvd.count()
    print(f"\n    VVD records: {vvd_count:,}")
else:
    print("    WARNING: prod_mn/prod_nm column not found")
    vvd_count = 0
    df_vvd = df

# -----------------------------------------------------------------------------
# STEP 4: JSON FIELD ANALYSIS (treatmt_adnl_dtl)
# -----------------------------------------------------------------------------

print("\n[4] Analyzing treatmt_adnl_dtl (JSON field)...")

# Find the JSON field
json_col = None
for c in df.columns:
    if c.lower() == 'treatmt_adnl_dtl':
        json_col = c
        break

if json_col and vvd_count > 0:
    stats = df_vvd.agg(
        count("*").alias("total"),
        count(when(col(json_col).isNotNull(), 1)).alias("not_null"),
        count(when(
            (col(json_col).isNotNull()) & (trim(col(json_col)) != ""), 1
        )).alias("not_empty"),
        countDistinct(json_col).alias("distinct")
    ).collect()[0]

    print(f"    Total:       {stats['total']:,}")
    print(f"    NOT NULL:    {stats['not_null']:,}")
    print(f"    NOT EMPTY:   {stats['not_empty']:,}")
    print(f"    Distinct:    {stats['distinct']:,}")

    if stats['not_empty'] > 0:
        # Length stats
        len_stats = df_vvd.filter(
            (col(json_col).isNotNull()) & (trim(col(json_col)) != "")
        ).agg(
            avg(length(col(json_col))).alias("avg_len"),
            spark_max(length(col(json_col))).alias("max_len")
        ).collect()[0]

        print(f"    Avg length:  {len_stats['avg_len']:.0f} chars")
        print(f"    Max length:  {len_stats['max_len']} chars")

        # Check for JSON markers
        markers = df_vvd.filter(col(json_col).isNotNull()).agg(
            count(when(col(json_col).contains("{"), 1)).alias("has_brace"),
            count(when(col(json_col).contains("Experiment"), 1)).alias("has_experiment"),
            count(when(col(json_col).contains("Test"), 1)).alias("has_test"),
            count(when(col(json_col).contains("Control"), 1)).alias("has_control")
        ).collect()[0]

        print(f"\n    Contains '{{':        {markers['has_brace']:,}")
        print(f"    Contains 'Experiment': {markers['has_experiment']:,}")
        print(f"    Contains 'Test':       {markers['has_test']:,}")
        print(f"    Contains 'Control':    {markers['has_control']:,}")

        # Sample content
        print("\n    Sample JSON content:")
        df_vvd.filter(
            (col(json_col).isNotNull()) & (trim(col(json_col)) != "")
        ).select(json_col).distinct().show(10, truncate=False)

elif json_col and vvd_count == 0:
    print("    No VVD records to analyze")
else:
    print("    ERROR: treatmt_adnl_dtl column not found")

# -----------------------------------------------------------------------------
# STEP 5: SAMPLE RECORDS
# -----------------------------------------------------------------------------

print("\n[5] Sample records...")

sample_cols = [c for c in df.columns if c.lower() in
               ['prod_mn', 'prod_nm', 'tactic_id', 'treatmt_adnl_dtl', 'treatmt_dtl']]

if sample_cols:
    df_vvd.select(sample_cols).show(10, truncate=100)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
