"""
Vintage Curve Configuration
===========================

All campaign configurations in one place.
Edit this file to add new campaigns or modify settings.

Usage in Jupyter:
    from config import CAMPAIGN_CONFIG, YEARS_TO_INCLUDE, get_config
"""

# =============================================================================
# UNIVERSAL STANDARDS
# =============================================================================

# Cohort aggregation - ALWAYS monthly (yyyy-MM), never weekly/daily
AGGREGATION_LEVEL = "MONTH"
COHORT_DATE_FORMAT = "yyyy-MM"

# Years to include
YEARS_TO_INCLUDE = [2025, 2026]

# Test group: TG4 = Test, all others = Control
TEST_GROUP_CODE = "TG4"

# Confidence level for lift calculations
CONFIDENCE_LEVEL = 0.95

# =============================================================================
# DATA PATHS
# =============================================================================

PATHS = {
    "tactic": "/user/427966379/tactic.parquet",
    "visa_dr_crd": "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT=",
    "pos_txn": "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT=",
    "token": "/user/427966379/token.parquet",
    "output": "/user/427966379"
}

# =============================================================================
# CAMPAIGN CONFIGURATIONS - VVD
# =============================================================================

CAMPAIGN_CONFIG = {

    # ACQUISITION CAMPAIGNS
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "success_source": "HIVE",
        "success_table_path": PATHS["visa_dr_crd"],
        "success_date_field": "ISS_DT",
        "filters": {
            "STS_CD": ["06", "08"],
            "SRVC_ID": 36,
            "ISS_DT_NOT_NULL": True
        },
        "deployment_type": "trigger"
    },

    "VDA": {
        "campaign_name": "VVD Black Friday Cyber Monday Targeted",
        "success_type": "ACQUISITION",
        "success_source": "HIVE",
        "success_table_path": PATHS["visa_dr_crd"],
        "success_date_field": "ISS_DT",
        "filters": {
            "STS_CD": ["06", "08"],
            "SRVC_ID": 36,
            "ISS_DT_NOT_NULL": True
        },
        "deployment_type": "batch"
    },

    # ACTIVATION CAMPAIGN
    "VDT": {
        "campaign_name": "VVD Activation Trigger",
        "success_type": "ACTIVATION",
        "success_source": "HIVE",
        "success_table_path": PATHS["visa_dr_crd"],
        "success_date_field": "ACTV_DT",
        "filters": {
            "STS_CD": ["06", "08"],
            "SRVC_ID": 36,
            "ISS_DT_NOT_NULL": True
        },
        "deployment_type": "trigger"
    },

    # USAGE CAMPAIGN
    "VUI": {
        "campaign_name": "VVD Usage Trigger",
        "success_type": "USAGE",
        "success_source": "HIVE",
        "success_table_path": PATHS["pos_txn"],
        "success_date_field": "TXN_DT",
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
        "deployment_type": "trigger"
    },

    # TOKENIZATION CAMPAIGNS
    "VUT": {
        "campaign_name": "VVD Tokenization Usage Campaign",
        "success_type": "TOKENIZATION",
        "success_source": "EDW",
        "success_table_path": PATHS["token"],
        "success_date_field": "TXN_DT",
        "filters": None,
        "deployment_type": "trigger"
    },

    "VAW": {
        "campaign_name": "VVD Add To Wallet Contextual Notification",
        "success_type": "TOKENIZATION",
        "success_source": "EDW",
        "success_table_path": PATHS["token"],
        "success_date_field": "TXN_DT",
        "filters": None,
        "deployment_type": "trigger"
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_config(mne):
    """Get configuration for a campaign."""
    if mne not in CAMPAIGN_CONFIG:
        raise ValueError(f"Campaign '{mne}' not found. Available: {list(CAMPAIGN_CONFIG.keys())}")
    return CAMPAIGN_CONFIG[mne]

def list_campaigns():
    """List all available campaigns."""
    for mne, config in CAMPAIGN_CONFIG.items():
        print(f"{mne}: {config['campaign_name']} ({config['success_type']})")

# All VVD campaign codes
ALL_MNES = list(CAMPAIGN_CONFIG.keys())
