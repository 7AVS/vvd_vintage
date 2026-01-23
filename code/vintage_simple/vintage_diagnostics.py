"""
Vintage Engine Diagnostics
==========================

Run this separately to diagnose issues with the vintage engine results.
Copy into a Jupyter cell and run after running vintage analysis.

Usage:
  # After running analysis
  results = run_vintage_analysis(spark, 'VCN')

  # Then run diagnostics
  diagnose_results(results)
"""

import pandas as pd

def diagnose_results(results):
    """
    Diagnose the structure of results from run_vintage_analysis.

    Helps identify issues before export.
    """
    print("="*60)
    print("RESULTS DIAGNOSTIC")
    print("="*60)

    if results is None:
        print("ERROR: results is None")
        return

    print(f"\nType of results: {type(results)}")

    if not isinstance(results, dict):
        print(f"ERROR: Expected dict, got {type(results)}")
        print(f"Value: {results}")
        return

    print(f"Keys in results: {list(results.keys())}")

    print("\n" + "-"*60)
    print("DETAIL BY KEY:")
    print("-"*60)

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

    print("\n" + "="*60)
    print("EXPORT READINESS CHECK")
    print("="*60)

    # Check what can be exported
    can_export_vintage = False
    can_export_channel = False
    can_export_engagement = False
    can_export_summary = False

    for key, value in results.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            if value.get("vintage_df") is not None:
                can_export_vintage = True
            if value.get("channel_breakdown_df") is not None:
                can_export_channel = True
            if value.get("engagement_vintage_df") is not None:
                can_export_engagement = True
            if value.get("summary_df") is not None:
                can_export_summary = True

    print(f"  vintage_curves.csv:     {'YES' if can_export_vintage else 'NO'}")
    print(f"  channel_breakdown.csv:  {'YES' if can_export_channel else 'NO'}")
    print(f"  engagement_vintage.csv: {'YES' if can_export_engagement else 'NO'}")
    print(f"  summary.csv:            {'YES' if can_export_summary else 'NO'}")

    if not any([can_export_vintage, can_export_channel, can_export_engagement, can_export_summary]):
        print("\n  WARNING: Nothing to export!")
        print("  Check that run_vintage_analysis completed successfully.")

    print("\n" + "="*60)


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


# Quick test function
def test_export_ready(results):
    """
    Quick check if results are ready for export.
    Returns True if at least one campaign has exportable data.
    """
    if not isinstance(results, dict):
        return False

    for key, value in results.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and value.get("vintage_df") is not None:
            return True

    return False
