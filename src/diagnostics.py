"""
Vintage Engine Diagnostics
==========================

Run this separately to diagnose issues with the vintage engine results.
Copy into a Jupyter cell and run after running vintage analysis.

Usage:
  # Single campaign
  results = run_vintage_analysis(spark, 'VCN')
  diagnose_results(results)

  # Multiple campaigns
  results = run_all_campaigns(spark, ['VCN', 'VDA'])
  diagnose_results(results)
"""

import pandas as pd


def _detect_result_structure(results):
    """
    Detect if results are flat (single campaign) or nested (multi-campaign).

    Returns: 'flat', 'nested', or 'unknown'
    """
    if not isinstance(results, dict):
        return 'unknown'

    # Check for flat structure (single campaign)
    # Keys would be: vintage_df, summary_df, channel_breakdown_df, etc.
    flat_keys = {'vintage_df', 'summary_df', 'channel_breakdown_df',
                 'engagement_summary_df', 'engagement_vintage_df'}
    if any(key in results for key in flat_keys):
        return 'flat'

    # Check for nested structure (multi-campaign)
    # Keys would be campaign mnemonics: VCN, VDA, etc.
    for key, value in results.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and any(k in value for k in flat_keys):
            return 'nested'

    return 'unknown'


def diagnose_results(results):
    """
    Diagnose the structure of results from run_vintage_analysis or run_all_campaigns.

    Handles both:
    - Flat structure (single campaign): results["vintage_df"]
    - Nested structure (multi-campaign): results["VCN"]["vintage_df"]
    """
    print("="*70)
    print("RESULTS DIAGNOSTIC")
    print("="*70)

    if results is None:
        print("ERROR: results is None")
        return

    print(f"\nType of results: {type(results)}")

    if not isinstance(results, dict):
        print(f"ERROR: Expected dict, got {type(results)}")
        print(f"Value: {results}")
        return

    # Detect structure
    structure = _detect_result_structure(results)
    print(f"Structure detected: {structure.upper()}")
    print(f"Keys in results: {list(results.keys())}")

    print("\n" + "-"*70)
    print("DETAIL BY KEY:")
    print("-"*70)

    for key, value in results.items():
        print(f"\n[{key}]")
        print(f"  Type: {type(value)}")

        if value is None:
            print("  Value: None")
        elif isinstance(value, dict):
            print(f"  Dict keys: {list(value.keys())}")
            for k, v in value.items():
                if isinstance(v, pd.DataFrame):
                    print(f"    {k}: DataFrame with {len(v)} rows, columns: {list(v.columns)}")
                elif v is None:
                    print(f"    {k}: None")
                else:
                    print(f"    {k}: {type(v)}")
        elif isinstance(value, pd.DataFrame):
            print(f"  DataFrame with {len(value)} rows")
            print(f"  Columns: {list(value.columns)}")
        else:
            print(f"  Value preview: {str(value)[:100]}")

    print("\n" + "="*70)
    print("EXPORT READINESS CHECK")
    print("="*70)

    # Check what can be exported based on structure
    can_export_vintage = False
    can_export_channel = False
    can_export_engagement = False
    can_export_summary = False

    if structure == 'flat':
        # Single campaign - check directly
        can_export_vintage = isinstance(results.get("vintage_df"), pd.DataFrame)
        can_export_channel = isinstance(results.get("channel_breakdown_df"), pd.DataFrame)
        can_export_engagement = isinstance(results.get("engagement_vintage_df"), pd.DataFrame)
        can_export_summary = isinstance(results.get("summary_df"), pd.DataFrame)
        print(f"\n  Single campaign result detected.")

    elif structure == 'nested':
        # Multi-campaign - check nested dicts
        for key, value in results.items():
            if key.startswith("_"):
                continue
            if isinstance(value, dict):
                if isinstance(value.get("vintage_df"), pd.DataFrame):
                    can_export_vintage = True
                if isinstance(value.get("channel_breakdown_df"), pd.DataFrame):
                    can_export_channel = True
                if isinstance(value.get("engagement_vintage_df"), pd.DataFrame):
                    can_export_engagement = True
                if isinstance(value.get("summary_df"), pd.DataFrame):
                    can_export_summary = True
        print(f"\n  Multi-campaign result detected.")
    else:
        print(f"\n  WARNING: Could not determine result structure.")

    print(f"\n  vintage_curves.csv:     {'YES' if can_export_vintage else 'NO'}")
    print(f"  channel_breakdown.csv:  {'YES' if can_export_channel else 'NO'}")
    print(f"  engagement_vintage.csv: {'YES' if can_export_engagement else 'NO'}")
    print(f"  summary.csv:            {'YES' if can_export_summary else 'NO'}")

    if not any([can_export_vintage, can_export_channel, can_export_engagement, can_export_summary]):
        print("\n  WARNING: Nothing to export!")
        print("  Check that run_vintage_analysis completed successfully.")
    else:
        print(f"\n  READY TO EXPORT: {sum([can_export_vintage, can_export_channel, can_export_engagement, can_export_summary])}/4 files")

    # Provide export hint based on structure
    if structure == 'flat':
        print("\n  HINT: For single campaign, wrap before export:")
        print("        results_wrapped = {'VCN': results}")
        print("        export_all_to_hdfs(results_wrapped, spark)")

    print("\n" + "="*70)


def diagnose_single_result(result, mne="UNKNOWN"):
    """
    Diagnose a single campaign result.
    """
    print(f"\nDiagnosing result for {mne}:")
    print(f"  Type: {type(result)}")

    if result is None:
        print("  Result is None")
        return

    if isinstance(result, dict):
        print(f"  Keys: {list(result.keys())}")
        for k, v in result.items():
            if isinstance(v, pd.DataFrame):
                print(f"    {k}: {len(v)} rows")
            elif v is None:
                print(f"    {k}: None")
            else:
                print(f"    {k}: {type(v)}")
    elif isinstance(result, pd.DataFrame):
        print(f"  DataFrame: {len(result)} rows, columns: {list(result.columns)}")
    else:
        print(f"  Unexpected type: {type(result)}")


def test_export_ready(results):
    """
    Quick check if results are ready for export.
    Returns True if exportable data exists.

    Handles both flat (single campaign) and nested (multi-campaign) structures.
    """
    if not isinstance(results, dict):
        return False

    structure = _detect_result_structure(results)

    if structure == 'flat':
        return isinstance(results.get("vintage_df"), pd.DataFrame)

    elif structure == 'nested':
        for key, value in results.items():
            if key.startswith("_"):
                continue
            if isinstance(value, dict) and isinstance(value.get("vintage_df"), pd.DataFrame):
                return True

    return False


def wrap_single_result(results, mne):
    """
    Wrap a single campaign result into multi-campaign format for export.

    Usage:
        results = run_vintage_analysis(spark, 'VCN')
        wrapped = wrap_single_result(results, 'VCN')
        export_all_to_hdfs(wrapped, spark)
    """
    structure = _detect_result_structure(results)

    if structure == 'flat':
        return {mne: results}
    elif structure == 'nested':
        print(f"Results already in nested format, returning as-is.")
        return results
    else:
        print(f"WARNING: Unknown structure, wrapping anyway.")
        return {mne: results}
