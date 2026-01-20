"""
Tactic Loader Module
====================

Loads campaign population data from the tactic table.
The tactic table contains client assignments to campaigns, test groups,
treatment dates, and segmentation fields.

Source Table: DTZTA_T_TACTIC_EVNT_HIST (via parquet)
Reference: Success Library Layer 1 - Governed Experiment Metadata
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

from ..config.base_config import YEARS_TO_INCLUDE, COHORT_DATE_FORMAT, TEST_GROUP_CODE
from ..config.paths import TACTIC_PARQUET_PATH


def load_tactic(
    spark: SparkSession,
    mne: str,
    years: list = None,
    tactic_path: str = None
) -> DataFrame:
    """
    Load tactic data for a specific campaign (MNE).

    This function:
    1. Reads the tactic parquet file
    2. Filters by MNE and year
    3. Adds derived columns (WINDOW_DAYS, GROUP, COHORT)

    Args:
        spark: Active SparkSession
        mne: Campaign mnemonic (e.g., "VCN")
        years: List of years to include (default: from base_config)
        tactic_path: Path to tactic parquet (default: from paths config)

    Returns:
        DataFrame with tactic data filtered and enriched

    Columns Added:
        - WINDOW_DAYS: Measurement window (TREATMT_END_DT - TREATMT_STRT_DT)
        - GROUP: "TEST" if TST_GRP_CD == 'TG4', else "CONTROL"
        - COHORT: Treatment start date formatted as yyyy-MM
    """
    # Use defaults from config if not specified
    years = years or YEARS_TO_INCLUDE
    tactic_path = tactic_path or TACTIC_PARQUET_PATH

    # Load parquet
    tactic = spark.read.parquet(tactic_path)

    # Filter by MNE and years
    tactic = tactic.filter(
        (F.col("MNE") == mne) &
        (F.year(F.col("TREATMT_STRT_DT")).isin(years))
    )

    # Add derived columns
    tactic = tactic.withColumn(
        "WINDOW_DAYS",
        F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT"))
    ).withColumn(
        "GROUP",
        F.when(F.col("TST_GRP_CD") == TEST_GROUP_CODE, "TEST").otherwise("CONTROL")
    ).withColumn(
        "COHORT",
        F.date_format(F.col("TREATMT_STRT_DT"), COHORT_DATE_FORMAT)
    )

    return tactic


def load_tactic_for_campaigns(
    spark: SparkSession,
    mnes: list,
    years: list = None,
    tactic_path: str = None
) -> DataFrame:
    """
    Load tactic data for multiple campaigns.

    Args:
        spark: Active SparkSession
        mnes: List of campaign mnemonics
        years: List of years to include
        tactic_path: Path to tactic parquet

    Returns:
        DataFrame with tactic data for all specified MNEs
    """
    years = years or YEARS_TO_INCLUDE
    tactic_path = tactic_path or TACTIC_PARQUET_PATH

    tactic = spark.read.parquet(tactic_path)

    tactic = tactic.filter(
        (F.col("MNE").isin(mnes)) &
        (F.year(F.col("TREATMT_STRT_DT")).isin(years))
    )

    # Add derived columns
    tactic = tactic.withColumn(
        "WINDOW_DAYS",
        F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT"))
    ).withColumn(
        "GROUP",
        F.when(F.col("TST_GRP_CD") == TEST_GROUP_CODE, "TEST").otherwise("CONTROL")
    ).withColumn(
        "COHORT",
        F.date_format(F.col("TREATMT_STRT_DT"), COHORT_DATE_FORMAT)
    )

    return tactic


def get_tactic_columns() -> list:
    """
    Return the standard tactic columns expected in the data.

    These are the key fields from DTZTA_T_TACTIC_EVNT_HIST.
    """
    return [
        "CLNT_NO",
        "TACTIC_ID",
        "TREATMT_STRT_DT",
        "TREATMT_END_DT",
        "TREATMT_EFF_DT",
        "MNE",
        "CAMPAIGN_NAME",
        "CHANNEL",
        "TST_GRP_CD",
        "TST_GRP_EFF_DT",
        "RPT_GRP_CD",       # Reporting group - for segmentation
        "RPT_GRP_EFF_DT",
        "TACTIC_CELL_CD",   # Tactic cell - for experiment design
        "STRTGY_SRC_CD",    # Strategy source
        "TRGT_TYP_CD",      # Target type
    ]


def validate_tactic_data(tactic_df: DataFrame) -> dict:
    """
    Validate tactic data and return summary statistics.

    Args:
        tactic_df: Tactic DataFrame to validate

    Returns:
        Dictionary with validation results
    """
    total_records = tactic_df.count()

    if total_records == 0:
        return {
            "valid": False,
            "total_records": 0,
            "error": "No records found"
        }

    # Check for required columns
    required_cols = ["CLNT_NO", "TREATMT_STRT_DT", "TREATMT_END_DT", "TST_GRP_CD"]
    missing_cols = [col for col in required_cols if col not in tactic_df.columns]

    # Get group distribution
    group_counts = tactic_df.groupBy("GROUP").count().collect()
    group_dist = {row["GROUP"]: row["count"] for row in group_counts}

    # Get cohort count
    cohort_count = tactic_df.select("COHORT").distinct().count()

    return {
        "valid": len(missing_cols) == 0,
        "total_records": total_records,
        "missing_columns": missing_cols,
        "group_distribution": group_dist,
        "cohort_count": cohort_count
    }
