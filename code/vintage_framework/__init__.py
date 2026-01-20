"""
Vintage Curve Framework
=======================

A standardized, modular framework for generating vintage curves
for marketing campaign measurement.

Quick Start:
    from pyspark.sql import SparkSession
    from vintage_framework.runners import run_vintage_analysis, run_all_campaigns

    spark = SparkSession.builder.appName("Vintage Analysis").getOrCreate()

    # Run single campaign
    results = run_vintage_analysis(spark, "VCN")

    # Run all VVD campaigns
    all_results = run_all_campaigns(spark, "VVD")

Reference:
    - Success Library Layer 3: Centralized Logic Repo
    - VVD Vintage Framework Design Document
"""

__version__ = "1.0.0"
__author__ = "Marketing Analytics Team"

# Expose main entry points at package level
from .runners import run_vintage_analysis, run_all_campaigns, VintageAnalysisResult
from .config.campaigns import get_campaign_config, list_campaigns, CAMPAIGN_REGISTRY

__all__ = [
    # Main functions
    "run_vintage_analysis",
    "run_all_campaigns",
    "VintageAnalysisResult",

    # Config access
    "get_campaign_config",
    "list_campaigns",
    "CAMPAIGN_REGISTRY",
]
