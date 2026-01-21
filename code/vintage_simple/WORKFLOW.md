# VVD Vintage Dashboard Workflow

## Overview

```
YARN/Spark (Jupyter)              Local (VS Code)
────────────────────              ────────────────
1. Run vintage_all_in_one.py  →
2. export_to_hdfs_csv()       →   3. Download CSV from Hue
                                  4. Run dashboard code
                                  5. Get HTML file
                                  6. Share anywhere
```

---

## Step 1: Run Analysis on YARN/Spark Jupyter

Copy the entire `vintage_all_in_one.py` into a Jupyter notebook cell and run it.

Then execute:

```python
# Run the analysis for all campaigns
results = run_all_campaigns(spark)

# Or run for a single campaign
results = run_vintage_analysis(spark, 'VCN')
```

---

## Step 2: Export to HDFS

```python
# Export results to your HDFS folder as CSV
export_to_hdfs_csv(results, spark)
```

This saves to: `/user/427966379/vintage_data.csv`

---

## Step 3: Download from Hue

1. Go to **Hue** → **File Browser**
2. Navigate to `/user/427966379/vintage_data.csv`
3. Download the CSV to your local computer
4. Put the CSV in: `Vvd/source/` folder

---

## Step 4: Generate Dashboard Locally (VS Code)

On your local machine, run:

```python
from vintage_dashboard import generate_dashboard_from_csv

generate_dashboard_from_csv(
    "C:/path/to/vintage_data.csv",      # where you saved the CSV
    "vvd_vintage_dashboard.html"         # output HTML file
)
```

Or from command line:

```bash
cd /mnt/c/Users/andre/New_projects/Vintage/Vvd/code/vintage_simple
python -c "from vintage_dashboard import generate_dashboard_from_csv; generate_dashboard_from_csv('vintage_data.csv', 'vvd_vintage_dashboard.html')"
```

---

## Step 5: Use the Dashboard

- Open `vvd_vintage_dashboard.html` in any browser
- Upload to SharePoint
- Email to stakeholders
- No server needed - it's a standalone HTML file

---

## Quick Reference

| Task | Command |
|------|---------|
| Run all campaigns | `results = run_all_campaigns(spark)` |
| Run single campaign | `results = run_vintage_analysis(spark, 'VCN')` |
| Export to HDFS | `export_to_hdfs_csv(results, spark)` |
| Generate HTML from CSV | `generate_dashboard_from_csv('data.csv', 'dashboard.html')` |

---

## Available Campaigns

- VCN - Contextual Notification
- VDA - Black Friday Cyber Monday Targeted
- VDT - Activation Trigger
- VUI - Usage Trigger
- VUT - Tokenization Usage
- VAW - Add To Wallet Contextual Notification
