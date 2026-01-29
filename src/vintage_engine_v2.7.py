"""
Vintage Engine v2.7
===================

Changes from v2.6:
- REORGANIZED: Code structured into clearly marked module sections (M1-M7)
  matching the module architecture in docs/architecture/engine_modules/
- ADDED: Module entry points — run_experiment(), run_campaign(), run_success(),
  run_journey(), run_engine() — each with defined inputs and outputs
- ADDED: Contract validation at module boundaries (runtime enforcement)
- MOVED: SUCCESS_DT aliasing from detect_success() (M6) to run_success() (M3)
  — M3 now enforces its output contract before handing off
- REMOVED: Hardcoded EDW fallback in load_from_edw() — single source of truth
- RENAMED: load_token_from_edw() → load_from_edw() — generic name
- SIMPLIFIED: detect_success() — always receives SUCCESS_DT from M3
- UPDATED: Runner reads like the DAG — each step is one line, one module

Architecture:
  CONTEXT LAYER                    ANALYSIS LAYER
  M1 Experiment ──→ M2 Campaign   M6 Engine ──→ M7 Output
       │                  │
       │                  ▼
       │           M3 Success ──→ M6
       │
       └──→ M5 Journey ────────→ M6

Module Catalog:     docs/architecture/engine_modules/MODULE_CATALOG.md
Handshake Contracts: docs/architecture/engine_modules/HANDSHAKE_CONTRACTS.md
Execution Flow:      docs/architecture/engine_modules/EXECUTION_FLOW.md

Output Schema:
  MNE | COHORT | TST_GRP_CD | RPT_GRP_CD | METRIC | DAY | WINDOW_DAYS | CLIENT_CNT | SUCCESS_CNT | RATE

Copy this entire file into a Jupyter notebook cell and run.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import StorageLevel
import pandas as pd
import numpy as np
from urllib.parse import quote
from IPython.display import HTML, display

# For inline plots in Jupyter
%matplotlib inline


# #############################################################################
#
#                              CONFIGURATION
#
# #############################################################################

USER_CONFIG = {
    "user_id": "427966379",
    "hdfs_base_path": "/user/427966379",
    "output_folder": "vintage_output_v2",
}


def get_hdfs_output_path():
    """Get the full HDFS output path."""
    return f"{USER_CONFIG['hdfs_base_path']}/{USER_CONFIG['output_folder']}"


OUTPUT_SCHEMA = {
    "vintage_curves": {
        "dimensions": ["MNE", "COHORT", "TST_GRP_CD", "RPT_GRP_CD", "METRIC", "DAY"],
        "metrics": ["WINDOW_DAYS", "CLIENT_CNT", "SUCCESS_CNT", "RATE"],
        "description": "Cumulative success curves per cell (no lift - dashboard calculates)",
    },
    "channel_breakdown": {
        "dimensions": ["MNE", "COHORT", "TST_GRP_CD", "RPT_GRP_CD", "CHANNEL"],
        "metrics": ["CLIENT_CNT", "SUCCESS_CNT", "RATE"],
        "description": "Summary by channel (not daily curves)",
    },
}

YEARS_TO_INCLUDE = [2025, 2026]

HIVE_PATHS = {
    "tactic_events": "/prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/",
    "visa_debit_card": "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT=",
    "pos_transactions": "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT=",
}

EDW_TABLES = {
    "feedback_master": "DTZV01.VENDOR_FEEDBACK_MASTER",
    "feedback_event": "DTZV01.VENDOR_FEEDBACK_EVENT",
    "pos_log": "DDWV05.CLNT_CRD_POS_LOG",
    "token_list": "DL_DECMAN.TOKEN_LIST",
}


# #############################################################################
#
#                        STAGE 1 DATA — M2 CAMPAIGN
#
# #############################################################################
# These dicts are Stage 1 (hardcoded). In Stage 2+, they are replaced by
# queries to Mnemonic Mapping v2 and the Success Library.

CAMPAIGN_METADATA = {
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
        "secondary_metric": None,
    },
    "VDA": {
        "campaign_name": "VVD Black Friday Cyber Monday Targeted",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
        "secondary_metric": None,
    },
    "VDT": {
        "campaign_name": "VVD Activation Trigger",
        "success_type": "ACTIVATION",
        "primary_metric": "card_activation",
        "secondary_metric": None,
    },
    "VUI": {
        "campaign_name": "VVD Usage Trigger",
        "success_type": "USAGE",
        "primary_metric": "card_usage",
        "secondary_metric": "wallet_provisioning",
    },
    "VUT": {
        "campaign_name": "VVD Tokenization Usage Campaign",
        "success_type": "TOKENIZATION",
        "primary_metric": "wallet_provisioning",
        "secondary_metric": "card_usage",
    },
    "VAW": {
        "campaign_name": "VVD Add To Wallet Contextual Notification",
        "success_type": "TOKENIZATION",
        "primary_metric": "wallet_provisioning",
        "secondary_metric": "card_usage",
    },
}


# #############################################################################
#
#                       STAGE 1 DATA — M3 SUCCESS
#
# #############################################################################
# Each metric is a COMPLETE DATA ASSET: identity + source routing + execution
# config + output contract. Everything needed to calculate success lives here.
#
# Output contract: Every metric must produce CLNT_NO + SUCCESS_DT.
# Source routing: "HIVE" = Spark parquet + PySpark filters
#                 "EDW"  = Teradata cursor + SQL query

SUCCESS_DEFINITIONS = {

    "card_acquisition": {
        "metric_id": "card_acquisition",
        "description": "Client acquired a new VVD card (issued in active/approved status)",
        "version": "1.0",
        "owner": "marketing_analytics",
        "source": "HIVE",
        "output_contract": {
            "client_key": "CLNT_NO",
            "date_key": "SUCCESS_DT",
        },
        "hive": {
            "table_path": HIVE_PATHS["visa_debit_card"],
            "date_field": "ISS_DT",
            "client_field": "CLNT_NO",
            "filters": {
                "STS_CD": ["06", "08"],
                "SRVC_ID": 36,
                "ISS_DT_NOT_NULL": True,
            },
            "add_card_type": True,
        },
        "edw": None,
        "business_rules": [
            "Card status code 06 (Active) or 08 (Approved)",
            "Service ID 36 (Visa Direct)",
            "Issue date must not be null (card was actually issued)",
        ],
    },

    "card_activation": {
        "metric_id": "card_activation",
        "description": "Client activated their VVD card",
        "version": "1.0",
        "owner": "marketing_analytics",
        "source": "HIVE",
        "output_contract": {
            "client_key": "CLNT_NO",
            "date_key": "SUCCESS_DT",
        },
        "hive": {
            "table_path": HIVE_PATHS["visa_debit_card"],
            "date_field": "ACTV_DT",
            "client_field": "CLNT_NO",
            "filters": {
                "STS_CD": ["06", "08"],
                "SRVC_ID": 36,
                "ISS_DT_NOT_NULL": True,
            },
            "add_card_type": True,
        },
        "edw": None,
        "business_rules": [
            "Card status code 06 (Active) or 08 (Approved)",
            "Service ID 36 (Visa Direct)",
            "Issue date must not be null",
            "Activation date (ACTV_DT) is the success event date",
        ],
    },

    "card_usage": {
        "metric_id": "card_usage",
        "description": "Client used their VVD card for a point-of-sale transaction",
        "version": "1.0",
        "owner": "marketing_analytics",
        "source": "HIVE",
        "output_contract": {
            "client_key": "CLNT_NO",
            "date_key": "SUCCESS_DT",
        },
        "hive": {
            "table_path": HIVE_PATHS["pos_transactions"],
            "date_field": "TXN_DT",
            "client_field": "CLNT_NO",
            "filters": {
                "SRVC_CD": 36,
                "TXN_TYPES": [
                    {"TXN_TP": 10, "MSG_TP": "0210"},
                    {"TXN_TP": 13, "MSG_TP": "0210"},
                    {"TXN_TP": 12, "MSG_TP": "0220"},
                ],
                "AMT1_GT": 0,
                "EXTRACT_CLNT_NO": True,
            },
            "add_card_type": False,
        },
        "edw": None,
        "business_rules": [
            "Service code 36 (Visa Direct)",
            "Transaction types: purchase (10/0210), refund (13/0210), cash-back (12/0220)",
            "Amount must be greater than 0",
            "Client number extracted from card number: SUBSTR(CLNT_CRD_NO, 7, 9)",
        ],
    },

    "wallet_provisioning": {
        "metric_id": "wallet_provisioning",
        "description": "Client provisioned their VVD card to a digital wallet",
        "version": "1.0",
        "owner": "marketing_analytics",
        "source": "EDW",
        "output_contract": {
            "client_key": "CLNT_NO",
            "date_key": "SUCCESS_DT",
        },
        "hive": None,
        "edw": {
            "tables": [
                {"alias": "B", "schema": "DDWV05", "table": "CLNT_CRD_POS_LOG", "role": "primary"},
                {"alias": "C", "schema": "DL_DECMAN", "table": "TOKEN_LIST", "role": "join"},
            ],
            "query": """
                SELECT DISTINCT
                    CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER) AS CLNT_NO,
                    B.TXN_DT AS SUCCESS_DT
                FROM {pos_log} AS B
                INNER JOIN {token_list} C
                    ON B.TOKN_REQSTR_ID = C.TOKEN_ID
                WHERE B.AMT1 = 0
                    AND SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190'
                    AND SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'
                    AND SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0'
                    AND B.POS_ENTR_MODE_CD_NON_EMV = '000'
                    AND B.SRVC_CD = 36
                    AND C.TOKEN_WALLET_IND = 'Y'
            """,
            "query_params": {
                "pos_log": "DDWV05.CLNT_CRD_POS_LOG",
                "token_list": "DL_DECMAN.TOKEN_LIST",
            },
            "client_key_logic": "CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER)",
            "date_field_source": "B.TXN_DT",
        },
        "business_rules": [
            "Zero-amount transactions only (AMT1 = 0)",
            "Card BIN prefix 45190 on CLNT_CRD_NO",
            "Visa debit BIN prefix 45199 on VISA_DR_CRD_NO",
            "Valid token requestor (first character > '0')",
            "Non-EMV POS entry mode (000)",
            "Service code 36 (Visa Direct)",
            "Token wallet indicator = Y (from TOKEN_LIST join)",
            "Client number extracted: SUBSTR(CLNT_CRD_NO, 7, 9) cast to INTEGER",
        ],
    },
}


# #############################################################################
#
#                        CONTRACT VALIDATION
#
# #############################################################################
# Every module boundary has a handshake contract. This function validates
# that the producing module met its obligations before passing data forward.
# See: docs/architecture/engine_modules/HANDSHAKE_CONTRACTS.md

def validate_contract(contract_id, df=None, config=None,
                      required_columns=None, required_keys=None, context=""):
    """
    Validate a handshake contract at a module boundary.

    Raises ValueError with clear identification if contract is violated.
    """
    prefix = f"[Contract {contract_id}]"
    if context:
        prefix += f" ({context})"

    if df is not None and required_columns:
        if hasattr(df, 'schema'):  # PySpark DataFrame
            actual = [f.name for f in df.schema.fields]
        else:  # Pandas DataFrame
            actual = list(df.columns)
        missing = [c for c in required_columns if c not in actual]
        if missing:
            raise ValueError(
                f"{prefix} VIOLATION: Missing columns: {missing}. "
                f"Available: {actual}"
            )

    if config is not None and required_keys:
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise ValueError(
                f"{prefix} VIOLATION: Missing keys: {missing}. "
                f"Available: {list(config.keys())}"
            )


# #############################################################################
#
#                    M1: EXPERIMENT METADATA
#                    "Who is in the test?"
#
# #############################################################################
# Entry point: run_experiment(spark, mne, log)
# Output:      dict with tactic_df, tactic_ids, email_channel_df, channels
# Contract:    C1 — validated at exit

def run_experiment(spark, mne, log):
    """
    M1: Load experiment metadata and identify channels.

    Returns dict with:
        tactic_df        — PySpark DataFrame of all experiment clients
        tactic_ids       — list of unique TACTIC_IDs
        email_channel_df — PySpark DataFrame of email-channel clients (or None)
        email_tactic_ids — list of email-channel TACTIC_IDs
        channels         — dict of channel counts
    Returns None if no experiment records found.
    """
    log("\n[M1] Loading experiment data...")
    tactic_df = _load_tactic(spark, mne)
    tactic_df.persist(StorageLevel.MEMORY_AND_DISK)

    tactic_ids = [row.TACTIC_ID for row in tactic_df.select("TACTIC_ID").distinct().collect()]
    log(f"[M1] Unique tactic IDs: {len(tactic_ids):,}")

    if len(tactic_ids) == 0:
        log("[M1] ERROR: No experiment records!")
        tactic_df.unpersist()
        return None

    log("\n[M1] Test groups in data:")
    tactic_df.groupBy("TST_GRP_CD").count().show()
    log("[M1] Report groups in data:")
    tactic_df.groupBy("RPT_GRP_CD").count().show()

    channel_counts = tactic_df.groupBy(
        F.trim(F.col("TACTIC_CELL_CD")).alias("CHANNEL")
    ).count().collect()
    channels = {row["CHANNEL"]: row["count"] for row in channel_counts}
    log(f"[M1] Channels in data: {channels}")

    email_client_count = sum(
        count for ch, count in channels.items() if ch and "EM" in ch
    )
    email_channel_df = None
    email_tactic_ids = []
    if email_client_count > 0:
        email_channel_df = tactic_df.filter(
            F.trim(F.col("TACTIC_CELL_CD")).contains("EM")
        )
        email_tactic_ids = [
            row.TACTIC_ID
            for row in email_channel_df.select("TACTIC_ID").distinct().collect()
        ]

    # Contract C1
    validate_contract("C1", df=tactic_df,
                      required_columns=["CLNT_NO", "TREATMT_STRT_DT", "TREATMT_END_DT",
                                        "TST_GRP_CD", "RPT_GRP_CD", "MNE",
                                        "WINDOW_DAYS", "COHORT"])

    return {
        "tactic_df": tactic_df,
        "tactic_ids": tactic_ids,
        "email_channel_df": email_channel_df,
        "email_tactic_ids": email_tactic_ids,
        "channels": channels,
    }


def _load_tactic(spark, mne):
    """M1 internal: Load and prepare experiment data from tactic_evnt_hist."""
    years = [str(y) for y in YEARS_TO_INCLUDE]
    base_path = HIVE_PATHS["tactic_events"]
    paths = [f"{base_path}EVNT_STRT_DT={year}*" for year in years]

    print(f"    [M1] Loading from partitions: {years}")

    tactic = spark.read.option("basePath", base_path) \
        .parquet(*paths) \
        .filter(F.substring(F.col("TACTIC_ID"), 8, 3) == mne)

    tactic = tactic \
        .withColumn("MNE", F.substring(F.col("TACTIC_ID"), 8, 3)) \
        .withColumn("CLNT_NO", F.regexp_replace(F.trim(F.col("TACTIC_EVNT_ID")), "^0+", "")) \
        .withColumn("TST_GRP_CD", F.trim(F.col("TST_GRP_CD"))) \
        .withColumn("RPT_GRP_CD", F.trim(F.col("RPT_GRP_CD")))

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

    tactic = tactic.withColumn("WINDOW_DAYS", F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT")))
    tactic = tactic.withColumn("COHORT", F.date_format(F.col("TREATMT_STRT_DT"), "yyyy-MM"))
    tactic = tactic.distinct()

    return tactic


# #############################################################################
#
#                    M2: CAMPAIGN MAPPING
#                    "What do we measure?"
#
# #############################################################################
# Entry point: run_campaign(mne, log)
# Output:      campaign config dict
# Contract:    C2 — validated at exit

def run_campaign(mne, log):
    """
    M2: Get campaign mapping and metadata.

    Returns dict with:
        campaign_name    — human-readable campaign name
        success_type     — ACQUISITION, ACTIVATION, USAGE, TOKENIZATION
        primary_metric   — key into SUCCESS_DEFINITIONS
        secondary_metric — key into SUCCESS_DEFINITIONS (or None)
    """
    campaign = CAMPAIGN_METADATA[mne]

    log(f"[M2] Campaign: {campaign['campaign_name']}")
    log(f"[M2] Primary Metric: {campaign['primary_metric']}")
    if campaign.get('secondary_metric'):
        log(f"[M2] Secondary Metric: {campaign['secondary_metric']}")

    # Contract C2
    validate_contract("C2", config=campaign,
                      required_keys=["campaign_name", "success_type", "primary_metric"])

    return campaign


# #############################################################################
#
#                    M3: SUCCESS DEFINITION
#                    "How do we calculate success?"
#
# #############################################################################
# Entry point: run_success(spark, campaign, metric_type, log)
# Output:      dict with df (CLNT_NO + SUCCESS_DT) and config
# Contract:    C3 — validated at exit (SUCCESS_DT enforced)

def run_success(spark, campaign, metric_type, log):
    """
    M3: Load success definition and produce outcome data.

    Takes campaign dict (from M2) and metric_type ("PRIMARY" or "SECONDARY").
    Returns dict with:
        df     — PySpark DataFrame with CLNT_NO + SUCCESS_DT
        config — flat config dict for the engine
    Returns None if the requested metric_type does not exist.
    """
    # Resolve metric name from campaign mapping (M2 output)
    if metric_type == "PRIMARY":
        metric = campaign["primary_metric"]
    elif metric_type == "SECONDARY":
        metric = campaign.get("secondary_metric")
        if metric is None:
            return None
    else:
        return None

    # Get definition and build config
    definition = SUCCESS_DEFINITIONS[metric]
    config = _build_success_config(campaign, definition, metric, metric_type)

    # Load data
    log(f"[M3] Loading {metric_type} success: {metric}...")
    success_df = _load_success_data(spark, config)

    # Enforce output contract: SUCCESS_DT must exist
    if "SUCCESS_DT" not in [f.name for f in success_df.schema.fields]:
        success_df = success_df.withColumn("SUCCESS_DT", F.col(config["success_date_field"]))

    # Contract C3
    validate_contract("C3", df=success_df,
                      required_columns=["CLNT_NO", "SUCCESS_DT"],
                      context=f"metric={metric}")

    return {
        "df": success_df,
        "config": config,
    }


def _build_success_config(campaign, definition, metric, metric_type):
    """M3 internal: Build flat config from campaign + definition."""
    config = {
        "campaign_name": campaign["campaign_name"],
        "success_type": campaign["success_type"],
        "metric_name": metric,
        "metric_type": metric_type,
        "success_source": definition["source"],
        "add_card_type": False,
    }

    if definition["source"] in ("HIVE", "DUAL"):
        hive = definition["hive"]
        config["success_table_path"] = hive["table_path"]
        config["success_date_field"] = hive["date_field"]
        config["filters"] = hive["filters"]
        config["add_card_type"] = hive.get("add_card_type", False)
    elif definition["source"] == "EDW":
        edw = definition["edw"]
        config["success_table_path"] = None
        config["success_date_field"] = definition["output_contract"]["date_key"]
        config["filters"] = None
        config["edw_config"] = edw

    return config


def _load_success_data(spark, config):
    """M3 internal: Load success outcome from Hive or EDW."""
    years_str = [str(y) for y in YEARS_TO_INCLUDE]

    if config["success_source"] == "EDW":
        print(f"    [M3] Loading from EDW ({config['metric_name']})...")
        edw_config = config.get("edw_config")
        token_pdf = _load_from_edw(edw_config)
        print(f"    [M3] Retrieved {len(token_pdf):,} records")
        return spark.createDataFrame(token_pdf)

    paths = [f"{config['success_table_path']}{year}*" for year in years_str]
    print(f"    [M3] Loading from Hive partitions: {years_str}")
    df = spark.read.parquet(*paths)

    df = _apply_success_filters(df, config["metric_name"])

    return df


def _load_from_edw(edw_config):
    """M3 internal: Execute EDW query from cataloged definition."""
    query = edw_config["query"].format(**edw_config["query_params"])

    cursor = EDW.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()

    return pd.DataFrame(rows, columns=columns)


def _apply_success_filters(spark_df, metric_name):
    """
    M3 internal: Apply success definition filters to a raw DataFrame.

    Translates the declarative filter config in
    SUCCESS_DEFINITIONS[metric]["hive"]["filters"] into PySpark operations.
    """
    definition = SUCCESS_DEFINITIONS[metric_name]
    hive_config = definition.get("hive")

    if hive_config is None:
        return spark_df

    filters = hive_config.get("filters")
    if not filters:
        return spark_df

    df = spark_df

    # Check that expected columns exist before filtering
    df_columns = [f.name for f in df.schema.fields]

    if "STS_CD" in filters:
        if "STS_CD" not in df_columns:
            raise ValueError(f"[M3] Filter requires column 'STS_CD' but it does not exist in DataFrame for '{metric_name}'")
        df = df.filter(F.col("STS_CD").isin(filters["STS_CD"]))
    if "SRVC_ID" in filters:
        if "SRVC_ID" not in df_columns:
            raise ValueError(f"[M3] Filter requires column 'SRVC_ID' but it does not exist in DataFrame for '{metric_name}'")
        df = df.filter(F.col("SRVC_ID") == filters["SRVC_ID"])
    if "SRVC_CD" in filters:
        if "SRVC_CD" not in df_columns:
            raise ValueError(f"[M3] Filter requires column 'SRVC_CD' but it does not exist in DataFrame for '{metric_name}'")
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
        df = df.withColumn(
            "CLNT_NO",
            F.regexp_replace(F.substring(F.col("CLNT_CRD_NO"), 7, 9), "^0+", "")
        )

    # Governance: warn on unrecognized filter keys
    recognized_keys = {
        "STS_CD", "SRVC_ID", "SRVC_CD", "TXN_TYPES",
        "ISS_DT_NOT_NULL", "AMT1_GT", "EXTRACT_CLNT_NO",
    }
    unrecognized = set(filters.keys()) - recognized_keys
    if unrecognized:
        print(f"    [M3] WARNING: Unrecognized filter keys for '{metric_name}': {unrecognized}")

    return df


# #############################################################################
#
#                    M5: CLIENT JOURNEY
#                    "What did clients do?"
#
# #############################################################################
# Entry point: run_journey(spark, experiment, include_engagement, log)
# Output:      dict with engagement_df (or None)
# Contract:    C5 — validated at exit

def run_journey(spark, experiment, include_engagement, log):
    """
    M5: Load client journey (engagement) data.

    Takes experiment dict (from M1).
    Returns dict with:
        engagement_df — PySpark DataFrame with engagement flags (or None)
    Returns None if engagement is not requested or no email channel found.
    """
    if not include_engagement:
        return None

    email_tactic_ids = experiment.get("email_tactic_ids", [])
    if not email_tactic_ids:
        return None

    log("[M5] Loading client journey (email engagement)...")
    engagement_df = _load_email_engagement(spark, email_tactic_ids)

    if engagement_df is None:
        return None

    # Contract C5
    validate_contract("C5", df=engagement_df,
                      required_columns=["CLNT_NO", "EMAIL_SENT", "EMAIL_OPENED",
                                        "EMAIL_CLICKED", "EMAIL_UNSUBSCRIBED"])

    return {
        "engagement_df": engagement_df,
    }


def _load_email_engagement(spark, treatment_ids):
    """M5 internal: Load email engagement data from EDW."""
    if not treatment_ids:
        print(f"    [M5] No treatment IDs provided")
        return None

    treatment_id_list = "','".join(treatment_ids)

    print(f"    [M5] Loading EMAIL engagement for {len(treatment_ids):,} tactic IDs...")

    query = f"""
    SELECT DISTINCT
        CAST(FEEDBACK_MASTER.CLNT_NO AS VARCHAR(20)) AS CLNT_NO,
        FEEDBACK_MASTER.TREATMENT_ID,
        'EMAIL' AS CHANNEL,

        MAX(CASE WHEN disposition_cd = 1 THEN 1 ELSE 0 END) AS SENT,
        MAX(CASE WHEN disposition_cd = 2 THEN 1 ELSE 0 END) AS OPENED,
        MAX(CASE WHEN disposition_cd = 3 THEN 1 ELSE 0 END) AS CLICKED,
        MAX(CASE WHEN disposition_cd = 4 THEN 1 ELSE 0 END) AS UNSUBSCRIBED,

        MAX(CASE WHEN disposition_cd = 1 THEN CAST(disposition_dt_tm AS DATE) END) AS SENT_DT,
        MAX(CASE WHEN disposition_cd = 2 THEN CAST(disposition_dt_tm AS DATE) END) AS OPENED_DT,
        MAX(CASE WHEN disposition_cd = 3 THEN CAST(disposition_dt_tm AS DATE) END) AS CLICKED_DT,
        MAX(CASE WHEN disposition_cd = 4 THEN CAST(disposition_dt_tm AS DATE) END) AS UNSUBSCRIBED_DT

    FROM {EDW_TABLES['feedback_master']} FEEDBACK_MASTER
    INNER JOIN {EDW_TABLES['feedback_event']} FEEDBACK_EVENT
        ON FEEDBACK_MASTER.consumer_id_hashed = FEEDBACK_EVENT.consumer_id_hashed
        AND FEEDBACK_MASTER.TREATMENT_ID = FEEDBACK_EVENT.TREATMENT_ID
    WHERE FEEDBACK_MASTER.TREATMENT_ID IN ('{treatment_id_list}')
    GROUP BY FEEDBACK_MASTER.CLNT_NO, FEEDBACK_MASTER.TREATMENT_ID
    """

    try:
        cursor = EDW.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()

        pdf = pd.DataFrame(rows, columns=columns)
        pdf['CLNT_NO'] = pdf['CLNT_NO'].astype(str).str.strip().str.lstrip('0')

        print(f"    [M5] Retrieved {len(pdf):,} email engagement records")

        if pdf.empty:
            return None

        return spark.createDataFrame(pdf)

    except Exception as e:
        print(f"    [M5] Email engagement data not available: {str(e)}")
        return None


# #############################################################################
#
#                    M6: VINTAGE ENGINE
#                    "What are the curves?"
#
# #############################################################################
# Entry point: run_engine(experiment, primary_success, secondary_success,
#                         journey, mne, include_engagement, log)
# Output:      dict with vintage_curves and channel_breakdown
# Contract:    C7 — validated at exit

def run_engine(experiment, primary_success, secondary_success, journey,
               mne, include_engagement, log):
    """
    M6: Build vintage curves from context data.

    Receives separate inputs from M1, M3, M5 and joins them internally.
    Does NOT access any data sources directly.
    """
    tactic_df = experiment["tactic_df"]
    engagement_df = journey["engagement_df"] if journey is not None else None

    # ── PRIMARY ──────────────────────────────────────────────
    log("\n[M6] Processing PRIMARY metric...")
    primary_df = _detect_success(tactic_df, primary_success["df"], primary_success["config"])

    if include_engagement and engagement_df is not None:
        primary_df = _enrich_with_engagement(primary_df, engagement_df)

    primary_df.persist(StorageLevel.MEMORY_AND_DISK)

    log("[M6] Building PRIMARY vintage curves...")
    primary_curves = _build_vintage_curves(primary_df, mne, "PRIMARY")
    log(f"[M6] PRIMARY curves: {len(primary_curves)} rows")

    # ── ENGAGEMENT CURVES ────────────────────────────────────
    engagement_curves = pd.DataFrame()
    if include_engagement and "EMAIL_SENT" in primary_df.columns:
        log("[M6] Building engagement curves...")
        engagement_curves = _build_engagement_curves(
            primary_df, mne, experiment["email_channel_df"]
        )
        log(f"[M6] Engagement curves: {len(engagement_curves)} rows")

    # ── CHANNEL BREAKDOWN ────────────────────────────────────
    log("[M6] Building channel breakdown...")
    channel_breakdown = _build_channel_breakdown(primary_df, mne)

    primary_df.unpersist()

    # ── SECONDARY ────────────────────────────────────────────
    secondary_curves = pd.DataFrame()
    if secondary_success is not None:
        log(f"\n[M6] Processing SECONDARY metric: {secondary_success['config']['metric_name']}...")
        secondary_df = _detect_success(
            tactic_df, secondary_success["df"], secondary_success["config"]
        )
        log("[M6] Building SECONDARY vintage curves...")
        secondary_curves = _build_vintage_curves(secondary_df, mne, "SECONDARY")
        log(f"[M6] SECONDARY curves: {len(secondary_curves)} rows")

    # ── COMBINE ──────────────────────────────────────────────
    all_curves = [primary_curves]
    if not secondary_curves.empty:
        all_curves.append(secondary_curves)
    if not engagement_curves.empty:
        all_curves.append(engagement_curves)
    vintage_curves = pd.concat(all_curves, ignore_index=True)

    # Contract C7
    validate_contract("C7", df=vintage_curves,
                      required_columns=["MNE", "COHORT", "TST_GRP_CD", "RPT_GRP_CD",
                                        "METRIC", "DAY", "WINDOW_DAYS",
                                        "CLIENT_CNT", "SUCCESS_CNT", "RATE"])

    return {
        "vintage_curves": vintage_curves,
        "channel_breakdown": channel_breakdown,
    }


def _detect_success(tactic_df, success_df, config):
    """M6 internal: Join experiment with success outcome."""
    tactic_columns = tactic_df.columns
    tactic_alias = tactic_df.alias("t")

    # M3 guarantees SUCCESS_DT exists (output contract C3)
    success_select = success_df.select(
        F.col("CLNT_NO").alias("SUCCESS_CLNT_NO"),
        F.col("SUCCESS_DT")
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

    groupby_cols = [f"t.{col}" for col in tactic_columns] + ["t.WINDOW_DAYS", "t.COHORT"]

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


def _enrich_with_engagement(success_df, engagement_df):
    """M6 internal: Enrich success data with engagement metrics."""
    result = success_df

    if engagement_df is not None:
        eng_cols = engagement_df.columns

        if "SENT" in eng_cols:
            engagement_select = engagement_df.select(
                F.col("CLNT_NO").alias("ENG_CLNT_NO"),
                F.col("SENT").alias("EMAIL_SENT"),
                F.col("OPENED").alias("EMAIL_OPENED"),
                F.col("CLICKED").alias("EMAIL_CLICKED"),
                F.col("UNSUBSCRIBED").alias("EMAIL_UNSUBSCRIBED"),
                F.col("SENT_DT").alias("EMAIL_SENT_DT"),
                F.col("OPENED_DT").alias("EMAIL_OPENED_DT"),
                F.col("CLICKED_DT").alias("EMAIL_CLICKED_DT"),
                F.col("UNSUBSCRIBED_DT").alias("EMAIL_UNSUBSCRIBED_DT")
            )
        else:
            engagement_select = engagement_df.select(
                F.col("CLNT_NO").alias("ENG_CLNT_NO"),
                F.col("EMAIL_SENT"),
                F.col("EMAIL_OPENED"),
                F.col("EMAIL_CLICKED"),
                F.col("EMAIL_UNSUBSCRIBED"),
                F.col("EMAIL_SENT_DT"),
                F.col("EMAIL_OPENED_DT"),
                F.col("EMAIL_CLICKED_DT"),
                F.col("EMAIL_UNSUBSCRIBED_DT")
            )

        result = result.join(
            engagement_select,
            result["CLNT_NO"] == engagement_select["ENG_CLNT_NO"],
            how="left"
        ).drop("ENG_CLNT_NO")

        for col in ["EMAIL_SENT", "EMAIL_OPENED", "EMAIL_CLICKED", "EMAIL_UNSUBSCRIBED"]:
            if col in result.columns:
                result = result.withColumn(col, F.coalesce(F.col(col), F.lit(0)))

    return result


def _build_vintage_curves(success_df, mne, metric_type="PRIMARY"):
    """M6 internal: Build cumulative success curves."""
    group_cols = ["COHORT", "TST_GRP_CD", "RPT_GRP_CD"]

    totals = success_df.groupBy(group_cols).agg(
        F.count("*").alias("CLIENT_CNT"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )

    successes = success_df.filter(F.col("SUCCESS_FLAG") == 1).groupBy(
        group_cols + ["DAYS_TO_FIRST_SUCCESS"]
    ).agg(F.count("*").alias("SUCCESSES_ON_DAY"))

    vintage = successes.join(totals, on=group_cols, how="right")
    pdf = vintage.toPandas()

    if pdf.empty:
        return pd.DataFrame()

    pdf = pdf.rename(columns={"DAYS_TO_FIRST_SUCCESS": "DAY"})
    pdf = pdf.sort_values(group_cols + ["DAY"])

    complete_rows = []

    for (cohort, tst_grp, rpt_grp), group_data in pdf.groupby(group_cols):
        if group_data.empty:
            continue

        client_cnt = group_data["CLIENT_CNT"].iloc[0]
        window_days = int(group_data["WINDOW_DAYS"].iloc[0]) if pd.notna(group_data["WINDOW_DAYS"].iloc[0]) else 90

        day_successes = group_data.dropna(subset=["DAY"]).set_index("DAY")["SUCCESSES_ON_DAY"].to_dict()

        cum_successes = 0
        max_day = max(int(max(day_successes.keys())) if day_successes else 0, window_days)

        for day in range(0, min(window_days + 1, max_day + 1)):
            if day in day_successes:
                cum_successes += day_successes[day]

            complete_rows.append({
                "MNE": mne,
                "COHORT": cohort,
                "TST_GRP_CD": tst_grp,
                "RPT_GRP_CD": rpt_grp,
                "METRIC": metric_type,
                "DAY": day,
                "WINDOW_DAYS": window_days,
                "CLIENT_CNT": client_cnt,
                "SUCCESS_CNT": cum_successes,
                "RATE": round(cum_successes / client_cnt * 100, 4) if client_cnt > 0 else 0
            })

    result = pd.DataFrame(complete_rows)
    return result


def _build_engagement_curves(success_df, mne, email_channel_df=None):
    """M6 internal: Build engagement vintage curves."""
    columns = success_df.columns

    if "EMAIL_SENT" not in columns:
        return pd.DataFrame()

    all_curves = []

    # EMAIL_SENT curve
    if email_channel_df is not None:
        sent_df = email_channel_df.join(
            success_df.filter(F.col("EMAIL_SENT") == 1).select(
                F.col("CLNT_NO").alias("SENT_CLNT_NO"),
                F.col("EMAIL_SENT_DT")
            ),
            email_channel_df["CLNT_NO"] == F.col("SENT_CLNT_NO"),
            how="left"
        ).drop("SENT_CLNT_NO")

        sent_df = sent_df.withColumn(
            "EMAIL_SENT_FLAG",
            F.when(F.col("EMAIL_SENT_DT").isNotNull(), 1).otherwise(0)
        ).withColumn(
            "DAYS_TO_SENT",
            F.when(F.col("EMAIL_SENT_DT").isNotNull(),
                   F.datediff(F.col("EMAIL_SENT_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None)
        )

        sent_curve = _build_engagement_metric_curve(sent_df, mne, "DAYS_TO_SENT", "EMAIL_SENT_FLAG", "EMAIL_SENT")
        if not sent_curve.empty:
            all_curves.append(sent_curve)

    # Filter to email recipients for open/click/unsub
    email_df = success_df.filter(F.col("EMAIL_SENT") == 1)

    email_df = email_df.withColumn(
        "DAYS_TO_OPEN",
        F.when(F.col("EMAIL_OPENED") == 1,
               F.datediff(F.col("EMAIL_OPENED_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None)
    ).withColumn(
        "DAYS_TO_CLICK",
        F.when(F.col("EMAIL_CLICKED") == 1,
               F.datediff(F.col("EMAIL_CLICKED_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None)
    ).withColumn(
        "DAYS_TO_UNSUB",
        F.when(F.col("EMAIL_UNSUBSCRIBED") == 1,
               F.datediff(F.col("EMAIL_UNSUBSCRIBED_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None)
    )

    open_curve = _build_engagement_metric_curve(email_df, mne, "DAYS_TO_OPEN", "EMAIL_OPENED", "EMAIL_OPEN")
    if not open_curve.empty:
        all_curves.append(open_curve)

    click_curve = _build_engagement_metric_curve(email_df, mne, "DAYS_TO_CLICK", "EMAIL_CLICKED", "EMAIL_CLICK")
    if not click_curve.empty:
        all_curves.append(click_curve)

    unsub_curve = _build_engagement_metric_curve(email_df, mne, "DAYS_TO_UNSUB", "EMAIL_UNSUBSCRIBED", "EMAIL_UNSUB")
    if not unsub_curve.empty:
        all_curves.append(unsub_curve)

    if not all_curves:
        return pd.DataFrame()

    return pd.concat(all_curves, ignore_index=True)


def _build_engagement_metric_curve(df, mne, days_col, flag_col, metric_name):
    """M6 internal: Build curve for a single engagement metric."""
    group_cols = ["COHORT", "TST_GRP_CD", "RPT_GRP_CD"]

    totals = df.groupBy(group_cols).agg(
        F.count("*").alias("CLIENT_CNT"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )

    events = df.filter(F.col(flag_col) == 1).groupBy(
        group_cols + [days_col]
    ).agg(F.count("*").alias("EVENTS_ON_DAY"))

    vintage = events.join(totals, on=group_cols, how="right")
    pdf = vintage.toPandas()

    if pdf.empty:
        return pd.DataFrame()

    pdf = pdf.rename(columns={days_col: "DAY"})
    pdf = pdf.sort_values(group_cols + ["DAY"])

    complete_rows = []

    for (cohort, tst_grp, rpt_grp), group_data in pdf.groupby(group_cols):
        if group_data.empty:
            continue

        client_cnt = group_data["CLIENT_CNT"].iloc[0]
        window_days = int(group_data["WINDOW_DAYS"].iloc[0]) if pd.notna(group_data["WINDOW_DAYS"].iloc[0]) else 90

        day_events = group_data.dropna(subset=["DAY"]).set_index("DAY")["EVENTS_ON_DAY"].to_dict()

        cum_events = 0
        max_day = max(int(max(day_events.keys())) if day_events else 0, window_days)

        for day in range(0, min(window_days + 1, max_day + 1)):
            if day in day_events:
                cum_events += day_events[day]

            complete_rows.append({
                "MNE": mne,
                "COHORT": cohort,
                "TST_GRP_CD": tst_grp,
                "RPT_GRP_CD": rpt_grp,
                "METRIC": metric_name,
                "DAY": day,
                "WINDOW_DAYS": window_days,
                "CLIENT_CNT": client_cnt,
                "SUCCESS_CNT": cum_events,
                "RATE": round(cum_events / client_cnt * 100, 4) if client_cnt > 0 else 0
            })

    return pd.DataFrame(complete_rows)


def _build_channel_breakdown(success_df, mne):
    """M6 internal: Build channel breakdown summary."""
    breakdown = success_df.withColumn(
        "CHANNEL",
        F.trim(F.coalesce(F.col("TACTIC_CELL_CD"), F.lit("UNKNOWN")))
    )

    breakdown = breakdown.groupBy("COHORT", "TST_GRP_CD", "RPT_GRP_CD", "CHANNEL").agg(
        F.count("*").alias("CLIENT_CNT"),
        F.sum("SUCCESS_FLAG").alias("SUCCESS_CNT")
    )

    pdf = breakdown.toPandas()
    pdf["MNE"] = mne
    pdf["RATE"] = (pdf["SUCCESS_CNT"] / pdf["CLIENT_CNT"] * 100).round(2)

    return pdf[["MNE", "COHORT", "TST_GRP_CD", "RPT_GRP_CD", "CHANNEL", "CLIENT_CNT", "SUCCESS_CNT", "RATE"]]


# #############################################################################
#
#                    M7: OUTPUT
#                    "How do we deliver results?"
#
# #############################################################################
# Entry point: run_output(results, mne)
# Input:       results dict from M6

def run_output(results, mne=None):
    """M7: Deliver results to consumer."""
    structure = _detect_result_structure(results)

    if structure == 'flat':
        prefix = f"{mne}_" if mne else ""
        print(f"Creating download links for {mne or 'single campaign'}...")
        print("-" * 40)

        if results.get("vintage_curves") is not None and not results["vintage_curves"].empty:
            _download_csv(results["vintage_curves"], f"{prefix}vintage_curves.csv")

        if results.get("channel_breakdown") is not None and not results["channel_breakdown"].empty:
            _download_csv(results["channel_breakdown"], f"{prefix}channel_breakdown.csv")

    elif structure == 'nested':
        print("Creating download links for all campaigns...")
        print("-" * 40)

        if results.get("_combined_curves") is not None:
            _download_csv(results["_combined_curves"], "vintage_curves.csv")

        if results.get("_combined_channel") is not None:
            _download_csv(results["_combined_channel"], "channel_breakdown.csv")

    else:
        print("ERROR: Could not understand results structure.")


def _detect_result_structure(results):
    """M7 internal: Detect flat vs nested results."""
    if not isinstance(results, dict):
        return 'unknown'
    if "vintage_curves" in results and isinstance(results["vintage_curves"], pd.DataFrame):
        return 'flat'
    for key, value in results.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and "vintage_curves" in value:
            return 'nested'
    return 'unknown'


def _download_csv(data, filename="vintage_results.csv"):
    """M7 internal: Create a clickable download link for a DataFrame."""
    import base64

    csv_data = data.to_csv(index=False)
    size_mb = len(csv_data.encode('utf-8')) / (1024 * 1024)

    if size_mb > 50:
        print(f"Data too large ({size_mb:.1f} MB). Filter before exporting.")
        return

    b64 = base64.b64encode(csv_data.encode()).decode()
    link = (
        f'<a download="{filename}" href="data:text/csv;base64,{b64}" '
        f'style="padding:6px 12px; background:#2196F3; color:white; '
        f'text-decoration:none; border-radius:3px; margin:2px; display:inline-block;">'
        f'Download {filename}</a>'
    )
    display(HTML(f'<div style="margin:5px 0;">{link} <span style="color:#666;">({size_mb:.2f} MB)</span></div>'))


# #############################################################################
#
#                    RUNNER — reads like the DAG
#
# #############################################################################
# This is the orchestrator. Each line is one module.
# See: docs/architecture/engine_modules/EXECUTION_FLOW.md

def run_vintage_analysis(spark, mne, verbose=True, include_engagement=True):
    """
    Run vintage analysis for a campaign.

    Pipeline:
        M1 (Experiment) → M2 (Campaign) → M3 (Success) ──┐
             └──→ M5 (Journey) ───────────────────────────┤
                                                           ▼
                                                     M6 (Engine)
    """
    def log(msg):
        if verbose:
            print(msg)

    log(f"\n{'='*60}")
    log(f"VINTAGE ANALYSIS v2.7: {mne}")
    log(f"{'='*60}")

    # ── M1: Experiment Metadata ─────────────────────────────
    experiment = run_experiment(spark, mne, log)
    if experiment is None:
        return None

    # ── M2: Campaign Mapping ────────────────────────────────
    campaign = run_campaign(mne, log)

    # ── M3: Success Definition (PRIMARY) ────────────────────
    primary_success = run_success(spark, campaign, "PRIMARY", log)

    # ── M3: Success Definition (SECONDARY) ──────────────────
    secondary_success = run_success(spark, campaign, "SECONDARY", log)

    # ── M5: Client Journey ──────────────────────────────────
    journey = run_journey(spark, experiment, include_engagement, log)

    # ── M6: Vintage Engine ──────────────────────────────────
    results = run_engine(
        experiment, primary_success, secondary_success,
        journey, mne, include_engagement, log
    )

    # ── Cleanup ─────────────────────────────────────────────
    experiment["tactic_df"].unpersist()

    # ── Summary ─────────────────────────────────────────────
    vintage_curves = results["vintage_curves"]
    channel_breakdown = results["channel_breakdown"]

    log(f"\n{'='*60}")
    log("OUTPUT SUMMARY")
    log(f"{'='*60}")
    log(f"Vintage curves: {len(vintage_curves)} rows")
    log(f"  Metrics: {vintage_curves['METRIC'].unique().tolist()}")
    log(f"  Test groups: {vintage_curves['TST_GRP_CD'].unique().tolist()}")
    log(f"  Report groups: {vintage_curves['RPT_GRP_CD'].unique().tolist()}")
    log(f"  Cohorts: {vintage_curves['COHORT'].nunique()}")
    log(f"Channel breakdown: {len(channel_breakdown)} rows")

    log(f"\n{'='*60}")
    log(f"COMPLETE: {mne}")
    log(f"{'='*60}")

    return results


def run_all_campaigns(spark, mnes=None, include_engagement=True):
    """Run vintage analysis for multiple campaigns."""
    mnes = mnes or list(CAMPAIGN_METADATA.keys())
    results = {}
    all_curves = []
    all_channel = []

    for mne in mnes:
        try:
            result = run_vintage_analysis(spark, mne, include_engagement=include_engagement)
            if result:
                results[mne] = result
                all_curves.append(result["vintage_curves"])
                all_channel.append(result["channel_breakdown"])
        except Exception as e:
            print(f"ERROR {mne}: {str(e)}")

    if all_curves:
        results["_combined_curves"] = pd.concat(all_curves, ignore_index=True)
        print(f"\nCombined vintage curves: {len(results['_combined_curves'])} rows")

    if all_channel:
        results["_combined_channel"] = pd.concat(all_channel, ignore_index=True)

    return results


# Backward-compatible aliases for M7
download_results = run_output


# #############################################################################
#
#                    SETUP & USAGE
#
# #############################################################################

spark = SparkSession.builder.appName("Vintage Engine v2.7").getOrCreate()

print("""
===============================================================================
                          VINTAGE ENGINE v2.7
===============================================================================

ARCHITECTURE:
  M1 Experiment → M2 Campaign → M3 Success ──┐
       └──→ M5 Journey ──────────────────────┤
                                              ▼
                                        M6 Engine → M7 Output

OUTPUT SCHEMA:
  MNE | COHORT | TST_GRP_CD | RPT_GRP_CD | METRIC | DAY | WINDOW_DAYS | CLIENT_CNT | SUCCESS_CNT | RATE

CHANGES IN v2.7:
  - Code organized into M1-M7 module sections matching architecture docs
  - Module entry points: run_experiment, run_campaign, run_success, run_journey, run_engine
  - Contract validation at module boundaries (runtime enforcement)
  - Runner reads like the DAG

Available campaigns: """ + ", ".join(list(CAMPAIGN_METADATA.keys())) + """

USAGE:

  Step 1: Run analysis
  --------------------
  results = run_vintage_analysis(spark, 'VAW')
  results = run_all_campaigns(spark)

  Step 2: Download
  ----------------
  run_output(results, 'VAW')   # Single campaign
  run_output(results)          # Multiple campaigns

===============================================================================
""")
