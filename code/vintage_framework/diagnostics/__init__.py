"""
Vintage Framework - Diagnostics Module
======================================

Scripts for investigating data before running vintage analysis.

Usage:
    from vintage_framework.diagnostics import (
        # User parquet diagnostics
        run_tactic_diagnostics,
        run_success_diagnostics,

        # Source table diagnostics (Layer 1 fields)
        run_ods_diagnostics,
        run_tactic_evnt_diagnostics,
    )

    # Run diagnostics
    tactic_results = run_tactic_diagnostics(spark)
    success_results = run_success_diagnostics(spark)

    # Investigate source tables for Layer 1 fields
    ods_results = run_ods_diagnostics(spark)
    tactic_evnt_results = run_tactic_evnt_diagnostics(spark)
"""

from .diagnose_tactic_data import (
    run_tactic_diagnostics,
    investigate_segment_codes,
    check_client_overlap
)

from .diagnose_success_tables import (
    run_success_diagnostics,
    diagnose_visa_dr_crd,
    diagnose_pos_txn,
    diagnose_token,
    validate_join_keys
)

from .diagnose_ods_mr_hist import (
    run_ods_diagnostics,
    investigate_json_field,
    check_contextual_fields
)

from .diagnose_tactic_evnt_hist import (
    run_tactic_evnt_diagnostics,
    compare_tactic_sources
)

__all__ = [
    # User parquet diagnostics
    "run_tactic_diagnostics",
    "investigate_segment_codes",
    "check_client_overlap",

    # Success table diagnostics
    "run_success_diagnostics",
    "diagnose_visa_dr_crd",
    "diagnose_pos_txn",
    "diagnose_token",
    "validate_join_keys",

    # ODS_MR_HIST diagnostics (Layer 1 - JSON field)
    "run_ods_diagnostics",
    "investigate_json_field",
    "check_contextual_fields",

    # TACTIC_EVNT_HIST diagnostics (Layer 1 - source table)
    "run_tactic_evnt_diagnostics",
    "compare_tactic_sources",
]
