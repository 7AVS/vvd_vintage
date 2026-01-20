"""
Vintage Analysis Runner
=======================

Copy this into a Jupyter notebook cell to run the analysis.

Usage:
    1. Upload config.py and vintage_pipeline.py to your Lumina environment
    2. Copy this code into a notebook cell
    3. Run!
"""

# =============================================================================
# SETUP - Run this cell first
# =============================================================================

from pyspark.sql import SparkSession

# Create Spark session (may already exist in Lumina)
spark = SparkSession.builder \
    .appName("VVD Vintage Curves") \
    .getOrCreate()

# Import the pipeline
from config import list_campaigns, CAMPAIGN_CONFIG
from vintage_pipeline import run_vintage_analysis, run_all_campaigns

# Show available campaigns
print("Available campaigns:")
list_campaigns()


# =============================================================================
# OPTION 1: Run a single campaign
# =============================================================================

# Uncomment to run:
# results = run_vintage_analysis(spark, "VCN")


# =============================================================================
# OPTION 2: Run all campaigns
# =============================================================================

# Uncomment to run:
# all_results = run_all_campaigns(spark)


# =============================================================================
# OPTION 3: Run specific campaigns
# =============================================================================

# Uncomment to run:
# results = run_all_campaigns(spark, mnes=["VCN", "VDT", "VUI"])


# =============================================================================
# OPTION 4: Run without saving (just view plots)
# =============================================================================

# Uncomment to run:
# results = run_vintage_analysis(spark, "VCN", save_outputs=False)


# =============================================================================
# ACCESS RESULTS
# =============================================================================

# After running, you can access:
# results["vintage_df"]  - Full vintage data (pandas DataFrame)
# results["summary_df"]  - Summary table (pandas DataFrame)
# results["paths"]       - Output file paths

# Example:
# df = results["vintage_df"]
# df.head()
