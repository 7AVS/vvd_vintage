"""
Base Configuration - Universal Standards
=========================================

These rules apply to ALL campaigns - no exceptions, no customization.
Based on VVD Vintage Framework Design Document.

Reference: Success Library Layer 3 - Centralized Logic Repo
"""

# =============================================================================
# AGGREGATION STANDARDS
# =============================================================================

# Cohort aggregation level - ALWAYS monthly, never weekly/daily
# Rationale: Keeps plots readable, especially for trigger campaigns with many waves
AGGREGATION_LEVEL = "MONTH"  # Format: yyyy-MM

# Date format for cohort labels
COHORT_DATE_FORMAT = "yyyy-MM"

# =============================================================================
# DATE FILTERS
# =============================================================================

# Years to include in analysis
# Adjust as needed for historical analysis
YEARS_TO_INCLUDE = [2025, 2026]

# =============================================================================
# TEST GROUP STANDARDS
# =============================================================================

# Test group identification
# TST_GRP_CD = 'TG4' is the action/test group
# All other values are control
TEST_GROUP_CODE = "TG4"
TEST_GROUP_LABEL = "TEST"
CONTROL_GROUP_LABEL = "CONTROL"

# =============================================================================
# MEASUREMENT WINDOW
# =============================================================================

# Measurement window is ALWAYS dynamic per deployment:
# WINDOW = TREATMT_END_DT - TREATMT_STRT_DT
# This is calculated at runtime, not configured here

# =============================================================================
# OUTPUT STANDARDS
# =============================================================================

# Standard output columns for vintage data
VINTAGE_OUTPUT_COLUMNS = [
    "MNE",
    "COHORT",
    "DAY",
    "WINDOW_DAYS",
    "GROUP",
    "TEST_CLIENTS",
    "TEST_SUCCESSES",
    "TEST_RATE",
    "CTRL_CLIENTS",
    "CTRL_SUCCESSES",
    "CTRL_RATE",
    "ABS_LIFT",
    "CI_LOWER",
    "CI_UPPER",
    "SIGNIFICANT"
]

# Summary output columns
SUMMARY_OUTPUT_COLUMNS = [
    "MNE",
    "COHORT",
    "WINDOW_DAYS",
    "TEST_CLIENTS",
    "TEST_SUCCESSES",
    "TEST_RATE",
    "CTRL_CLIENTS",
    "CTRL_SUCCESSES",
    "CTRL_RATE",
    "ABS_LIFT",
    "CI_LOWER",
    "CI_UPPER",
    "SIGNIFICANT"
]

# =============================================================================
# CONFIDENCE INTERVAL
# =============================================================================

# Confidence level for lift calculations
CONFIDENCE_LEVEL = 0.95

# =============================================================================
# PLOT STANDARDS
# =============================================================================

# Figure size for main vintage plot (all cohorts)
MAIN_PLOT_FIGSIZE = (14, 8)

# Figure size limits for grid plots
GRID_PLOT_MAX_WIDTH = 15
GRID_PLOT_MAX_HEIGHT = 12

# Maximum cohorts for grid view (beyond this, skip grid plot)
MAX_COHORTS_FOR_GRID = 12

# DPI for saved plots
PLOT_DPI = 100

# =============================================================================
# SUCCESS TYPES
# =============================================================================

# Standard success types recognized by the framework
# These align with Success Library metric pillars
SUCCESS_TYPES = [
    "ACQUISITION",    # New product issued/opened
    "ACTIVATION",     # Product activated by client
    "USAGE",          # Transaction/usage activity
    "TOKENIZATION",   # Digital wallet provisioning
    "ENGAGEMENT",     # Client interaction metrics
    "RETENTION",      # Client retention metrics
]
