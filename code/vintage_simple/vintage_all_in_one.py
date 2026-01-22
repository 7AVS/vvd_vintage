"""
Vintage Curve Analysis Engine
=============================

Architecture aligned with SuperFact 4-Layer Framework:
- Layer 1: Experiment Metadata (tactic_evnt_hist) - "Who is in test?"
- Layer 2: Campaign Metadata (CAMPAIGN_METADATA) - "What to measure?"
- Layer 3: Success Definitions (SUCCESS_DEFINITIONS) - "How to calculate?"
- Layer 4: Client Journey (fulfillment, engagement, outcome) - "What actually happened?"

SWAP POINTS documented for future migration:
- Layer 2: Replace CAMPAIGN_METADATA with query to Mnemonic Mapping v2
- Layer 3: Replace SUCCESS_DEFINITIONS with Success Library (GitHub or curated data)
- Layer 4: Expand to unified Client Journey table when available

Copy this entire file into a Jupyter notebook cell and run.
For HDFS/Yarn environments (Lumina): Plots display inline, data returned as DataFrames.
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
# LAYER 2: CAMPAIGN METADATA
# =============================================================================
# Defines WHAT to measure for each campaign.
# Maps campaign MNE to success metric type.
#
# SWAP POINT: When Mnemonic Mapping v2 has Primary/Secondary/Tertiary metric
# fields, replace this dict with a query:
#   SELECT primary_metric, secondary_metric FROM mnemonic_mapping_v2 WHERE mne = '{mne}'
# =============================================================================

CAMPAIGN_METADATA = {
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
        # Channel is NOT hardcoded - comes from TACTIC_CELL_CD in tactic data
    },
    "VDA": {
        "campaign_name": "VVD Black Friday Cyber Monday Targeted",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
    },
    "VDT": {
        "campaign_name": "VVD Activation Trigger",
        "success_type": "ACTIVATION",
        "primary_metric": "card_activation",
    },
    "VUI": {
        "campaign_name": "VVD Usage Trigger",
        "success_type": "USAGE",
        "primary_metric": "card_usage",
    },
    "VUT": {
        "campaign_name": "VVD Tokenization Usage Campaign",
        "success_type": "TOKENIZATION",
        "primary_metric": "wallet_provisioning",
    },
    "VAW": {
        "campaign_name": "VVD Add To Wallet Contextual Notification",
        "success_type": "TOKENIZATION",
        "primary_metric": "wallet_provisioning",
    },
}

# =============================================================================
# LAYER 3: SUCCESS DEFINITIONS
# =============================================================================
# Defines HOW to calculate each success metric.
# Contains source tables, filters, and logic.
#
# SWAP POINT: When Success Library exists (GitHub repo or curated data set),
# replace this dict with:
#   Option A: %Run from GitHub - pull SQL/logic snippet
#   Option B: Query curated data set directly
# =============================================================================

SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "description": "Client acquired a new VVD card",
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
    },
    "card_activation": {
        "description": "Client activated their VVD card",
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
    },
    "card_usage": {
        "description": "Client used their VVD card for a transaction",
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
    },
    "wallet_provisioning": {
        "description": "Client provisioned card to digital wallet",
        "source": "EDW",
        "date_field": "TXN_DT",
        "client_field": "CLNT_NO",
        "filters": None,
        "add_card_type": False,
    },
}

# =============================================================================
# HELPER: Get configs for a campaign
# =============================================================================

ALL_MNES = list(CAMPAIGN_METADATA.keys())

def get_campaign_config(mne):
    """Get Layer 2 campaign metadata."""
    return CAMPAIGN_METADATA[mne]

def get_success_definition(metric_name):
    """Get Layer 3 success definition."""
    return SUCCESS_DEFINITIONS[metric_name]

def get_full_config(mne):
    """Get combined config for backward compatibility."""
    campaign = CAMPAIGN_METADATA[mne]
    metric = campaign["primary_metric"]
    success = SUCCESS_DEFINITIONS[metric]

    # Merge for backward compatibility with existing functions
    # Note: Channel is NOT included here - it comes from tactic data (TACTIC_CELL_CD)
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

# =============================================================================
# LAYER 1: EXPERIMENT METADATA
# =============================================================================
# Loads tactic data - identifies who is in test vs control.
# Source: tactic_evnt_hist (parquet)
#
# SWAP POINT: When Experiment Metadata table is built with enriched fields
# (Experiment Name, Type, Purpose, Hypothesis), query it for test group
# definitions instead of hardcoding TEST_GROUP_CODE.
# =============================================================================

def load_tactic(spark, mne):
    """
    Layer 1: Load experiment metadata from tactic_evnt_hist.

    Identifies WHO is in the test/control groups.

    Source: /prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/
    Partition: EVNT_STRT_DT={year}*

    Key transformations:
    - MNE: extracted from TACTIC_ID positions 8-10
    - CLNT_NO: TACTIC_EVNT_ID trimmed with leading zeros removed
    - GROUP: TG4 = Test, others = Control (SWAP POINT: query metadata table)
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
        F.col("RPT_GRP_CD"),          # For future segment filtering
        F.col("TREATMT_MN"),
        F.col("TACTIC_CELL_CD"),
        F.col("STRTGY_SRC_CD"),
        F.col("ADDNL_DECISN_DATA1"),  # Flexible field - may contain channel
        F.col("ADDNL_DECISN_DATA2"),
        F.col("ADDNL_DECISN_DATA3"),
        F.col("MNE"),
    )

    # Derived columns
    tactic = tactic.withColumn("WINDOW_DAYS", F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT")))

    # SWAP POINT: When Experiment Metadata table exists, query it for test group definition
    # instead of hardcoding TEST_GROUP_CODE
    tactic = tactic.withColumn("GROUP", F.when(F.col("TST_GRP_CD") == TEST_GROUP_CODE, "TEST").otherwise("CONTROL"))
    tactic = tactic.withColumn("COHORT", F.date_format(F.col("TREATMT_STRT_DT"), "yyyy-MM"))

    tactic = tactic.distinct()

    return tactic

# =============================================================================
# LAYER 4: CLIENT JOURNEY - FULFILLMENT
# =============================================================================
# Verifies that the contact was actually delivered.
# For EMAIL channel: fulfillment = email was sent (disposition_cd=1 in VENDOR_FEEDBACK)
# For other channels: would need separate fulfillment tracking
#
# NOTE: For email campaigns, we use EMAIL_SENT from load_email_engagement() as
# the fulfillment indicator. This function returns None for email-only analysis.
# =============================================================================

def load_fulfillment(spark, tactic_ids, channel="EMAIL"):
    """
    Layer 4: Load fulfillment data to verify contact delivery.

    For EMAIL channel: Returns None - use EMAIL_SENT from load_email_engagement()
    For other channels: Would query channel-specific fulfillment source

    The concept of fulfillment varies by channel:
    - EMAIL: email was sent (disposition_cd=1)
    - MOBILE: banner was displayed
    - ONB: offer was shown in online banking
    - ONO: lead was delivered to advisory centre
    """
    if channel == "EMAIL":
        # For email, fulfillment = email sent, which is captured in load_email_engagement()
        print(f"    [Layer 4] Email fulfillment: Using EMAIL_SENT from engagement data")
        return None

    # Placeholder for future channel-specific fulfillment
    print(f"    [Layer 4] Fulfillment for channel '{channel}' not yet implemented")
    return None

# =============================================================================
# LAYER 4: CLIENT JOURNEY - EMAIL ENGAGEMENT
# =============================================================================
# Tracks email engagement metrics.
# Answers: "Did the client receive/open/click the email?"
#
# Source: VENDOR_FEEDBACK_MASTER + VENDOR_FEEDBACK_EVENT (Teradata via EDW)
# =============================================================================

def load_email_engagement(spark, treatment_ids):
    """
    Layer 4: Load email engagement data.

    Tracks the email funnel: sent → delivered → opened → clicked

    Source: DTZV01.VENDOR_FEEDBACK_MASTER + DTZV01.VENDOR_FEEDBACK_EVENT

    Disposition codes:
    - 1 = email_sent
    - 2 = email_opened
    - 3 = email_clicked
    - 4 = email_unsubscribed
    - 5 = email_hardbounce

    Returns DataFrame with:
    - CLNT_NO, TREATMENT_ID
    - EMAIL_SENT, EMAIL_SENT_DT (also serves as fulfillment for email channel)
    - EMAIL_OPENED, EMAIL_OPENED_DT
    - EMAIL_CLICKED, EMAIL_CLICKED_DT
    - EMAIL_UNSUBSCRIBED, EMAIL_UNSUBSCRIBED_DT
    - EMAIL_BOUNCED, EMAIL_BOUNCED_DT
    """
    # Build treatment_id filter
    treatment_id_list = "','".join(treatment_ids) if treatment_ids else ""

    query = f"""
    SELECT DISTINCT
        CAST(FEEDBACK_MASTER.CLNT_NO AS VARCHAR(20)) AS CLNT_NO,
        FEEDBACK_MASTER.TREATMENT_ID,

        MAX(CASE WHEN disposition_cd = 1 THEN 1 ELSE 0 END) AS EMAIL_SENT,
        MAX(CASE WHEN disposition_cd = 2 THEN 1 ELSE 0 END) AS EMAIL_OPENED,
        MAX(CASE WHEN disposition_cd = 3 THEN 1 ELSE 0 END) AS EMAIL_CLICKED,
        MAX(CASE WHEN disposition_cd = 4 THEN 1 ELSE 0 END) AS EMAIL_UNSUBSCRIBED,
        MAX(CASE WHEN disposition_cd = 5 THEN 1 ELSE 0 END) AS EMAIL_BOUNCED,

        MAX(CASE WHEN disposition_cd = 1 THEN CAST(disposition_dt_tm AS DATE) END) AS EMAIL_SENT_DT,
        MAX(CASE WHEN disposition_cd = 2 THEN CAST(disposition_dt_tm AS DATE) END) AS EMAIL_OPENED_DT,
        MAX(CASE WHEN disposition_cd = 3 THEN CAST(disposition_dt_tm AS DATE) END) AS EMAIL_CLICKED_DT,
        MAX(CASE WHEN disposition_cd = 4 THEN CAST(disposition_dt_tm AS DATE) END) AS EMAIL_UNSUBSCRIBED_DT,
        MAX(CASE WHEN disposition_cd = 5 THEN CAST(disposition_dt_tm AS DATE) END) AS EMAIL_BOUNCED_DT

    FROM DTZV01.VENDOR_FEEDBACK_MASTER FEEDBACK_MASTER
    INNER JOIN DTZV01.VENDOR_FEEDBACK_EVENT FEEDBACK_EVENT
        ON FEEDBACK_MASTER.consumer_id_hashed = FEEDBACK_EVENT.consumer_id_hashed
        AND FEEDBACK_MASTER.TREATMENT_ID = FEEDBACK_EVENT.TREATMENT_ID
    WHERE FEEDBACK_MASTER.TREATMENT_ID IN ('{treatment_id_list}')
    GROUP BY FEEDBACK_MASTER.CLNT_NO, FEEDBACK_MASTER.TREATMENT_ID
    """

    print(f"    [Layer 4] Loading email engagement data from EDW...")

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

# =============================================================================
# LAYER 4: CLIENT JOURNEY - SUCCESS OUTCOME
# =============================================================================
# Checks if the client achieved the success metric.
# Answers: "Did the client convert (acquire card, activate, transact, etc.)?"
#
# Sources: VISA_DR_CRD, POS_TXN, EDW (depending on success type)
# =============================================================================

def load_token_from_edw():
    """
    Layer 4: Load token/provisioning data from EDW.

    For wallet provisioning success metric.
    Source: DDWV05.CLNT_CRD_POS_LOG + DL_DECMAN.TOKEN_LIST
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

    Checks if client achieved the success metric (conversion).

    Sources (depending on config):
    - HIVE: VISA_DR_CRD, POS_TXN (parquet)
    - EDW: Token/provisioning data
    """
    years_str = [str(y) for y in YEARS_TO_INCLUDE]

    # Handle EDW source (Token/Provisioning)
    if config["success_source"] == "EDW":
        print("    [Layer 4] Loading success outcome from EDW (token)...")
        token_pdf = load_token_from_edw()
        print(f"    [Layer 4] Retrieved {len(token_pdf):,} token records")
        return spark.createDataFrame(token_pdf)

    # Handle HIVE sources
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
    """Alias for load_success_outcome for backward compatibility."""
    return load_success_outcome(spark, config)

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


def enrich_with_engagement(success_df, email_df, fulfillment_df):
    """
    Enrich success data with email engagement and fulfillment metrics.

    Adds Layer 4 context: Was email sent? Opened? Clicked? Was contact fulfilled?
    """
    result = success_df

    # Add email engagement if available
    if email_df is not None:
        email_select = email_df.select(
            F.col("CLNT_NO").alias("EMAIL_CLNT_NO"),
            F.col("EMAIL_SENT"),
            F.col("EMAIL_OPENED"),
            F.col("EMAIL_CLICKED"),
            F.col("EMAIL_UNSUBSCRIBED"),
            F.col("EMAIL_BOUNCED")
        )
        result = result.join(
            email_select,
            result["CLNT_NO"] == email_select["EMAIL_CLNT_NO"],
            how="left"
        ).drop("EMAIL_CLNT_NO")

        # Fill nulls with 0
        for col in ["EMAIL_SENT", "EMAIL_OPENED", "EMAIL_CLICKED", "EMAIL_UNSUBSCRIBED", "EMAIL_BOUNCED"]:
            result = result.withColumn(col, F.coalesce(F.col(col), F.lit(0)))

    # Add fulfillment if available
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
# VINTAGE CALCULATIONS - The Engine (Layer-agnostic)
# =============================================================================
# This is the core calculation engine. It takes data from the layers above
# and produces vintage curves, lift, and confidence intervals.
# This does NOT change when data sources change - it's the stable core.
# =============================================================================

def build_vintage_data(success_df):
    """Build vintage curve data from success detection results.

    Groups by COHORT, GROUP, and CHANNEL (TACTIC_CELL_CD) to allow
    dashboard filtering by channel.
    """
    # Add CHANNEL column from TACTIC_CELL_CD (coalesce nulls to 'ALL')
    success_df = success_df.withColumn(
        "CHANNEL",
        F.coalesce(F.col("TACTIC_CELL_CD"), F.lit("ALL"))
    )

    group_cols = ["COHORT", "GROUP", "CHANNEL"]

    totals = success_df.groupBy(group_cols).agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )
    successes = success_df.filter(F.col("SUCCESS_FLAG") == 1).groupBy(
        group_cols + ["DAYS_TO_FIRST_SUCCESS"]
    ).agg(F.count("*").alias("SUCCESSES_ON_DAY"))
    vintage = successes.join(totals, on=group_cols, how="left")
    return vintage.orderBy("COHORT", "CHANNEL", "GROUP", "DAYS_TO_FIRST_SUCCESS")


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
    """Prepare vintage table with cumulative rates and lift calculations.

    Now includes CHANNEL for dashboard filtering.
    """
    pdf = vintage_spark_df.toPandas()
    if pdf.empty:
        return pdf

    # Handle CHANNEL column (may not exist in older data)
    has_channel = "CHANNEL" in pdf.columns
    if not has_channel:
        pdf["CHANNEL"] = "ALL"

    group_cols = ["COHORT", "CHANNEL", "GROUP"]
    pdf = pdf.sort_values(group_cols + ["DAYS_TO_FIRST_SUCCESS"])
    pdf["CUMULATIVE_SUCCESSES"] = pdf.groupby(group_cols)["SUCCESSES_ON_DAY"].cumsum()
    pdf["CUMULATIVE_RATE"] = pdf["CUMULATIVE_SUCCESSES"] / pdf["TOTAL_CLIENTS"] * 100
    pdf = pdf.rename(columns={"DAYS_TO_FIRST_SUCCESS": "DAY"})

    # Get unique combinations
    cohorts = pdf["COHORT"].unique()
    channels = pdf["CHANNEL"].unique()
    complete_rows = []

    for cohort in cohorts:
        for channel in channels:
            for group in ["TEST", "CONTROL"]:
                data = pdf[(pdf["COHORT"] == cohort) & (pdf["CHANNEL"] == channel) & (pdf["GROUP"] == group)]
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
                        "COHORT": cohort, "CHANNEL": channel, "GROUP": group, "DAY": day,
                        "WINDOW_DAYS": window_days, "TOTAL_CLIENTS": total_clients,
                        "CUMULATIVE_SUCCESSES": cum_successes,
                        "CUMULATIVE_RATE": cum_successes / total_clients * 100 if total_clients > 0 else 0
                    })

    complete_df = pd.DataFrame(complete_rows)

    lift_rows = []
    for cohort in cohorts:
        for channel in channels:
            cdata = complete_df[(complete_df["COHORT"] == cohort) & (complete_df["CHANNEL"] == channel)]
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
                    "COHORT": cohort, "CHANNEL": channel, "DAY": day, "WINDOW_DAYS": window_days,
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

    # Group by COHORT and CHANNEL (if present) to get final day
    group_cols = ["COHORT"]
    if "CHANNEL" in lift_df.columns:
        group_cols.append("CHANNEL")

    final = lift_df.loc[lift_df.groupby(group_cols)["DAY"].idxmax()].copy()
    final["MNE"] = mne

    # Build column list based on what's available
    cols = ["MNE", "COHORT"]
    if "CHANNEL" in lift_df.columns:
        cols.append("CHANNEL")
    cols.extend(["WINDOW_DAYS", "TEST_CLIENTS", "TEST_SUCCESSES", "TEST_RATE",
                 "CTRL_CLIENTS", "CTRL_SUCCESSES", "CTRL_RATE", "ABS_LIFT", "CI_LOWER", "CI_UPPER", "SIGNIFICANT"])

    return final[cols].sort_values(group_cols)


