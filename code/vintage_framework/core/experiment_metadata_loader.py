"""
Experiment Metadata Loader Module
=================================

[WORK IN PROGRESS]

This module extracts experiment design metadata from tactic and ODS data.
It enables discovery of campaign structure (segments, test groups, etc.)
without hardcoding.

Reference: Success Library Layer 1 - Governed Experiment Metadata Semantic Layer

Data Sources:
- Tactic Table (DTZTA_T_TACTIC_EVNT_HIST):
  - RPT_GRP_CD: Reporting group code (custom segmentation)
  - TACTIC_CELL_CD: Tactic cell code
  - STRTGY_SRC_CD: Strategy source code
  - TRGT_TYP_CD: Target type code

- ODS Table (ed10_im.prod_x610_crm.ods_mr_hist):
  - Additional Detail: JSON field with experiment configuration
  - Treatment Detail: Treatment specifics

Future Integration:
- When upstream layers (Layer 1, Layer 2) are built, this module
  will pull from governed metadata repositories instead of raw data.
- Tags and segment definitions will come from campaign configuration
  artifacts, not inferred from data.

Current Status:
- Discovery mode: Introspect available data to understand structure
- Manual validation required
- See diagnostics/ for investigation scripts
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from typing import Dict, Any, Optional


def discover_campaign_structure(
    tactic_df: DataFrame,
    mne: str
) -> Dict[str, Any]:
    """
    Introspect tactic data to discover experiment design.

    This function analyzes the tactic data to understand:
    - What test groups exist (beyond just TG4)
    - What segments are defined (RPT_GRP_CD)
    - What tactic cells are used (TACTIC_CELL_CD)
    - Distribution of clients across these dimensions

    [WIP] This is a discovery tool. In the future, this information
    should come from governed metadata, not inferred from data.

    Args:
        tactic_df: Tactic DataFrame (already filtered by MNE)
        mne: Campaign mnemonic

    Returns:
        Dictionary with discovered campaign structure:
        - mne: Campaign code
        - total_clients: Total clients in campaign
        - test_groups: DataFrame with test group distribution
        - segments: DataFrame with segment distribution (RPT_GRP_CD)
        - tactic_cells: DataFrame with tactic cell distribution
        - cohorts: DataFrame with cohort distribution
        - channels: DataFrame with channel distribution
        - window_days: DataFrame with measurement window distribution
    """
    total_clients = tactic_df.count()

    if total_clients == 0:
        return {
            "mne": mne,
            "total_clients": 0,
            "error": "No data found for this campaign"
        }

    # Discover test groups
    test_groups = tactic_df.groupBy("TST_GRP_CD").agg(
        F.count("*").alias("client_count"),
        F.countDistinct("CLNT_NO").alias("unique_clients")
    ).orderBy("TST_GRP_CD")

    # Discover segments (RPT_GRP_CD)
    # This is where age groups, risk segments, etc. are defined
    segments = None
    if "RPT_GRP_CD" in tactic_df.columns:
        segments = tactic_df.groupBy("RPT_GRP_CD").agg(
            F.count("*").alias("client_count"),
            F.countDistinct("CLNT_NO").alias("unique_clients")
        ).orderBy("RPT_GRP_CD")

    # Discover tactic cells
    tactic_cells = None
    if "TACTIC_CELL_CD" in tactic_df.columns:
        tactic_cells = tactic_df.groupBy("TACTIC_CELL_CD").agg(
            F.count("*").alias("client_count"),
            F.countDistinct("CLNT_NO").alias("unique_clients")
        ).orderBy("TACTIC_CELL_CD")

    # Discover cohorts
    cohorts = tactic_df.groupBy("COHORT").agg(
        F.count("*").alias("client_count"),
        F.countDistinct("CLNT_NO").alias("unique_clients"),
        F.min("TREATMT_STRT_DT").alias("start_date"),
        F.max("TREATMT_END_DT").alias("end_date")
    ).orderBy("COHORT")

    # Discover channels
    channels = None
    if "CHANNEL" in tactic_df.columns:
        channels = tactic_df.groupBy("CHANNEL").agg(
            F.count("*").alias("client_count"),
            F.countDistinct("CLNT_NO").alias("unique_clients")
        ).orderBy("CHANNEL")

    # Discover measurement windows
    window_days = tactic_df.groupBy("WINDOW_DAYS").agg(
        F.count("*").alias("deployment_count")
    ).orderBy("WINDOW_DAYS")

    return {
        "mne": mne,
        "total_clients": total_clients,
        "test_groups": test_groups,
        "segments": segments,
        "tactic_cells": tactic_cells,
        "cohorts": cohorts,
        "channels": channels,
        "window_days": window_days
    }


def print_campaign_structure(structure: Dict[str, Any]) -> None:
    """
    Print discovered campaign structure in readable format.

    Args:
        structure: Result from discover_campaign_structure()
    """
    print(f"\n{'='*60}")
    print(f"CAMPAIGN STRUCTURE: {structure['mne']}")
    print(f"{'='*60}")
    print(f"Total Records: {structure['total_clients']:,}")

    if structure.get("error"):
        print(f"ERROR: {structure['error']}")
        return

    print(f"\n--- Test Groups ---")
    if structure.get("test_groups"):
        structure["test_groups"].show(truncate=False)

    print(f"\n--- Segments (RPT_GRP_CD) ---")
    if structure.get("segments"):
        structure["segments"].show(truncate=False)
    else:
        print("No segment data available")

    print(f"\n--- Tactic Cells ---")
    if structure.get("tactic_cells"):
        structure["tactic_cells"].show(truncate=False)
    else:
        print("No tactic cell data available")

    print(f"\n--- Cohorts ---")
    if structure.get("cohorts"):
        structure["cohorts"].show(truncate=False)

    print(f"\n--- Channels ---")
    if structure.get("channels"):
        structure["channels"].show(truncate=False)
    else:
        print("No channel data available")

    print(f"\n--- Measurement Windows ---")
    if structure.get("window_days"):
        structure["window_days"].show(truncate=False)


def get_segment_mapping(
    tactic_df: DataFrame,
    segment_field: str = "RPT_GRP_CD"
) -> Dict[str, str]:
    """
    [WIP] Get mapping of segment codes to descriptions.

    Currently returns codes only. Future versions should:
    - Look up descriptions from mnemonic mapping table
    - Return human-readable segment names

    Args:
        tactic_df: Tactic DataFrame
        segment_field: Field containing segment codes

    Returns:
        Dictionary mapping segment codes to descriptions
    """
    if segment_field not in tactic_df.columns:
        return {}

    segments = tactic_df.select(segment_field).distinct().collect()

    # [WIP] Currently just returns code -> code mapping
    # TODO: Integrate with mnemonic mapping table for descriptions
    return {row[segment_field]: row[segment_field] for row in segments if row[segment_field]}


# =============================================================================
# FUTURE: ODS Integration
# =============================================================================

def load_ods_experiment_metadata(
    spark: SparkSession,
    tactic_ids: list
) -> Optional[DataFrame]:
    """
    [NOT IMPLEMENTED] Load experiment metadata from ODS table.

    The ODS table (ed10_im.prod_x610_crm.ods_mr_hist) contains
    an "Additional Detail" field with JSON-formatted experiment
    configuration.

    Future implementation should:
    1. Query ODS table for matching tactic IDs
    2. Parse JSON from Additional Detail field
    3. Extract experiment type, hypothesis, segments, etc.
    4. Return structured metadata

    Args:
        spark: Active SparkSession
        tactic_ids: List of tactic IDs to look up

    Returns:
        DataFrame with experiment metadata, or None if not available
    """
    # TODO: Implement when ODS access is confirmed
    # Query pattern:
    # SELECT TACTIC, ADDITIONAL_DETAIL, TREATMENT_DETAIL
    # FROM ed10_im.prod_x610_crm.ods_mr_hist
    # WHERE TACTIC IN (...)

    print("[WIP] ODS integration not yet implemented")
    print("See diagnostics/diagnose_ods_data.py for investigation")
    return None


def parse_experiment_json(json_str: str) -> Dict[str, Any]:
    """
    [NOT IMPLEMENTED] Parse experiment configuration from JSON.

    Expected JSON structure:
    {
        "Experiments": ["TestABC01_overall_test", "TestABC12_banner_challenger"],
        "TestABC01_overall_test": {
            "type": "Test vs Control",
            "performance": "Campaign Performance",
            "level": "Campaign Level",
            "impact": "Campaign Impact",
            "method": "Frequentist Causal"
        }
    }

    Args:
        json_str: JSON string from Additional Detail field

    Returns:
        Parsed experiment configuration
    """
    import json

    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}


# =============================================================================
# VALIDATION
# =============================================================================

def validate_experiment_design(structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate discovered experiment design.

    Checks for common issues:
    - Missing test or control groups
    - Unbalanced segment sizes
    - Inconsistent measurement windows

    Args:
        structure: Result from discover_campaign_structure()

    Returns:
        Dictionary with validation results and warnings
    """
    warnings = []
    errors = []

    if structure.get("error"):
        return {"valid": False, "errors": [structure["error"]], "warnings": []}

    # Check test groups
    if structure.get("test_groups"):
        test_groups_df = structure["test_groups"].toPandas()
        group_codes = test_groups_df["TST_GRP_CD"].tolist()

        if "TG4" not in group_codes:
            errors.append("No TG4 (Test) group found")

        non_tg4 = [g for g in group_codes if g != "TG4"]
        if not non_tg4:
            warnings.append("No Control groups found (only TG4)")

    # Check segments
    if structure.get("segments"):
        segments_df = structure["segments"].toPandas()
        if len(segments_df) == 1:
            warnings.append("Only one segment found - no A/B segmentation")
        elif segments_df["client_count"].std() > segments_df["client_count"].mean():
            warnings.append("Large variance in segment sizes - check for imbalance")

    # Check measurement windows
    if structure.get("window_days"):
        windows_df = structure["window_days"].toPandas()
        if len(windows_df) > 3:
            warnings.append(f"Multiple measurement windows found ({len(windows_df)}) - verify consistency")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
