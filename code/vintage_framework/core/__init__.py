"""
Vintage Framework - Core Module
===============================

This module contains the core processing logic for vintage curve analysis.

Pipeline Flow:
1. experiment_metadata_loader - [WIP] Extract experiment design from tactic/ODS
2. tactic_loader - Load population (clients in campaign)
3. success_loader - Load success data based on campaign type
4. success_detector - Join tactic with success to identify conversions
5. vintage_calculator - Calculate vintage curves with lift and CI
6. plotter - Generate visualizations

Reference: Success Library Layer 3 - Centralized Logic Repo
"""

from .tactic_loader import load_tactic, load_tactic_for_campaigns
from .success_loader import load_success_table
from .success_detector import detect_success
from .vintage_calculator import (
    build_vintage_data,
    prepare_vintage_table,
    generate_summary_table,
    calculate_confidence_interval
)
from .plotter import plot_campaign_vintage, plot_test_vs_control_by_cohort
from .experiment_metadata_loader import discover_campaign_structure

__all__ = [
    # Loaders
    "load_tactic",
    "load_tactic_for_campaigns",
    "load_success_table",

    # Processing
    "detect_success",
    "build_vintage_data",
    "prepare_vintage_table",
    "generate_summary_table",
    "calculate_confidence_interval",

    # Visualization
    "plot_campaign_vintage",
    "plot_test_vs_control_by_cohort",

    # Experiment metadata (WIP)
    "discover_campaign_structure",
]
