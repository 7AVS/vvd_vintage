# =============================================================================
# SIMPLE TEST - Does ods_hist table exist and can we read it?
# =============================================================================

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ODS HIST Simple Test") \
    .enableHiveSupport() \
    .getOrCreate()

TABLE = "prod_x610_crm.ods_hist"

print("=" * 60)
print("SIMPLE TEST: Can we access ods_hist?")
print("=" * 60)

# Test 1: Does the table exist?
print("\n[1] Checking if table exists...")
try:
    tables = spark.sql("SHOW TABLES IN prod_x610_crm LIKE 'ods_hist'")
    tables.show()
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2: Can we get the schema?
print("\n[2] Getting schema (DESCRIBE)...")
try:
    schema = spark.sql(f"DESCRIBE {TABLE}")
    schema.show(50, truncate=False)
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3: Can we read just 10 rows? (no filter)
print("\n[3] Reading 10 rows (no filter)...")
try:
    df = spark.sql(f"SELECT * FROM {TABLE} LIMIT 10")
    print(f"    Columns: {df.columns}")
    df.show(5, truncate=50)
except Exception as e:
    print(f"    ERROR: {e}")

# Test 4: What partitions exist?
print("\n[4] Checking partitions...")
try:
    partitions = spark.sql(f"SHOW PARTITIONS {TABLE}")
    partitions.show(20, truncate=False)
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
