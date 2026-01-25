"""Vintage Engine v2.4 - Core (Slim version for Jupyter)"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import StorageLevel
import pandas as pd
import numpy as np
from urllib.parse import quote
from IPython.display import HTML, display

%matplotlib inline

# === USER CONFIG ===
USER_CONFIG = {
    "user_id": "427966379",
    "hdfs_base_path": "/user/427966379",
    "output_folder": "vintage_output_v2",
}

def get_hdfs_output_path():
    return f"{USER_CONFIG['hdfs_base_path']}/{USER_CONFIG['output_folder']}"

# === GLOBAL CONFIG ===
YEARS_TO_INCLUDE = [2025, 2026]

# === HIVE_PATHS (file system paths) ===
HIVE_PATHS = {
    "tactic_events": "/prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/",
    "visa_debit_card": "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT=",
    "pos_transactions": "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT=",
}

# === EDW_TABLES (schema.table references) ===
EDW_TABLES = {
    "feedback_master": "DTZV01.VENDOR_FEEDBACK_MASTER",
    "feedback_event": "DTZV01.VENDOR_FEEDBACK_EVENT",
    "pos_log": "DDWV05.CLNT_CRD_POS_LOG",
    "token_list": "DL_DECMAN.TOKEN_LIST",
}

# === LAYER 2: CAMPAIGN METADATA ===
CAMPAIGN_METADATA = {
    "VCN": {"campaign_name": "VVD Contextual Notification", "success_type": "ACQUISITION", "primary_metric": "card_acquisition", "secondary_metric": None},
    "VDA": {"campaign_name": "VVD Black Friday Cyber Monday Targeted", "success_type": "ACQUISITION", "primary_metric": "card_acquisition", "secondary_metric": None},
    "VDT": {"campaign_name": "VVD Activation Trigger", "success_type": "ACTIVATION", "primary_metric": "card_activation", "secondary_metric": None},
    "VUI": {"campaign_name": "VVD Usage Trigger", "success_type": "USAGE", "primary_metric": "card_usage", "secondary_metric": "wallet_provisioning"},
    "VUT": {"campaign_name": "VVD Tokenization Usage Campaign", "success_type": "TOKENIZATION", "primary_metric": "wallet_provisioning", "secondary_metric": "card_usage"},
    "VAW": {"campaign_name": "VVD Add To Wallet Contextual Notification", "success_type": "TOKENIZATION", "primary_metric": "wallet_provisioning", "secondary_metric": "card_usage"},
}

# === LAYER 3: SUCCESS DEFINITIONS ===
SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "description": "Client acquired a new VVD card", "version": "1.0", "source": "HIVE",
        "table_path": HIVE_PATHS["visa_debit_card"], "date_field": "ISS_DT", "client_field": "CLNT_NO",
        "filters": {"STS_CD": ["06", "08"], "SRVC_ID": 36, "ISS_DT_NOT_NULL": True}, "add_card_type": True,
    },
    "card_activation": {
        "description": "Client activated their VVD card", "version": "1.0", "source": "HIVE",
        "table_path": HIVE_PATHS["visa_debit_card"], "date_field": "ACTV_DT", "client_field": "CLNT_NO",
        "filters": {"STS_CD": ["06", "08"], "SRVC_ID": 36, "ISS_DT_NOT_NULL": True}, "add_card_type": True,
    },
    "card_usage": {
        "description": "Client used their VVD card for a transaction", "version": "1.0", "source": "HIVE",
        "table_path": HIVE_PATHS["pos_transactions"], "date_field": "TXN_DT", "client_field": "CLNT_NO",
        "filters": {"SRVC_CD": 36, "TXN_TYPES": [{"TXN_TP": 10, "MSG_TP": "0210"}, {"TXN_TP": 13, "MSG_TP": "0210"}, {"TXN_TP": 12, "MSG_TP": "0220"}], "AMT1_GT": 0, "EXTRACT_CLNT_NO": True},
        "add_card_type": False,
    },
    "wallet_provisioning": {
        "description": "Client provisioned card to digital wallet", "version": "1.0", "source": "EDW",
        "table_path": None, "date_field": "TXN_DT", "client_field": "CLNT_NO", "filters": None, "add_card_type": False,
    },
}

ALL_MNES = list(CAMPAIGN_METADATA.keys())

def get_campaign_config(mne): return CAMPAIGN_METADATA[mne]
def get_success_definition(metric_name): return SUCCESS_DEFINITIONS[metric_name]

def get_full_config(mne, metric_type="PRIMARY"):
    campaign = CAMPAIGN_METADATA[mne]
    metric = campaign["primary_metric"] if metric_type == "PRIMARY" else campaign.get("secondary_metric")
    if metric is None: return None
    success = SUCCESS_DEFINITIONS[metric]
    return {
        "campaign_name": campaign["campaign_name"], "success_type": campaign["success_type"],
        "metric_name": metric, "metric_type": metric_type, "success_source": success["source"],
        "success_table_path": success.get("table_path"), "success_date_field": success["date_field"],
        "filters": success["filters"], "add_card_type": success.get("add_card_type", False),
    }

# === LAYER 1: EXPERIMENT ===
def load_tactic(spark, mne):
    years = [str(y) for y in YEARS_TO_INCLUDE]
    base_path = HIVE_PATHS["tactic_events"]
    paths = [f"{base_path}EVNT_STRT_DT={year}*" for year in years]
    print(f"    [Layer 1] Loading experiment data from partitions: {years}")
    tactic = spark.read.option("basePath", base_path).parquet(*paths).filter(F.substring(F.col("TACTIC_ID"), 8, 3) == mne)
    tactic = tactic.withColumn("MNE", F.substring(F.col("TACTIC_ID"), 8, 3)) \
        .withColumn("CLNT_NO", F.regexp_replace(F.trim(F.col("TACTIC_EVNT_ID")), "^0+", "")) \
        .withColumn("TST_GRP_CD", F.trim(F.col("TST_GRP_CD"))) \
        .withColumn("RPT_GRP_CD", F.trim(F.col("RPT_GRP_CD")))
    tactic = tactic.select("CLNT_NO", "TACTIC_ID", "TREATMT_STRT_DT", "TREATMT_END_DT", "TST_GRP_CD", "RPT_GRP_CD", "TREATMT_MN", "TACTIC_CELL_CD", "STRTGY_SRC_CD", "ADDNL_DECISN_DATA1", "ADDNL_DECISN_DATA2", "ADDNL_DECISN_DATA3", "MNE")
    tactic = tactic.withColumn("WINDOW_DAYS", F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT")))
    tactic = tactic.withColumn("COHORT", F.date_format(F.col("TREATMT_STRT_DT"), "yyyy-MM"))
    return tactic.distinct()

# === LAYER 4: ENGAGEMENT ===
def load_channel_engagement(spark, treatment_ids, channel):
    if channel.upper() == "EMAIL": return _load_email_engagement(spark, treatment_ids)
    print(f"    [Layer 4] No loader implemented for channel: {channel}")
    return None

def _load_email_engagement(spark, treatment_ids):
    if not treatment_ids:
        print(f"    [Layer 4] No treatment IDs provided for email engagement")
        return None
    treatment_id_list = "','".join(treatment_ids)
    print(f"    [Layer 4] Loading EMAIL engagement for {len(treatment_ids):,} tactic IDs...")
    query = f"""
    SELECT DISTINCT CAST(FEEDBACK_MASTER.CLNT_NO AS VARCHAR(20)) AS CLNT_NO, FEEDBACK_MASTER.TREATMENT_ID, 'EMAIL' AS CHANNEL,
        MAX(CASE WHEN disposition_cd = 1 THEN 1 ELSE 0 END) AS SENT, MAX(CASE WHEN disposition_cd = 2 THEN 1 ELSE 0 END) AS OPENED, MAX(CASE WHEN disposition_cd = 3 THEN 1 ELSE 0 END) AS CLICKED,
        MAX(CASE WHEN disposition_cd = 1 THEN CAST(disposition_dt_tm AS DATE) END) AS SENT_DT, MAX(CASE WHEN disposition_cd = 2 THEN CAST(disposition_dt_tm AS DATE) END) AS OPENED_DT, MAX(CASE WHEN disposition_cd = 3 THEN CAST(disposition_dt_tm AS DATE) END) AS CLICKED_DT
    FROM {EDW_TABLES['feedback_master']} FEEDBACK_MASTER
    INNER JOIN {EDW_TABLES['feedback_event']} FEEDBACK_EVENT ON FEEDBACK_MASTER.consumer_id_hashed = FEEDBACK_EVENT.consumer_id_hashed AND FEEDBACK_MASTER.TREATMENT_ID = FEEDBACK_EVENT.TREATMENT_ID
    WHERE FEEDBACK_MASTER.TREATMENT_ID IN ('{treatment_id_list}')
    GROUP BY FEEDBACK_MASTER.CLNT_NO, FEEDBACK_MASTER.TREATMENT_ID"""
    try:
        cursor = EDW.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        pdf = pd.DataFrame(rows, columns=columns)
        pdf['CLNT_NO'] = pdf['CLNT_NO'].astype(str).str.strip().str.lstrip('0')
        print(f"    [Layer 4] Retrieved {len(pdf):,} email engagement records")
        return spark.createDataFrame(pdf) if not pdf.empty else None
    except Exception as e:
        print(f"    [Layer 4] Email engagement data not available: {str(e)}")
        return None

# === LAYER 4: SUCCESS OUTCOME ===
def load_token_from_edw():
    query = f"""SELECT DISTINCT CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER) AS CLNT_NO, B.TXN_DT
    FROM {EDW_TABLES['pos_log']} AS B INNER JOIN {EDW_TABLES['token_list']} C ON B.TOKN_REQSTR_ID = C.TOKEN_ID
    WHERE B.AMT1 = 0 AND SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190' AND SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'
        AND SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0' AND B.POS_ENTR_MODE_CD_NON_EMV = '000' AND B.SRVC_CD = 36 AND C.TOKEN_WALLET_IND = 'Y'"""
    cursor = EDW.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    return pd.DataFrame(rows, columns=columns)

