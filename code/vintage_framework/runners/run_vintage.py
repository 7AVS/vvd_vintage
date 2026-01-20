"""
Vintage Analysis Runner
=======================

Main entry point for running vintage curve analysis.

This module orchestrates the full pipeline:
1. Load tactic data (population)
2. [Optional] Discover campaign structure
3. Load success data
4. Detect success (join tactic with success)
5. Build vintage curves
6. Generate plots and outputs

Usage in Jupyter:
    from pyspark.sql import SparkSession
    from vintage_framework.runners import run_vintage_analysis, run_all_campaigns

    spark = SparkSession.builder.appName("Vintage Analysis").getOrCreate()

    # Single campaign
    results = run_vintage_analysis(spark, "VCN")

    # All VVD campaigns
    all_results = run_all_campaigns(spark, "VVD")

Reference: Success Library Layer 3 - Centralized Logic Repo
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import pandas as pd

from pyspark.sql import SparkSession
from pyspark import StorageLevel

from ..config.campaigns import get_campaign_config, CAMPAIGN_REGISTRY
from ..config.paths import get_output_path
from ..core.tactic_loader import load_tactic, validate_tactic_data
from ..core.success_loader import load_success_table, validate_success_data
from ..core.success_detector import detect_success, get_success_summary, validate_success_detection
from ..core.vintage_calculator import (
    build_vintage_data,
    prepare_vintage_table,
    generate_summary_table,
    calculate_overall_lift
)
from ..core.plotter import (
    plot_campaign_vintage,
    plot_test_vs_control_by_cohort,
    plot_lift_over_time,
    create_summary_visualization
)
from ..core.experiment_metadata_loader import (
    discover_campaign_structure,
    print_campaign_structure,
    validate_experiment_design
)


@dataclass
class VintageAnalysisResult:
    """Container for vintage analysis results."""
    mne: str
    product: str
    success_type: str
    vintage_df: Optional[pd.DataFrame]
    summary_df: Optional[pd.DataFrame]
    overall_lift: Optional[Dict[str, Any]]
    campaign_structure: Optional[Dict[str, Any]]
    output_paths: Dict[str, str]
    success: bool
    error: Optional[str] = None


def run_vintage_analysis(
    spark: SparkSession,
    mne: str,
    product: str = "VVD",
    discover_structure: bool = False,
    save_outputs: bool = True,
    verbose: bool = True
) -> VintageAnalysisResult:
    """
    Run full vintage analysis for a single campaign.

    Pipeline Steps:
    1. Load campaign configuration
    2. Load tactic data
    3. [Optional] Discover campaign structure
    4. Load success data
    5. Detect success
    6. Build vintage curves
    7. Calculate lift and CI
    8. Generate plots
    9. Save outputs

    Args:
        spark: Active SparkSession
        mne: Campaign mnemonic (e.g., "VCN")
        product: Product code (default: "VVD")
        discover_structure: If True, run campaign structure discovery
        save_outputs: If True, save CSV and plots to output path
        verbose: If True, print progress messages

    Returns:
        VintageAnalysisResult with all outputs and metadata
    """
    output_paths = {}

    def log(msg: str):
        if verbose:
            print(msg)

    try:
        # Step 0: Load configuration
        log(f"\n{'='*60}")
        log(f"Running Vintage Analysis for {mne}")
        log(f"{'='*60}")

        config = get_campaign_config(product, mne)
        log(f"Campaign: {config.get('campaign_name', config.get('description', 'N/A'))}")
        log(f"Success Type: {config['success_type']}")
        log(f"Source: {config['success_source']}")

        # Step 1: Load tactic data
        log("\n[1] Loading tactic data...")
        tactic_df = load_tactic(spark, mne)
        tactic_validation = validate_tactic_data(tactic_df)

        if not tactic_validation["valid"]:
            raise ValueError(f"Tactic validation failed: {tactic_validation.get('error', 'Unknown')}")

        log(f"    Tactic records: {tactic_validation['total_records']:,}")
        log(f"    Cohorts: {tactic_validation['cohort_count']}")
        log(f"    Groups: {tactic_validation['group_distribution']}")

        if tactic_validation['total_records'] == 0:
            raise ValueError(f"No tactic records found for {mne}")

        # Step 2: [Optional] Discover campaign structure
        campaign_structure = None
        if discover_structure:
            log("\n[2] Discovering campaign structure...")
            campaign_structure = discover_campaign_structure(tactic_df, mne)
            validation = validate_experiment_design(campaign_structure)

            if validation["warnings"]:
                for warn in validation["warnings"]:
                    log(f"    WARNING: {warn}")

            if verbose:
                print_campaign_structure(campaign_structure)

        # Step 3: Load success data
        log("\n[3] Loading success table...")
        success_table = load_success_table(spark, config)
        success_validation = validate_success_data(success_table, config)

        if not success_validation["valid"]:
            raise ValueError(f"Success data validation failed: {success_validation.get('error', 'Unknown')}")

        log(f"    Success records: {success_validation['total_records']:,}")
        log(f"    Date range: {success_validation['date_range']['min']} to {success_validation['date_range']['max']}")

        # Step 4: Detect success
        log("\n[4] Detecting success...")
        success_df = detect_success(tactic_df, success_table, config)
        success_df.persist(StorageLevel.MEMORY_AND_DISK)

        detection_validation = validate_success_detection(success_df)
        if not detection_validation["valid"]:
            raise ValueError(f"Success detection failed: {detection_validation.get('error', 'Unknown')}")

        log(f"    Total records: {detection_validation['total_records']:,}")
        log(f"    Total successes: {detection_validation['total_successes']:,}")
        log(f"    Overall rate: {detection_validation['overall_success_rate']*100:.2f}%")

        # Show summary by group
        log("\n[5] Success summary by group:")
        summary_by_group = get_success_summary(success_df)
        if verbose:
            summary_by_group.show()

        # Step 5: Build vintage data
        log("\n[6] Building vintage curves...")
        vintage_spark = build_vintage_data(success_df)

        # Step 6: Calculate lift and CI
        log("\n[7] Calculating lift and confidence intervals...")
        vintage_df = prepare_vintage_table(vintage_spark)

        if vintage_df.empty:
            raise ValueError("No vintage data generated - check data quality")

        # Step 7: Generate summary table
        log("\n[8] Generating summary table...")
        summary_df = generate_summary_table(vintage_df, mne)
        overall_lift = calculate_overall_lift(vintage_df)

        if verbose:
            log("\nSummary Table (Final Rates by Cohort):")
            print(summary_df.to_string(index=False))

            log("\nOverall Lift:")
            log(f"    Test Rate: {overall_lift['test_rate']:.2f}%")
            log(f"    Control Rate: {overall_lift['ctrl_rate']:.2f}%")
            log(f"    Lift: {overall_lift['overall_lift_pp']:.2f}pp [{overall_lift['ci_lower_pp']:.2f}, {overall_lift['ci_upper_pp']:.2f}]")
            log(f"    Significant: {overall_lift['significant']}")

        # Step 8: Generate plots
        if save_outputs:
            log("\n[9] Generating plots...")
            cohorts = sorted(vintage_df["COHORT"].unique())
            log(f"    Found {len(cohorts)} cohorts")

            # Plot 1: All cohorts on one chart
            save_path_1 = get_output_path(f"{mne}_vintage_all_cohorts.png")
            plot_campaign_vintage(vintage_df, mne, config, save_path_1)
            output_paths["vintage_plot"] = save_path_1

            # Plot 2: Grid view (if not too many cohorts)
            if len(cohorts) <= 12:
                save_path_2 = get_output_path(f"{mne}_vintage_grid.png")
                plot_test_vs_control_by_cohort(vintage_df, mne, config, save_path_2)
                output_paths["grid_plot"] = save_path_2

            # Plot 3: Lift over time
            save_path_3 = get_output_path(f"{mne}_lift_over_time.png")
            plot_lift_over_time(vintage_df, mne, config, save_path_3)
            output_paths["lift_plot"] = save_path_3

            # Plot 4: Summary bar chart
            save_path_4 = get_output_path(f"{mne}_summary_bars.png")
            create_summary_visualization(summary_df, mne, config, save_path_4)
            output_paths["summary_plot"] = save_path_4

            # Step 9: Save data outputs
            log("\n[10] Saving outputs...")
            vintage_df["MNE"] = mne

            full_csv_path = get_output_path(f"{mne}_vintage_full.csv")
            summary_csv_path = get_output_path(f"{mne}_vintage_summary.csv")

            vintage_df.to_csv(full_csv_path, index=False)
            summary_df.to_csv(summary_csv_path, index=False)

            output_paths["vintage_csv"] = full_csv_path
            output_paths["summary_csv"] = summary_csv_path

            log(f"    Full table: {full_csv_path}")
            log(f"    Summary: {summary_csv_path}")

        # Cleanup
        success_df.unpersist()

        log(f"\n{'='*60}")
        log(f"ANALYSIS COMPLETE: {mne}")
        log(f"{'='*60}")

        return VintageAnalysisResult(
            mne=mne,
            product=product,
            success_type=config["success_type"],
            vintage_df=vintage_df,
            summary_df=summary_df,
            overall_lift=overall_lift,
            campaign_structure=campaign_structure,
            output_paths=output_paths,
            success=True
        )

    except Exception as e:
        log(f"\n*** ERROR processing {mne}: {str(e)} ***")

        return VintageAnalysisResult(
            mne=mne,
            product=product,
            success_type="UNKNOWN",
            vintage_df=None,
            summary_df=None,
            overall_lift=None,
            campaign_structure=None,
            output_paths=output_paths,
            success=False,
            error=str(e)
        )


def run_all_campaigns(
    spark: SparkSession,
    product: str = "VVD",
    mnes: List[str] = None,
    discover_structure: bool = False,
    save_outputs: bool = True,
    verbose: bool = True
) -> Dict[str, VintageAnalysisResult]:
    """
    Run vintage analysis for all campaigns of a product.

    Args:
        spark: Active SparkSession
        product: Product code (default: "VVD")
        mnes: Optional list of specific MNEs to run (default: all for product)
        discover_structure: If True, run campaign structure discovery
        save_outputs: If True, save CSV and plots
        verbose: If True, print progress messages

    Returns:
        Dictionary mapping MNE to VintageAnalysisResult
    """
    # Get campaign list
    if mnes is None:
        if product not in CAMPAIGN_REGISTRY:
            raise ValueError(f"Product '{product}' not found. Available: {list(CAMPAIGN_REGISTRY.keys())}")
        mnes = list(CAMPAIGN_REGISTRY[product].keys())

    results = {}
    all_vintage_tables = []
    all_summary_tables = []

    print(f"\n{'='*60}")
    print(f"RUNNING ALL {product} CAMPAIGNS")
    print(f"Campaigns: {', '.join(mnes)}")
    print(f"{'='*60}")

    # Run each campaign
    for mne in mnes:
        result = run_vintage_analysis(
            spark=spark,
            mne=mne,
            product=product,
            discover_structure=discover_structure,
            save_outputs=save_outputs,
            verbose=verbose
        )

        results[mne] = result

        if result.success and result.vintage_df is not None:
            all_vintage_tables.append(result.vintage_df)
            all_summary_tables.append(result.summary_df)

    # Combine all results
    if all_vintage_tables and save_outputs:
        print(f"\n{'='*60}")
        print("COMBINING ALL CAMPAIGN RESULTS")
        print(f"{'='*60}")

        combined_vintage = pd.concat(all_vintage_tables, ignore_index=True)
        combined_summary = pd.concat(all_summary_tables, ignore_index=True)

        combined_vintage_path = get_output_path(f"ALL_{product}_vintage_full.csv")
        combined_summary_path = get_output_path(f"ALL_{product}_vintage_summary.csv")

        combined_vintage.to_csv(combined_vintage_path, index=False)
        combined_summary.to_csv(combined_summary_path, index=False)

        print(f"\nCombined full table: {combined_vintage_path}")
        print(f"Combined summary: {combined_summary_path}")

        print(f"\n{'='*60}")
        print(f"FINAL SUMMARY - ALL {product} CAMPAIGNS")
        print(f"{'='*60}")
        print(combined_summary.to_string(index=False))

    # Print final status
    successful = sum(1 for r in results.values() if r.success)
    failed = len(results) - successful

    print(f"\n{'='*60}")
    print(f"ANALYSIS COMPLETE")
    print(f"Successful: {successful}/{len(results)}")
    if failed > 0:
        print(f"Failed: {failed}")
        for mne, result in results.items():
            if not result.success:
                print(f"  - {mne}: {result.error}")
    print(f"{'='*60}")

    return results


# =============================================================================
# JUPYTER NOTEBOOK ENTRY POINT
# =============================================================================

def create_spark_session(app_name: str = "Vintage Analysis") -> SparkSession:
    """
    Create or get existing SparkSession.

    Convenience function for Jupyter notebooks.
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()


# Example usage when running as script
if __name__ == "__main__":
    # This would typically be run in a Jupyter notebook
    spark = create_spark_session()

    # Run all VVD campaigns
    results = run_all_campaigns(spark, "VVD")
