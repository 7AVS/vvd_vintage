# Vintage Automation Engine - Code Block Documentation

This document explains each code block in `vintage_all_in_one.py`, what items exist today (hardcoded), and what they will be replaced with when SuperFact layers mature.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        vintage_all_in_one.py                                 │
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   Layer 1   │   │   Layer 2   │   │   Layer 3   │   │   Layer 4   │     │
│  │ Experiment  │   │  Campaign   │   │   Success   │   │   Client    │     │
│  │  Metadata   │   │  Metadata   │   │ Definitions │   │   Journey   │     │
│  │             │   │             │   │             │   │             │     │
│  │ SWAP: Query │   │ SWAP: Query │   │ SWAP: %Run  │   │ SWAP: Query │     │
│  │ Experiment  │   │ Mnemonic    │   │ from GitHub │   │ Unified     │     │
│  │ Metadata    │   │ Mapping v2  │   │ OR curated  │   │ Journey     │     │
│  │ table       │   │             │   │ data        │   │ table       │     │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘     │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                    │                                        │
│                                    ▼                                        │
│                    ┌───────────────────────────────┐                       │
│                    │      VINTAGE ENGINE           │                       │
│                    │      (Layer-agnostic)         │                       │
│                    │  • build_vintage_data()       │                       │
│                    │  • calculate_ci()             │                       │
│                    │  • prepare_vintage_table()    │                       │
│                    │  • generate_summary()         │                       │
│                    │                               │                       │
│                    │  This block does NOT change   │                       │
│                    │  when data sources change     │                       │
│                    └───────────────────────────────┘                       │
│                                    │                                        │
│                                    ▼                                        │
│                         ┌─────────────────┐                                │
│                         │     OUTPUT      │                                │
│                         │  vintage_df     │                                │
│                         │  summary_df     │                                │
│                         │  engagement_df  │                                │
│                         └─────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Block 1: CONFIGURATION (Lines 31-38)

**Purpose:** Global settings for the analysis.

**What exists TODAY:**
```python
YEARS_TO_INCLUDE = [2025, 2026]      # Which years to pull data from
TEST_GROUP_CODE = "TG4"               # Which TST_GRP_CD indicates Test group
CONFIDENCE_LEVEL = 0.95               # For statistical calculations
```

**What will be REPLACED:**

| Item | Today | Future |
|------|-------|--------|
| `YEARS_TO_INCLUDE` | Hardcoded list | Dynamic based on campaign active dates (from Experiment Metadata table) |
| `TEST_GROUP_CODE` | Hardcoded "TG4" | Query from Experiment Metadata table - different campaigns may use different test group codes |
| `CONFIDENCE_LEVEL` | Hardcoded 0.95 | Stays as config (this is calculation logic, not data) |

---

## Block 2: PATHS (Lines 40-60)

**Purpose:** Data source locations for all layers.

**What exists TODAY:**
```python
PATHS = {
    # Layer 1: Experiment Metadata
    "tactic_base_path": "/prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/",

    # Layer 4: Success Outcome Sources
    "visa_dr_crd": "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/...",
    "pos_txn": "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/...",

    # Layer 4: EDW Sources
    "token_source": "EDW",
    "email_source": "EDW",
    "fulfillment_source": "EDW",
}
```

**What will be REPLACED:**

| Path | Today | Future |
|------|-------|--------|
| `tactic_base_path` | Static HIVE path | Could remain static OR point to Experiment Metadata semantic layer |
| `visa_dr_crd` | Static HIVE path | Query from Success Library - different metrics may use different tables |
| `pos_txn` | Static HIVE path | Query from Success Library |
| EDW sources | Direct EDW queries | Could move to unified Client Journey semantic layer |

---

## Block 3: LAYER 2 - CAMPAIGN_METADATA (Lines 62-110)

**Purpose:** Defines WHAT to measure for each campaign. Maps campaign MNE to success metric type.

**What exists TODAY:**
```python
CAMPAIGN_METADATA = {
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",  # Links to Layer 3
        # Channel is NOT here - comes from TACTIC_CELL_CD in tactic data
    },
    "VDA": {...},
    "VDT": {...},
    "VUI": {...},
    "VUT": {...},
    "VAW": {...},
}
```

**Fields in each campaign:**

