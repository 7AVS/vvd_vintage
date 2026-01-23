"""
Vintage Engine v2.1
===================

Changes from v2:
- FIXED: Removed [:5] bug that limited email engagement to 5 tactic IDs
- REMOVED: MODULE_CONTRACTS (visual clutter, no performance impact)
- OPTIMIZED: Reduced unnecessary .count() calls
- ADDED: Validation summary at end of run
- ADDED: User-configurable HDFS paths with Hue link generation

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
from urllib.parse import quote
from IPython.display import HTML, display

# For inline plots in Jupyter
%matplotlib inline

# =============================================================================
# USER CONFIGURATION
# =============================================================================
# UPDATE THESE VALUES for your environment before running.
# =============================================================================

USER_CONFIG = {
    # Your user ID (used in HDFS paths)
    "user_id": "427966379",  # ← CHANGE THIS to your user ID

    # Base HDFS path for output files
    # Files will be saved to: {hdfs_base_path}/{output_folder}/
    "hdfs_base_path": "/user/427966379",  # ← CHANGE THIS to your HDFS home

    # Output folder name
    "output_folder": "vintage_output",
}

# NOTE: Download links use relative paths (/filebrowser/download=...)
# These work automatically when running in Hue/Lumina environment.
# No need to configure Hue URL.

def get_hdfs_output_path():
    """Get the full HDFS output path."""
    return f"{USER_CONFIG['hdfs_base_path']}/{USER_CONFIG['output_folder']}"

def get_hue_download_link(hdfs_path):
    """Generate a Hue file browser link for an HDFS path (opens file in Hue)."""
    # URL encode the path (/ becomes %2F)
    encoded_path = quote(hdfs_path, safe='')
    return f"/hue/filebrowser/view={encoded_path}"

def get_hue_browse_link(hdfs_path):
    """Generate a Hue file browser link for an HDFS path."""
    folder_path = "/".join(hdfs_path.rsplit("/", 1)[:-1]) if "/" in hdfs_path else hdfs_path
    return f"/filebrowser/#/{folder_path}"

def rename_spark_output(spark, temp_folder_path, final_file_path):
    """
    Rename Spark's part-00000*.csv output to a sensible filename.

    Spark writes to folders with part-00000-xxxx.csv files inside.
    This function finds that file and renames it to the desired name.

    Returns: True if successful, False otherwise
    """
    try:
        fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
        temp_path = spark._jvm.org.apache.hadoop.fs.Path(temp_folder_path)

        # Check if temp folder exists
        if not fs.exists(temp_path):
            print(f"    Warning: Temp folder does not exist: {temp_folder_path}")
            return False

        # Find the part-00000*.csv file
        files = fs.listStatus(temp_path)
        csv_file = None

        for f in files:
            name = f.getPath().getName()
            if name.startswith("part-") and name.endswith(".csv"):
                csv_file = f.getPath()
                break

        if csv_file is None:
            print(f"    Warning: No CSV file found in {temp_folder_path}")
            return False

        # Delete target if exists
        final_path = spark._jvm.org.apache.hadoop.fs.Path(final_file_path)
        if fs.exists(final_path):
            fs.delete(final_path, False)

        # Rename the file
        success = fs.rename(csv_file, final_path)

        if success:
            # Clean up temp folder
            fs.delete(temp_path, True)

        return success

    except Exception as e:
        print(f"    Warning: Could not rename file: {str(e)}")
        return False

def display_download_links(exported_files):
    """Display download information in Jupyter notebook."""
    if not exported_files:
        return

    # Get the folder path from the first file
    if exported_files:
        folder_path = "/".join(exported_files[0][1].rsplit("/", 1)[:-1])
    else:
        folder_path = ""

    # Build HTML with both clickable links and plain paths
    html = f"""
    <div style="background:#f5f5f5; padding:10px; border-radius:5px; margin:10px 0;">
        <h4 style="margin-top:0;">Files exported to HDFS:</h4>
        <p><b>Folder:</b> <code>{folder_path}</code></p>
        <p><i>In Hue: Go to File Browser → Navigate to the path above → Click file to download</i></p>
        <table style="width:100%; border-collapse:collapse;">
            <tr style="background:#e0e0e0;">
                <th style="text-align:left; padding:5px;">File</th>
                <th style="text-align:right; padding:5px;">Rows</th>
                <th style="text-align:left; padding:5px;">Full Path</th>
            </tr>
    """

    for name, path, rows in exported_files:
        link = get_hue_download_link(path)
        html += f"""
            <tr style="border-bottom:1px solid #ddd;">
                <td style="padding:5px;"><a href="{link}" target="_blank">{name}</a></td>
                <td style="text-align:right; padding:5px;">{rows:,}</td>
                <td style="padding:5px; font-size:0.9em;"><code>{path}</code></td>
            </tr>
        """

    html += """
        </table>
    </div>
    """

    display(HTML(html))

# =============================================================================
# MODULE REGISTRY
# =============================================================================
# Documents what modules exist, their status, and swap targets.
# =============================================================================

MODULE_REGISTRY = {
    "experiment": {
        "layer": 1,
        "status": "ACTIVE",
        "description": "Identifies who is in test vs control",
        "function": "load_tactic",
        "swap_target": "Experiment Metadata table (when built)",
    },
    "campaign": {
        "layer": 2,
        "status": "ACTIVE",
        "description": "Maps campaign to success metrics",
        "function": "get_campaign_config",
        "swap_target": "Mnemonic Mapping v2 query",
    },
    "success": {
        "layer": 3,
        "status": "ACTIVE",
        "description": "Defines how to calculate each metric",
        "function": "get_success_definition",
        "swap_target": "Success Library (GitHub or curated data)",
    },
    "enrichment": {
        "layer": 4,
        "status": "PLANNED",
        "description": "Adds context: tenure, profitability, region",
        "function": "load_enrichment",
        "swap_target": "Enrichment catalog",
    },
    "journey_email": {
        "layer": 4,
        "status": "ACTIVE",
        "description": "Email engagement: sent, opened, clicked",
        "function": "load_channel_engagement",
    },
    "journey_mobile": {
        "layer": 4,
        "status": "PLANNED",
        "description": "Mobile engagement: banner displayed, clicked",
        "function": "load_channel_engagement",
    },
    "journey_outcome": {
        "layer": 4,
        "status": "ACTIVE",
        "description": "Success outcome (conversion)",
        "function": "load_success_outcome",
    },
    "vintage_engine": {
        "layer": "analysis",
        "status": "ACTIVE",
        "description": "Calculates maturation curves over time",
        "function": "run_vintage_analysis",
    },
}

# =============================================================================
# OUTPUT SCHEMA
# =============================================================================
# Defines what the final output looks like.
# =============================================================================

OUTPUT_SCHEMA = {
    "vintage_curves": {
        "dimensions": ["MNE", "COHORT", "GROUP", "DAY"],
        "optional_dimensions": ["CHANNEL", "SEGMENT"],
        "metrics": ["WINDOW_DAYS", "TEST_CLIENTS", "TEST_SUCCESSES", "TEST_RATE",
                    "CTRL_CLIENTS", "CTRL_SUCCESSES", "CTRL_RATE",
                    "ABS_LIFT", "CI_LOWER", "CI_UPPER", "SIGNIFICANT"],
    },
    "channel_breakdown": {
        "dimensions": ["MNE", "COHORT", "GROUP", "CHANNEL"],
        "metrics": ["CLIENT_COUNT", "SUCCESS_COUNT", "SUCCESS_RATE"],
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
    "tactic_base_path": "/prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/",
    "visa_dr_crd": "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT=",
    "pos_txn": "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT=",
}

# =============================================================================
# SUPPORTED CHANNELS
# =============================================================================

SUPPORTED_CHANNELS = {
    "EMAIL": {"status": "ACTIVE", "code_prefix": "EM"},
    "MOBILE": {"status": "PLANNED", "code_prefix": "MB"},
    "BANNER": {"status": "PLANNED", "code_prefix": "BN"},
}

# =============================================================================
# LAYER 2: CAMPAIGN METADATA
# =============================================================================

CAMPAIGN_METADATA = {
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
        "secondary_metric": None,
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
        "code_path": None,
        "table_path_curated": None,
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

ENRICHMENT_CATALOG = {
    "tenure": {"status": "PLANNED", "segments": ["NEW", "ESTABLISHED", "LONG_TERM"]},
    "profitability": {"status": "PLANNED", "segments": ["HIGH", "MEDIUM", "LOW"]},
    "region": {"status": "PLANNED", "segments": ["EAST", "WEST", "CENTRAL", "ATLANTIC"]},
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

ALL_MNES = list(CAMPAIGN_METADATA.keys())


def get_campaign_config(mne):
    """Layer 2: Get campaign metadata."""
    return CAMPAIGN_METADATA[mne]


def get_success_definition(metric_name):
    """Layer 3: Get success definition."""
    return SUCCESS_DEFINITIONS[metric_name]


def get_full_config(mne):
    """Get combined config for backward compatibility."""
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
    """Print status of all modules."""
    print("\n" + "="*60)
    print("MODULE STATUS")
    print("="*60)
    for name, info in MODULE_REGISTRY.items():
        icon = {"ACTIVE": "[OK]", "PLANNED": "[--]", "PARTIAL": "[~~]"}.get(info["status"], "[??]")
        swap = f" -> {info['swap_target']}" if info.get("swap_target") else ""
        print(f"  {icon} {name}: {info['status']}{swap}")
    print("="*60 + "\n")


# =============================================================================
# LAYER 1: EXPERIMENT MODULE
# =============================================================================

def load_tactic(spark, mne):
    """
    Layer 1: Load experiment metadata from tactic_evnt_hist.
    Identifies WHO is in the test/control groups.
    """
    years = [str(y) for y in YEARS_TO_INCLUDE]
    base_path = PATHS["tactic_base_path"]
    paths = [f"{base_path}EVNT_STRT_DT={year}*" for year in years]

    print(f"    [Layer 1] Loading experiment data from partitions: {years}")

    tactic = spark.read.option("basePath", base_path) \
        .parquet(*paths) \
        .filter(F.substring(F.col("TACTIC_ID"), 8, 3) == mne)

    tactic = tactic \
        .withColumn("MNE", F.substring(F.col("TACTIC_ID"), 8, 3)) \
        .withColumn("CLNT_NO", F.regexp_replace(F.trim(F.col("TACTIC_EVNT_ID")), "^0+", "")) \
        .withColumn("TST_GRP_CD", F.trim(F.col("TST_GRP_CD")))

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
    tactic = tactic.withColumn("GROUP", F.when(F.col("TST_GRP_CD") == TEST_GROUP_CODE, "TEST").otherwise("CONTROL"))
    tactic = tactic.withColumn("COHORT", F.date_format(F.col("TREATMT_STRT_DT"), "yyyy-MM"))

    tactic = tactic.distinct()

    return tactic


# =============================================================================
# LAYER 4: JOURNEY MODULE - FULFILLMENT
# =============================================================================

def load_fulfillment(spark, tactic_ids, channel="EMAIL"):
    """Layer 4: Load fulfillment data. For EMAIL, use SENT from engagement."""
    if channel == "EMAIL":
        print(f"    [Layer 4] Email fulfillment: Using SENT from engagement data")
        return None
    print(f"    [Layer 4] Fulfillment for channel '{channel}' not yet implemented")
    return None


# =============================================================================
# LAYER 4: JOURNEY MODULE - CHANNEL ENGAGEMENT
# =============================================================================

def load_channel_engagement(spark, treatment_ids, channel):
    """
    Layer 4: Load engagement data for a channel.
    Dispatcher - routes to channel-specific loaders.
    """
    channel_upper = channel.upper()

    if channel_upper not in SUPPORTED_CHANNELS:
        print(f"    [Layer 4] Unknown channel: {channel}")
        return None

    if SUPPORTED_CHANNELS[channel_upper]["status"] == "PLANNED":
        print(f"    [Layer 4] Channel '{channel}' is PLANNED but not yet implemented")
        return None

    if channel_upper == "EMAIL":
        return _load_email_engagement(spark, treatment_ids)
    else:
        print(f"    [Layer 4] No loader for channel: {channel}")
        return None


def _load_email_engagement(spark, treatment_ids):
    """
    Internal: Load email engagement data from EDW.

    v2.1 FIX: Now uses ALL treatment_ids, not just first 5.
    """
    if not treatment_ids:
        print(f"    [Layer 4] No treatment IDs provided for email engagement")
        return None

    # v2.1: Use ALL treatment IDs (removed [:5] bug)
    treatment_id_list = "','".join(treatment_ids)

    print(f"    [Layer 4] Loading EMAIL engagement for {len(treatment_ids):,} tactic IDs...")

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


# Backward compatibility
def load_email_engagement(spark, treatment_ids):
    """Alias for backward compatibility."""
    return _load_email_engagement(spark, treatment_ids)


# =============================================================================
# LAYER 4: JOURNEY MODULE - SUCCESS OUTCOME
# =============================================================================

def load_token_from_edw():
    """Layer 4: Load token/provisioning data from EDW."""
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

    return pd.DataFrame(rows, columns=columns)


def load_success_outcome(spark, config):
    """Layer 4: Load success outcome data."""
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


# =============================================================================
# LAYER 4: ENRICHMENT MODULE (PLACEHOLDER)
# =============================================================================

def load_enrichment(spark, client_df, enrichment_type):
    """
    Layer 4: Load enrichment data. STATUS: PLANNED.
    When implemented, returns DataFrame with CLNT_NO, SEGMENT, SEGMENT_TYPE.
    """
    if enrichment_type not in ENRICHMENT_CATALOG:
        print(f"    [Layer 4] Unknown enrichment: {enrichment_type}")
        return None

    if ENRICHMENT_CATALOG[enrichment_type]["status"] == "PLANNED":
        print(f"    [Layer 4] Enrichment '{enrichment_type}' is PLANNED (not yet available)")
        return None

    return None


def enrich_with_segments(success_df, enrichment_df):
    """Add segment data to success DataFrame. Ready when enrichment is available."""
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

    result = result.withColumn("SEGMENT", F.coalesce(F.col("SEGMENT"), F.lit("UNKNOWN")))
    result = result.withColumn("SEGMENT_TYPE", F.coalesce(F.col("SEGMENT_TYPE"), F.lit("NONE")))

    return result


# =============================================================================
# SUCCESS DETECTION
# =============================================================================

def detect_success(tactic_df, success_df, config):
    """Join experiment data with success outcome."""
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
    """Enrich success data with engagement metrics."""
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
                F.col("BOUNCED").alias("EMAIL_BOUNCED"),
                F.col("SENT_DT").alias("EMAIL_SENT_DT"),
                F.col("OPENED_DT").alias("EMAIL_OPENED_DT"),
                F.col("CLICKED_DT").alias("EMAIL_CLICKED_DT"),
                F.col("UNSUBSCRIBED_DT").alias("EMAIL_UNSUBSCRIBED_DT"),
                F.col("BOUNCED_DT").alias("EMAIL_BOUNCED_DT")
            )
        else:
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


# =============================================================================
# VINTAGE ENGINE - Core Calculations
# =============================================================================

def build_vintage_data(success_df):
    """Build vintage curve data."""
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
    """Build channel breakdown."""
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

    # v2.1: Removed .count() call here - we'll know if empty when we get to pandas
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
    """Prepare vintage table with cumulative rates and lift."""
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
    """Generate email engagement summary. Counts derived from aggregated data."""
    columns = success_df.columns

    if "EMAIL_SENT" not in columns:
        return pd.DataFrame([{"MNE": mne, "EMAIL_DATA": "Not available"}])

    # Use aggregation instead of multiple .count() calls
    agg_result = success_df.agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.sum(F.when(F.col("EMAIL_SENT") == 1, 1).otherwise(0)).alias("EMAIL_SENT"),
        F.sum(F.when(F.col("EMAIL_OPENED") == 1, 1).otherwise(0)).alias("EMAIL_OPENED") if "EMAIL_OPENED" in columns else F.lit(0).alias("EMAIL_OPENED"),
        F.sum(F.when(F.col("EMAIL_CLICKED") == 1, 1).otherwise(0)).alias("EMAIL_CLICKED") if "EMAIL_CLICKED" in columns else F.lit(0).alias("EMAIL_CLICKED"),
        F.sum(F.when(F.col("EMAIL_UNSUBSCRIBED") == 1, 1).otherwise(0)).alias("EMAIL_UNSUBSCRIBED") if "EMAIL_UNSUBSCRIBED" in columns else F.lit(0).alias("EMAIL_UNSUBSCRIBED"),
        F.sum(F.when(F.col("EMAIL_BOUNCED") == 1, 1).otherwise(0)).alias("EMAIL_BOUNCED") if "EMAIL_BOUNCED" in columns else F.lit(0).alias("EMAIL_BOUNCED"),
    ).collect()[0]

    total = agg_result["TOTAL_CLIENTS"]
    email_sent = agg_result["EMAIL_SENT"]

    summary_data = {
        "MNE": mne,
        "TOTAL_CLIENTS": total,
        "EMAIL_SENT": email_sent,
        "SEND_RATE": round(email_sent / total * 100, 2) if total > 0 else 0,
        "EMAIL_OPENED": agg_result["EMAIL_OPENED"],
        "OPEN_RATE": round(agg_result["EMAIL_OPENED"] / email_sent * 100, 2) if email_sent > 0 else 0,
        "EMAIL_CLICKED": agg_result["EMAIL_CLICKED"],
        "CLICK_RATE": round(agg_result["EMAIL_CLICKED"] / email_sent * 100, 2) if email_sent > 0 else 0,
        "EMAIL_UNSUBSCRIBED": agg_result["EMAIL_UNSUBSCRIBED"],
        "UNSUB_RATE": round(agg_result["EMAIL_UNSUBSCRIBED"] / email_sent * 100, 2) if email_sent > 0 else 0,
        "EMAIL_BOUNCED": agg_result["EMAIL_BOUNCED"],
        "BOUNCE_RATE": round(agg_result["EMAIL_BOUNCED"] / email_sent * 100, 2) if email_sent > 0 else 0,
    }

    return pd.DataFrame([summary_data])


# =============================================================================
# PLOTTING
# =============================================================================

def plot_vintage(vintage_df, mne, config):
    """Plot vintage curves."""
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
    """Plot grid view."""
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
# VALIDATION SUMMARY
# =============================================================================
# Prints a quick validation check at the end of each run so you can spot issues.
# =============================================================================

def print_validation_summary(mne, results):
    """Print validation summary to help spot data issues."""
    print("\n" + "="*60)
    print(f"VALIDATION SUMMARY: {mne}")
    print("="*60)

    issues = []

    # Check vintage data
    vintage_df = results.get("vintage_df")
    if vintage_df is None or vintage_df.empty:
        issues.append("WARNING: No vintage data generated")
    else:
        n_cohorts = vintage_df["COHORT"].nunique()
        total_test = vintage_df["TEST_CLIENTS"].iloc[0] if not vintage_df.empty else 0
        total_ctrl = vintage_df["CTRL_CLIENTS"].iloc[0] if not vintage_df.empty else 0
        print(f"  Cohorts: {n_cohorts}")
        print(f"  Test clients: {total_test:,}")
        print(f"  Control clients: {total_ctrl:,}")

        if total_test == 0:
            issues.append("WARNING: Zero test clients")
        if total_ctrl == 0:
            issues.append("WARNING: Zero control clients")

    # Check channel breakdown
    channel_df = results.get("channel_breakdown_df")
    if channel_df is not None and not channel_df.empty:
        channels = channel_df["CHANNEL"].unique().tolist()
        print(f"  Channels found: {channels}")
        total_by_channel = channel_df.groupby("CHANNEL")["CLIENT_COUNT"].sum().to_dict()
        for ch, count in total_by_channel.items():
            print(f"    - {ch}: {count:,} clients")

    # Check engagement
    engagement_df = results.get("engagement_summary_df")
    if engagement_df is not None and not engagement_df.empty:
        if "EMAIL_SENT" in engagement_df.columns:
            sent = engagement_df["EMAIL_SENT"].iloc[0]
            opened = engagement_df.get("EMAIL_OPENED", pd.Series([0])).iloc[0]
            clicked = engagement_df.get("EMAIL_CLICKED", pd.Series([0])).iloc[0]
            print(f"  Email sent: {sent:,}")
            print(f"  Email opened: {opened:,}")
            print(f"  Email clicked: {clicked:,}")

            if sent == 0 and any("EM" in str(ch) for ch in (channel_df["CHANNEL"].unique() if channel_df is not None else [])):
                issues.append("WARNING: Email channel exists but EMAIL_SENT=0 - check engagement data")

    # Print issues
    if issues:
        print("\n  ISSUES DETECTED:")
        for issue in issues:
            print(f"    {issue}")
    else:
        print("\n  No issues detected")

    print("="*60)


# =============================================================================
# MAIN RUNNER
# =============================================================================

def run_vintage_analysis(spark, mne, show_plots=True, verbose=True, include_engagement=True, enrichment_types=None):
    """
    Run vintage analysis for a campaign.

    v2.1 improvements:
    - Reduced .count() calls
    - Fixed email tactic ID limitation
    - Added validation summary
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

    config = get_full_config(mne)

    # Layer 1: Load experiment data
    log("\n[Layer 1] Loading experiment data...")
    tactic_df = load_tactic(spark, mne)

    # Cache tactic_df since we use it multiple times
    tactic_df.persist(StorageLevel.MEMORY_AND_DISK)

    # Get tactic IDs (we need this list for engagement query)
    tactic_ids = [row.TACTIC_ID for row in tactic_df.select("TACTIC_ID").distinct().collect()]
    log(f"[Layer 1] Unique tactic IDs: {len(tactic_ids):,}")

    if len(tactic_ids) == 0:
        log("[Layer 1] ERROR: No experiment records!")
        tactic_df.unpersist()
        return None

    # Layer 4: Load client journey data
    log("\n[Layer 4] Loading client journey data...")

    # 4a: Detect channels
    channel_counts = tactic_df.groupBy(F.trim(F.col("TACTIC_CELL_CD")).alias("CHANNEL_TRIMMED")).count().collect()
    channels_in_data = {row["CHANNEL_TRIMMED"]: row["count"] for row in channel_counts}
    log(f"    [Layer 4] Channels in data: {channels_in_data}")

    # 4b: Fulfillment
    fulfillment_df = None
    if include_engagement:
        has_email = any("EM" in ch for ch in channels_in_data.keys() if ch)
        fulfillment_df = load_fulfillment(spark, tactic_ids, channel="EMAIL" if has_email else "OTHER")

    # 4c: Channel engagement
    # v2.1 FIX: Use ALL tactic IDs for email clients, not just first 5
    engagement_df = None
    if include_engagement:
        email_client_count = sum(count for ch, count in channels_in_data.items() if ch and "EM" in ch)
        log(f"    [Layer 4] Email channel clients: {email_client_count:,}")

        if email_client_count > 0:
            email_clients = tactic_df.filter(F.trim(F.col("TACTIC_CELL_CD")).contains("EM"))
            email_tactic_ids = [row.TACTIC_ID for row in email_clients.select("TACTIC_ID").distinct().collect()]

            # v2.1 FIX: Use ALL email tactic IDs (removed [:5] limitation)
            engagement_df = load_channel_engagement(spark, email_tactic_ids, "EMAIL")

    # 4d: Success outcome
    log("\n[Layer 4] Loading success outcome...")
    success_table = load_success_outcome(spark, config)

    # Detect success
    log("\n[Engine] Detecting success...")
    success_df = detect_success(tactic_df, success_table, config)

    # Unpersist tactic_df - we don't need it anymore
    tactic_df.unpersist()

    # Enrich with engagement
    if include_engagement and (engagement_df is not None or fulfillment_df is not None):
        log("[Engine] Enriching with engagement data...")
        success_df = enrich_with_engagement(success_df, engagement_df, fulfillment_df)

    # Enrichment hook
    if enrichment_types:
        log("\n[Layer 4] Loading enrichment data...")
        for enrichment_type in enrichment_types:
            enrichment_df = load_enrichment(spark, success_df, enrichment_type)
            if enrichment_df is not None:
                success_df = enrich_with_segments(success_df, enrichment_df)
                log(f"    [Layer 4] Added enrichment: {enrichment_type}")

    success_df.persist(StorageLevel.MEMORY_AND_DISK)

    # Success summary by group (single aggregation instead of multiple counts)
    log("\n[Engine] Success summary by group:")
    success_df.groupBy("GROUP").agg(
        F.count("*").alias("TOTAL"),
        F.sum("SUCCESS_FLAG").alias("SUCCESSES"),
        F.round(F.avg("SUCCESS_FLAG") * 100, 2).alias("RATE_%")
    ).show()

    # Build vintage curves
    log("\n[Engine] Building vintage curves...")
    vintage_spark = build_vintage_data(success_df)
    vintage_df = prepare_vintage_table(vintage_spark)

    if vintage_df.empty:
        log("[Engine] ERROR: No vintage data!")
        success_df.unpersist()
        return None

    # Channel breakdown
    log("\n[Engine] Building channel breakdown...")
    channel_breakdown_spark = build_channel_breakdown(success_df)
    channel_breakdown_df = channel_breakdown_spark.toPandas()
    channel_breakdown_df["MNE"] = mne
    channel_breakdown_df["SUCCESS_RATE"] = (
        channel_breakdown_df["SUCCESS_COUNT"] / channel_breakdown_df["CLIENT_COUNT"] * 100
    ).round(2)

    # Generate summaries
    log("\n[Engine] Generating summaries...")
    summary_df = generate_summary(vintage_df, mne)
    print(summary_df.to_string(index=False))

    # Engagement summary
    engagement_summary_df = None
    if include_engagement:
        engagement_summary_df = generate_engagement_summary(success_df, mne)
        if not engagement_summary_df.empty and "EMAIL_SENT" in engagement_summary_df.columns:
            log("\n[Layer 4] Engagement Summary:")
            print(engagement_summary_df.to_string(index=False))

    # Engagement vintage
    engagement_vintage_df = None
    if include_engagement and "EMAIL_SENT" in success_df.columns:
        log("\n[Engine] Building engagement vintage curves...")
        engagement_vintage_df = build_engagement_vintage(success_df, mne)

    # Build results dict
    results = {
        "vintage_df": vintage_df,
        "summary_df": summary_df,
        "channel_breakdown_df": channel_breakdown_df,
        "engagement_summary_df": engagement_summary_df,
        "engagement_vintage_df": engagement_vintage_df,
    }

    # Validation summary
    print_validation_summary(mne, results)

    # Plotting
    if show_plots:
        log("\n[Output] Plotting...")
        plot_vintage(vintage_df, mne, config)
        plot_grid(vintage_df, mne, config)

    success_df.unpersist()

    log(f"\n{'='*60}")
    log(f"COMPLETE: {mne}")
    log(f"{'='*60}")

    return results


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
        results["_combined_engagement"] = combined_eng

    if all_channel_breakdown:
        combined_channel = pd.concat(all_channel_breakdown, ignore_index=True)
        results["_combined_channel_breakdown"] = combined_channel

    if all_engagement_vintage:
        combined_eng_vintage = pd.concat(all_engagement_vintage, ignore_index=True)
        results["_combined_engagement_vintage"] = combined_eng_vintage

    return results


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def _detect_result_structure(results):
    """Detect if results are flat (single campaign) or nested (multi-campaign)."""
    if not isinstance(results, dict):
        return 'unknown'
    flat_keys = {'vintage_df', 'summary_df', 'channel_breakdown_df',
                 'engagement_summary_df', 'engagement_vintage_df'}
    if any(key in results for key in flat_keys):
        return 'flat'
    for key, value in results.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and any(k in value for k in flat_keys):
            return 'nested'
    return 'unknown'