def load_success_outcome(spark, config):
    years_str = [str(y) for y in YEARS_TO_INCLUDE]
    if config["success_source"] == "EDW":
        print(f"    [Layer 4] Loading success outcome from EDW ({config['metric_name']})...")
        token_pdf = load_token_from_edw()
        print(f"    [Layer 4] Retrieved {len(token_pdf):,} records")
        return spark.createDataFrame(token_pdf)
    paths = [f"{config['success_table_path']}{year}*" for year in years_str]
    print(f"    [Layer 4] Loading success outcome from partitions: {years_str}")
    df = spark.read.parquet(*paths)
    filters = config.get("filters")
    if filters:
        if "STS_CD" in filters: df = df.filter(F.col("STS_CD").isin(filters["STS_CD"]))
        if "SRVC_ID" in filters: df = df.filter(F.col("SRVC_ID") == filters["SRVC_ID"])
        if "SRVC_CD" in filters: df = df.filter(F.col("SRVC_CD") == filters["SRVC_CD"])
        if "TXN_TYPES" in filters:
            txn_cond = None
            for t in filters["TXN_TYPES"]:
                c = (F.col("TXN_TP") == t["TXN_TP"]) & (F.col("MSG_TP") == t["MSG_TP"])
                txn_cond = c if txn_cond is None else txn_cond | c
            df = df.filter(txn_cond)
        if filters.get("ISS_DT_NOT_NULL"): df = df.filter(F.col("ISS_DT").isNotNull())
        if "AMT1_GT" in filters: df = df.filter(F.col("AMT1") > filters["AMT1_GT"])
        if filters.get("EXTRACT_CLNT_NO"): df = df.withColumn("CLNT_NO", F.regexp_replace(F.substring(F.col("CLNT_CRD_NO"), 7, 9), "^0+", ""))
    return df

