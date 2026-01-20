"""
Plotter Module
==============

Generates visualizations for vintage curve analysis.

Plot Types:
1. Campaign Vintage: All cohorts on one chart (Test solid, Control dashed)
2. Grid View: One subplot per cohort for detailed comparison

Reference: VVD Vintage Framework Design Document
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from ..config.base_config import (
    MAIN_PLOT_FIGSIZE,
    GRID_PLOT_MAX_WIDTH,
    GRID_PLOT_MAX_HEIGHT,
    MAX_COHORTS_FOR_GRID,
    PLOT_DPI
)


def plot_campaign_vintage(
    vintage_df: pd.DataFrame,
    mne: str,
    config: dict,
    save_path: str
) -> None:
    """
    Plot vintage curves for ALL cohorts on ONE chart.

    Each cohort has two lines with the same color:
    - Solid line: Test group
    - Dashed line: Control group

    This visualization shows the overall campaign performance
    across all monthly cohorts.

    Args:
        vintage_df: Result from prepare_vintage_table()
        mne: Campaign mnemonic
        config: Campaign configuration dictionary
        save_path: Full path to save the plot
    """
    if vintage_df.empty:
        print(f"    WARNING: No data to plot for {mne}")
        return

    fig, ax = plt.subplots(figsize=MAIN_PLOT_FIGSIZE)

    # Get unique cohorts and assign colors
    cohorts = sorted(vintage_df["COHORT"].unique())
    n_cohorts = len(cohorts)

    # Select colormap based on number of cohorts
    if n_cohorts <= 10:
        colors = plt.cm.tab10(np.linspace(0, 1, 10))
    else:
        colors = plt.cm.tab20(np.linspace(0, 1, 20))

    # Plot each cohort
    for i, cohort in enumerate(cohorts):
        cohort_data = vintage_df[vintage_df["COHORT"] == cohort]

        if cohort_data.empty:
            continue

        color = colors[i % len(colors)]
        test_n = int(cohort_data["TEST_CLIENTS"].iloc[0])
        ctrl_n = int(cohort_data["CTRL_CLIENTS"].iloc[0])

        # Test line (solid)
        ax.plot(
            cohort_data["DAY"],
            cohort_data["TEST_RATE"],
            linestyle='-',
            marker='o',
            linewidth=1.5,
            markersize=3,
            color=color,
            label=f'{cohort} Test (n={test_n:,})',
            alpha=0.9
        )

        # Control line (dashed, same color)
        ax.plot(
            cohort_data["DAY"],
            cohort_data["CTRL_RATE"],
            linestyle='--',
            marker='s',
            linewidth=1.5,
            markersize=3,
            color=color,
            label=f'{cohort} Ctrl (n={ctrl_n:,})',
            alpha=0.7
        )

    # Formatting
    ax.set_xlabel("Days from Treatment", fontsize=12)
    ax.set_ylabel("Cumulative Conversion Rate (%)", fontsize=12)

    title = f"{mne} - {config.get('campaign_name', config.get('description', ''))}"
    subtitle = f"Vintage Curves: Test (solid) vs Control (dashed) | {config['success_type']}"
    ax.set_title(f"{title}\n{subtitle}", fontsize=13)

    ax.legend(
        title="Cohort / Group",
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        fontsize=8
    )

    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)

    plt.tight_layout()
    plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
    plt.close()

    print(f"    Plot saved: {save_path}")


def plot_test_vs_control_by_cohort(
    vintage_df: pd.DataFrame,
    mne: str,
    config: dict,
    save_path: str
) -> None:
    """
    Plot grid view with one subplot per cohort.

    Useful for detailed comparison of Test vs Control
    within each cohort, including lift annotations.

    Args:
        vintage_df: Result from prepare_vintage_table()
        mne: Campaign mnemonic
        config: Campaign configuration dictionary
        save_path: Full path to save the plot
    """
    cohorts = sorted(vintage_df["COHORT"].unique())
    n_cohorts = len(cohorts)

    if n_cohorts == 0:
        print(f"    WARNING: No cohorts to plot for {mne}")
        return

    if n_cohorts > MAX_COHORTS_FOR_GRID:
        print(f"    WARNING: Too many cohorts ({n_cohorts}) for grid view, skipping")
        return

    # Calculate grid dimensions
    n_cols = min(3, n_cohorts)
    n_rows = (n_cohorts + n_cols - 1) // n_cols

    # Calculate figure size with limits
    fig_width = min(5 * n_cols, GRID_PLOT_MAX_WIDTH)
    fig_height = min(4 * n_rows, GRID_PLOT_MAX_HEIGHT)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_width, fig_height), squeeze=False)

    # Plot each cohort
    for idx, cohort in enumerate(cohorts):
        row = idx // n_cols
        col = idx % n_cols
        ax = axes[row, col]

        cohort_data = vintage_df[vintage_df["COHORT"] == cohort]

        if cohort_data.empty:
            continue

        window_days = int(cohort_data["WINDOW_DAYS"].iloc[0])
        final_row = cohort_data[cohort_data["DAY"] == cohort_data["DAY"].max()].iloc[0]

        # Plot Test
        ax.plot(
            cohort_data["DAY"],
            cohort_data["TEST_RATE"],
            marker='o',
            linewidth=1.5,
            markersize=3,
            color='#2E86AB',
            label=f'Test (n={int(final_row["TEST_CLIENTS"]):,})'
        )

        # Plot Control
        ax.plot(
            cohort_data["DAY"],
            cohort_data["CTRL_RATE"],
            marker='s',
            linewidth=1.5,
            markersize=3,
            color='#A23B72',
            label=f'Control (n={int(final_row["CTRL_CLIENTS"]):,})'
        )

        # Add lift annotation
        lift_text = f'Lift: {final_row["ABS_LIFT"]:.2f}pp\n[{final_row["CI_LOWER"]:.2f}, {final_row["CI_UPPER"]:.2f}]'
        ax.annotate(
            lift_text,
            xy=(0.95, 0.05),
            xycoords='axes fraction',
            fontsize=8,
            ha='right',
            va='bottom',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )

        ax.set_title(f'Cohort: {cohort}', fontsize=10)
        ax.set_xlabel("Days", fontsize=9)
        ax.set_ylabel("Rate (%)", fontsize=9)
        ax.legend(fontsize=7, loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, window_days)
        ax.set_ylim(0, None)

    # Hide empty subplots
    for idx in range(n_cohorts, n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axes[row, col].set_visible(False)

    # Overall title
    title = f"{mne} - {config.get('campaign_name', config.get('description', ''))} | {config['success_type']}"
    fig.suptitle(title, fontsize=13, y=1.02)

    plt.tight_layout()
    plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
    plt.close()

    print(f"    Plot saved: {save_path}")


def plot_lift_over_time(
    vintage_df: pd.DataFrame,
    mne: str,
    config: dict,
    save_path: str
) -> None:
    """
    Plot lift (with confidence interval) over time for each cohort.

    Shows how the treatment effect develops over the measurement window.

    Args:
        vintage_df: Result from prepare_vintage_table()
        mne: Campaign mnemonic
        config: Campaign configuration dictionary
        save_path: Full path to save the plot
    """
    if vintage_df.empty:
        print(f"    WARNING: No data to plot for {mne}")
        return

    fig, ax = plt.subplots(figsize=MAIN_PLOT_FIGSIZE)

    cohorts = sorted(vintage_df["COHORT"].unique())
    n_cohorts = len(cohorts)

    if n_cohorts <= 10:
        colors = plt.cm.tab10(np.linspace(0, 1, 10))
    else:
        colors = plt.cm.tab20(np.linspace(0, 1, 20))

    for i, cohort in enumerate(cohorts):
        cohort_data = vintage_df[vintage_df["COHORT"] == cohort]

        if cohort_data.empty:
            continue

        color = colors[i % len(colors)]

        # Plot lift line
        ax.plot(
            cohort_data["DAY"],
            cohort_data["ABS_LIFT"],
            linestyle='-',
            linewidth=1.5,
            color=color,
            label=f'{cohort}',
            alpha=0.9
        )

        # Add confidence interval as shaded region
        ax.fill_between(
            cohort_data["DAY"],
            cohort_data["CI_LOWER"],
            cohort_data["CI_UPPER"],
            color=color,
            alpha=0.2
        )

    # Add zero line for reference
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)

    ax.set_xlabel("Days from Treatment", fontsize=12)
    ax.set_ylabel("Absolute Lift (percentage points)", fontsize=12)

    title = f"{mne} - {config.get('campaign_name', config.get('description', ''))}"
    ax.set_title(f"{title}\nLift Over Time (with 95% CI)", fontsize=13)

    ax.legend(title="Cohort", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
    plt.close()

    print(f"    Plot saved: {save_path}")


def create_summary_visualization(
    summary_df: pd.DataFrame,
    mne: str,
    config: dict,
    save_path: str
) -> None:
    """
    Create a bar chart showing final rates by cohort.

    Args:
        summary_df: Result from generate_summary_table()
        mne: Campaign mnemonic
        config: Campaign configuration dictionary
        save_path: Full path to save the plot
    """
    if summary_df.empty:
        print(f"    WARNING: No data for summary visualization")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    cohorts = summary_df["COHORT"].tolist()
    x = np.arange(len(cohorts))
    width = 0.35

    # Bar chart
    bars_test = ax.bar(x - width/2, summary_df["TEST_RATE"], width,
                       label='Test', color='#2E86AB', alpha=0.8)
    bars_ctrl = ax.bar(x + width/2, summary_df["CTRL_RATE"], width,
                       label='Control', color='#A23B72', alpha=0.8)

    # Add lift annotations
    for i, (_, row) in enumerate(summary_df.iterrows()):
        lift_text = f'{row["ABS_LIFT"]:.2f}pp'
        sig_marker = '*' if row["SIGNIFICANT"] else ''
        ax.annotate(
            f'{lift_text}{sig_marker}',
            xy=(x[i], max(row["TEST_RATE"], row["CTRL_RATE"]) + 0.5),
            ha='center',
            fontsize=8
        )

    ax.set_xlabel("Cohort", fontsize=12)
    ax.set_ylabel("Final Conversion Rate (%)", fontsize=12)
    ax.set_title(f"{mne} - Final Rates by Cohort\n(* indicates statistical significance)", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(cohorts, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
    plt.close()

    print(f"    Plot saved: {save_path}")