def _cleanup_hdfs_folder(spark, folder_path):
    """Delete existing HDFS folder if it exists."""
    try:
        fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
        path = spark._jvm.org.apache.hadoop.fs.Path(folder_path)
        if fs.exists(path):
            fs.delete(path, True)  # True = recursive
            return True
        return False
    except Exception as e:
        print(f"  Warning: Could not clean up folder: {e}")
        return False


def export_results(results, spark, mne=None, base_path=None, clean_first=True):
    """
    SIMPLE EXPORT - Just call this after running vintage analysis.

    Works with both single campaign and multi-campaign results.
    Automatically detects the structure and handles it.

    Usage:
        # Single campaign
        results = run_vintage_analysis(spark, 'VUT')
        export_results(results, spark, 'VUT')

        # Multiple campaigns
        results = run_all_campaigns(spark)
        export_results(results, spark)

    Parameters:
        results: Output from run_vintage_analysis() or run_all_campaigns()
        spark: SparkSession
        mne: Campaign mnemonic (required for single campaign, ignored for multi)
        base_path: HDFS output path (optional, uses USER_CONFIG if not provided)
        clean_first: If True, deletes existing output folder before export (default True)
    """
    if base_path is None:
        base_path = get_hdfs_output_path()

    # Detect structure
    structure = _detect_result_structure(results)

    if structure == 'flat':
        # Single campaign - need MNE
        if mne is None:
            print("ERROR: For single campaign results, you must provide the campaign mnemonic.")
            print("       Example: export_results(results, spark, 'VUT')")
            return None
        # Wrap it
        results_to_export = {mne: results}
        print(f"Single campaign detected: {mne}")
    elif structure == 'nested':
        results_to_export = results
        campaigns = [k for k in results.keys() if not k.startswith("_")]
        print(f"Multiple campaigns detected: {', '.join(campaigns)}")
    else:
        print("ERROR: Could not understand results structure.")
        print("       Make sure you're passing the output from run_vintage_analysis() or run_all_campaigns()")
        return None

    # Clean up existing folder
    if clean_first:
        if _cleanup_hdfs_folder(spark, base_path):
            print(f"Cleaned up existing folder: {base_path}")

    # Now export using the existing function
    return export_all_to_hdfs(results_to_export, spark, base_path)