def generate_engagement_summary(success_df, mne):
    """Generate email engagement summary with funnel metrics.

    Rates are calculated as:
    - SEND_RATE: emails sent / total clients in experiment
    - OPEN_RATE: emails opened / emails sent
    - CLICK_RATE: emails clicked / emails sent
    - UNSUB_RATE: unsubscribes / emails sent
    """
    columns = success_df.columns

    summary_data = {"MNE": mne}

    total = success_df.count()
    summary_data["TOTAL_CLIENTS"] = total

    email_sent = 0
    if "EMAIL_SENT" in columns:
        email_sent = success_df.filter(F.col("EMAIL_SENT") == 1).count()
        summary_data["EMAIL_SENT"] = email_sent
        summary_data["SEND_RATE"] = round(email_sent / total * 100, 2) if total > 0 else 0

    # Rates below are calculated based on emails sent (the actual audience)
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

def run_vintage_analysis(spark, mne, show_plots=True, verbose=True, include_engagement=True):
    """
    Run vintage analysis for a campaign.

    Flows through all 4 layers:
    1. Layer 1: Load experiment data (tactic)
    2. Layer 2: Get campaign metadata (what to measure)
    3. Layer 3: Get success definition (how to calculate)
    4. Layer 4: Load client journey (fulfillment, engagement, outcome)
    5. Vintage Engine: Calculate curves, lift, CI

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

    # 4a: Check what channels exist in the tactic data
    # Channel comes from TACTIC_CELL_CD - NOT hardcoded
    channel_counts = tactic_df.groupBy("TACTIC_CELL_CD").count().collect()
    channels_in_data = {row["TACTIC_CELL_CD"]: row["count"] for row in channel_counts}
    log(f"    [Layer 4] Channels in data: {channels_in_data}")

    # 4b: Fulfillment - for email, this is captured via EMAIL_SENT
    fulfillment_df = None
    if include_engagement:
        # Check if there are email clients - fulfillment for email = email sent
        has_email = "EM" in channels_in_data and channels_in_data["EM"] > 0
        fulfillment_df = load_fulfillment(spark, tactic_ids, channel="EMAIL" if has_email else "OTHER")

    # 4c: Email engagement (only for clients with TACTIC_CELL_CD = 'EM')
    email_df = None
    if include_engagement:
        # Filter tactic to only email channel clients (TACTIC_CELL_CD = 'EM')
        email_clients = tactic_df.filter(F.col("TACTIC_CELL_CD") == "EM")
        email_client_count = channels_in_data.get("EM", 0)
        log(f"    [Layer 4] Email channel clients (TACTIC_CELL_CD=EM): {email_client_count:,}")

        if email_client_count > 0:
            # Get tactic IDs for email clients only
            email_tactic_ids = [row.TACTIC_ID for row in email_clients.select("TACTIC_ID").distinct().collect()]
            email_df = load_email_engagement(spark, email_tactic_ids[:5] if email_tactic_ids else [])

    # 4c: Success outcome
    log("\n[Layer 4] Loading success outcome...")
    success_table = load_success_outcome(spark, config)

    # Detect success (join Layer 1 + Layer 4)
    log("\n[Engine] Detecting success...")
    success_df = detect_success(tactic_df, success_table, config)

    # Enrich with engagement data if available
    # Note: email_df only contains data for TACTIC_CELL_CD='EM' clients
    # Non-email clients will have NULL/0 for email engagement columns
    if include_engagement and (email_df is not None or fulfillment_df is not None):
        log("[Engine] Enriching with engagement data...")
        success_df = enrich_with_engagement(success_df, email_df, fulfillment_df)

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

    # Generate summaries
    log("\n[Engine] Generating summaries...")
    summary_df = generate_summary(vintage_df, mne)
    print(summary_df.to_string(index=False))

    # Engagement summary if available
    engagement_summary_df = None
    if include_engagement:
        engagement_summary_df = generate_engagement_summary(success_df, mne)
        if not engagement_summary_df.empty and len(engagement_summary_df.columns) > 2:
            log("\n[Layer 4] Engagement Summary:")
            print(engagement_summary_df.to_string(index=False))

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
        "engagement_summary_df": engagement_summary_df
    }


def run_all_campaigns(spark, mnes=None, show_plots=True, include_engagement=True):
    """Run vintage analysis for multiple campaigns."""
    mnes = mnes or ALL_MNES
    results = {}
    all_summaries = []
    all_engagement = []

    for mne in mnes:
        try:
            result = run_vintage_analysis(spark, mne, show_plots=show_plots, include_engagement=include_engagement)
            if result:
                results[mne] = result
                all_summaries.append(result["summary_df"])
                if result.get("engagement_summary_df") is not None:
                    all_engagement.append(result["engagement_summary_df"])
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


def export_to_hdfs_csv(results, spark, hdfs_path="/user/427966379/vintage_data.csv"):
    """Export vintage results to HDFS as CSV."""
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

spark = SparkSession.builder.appName("Vintage Analysis").getOrCreate()

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     VINTAGE CURVE ANALYSIS ENGINE                             ║
║                                                                              ║
║  Architecture: SuperFact 4-Layer Framework                                   ║
║  - Layer 1: Experiment Metadata (tactic_evnt_hist)                           ║
║  - Layer 2: Campaign Metadata (CAMPAIGN_METADATA) [SWAP POINT]               ║
║  - Layer 3: Success Definitions (SUCCESS_DEFINITIONS) [SWAP POINT]           ║
║  - Layer 4: Client Journey (fulfillment, engagement, outcome)                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Available campaigns: """ + ", ".join(ALL_MNES) + """

Usage:
  # Single campaign
  results = run_vintage_analysis(spark, 'VCN')

  # All campaigns
  results = run_all_campaigns(spark)

  # Without engagement data (faster)
  results = run_vintage_analysis(spark, 'VCN', include_engagement=False)

  # Export to HDFS
  export_to_hdfs_csv(results, spark)
""")
