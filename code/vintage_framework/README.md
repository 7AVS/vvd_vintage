# Vintage Curve Framework

A standardized, modular framework for generating vintage curves for marketing campaign measurement.

## Overview

This framework provides a reusable pipeline for calculating and visualizing vintage curves (cumulative success rates over time) for marketing campaigns. It is designed to:

- **Work now**: Pull from raw tables, produce curves and outputs
- **Align with the future**: Structure that maps to Success Library principles for eventual integration

### Reference Documents

- `docs/success_library_project_context.md` - Full Success Library / SuperFact architecture
- `docs/05_EXECUTIVE_BRIEFING.md` - Executive summary of Success Library
- `code/VVD_Vintage_Framework_Design.md` - VVD-specific design document

---

## Directory Structure

```
vintage_framework/
├── config/
│   ├── __init__.py
│   ├── base_config.py              # Universal standards (aggregation, test groups)
│   ├── paths.py                    # Data source paths
│   └── campaigns/
│       ├── __init__.py             # Campaign registry
│       └── vvd.py                  # VVD campaign configurations
│
├── core/
│   ├── __init__.py
│   ├── experiment_metadata_loader.py  # [WIP] Layer 1 integration
│   ├── tactic_loader.py            # Load population data
│   ├── success_loader.py           # Load success data
│   ├── success_detector.py         # Join tactic ↔ success
│   ├── vintage_calculator.py       # Calculate vintage curves
│   └── plotter.py                  # Generate visualizations
│
├── runners/
│   ├── __init__.py
│   └── run_vintage.py              # Main entry point
│
├── diagnostics/
│   ├── diagnose_tactic_data.py     # Investigate tactic table
│   └── diagnose_success_tables.py  # Investigate success tables
│
├── outputs/
│   ├── data/                       # CSV/Parquet outputs
│   └── plots/                      # PNG visualizations
│
└── README.md                       # This file
```

---

## Quick Start

### In Jupyter Notebook

```python
from pyspark.sql import SparkSession
from vintage_framework.runners import run_vintage_analysis, run_all_campaigns

# Create Spark session
spark = SparkSession.builder.appName("Vintage Analysis").getOrCreate()

# Run single campaign
results = run_vintage_analysis(spark, "VCN")

# Run all VVD campaigns
all_results = run_all_campaigns(spark, "VVD")
```

### Outputs

Each campaign run produces:
- `{MNE}_vintage_full.csv` - Full vintage data (all days, all cohorts)
- `{MNE}_vintage_summary.csv` - Summary table (final rates per cohort)
- `{MNE}_vintage_all_cohorts.png` - Main vintage curve plot
- `{MNE}_vintage_grid.png` - Grid view (one subplot per cohort)
- `{MNE}_lift_over_time.png` - Lift with confidence intervals
- `{MNE}_summary_bars.png` - Bar chart of final rates

---

## Universal Standards

These rules apply to ALL campaigns (defined in `config/base_config.py`):

| Rule | Standard | Rationale |
|------|----------|-----------|
| Aggregation Level | MONTH (yyyy-MM) | Keeps plots readable |
| Years | 2025, 2026 | Focus on recent data |
| Test Group | TST_GRP_CD = 'TG4' | All others = Control |
| Measurement Window | TREATMT_END_DT - TREATMT_STRT_DT | Dynamic per deployment |
| Confidence Level | 95% | Statistical standard |

---

## VVD Campaigns

Six campaigns configured in `config/campaigns/vvd.py`:

