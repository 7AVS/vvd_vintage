"""
Vintage Calculator Module
=========================

Calculates vintage curves from success detection results.
A vintage curve shows cumulative success rate over time from treatment date.

Key Outputs:
- Cumulative success rate by day
- Lift (Test - Control) with confidence intervals
- Summary statistics per cohort

Reference: Success Library Layer 3 - Centralized Logic Repo
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
import pandas as pd
import numpy as np
from scipy import stats

from ..config.base_config import CONFIDENCE_LEVEL


def build_vintage_data(success_df: DataFrame) -> DataFrame:
    """
    Build vintage curve data from success DataFrame.

    Aggregates success data by COHORT, GROUP, and day to create
    the foundation for vintage curve plotting.

    Args:
        success_df: Result from detect_success()

    Returns:
        Spark DataFrame with columns:
        - COHORT: Month cohort (yyyy-MM)
        - GROUP: TEST or CONTROL
        - DAYS_TO_FIRST_SUCCESS: Day number from treatment
        - SUCCESSES_ON_DAY: Count of successes on that day
        - TOTAL_CLIENTS: Total clients in cohort-group
        - WINDOW_DAYS: Median measurement window for the cohort
    """
    # Total clients per cohort and group
    # Use median WINDOW_DAYS when multiple deployments exist in same month
    totals = success_df.groupBy("COHORT", "GROUP").agg(
        F.count("*").alias("TOTAL_CLIENTS"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )

    # Successes by cohort, group, and day
    successes = success_df.filter(
        F.col("SUCCESS_FLAG") == 1
    ).groupBy("COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS").agg(
        F.count("*").alias("SUCCESSES_ON_DAY")
    )

    # Join totals
    vintage = successes.join(totals, on=["COHORT", "GROUP"], how="left")

    return vintage.orderBy("COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS")


def calculate_confidence_interval(
    test_successes: int,
    test_n: int,
    ctrl_successes: int,
    ctrl_n: int,
    confidence: float = None
) -> tuple:
    """
    Calculate confidence interval for absolute lift (difference in proportions).

    Uses normal approximation for the confidence interval of the
    difference between two proportions.

    Args:
        test_successes: Number of successes in test group
        test_n: Total in test group
        ctrl_successes: Number of successes in control group
        ctrl_n: Total in control group
        confidence: Confidence level (default: from base_config)

    Returns:
        Tuple of (lift, ci_lower, ci_upper)
        - lift: Absolute lift (test_rate - ctrl_rate)
        - ci_lower: Lower bound of confidence interval
        - ci_upper: Upper bound of confidence interval
    """
    confidence = confidence or CONFIDENCE_LEVEL

    if test_n == 0 or ctrl_n == 0:
        return np.nan, np.nan, np.nan

    p_test = test_successes / test_n
    p_ctrl = ctrl_successes / ctrl_n

    lift = p_test - p_ctrl

    # Standard error of difference
    se = np.sqrt(
        (p_test * (1 - p_test) / test_n) +
        (p_ctrl * (1 - p_ctrl) / ctrl_n)
    )

    # Z-score for confidence level
    z = stats.norm.ppf(1 - (1 - confidence) / 2)

    ci_lower = lift - z * se
    ci_upper = lift + z * se

    return lift, ci_lower, ci_upper


def prepare_vintage_table(vintage_spark_df: DataFrame) -> pd.DataFrame:
    """
    Convert Spark DataFrame to Pandas and calculate cumulative rates, lift, and CI.

    This function:
    1. Converts to Pandas for easier manipulation
    2. Calculates cumulative successes and rates
    3. Fills in missing days for complete curves
    4. Calculates lift and confidence intervals
    5. Adds significance flag

    Args:
        vintage_spark_df: Result from build_vintage_data()

    Returns:
        Pandas DataFrame with columns:
        - COHORT, DAY, WINDOW_DAYS
        - TEST_CLIENTS, TEST_SUCCESSES, TEST_RATE
        - CTRL_CLIENTS, CTRL_SUCCESSES, CTRL_RATE
        - ABS_LIFT, CI_LOWER, CI_UPPER, SIGNIFICANT
    """
    pdf = vintage_spark_df.toPandas()

    if pdf.empty:
        return pdf

    # Sort
    pdf = pdf.sort_values(["COHORT", "GROUP", "DAYS_TO_FIRST_SUCCESS"])

    # Cumulative successes per cohort-group
    pdf["CUMULATIVE_SUCCESSES"] = pdf.groupby(["COHORT", "GROUP"])["SUCCESSES_ON_DAY"].cumsum()
    pdf["CUMULATIVE_RATE"] = pdf["CUMULATIVE_SUCCESSES"] / pdf["TOTAL_CLIENTS"] * 100

    # Rename for clarity
    pdf = pdf.rename(columns={"DAYS_TO_FIRST_SUCCESS": "DAY"})

    # Fill in missing days for complete curves
    complete_df = _fill_missing_days(pdf)

    # Calculate lift and CI
    lift_df = _calculate_lift_table(complete_df)

    return lift_df


def _fill_missing_days(pdf: pd.DataFrame) -> pd.DataFrame:
    """
    Fill in missing days to create complete curves.

    Some days may have no successes, but we need continuous
    curves for proper visualization.
    """
    cohorts = pdf["COHORT"].unique()
    groups = ["TEST", "CONTROL"]

    complete_rows = []

    for cohort in cohorts:
        for group in groups:
            cohort_group_data = pdf[(pdf["COHORT"] == cohort) & (pdf["GROUP"] == group)]

            if cohort_group_data.empty:
                continue

            total_clients = cohort_group_data["TOTAL_CLIENTS"].iloc[0]
            window_days = int(cohort_group_data["WINDOW_DAYS"].iloc[0])
            max_day_with_data = cohort_group_data["DAY"].max()

            cum_successes = 0

            for day in range(0, window_days + 1):
                # Don't extrapolate beyond available data
                if day > max_day_with_data:
                    break

                day_data = cohort_group_data[cohort_group_data["DAY"] == day]

                if not day_data.empty:
                    cum_successes = day_data["CUMULATIVE_SUCCESSES"].iloc[0]

                complete_rows.append({
                    "COHORT": cohort,
                    "GROUP": group,
                    "DAY": day,
                    "WINDOW_DAYS": window_days,
                    "TOTAL_CLIENTS": total_clients,
                    "CUMULATIVE_SUCCESSES": cum_successes,
                    "CUMULATIVE_RATE": cum_successes / total_clients * 100 if total_clients > 0 else 0
                })

    return pd.DataFrame(complete_rows)


def _calculate_lift_table(complete_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate lift and confidence intervals for each cohort-day.

    Compares TEST vs CONTROL cumulative rates.
    """
    cohorts = complete_df["COHORT"].unique()
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

            test_successes = test_row["CUMULATIVE_SUCCESSES"].iloc[0]
            test_n = test_row["TOTAL_CLIENTS"].iloc[0]
            ctrl_successes = ctrl_row["CUMULATIVE_SUCCESSES"].iloc[0]
            ctrl_n = ctrl_row["TOTAL_CLIENTS"].iloc[0]

            lift, ci_lower, ci_upper = calculate_confidence_interval(
                test_successes, test_n, ctrl_successes, ctrl_n
            )

            lift_rows.append({
                "COHORT": cohort,
                "DAY": day,
                "WINDOW_DAYS": window_days,
                "TEST_CLIENTS": test_n,
                "TEST_SUCCESSES": test_successes,
                "TEST_RATE": test_row["CUMULATIVE_RATE"].iloc[0],
                "CTRL_CLIENTS": ctrl_n,
                "CTRL_SUCCESSES": ctrl_successes,
                "CTRL_RATE": ctrl_row["CUMULATIVE_RATE"].iloc[0],
                "ABS_LIFT": lift * 100,  # Convert to percentage points
                "CI_LOWER": ci_lower * 100,
                "CI_UPPER": ci_upper * 100
            })

    lift_df = pd.DataFrame(lift_rows)

    # Add significance flag (CI doesn't cross zero)
    if not lift_df.empty:
        lift_df["SIGNIFICANT"] = (lift_df["CI_LOWER"] > 0) | (lift_df["CI_UPPER"] < 0)

    return lift_df


