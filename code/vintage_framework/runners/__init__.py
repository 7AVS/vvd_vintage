"""
Vintage Framework - Runners Module
==================================

Entry points for running vintage curve analysis.

Usage:
    # In Jupyter notebook:
    from vintage_framework.runners import run_vintage_analysis, run_all_campaigns

    # Run single campaign
    results = run_vintage_analysis(spark, "VCN")

    # Run all VVD campaigns
    all_results = run_all_campaigns(spark, "VVD")
"""

from .run_vintage import (
    run_vintage_analysis,
    run_all_campaigns,
    VintageAnalysisResult
)

__all__ = [
    "run_vintage_analysis",
    "run_all_campaigns",
    "VintageAnalysisResult"
]