def export_all_to_hdfs(results, spark, base_path=None):
    """
    Export ALL vintage results to HDFS as separate CSV files.

    Uses USER_CONFIG if base_path not provided.
    Renames Spark output to sensible filenames.
    Displays clickable download links in Jupyter.
    """
    if base_path is None:
        base_path = get_hdfs_output_path()

    exported = []

    def write_and_rename(spark_df, filename, row_count):
        """Helper: Write to temp folder, rename to final file."""
        temp_path = f"{base_path}/_temp_{filename}"
        final_path = f"{base_path}/{filename}"

        # Write to temp folder
        spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(temp_path)

        # Rename part-00000*.csv to sensible name
        if rename_spark_output(spark, temp_path, final_path):
            print(f"  Exported: {filename} ({row_count:,} rows)")
            return (filename, final_path, row_count)
        else:
            # Fallback: keep the folder approach
            print(f"  Exported: {filename} ({row_count:,} rows) [folder]")
            return (filename, temp_path, row_count)

    print(f"\nExporting to HDFS: {base_path}/")
    print("-" * 40)

    # 1. Vintage curves
    all_vintage = []
    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        # Handle both dict format and direct DataFrame
        if isinstance(result, dict) and "vintage_df" in result:
            df = result["vintage_df"].copy()
        elif isinstance(result, pd.DataFrame):
            df = result.copy()
        else:
            print(f"    Warning: Unexpected result format for {mne}: {type(result)}")
            continue
        df["MNE"] = mne
        all_vintage.append(df)

    if all_vintage:
        combined = pd.concat(all_vintage, ignore_index=True)
        spark_df = spark.createDataFrame(combined)
        exported.append(write_and_rename(spark_df, "vintage_curves.csv", len(combined)))

    # 2. Channel breakdown
    all_channel = []
    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        if isinstance(result, dict) and result.get("channel_breakdown_df") is not None:
            all_channel.append(result["channel_breakdown_df"])

    if all_channel:
        combined = pd.concat(all_channel, ignore_index=True)
        spark_df = spark.createDataFrame(combined)
        exported.append(write_and_rename(spark_df, "channel_breakdown.csv", len(combined)))

    # 3. Engagement vintage
    all_eng_vintage = []
    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        if isinstance(result, dict) and result.get("engagement_vintage_df") is not None:
            all_eng_vintage.append(result["engagement_vintage_df"])

    if all_eng_vintage:
        combined = pd.concat(all_eng_vintage, ignore_index=True)
        spark_df = spark.createDataFrame(combined)
        exported.append(write_and_rename(spark_df, "engagement_vintage.csv", len(combined)))

    # 4. Summary
    all_summary = []
    for mne, result in results.items():
        if mne.startswith("_") or result is None:
            continue
        if isinstance(result, dict) and result.get("summary_df") is not None:
            all_summary.append(result["summary_df"])

    if all_summary:
        combined = pd.concat(all_summary, ignore_index=True)
        spark_df = spark.createDataFrame(combined)
        exported.append(write_and_rename(spark_df, "summary.csv", len(combined)))

    # Print summary
    print("-" * 40)
    print(f"EXPORT COMPLETE: {len(exported)} files to {base_path}/")

    # Display clickable download links in Jupyter
    display_download_links(exported)

    return exported


