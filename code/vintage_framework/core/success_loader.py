"""
Success Loader Module
=====================

Loads success data from various sources (HIVE, EDW) based on campaign configuration.
Applies appropriate filters for each success type.

Source Tables:
- DDWTA_VISA_DR_CRD: Card issuance/activation data
- DDWTA_T_PT_OF_SALE_TXN: Transaction data
- Token parquet: Pre-pulled tokenization data from EDW

Reference: Success Library Layer 3 - Centralized Logic Repo
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

from ..config.base_config import YEARS_TO_INCLUDE
from ..config.paths import get_success_table_path


def load_success_table(
    spark: SparkSession,
    config: dict,
    years: list = None
) -> DataFrame:
    """
    Load success table based on campaign configuration.

    This function dynamically routes to the appropriate loader
    based on the success_source in the config.

    Args:
        spark: Active SparkSession
        config: Campaign configuration dictionary
        years: List of years to include (for HIVE sources)

    Returns:
        DataFrame with success data, filtered and enriched
    """
    source = config.get("success_source", "HIVE")

    if source == "HIVE":
        return _load_success_table_hive(spark, config, years)
    elif source == "EDW":
        return _load_success_table_edw(spark, config)
    else:
        raise ValueError(f"Unknown success source: {source}")


def _load_success_table_hive(
    spark: SparkSession,
    config: dict,
    years: list = None
) -> DataFrame:
    """
    Load success table from HIVE with year partitions.

    Applies filters based on success type:
    - ACQUISITION/ACTIVATION: STS_CD, SRVC_ID, ISS_DT not null
    - USAGE: SRVC_CD, TXN_TYPES, AMT1 > 0
    """
    years = years or YEARS_TO_INCLUDE
    years_str = [str(y) for y in years]

    # Build paths for year partitions
    base_path = config["success_table_path"]
    paths = get_success_table_path(base_path, years_str)

    # Read parquet
    df = spark.read.parquet(*paths)

    # Apply filters
    df = _apply_filters(df, config)

    # Add Card_Type for ACQUISITION/ACTIVATION
    if config["success_type"] in ["ACQUISITION", "ACTIVATION"]:
        df = df.withColumn(
            "Card_Type",
            F.when(F.col("VISA_DR_CRD_BRND_CD") == "03", "Digital")
            .otherwise("Hybrid/Plastic")
        )

    return df


def _load_success_table_edw(
    spark: SparkSession,
    config: dict
) -> DataFrame:
    """
    Load pre-pulled success data from EDW (parquet format).

    Used for TOKENIZATION campaigns where data is pre-extracted
    from EDW tables (DDWV05.CLNT_CRD_POS_LOG + DL_DECMAN.TOKEN_LIST).
    """
    path = config["success_table_path"]
    return spark.read.parquet(path)


def _apply_filters(df: DataFrame, config: dict) -> DataFrame:
    """
    Apply filters to success DataFrame based on campaign configuration.

    Supports various filter operators:
    - eq: equals
    - in: in list
    - gt: greater than
    - not_null: is not null
    - or: OR combination of conditions (for complex filters)
    """
    filters = config.get("filters")

    if not filters:
        return df

    for field, filter_spec in filters.items():
        # Skip special complex filters (handled separately)
        if field == "TXN_TYPES":
            df = _apply_txn_type_filter(df, filter_spec)
            continue

        operator = filter_spec.get("operator")
        value = filter_spec.get("value")

        if operator == "eq":
            df = df.filter(F.col(field) == value)
        elif operator == "in":
            df = df.filter(F.col(field).isin(value))
        elif operator == "gt":
            df = df.filter(F.col(field) > value)
        elif operator == "not_null":
            df = df.filter(F.col(field).isNotNull())

    # Handle client ID extraction (for USAGE table)
    if config.get("client_id_extraction"):
        df = _extract_client_id(df, config["client_id_extraction"])

    return df


def _apply_txn_type_filter(df: DataFrame, filter_spec: dict) -> DataFrame:
    """
    Apply complex TXN_TYPE filter for USAGE success.

    This handles the OR combination of TXN_TP + MSG_TP conditions
    that define valid purchase transactions.
    """
    conditions = filter_spec.get("conditions", [])

    if not conditions:
        return df

    combined_condition = None

    for cond in conditions:
        # Each condition is a dict of field: {operator, value}
        field_conditions = []
        for field, spec in cond.items():
            op = spec.get("operator")
            val = spec.get("value")
            if op == "eq":
                field_conditions.append(F.col(field) == val)

        # AND all fields in this condition
        if field_conditions:
            this_condition = field_conditions[0]
            for fc in field_conditions[1:]:
                this_condition = this_condition & fc

            # OR with previous conditions
            if combined_condition is None:
                combined_condition = this_condition
            else:
                combined_condition = combined_condition | this_condition

    if combined_condition is not None:
        df = df.filter(combined_condition)

    return df


def _extract_client_id(df: DataFrame, extraction_config: dict) -> DataFrame:
    """
    Extract CLNT_NO from source field (used for USAGE table).

    The USAGE table stores client ID in CLNT_CRD_NO field,
    requiring substring extraction and leading zero removal.
    """
    source_field = extraction_config["source_field"]
    method = extraction_config.get("method")

    if method == "substring_strip":
        start = extraction_config["start"]
        length = extraction_config["length"]

        df = df.withColumn(
            "CLNT_NO",
            F.regexp_replace(
                F.substring(F.col(source_field), start, length),
                "^0+",
                ""
            )
        )

        # Also extract POS_MODE for additional analysis
        df = df.withColumn(
            "POS_MODE",
            F.substring(F.col("POS_ENTRY_MODE_CD_NON_EMV"), 1, 2)
        )

    return df


def get_success_date_field(config: dict) -> str:
    """Get the success date field from campaign configuration."""
    return config.get("success_date_field", "SUCCESS_DT")


def validate_success_data(success_df: DataFrame, config: dict) -> dict:
    """
    Validate success data and return summary statistics.

    Args:
        success_df: Success DataFrame to validate
        config: Campaign configuration

    Returns:
        Dictionary with validation results
    """
    total_records = success_df.count()

    if total_records == 0:
        return {
            "valid": False,
            "total_records": 0,
            "error": "No records found"
        }

    success_date_field = config["success_date_field"]

    # Check if success date field exists
    if success_date_field not in success_df.columns:
        return {
            "valid": False,
            "total_records": total_records,
            "error": f"Success date field '{success_date_field}' not found"
        }

    # Get date range
    date_range = success_df.agg(
        F.min(success_date_field).alias("min_date"),
        F.max(success_date_field).alias("max_date")
    ).collect()[0]

    return {
        "valid": True,
        "total_records": total_records,
        "success_date_field": success_date_field,
        "date_range": {
            "min": str(date_range["min_date"]),
            "max": str(date_range["max_date"])
        }
    }