def generate_summary_table(lift_df: pd.DataFrame, mne: str) -> pd.DataFrame:
    """
    Generate summary table with final rates per cohort.

    Takes the maximum day (end of measurement window) for each cohort
    to create a summary of final results.

    Args:
        lift_df: Result from prepare_vintage_table()
        mne: Campaign mnemonic

    Returns:
        Pandas DataFrame with one row per cohort showing final metrics
    """
    if lift_df.empty:
        return pd.DataFrame()

    # Get max day per cohort (final measurement)
    final_rates = lift_df.loc[lift_df.groupby("COHORT")["DAY"].idxmax()].copy()

    final_rates["MNE"] = mne

    # Reorder columns
    columns = [
        "MNE", "COHORT", "WINDOW_DAYS",
        "TEST_CLIENTS", "TEST_SUCCESSES", "TEST_RATE",
        "CTRL_CLIENTS", "CTRL_SUCCESSES", "CTRL_RATE",
        "ABS_LIFT", "CI_LOWER", "CI_UPPER", "SIGNIFICANT"
    ]

    final_rates = final_rates[columns].sort_values("COHORT")

    return final_rates


def calculate_overall_lift(lift_df: pd.DataFrame) -> dict:
    """
    Calculate overall lift across all cohorts.

    Useful for executive summaries.

    Args:
        lift_df: Result from prepare_vintage_table()

    Returns:
        Dictionary with overall statistics
    """
    if lift_df.empty:
        return {}

    # Get final day for each cohort
    final_rows = lift_df.loc[lift_df.groupby("COHORT")["DAY"].idxmax()]

    # Sum totals across cohorts
    total_test_clients = final_rows["TEST_CLIENTS"].sum()
    total_test_successes = final_rows["TEST_SUCCESSES"].sum()
    total_ctrl_clients = final_rows["CTRL_CLIENTS"].sum()
    total_ctrl_successes = final_rows["CTRL_SUCCESSES"].sum()

    # Calculate overall lift
    lift, ci_lower, ci_upper = calculate_confidence_interval(
        total_test_successes, total_test_clients,
        total_ctrl_successes, total_ctrl_clients
    )

    return {
        "total_test_clients": int(total_test_clients),
        "total_test_successes": int(total_test_successes),
        "test_rate": total_test_successes / total_test_clients * 100 if total_test_clients > 0 else 0,
        "total_ctrl_clients": int(total_ctrl_clients),
        "total_ctrl_successes": int(total_ctrl_successes),
        "ctrl_rate": total_ctrl_successes / total_ctrl_clients * 100 if total_ctrl_clients > 0 else 0,
        "overall_lift_pp": lift * 100,
        "ci_lower_pp": ci_lower * 100,
        "ci_upper_pp": ci_upper * 100,
        "significant": (ci_lower > 0) or (ci_upper < 0)
    }
