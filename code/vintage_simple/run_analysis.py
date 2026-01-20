"""
Vintage Analysis Runner
=======================

Copy this into a Jupyter notebook cell to run the analysis.
"""

# =============================================================================
# SETUP
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
# RUN ANALYSIS
# =============================================================================

# Single campaign
results = run_vintage_analysis(spark, "VCN")

# Or all campaigns:
# all_results = run_all_campaigns(spark)

# Or specific campaigns:
# results = run_all_campaigns(spark, mnes=["VCN", "VDT", "VUI"])


# =============================================================================
# ACCESS RESULTS
# =============================================================================

# After running, access data like this:
# vintage_data = results["vintage_df"]
# summary_data = results["summary_df"]
# vintage_data.head()
