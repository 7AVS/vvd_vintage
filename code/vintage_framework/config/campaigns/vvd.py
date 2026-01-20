"""
VVD (Virtual Visa Debit) Campaign Configurations
=================================================

This file defines all VVD campaigns and their success measurement logic.

Campaigns:
- VCN: VVD Contextual Notification (Acquisition)
- VDA: VVD Black Friday Cyber Monday Targeted (Acquisition)
- VDT: VVD Activation Trigger (Activation)
- VUI: VVD Usage Trigger (Usage)
- VUT: VVD Tokenization Usage Campaign (Tokenization)
- VAW: VVD Add To Wallet Contextual Notification (Tokenization)

Reference: VVD Vintage Framework Design Document
Reference: Success Library - VVD_ACQ_001, VVD_ACT_001, VVD_USG_001, VVD_PRV_001
"""

from ..paths import VISA_DR_CRD_PATH, POS_TXN_PATH, TOKEN_PARQUET_PATH

# =============================================================================
# VVD CAMPAIGN CONFIGURATION
# =============================================================================

CAMPAIGN_CONFIG = {

    # -------------------------------------------------------------------------
    # ACQUISITION CAMPAIGNS
    # -------------------------------------------------------------------------

    "VCN": {
        "mne": "VCN",
        "product": "VVD",
        "campaign_name": "VVD Contextual Notification",
        "description": "Trigger campaign for VVD acquisition via contextual notifications",

        # Success configuration
        "success_type": "ACQUISITION",
        "success_source": "HIVE",
        "success_table_path": VISA_DR_CRD_PATH,
        "success_date_field": "ISS_DT",  # Issue date = acquisition success

        # Filters for success table
        "filters": {
            "STS_CD": {"operator": "in", "value": ["06", "08"]},  # Valid status codes
            "SRVC_ID": {"operator": "eq", "value": 36},           # VVD service ID
            "ISS_DT": {"operator": "not_null"}                    # Must have issue date
        },

        # Deployment characteristics
        "deployment_type": "trigger",  # Monthly trigger deployments
        "has_reminder": False,

        # Success Library reference (for future integration)
        "metric_id": "VVD_ACQ_001"
    },

    "VDA": {
        "mne": "VDA",
        "product": "VVD",
        "campaign_name": "VVD Black Friday Cyber Monday Targeted",
        "description": "Seasonal batch campaign for VVD acquisition during BFCM",

        # Success configuration
        "success_type": "ACQUISITION",
        "success_source": "HIVE",
        "success_table_path": VISA_DR_CRD_PATH,
        "success_date_field": "ISS_DT",

        # Filters for success table
        "filters": {
            "STS_CD": {"operator": "in", "value": ["06", "08"]},
            "SRVC_ID": {"operator": "eq", "value": 36},
            "ISS_DT": {"operator": "not_null"}
        },

        # Deployment characteristics
        "deployment_type": "batch",  # Seasonal/yearly batch
        "has_reminder": False,

        # Success Library reference
        "metric_id": "VVD_ACQ_001"
    },

    # -------------------------------------------------------------------------
    # ACTIVATION CAMPAIGN
    # -------------------------------------------------------------------------

    "VDT": {
        "mne": "VDT",
        "product": "VVD",
        "campaign_name": "VVD Activation Trigger",
        "description": "Trigger campaign to activate VVD cards, with 15-day reminder",

        # Success configuration
        "success_type": "ACTIVATION",
        "success_source": "HIVE",
        "success_table_path": VISA_DR_CRD_PATH,
        "success_date_field": "ACTV_DT",  # Activation date = success

        # Filters for success table
        "filters": {
            "STS_CD": {"operator": "in", "value": ["06", "08"]},
            "SRVC_ID": {"operator": "eq", "value": 36},
            "ISS_DT": {"operator": "not_null"}  # Card must exist (have ISS_DT)
        },

        # Deployment characteristics
        "deployment_type": "trigger",
        "has_reminder": True,  # Sends reminder at day 15

        # Success Library reference
        "metric_id": "VVD_ACT_001"
    },

    # -------------------------------------------------------------------------
    # USAGE CAMPAIGN
    # -------------------------------------------------------------------------

    "VUI": {
        "mne": "VUI",
        "product": "VVD",
        "campaign_name": "VVD Usage Trigger",
        "description": "Trigger campaign to drive VVD card usage/transactions",

        # Success configuration
        "success_type": "USAGE",
        "success_source": "HIVE",
        "success_table_path": POS_TXN_PATH,
        "success_date_field": "TXN_DT",  # Transaction date = success

        # Filters for success table
        "filters": {
            "SRVC_CD": {"operator": "eq", "value": 36},
            "AMT1": {"operator": "gt", "value": 0},  # Positive transaction amount
            # Complex filter: TXN_TP and MSG_TP combinations for purchase transactions
            "TXN_TYPES": {
                "operator": "or",
                "conditions": [
                    {"TXN_TP": {"operator": "eq", "value": 10}, "MSG_TP": {"operator": "eq", "value": "0210"}},
                    {"TXN_TP": {"operator": "eq", "value": 13}, "MSG_TP": {"operator": "eq", "value": "0210"}},
                    {"TXN_TP": {"operator": "eq", "value": 12}, "MSG_TP": {"operator": "eq", "value": "0220"}}
                ]
            }
        },

        # Special handling for this table
        "client_id_extraction": {
            "source_field": "CLNT_CRD_NO",
            "method": "substring_strip",  # substring(7, 9) then strip leading zeros
            "start": 7,
            "length": 9
        },

        # Deployment characteristics
        "deployment_type": "trigger",
        "has_reminder": False,

        # Success Library reference
        "metric_id": "VVD_USG_001"
    },

    # -------------------------------------------------------------------------
    # TOKENIZATION CAMPAIGNS
    # -------------------------------------------------------------------------

    "VUT": {
        "mne": "VUT",
        "product": "VVD",
        "campaign_name": "VVD Tokenization Usage Campaign",
        "description": "Campaign to drive digital wallet provisioning (Apple Pay, Google Pay, etc.)",

        # Success configuration
        "success_type": "TOKENIZATION",
        "success_source": "EDW",  # Pre-pulled from EDW
        "success_table_path": TOKEN_PARQUET_PATH,
        "success_date_field": "TXN_DT",

        # Filters: None - data is pre-filtered in EDW query
        "filters": None,

        # Deployment characteristics
        "deployment_type": "trigger",
        "has_reminder": False,

        # Success Library reference
        "metric_id": "VVD_PRV_001"
    },

    "VAW": {
        "mne": "VAW",
        "product": "VVD",
        "campaign_name": "VVD Add To Wallet Contextual Notification",
        "description": "Contextual notification to drive digital wallet provisioning",

        # Success configuration
        "success_type": "TOKENIZATION",
        "success_source": "EDW",
        "success_table_path": TOKEN_PARQUET_PATH,
        "success_date_field": "TXN_DT",

        # Filters: None - data is pre-filtered in EDW query
        "filters": None,

        # Deployment characteristics
        "deployment_type": "trigger",
        "has_reminder": False,

        # Success Library reference
        "metric_id": "VVD_PRV_001"
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_mnes_by_success_type(success_type: str) -> list:
    """Get all MNEs for a given success type."""
    return [mne for mne, config in CAMPAIGN_CONFIG.items()
            if config["success_type"] == success_type]


def get_mnes_by_deployment_type(deployment_type: str) -> list:
    """Get all MNEs for a given deployment type."""
    return [mne for mne, config in CAMPAIGN_CONFIG.items()
            if config["deployment_type"] == deployment_type]


# List of all VVD MNEs
ALL_VVD_MNES = list(CAMPAIGN_CONFIG.keys())

# Group by success type
ACQUISITION_MNES = get_mnes_by_success_type("ACQUISITION")  # VCN, VDA
ACTIVATION_MNES = get_mnes_by_success_type("ACTIVATION")    # VDT
USAGE_MNES = get_mnes_by_success_type("USAGE")              # VUI
TOKENIZATION_MNES = get_mnes_by_success_type("TOKENIZATION")  # VUT, VAW