# === SUCCESS DETECTION ===
def detect_success(tactic_df, success_df, config):
    tactic_columns = tactic_df.columns
    tactic_alias = tactic_df.alias("t")
    success_select = success_df.select(F.col("CLNT_NO").alias("SUCCESS_CLNT_NO"), F.col(config["success_date_field"]).alias("SUCCESS_DT")).alias("s")
    joined = tactic_alias.join(success_select, (F.col("t.CLNT_NO") == F.col("s.SUCCESS_CLNT_NO")) & (F.col("s.SUCCESS_DT") >= F.col("t.TREATMT_STRT_DT")) & (F.col("s.SUCCESS_DT") <= F.col("t.TREATMT_END_DT")), how="left")
    joined = joined.withColumn("DAYS_TO_SUCCESS", F.when(F.col("s.SUCCESS_DT").isNotNull(), F.datediff(F.col("s.SUCCESS_DT"), F.col("t.TREATMT_STRT_DT"))).otherwise(None))
    groupby_cols = [f"t.{col}" for col in tactic_columns] + ["t.WINDOW_DAYS", "t.COHORT"]
    result = joined.groupBy(groupby_cols).agg(F.max(F.when(F.col("s.SUCCESS_DT").isNotNull(), 1).otherwise(0)).alias("SUCCESS_FLAG"), F.min("s.SUCCESS_DT").alias("FIRST_SUCCESS_DT"), F.min("DAYS_TO_SUCCESS").alias("DAYS_TO_FIRST_SUCCESS"), F.count("s.SUCCESS_DT").alias("SUCCESS_COUNT"))
    for col in result.columns:
        if col.startswith("t."): result = result.withColumnRenamed(col, col[2:])
    return result