| Field | Description | Source Today | Source Future |
|-------|-------------|--------------|---------------|
| `campaign_name` | Human-readable name | Hardcoded | Mnemonic Mapping v2 - Description field |
| `success_type` | Category (ACQUISITION, USAGE, etc.) | Hardcoded | Mnemonic Mapping v2 - Measurement Category |
| `primary_metric` | Which metric to use | Hardcoded | Mnemonic Mapping v2 - Primary Metric field |

**Note:** Channel is NOT hardcoded in CAMPAIGN_METADATA. Channel comes from **TACTIC_CELL_CD** in the tactic data (EM = Email, IM = In-Market, etc.). A campaign can have multiple channels at the client level.

**SWAP POINT:**
```python
# TODAY:
config = CAMPAIGN_METADATA["VCN"]

# FUTURE:
query = "SELECT primary_metric, secondary_metric, description FROM mnemonic_mapping_v2 WHERE mne = 'VCN'"
config = query_result
```

---

## Block 4: LAYER 3 - SUCCESS_DEFINITIONS (Lines 112-177)

**Purpose:** Defines HOW to calculate each success metric. Contains source tables, filters, and logic.

**What exists TODAY:**
```python
SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "description": "Client acquired a new VVD card",
        "source": "HIVE",
        "table_path": PATHS["visa_dr_crd"],
        "date_field": "ISS_DT",
        "client_field": "CLNT_NO",
        "filters": {
            "STS_CD": ["06", "08"],    # Status codes for approved
            "SRVC_ID": 36,              # VVD service ID
            "ISS_DT_NOT_NULL": True
        },
        "add_card_type": True,
    },
    "card_activation": {...},
    "card_usage": {...},
    "wallet_provisioning": {...},
}
```

**Fields in each metric:**

| Field | Description | Source Today | Source Future |
|-------|-------------|--------------|---------------|
| `description` | What success means | Hardcoded | Success Library GitHub - README or docstring |
| `source` | Where data lives (HIVE/EDW) | Hardcoded | Success Library - documented in metadata |
| `table_path` | Full path to data | Hardcoded | Success Library - documented or curated data set path |
| `date_field` | Which column is success date | Hardcoded | Success Library - SQL/logic in code file |
| `filters` | All filter conditions | Hardcoded | Success Library - SQL/logic in code file |

**SWAP POINT:**
```python
# TODAY:
definition = SUCCESS_DEFINITIONS["card_acquisition"]
# Then manually apply filters in load_success_outcome()

# FUTURE (Option A - GitHub %Run):
%run /success_library/metrics/card_acquisition.py
# Code file contains all logic, returns filtered DataFrame

# FUTURE (Option B - Curated Data Set):
query = "SELECT * FROM semantic_layer.card_acquisition WHERE client_no = ..."
# Pre-calculated success table, just join
```

---

## Block 5: LAYER 1 - load_tactic() (Lines 213-280)

**Purpose:** Loads experiment data - identifies WHO is in test vs control.

**What the function does:**
1. Reads from tactic_evnt_hist partitions
2. Extracts MNE from TACTIC_ID
3. Formats CLNT_NO (trim, remove leading zeros)
4. Assigns GROUP (Test vs Control based on TST_GRP_CD)
5. Creates COHORT (year-month from treatment start date)

**Key transformations TODAY:**
```python
# MNE extraction - position 8-10 of TACTIC_ID
.withColumn("MNE", F.substring(F.col("TACTIC_ID"), 8, 3))

# Client number cleanup
.withColumn("CLNT_NO", F.regexp_replace(F.trim(F.col("TACTIC_EVNT_ID")), "^0+", ""))

# Test/Control assignment - HARDCODED
.withColumn("GROUP", F.when(F.col("TST_GRP_CD") == "TG4", "TEST").otherwise("CONTROL"))
```

**What will be REPLACED:**

| Item | Today | Future |
|------|-------|--------|
| Partition years | Hardcoded list | Query from Experiment Metadata - "active between dates" |
| Test group code | Hardcoded "TG4" | Query from Experiment Metadata - different experiments may have different test group definitions |
| MNE extraction | Fixed position | Could be enriched with Experiment Metadata - campaign name, hypothesis, etc. |

**Columns selected (for reference):**
- CLNT_NO, TACTIC_ID, TREATMT_STRT_DT, TREATMT_END_DT
- TST_GRP_CD, RPT_GRP_CD (segment), TREATMT_MN
- TACTIC_CELL_CD, STRTGY_SRC_CD
- ADDNL_DECISN_DATA1/2/3 (flexible fields - may contain channel)
- MNE, WINDOW_DAYS, GROUP, COHORT (derived)

---

