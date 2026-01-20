"""
VVD Vintage Curve Analysis - All In One
========================================

Copy this entire file into a Jupyter notebook cell and run.
No imports needed - everything is self-contained.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import StorageLevel
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

# =============================================================================
# CONFIGURATION
# =============================================================================

YEARS_TO_INCLUDE = [2025, 2026]
TEST_GROUP_CODE = "TG4"
CONFIDENCE_LEVEL = 0.95

PATHS = {
    "tactic": "/user/427966379/tactic.parquet",
    "visa_dr_crd": "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT=",
    "pos_txn": "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT=",
    "token": "/user/427966379/token.parquet",
    "output": "/user/427966379"
}

CAMPAIGN_CONFIG = {
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "success_source": "HIVE",
        "success_table_path": PATHS["visa_dr_crd"],
        "success_date_field": "ISS_DT",
        "filters": {"STS_CD": ["06", "08"], "SRVC_ID": 36, "ISS_DT_NOT_NULL": True},
    },
    "VDA": {
        "campaign_name": "VVD Black Friday Cyber Monday Targeted",
        "success_type": "ACQUISITION",
        "success_source": "HIVE",
        "success_table_path": PATHS["visa_dr_crd"],
        "success_date_field": "ISS_DT",
        "filters": {"STS_CD": ["06", "08"], "SRVC_ID": 36, "ISS_DT_NOT_NULL": True},
    },
    "VDT": {
        "campaign_name": "VVD Activation Trigger",
        "success_type": "ACTIVATION",
        "success_source": "HIVE",
        "success_table_path": PATHS["visa_dr_crd"],
        "success_date_field": "ACTV_DT",
        "filters": {"STS_CD": ["06", "08"], "SRVC_ID": 36, "ISS_DT_NOT_NULL": True},
    },
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
    },
    "VUT": {
        "campaign_name": "VVD Tokenization Usage Campaign",
        "success_type": "TOKENIZATION",
        "success_source": "EDW",
        "success_table_path": PATHS["token"],
        "success_date_field": "TXN_DT",
        "filters": None,
    },
    "VAW": {
        "campaign_name": "VVD Add To Wallet Contextual Notification",
        "success_type": "TOKENIZATION",
        "success_source": "EDW",
        "success_table_path": PATHS["token"],
        "success_date_field": "TXN_DT",
        "filters": None,
    },
}

ALL_MNES = list(CAMPAIGN_CONFIG.keys())

def get_config(mne):
    return CAMPAIGN_CONFIG[mne]

# =============================================================================
# DATA LOADING
# =============================================================================

def load_tactic(spark, mne):
    tactic = spark.read.parquet(PATHS["tactic"])
    tactic = tactic.filter(
        (F.col("MNE") == mne) &
        (F.year(F.col("TREATMT_STRT_DT")).isin(YEARS_TO_INCLUDE))
    )
    tactic = tactic.withColumn("WINDOW_DAYS", F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT")))
    tactic = tactic.withColumn("GROUP", F.when(F.col("TST_GRP_CD") == TEST_GROUP_CODE, "TEST").otherwise("CONTROL"))
    tactic = tactic.withColumn("COHORT", F.date_format(F.col("TREATMT_STRT_DT"), "yyyy-MM"))
    return tactic


def load_success_table(spark, config):
    years_str = [str(y) for y in YEARS_TO_INCLUDE]

    if config["success_source"] == "EDW":
        return spark.read.parquet(config["success_table_path"])

    paths = [f"{config['success_table_path']}{year}*" for year in years_str]
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

    if config["success_type"] in ["ACQUISITION", "ACTIVATION"]:
        df = df.withColumn("Card_Type", F.when(F.col("VISA_DR_CRD_BRND_CD") == "03", "Digital").otherwise("Hybrid/Plastic"))

    return df

# =============================================================================
# SUCCESS DETECTION
# =============================================================================

def detect_success(tactic_df, success_df, config):
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

# =============================================================================
# VINTAGE CALCULATIONS
# =============================================================================

def build_vintage_data(success_df):
    totals = success_df.groupBy("COHORT", "GROUP").agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )
    successes = success_df.filter(F.col("SUCCESS_FLAG") == 1).groupBy(
        "COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS"
    ).agg(F.count("*").alias("SUCCESSES_ON_DAY"))
    vintage = successes.join(totals, on=["COHORT", "GROUP"], how="left")
    return vintage.orderBy("COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS")


def calculate_ci(test_succ, test_n, ctrl_succ, ctrl_n):
    if test_n == 0 or ctrl_n == 0:
        return np.nan, np.nan, np.nan
    p_test, p_ctrl = test_succ / test_n, ctrl_succ / ctrl_n
    lift = p_test - p_ctrl
    se = np.sqrt((p_test * (1 - p_test) / test_n) + (p_ctrl * (1 - p_ctrl) / ctrl_n))
    z = stats.norm.ppf(1 - (1 - CONFIDENCE_LEVEL) / 2)
    return lift, lift - z * se, lift + z * se


def prepare_vintage_table(vintage_spark_df):
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
    if lift_df.empty:
        return pd.DataFrame()
    final = lift_df.loc[lift_df.groupby("COHORT")["DAY"].idxmax()].copy()
    final["MNE"] = mne
    cols = ["MNE", "COHORT", "WINDOW_DAYS", "TEST_CLIENTS", "TEST_SUCCESSES", "TEST_RATE",
            "CTRL_CLIENTS", "CTRL_SUCCESSES", "CTRL_RATE", "ABS_LIFT", "CI_LOWER", "CI_UPPER", "SIGNIFICANT"]
    return final[cols].sort_values("COHORT")

# =============================================================================
# PLOTTING
# =============================================================================

def plot_vintage(vintage_df, mne, config, save_path=None):
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

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Plot saved: {save_path}")
    plt.show()
    plt.close()

# =============================================================================
# MAIN RUNNER
# =============================================================================

def run_vintage_analysis(spark, mne, save_outputs=True, verbose=True):
    """Run vintage analysis for a campaign."""
    def log(msg):
        if verbose:
            print(msg)

    log(f"\n{'='*60}")
    log(f"VINTAGE ANALYSIS: {mne}")
    log(f"{'='*60}")

    config = get_config(mne)
    log(f"Campaign: {config['campaign_name']}")
    log(f"Success Type: {config['success_type']}")

    log("\n[1] Loading tactic...")
    tactic_df = load_tactic(spark, mne)
    tactic_count = tactic_df.count()
    log(f"    Records: {tactic_count:,}")

    if tactic_count == 0:
        log("    ERROR: No tactic records!")
        return None

    log("\n[2] Loading success table...")
    success_table = load_success_table(spark, config)

    log("\n[3] Detecting success...")
    success_df = detect_success(tactic_df, success_table, config)
    success_df.persist(StorageLevel.MEMORY_AND_DISK)

    log("\n[4] Success summary:")
    success_df.groupBy("GROUP").agg(
        F.count("*").alias("TOTAL"),
        F.sum("SUCCESS_FLAG").alias("SUCCESSES"),
        F.avg("SUCCESS_FLAG").alias("RATE")
    ).show()

    log("\n[5] Building vintage curves...")
    vintage_spark = build_vintage_data(success_df)
    vintage_df = prepare_vintage_table(vintage_spark)

    if vintage_df.empty:
        log("    ERROR: No vintage data!")
        success_df.unpersist()
        return None

    log("\n[6] Summary:")
    summary_df = generate_summary(vintage_df, mne)
    print(summary_df.to_string(index=False))

    output_paths = {}
    if save_outputs:
        log("\n[7] Saving outputs...")
        vintage_df["MNE"] = mne
        csv_path = f"{PATHS['output']}/{mne}_vintage_full.csv"
        summary_path = f"{PATHS['output']}/{mne}_vintage_summary.csv"
        plot_path = f"{PATHS['output']}/{mne}_vintage_plot.png"
        vintage_df.to_csv(csv_path, index=False)
        summary_df.to_csv(summary_path, index=False)
        output_paths = {"csv": csv_path, "summary": summary_path, "plot": plot_path}
        log(f"    CSV: {csv_path}")

    log("\n[8] Plotting...")
    plot_vintage(vintage_df, mne, config, output_paths.get("plot"))

    success_df.unpersist()
    log(f"\n{'='*60}")
    log(f"COMPLETE: {mne}")
    log(f"{'='*60}")

    return {"vintage_df": vintage_df, "summary_df": summary_df, "paths": output_paths}


def run_all_campaigns(spark, mnes=None):
    """Run vintage analysis for all campaigns."""
    mnes = mnes or ALL_MNES
    results = {}
    all_summaries = []

    for mne in mnes:
        try:
            result = run_vintage_analysis(spark, mne)
            if result:
                results[mne] = result
                all_summaries.append(result["summary_df"])
        except Exception as e:
            print(f"ERROR {mne}: {str(e)}")

    if all_summaries:
        combined = pd.concat(all_summaries, ignore_index=True)
        print(f"\n{'='*60}")
        print("ALL CAMPAIGNS SUMMARY")
        print(f"{'='*60}")
        print(combined.to_string(index=False))

    return results


# =============================================================================
# RUN - Uncomment to execute
# =============================================================================

# Get or create Spark session
spark = SparkSession.builder.appName("VVD Vintage").getOrCreate()

# Show available campaigns
print("Available campaigns:", ALL_MNES)

# Run single campaign - uncomment one:
# results = run_vintage_analysis(spark, "VCN")
# results = run_vintage_analysis(spark, "VDA")
# results = run_vintage_analysis(spark, "VDT")
# results = run_vintage_analysis(spark, "VUI")
# results = run_vintage_analysis(spark, "VUT")
# results = run_vintage_analysis(spark, "VAW")

# Run all campaigns:
# results = run_all_campaigns(spark)