def enrich_with_engagement(success_df, engagement_df):
    result = success_df
    if engagement_df is not None:
        eng_cols = engagement_df.columns
        if "SENT" in eng_cols:
            engagement_select = engagement_df.select(F.col("CLNT_NO").alias("ENG_CLNT_NO"), F.col("SENT").alias("EMAIL_SENT"), F.col("OPENED").alias("EMAIL_OPENED"), F.col("CLICKED").alias("EMAIL_CLICKED"), F.col("SENT_DT").alias("EMAIL_SENT_DT"), F.col("OPENED_DT").alias("EMAIL_OPENED_DT"), F.col("CLICKED_DT").alias("EMAIL_CLICKED_DT"))
        else:
            engagement_select = engagement_df.select(F.col("CLNT_NO").alias("ENG_CLNT_NO"), F.col("EMAIL_SENT"), F.col("EMAIL_OPENED"), F.col("EMAIL_CLICKED"), F.col("EMAIL_SENT_DT"), F.col("EMAIL_OPENED_DT"), F.col("EMAIL_CLICKED_DT"))
        result = result.join(engagement_select, result["CLNT_NO"] == engagement_select["ENG_CLNT_NO"], how="left").drop("ENG_CLNT_NO")
        for col in ["EMAIL_SENT", "EMAIL_OPENED", "EMAIL_CLICKED"]:
            if col in result.columns: result = result.withColumn(col, F.coalesce(F.col(col), F.lit(0)))
    return result