def export_to_hdfs_csv(results, spark, hdfs_path=None):
    """Export vintage results to HDFS as single CSV (legacy)."""
    if hdfs_path is None:
        hdfs_path = f"{get_hdfs_output_path()}/vintage_data.csv"

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

    # Write to temp, then rename
    temp_path = hdfs_path.replace(".csv", "_temp.csv")
    spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(temp_path)

    if rename_spark_output(spark, temp_path, hdfs_path):
        print(f"Exported to HDFS: {hdfs_path}")
    else:
        print(f"Exported to HDFS: {temp_path} (folder)")
        hdfs_path = temp_path

    print(f"Rows: {len(combined):,}")

    # Display clickable link
    display_download_links([("vintage_data.csv", hdfs_path, len(combined))])

    return hdfs_path


# =============================================================================
# BROWSER DOWNLOAD FUNCTIONS
# =============================================================================
# For environments where HDFS download links don't work (e.g., Jupyter on
# separate server from Hue). Creates base64-encoded download links that work
# directly in the browser.
# =============================================================================

def download_csv(data, filename="vintage_results.csv"):
    """
    Create a clickable download link for a DataFrame.

    Converts DataFrame to CSV, base64-encodes it, and displays an HTML link
    that triggers a browser download. Works in Jupyter notebooks when HDFS
    download links are inaccessible.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame to download.
    filename : str, optional
        Name for the downloaded file (default: "vintage_results.csv").

    Returns
    -------
    None
        Displays an HTML download link in the notebook.

    Notes
    -----
    - Maximum file size: 50 MB (to avoid browser memory issues)
    - For larger datasets, filter before exporting
    """
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