## Block 6: LAYER 4 - load_fulfillment() (Lines 282-339)

**Purpose:** Verifies contact was actually delivered ("Was the planned treatment actually sent?").

**What the function does:**
1. Queries DG6V01.TACTIC_EVNT_IP_AR_HIST via EDW
2. Retrieves records that match tactic_id pattern
3. Returns FULFILLMENT_FLAG, FULFILLMENT_DT, FULFILLMENT_AMT

**Query TODAY:**
```sql
SELECT DISTINCT
    CAST(CLNT_NO AS VARCHAR(20)) AS CLNT_NO,
    1 AS FULFILLMENT_FLAG,
    ADDNL_DATA_DT AS FULFILLMENT_DT,
    AMT AS FULFILLMENT_AMT
FROM DG6V01.TACTIC_EVNT_IP_AR_HIST
WHERE tactic_id LIKE '{pattern}'
```

**What will be REPLACED:**

| Item | Today | Future |
|------|-------|--------|
| Source table | Direct EDW query | Unified Client Journey semantic layer |
| Query logic | Inline SQL | Could be standardized in Success Library |

---

## Block 7: LAYER 4 - load_email_engagement() (Lines 341-419)

**Purpose:** Tracks email engagement funnel (sent → opened → clicked).

**What the function does:**
1. Joins VENDOR_FEEDBACK_MASTER + VENDOR_FEEDBACK_EVENT
2. Pivots disposition codes into columns
3. Returns EMAIL_SENT, EMAIL_OPENED, EMAIL_CLICKED, EMAIL_BOUNCED flags

**Disposition codes:**
- 1 = email_sent
- 2 = email_opened
- 3 = email_clicked
- 4 = email_unsubscribed
- 5 = email_hardbounce

**What will be REPLACED:**

| Item | Today | Future |
|------|-------|--------|
| Source tables | Direct EDW query | Unified Client Journey - Engagement semantic layer |
| Disposition logic | Inline pivots | Standardized in Client Journey layer |

---

## Block 8: LAYER 4 - load_success_outcome() (Lines 421-516)

**Purpose:** Checks if client achieved the success metric (conversion).

**What the function does:**
1. Routes to correct data source (HIVE or EDW)
2. Applies all filters from SUCCESS_DEFINITIONS
3. Returns DataFrame with client, date, and optional card_type

**Filter application TODAY:**
```python
if "STS_CD" in filters:
    df = df.filter(F.col("STS_CD").isin(filters["STS_CD"]))
if "SRVC_ID" in filters:
    df = df.filter(F.col("SRVC_ID") == filters["SRVC_ID"])
# ... etc for each filter type
```

**What will be REPLACED:**

| Item | Today | Future |
|------|-------|--------|
| Filter logic | Inline if/else for each filter type | Success Library code file contains all logic |
| Source routing | Manual HIVE vs EDW check | Could have curated data set that abstracts source |
| Card type logic | Hardcoded brand code check | Success Library standardized definition |

---

## Block 9: detect_success() (Lines 518-564)

**Purpose:** Join experiment data (Layer 1) with success outcome (Layer 4).

**What the function does:**
1. Left join tactic to success on CLNT_NO
2. Filter success within treatment window (TREATMT_STRT_DT to TREATMT_END_DT)
3. Calculate DAYS_TO_SUCCESS
4. Aggregate to get SUCCESS_FLAG, FIRST_SUCCESS_DT, SUCCESS_COUNT

**This block is STABLE** - does not change when data sources change. It's the core join logic.

---

## Block 10: VINTAGE ENGINE (Lines 611-754)

**Purpose:** Core calculation engine - takes data from layers and produces vintage curves.

**Functions:**
- `build_vintage_data()` - Aggregates successes by cohort, group, day
- `calculate_ci()` - Calculates lift and confidence interval
- `prepare_vintage_table()` - Creates cumulative curves, fills gaps
- `generate_summary()` - Final day metrics per cohort
- `generate_engagement_summary()` - Email/fulfillment funnel metrics

**This entire block is STABLE** - it does not depend on where data comes from. When SuperFact layers mature, this engine stays exactly the same.

---

## Block 11: PLOTTING (Lines 756-837)

**Purpose:** Visualization of vintage curves.

**Functions:**
- `plot_vintage()` - All cohorts on one chart
- `plot_grid()` - One subplot per cohort

**This block is STABLE** - visualization logic doesn't change with data sources.

---

## Block 12: run_vintage_analysis() (Lines 839-967)

