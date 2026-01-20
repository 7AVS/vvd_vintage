"""
Vintage Framework - Diagnostics Module
======================================

Scripts for investigating data before running vintage analysis.

Usage:
    from vintage_framework.diagnostics.diagnose_tactic_data import run_tactic_diagnostics
    from vintage_framework.diagnostics.diagnose_success_tables import run_success_diagnostics

    # Run tactic diagnostics
    tactic_results = run_tactic_diagnostics(spark)

    # Run success table diagnostics
    success_results = run_success_diagnostics(spark)
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

__all__ = [
    # Tactic diagnostics
    "run_tactic_diagnostics",
    "investigate_segment_codes",
    "check_client_overlap",

    # Success table diagnostics
    "run_success_diagnostics",
    "diagnose_visa_dr_crd",
    "diagnose_pos_txn",
    "diagnose_token",
    "validate_join_keys",
]
