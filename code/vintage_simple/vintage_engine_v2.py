"""
Vintage Engine v2
=================

Improved modular structure aligned with VINTAGE_ENGINE_ARCHITECTURE.md

Key improvements over v1:
- MODULE_REGISTRY: Documents all modules, their status, and swap targets
- MODULE_CONTRACTS: Defines INPUT/OUTPUT schemas for each module
- Channel-agnostic Journey module pattern
- Enrichment placeholder with interface definition
- Extended schemas for Stage 2/3 readiness
- Explicit OUTPUT_SCHEMA

Architecture: SuperFact 4-Layer Framework
- Layer 1: Experiment Metadata (tactic_evnt_hist) - "Who is in test?"
- Layer 2: Campaign Metadata (CAMPAIGN_METADATA) - "What to measure?"
- Layer 3: Success Definitions (SUCCESS_DEFINITIONS) - "How to calculate?"
- Layer 4: Client Journey (fulfillment, engagement, outcome) - "What actually happened?"

Copy this entire file into a Jupyter notebook cell and run.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import StorageLevel
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

# For inline plots in Jupyter
%matplotlib inline

# =============================================================================
# MODULE REGISTRY
# =============================================================================
# Documents what modules exist, their status, and swap targets.
# This makes the architecture visible in the code itself.
# =============================================================================

MODULE_REGISTRY = {
    # Context Layer Modules
    "experiment": {
        "layer": 1,
        "status": "ACTIVE",
        "description": "Identifies who is in test vs control",
        "function": "load_tactic",
        "swap_ready": False,
        "swap_target": "Experiment Metadata table (when built)",
    },
    "campaign": {
        "layer": 2,
        "status": "ACTIVE",
        "description": "Maps campaign to success metrics",
        "function": "get_campaign_config",
        "swap_ready": True,
        "swap_target": "Mnemonic Mapping v2 query",
    },
    "success": {
        "layer": 3,
        "status": "ACTIVE",
        "description": "Defines how to calculate each metric",
        "function": "get_success_definition",
        "swap_ready": True,
        "swap_target": "Success Library (GitHub or curated data)",
    },
    "enrichment": {
        "layer": 4,
        "status": "PLANNED",
        "description": "Adds context: tenure, profitability, region",
        "function": "load_enrichment",
        "swap_ready": False,
        "swap_target": "Enrichment catalog",
    },
    "journey_email": {
        "layer": 4,
        "status": "ACTIVE",
        "description": "Email engagement: sent, opened, clicked",
        "function": "load_channel_engagement",
        "swap_ready": False,
        "swap_target": None,
    },
    "journey_mobile": {
        "layer": 4,
        "status": "PLANNED",
        "description": "Mobile engagement: banner displayed, clicked",
        "function": "load_channel_engagement",
        "swap_ready": False,
        "swap_target": None,
    },
    "journey_fulfillment": {
        "layer": 4,
        "status": "PARTIAL",
        "description": "Verifies contact was delivered",
        "function": "load_fulfillment",
        "swap_ready": False,
        "swap_target": None,
    },
    "journey_outcome": {
        "layer": 4,
        "status": "ACTIVE",
        "description": "Success outcome (conversion)",
        "function": "load_success_outcome",
        "swap_ready": False,
        "swap_target": None,
    },
    # Analysis Layer
    "vintage_engine": {
        "layer": "analysis",
        "status": "ACTIVE",
        "description": "Calculates maturation curves over time",
        "function": "run_vintage_analysis",
        "swap_ready": False,
        "swap_target": None,
    },
}

# =============================================================================
# MODULE CONTRACTS
# =============================================================================
# Defines what each module expects as INPUT and returns as OUTPUT.
# This is the "interface" that future modules must follow.
# =============================================================================

MODULE_CONTRACTS = {
    "experiment": {
        "input": {
            "spark": "SparkSession",
            "mne": "str - Campaign mnemonic (e.g., 'VCN')",
        },
        "output": {
            "type": "Spark DataFrame",
            "required_columns": [
                "CLNT_NO",           # Client identifier (string, no leading zeros)
                "TACTIC_ID",         # Full tactic identifier
                "TREATMT_STRT_DT",   # Treatment start date
                "TREATMT_END_DT",    # Treatment end date
                "TST_GRP_CD",        # Test group code (e.g., TG4)
                "GROUP",             # Derived: TEST or CONTROL
                "COHORT",            # Derived: yyyy-MM format
                "WINDOW_DAYS",       # Derived: days between start and end
                "TACTIC_CELL_CD",    # Channel indicator
            ],
            "optional_columns": [
                "RPT_GRP_CD",        # Report group for segment filtering
                "TREATMT_MN",        # Treatment month
                "STRTGY_SRC_CD",     # Strategy source
                "ADDNL_DECISN_DATA1", "ADDNL_DECISN_DATA2", "ADDNL_DECISN_DATA3",
            ],
        },
    },
    "campaign": {
        "input": {
            "mne": "str - Campaign mnemonic",
        },
        "output": {
            "type": "dict",
            "required_keys": [
                "campaign_name",     # Human-readable name
                "success_type",      # ACQUISITION, ACTIVATION, USAGE, TOKENIZATION
                "primary_metric",    # Key into SUCCESS_DEFINITIONS
            ],
            "optional_keys": [
                "secondary_metric",  # Future: secondary success metric
                "tertiary_metric",   # Future: tertiary success metric
            ],
        },
    },
    "success": {
        "input": {
            "metric_name": "str - Metric key (e.g., 'card_acquisition')",
        },
        "output": {
            "type": "dict",
            "required_keys": [
                "description",       # Human-readable description
                "source",            # HIVE or EDW
                "date_field",        # Column name for success date
                "client_field",      # Column name for client ID
                "filters",           # dict or None - filter conditions
            ],
            "optional_keys": [
                "table_path",        # For HIVE sources
                "add_card_type",     # Whether to add card type column
                "code_path",         # Stage 2: GitHub path
                "table_path_curated", # Stage 3: curated table path
                "version",           # For multi-version support
            ],
        },
    },
    "enrichment": {
        "input": {
            "spark": "SparkSession",
            "client_df": "Spark DataFrame with CLNT_NO column",
            "enrichment_type": "str - e.g., 'tenure', 'profitability', 'region'",
        },
        "output": {
            "type": "Spark DataFrame",
            "required_columns": [
                "CLNT_NO",           # Client identifier (join key)
                "SEGMENT",           # Segment value (e.g., 'HIGH', 'MEDIUM', 'LOW')
                "SEGMENT_TYPE",      # What kind of segment (e.g., 'TENURE')
            ],
            "optional_columns": [
                "SEGMENT_VALUE",     # Raw value before segmentation
            ],
        },
    },
    "journey_engagement": {
        "input": {
            "spark": "SparkSession",
            "treatment_ids": "list[str] - TACTIC_IDs to query",
            "channel": "str - EMAIL, MOBILE, BANNER, etc.",
        },
        "output": {
            "type": "Spark DataFrame",
            "required_columns": [
                "CLNT_NO",           # Client identifier
                "CHANNEL",           # Channel type
                "SENT",              # 1/0 - contact was sent
                "SENT_DT",           # Date sent
            ],
            "optional_columns": [
                "OPENED",            # 1/0 - contact was opened
                "OPENED_DT",
                "CLICKED",           # 1/0 - contact was clicked
                "CLICKED_DT",
                "BOUNCED",           # 1/0 - contact bounced
                "BOUNCED_DT",
                "UNSUBSCRIBED",      # 1/0 - client unsubscribed
                "UNSUBSCRIBED_DT",
            ],
        },
    },
    "journey_outcome": {
        "input": {
            "spark": "SparkSession",
            "config": "dict - from get_full_config()",
        },
        "output": {
            "type": "Spark DataFrame",
            "required_columns": [
                "CLNT_NO",           # Client identifier
                # Plus the date_field from config (e.g., ISS_DT, ACTV_DT, TXN_DT)
            ],
        },
    },
}

# =============================================================================
# OUTPUT SCHEMA
# =============================================================================
# Defines what the final output looks like.
# Makes dimensions explicit so enrichment can add segments.
# =============================================================================

OUTPUT_SCHEMA = {
    "vintage_curves": {
        "required_dimensions": ["MNE", "COHORT", "GROUP", "DAY"],
        "optional_dimensions": ["CHANNEL", "SEGMENT", "SEGMENT_TYPE"],
        "metrics": [
            "WINDOW_DAYS",
            "TEST_CLIENTS", "TEST_SUCCESSES", "TEST_RATE",
            "CTRL_CLIENTS", "CTRL_SUCCESSES", "CTRL_RATE",
            "ABS_LIFT", "CI_LOWER", "CI_UPPER", "SIGNIFICANT",
        ],
    },
    "summary": {
        "required_dimensions": ["MNE", "COHORT"],
        "optional_dimensions": ["SEGMENT", "SEGMENT_TYPE"],
        "metrics": [
            "WINDOW_DAYS",
            "TEST_CLIENTS", "TEST_SUCCESSES", "TEST_RATE",
            "CTRL_CLIENTS", "CTRL_SUCCESSES", "CTRL_RATE",
            "ABS_LIFT", "CI_LOWER", "CI_UPPER", "SIGNIFICANT",
        ],
    },
    "channel_breakdown": {
        "required_dimensions": ["MNE", "COHORT", "GROUP", "CHANNEL"],
        "metrics": ["CLIENT_COUNT", "SUCCESS_COUNT", "SUCCESS_RATE"],
    },
    "engagement_vintage": {
        "required_dimensions": ["MNE", "COHORT", "GROUP", "DAY", "METRIC"],
        "metrics": ["WINDOW_DAYS", "TOTAL_CLIENTS", "CUMULATIVE_EVENTS", "CUMULATIVE_RATE"],
    },
}

# =============================================================================
# CONFIGURATION - GLOBAL SETTINGS
# =============================================================================

YEARS_TO_INCLUDE = [2025, 2026]
TEST_GROUP_CODE = "TG4"
CONFIDENCE_LEVEL = 0.95

# =============================================================================
# PATHS - Data Source Locations
# =============================================================================

PATHS = {
    # Layer 1: Experiment Metadata
    "tactic_base_path": "/prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/",
    "tactic_partition_pattern": "EVNT_STRT_DT=",

    # Layer 4: Client Journey - Success Outcome Sources
    "visa_dr_crd": "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT=",
    "pos_txn": "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT=",

    # Layer 4: Client Journey - Token (EDW)
    "token_source": "EDW",

    # Layer 4: Client Journey - Email Engagement (Teradata via EDW)
    "email_source": "EDW",

    # Layer 4: Client Journey - Fulfillment (Teradata via EDW)
    "fulfillment_source": "EDW",
}

# =============================================================================
# SUPPORTED CHANNELS
# =============================================================================
# Channels that the Journey module can handle.
# Used by load_channel_engagement() dispatcher.
# =============================================================================

SUPPORTED_CHANNELS = {
    "EMAIL": {
        "status": "ACTIVE",
        "code_prefix": "EM",  # Matches TACTIC_CELL_CD containing "EM"
        "function": "_load_email_engagement",
    },
    "MOBILE": {
        "status": "PLANNED",
        "code_prefix": "MB",
        "function": "_load_mobile_engagement",
    },
    "BANNER": {
        "status": "PLANNED",
        "code_prefix": "BN",
        "function": "_load_banner_engagement",
    },
    "ONB": {
        "status": "PLANNED",
        "code_prefix": "ONB",
        "function": "_load_onb_engagement",
    },
}

# =============================================================================
# LAYER 2: CAMPAIGN METADATA
# =============================================================================
# Defines WHAT to measure for each campaign.
# Extended schema includes secondary/tertiary metrics for future use.
#
# SWAP POINT: When Mnemonic Mapping v2 has metric fields, replace with query:
#   SELECT primary_metric, secondary_metric FROM mnemonic_mapping_v2 WHERE mne = '{mne}'
# =============================================================================

CAMPAIGN_METADATA = {
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
        "secondary_metric": None,  # Future: could be "card_activation"
        "tertiary_metric": None,
    },
    "VDA": {
        "campaign_name": "VVD Black Friday Cyber Monday Targeted",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
        "secondary_metric": None,
        "tertiary_metric": None,
    },
    "VDT": {
        "campaign_name": "VVD Activation Trigger",
        "success_type": "ACTIVATION",
        "primary_metric": "card_activation",
        "secondary_metric": None,
        "tertiary_metric": None,
    },
    "VUI": {
        "campaign_name": "VVD Usage Trigger",
        "success_type": "USAGE",
        "primary_metric": "card_usage",
        "secondary_metric": None,
        "tertiary_metric": None,
    },
    "VUT": {
        "campaign_name": "VVD Tokenization Usage Campaign",
        "success_type": "TOKENIZATION",
        "primary_metric": "wallet_provisioning",
        "secondary_metric": None,
        "tertiary_metric": None,
    },
    "VAW": {
        "campaign_name": "VVD Add To Wallet Contextual Notification",
        "success_type": "TOKENIZATION",
        "primary_metric": "wallet_provisioning",
        "secondary_metric": None,
        "tertiary_metric": None,
    },
}

# =============================================================================
# LAYER 3: SUCCESS DEFINITIONS
# =============================================================================
# Defines HOW to calculate each success metric.
# Extended schema includes Stage 2/3 fields for future use.
#
# SWAP POINT: When Success Library exists:
#   Stage 2: %Run from GitHub using code_path
#   Stage 3: Query curated table using table_path_curated
# =============================================================================

SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "description": "Client acquired a new VVD card",
        "version": "1.0",
        "source": "HIVE",
        "table_path": PATHS["visa_dr_crd"],
        "date_field": "ISS_DT",
        "client_field": "CLNT_NO",
        "filters": {
            "STS_CD": ["06", "08"],
            "SRVC_ID": 36,
            "ISS_DT_NOT_NULL": True
        },
        "add_card_type": True,
        # Stage 2/3 fields (not yet active)
        "code_path": None,  # Future: "github.com/team/success-library/card_acquisition.py"
        "table_path_curated": None,  # Future: "/curated/success/card_acquisition"
    },
    "card_activation": {
        "description": "Client activated their VVD card",
        "version": "1.0",
        "source": "HIVE",
        "table_path": PATHS["visa_dr_crd"],
        "date_field": "ACTV_DT",
        "client_field": "CLNT_NO",
        "filters": {
            "STS_CD": ["06", "08"],
            "SRVC_ID": 36,
            "ISS_DT_NOT_NULL": True
        },
        "add_card_type": True,
        "code_path": None,
        "table_path_curated": None,
    },
    "card_usage": {
        "description": "Client used their VVD card for a transaction",
        "version": "1.0",
        "source": "HIVE",
        "table_path": PATHS["pos_txn"],
        "date_field": "TXN_DT",
        "client_field": "CLNT_NO",
        "filters": {
            "SRVC_CD": 36,
            "TXN_TYPES": [
                {"TXN_TP": 10, "MSG_TP": "0210"},
                {"TXN_TP": 13, "MSG_TP": "0210"},
                {"TXN_TP": 12, "MSG_TP": "0220"}
            ],
            "AMT1_GT": 0,
            "EXTRACT_CLNT_NO": True
        },
        "add_card_type": False,
        "code_path": None,
        "table_path_curated": None,
    },
    "wallet_provisioning": {
        "description": "Client provisioned card to digital wallet",
        "version": "1.0",
        "source": "EDW",
        "table_path": None,
        "date_field": "TXN_DT",
        "client_field": "CLNT_NO",
        "filters": None,
        "add_card_type": False,
        "code_path": None,
        "table_path_curated": None,
    },
}

# =============================================================================
# ENRICHMENT CATALOG (PLACEHOLDER)
# =============================================================================
# Defines available enrichment types for future use.
# Status: PLANNED - data sources not yet available.
#
# When implementing, each enrichment would:
# 1. Query its data source
# 2. Return DataFrame matching MODULE_CONTRACTS["enrichment"]["output"]
# 3. Be joined to success_df to add SEGMENT column
# =============================================================================

ENRICHMENT_CATALOG = {
    "tenure": {
        "status": "PLANNED",
        "description": "Client tenure with bank",
        "segments": ["NEW", "ESTABLISHED", "LONG_TERM"],
        "source": None,  # Future: table path or query
    },
    "profitability": {
        "status": "PLANNED",
        "description": "Client profitability tier",
        "segments": ["HIGH", "MEDIUM", "LOW"],
        "source": None,
    },
    "region": {
        "status": "PLANNED",
        "description": "Client geographic region",
        "segments": ["EAST", "WEST", "CENTRAL", "ATLANTIC"],
        "source": None,
    },
    "attrition_risk": {
        "status": "PLANNED",
        "description": "Client attrition risk score",
        "segments": ["HIGH_RISK", "MEDIUM_RISK", "LOW_RISK"],
        "source": None,
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

ALL_MNES = list(CAMPAIGN_METADATA.keys())


def get_campaign_config(mne):
    """
    Layer 2: Get campaign metadata.

    Contract: MODULE_CONTRACTS["campaign"]
    Input: mne (str)
    Output: dict with campaign_name, success_type, primary_metric, etc.
    """
    return CAMPAIGN_METADATA[mne]


def get_success_definition(metric_name):
    """
    Layer 3: Get success definition.

    Contract: MODULE_CONTRACTS["success"]
    Input: metric_name (str)
    Output: dict with description, source, date_field, filters, etc.
    """
    return SUCCESS_DEFINITIONS[metric_name]


def get_full_config(mne):
    """
    Get combined config for backward compatibility.

    NOTE: This merges Layer 2 + Layer 3. In a fully modular design,
    these would stay separate. Kept for compatibility with existing functions.
    """
    campaign = CAMPAIGN_METADATA[mne]
    metric = campaign["primary_metric"]
    success = SUCCESS_DEFINITIONS[metric]

    return {
        "campaign_name": campaign["campaign_name"],
        "success_type": campaign["success_type"],
        "primary_metric": metric,
        "success_source": success["source"],
        "success_table_path": success.get("table_path"),
        "success_date_field": success["date_field"],
        "filters": success["filters"],
        "add_card_type": success.get("add_card_type", False),
    }


def print_module_status():
    """Print status of all modules for visibility."""
    print("\n" + "="*60)
    print("MODULE STATUS")
    print("="*60)
    for name, info in MODULE_REGISTRY.items():
        status_icon = {"ACTIVE": "[OK]", "PLANNED": "[--]", "PARTIAL": "[~~]"}.get(info["status"], "[??]")
        swap = f" -> {info['swap_target']}" if info.get("swap_ready") else ""
        print(f"  {status_icon} {name}: {info['status']}{swap}")
    print("="*60 + "\n")


# =============================================================================
# LAYER 1: EXPERIMENT MODULE
# =============================================================================
# Loads tactic data - identifies who is in test vs control.
#
# Contract: MODULE_CONTRACTS["experiment"]
# Input: spark (SparkSession), mne (str)
# Output: Spark DataFrame with CLNT_NO, GROUP, COHORT, TACTIC_CELL_CD, etc.
# =============================================================================

def load_tactic(spark, mne):
    """
    Layer 1: Load experiment metadata from tactic_evnt_hist.

    Identifies WHO is in the test/control groups.

    Contract: MODULE_CONTRACTS["experiment"]

    Source: /prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/
    Partition: EVNT_STRT_DT={year}*

    Returns Spark DataFrame with required columns:
    - CLNT_NO, TACTIC_ID, TREATMT_STRT_DT, TREATMT_END_DT
    - TST_GRP_CD, GROUP (TEST/CONTROL), COHORT (yyyy-MM)
    - WINDOW_DAYS, TACTIC_CELL_CD
    """
    years = [str(y) for y in YEARS_TO_INCLUDE]
    base_path = PATHS["tactic_base_path"]
    paths = [f"{base_path}EVNT_STRT_DT={year}*" for year in years]

    print(f"    [Layer 1] Loading experiment data from partitions: {years}")

    tactic = spark.read.option("basePath", base_path) \
        .parquet(*paths) \
        .filter(F.substring(F.col("TACTIC_ID"), 8, 3) == mne)

    # Field transformations
    tactic = tactic \
        .withColumn("MNE", F.substring(F.col("TACTIC_ID"), 8, 3)) \
        .withColumn("CLNT_NO", F.regexp_replace(F.trim(F.col("TACTIC_EVNT_ID")), "^0+", "")) \
        .withColumn("TST_GRP_CD", F.trim(F.col("TST_GRP_CD")))

    # Select relevant columns
    tactic = tactic.select(
        F.col("CLNT_NO"),
        F.col("TACTIC_ID"),
        F.col("TREATMT_STRT_DT"),
        F.col("TREATMT_END_DT"),
        F.col("TST_GRP_CD"),
        F.col("RPT_GRP_CD"),
        F.col("TREATMT_MN"),
        F.col("TACTIC_CELL_CD"),
        F.col("STRTGY_SRC_CD"),
        F.col("ADDNL_DECISN_DATA1"),
        F.col("ADDNL_DECISN_DATA2"),
        F.col("ADDNL_DECISN_DATA3"),
        F.col("MNE"),
    )

    # Derived columns
    tactic = tactic.withColumn("WINDOW_DAYS", F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT")))
    tactic = tactic.withColumn("GROUP", F.when(F.col("TST_GRP_CD") == TEST_GROUP_CODE, "TEST").otherwise("CONTROL"))
    tactic = tactic.withColumn("COHORT", F.date_format(F.col("TREATMT_STRT_DT"), "yyyy-MM"))

    tactic = tactic.distinct()

    return tactic


# =============================================================================
# LAYER 4: JOURNEY MODULE - FULFILLMENT
# =============================================================================

def load_fulfillment(spark, tactic_ids, channel="EMAIL"):
    """
    Layer 4: Load fulfillment data to verify contact delivery.

    For EMAIL channel: Returns None - use SENT from load_channel_engagement()
    For other channels: Would query channel-specific fulfillment source
    """
    if channel == "EMAIL":
        print(f"    [Layer 4] Email fulfillment: Using SENT from engagement data")
        return None

    print(f"    [Layer 4] Fulfillment for channel '{channel}' not yet implemented")
    return None


# =============================================================================
# LAYER 4: JOURNEY MODULE - CHANNEL ENGAGEMENT (DISPATCHER)
# =============================================================================
# Channel-agnostic pattern: single entry point routes to channel-specific loaders.
# This makes adding new channels straightforward - just add the loader function
# and register in SUPPORTED_CHANNELS.
# =============================================================================

def load_channel_engagement(spark, treatment_ids, channel):
    """
    Layer 4: Load engagement data for a channel.

    Contract: MODULE_CONTRACTS["journey_engagement"]

    This is the DISPATCHER - routes to channel-specific loaders.

    Supported channels: See SUPPORTED_CHANNELS dict

    Returns standardized DataFrame with:
    - CLNT_NO, CHANNEL
    - SENT, SENT_DT (required)
    - OPENED, OPENED_DT, CLICKED, CLICKED_DT, etc. (optional)
    """
    channel_upper = channel.upper()

    if channel_upper not in SUPPORTED_CHANNELS:
        print(f"    [Layer 4] Unknown channel: {channel}")
        return None

    channel_info = SUPPORTED_CHANNELS[channel_upper]

    if channel_info["status"] == "PLANNED":
        print(f"    [Layer 4] Channel '{channel}' is PLANNED but not yet implemented")
        return None

    # Route to channel-specific loader
    if channel_upper == "EMAIL":
        return _load_email_engagement(spark, treatment_ids)
    elif channel_upper == "MOBILE":
        return _load_mobile_engagement(spark, treatment_ids)
    elif channel_upper == "BANNER":
        return _load_banner_engagement(spark, treatment_ids)
    else:
        print(f"    [Layer 4] No loader for channel: {channel}")
        return None


def _load_email_engagement(spark, treatment_ids):
    """
    Internal: Load email engagement data.

    Source: DTZV01.VENDOR_FEEDBACK_MASTER + DTZV01.VENDOR_FEEDBACK_EVENT

    Disposition codes:
    - 1 = sent, 2 = opened, 3 = clicked, 4 = unsubscribed, 5 = bounced

    Returns DataFrame matching journey_engagement contract with CHANNEL='EMAIL'.
    """
    treatment_id_list = "','".join(treatment_ids) if treatment_ids else ""

    query = f"""
    SELECT DISTINCT
        CAST(FEEDBACK_MASTER.CLNT_NO AS VARCHAR(20)) AS CLNT_NO,
        FEEDBACK_MASTER.TREATMENT_ID,
        'EMAIL' AS CHANNEL,

        MAX(CASE WHEN disposition_cd = 1 THEN 1 ELSE 0 END) AS SENT,
        MAX(CASE WHEN disposition_cd = 2 THEN 1 ELSE 0 END) AS OPENED,
        MAX(CASE WHEN disposition_cd = 3 THEN 1 ELSE 0 END) AS CLICKED,
        MAX(CASE WHEN disposition_cd = 4 THEN 1 ELSE 0 END) AS UNSUBSCRIBED,
        MAX(CASE WHEN disposition_cd = 5 THEN 1 ELSE 0 END) AS BOUNCED,

        MAX(CASE WHEN disposition_cd = 1 THEN CAST(disposition_dt_tm AS DATE) END) AS SENT_DT,
        MAX(CASE WHEN disposition_cd = 2 THEN CAST(disposition_dt_tm AS DATE) END) AS OPENED_DT,
        MAX(CASE WHEN disposition_cd = 3 THEN CAST(disposition_dt_tm AS DATE) END) AS CLICKED_DT,
        MAX(CASE WHEN disposition_cd = 4 THEN CAST(disposition_dt_tm AS DATE) END) AS UNSUBSCRIBED_DT,
        MAX(CASE WHEN disposition_cd = 5 THEN CAST(disposition_dt_tm AS DATE) END) AS BOUNCED_DT

    FROM DTZV01.VENDOR_FEEDBACK_MASTER FEEDBACK_MASTER
    INNER JOIN DTZV01.VENDOR_FEEDBACK_EVENT FEEDBACK_EVENT
        ON FEEDBACK_MASTER.consumer_id_hashed = FEEDBACK_EVENT.consumer_id_hashed
        AND FEEDBACK_MASTER.TREATMENT_ID = FEEDBACK_EVENT.TREATMENT_ID
    WHERE FEEDBACK_MASTER.TREATMENT_ID IN ('{treatment_id_list}')
    GROUP BY FEEDBACK_MASTER.CLNT_NO, FEEDBACK_MASTER.TREATMENT_ID
    """

    print(f"    [Layer 4] Loading EMAIL engagement from EDW...")

    try:
        cursor = EDW.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()

        pdf = pd.DataFrame(rows, columns=columns)
        pdf['CLNT_NO'] = pdf['CLNT_NO'].astype(str).str.strip().str.lstrip('0')

        print(f"    [Layer 4] Retrieved {len(pdf):,} email engagement records")

        if pdf.empty:
            return None

        return spark.createDataFrame(pdf)

    except Exception as e:
        print(f"    [Layer 4] Email engagement data not available: {str(e)}")
        return None


def _load_mobile_engagement(spark, treatment_ids):
    """
    Internal: Load mobile engagement data.

    STATUS: PLANNED - Not yet implemented.

    When implemented, should return DataFrame matching journey_engagement contract
    with CHANNEL='MOBILE'.
    """
    print(f"    [Layer 4] Mobile engagement loader not yet implemented")
    return None


def _load_banner_engagement(spark, treatment_ids):
    """
    Internal: Load banner/display engagement data.

    STATUS: PLANNED - Not yet implemented.
    """
    print(f"    [Layer 4] Banner engagement loader not yet implemented")
    return None


# Backward compatibility alias
def load_email_engagement(spark, treatment_ids):
    """Alias for backward compatibility."""
    return _load_email_engagement(spark, treatment_ids)


# =============================================================================
# LAYER 4: JOURNEY MODULE - SUCCESS OUTCOME
# =============================================================================

def load_token_from_edw():
    """
    Layer 4: Load token/provisioning data from EDW.
    """
    query = """
    SELECT DISTINCT
        CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER) AS CLNT_NO,
        B.TXN_DT
    FROM DDWV05.CLNT_CRD_POS_LOG AS B
    INNER JOIN DL_DECMAN.TOKEN_LIST C
        ON B.TOKN_REQSTR_ID = C.TOKEN_ID
    WHERE B.AMT1 = 0
        AND SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190'
        AND SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'
        AND SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0'
        AND B.POS_ENTR_MODE_CD_NON_EMV = '000'
        AND B.SRVC_CD = 36
        AND C.TOKEN_WALLET_IND = 'Y'
    """

    cursor = EDW.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()

    df = pd.DataFrame(rows, columns=columns)
    return df


def load_success_outcome(spark, config):
    """
    Layer 4: Load success outcome data.

    Contract: MODULE_CONTRACTS["journey_outcome"]
    """
    years_str = [str(y) for y in YEARS_TO_INCLUDE]

    if config["success_source"] == "EDW":
        print("    [Layer 4] Loading success outcome from EDW (token)...")
        token_pdf = load_token_from_edw()
        print(f"    [Layer 4] Retrieved {len(token_pdf):,} token records")
        return spark.createDataFrame(token_pdf)

    paths = [f"{config['success_table_path']}{year}*" for year in years_str]
    print(f"    [Layer 4] Loading success outcome from partitions: {years_str}")
    df = spark.read.parquet(*paths)

    filters = config.get("filters")
    if filters:
        if "STS_CD" in filters:
            df = df.filter(F.col("STS_CD").isin(filters["STS_CD"]))
        if "SRVC_ID" in filters:
            df = df.filter(F.col("SRVC_ID") == filters["SRVC_ID"])
        if "SRVC_CD" in filters:
            df = df.filter(F.col("SRVC_CD") == filters["SRVC_CD"])
        if "TXN_TYPES" in filters:
            txn_cond = None
            for t in filters["TXN_TYPES"]:
                c = (F.col("TXN_TP") == t["TXN_TP"]) & (F.col("MSG_TP") == t["MSG_TP"])
                txn_cond = c if txn_cond is None else txn_cond | c
            df = df.filter(txn_cond)
        if filters.get("ISS_DT_NOT_NULL"):
            df = df.filter(F.col("ISS_DT").isNotNull())
        if "AMT1_GT" in filters:
            df = df.filter(F.col("AMT1") > filters["AMT1_GT"])
        if filters.get("EXTRACT_CLNT_NO"):
            df = df.withColumn("CLNT_NO", F.regexp_replace(F.substring(F.col("CLNT_CRD_NO"), 7, 9), "^0+", ""))

    if config.get("add_card_type"):
        df = df.withColumn("Card_Type", F.when(F.col("VISA_DR_CRD_BRND_CD") == "03", "Digital").otherwise("Hybrid/Plastic"))

    return df


# Backward compatibility alias
def load_success_table(spark, config):
    """Alias for backward compatibility."""
    return load_success_outcome(spark, config)


# =============================================================================
# LAYER 4: ENRICHMENT MODULE (PLACEHOLDER)
# =============================================================================
# This module is PLANNED but not yet implemented.
# The interface is defined so future implementation follows the contract.
#
# When data is available, implement the specific enrichment loaders
# and plug them in here.
# =============================================================================

def load_enrichment(spark, client_df, enrichment_type):
    """
    Layer 4: Load enrichment data to add context (segments).

    Contract: MODULE_CONTRACTS["enrichment"]

    STATUS: PLANNED - Not yet implemented.

    When implemented:
    - Queries enrichment data source
    - Joins to client_df on CLNT_NO
    - Returns DataFrame with SEGMENT and SEGMENT_TYPE columns

    Parameters:
        spark: SparkSession
        client_df: DataFrame with CLNT_NO column
        enrichment_type: str - 'tenure', 'profitability', 'region', etc.

    Returns:
        Spark DataFrame with columns: CLNT_NO, SEGMENT, SEGMENT_TYPE
        Or None if enrichment not available
    """
    if enrichment_type not in ENRICHMENT_CATALOG:
        print(f"    [Layer 4] Unknown enrichment type: {enrichment_type}")
        return None

    enrichment_info = ENRICHMENT_CATALOG[enrichment_type]

    if enrichment_info["status"] == "PLANNED":
        print(f"    [Layer 4] Enrichment '{enrichment_type}' is PLANNED but not yet implemented")
        print(f"    [Layer 4] Expected segments: {enrichment_info['segments']}")
        return None

    # Route to specific enrichment loader when implemented
    if enrichment_type == "tenure":
        return _load_tenure_enrichment(spark, client_df)
    elif enrichment_type == "profitability":
        return _load_profitability_enrichment(spark, client_df)
    elif enrichment_type == "region":
        return _load_region_enrichment(spark, client_df)
    else:
        return None


def _load_tenure_enrichment(spark, client_df):
    """Internal: Load tenure enrichment. STATUS: PLANNED"""
    print(f"    [Layer 4] Tenure enrichment not yet implemented")
    return None


def _load_profitability_enrichment(spark, client_df):
    """Internal: Load profitability enrichment. STATUS: PLANNED"""
    print(f"    [Layer 4] Profitability enrichment not yet implemented")
    return None


def _load_region_enrichment(spark, client_df):
    """Internal: Load region enrichment. STATUS: PLANNED"""
    print(f"    [Layer 4] Region enrichment not yet implemented")
    return None


# =============================================================================
# SUCCESS DETECTION - Joins experiment data with client journey
# =============================================================================

def detect_success(tactic_df, success_df, config):
    """
    Join experiment data (Layer 1) with success outcome (Layer 4).

    Determines which clients in the experiment achieved success
    within their treatment window.
    """
    tactic_columns = tactic_df.columns
    tactic_alias = tactic_df.alias("t")

    success_select = success_df.select(
        F.col("CLNT_NO").alias("SUCCESS_CLNT_NO"),
        F.col(config["success_date_field"]).alias("SUCCESS_DT")
    ).alias("s")

    joined = tactic_alias.join(
        success_select,
        (F.col("t.CLNT_NO") == F.col("s.SUCCESS_CLNT_NO")) &
        (F.col("s.SUCCESS_DT") >= F.col("t.TREATMT_STRT_DT")) &
        (F.col("s.SUCCESS_DT") <= F.col("t.TREATMT_END_DT")),
        how="left"
    )

    joined = joined.withColumn(
        "DAYS_TO_SUCCESS",
        F.when(F.col("s.SUCCESS_DT").isNotNull(),
               F.datediff(F.col("s.SUCCESS_DT"), F.col("t.TREATMT_STRT_DT"))).otherwise(None)
    )

    groupby_cols = [f"t.{col}" for col in tactic_columns] + ["t.WINDOW_DAYS", "t.GROUP", "t.COHORT"]

    result = joined.groupBy(groupby_cols).agg(
        F.max(F.when(F.col("s.SUCCESS_DT").isNotNull(), 1).otherwise(0)).alias("SUCCESS_FLAG"),
        F.min("s.SUCCESS_DT").alias("FIRST_SUCCESS_DT"),
        F.min("DAYS_TO_SUCCESS").alias("DAYS_TO_FIRST_SUCCESS"),
        F.count("s.SUCCESS_DT").alias("SUCCESS_COUNT")
    )

    for col in result.columns:
        if col.startswith("t."):
            result = result.withColumnRenamed(col, col[2:])

    return result


def enrich_with_engagement(success_df, engagement_df, fulfillment_df):
    """
    Enrich success data with engagement metrics.

    Updated to use standardized engagement column names (SENT, OPENED, CLICKED).
    """
    result = success_df

    if engagement_df is not None:
        # Check column names - support both old (EMAIL_SENT) and new (SENT) format
        eng_cols = engagement_df.columns

        if "SENT" in eng_cols:
            # New standardized format
            engagement_select = engagement_df.select(
                F.col("CLNT_NO").alias("ENG_CLNT_NO"),
                F.col("SENT").alias("EMAIL_SENT"),
                F.col("OPENED").alias("EMAIL_OPENED"),
                F.col("CLICKED").alias("EMAIL_CLICKED"),
                F.col("UNSUBSCRIBED").alias("EMAIL_UNSUBSCRIBED"),
                F.col("BOUNCED").alias("EMAIL_BOUNCED"),
                F.col("SENT_DT").alias("EMAIL_SENT_DT"),
                F.col("OPENED_DT").alias("EMAIL_OPENED_DT"),
                F.col("CLICKED_DT").alias("EMAIL_CLICKED_DT"),
                F.col("UNSUBSCRIBED_DT").alias("EMAIL_UNSUBSCRIBED_DT"),
                F.col("BOUNCED_DT").alias("EMAIL_BOUNCED_DT")
            )
        else:
            # Old format (backward compatibility)
            engagement_select = engagement_df.select(
                F.col("CLNT_NO").alias("ENG_CLNT_NO"),
                F.col("EMAIL_SENT"),
                F.col("EMAIL_OPENED"),
                F.col("EMAIL_CLICKED"),
                F.col("EMAIL_UNSUBSCRIBED"),
                F.col("EMAIL_BOUNCED"),
                F.col("EMAIL_SENT_DT"),
                F.col("EMAIL_OPENED_DT"),
                F.col("EMAIL_CLICKED_DT"),
                F.col("EMAIL_UNSUBSCRIBED_DT"),
                F.col("EMAIL_BOUNCED_DT")
            )

        result = result.join(
            engagement_select,
            result["CLNT_NO"] == engagement_select["ENG_CLNT_NO"],
            how="left"
        ).drop("ENG_CLNT_NO")

        for col in ["EMAIL_SENT", "EMAIL_OPENED", "EMAIL_CLICKED", "EMAIL_UNSUBSCRIBED", "EMAIL_BOUNCED"]:
            if col in result.columns:
                result = result.withColumn(col, F.coalesce(F.col(col), F.lit(0)))

    if fulfillment_df is not None:
        fulfillment_select = fulfillment_df.select(
            F.col("CLNT_NO").alias("FFLMNT_CLNT_NO"),
            F.col("FULFILLMENT_FLAG")
        )
        result = result.join(
            fulfillment_select,
            result["CLNT_NO"] == fulfillment_select["FFLMNT_CLNT_NO"],
            how="left"
        ).drop("FFLMNT_CLNT_NO")

        result = result.withColumn("FULFILLMENT_FLAG", F.coalesce(F.col("FULFILLMENT_FLAG"), F.lit(0)))

    return result


def enrich_with_segments(success_df, enrichment_df):
    """
    Add segment data to success DataFrame.

    This is where enrichment module output gets joined.
    STATUS: Ready for use when enrichment data is available.

    Parameters:
        success_df: DataFrame with client success data
        enrichment_df: DataFrame with CLNT_NO, SEGMENT, SEGMENT_TYPE

    Returns:
        DataFrame with SEGMENT and SEGMENT_TYPE columns added
    """
    if enrichment_df is None:
        return success_df

    enrichment_select = enrichment_df.select(
        F.col("CLNT_NO").alias("ENRICH_CLNT_NO"),
        F.col("SEGMENT"),
        F.col("SEGMENT_TYPE")
    )

    result = success_df.join(
        enrichment_select,
        success_df["CLNT_NO"] == enrichment_select["ENRICH_CLNT_NO"],
        how="left"
    ).drop("ENRICH_CLNT_NO")

    # Fill nulls for clients without enrichment data
    result = result.withColumn("SEGMENT", F.coalesce(F.col("SEGMENT"), F.lit("UNKNOWN")))
    result = result.withColumn("SEGMENT_TYPE", F.coalesce(F.col("SEGMENT_TYPE"), F.lit("NONE")))

    return result


# =============================================================================
# VINTAGE ENGINE - Core Calculations (Stable)
# =============================================================================
# This is the core calculation engine. It takes data from the layers above
# and produces vintage curves, lift, and confidence intervals.
# This does NOT change when data sources change - it's the stable core.
# =============================================================================

def build_vintage_data(success_df):
    """Build vintage curve data from success detection results."""
    group_cols = ["COHORT", "GROUP"]

    totals = success_df.groupBy(group_cols).agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )
    successes = success_df.filter(F.col("SUCCESS_FLAG") == 1).groupBy(
        group_cols + ["DAYS_TO_FIRST_SUCCESS"]
    ).agg(F.count("*").alias("SUCCESSES_ON_DAY"))
    vintage = successes.join(totals, on=group_cols, how="left")
    return vintage.orderBy("COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS")


def build_channel_breakdown(success_df):
    """Build channel breakdown for dashboard visibility."""
    breakdown = success_df.withColumn(
        "CHANNEL",
        F.trim(F.coalesce(F.col("TACTIC_CELL_CD"), F.lit("UNKNOWN")))
    )

    breakdown = breakdown.groupBy("COHORT", "GROUP", "CHANNEL").agg(
        F.count("*").alias("CLIENT_COUNT"),
        F.sum("SUCCESS_FLAG").alias("SUCCESS_COUNT")
    )

    return breakdown.orderBy("COHORT", "GROUP", "CHANNEL")


def build_engagement_vintage(success_df, mne):
    """Build vintage curves for engagement metrics."""
    columns = success_df.columns

    if "EMAIL_SENT" not in columns:
        return None

    engagement_df = success_df.withColumn(
        "DAYS_TO_OPEN",
        F.when(F.col("EMAIL_OPENED") == 1,
               F.datediff(F.col("EMAIL_OPENED_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None)
    ).withColumn(
        "DAYS_TO_CLICK",
        F.when(F.col("EMAIL_CLICKED") == 1,
               F.datediff(F.col("EMAIL_CLICKED_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None)
    )

    email_sent_df = engagement_df.filter(F.col("EMAIL_SENT") == 1)

    if email_sent_df.count() == 0:
        return None

    all_metrics = []

    if "EMAIL_OPENED" in columns:
        open_vintage = _build_metric_vintage(email_sent_df, "DAYS_TO_OPEN", "EMAIL_OPENED", "OPEN_RATE")
        if open_vintage is not None:
            all_metrics.append(open_vintage)

    if "EMAIL_CLICKED" in columns:
        click_vintage = _build_metric_vintage(email_sent_df, "DAYS_TO_CLICK", "EMAIL_CLICKED", "CLICK_RATE")
        if click_vintage is not None:
            all_metrics.append(click_vintage)

    if not all_metrics:
        return None

    combined = pd.concat(all_metrics, ignore_index=True)
    combined["MNE"] = mne
    return combined


def _build_metric_vintage(df, days_col, flag_col, metric_name):
    """Helper to build vintage curve for a single metric."""
    totals = df.groupBy("COHORT", "GROUP").agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )

    events = df.filter(F.col(flag_col) == 1).groupBy(
        "COHORT", "GROUP", days_col
    ).agg(F.count("*").alias("EVENTS_ON_DAY"))

    vintage = events.join(totals, on=["COHORT", "GROUP"], how="left")
    pdf = vintage.toPandas()

    if pdf.empty:
        return None

    pdf = pdf.rename(columns={days_col: "DAY"})
    pdf = pdf.sort_values(["COHORT", "GROUP", "DAY"])
    pdf["CUMULATIVE_EVENTS"] = pdf.groupby(["COHORT", "GROUP"])["EVENTS_ON_DAY"].cumsum()
    pdf["CUMULATIVE_RATE"] = pdf["CUMULATIVE_EVENTS"] / pdf["TOTAL_CLIENTS"] * 100
    pdf["METRIC"] = metric_name

    return pdf[["COHORT", "GROUP", "DAY", "WINDOW_DAYS", "TOTAL_CLIENTS",
                "CUMULATIVE_EVENTS", "CUMULATIVE_RATE", "METRIC"]]


def calculate_ci(test_succ, test_n, ctrl_succ, ctrl_n):
    """Calculate lift and confidence interval."""
    if test_n == 0 or ctrl_n == 0:
        return np.nan, np.nan, np.nan
    p_test, p_ctrl = test_succ / test_n, ctrl_succ / ctrl_n
    lift = p_test - p_ctrl
    se = np.sqrt((p_test * (1 - p_test) / test_n) + (p_ctrl * (1 - p_ctrl) / ctrl_n))
    z = stats.norm.ppf(1 - (1 - CONFIDENCE_LEVEL) / 2)
    return lift, lift - z * se, lift + z * se


def prepare_vintage_table(vintage_spark_df):
    """Prepare vintage table with cumulative rates and lift calculations."""
    pdf = vintage_spark_df.toPandas()
    if pdf.empty:
        return pdf

    pdf = pdf.sort_values(["COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS"])
    pdf["CUMULATIVE_SUCCESSES"] = pdf.groupby(["COHORT", "GROUP"])["SUCCESSES_ON_DAY"].cumsum()
    pdf["CUMULATIVE_RATE"] = pdf["CUMULATIVE_SUCCESSES"] / pdf["TOTAL_CLIENTS"] * 100
    pdf = pdf.rename(columns={"DAYS_TO_FIRST_SUCCESS": "DAY"})

    cohorts = pdf["COHORT"].unique()
    complete_rows = []

    for cohort in cohorts:
        for group in ["TEST", "CONTROL"]:
            data = pdf[(pdf["COHORT"] == cohort) & (pdf["GROUP"] == group)]
            if data.empty:
                continue
            total_clients = data["TOTAL_CLIENTS"].iloc[0]
            window_days = int(data["WINDOW_DAYS"].iloc[0])
            max_day = int(data["DAY"].max())
            cum_successes = 0
            for day in range(0, min(window_days + 1, max_day + 1)):
                day_data = data[data["DAY"] == day]
                if not day_data.empty:
                    cum_successes = day_data["CUMULATIVE_SUCCESSES"].iloc[0]
                complete_rows.append({
                    "COHORT": cohort, "GROUP": group, "DAY": day,
                    "WINDOW_DAYS": window_days, "TOTAL_CLIENTS": total_clients,
                    "CUMULATIVE_SUCCESSES": cum_successes,
                    "CUMULATIVE_RATE": cum_successes / total_clients * 100 if total_clients > 0 else 0
                })

    complete_df = pd.DataFrame(complete_rows)

    lift_rows = []
    for cohort in cohorts:
        cdata = complete_df[complete_df["COHORT"] == cohort]
        tdata = cdata[cdata["GROUP"] == "TEST"]
        ctdata = cdata[cdata["GROUP"] == "CONTROL"]
        if tdata.empty or ctdata.empty:
            continue
        window_days = int(tdata["WINDOW_DAYS"].iloc[0])
        for day in tdata["DAY"].unique():
            tr = tdata[tdata["DAY"] == day]
            cr = ctdata[ctdata["DAY"] == day]
            if tr.empty or cr.empty:
                continue
            lift, ci_lo, ci_hi = calculate_ci(
                tr["CUMULATIVE_SUCCESSES"].iloc[0], tr["TOTAL_CLIENTS"].iloc[0],
                cr["CUMULATIVE_SUCCESSES"].iloc[0], cr["TOTAL_CLIENTS"].iloc[0]
            )
            lift_rows.append({
                "COHORT": cohort, "DAY": day, "WINDOW_DAYS": window_days,
                "TEST_CLIENTS": tr["TOTAL_CLIENTS"].iloc[0],
                "TEST_SUCCESSES": tr["CUMULATIVE_SUCCESSES"].iloc[0],
                "TEST_RATE": tr["CUMULATIVE_RATE"].iloc[0],
                "CTRL_CLIENTS": cr["TOTAL_CLIENTS"].iloc[0],
                "CTRL_SUCCESSES": cr["CUMULATIVE_SUCCESSES"].iloc[0],
                "CTRL_RATE": cr["CUMULATIVE_RATE"].iloc[0],
                "ABS_LIFT": lift * 100, "CI_LOWER": ci_lo * 100, "CI_UPPER": ci_hi * 100
            })

    lift_df = pd.DataFrame(lift_rows)
    if not lift_df.empty:
        lift_df["SIGNIFICANT"] = (lift_df["CI_LOWER"] > 0) | (lift_df["CI_UPPER"] < 0)
    return lift_df


def generate_summary(lift_df, mne):
    """Generate summary table for final day metrics."""
    if lift_df.empty:
        return pd.DataFrame()
    final = lift_df.loc[lift_df.groupby("COHORT")["DAY"].idxmax()].copy()
    final["MNE"] = mne
    cols = ["MNE", "COHORT", "WINDOW_DAYS", "TEST_CLIENTS", "TEST_SUCCESSES", "TEST_RATE",
            "CTRL_CLIENTS", "CTRL_SUCCESSES", "CTRL_RATE", "ABS_LIFT", "CI_LOWER", "CI_UPPER", "SIGNIFICANT"]
    return final[cols].sort_values("COHORT")


def generate_engagement_summary(success_df, mne):
    """Generate email engagement summary with funnel metrics."""
    columns = success_df.columns

    summary_data = {"MNE": mne}

    total = success_df.count()
    summary_data["TOTAL_CLIENTS"] = total

    email_sent = 0
    if "EMAIL_SENT" in columns:
        email_sent = success_df.filter(F.col("EMAIL_SENT") == 1).count()
        summary_data["EMAIL_SENT"] = email_sent
        summary_data["SEND_RATE"] = round(email_sent / total * 100, 2) if total > 0 else 0

    if "EMAIL_OPENED" in columns:
        email_opened = success_df.filter(F.col("EMAIL_OPENED") == 1).count()
        summary_data["EMAIL_OPENED"] = email_opened
        summary_data["OPEN_RATE"] = round(email_opened / email_sent * 100, 2) if email_sent > 0 else 0

    if "EMAIL_CLICKED" in columns:
        email_clicked = success_df.filter(F.col("EMAIL_CLICKED") == 1).count()
        summary_data["EMAIL_CLICKED"] = email_clicked
        summary_data["CLICK_RATE"] = round(email_clicked / email_sent * 100, 2) if email_sent > 0 else 0

    if "EMAIL_UNSUBSCRIBED" in columns:
        email_unsub = success_df.filter(F.col("EMAIL_UNSUBSCRIBED") == 1).count()
        summary_data["EMAIL_UNSUBSCRIBED"] = email_unsub
        summary_data["UNSUB_RATE"] = round(email_unsub / email_sent * 100, 2) if email_sent > 0 else 0

    if "EMAIL_BOUNCED" in columns:
        email_bounced = success_df.filter(F.col("EMAIL_BOUNCED") == 1).count()
        summary_data["EMAIL_BOUNCED"] = email_bounced
        summary_data["BOUNCE_RATE"] = round(email_bounced / email_sent * 100, 2) if email_sent > 0 else 0

    return pd.DataFrame([summary_data])


# =============================================================================
# PLOTTING
# =============================================================================

def plot_vintage(vintage_df, mne, config):
    """Plot vintage curves - all cohorts on one chart."""
    if vintage_df.empty:
        print(f"No data to plot for {mne}")
        return

    fig, ax = plt.subplots(figsize=(14, 8))
    cohorts = sorted(vintage_df["COHORT"].unique())
    colors = plt.cm.tab10(np.linspace(0, 1, min(len(cohorts), 10)))
    if len(cohorts) > 10:
        colors = plt.cm.tab20(np.linspace(0, 1, min(len(cohorts), 20)))

    for i, cohort in enumerate(cohorts):
        data = vintage_df[vintage_df["COHORT"] == cohort]
        if data.empty:
            continue
        color = colors[i % len(colors)]
        test_n = int(data["TEST_CLIENTS"].iloc[0])
        ctrl_n = int(data["CTRL_CLIENTS"].iloc[0])
        ax.plot(data["DAY"], data["TEST_RATE"], '-o', linewidth=1.5, markersize=3,
                color=color, label=f'{cohort} Test (n={test_n:,})', alpha=0.9)
        ax.plot(data["DAY"], data["CTRL_RATE"], '--s', linewidth=1.5, markersize=3,
                color=color, label=f'{cohort} Ctrl (n={ctrl_n:,})', alpha=0.7)

    ax.set_xlabel("Days from Treatment", fontsize=12)
    ax.set_ylabel("Cumulative Conversion Rate (%)", fontsize=12)
    ax.set_title(f"{mne} - {config['campaign_name']}\nTest (solid) vs Control (dashed) | {config['success_type']}", fontsize=13)
    ax.legend(title="Cohort / Group", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)
    plt.tight_layout()
    plt.show()


def plot_grid(vintage_df, mne, config):
    """Plot grid view - one subplot per cohort."""
    cohorts = sorted(vintage_df["COHORT"].unique())
    n_cohorts = len(cohorts)

    if n_cohorts == 0 or n_cohorts > 12:
        print(f"Skipping grid plot: {n_cohorts} cohorts")
        return

    n_cols = min(3, n_cohorts)
    n_rows = (n_cohorts + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(min(5*n_cols, 15), min(4*n_rows, 12)), squeeze=False)

    for idx, cohort in enumerate(cohorts):
        ax = axes[idx // n_cols, idx % n_cols]
        data = vintage_df[vintage_df["COHORT"] == cohort]

        if data.empty:
            continue

        final = data[data["DAY"] == data["DAY"].max()].iloc[0]

        ax.plot(data["DAY"], data["TEST_RATE"], '-o', color='#2E86AB',
                label=f'Test (n={int(final["TEST_CLIENTS"]):,})')
        ax.plot(data["DAY"], data["CTRL_RATE"], '-s', color='#A23B72',
                label=f'Control (n={int(final["CTRL_CLIENTS"]):,})')

        ax.annotate(f'Lift: {final["ABS_LIFT"]:.2f}pp\n[{final["CI_LOWER"]:.2f}, {final["CI_UPPER"]:.2f}]',
                    xy=(0.95, 0.05), xycoords='axes fraction', fontsize=8, ha='right', va='bottom',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax.set_title(f'Cohort: {cohort}', fontsize=10)
        ax.set_xlabel("Days", fontsize=9)
        ax.set_ylabel("Rate (%)", fontsize=9)
        ax.legend(fontsize=7, loc='upper left')
        ax.grid(True, alpha=0.3)

    for idx in range(n_cohorts, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].set_visible(False)

    fig.suptitle(f"{mne} - {config['campaign_name']} | {config['success_type']}", fontsize=13, y=1.02)
    plt.tight_layout()
    plt.show()


# =============================================================================
# MAIN RUNNER
# =============================================================================

def run_vintage_analysis(spark, mne, show_plots=True, verbose=True, include_engagement=True, enrichment_types=None):
    """
    Run vintage analysis for a campaign.

    Parameters:
        spark: SparkSession
        mne: Campaign mnemonic (e.g., 'VCN')
        show_plots: Whether to display plots
        verbose: Whether to print progress messages
        include_engagement: Whether to load engagement data
        enrichment_types: List of enrichment types to add (e.g., ['tenure', 'region'])
                         STATUS: PLANNED - will work when enrichment data is available

    Returns dict with vintage_df, summary_df, and engagement_summary_df.
    """
    def log(msg):
        if verbose:
            print(msg)

    log(f"\n{'='*60}")
    log(f"VINTAGE ANALYSIS: {mne}")
    log(f"{'='*60}")

    # Layer 2: Get campaign metadata
    campaign = get_campaign_config(mne)
    log(f"[Layer 2] Campaign: {campaign['campaign_name']}")
    log(f"[Layer 2] Success Type: {campaign['success_type']}")
    log(f"[Layer 2] Primary Metric: {campaign['primary_metric']}")

    # Layer 3: Get success definition
    success_def = get_success_definition(campaign['primary_metric'])
    log(f"[Layer 3] Success Definition: {success_def['description']}")

    # Combined config for existing functions
    config = get_full_config(mne)

    # Layer 1: Load experiment data
    log("\n[Layer 1] Loading experiment data...")
    tactic_df = load_tactic(spark, mne)
    tactic_count = tactic_df.count()
    log(f"[Layer 1] Experiment records: {tactic_count:,}")

    if tactic_count == 0:
        log("[Layer 1] ERROR: No experiment records!")
        return None

    # Get unique tactic IDs for Layer 4 queries
    tactic_ids = [row.TACTIC_ID for row in tactic_df.select("TACTIC_ID").distinct().collect()]

    # Layer 4: Load client journey data
    log("\n[Layer 4] Loading client journey data...")

    # 4a: Detect channels in data
    channel_counts = tactic_df.groupBy(F.trim(F.col("TACTIC_CELL_CD")).alias("CHANNEL_TRIMMED")).count().collect()
    channels_in_data = {row["CHANNEL_TRIMMED"]: row["count"] for row in channel_counts}
    log(f"    [Layer 4] Channels in data: {channels_in_data}")

    # 4b: Fulfillment
    fulfillment_df = None
    if include_engagement:
        has_email = any("EM" in ch for ch in channels_in_data.keys() if ch)
        fulfillment_df = load_fulfillment(spark, tactic_ids, channel="EMAIL" if has_email else "OTHER")

    # 4c: Channel engagement (using dispatcher)
    engagement_df = None
    if include_engagement:
        email_client_count = sum(count for ch, count in channels_in_data.items() if ch and "EM" in ch)
        log(f"    [Layer 4] Email channel clients: {email_client_count:,}")

        if email_client_count > 0:
            email_clients = tactic_df.filter(F.trim(F.col("TACTIC_CELL_CD")).contains("EM"))
            email_tactic_ids = [row.TACTIC_ID for row in email_clients.select("TACTIC_ID").distinct().collect()]
            engagement_df = load_channel_engagement(spark, email_tactic_ids[:5] if email_tactic_ids else [], "EMAIL")

    # 4d: Success outcome
    log("\n[Layer 4] Loading success outcome...")
    success_table = load_success_outcome(spark, config)

    # Detect success (join Layer 1 + Layer 4)
    log("\n[Engine] Detecting success...")
    success_df = detect_success(tactic_df, success_table, config)

    # Enrich with engagement data
    if include_engagement and (engagement_df is not None or fulfillment_df is not None):
        log("[Engine] Enriching with engagement data...")
        success_df = enrich_with_engagement(success_df, engagement_df, fulfillment_df)

    # ==========================================================================
    # ENRICHMENT HOOK (PLACEHOLDER)
    # ==========================================================================
    # When enrichment data is available, this is where it would be added.
    # The enrichment_types parameter specifies which enrichments to include.
    # ==========================================================================
    if enrichment_types:
        log("\n[Layer 4] Loading enrichment data...")
        for enrichment_type in enrichment_types:
            enrichment_df = load_enrichment(spark, success_df, enrichment_type)
            if enrichment_df is not None:
                success_df = enrich_with_segments(success_df, enrichment_df)
                log(f"    [Layer 4] Added enrichment: {enrichment_type}")
            else:
                log(f"    [Layer 4] Enrichment '{enrichment_type}' not available (PLANNED)")

    success_df.persist(StorageLevel.MEMORY_AND_DISK)

    # Success summary
    log("\n[Engine] Success summary by group:")
    success_df.groupBy("GROUP").agg(
        F.count("*").alias("TOTAL"),
        F.sum("SUCCESS_FLAG").alias("SUCCESSES"),
        F.avg("SUCCESS_FLAG").alias("RATE")
    ).show()

    # Build vintage curves
    log("\n[Engine] Building vintage curves...")
    vintage_spark = build_vintage_data(success_df)
    vintage_df = prepare_vintage_table(vintage_spark)

    if vintage_df.empty:
        log("[Engine] ERROR: No vintage data!")
        success_df.unpersist()
        return None

    # Build channel breakdown
    log("\n[Engine] Building channel breakdown...")
    channel_breakdown_spark = build_channel_breakdown(success_df)
    channel_breakdown_df = channel_breakdown_spark.toPandas()
    channel_breakdown_df["MNE"] = mne
    channel_breakdown_df["SUCCESS_RATE"] = (
        channel_breakdown_df["SUCCESS_COUNT"] / channel_breakdown_df["CLIENT_COUNT"] * 100
    ).round(2)
    log(f"    Channel breakdown rows: {len(channel_breakdown_df)}")
    print(channel_breakdown_df.to_string(index=False))

    # Generate summaries
    log("\n[Engine] Generating summaries...")
    summary_df = generate_summary(vintage_df, mne)
    print(summary_df.to_string(index=False))

    # Engagement summary
    engagement_summary_df = None
    if include_engagement:
        engagement_summary_df = generate_engagement_summary(success_df, mne)
        if not engagement_summary_df.empty and len(engagement_summary_df.columns) > 2:
            log("\n[Layer 4] Engagement Summary:")
            print(engagement_summary_df.to_string(index=False))

    # Engagement vintage curves
    engagement_vintage_df = None
    if include_engagement and "EMAIL_SENT" in success_df.columns:
        log("\n[Engine] Building engagement vintage curves...")
        engagement_vintage_df = build_engagement_vintage(success_df, mne)
        if engagement_vintage_df is not None and not engagement_vintage_df.empty:
            log(f"    Engagement vintage rows: {len(engagement_vintage_df)}")

    # Plotting
    if show_plots:
        log("\n[Output] Plotting...")
        plot_vintage(vintage_df, mne, config)
        plot_grid(vintage_df, mne, config)

    success_df.unpersist()

    log(f"\n{'='*60}")
    log(f"COMPLETE: {mne}")
    log(f"{'='*60}")

    return {
        "vintage_df": vintage_df,
        "summary_df": summary_df,
        "channel_breakdown_df": channel_breakdown_df,
        "engagement_summary_df": engagement_summary_df,
        "engagement_vintage_df": engagement_vintage_df,
    }


def run_all_campaigns(spark, mnes=None, show_plots=True, include_engagement=True, enrichment_types=None):
    """Run vintage analysis for multiple campaigns."""
    mnes = mnes or ALL_MNES
    results = {}
    all_summaries = []
    all_engagement = []
    all_channel_breakdown = []
    all_engagement_vintage = []

    for mne in mnes:
        try:
            result = run_vintage_analysis(
                spark, mne,
                show_plots=show_plots,
                include_engagement=include_engagement,
                enrichment_types=enrichment_types
            )
            if result:
                results[mne] = result
                all_summaries.append(result["summary_df"])
                if result.get("engagement_summary_df") is not None:
                    all_engagement.append(result["engagement_summary_df"])
                if result.get("channel_breakdown_df") is not None:
                    all_channel_breakdown.append(result["channel_breakdown_df"])
                if result.get("engagement_vintage_df") is not None:
                    all_engagement_vintage.append(result["engagement_vintage_df"])
        except Exception as e:
            print(f"ERROR {mne}: {str(e)}")

    if all_summaries:
        combined = pd.concat(all_summaries, ignore_index=True)
        print(f"\n{'='*60}")
        print("ALL CAMPAIGNS - VINTAGE SUMMARY")
        print(f"{'='*60}")
        print(combined.to_string(index=False))
        results["_combined_summary"] = combined

    if all_engagement:
        combined_eng = pd.concat(all_engagement, ignore_index=True)
        print(f"\n{'='*60}")
        print("ALL CAMPAIGNS - ENGAGEMENT SUMMARY")
        print(f"{'='*60}")
        print(combined_eng.to_string(index=False))
        results["_combined_engagement"] = combined_eng

    if all_channel_breakdown:
        combined_channel = pd.concat(all_channel_breakdown, ignore_index=True)
        print(f"\n{'='*60}")
        print("ALL CAMPAIGNS - CHANNEL BREAKDOWN")
        print(f"{'='*60}")
        print(combined_channel.to_string(index=False))
        results["_combined_channel_breakdown"] = combined_channel

    if all_engagement_vintage:
        combined_eng_vintage = pd.concat(all_engagement_vintage, ignore_index=True)
        print(f"\n{'='*60}")
        print("ALL CAMPAIGNS - ENGAGEMENT VINTAGE")
        print(f"{'='*60}")
        print(combined_eng_vintage.head(20).to_string(index=False))
        results["_combined_engagement_vintage"] = combined_eng_vintage

    return results


# =============================================================================
# CSV EXPORT
# =============================================================================

def export_to_csv(results, output_path="vintage_data.csv"):
    """Export vintage results to local CSV."""
    all_data = []

    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        df = result["vintage_df"].copy()
        df["MNE"] = mne
        all_data.append(df)

    if not all_data:
        print("No data to export")
        return

    combined = pd.concat(all_data, ignore_index=True)
    combined.to_csv(output_path, index=False)
    print(f"Exported {len(combined)} rows to {output_path}")
    return output_path


def export_all_to_hdfs(results, spark, base_path="/user/427966379/vintage_output"):
    """Export ALL vintage results to HDFS as separate CSV files."""
    exported = []

    # 1. Main vintage curves
    all_vintage = []
    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        df = result["vintage_df"].copy()
        df["MNE"] = mne
        all_vintage.append(df)

    if all_vintage:
        combined = pd.concat(all_vintage, ignore_index=True)
        spark_df = spark.createDataFrame(combined)
        path = f"{base_path}/vintage_curves.csv"
        spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(path)
        print(f"Exported vintage_curves.csv: {len(combined):,} rows")
        exported.append(path)

    # 2. Channel breakdown
    all_channel = []
    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        if result.get("channel_breakdown_df") is not None:
            all_channel.append(result["channel_breakdown_df"])

    if all_channel:
        combined = pd.concat(all_channel, ignore_index=True)
        spark_df = spark.createDataFrame(combined)
        path = f"{base_path}/channel_breakdown.csv"
        spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(path)
        print(f"Exported channel_breakdown.csv: {len(combined):,} rows")
        exported.append(path)

    # 3. Engagement vintage
    all_eng_vintage = []
    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        if result.get("engagement_vintage_df") is not None:
            all_eng_vintage.append(result["engagement_vintage_df"])

    if all_eng_vintage:
        combined = pd.concat(all_eng_vintage, ignore_index=True)
        spark_df = spark.createDataFrame(combined)
        path = f"{base_path}/engagement_vintage.csv"
        spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(path)
        print(f"Exported engagement_vintage.csv: {len(combined):,} rows")
        exported.append(path)

    # 4. Summary
    all_summary = []
    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        if result.get("summary_df") is not None:
            all_summary.append(result["summary_df"])

    if all_summary:
        combined = pd.concat(all_summary, ignore_index=True)
        spark_df = spark.createDataFrame(combined)
        path = f"{base_path}/summary.csv"
        spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(path)
        print(f"Exported summary.csv: {len(combined):,} rows")
        exported.append(path)

    print(f"\n{'='*60}")
    print(f"EXPORT COMPLETE: {len(exported)} files to {base_path}/")
    print(f"{'='*60}")

    return exported


def export_to_hdfs_csv(results, spark, hdfs_path="/user/427966379/vintage_data.csv"):
    """Export vintage results to HDFS as CSV (legacy)."""
    all_data = []

    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        df = result["vintage_df"].copy()
        df["MNE"] = mne
        all_data.append(df)

    if not all_data:
        print("No data to export")
        return

    combined = pd.concat(all_data, ignore_index=True)
    spark_df = spark.createDataFrame(combined)

    spark_df.coalesce(1) \
        .write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(hdfs_path)

    print(f"Exported CSV to HDFS: {hdfs_path}")
    print(f"Rows: {len(combined):,}")
    print(f"Campaigns: {', '.join([m for m in results.keys() if not m.startswith('_')])}")
    return hdfs_path


# =============================================================================
# SETUP & USAGE
# =============================================================================

spark = SparkSession.builder.appName("Vintage Engine v2").getOrCreate()

# Print module status on load
print_module_status()

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        VINTAGE ENGINE v2                                      ║
║                                                                              ║
║  Improvements over v1:                                                       ║
║  - MODULE_REGISTRY: See what modules exist and their status                  ║
║  - MODULE_CONTRACTS: Clear INPUT/OUTPUT definitions                          ║
║  - Channel-agnostic Journey: Easy to add mobile, banner, etc.                ║
║  - Enrichment placeholder: Ready when data is available                      ║
║  - Extended schemas: Stage 2/3 fields for future migration                   ║
║                                                                              ║
║  Architecture: SuperFact 4-Layer Framework                                   ║
║  - Layer 1: Experiment Metadata                                              ║
║  - Layer 2: Campaign Metadata [SWAP POINT]                                   ║
║  - Layer 3: Success Definitions [SWAP POINT]                                 ║
║  - Layer 4: Client Journey (fulfillment, engagement, outcome, enrichment)    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Available campaigns: """ + ", ".join(ALL_MNES) + """

Usage:
  # Single campaign
  results = run_vintage_analysis(spark, 'VCN')

  # All campaigns
  results = run_all_campaigns(spark)

  # With enrichment (when available)
  results = run_vintage_analysis(spark, 'VCN', enrichment_types=['tenure', 'region'])

  # Check module status
  print_module_status()

  # Export to HDFS
  export_all_to_hdfs(results, spark)
""")
