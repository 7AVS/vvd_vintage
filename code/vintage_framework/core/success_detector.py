"""
Success Detector Module
=======================

Joins tactic data with success data to detect campaign conversions.
This is the core attribution logic that determines which clients
achieved success within their measurement window.

Reference: Success Library Layer 3 - Centralized Logic Repo
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def detect_success(
    tactic_df: DataFrame,
    success_df: DataFrame,
    config: dict
) -> DataFrame:
    """
    Join tactic with success table to detect conversions.

    Logic:
    1. Left join tactic to success on CLNT_NO
    2. Filter success events within measurement window (TREATMT_STRT_DT to TREATMT_END_DT)
    3. Calculate days to success
    4. Aggregate to client-deployment level

    Args:
        tactic_df: Tactic DataFrame with population (must have WINDOW_DAYS, GROUP, COHORT)
        success_df: Success DataFrame with conversion events
        config: Campaign configuration dictionary

    Returns:
        DataFrame with one row per client-deployment, including:
        - All tactic columns
        - SUCCESS_FLAG: 1 if client converted, 0 otherwise
        - FIRST_SUCCESS_DT: Date of first success (if any)
        - DAYS_TO_FIRST_SUCCESS: Days from treatment start to first success
        - SUCCESS_COUNT: Total successes in window
    """
    # Get all tactic columns for grouping
    tactic_columns = tactic_df.columns

    # Ensure derived columns exist
    required_cols = ["WINDOW_DAYS", "GROUP", "COHORT"]
    for col in required_cols:
        if col not in tactic_columns:
            raise ValueError(f"Tactic DataFrame missing required column: {col}")

    # Alias for join
    tactic_alias = tactic_df.alias("t")

    # Prepare success table with standardized column names
    success_date_field = config["success_date_field"]
    success_select = success_df.select(
        F.col("CLNT_NO").alias("SUCCESS_CLNT_NO"),
        F.col(success_date_field).alias("SUCCESS_DT")
    ).alias("s")

    # Left join - success within measurement window
    joined = tactic_alias.join(
        success_select,
        (F.col("t.CLNT_NO") == F.col("s.SUCCESS_CLNT_NO")) &
        (F.col("s.SUCCESS_DT") >= F.col("t.TREATMT_STRT_DT")) &
        (F.col("s.SUCCESS_DT") <= F.col("t.TREATMT_END_DT")),
        how="left"
    )

    # Calculate days to success
    joined = joined.withColumn(
        "DAYS_TO_SUCCESS",
        F.when(
            F.col("s.SUCCESS_DT").isNotNull(),
            F.datediff(F.col("s.SUCCESS_DT"), F.col("t.TREATMT_STRT_DT"))
        ).otherwise(None)
    )

    # Aggregate to client-deployment level
    # Group by all tactic columns plus derived columns
    groupby_cols = [f"t.{col}" for col in tactic_columns if col not in required_cols]
    groupby_cols.extend(["t.WINDOW_DAYS", "t.GROUP", "t.COHORT"])

    # Also preserve the derived columns from tactic
    for col in required_cols:
        if f"t.{col}" not in groupby_cols:
            groupby_cols.append(f"t.{col}")

    result = joined.groupBy(groupby_cols).agg(
        # SUCCESS_FLAG: 1 if any success, 0 otherwise
        F.max(
            F.when(F.col("s.SUCCESS_DT").isNotNull(), 1).otherwise(0)
        ).alias("SUCCESS_FLAG"),

        # First success date
        F.min("s.SUCCESS_DT").alias("FIRST_SUCCESS_DT"),

        # Days to first success
        F.min("DAYS_TO_SUCCESS").alias("DAYS_TO_FIRST_SUCCESS"),

        # Count of successes in window (for volume analysis)
        F.count("s.SUCCESS_DT").alias("SUCCESS_COUNT")
    )

    # Clean up column names (remove "t." prefix)
    for col in result.columns:
        if col.startswith("t."):
            result = result.withColumnRenamed(col, col[2:])

    return result


def get_success_summary(success_df: DataFrame) -> DataFrame:
    """
    Generate summary statistics for success detection results.

    Args:
        success_df: Result from detect_success()

    Returns:
        DataFrame with summary by GROUP
    """
    return success_df.groupBy("GROUP").agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.sum("SUCCESS_FLAG").alias("TOTAL_SUCCESSES"),
        F.avg("SUCCESS_FLAG").alias("SUCCESS_RATE"),
        F.avg(
            F.when(F.col("SUCCESS_FLAG") == 1, F.col("DAYS_TO_FIRST_SUCCESS"))
        ).alias("AVG_DAYS_TO_SUCCESS")
    )


def get_success_summary_by_cohort(success_df: DataFrame) -> DataFrame:
    """
    Generate summary statistics by COHORT and GROUP.

    Args:
        success_df: Result from detect_success()

    Returns:
        DataFrame with summary by COHORT and GROUP
    """
    return success_df.groupBy("COHORT", "GROUP").agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.sum("SUCCESS_FLAG").alias("TOTAL_SUCCESSES"),
        F.avg("SUCCESS_FLAG").alias("SUCCESS_RATE"),
        F.avg(
            F.when(F.col("SUCCESS_FLAG") == 1, F.col("DAYS_TO_FIRST_SUCCESS"))
        ).alias("AVG_DAYS_TO_SUCCESS"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("MEDIAN_WINDOW_DAYS")
    ).orderBy("COHORT", "GROUP")


def validate_success_detection(success_df: DataFrame) -> dict:
    """
    Validate success detection results.

    Args:
        success_df: Result from detect_success()

    Returns:
        Dictionary with validation results
    """
    total = success_df.count()

    if total == 0:
        return {
            "valid": False,
            "error": "No records after success detection"
        }

    # Check for both TEST and CONTROL groups
    groups = [row["GROUP"] for row in success_df.select("GROUP").distinct().collect()]

    # Get basic stats
    stats = success_df.agg(
        F.sum("SUCCESS_FLAG").alias("total_successes"),
        F.avg("SUCCESS_FLAG").alias("overall_rate")
    ).collect()[0]

    return {
        "valid": True,
        "total_records": total,
        "groups_present": groups,
        "has_test_and_control": "TEST" in groups and "CONTROL" in groups,
        "total_successes": int(stats["total_successes"]) if stats["total_successes"] else 0,
        "overall_success_rate": float(stats["overall_rate"]) if stats["overall_rate"] else 0
    }