def download_results(results, mne=None):
    """
    Download all result DataFrames with one call.

    Creates browser download links for vintage_df, summary_df,
    channel_breakdown_df, and engagement_vintage_df. Works with both
    single-campaign and multi-campaign results.

    Parameters
    ----------
    results : dict
        Output from run_vintage_analysis() or run_all_campaigns().
    mne : str, optional
        Campaign mnemonic. Required for single-campaign results to name files.
        Ignored for multi-campaign results (uses combined data).

    Returns
    -------
    None
        Displays HTML download links in the notebook.

    Examples
    --------
    # Single campaign
    results = run_vintage_analysis(spark, 'VUT')
    download_results(results, 'VUT')

    # Multiple campaigns
    results = run_all_campaigns(spark)
    download_results(results)
    """
    structure = _detect_result_structure(results)

    if structure == 'flat':
        # Single campaign results
        prefix = f"{mne}_" if mne else ""
        print(f"Creating download links for {mne or 'single campaign'}...")
        print("-" * 40)

        if results.get("vintage_df") is not None and not results["vintage_df"].empty:
            download_csv(results["vintage_df"], f"{prefix}vintage_curves.csv")

        if results.get("summary_df") is not None and not results["summary_df"].empty:
            download_csv(results["summary_df"], f"{prefix}summary.csv")

        if results.get("channel_breakdown_df") is not None and not results["channel_breakdown_df"].empty:
            download_csv(results["channel_breakdown_df"], f"{prefix}channel_breakdown.csv")

        if results.get("engagement_vintage_df") is not None and not results["engagement_vintage_df"].empty:
            download_csv(results["engagement_vintage_df"], f"{prefix}engagement_vintage.csv")

    elif structure == 'nested':
        # Multi-campaign results - combine all data
        print("Creating download links for all campaigns...")
        print("-" * 40)

        # Vintage curves
        all_vintage = []
        for key, result in results.items():
            if key.startswith("_") or result is None:
                continue
            if isinstance(result, dict) and result.get("vintage_df") is not None:
                df = result["vintage_df"].copy()
                df["MNE"] = key
                all_vintage.append(df)
        if all_vintage:
            download_csv(pd.concat(all_vintage, ignore_index=True), "vintage_curves.csv")

        # Summary
        if results.get("_combined_summary") is not None:
            download_csv(results["_combined_summary"], "summary.csv")
        else:
            all_summary = []
            for key, result in results.items():
                if key.startswith("_") or result is None:
                    continue
                if isinstance(result, dict) and result.get("summary_df") is not None:
                    all_summary.append(result["summary_df"])
            if all_summary:
                download_csv(pd.concat(all_summary, ignore_index=True), "summary.csv")

        # Channel breakdown
        if results.get("_combined_channel_breakdown") is not None:
            download_csv(results["_combined_channel_breakdown"], "channel_breakdown.csv")
        else:
            all_channel = []
            for key, result in results.items():
                if key.startswith("_") or result is None:
                    continue
                if isinstance(result, dict) and result.get("channel_breakdown_df") is not None:
                    all_channel.append(result["channel_breakdown_df"])
            if all_channel:
                download_csv(pd.concat(all_channel, ignore_index=True), "channel_breakdown.csv")

        # Engagement vintage
        if results.get("_combined_engagement_vintage") is not None:
            download_csv(results["_combined_engagement_vintage"], "engagement_vintage.csv")
        else:
            all_eng = []
            for key, result in results.items():
                if key.startswith("_") or result is None:
                    continue
                if isinstance(result, dict) and result.get("engagement_vintage_df") is not None:
                    all_eng.append(result["engagement_vintage_df"])
            if all_eng:
                download_csv(pd.concat(all_eng, ignore_index=True), "engagement_vintage.csv")

    else:
        print("ERROR: Could not understand results structure.")
        print("       Pass output from run_vintage_analysis() or run_all_campaigns()")


# =============================================================================
# SETUP & USAGE
# =============================================================================

spark = SparkSession.builder.appName("Vintage Engine v2.1").getOrCreate()

print_module_status()

print("""
===============================================================================
                          VINTAGE ENGINE v2.1
===============================================================================

Available campaigns: """ + ", ".join(ALL_MNES) + """

USAGE:

  Step 1: Run analysis
  --------------------
  results = run_vintage_analysis(spark, 'VUT')   # Single campaign
  results = run_all_campaigns(spark)              # All campaigns

  Step 2: Export (choose one)
  ---------------------------
  # Option A: HDFS export (if Hue download links work)
  export_results(results, spark, 'VUT')           # Single campaign
  export_results(results, spark)                  # Multiple campaigns

  # Option B: Browser download (if HDFS links don't work)
  download_results(results, 'VUT')                # Single campaign
  download_results(results)                       # Multiple campaigns

  # Option C: Download individual DataFrame
  download_csv(results['vintage_df'], 'my_data.csv')

HDFS output folder: """ + get_hdfs_output_path() + """
===============================================================================
""")