**Purpose:** Main orchestrator - runs through all 4 layers.

**Flow:**
```
1. Layer 2: get_campaign_config(mne) → what to measure
2. Layer 3: get_success_definition(metric) → how to calculate
3. Layer 1: load_tactic(spark, mne) → who is in test
4. Layer 4a: load_fulfillment() → was contact delivered
5. Layer 4b: load_email_engagement() → email funnel
6. Layer 4c: load_success_outcome() → did they convert
7. detect_success() → join experiment with outcome
8. enrich_with_engagement() → add email/fulfillment flags
9. Vintage Engine → calculate curves, lift, CI
10. Output → vintage_df, summary_df, engagement_summary_df
```

---

## Summary: What Changes vs What Stays

### WILL CHANGE (Swap Points)

| Block | Current | Future Source | Trigger |
|-------|---------|---------------|---------|
| CAMPAIGN_METADATA | Hardcoded dict | Mnemonic Mapping v2 | When Primary/Secondary metric fields added |
| SUCCESS_DEFINITIONS | Hardcoded dict | Success Library GitHub | When repo structure finalized |
| TEST_GROUP_CODE | Hardcoded "TG4" | Experiment Metadata table | When table built with test group definitions |
| YEARS_TO_INCLUDE | Hardcoded list | Experiment Metadata table | When "active between dates" field available |
| Fulfillment query | Direct EDW | Client Journey semantic layer | When layer built |
| Email engagement query | Direct EDW | Client Journey Engagement layer | When layer built |

### STAYS THE SAME

| Block | Why |
|-------|-----|
| Vintage Engine (build_vintage_data, calculate_ci, etc.) | Pure calculation logic - input-agnostic |
| detect_success() | Core join logic - works with any DataFrame |
| Plotting functions | Visualization only - works with output DataFrames |
| run_vintage_analysis() | Orchestration - just changes which functions it calls |

---

## Output Data Structures

### vintage_df (per campaign)
| Column | Description |
|--------|-------------|
| COHORT | Year-month of treatment start |
| DAY | Days from treatment (0, 1, 2, ...) |
| WINDOW_DAYS | Treatment window length |
| TEST_CLIENTS | Total test group size |
| TEST_SUCCESSES | Cumulative test successes |
| TEST_RATE | Cumulative test rate (%) |
| CTRL_CLIENTS | Total control group size |
| CTRL_SUCCESSES | Cumulative control successes |
| CTRL_RATE | Cumulative control rate (%) |
| ABS_LIFT | Absolute lift (percentage points) |
| CI_LOWER | 95% CI lower bound |
| CI_UPPER | 95% CI upper bound |
| SIGNIFICANT | True if CI doesn't cross zero |

### summary_df (per campaign)
Same as vintage_df but only final day of each cohort, plus MNE column.

### engagement_summary_df (per campaign)
| Column | Description |
|--------|-------------|
| MNE | Campaign code |
| TOTAL_CLIENTS | Total experiment population |
| EMAIL_SENT | Count sent |
| EMAIL_SENT_RATE | % sent |
| EMAIL_OPENED | Count opened |
| EMAIL_OPEN_RATE | % opened |
| EMAIL_CLICKED | Count clicked |
| EMAIL_CLICK_RATE | % clicked |
| FULFILLED | Count fulfilled |
| FULFILLMENT_RATE | % fulfilled |

---

## How to Add a New Campaign

1. Add entry to `CAMPAIGN_METADATA` (Layer 2)
2. If new success metric, add to `SUCCESS_DEFINITIONS` (Layer 3)
3. Run `run_vintage_analysis(spark, 'NEW_MNE')`

When Mnemonic Mapping v2 and Success Library are ready:
1. Campaign automatically pulled from Mnemonic Mapping v2
2. Success logic automatically pulled from Success Library
3. Just run the analysis

---

## How to Add a New Success Metric

1. Add entry to `SUCCESS_DEFINITIONS`:
```python
"new_metric": {
    "description": "What this metric measures",
    "source": "HIVE" or "EDW",
    "table_path": "/path/to/data",
    "date_field": "SUCCESS_DATE_COLUMN",
    "client_field": "CLNT_NO",
    "filters": {
        # Whatever filters define success
    },
}
```

2. If filters need special handling, update `load_success_outcome()` filter logic

When Success Library is ready:
1. Add code file to GitHub repo
2. Update Mnemonic Mapping v2 to point campaigns to new metric
3. Engine automatically picks it up
