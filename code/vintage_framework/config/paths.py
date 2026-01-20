"""
Data Source Paths Configuration
===============================

Central location for all data source paths.
Modify this file when paths change or when moving between environments.

Reference: Success Library Layer 4 - Client Marketing Interaction Journey
"""

# =============================================================================
# TACTIC / POPULATION DATA
# =============================================================================

# Tactic event history - contains campaign deployments and client assignments
# Original table: DTZTA_T_TACTIC_EVNT_HIST
TACTIC_PARQUET_PATH = "/user/427966379/tactic.parquet"

# ODS table for experiment metadata (Layer 1)
# Contains Additional Detail field with JSON experiment configuration
ODS_TABLE = "ed10_im.prod_x610_crm.ods_mr_hist"

# =============================================================================
# SUCCESS DATA - HIVE PATHS
# =============================================================================

# DDWTA_VISA_DR_CRD - Card issuance and activation data
# Used for: Acquisition (ISS_DT), Activation (ACTV_DT)
VISA_DR_CRD_PATH = "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT="

# DDWTA_T_PT_OF_SALE_TXN - Point of sale transactions
# Used for: Usage (TXN_DT)
POS_TXN_PATH = "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT="

# =============================================================================
# SUCCESS DATA - EDW / PRE-PULLED
# =============================================================================

# Token provisioning data (pre-pulled from EDW)
# Original source: DDWV05.CLNT_CRD_POS_LOG joined with DL_DECMAN.TOKEN_LIST
TOKEN_PARQUET_PATH = "/user/427966379/token.parquet"

# =============================================================================
# OUTPUT PATHS
# =============================================================================

# Base path for outputs
OUTPUT_BASE_PATH = "/user/427966379"

# Output subdirectories (relative to OUTPUT_BASE_PATH)
OUTPUT_DATA_SUBDIR = ""  # CSV/Parquet files
OUTPUT_PLOTS_SUBDIR = ""  # PNG plots

# =============================================================================
# PATH HELPERS
# =============================================================================

def get_success_table_path(base_path: str, years: list) -> list:
    """
    Generate list of paths for year-partitioned success tables.

    Args:
        base_path: Base path with partition pattern (e.g., CAPTR_DT=)
        years: List of years to include

    Returns:
        List of paths with year wildcards
    """
    return [f"{base_path}{year}*" for year in years]


def get_output_path(filename: str, subdir: str = "") -> str:
    """
    Generate full output path for a file.

    Args:
        filename: Name of the output file
        subdir: Optional subdirectory

    Returns:
        Full path for output file
    """
    if subdir:
        return f"{OUTPUT_BASE_PATH}/{subdir}/{filename}"
    return f"{OUTPUT_BASE_PATH}/{filename}"