| MNE | Campaign | Success Type | Success Field |
|-----|----------|--------------|---------------|
| VCN | Contextual Notification | ACQUISITION | ISS_DT |
| VDA | Black Friday Cyber Monday | ACQUISITION | ISS_DT |
| VDT | Activation Trigger | ACTIVATION | ACTV_DT |
| VUI | Usage Trigger | USAGE | TXN_DT |
| VUT | Tokenization Usage | TOKENIZATION | TXN_DT |
| VAW | Add To Wallet | TOKENIZATION | TXN_DT |

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. LOAD TACTIC                                              │
│     - Source: tactic.parquet                                │
│     - Filter by MNE, years                                  │
│     - Add: WINDOW_DAYS, GROUP, COHORT                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. [WIP] DISCOVER CAMPAIGN STRUCTURE                        │
│     - Optional step                                         │
│     - Investigate segments (RPT_GRP_CD)                     │
│     - Understand test group design                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. LOAD SUCCESS DATA                                        │
│     - Source varies by success type:                        │
│       - ACQUISITION/ACTIVATION: DDWTA_VISA_DR_CRD          │
│       - USAGE: DDWTA_T_PT_OF_SALE_TXN                       │
│       - TOKENIZATION: token.parquet (pre-pulled from EDW)  │
│     - Apply filters per config                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. DETECT SUCCESS                                           │
│     - Left join tactic to success on CLNT_NO                │
│     - Filter: SUCCESS_DT within measurement window          │
│     - Calculate: DAYS_TO_FIRST_SUCCESS                      │
│     - Aggregate to client-deployment level                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. BUILD VINTAGE CURVES                                     │
│     - Aggregate by COHORT, GROUP, DAY                       │
│     - Calculate cumulative success rate                     │
│     - Calculate lift (Test - Control)                       │
│     - Calculate confidence intervals                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  6. GENERATE OUTPUTS                                         │
│     - Plots: vintage curves, lift, summary                  │
│     - Data: CSV files for further analysis                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Adding a New Product

1. Create a new config file: `config/campaigns/{product}.py`
2. Follow the pattern in `vvd.py`
3. Register in `config/campaigns/__init__.py`
4. Run with: `run_vintage_analysis(spark, "MNE", product="PRODUCT")`

Example structure for a new campaign:

```python
CAMPAIGN_CONFIG = {
    "NEW_MNE": {
        "mne": "NEW_MNE",
        "product": "NEW_PRODUCT",
        "campaign_name": "Campaign Description",
        "success_type": "ACQUISITION",  # or ACTIVATION, USAGE, etc.
        "success_source": "HIVE",       # or "EDW"
        "success_table_path": "/path/to/table",
        "success_date_field": "SUCCESS_DT",
        "filters": {
            "FIELD": {"operator": "eq", "value": "value"}
        },
        "deployment_type": "trigger",   # or "batch"
        "metric_id": "PRODUCT_ACQ_001"  # Success Library reference
    }
}
```

---

## Diagnostics

Before running analysis on new data, use diagnostic scripts:

```python
# Investigate tactic data
from vintage_framework.diagnostics.diagnose_tactic_data import run_tactic_diagnostics
results = run_tactic_diagnostics(spark)

# Investigate success tables
from vintage_framework.diagnostics.diagnose_success_tables import run_success_diagnostics
results = run_success_diagnostics(spark)

# Check specific campaign segments
from vintage_framework.diagnostics.diagnose_tactic_data import investigate_segment_codes
segment_df = investigate_segment_codes(spark, mne="VCN")
```

---

## Work In Progress

### Experiment Metadata Loader (`core/experiment_metadata_loader.py`)

This module is a **placeholder** for future integration with:
- Layer 1: Governed Experiment Metadata (ODS table)
- Layer 2: Campaign Metadata (Mnemonic Mapping V2)

Current functionality:
- Discover campaign structure from tactic data
- Identify segments (RPT_GRP_CD)
- Validate experiment design

Future functionality:
- Pull segment descriptions from governed metadata
- Parse JSON experiment configuration from ODS
- Auto-configure vintage analysis based on campaign tags

---

## Success Library Integration

This framework aligns with the Success Library (SuperFact) architecture:

| Layer | Status | Integration Point |
|-------|--------|-------------------|
| Layer 1: Experiment Metadata | Not built | `experiment_metadata_loader.py` |
| Layer 2: Campaign Metadata | Not built | Campaign configs reference `metric_id` |
| Layer 3: Success Library | **This framework** | Calculation logic |
| Layer 4: Client Journey | Not built | Outputs feed dashboards |

The `metric_id` field in campaign configs (e.g., `VVD_ACQ_001`) maps to the Success Library metric catalog, enabling future automated integration.

---

## Troubleshooting

### No tactic records found
- Check MNE spelling matches exactly
- Verify years in `base_config.py` match data availability
- Run `diagnose_tactic_data.py` to explore

### No success records after join
- Check CLNT_NO format matches between tactic and success tables
- Verify success table filters aren't too restrictive
- Run `validate_join_keys()` in diagnostics

### Empty vintage curves
- Check that measurement windows have passed
- Verify success dates fall within treatment windows
- Look for data quality issues in success detection summary

---

## Version History

| Date | Changes |
|------|---------|
| 2026-01-19 | Initial framework creation |

---

## Contact

Marketing Analytics Team