# === VINTAGE CURVES ===
def build_vintage_curves(success_df, mne, metric_type="PRIMARY"):
    group_cols = ["COHORT", "TST_GRP_CD", "RPT_GRP_CD"]
    totals = success_df.groupBy(group_cols).agg(F.count("*").alias("CLIENT_CNT"), F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS"))
    successes = success_df.filter(F.col("SUCCESS_FLAG") == 1).groupBy(group_cols + ["DAYS_TO_FIRST_SUCCESS"]).agg(F.count("*").alias("SUCCESSES_ON_DAY"))
    vintage = successes.join(totals, on=group_cols, how="right")
    pdf = vintage.toPandas()
    if pdf.empty: return pd.DataFrame()
    pdf = pdf.rename(columns={"DAYS_TO_FIRST_SUCCESS": "DAY"}).sort_values(group_cols + ["DAY"])
    complete_rows = []
    for (cohort, tst_grp, rpt_grp), group_data in pdf.groupby(group_cols):
        if group_data.empty: continue
        client_cnt = group_data["CLIENT_CNT"].iloc[0]
        window_days = int(group_data["WINDOW_DAYS"].iloc[0]) if pd.notna(group_data["WINDOW_DAYS"].iloc[0]) else 90
        day_successes = group_data.dropna(subset=["DAY"]).set_index("DAY")["SUCCESSES_ON_DAY"].to_dict()
        cum_successes = 0
        max_day = max(int(max(day_successes.keys())) if day_successes else 0, window_days)
        for day in range(0, min(window_days + 1, max_day + 1)):
            if day in day_successes: cum_successes += day_successes[day]
            complete_rows.append({"MNE": mne, "COHORT": cohort, "TST_GRP_CD": tst_grp, "RPT_GRP_CD": rpt_grp, "METRIC": metric_type, "DAY": day, "WINDOW_DAYS": window_days, "CLIENT_CNT": client_cnt, "SUCCESS_CNT": cum_successes, "RATE": round(cum_successes / client_cnt * 100, 4) if client_cnt > 0 else 0})
    return pd.DataFrame(complete_rows)

def build_engagement_curves(success_df, mne):
    columns = success_df.columns
    if "EMAIL_SENT" not in columns: return pd.DataFrame()
    email_df = success_df.filter(F.col("EMAIL_SENT") == 1)
    email_df = email_df.withColumn("DAYS_TO_OPEN", F.when(F.col("EMAIL_OPENED") == 1, F.datediff(F.col("EMAIL_OPENED_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None)).withColumn("DAYS_TO_CLICK", F.when(F.col("EMAIL_CLICKED") == 1, F.datediff(F.col("EMAIL_CLICKED_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None))
    all_curves = []
    open_curve = _build_engagement_metric_curve(email_df, mne, "DAYS_TO_OPEN", "EMAIL_OPENED", "EMAIL_OPEN")
    if not open_curve.empty: all_curves.append(open_curve)
    click_curve = _build_engagement_metric_curve(email_df, mne, "DAYS_TO_CLICK", "EMAIL_CLICKED", "EMAIL_CLICK")
    if not click_curve.empty: all_curves.append(click_curve)
    return pd.concat(all_curves, ignore_index=True) if all_curves else pd.DataFrame()

def _build_engagement_metric_curve(df, mne, days_col, flag_col, metric_name):
    group_cols = ["COHORT", "TST_GRP_CD", "RPT_GRP_CD"]
    totals = df.groupBy(group_cols).agg(F.count("*").alias("CLIENT_CNT"), F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS"))
    events = df.filter(F.col(flag_col) == 1).groupBy(group_cols + [days_col]).agg(F.count("*").alias("EVENTS_ON_DAY"))
    vintage = events.join(totals, on=group_cols, how="right")
    pdf = vintage.toPandas()
    if pdf.empty: return pd.DataFrame()
    pdf = pdf.rename(columns={days_col: "DAY"}).sort_values(group_cols + ["DAY"])
    complete_rows = []
    for (cohort, tst_grp, rpt_grp), group_data in pdf.groupby(group_cols):
        if group_data.empty: continue
        client_cnt = group_data["CLIENT_CNT"].iloc[0]
        window_days = int(group_data["WINDOW_DAYS"].iloc[0]) if pd.notna(group_data["WINDOW_DAYS"].iloc[0]) else 90
        day_events = group_data.dropna(subset=["DAY"]).set_index("DAY")["EVENTS_ON_DAY"].to_dict()
        cum_events = 0
        max_day = max(int(max(day_events.keys())) if day_events else 0, window_days)
        for day in range(0, min(window_days + 1, max_day + 1)):
            if day in day_events: cum_events += day_events[day]
            complete_rows.append({"MNE": mne, "COHORT": cohort, "TST_GRP_CD": tst_grp, "RPT_GRP_CD": rpt_grp, "METRIC": metric_name, "DAY": day, "WINDOW_DAYS": window_days, "CLIENT_CNT": client_cnt, "SUCCESS_CNT": cum_events, "RATE": round(cum_events / client_cnt * 100, 4) if client_cnt > 0 else 0})
    return pd.DataFrame(complete_rows)

def build_channel_breakdown(success_df, mne):
    breakdown = success_df.withColumn("CHANNEL", F.trim(F.coalesce(F.col("TACTIC_CELL_CD"), F.lit("UNKNOWN"))))
    breakdown = breakdown.groupBy("COHORT", "TST_GRP_CD", "RPT_GRP_CD", "CHANNEL").agg(F.count("*").alias("CLIENT_CNT"), F.sum("SUCCESS_FLAG").alias("SUCCESS_CNT"))
    pdf = breakdown.toPandas()
    pdf["MNE"] = mne
    pdf["RATE"] = (pdf["SUCCESS_CNT"] / pdf["CLIENT_CNT"] * 100).round(2)
    return pdf[["MNE", "COHORT", "TST_GRP_CD", "RPT_GRP_CD", "CHANNEL", "CLIENT_CNT", "SUCCESS_CNT", "RATE"]]

# === MAIN RUNNER ===
def run_vintage_analysis(spark, mne, verbose=True, include_engagement=True):
    def log(msg):
        if verbose: print(msg)
    log(f"\n{'='*60}\nVINTAGE ANALYSIS v2.4: {mne}\n{'='*60}")
    campaign = get_campaign_config(mne)
    log(f"[Layer 2] Campaign: {campaign['campaign_name']}")
    log(f"[Layer 2] Primary Metric: {campaign['primary_metric']}")
    if campaign.get('secondary_metric'): log(f"[Layer 2] Secondary Metric: {campaign['secondary_metric']}")
    log("\n[Layer 1] Loading experiment data...")
    tactic_df = load_tactic(spark, mne)
    tactic_df.persist(StorageLevel.MEMORY_AND_DISK)
    tactic_ids = [row.TACTIC_ID for row in tactic_df.select("TACTIC_ID").distinct().collect()]
    log(f"[Layer 1] Unique tactic IDs: {len(tactic_ids):,}")
    if len(tactic_ids) == 0:
        log("[Layer 1] ERROR: No experiment records!")
        tactic_df.unpersist()
        return None
    log("\n[Layer 1] Test groups in data:")
    tactic_df.groupBy("TST_GRP_CD").count().show()
    log("[Layer 1] Report groups in data:")
    tactic_df.groupBy("RPT_GRP_CD").count().show()
    channel_counts = tactic_df.groupBy(F.trim(F.col("TACTIC_CELL_CD")).alias("CHANNEL")).count().collect()
    channels_in_data = {row["CHANNEL"]: row["count"] for row in channel_counts}
    log(f"[Layer 4] Channels in data: {channels_in_data}")
    engagement_df = None
    if include_engagement:
        email_client_count = sum(count for ch, count in channels_in_data.items() if ch and "EM" in ch)
        if email_client_count > 0:
            email_clients = tactic_df.filter(F.trim(F.col("TACTIC_CELL_CD")).contains("EM"))
            email_tactic_ids = [row.TACTIC_ID for row in email_clients.select("TACTIC_ID").distinct().collect()]
            engagement_df = load_channel_engagement(spark, email_tactic_ids, "EMAIL")
    log("\n[Engine] Processing PRIMARY metric...")
    primary_config = get_full_config(mne, "PRIMARY")
    success_table_primary = load_success_outcome(spark, primary_config)
    success_df_primary = detect_success(tactic_df, success_table_primary, primary_config)
    if include_engagement and engagement_df is not None:
        success_df_primary = enrich_with_engagement(success_df_primary, engagement_df)
    success_df_primary.persist(StorageLevel.MEMORY_AND_DISK)
    log("[Engine] Building PRIMARY vintage curves...")
    primary_curves = build_vintage_curves(success_df_primary, mne, "PRIMARY")
    log(f"[Engine] PRIMARY curves: {len(primary_curves)} rows")
    engagement_curves = pd.DataFrame()
    if include_engagement and "EMAIL_SENT" in success_df_primary.columns:
        log("[Engine] Building engagement curves...")
        engagement_curves = build_engagement_curves(success_df_primary, mne)
        log(f"[Engine] Engagement curves: {len(engagement_curves)} rows")
    log("[Engine] Building channel breakdown...")
    channel_breakdown = build_channel_breakdown(success_df_primary, mne)
    success_df_primary.unpersist()
    secondary_curves = pd.DataFrame()
    secondary_config = get_full_config(mne, "SECONDARY")
    if secondary_config is not None:
        log(f"\n[Engine] Processing SECONDARY metric: {secondary_config['metric_name']}...")
        success_table_secondary = load_success_outcome(spark, secondary_config)
        success_df_secondary = detect_success(tactic_df, success_table_secondary, secondary_config)
        log("[Engine] Building SECONDARY vintage curves...")
        secondary_curves = build_vintage_curves(success_df_secondary, mne, "SECONDARY")
        log(f"[Engine] SECONDARY curves: {len(secondary_curves)} rows")
    tactic_df.unpersist()
    all_curves = [primary_curves]
    if not secondary_curves.empty: all_curves.append(secondary_curves)
    if not engagement_curves.empty: all_curves.append(engagement_curves)
    vintage_curves = pd.concat(all_curves, ignore_index=True)
    log(f"\n{'='*60}\nOUTPUT SUMMARY\n{'='*60}")
    log(f"Vintage curves: {len(vintage_curves)} rows")
    log(f"  Metrics: {vintage_curves['METRIC'].unique().tolist()}")
    log(f"  Test groups: {vintage_curves['TST_GRP_CD'].unique().tolist()}")
    log(f"  Report groups: {vintage_curves['RPT_GRP_CD'].unique().tolist()}")
    log(f"  Cohorts: {vintage_curves['COHORT'].nunique()}")
    log(f"Channel breakdown: {len(channel_breakdown)} rows")
    results = {"vintage_curves": vintage_curves, "channel_breakdown": channel_breakdown}
    log(f"\n{'='*60}\nCOMPLETE: {mne}\n{'='*60}")
    return results

def run_all_campaigns(spark, mnes=None, include_engagement=True):
    mnes = mnes or ALL_MNES
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

# === EXPORT ===
def _detect_result_structure(results):
    if not isinstance(results, dict): return 'unknown'
    if "vintage_curves" in results and isinstance(results["vintage_curves"], pd.DataFrame): return 'flat'
    for key, value in results.items():
        if key.startswith("_"): continue
        if isinstance(value, dict) and "vintage_curves" in value: return 'nested'
    return 'unknown'

def download_csv(data, filename="vintage_results.csv"):
    import base64
    csv_data = data.to_csv(index=False)
    size_mb = len(csv_data.encode('utf-8')) / (1024 * 1024)
    if size_mb > 50:
        print(f"Data too large ({size_mb:.1f} MB). Filter before exporting.")
        return
    b64 = base64.b64encode(csv_data.encode()).decode()
    link = f'<a download="{filename}" href="data:text/csv;base64,{b64}" style="padding:6px 12px; background:#2196F3; color:white; text-decoration:none; border-radius:3px; margin:2px; display:inline-block;">Download {filename}</a>'
    display(HTML(f'<div style="margin:5px 0;">{link} <span style="color:#666;">({size_mb:.2f} MB)</span></div>'))

def download_results(results, mne=None):
    structure = _detect_result_structure(results)
    if structure == 'flat':
        prefix = f"{mne}_" if mne else ""
        print(f"Creating download links for {mne or 'single campaign'}...")
        print("-" * 40)
        if results.get("vintage_curves") is not None and not results["vintage_curves"].empty:
            download_csv(results["vintage_curves"], f"{prefix}vintage_curves.csv")
        if results.get("channel_breakdown") is not None and not results["channel_breakdown"].empty:
            download_csv(results["channel_breakdown"], f"{prefix}channel_breakdown.csv")
    elif structure == 'nested':
        print("Creating download links for all campaigns...")
        print("-" * 40)
        if results.get("_combined_curves") is not None:
            download_csv(results["_combined_curves"], "vintage_curves.csv")
        if results.get("_combined_channel") is not None:
            download_csv(results["_combined_channel"], "channel_breakdown.csv")
    else:
        print("ERROR: Could not understand results structure.")

# === INIT ===
spark = SparkSession.builder.appName("Vintage Engine v2.4").getOrCreate()
print(f"VINTAGE ENGINE v2.4 CORE | Campaigns: {', '.join(ALL_MNES)} | Usage: results = run_vintage_analysis(spark, 'VAW')")
