"""
Vintage Curve Pipeline
======================

All functions for vintage curve analysis in one file.

Usage in Jupyter:
    from vintage_pipeline import run_vintage_analysis, run_all_campaigns

    # Single campaign
    results = run_vintage_analysis(spark, "VCN")

    # All campaigns
    all_results = run_all_campaigns(spark)
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import StorageLevel
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

from config import (
    CAMPAIGN_CONFIG, PATHS, YEARS_TO_INCLUDE,
    TEST_GROUP_CODE, COHORT_DATE_FORMAT, CONFIDENCE_LEVEL,
    get_config, ALL_MNES
)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_tactic(spark, mne, years=None):
    """Load tactic data for a campaign."""
    years = years or YEARS_TO_INCLUDE

    tactic = spark.read.parquet(PATHS["tactic"])

    tactic = tactic.filter(
        (F.col("MNE") == mne) &
        (F.year(F.col("TREATMT_STRT_DT")).isin(years))
    )

    # Add derived columns
    tactic = tactic.withColumn(
        "WINDOW_DAYS",
        F.datediff(F.col("TREATMT_END_DT"), F.col("TREATMT_STRT_DT"))
    ).withColumn(
        "GROUP",
        F.when(F.col("TST_GRP_CD") == TEST_GROUP_CODE, "TEST").otherwise("CONTROL")
    ).withColumn(
        "COHORT",
        F.date_format(F.col("TREATMT_STRT_DT"), COHORT_DATE_FORMAT)
    )

    return tactic


def load_success_table(spark, config, years=None):
    """Load success table based on campaign configuration."""
    years = years or YEARS_TO_INCLUDE
    years_str = [str(y) for y in years]

    if config["success_source"] == "EDW":
        return spark.read.parquet(config["success_table_path"])

    # HIVE source
    paths = [f"{config['success_table_path']}{year}*" for year in years_str]
    df = spark.read.parquet(*paths)

    # Apply filters
    filters = config.get("filters")
    if filters:
        if "STS_CD" in filters:
            df = df.filter(F.col("STS_CD").isin(filters["STS_CD"]))

        if "SRVC_ID" in filters:
            df = df.filter(F.col("SRVC_ID") == filters["SRVC_ID"])

        if "SRVC_CD" in filters:
            df = df.filter(F.col("SRVC_CD") == filters["SRVC_CD"])

        if "TXN_TYPES" in filters:
            txn_conditions = None
            for txn_type in filters["TXN_TYPES"]:
                condition = (F.col("TXN_TP") == txn_type["TXN_TP"]) & (F.col("MSG_TP") == txn_type["MSG_TP"])
                txn_conditions = condition if txn_conditions is None else txn_conditions | condition
            df = df.filter(txn_conditions)

        if filters.get("ISS_DT_NOT_NULL"):
            df = df.filter(F.col("ISS_DT").isNotNull())

        if "AMT1_GT" in filters:
            df = df.filter(F.col("AMT1") > filters["AMT1_GT"])

        if filters.get("EXTRACT_CLNT_NO"):
            df = df.withColumn(
                "CLNT_NO",
                F.regexp_replace(F.substring(F.col("CLNT_CRD_NO"), 7, 9), "^0+", "")
            )

    # Add Card_Type for acquisition/activation
    if config["success_type"] in ["ACQUISITION", "ACTIVATION"]:
        df = df.withColumn(
            "Card_Type",
            F.when(F.col("VISA_DR_CRD_BRND_CD") == "03", "Digital").otherwise("Hybrid/Plastic")
        )

    return df


# =============================================================================
# SUCCESS DETECTION
# =============================================================================

def detect_success(tactic_df, success_df, config):
    """Join tactic with success table to detect conversions."""
    tactic_columns = tactic_df.columns

    tactic_alias = tactic_df.alias("t")
    success_date_field = config["success_date_field"]

    success_select = success_df.select(
        F.col("CLNT_NO").alias("SUCCESS_CLNT_NO"),
        F.col(success_date_field).alias("SUCCESS_DT")
    ).alias("s")

    # Left join - success within measurement window
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

    # Aggregate to client level
    groupby_cols = [f"t.{col}" for col in tactic_columns] + ["t.WINDOW_DAYS", "t.GROUP", "t.COHORT"]

    result = joined.groupBy(groupby_cols).agg(
        F.max(F.when(F.col("s.SUCCESS_DT").isNotNull(), 1).otherwise(0)).alias("SUCCESS_FLAG"),
        F.min("s.SUCCESS_DT").alias("FIRST_SUCCESS_DT"),
        F.min("DAYS_TO_SUCCESS").alias("DAYS_TO_FIRST_SUCCESS"),
        F.count("s.SUCCESS_DT").alias("SUCCESS_COUNT")
    )

    # Clean column names
    for col in result.columns:
        if col.startswith("t."):
            result = result.withColumnRenamed(col, col[2:])

    return result


# =============================================================================
# VINTAGE CALCULATIONS
# =============================================================================

def build_vintage_data(success_df):
    """Build vintage curve data from success DataFrame."""
    totals = success_df.groupBy("COHORT", "GROUP").agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )

    successes = success_df.filter(F.col("SUCCESS_FLAG") == 1).groupBy(
        "COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS"
    ).agg(F.count("*").alias("SUCCESSES_ON_DAY"))

    vintage = successes.join(totals, on=["COHORT", "GROUP"], how="left")

    return vintage.orderBy("COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS")


def calculate_confidence_interval(test_successes, test_n, ctrl_successes, ctrl_n):
    """Calculate confidence interval for lift."""
    if test_n == 0 or ctrl_n == 0:
        return np.nan, np.nan, np.nan

    p_test = test_successes / test_n
    p_ctrl = ctrl_successes / ctrl_n
    lift = p_test - p_ctrl

    se = np.sqrt((p_test * (1 - p_test) / test_n) + (p_ctrl * (1 - p_ctrl) / ctrl_n))
    z = stats.norm.ppf(1 - (1 - CONFIDENCE_LEVEL) / 2)

    return lift, lift - z * se, lift + z * se


def prepare_vintage_table(vintage_spark_df):
    """Convert to Pandas and calculate cumulative rates, lift, and CI."""
    pdf = vintage_spark_df.toPandas()

    if pdf.empty:
        return pdf

    pdf = pdf.sort_values(["COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS"])
    pdf["CUMULATIVE_SUCCESSES"] = pdf.groupby(["COHORT", "GROUP"])["SUCCESSES_ON_DAY"].cumsum()
    pdf["CUMULATIVE_RATE"] = pdf["CUMULATIVE_SUCCESSES"] / pdf["TOTAL_CLIENTS"] * 100
    pdf = pdf.rename(columns={"DAYS_TO_FIRST_SUCCESS": "DAY"})

    # Fill missing days
    cohorts = pdf["COHORT"].unique()
    complete_rows = []

    for cohort in cohorts:
        for group in ["TEST", "CONTROL"]:
            data = pdf[(pdf["COHORT"] == cohort) & (pdf["GROUP"] == group)]
            if data.empty:
                continue

            total_clients = data["TOTAL_CLIENTS"].iloc[0]
            window_days = int(data["WINDOW_DAYS"].iloc[0])
            max_day = data["DAY"].max()

            cum_successes = 0
            for day in range(0, min(window_days + 1, int(max_day) + 1)):
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

    # Calculate lift
    lift_rows = []
    for cohort in cohorts:
        cohort_data = complete_df[complete_df["COHORT"] == cohort]
        test_data = cohort_data[cohort_data["GROUP"] == "TEST"]
        ctrl_data = cohort_data[cohort_data["GROUP"] == "CONTROL"]

        if test_data.empty or ctrl_data.empty:
            continue

        window_days = int(test_data["WINDOW_DAYS"].iloc[0])

        for day in test_data["DAY"].unique():
            test_row = test_data[test_data["DAY"] == day]
            ctrl_row = ctrl_data[ctrl_data["DAY"] == day]

            if test_row.empty or ctrl_row.empty:
                continue

            lift, ci_lower, ci_upper = calculate_confidence_interval(
                test_row["CUMULATIVE_SUCCESSES"].iloc[0], test_row["TOTAL_CLIENTS"].iloc[0],
                ctrl_row["CUMULATIVE_SUCCESSES"].iloc[0], ctrl_row["TOTAL_CLIENTS"].iloc[0]
            )

            lift_rows.append({
                "COHORT": cohort, "DAY": day, "WINDOW_DAYS": window_days,
                "TEST_CLIENTS": test_row["TOTAL_CLIENTS"].iloc[0],
                "TEST_SUCCESSES": test_row["CUMULATIVE_SUCCESSES"].iloc[0],
                "TEST_RATE": test_row["CUMULATIVE_RATE"].iloc[0],
                "CTRL_CLIENTS": ctrl_row["TOTAL_CLIENTS"].iloc[0],
                "CTRL_SUCCESSES": ctrl_row["CUMULATIVE_SUCCESSES"].iloc[0],
                "CTRL_RATE": ctrl_row["CUMULATIVE_RATE"].iloc[0],
                "ABS_LIFT": lift * 100, "CI_LOWER": ci_lower * 100, "CI_UPPER": ci_upper * 100
            })

    lift_df = pd.DataFrame(lift_rows)
    if not lift_df.empty:
        lift_df["SIGNIFICANT"] = (lift_df["CI_LOWER"] > 0) | (lift_df["CI_UPPER"] < 0)

    return lift_df


def generate_summary_table(lift_df, mne):
    """Generate summary table with final rates per cohort."""
    if lift_df.empty:
        return pd.DataFrame()

    final_rates = lift_df.loc[lift_df.groupby("COHORT")["DAY"].idxmax()].copy()
    final_rates["MNE"] = mne

    cols = ["MNE", "COHORT", "WINDOW_DAYS", "TEST_CLIENTS", "TEST_SUCCESSES", "TEST_RATE",
            "CTRL_CLIENTS", "CTRL_SUCCESSES", "CTRL_RATE", "ABS_LIFT", "CI_LOWER", "CI_UPPER", "SIGNIFICANT"]

    return final_rates[cols].sort_values("COHORT")


# =============================================================================
# PLOTTING
# =============================================================================

def plot_vintage(vintage_df, mne, config, save_path=None):
    """Plot vintage curves - all cohorts on one chart."""
    if vintage_df.empty:
        print(f"WARNING: No data to plot for {mne}")
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


def plot_grid(vintage_df, mne, config, save_path=None):
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

    # Hide empty subplots
    for idx in range(n_cohorts, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].set_visible(False)

    fig.suptitle(f"{mne} - {config['campaign_name']} | {config['success_type']}", fontsize=13, y=1.02)
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
    """
    Run full vintage analysis for a campaign.

    Args:
        spark: SparkSession
        mne: Campaign code (e.g., "VCN")
        save_outputs: Save CSV and plots
        verbose: Print progress

    Returns:
        dict with vintage_df, summary_df, and paths
    """
    def log(msg):
        if verbose:
            print(msg)

    log(f"\n{'='*60}")
    log(f"VINTAGE ANALYSIS: {mne}")
    log(f"{'='*60}")

    config = get_config(mne)
    log(f"Campaign: {config['campaign_name']}")
    log(f"Success Type: {config['success_type']}")

    # Load data
    log("\n[1] Loading tactic data...")
    tactic_df = load_tactic(spark, mne)
    tactic_count = tactic_df.count()
    log(f"    Records: {tactic_count:,}")

    if tactic_count == 0:
        log("    ERROR: No tactic records found!")
        return None

    log("\n[2] Loading success table...")
    success_table = load_success_table(spark, config)

    # Detect success
    log("\n[3] Detecting success...")
    success_df = detect_success(tactic_df, success_table, config)
    success_df.persist(StorageLevel.MEMORY_AND_DISK)

    log("\n[4] Success summary:")
    success_df.groupBy("GROUP").agg(
        F.count("*").alias("TOTAL"),
        F.sum("SUCCESS_FLAG").alias("SUCCESSES"),
        F.avg("SUCCESS_FLAG").alias("RATE")
    ).show()

    # Build vintage
    log("\n[5] Building vintage curves...")
    vintage_spark = build_vintage_data(success_df)
    vintage_df = prepare_vintage_table(vintage_spark)

    if vintage_df.empty:
        log("    ERROR: No vintage data generated!")
        success_df.unpersist()
        return None

    # Summary
    log("\n[6] Summary table:")
    summary_df = generate_summary_table(vintage_df, mne)
    print(summary_df.to_string(index=False))

    # Outputs
    output_paths = {}
    if save_outputs:
        log("\n[7] Saving outputs...")
        vintage_df["MNE"] = mne

        csv_path = f"{PATHS['output']}/{mne}_vintage_full.csv"
        summary_path = f"{PATHS['output']}/{mne}_vintage_summary.csv"
        plot_path = f"{PATHS['output']}/{mne}_vintage_plot.png"
        grid_path = f"{PATHS['output']}/{mne}_vintage_grid.png"

        vintage_df.to_csv(csv_path, index=False)
        summary_df.to_csv(summary_path, index=False)

        output_paths = {"csv": csv_path, "summary": summary_path, "plot": plot_path, "grid": grid_path}
        log(f"    CSV: {csv_path}")
        log(f"    Summary: {summary_path}")

    # Plots
    log("\n[8] Generating plots...")
    plot_vintage(vintage_df, mne, config, output_paths.get("plot"))
    plot_grid(vintage_df, mne, config, output_paths.get("grid"))

    success_df.unpersist()

    log(f"\n{'='*60}")
    log(f"COMPLETE: {mne}")
    log(f"{'='*60}")

    return {"vintage_df": vintage_df, "summary_df": summary_df, "paths": output_paths}


def run_all_campaigns(spark, mnes=None, save_outputs=True, verbose=True):
    """Run vintage analysis for all campaigns."""
    mnes = mnes or ALL_MNES

    print(f"\n{'='*60}")
    print(f"RUNNING ALL CAMPAIGNS: {', '.join(mnes)}")
    print(f"{'='*60}")

    results = {}
    all_summaries = []

    for mne in mnes:
        try:
            result = run_vintage_analysis(spark, mne, save_outputs, verbose)
            if result:
                results[mne] = result
                all_summaries.append(result["summary_df"])
        except Exception as e:
            print(f"\n*** ERROR {mne}: {str(e)} ***\n")

    # Combined summary
    if all_summaries:
        combined = pd.concat(all_summaries, ignore_index=True)

        if save_outputs:
            combined_path = f"{PATHS['output']}/ALL_CAMPAIGNS_summary.csv"
            combined.to_csv(combined_path, index=False)
            print(f"\nCombined summary: {combined_path}")

        print(f"\n{'='*60}")
        print("FINAL SUMMARY - ALL CAMPAIGNS")
        print(f"{'='*60}")
        print(combined.to_string(index=False))

    return results
