# Vintage Automation Engine - Layer View (Zoomed Out)

A high-level view of the code organized by SuperFact Layer. Shows which code blocks, functions, and variables belong to each layer.

---

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SUPERFACT 4-LAYER VIEW                                   │
│                                vintage_all_in_one.py                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗ │
│  ║  LAYER 1: EXPERIMENT METADATA                                                      ║ │
│  ║  "Who is in the test?"                                                             ║ │
│  ║                                                                                    ║ │
│  ║  Code:     load_tactic()                                                           ║ │
│  ║  Config:   YEARS_TO_INCLUDE, TEST_GROUP_CODE                                       ║ │
│  ║  Path:     PATHS["tactic_base_path"]                                               ║ │
│  ║  Source:   tactic_evnt_hist (parquet)                                              ║ │
│  ║  Swap:     → Experiment Metadata table                                             ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝ │
│                                         │                                               │
│                                         ▼                                               │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗ │
│  ║  LAYER 2: CAMPAIGN METADATA                                                        ║ │
│  ║  "What to measure?"                                                                ║ │
│  ║                                                                                    ║ │
│  ║  Code:     get_campaign_config()                                                   ║ │
│  ║  Config:   CAMPAIGN_METADATA dict                                                  ║ │
│  ║  Fields:   campaign_name, success_type, primary_metric, channel                    ║ │
│  ║  Source:   Hardcoded                                                               ║ │
│  ║  Swap:     → Mnemonic Mapping v2 query                                             ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝ │
│                                         │                                               │
│                                         ▼                                               │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗ │
│  ║  LAYER 3: SUCCESS DEFINITIONS                                                      ║ │
│  ║  "How to calculate?"                                                               ║ │
│  ║                                                                                    ║ │
│  ║  Code:     get_success_definition()                                                ║ │
│  ║  Config:   SUCCESS_DEFINITIONS dict                                                ║ │
│  ║  Fields:   table_path, date_field, filters, add_card_type                          ║ │
│  ║  Source:   Hardcoded                                                               ║ │
│  ║  Swap:     → Success Library (GitHub %Run OR curated data set)                     ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝ │
│                                         │                                               │
│                                         ▼                                               │
│  ╔═══════════════════════════════════════════════════════════════════════════════════╗ │
│  ║  LAYER 4: CLIENT JOURNEY                                                           ║ │
│  ║  "What did they actually do?"                                                      ║ │
│  ║                                                                                    ║ │
│  ║  Code:     load_fulfillment(), load_email_engagement(), load_success_outcome()     ║ │
│  ║  Config:   PATHS["visa_dr_crd"], PATHS["pos_txn"], EDW queries                     ║ │
│  ║  Fields:   EMAIL_SENT/OPENED/CLICKED/UNSUBSCRIBED, SUCCESS_FLAG                    ║ │
│  ║  Source:   Multiple (HIVE parquet + EDW Teradata)                                  ║ │
│  ║  Swap:     → Unified Client Journey semantic layer                                 ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════════════╝ │
│                                         │                                               │
│                                         ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│  │  VINTAGE ENGINE (Layer-agnostic - does NOT change)                                 │ │
│  │                                                                                    │ │
│  │  detect_success() → build_vintage_data() → prepare_vintage_table()                 │ │
│  │  calculate_ci() → generate_summary() → generate_engagement_summary()               │ │
│  │  plot_vintage() → plot_grid()                                                      │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
│                                         │                                               │
│                                         ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│  │  OUTPUT                                                                            │ │
│  │  vintage_df, summary_df, engagement_summary_df → Dashboard / CSV / HDFS            │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## LAYER 1: Experiment Metadata

**Question:** "Who is in the test?"

### Code Blocks in This Layer

| Item | Type | Location |
|------|------|----------|
| `load_tactic()` | Function | Lines 223-280 |
| `YEARS_TO_INCLUDE` | Config | Line 35 |
| `TEST_GROUP_CODE` | Config | Line 36 |
| `PATHS["tactic_base_path"]` | Path | Line 45 |

### Variables & What They Control

```
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1 VARIABLES                                                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  YEARS_TO_INCLUDE = [2025, 2026]                                           │
│  ├── Controls: Which partition years to read                               │
│  ├── Today: Hardcoded list                                                 │
│  └── Future: Dynamic from Experiment Metadata "active between dates"       │
│                                                                            │
│  TEST_GROUP_CODE = "TG4"                                                   │
│  ├── Controls: Which TST_GRP_CD means "Test" (vs Control)                  │
│  ├── Today: Hardcoded - assumes all campaigns use TG4                      │
│  └── Future: Query per-experiment from Experiment Metadata table           │
│                                                                            │
│  PATHS["tactic_base_path"] = "/prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/"
│  ├── Controls: Where to read tactic data from                              │
│  ├── Today: Static HIVE path                                               │
│  └── Future: Could point to semantic layer or remain static                │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
tactic_evnt_hist (parquet)
         │
         ▼
    load_tactic()
         │
         ├── Extract MNE from TACTIC_ID[8:10]
         ├── Clean CLNT_NO (trim, remove leading zeros)
         ├── Assign GROUP based on TEST_GROUP_CODE
         ├── Create COHORT (year-month)
         │
         ▼
    tactic_df (Spark DataFrame)
         │
         Fields: CLNT_NO, TACTIC_ID, TREATMT_STRT_DT, TREATMT_END_DT,
                 TST_GRP_CD, RPT_GRP_CD, GROUP, COHORT, WINDOW_DAYS
```

### Swap Point Summary

| Today | Future | Trigger |
|-------|--------|---------|
| Hardcoded years [2025, 2026] | Query "active between dates" | Experiment Metadata table built |
| Hardcoded TEST_GROUP_CODE = "TG4" | Query test group definition per experiment | Experiment Metadata has test group field |
| Static HIVE path | Same or semantic layer | Optional - path may remain static |

---

## LAYER 2: Campaign Metadata

**Question:** "What to measure?"

### Code Blocks in This Layer

| Item | Type | Location |
|------|------|----------|
| `CAMPAIGN_METADATA` | Dict | Lines 73-110 |
| `get_campaign_config()` | Function | Lines 185-187 |
| `ALL_MNES` | List | Line 183 |

### Variables & What They Control

```
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2 VARIABLES                                                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  CAMPAIGN_METADATA = {                                                     │
│      "VCN": {                                                              │
│          "campaign_name": "VVD Contextual Notification",                   │
│          "success_type": "ACQUISITION",                                    │
│          "primary_metric": "card_acquisition",  ← Links to Layer 3        │
│          "channel": "EMAIL",                                               │
│      },                                                                    │
│      "VDA": {...}, "VDT": {...}, "VUI": {...}, "VUT": {...}, "VAW": {...} │
│  }                                                                         │
│                                                                            │
│  Each field:                                                               │
│  ├── campaign_name   → Today: Hardcoded | Future: Mnemonic Mapping v2     │
│  ├── success_type    → Today: Hardcoded | Future: Measurement Category    │
│  ├── primary_metric  → Today: Hardcoded | Future: Primary Metric field    │
│  └── channel         → Today: Hardcoded | Future: New field in MM v2      │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
CAMPAIGN_METADATA (hardcoded dict)
         │
         ▼
  get_campaign_config(mne)
         │
         ├── Returns: campaign_name, success_type, primary_metric, channel
         │
         ▼
  primary_metric value → used to lookup Layer 3
```

### Swap Point Summary

| Today | Future | Trigger |
|-------|--------|---------|
| `CAMPAIGN_METADATA["VCN"]["primary_metric"]` | `SELECT primary_metric FROM mnemonic_mapping_v2 WHERE mne = 'VCN'` | Primary/Secondary metric fields added to MM v2 |
| 6 campaigns hardcoded | Query all measurable campaigns | MM v2 has measurement flag |

### Current Campaigns Configured

| MNE | Campaign Name | Success Type | Primary Metric |
|-----|---------------|--------------|----------------|
| VCN | Contextual Notification | ACQUISITION | card_acquisition |
| VDA | Black Friday Cyber Monday | ACQUISITION | card_acquisition |
| VDT | Activation Trigger | ACTIVATION | card_activation |
| VUI | Usage Trigger | USAGE | card_usage |
| VUT | Tokenization Usage | TOKENIZATION | wallet_provisioning |
| VAW | Add To Wallet | TOKENIZATION | wallet_provisioning |

---

## LAYER 3: Success Definitions

**Question:** "How to calculate?"

### Code Blocks in This Layer

| Item | Type | Location |
|------|------|----------|
| `SUCCESS_DEFINITIONS` | Dict | Lines 124-177 |
| `get_success_definition()` | Function | Lines 189-191 |
| Filter logic in `load_success_outcome()` | Code | Lines 487-510 |

### Variables & What They Control

```
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3 VARIABLES                                                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  SUCCESS_DEFINITIONS = {                                                   │
│      "card_acquisition": {                                                 │
│          "description": "Client acquired a new VVD card",                  │
│          "source": "HIVE",                                                 │
│          "table_path": PATHS["visa_dr_crd"],                               │
│          "date_field": "ISS_DT",                                           │
│          "client_field": "CLNT_NO",                                        │
│          "filters": {                                                      │
│              "STS_CD": ["06", "08"],                                       │
│              "SRVC_ID": 36,                                                │
│              "ISS_DT_NOT_NULL": True                                       │
│          },                                                                │
│          "add_card_type": True,                                            │
│      },                                                                    │
│      "card_activation": {...},                                             │
│      "card_usage": {...},                                                  │
│      "wallet_provisioning": {...}                                          │
│  }                                                                         │
│                                                                            │
│  Each field:                                                               │
│  ├── description  → Today: Hardcoded | Future: Success Library README     │
│  ├── source       → Today: Hardcoded | Future: Success Library metadata   │
│  ├── table_path   → Today: Hardcoded | Future: Success Library OR curated │
│  ├── date_field   → Today: Hardcoded | Future: In Success Library SQL     │
│  ├── filters      → Today: Hardcoded | Future: In Success Library SQL     │
│  └── add_card_type→ Today: Hardcoded | Future: In Success Library logic   │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
SUCCESS_DEFINITIONS (hardcoded dict)
         │
         ▼
  get_success_definition(metric_name)
         │
         ├── Returns: table_path, filters, date_field, etc.
         │
         ▼
  load_success_outcome() uses these to:
         │
         ├── Read from correct table
         ├── Apply all filters
         ├── Return filtered success records
```

### Filter Logic (Currently Inline)

```python
# This logic is currently in load_success_outcome()
# Will move to Success Library code files

if "STS_CD" in filters:
    df = df.filter(F.col("STS_CD").isin(filters["STS_CD"]))
if "SRVC_ID" in filters:
    df = df.filter(F.col("SRVC_ID") == filters["SRVC_ID"])
if "TXN_TYPES" in filters:
    # Complex transaction type filtering
if filters.get("ISS_DT_NOT_NULL"):
    df = df.filter(F.col("ISS_DT").isNotNull())
```

### Swap Point Summary

| Today | Future Option A | Future Option B |
|-------|-----------------|-----------------|
| `SUCCESS_DEFINITIONS["card_acquisition"]` | `%Run /success_library/card_acquisition.py` | `SELECT * FROM semantic.card_acquisition` |
| Inline filter logic | Logic in GitHub code file | Pre-filtered curated data set |

### Current Metrics Defined

| Metric | Source | Table | Key Filters |
|--------|--------|-------|-------------|
| card_acquisition | HIVE | VISA_DR_CRD | STS_CD in (06,08), SRVC_ID=36, ISS_DT not null |
| card_activation | HIVE | VISA_DR_CRD | STS_CD in (06,08), SRVC_ID=36, ACTV_DT |
| card_usage | HIVE | POS_TXN | SRVC_CD=36, specific TXN_TP/MSG_TP combos |
| wallet_provisioning | EDW | CLNT_CRD_POS_LOG + TOKEN_LIST | Token wallet indicator |

---

## LAYER 4: Client Journey

**Question:** "What did they actually do?"

### Code Blocks in This Layer

| Item | Type | Location |
|------|------|----------|
| `load_fulfillment()` | Function | Lines 291-339 |
| `load_email_engagement()` | Function | Lines 350-419 |
| `load_success_outcome()` | Function | Lines 463-516 |
| `load_token_from_edw()` | Function | Lines 430-460 |
| `enrich_with_engagement()` | Function | Lines 567-608 |
| `generate_engagement_summary()` | Function | Lines 723-753 |

### Variables & What They Control

```
┌────────────────────────────────────────────────────────────────────────────┐
│ LAYER 4 VARIABLES                                                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  FULFILLMENT (load_fulfillment)                                            │
│  ├── Concept: "Was the contact actually delivered?"                        │
│  ├── For EMAIL: Returns None - uses EMAIL_SENT as fulfillment indicator    │
│  ├── For other channels: Would need channel-specific fulfillment source    │
│  └── Future: Per-channel fulfillment tracking                              │
│                                                                            │
│  EMAIL ENGAGEMENT (load_email_engagement)                                  │
│  ├── Source: DTZV01.VENDOR_FEEDBACK_MASTER + VENDOR_FEEDBACK_EVENT (EDW)   │
│  ├── Output: EMAIL_SENT, EMAIL_OPENED, EMAIL_CLICKED, EMAIL_UNSUBSCRIBED,  │
│  │           EMAIL_BOUNCED (with corresponding _DT fields)                 │
│  ├── Disposition codes: 1=sent, 2=opened, 3=clicked, 4=unsub, 5=bounce     │
│  ├── Channel filter: Only for TACTIC_CELL_CD = 'EM' clients                │
│  ├── Note: EMAIL_SENT serves as fulfillment for email channel              │
│  ├── Today: Direct EDW query with pivot                                    │
│  └── Future: Engagement semantic layer                                     │
│                                                                            │
│  SUCCESS OUTCOME (load_success_outcome)                                    │
│  ├── Source: VISA_DR_CRD, POS_TXN (HIVE) or EDW for token                  │
│  ├── Output: SUCCESS_DT, SUCCESS_FLAG, DAYS_TO_SUCCESS                     │
│  ├── Today: Direct HIVE read + filters from Layer 3                        │
│  └── Future: Success Library curated data set                              │
│                                                                            │
│  PATHS for Layer 4:                                                        │
│  ├── PATHS["visa_dr_crd"] = "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/..."│
│  ├── PATHS["pos_txn"] = "/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/." │
│  ├── PATHS["token_source"] = "EDW"                                         │
│  ├── PATHS["email_source"] = "EDW"                                         │
│  └── PATHS["fulfillment_source"] = "EDW"                                   │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
                    ┌─────────────────────┐
                    │     Layer 4         │
                    │   Client Journey    │
                    └─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌───────────────────┐
│ Fulfillment   │   │ Email Engagement│   │ Success Outcome   │
│               │   │ (EM channel)    │   │                   │
│ EMAIL: uses   │   │ sent/opened/    │   │ Did they          │
│ EMAIL_SENT    │   │ clicked/unsub/  │   │ convert?          │
│ Other: TBD    │   │ bounced         │   │                   │
│               │   │ VENDOR_FEEDBACK │   │ VISA_DR_CRD       │
│               │   │ _MASTER/_EVENT  │   │ POS_TXN / EDW     │
└───────┬───────┘   └────────┬────────┘   └─────────┬─────────┘
        │                    │                      │
        └────────────────────┼──────────────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ enrich_with_engagement│
                 │                       │
                 │ Join all Layer 4 data │
                 │ to experiment records │
                 └───────────────────────┘
                             │
                             ▼
                    Enriched success_df
```

### Swap Point Summary

| Component | Today | Future | Trigger |
|-----------|-------|--------|---------|
| Fulfillment query | Direct EDW SQL | Client Journey layer | Layer built |
| Email engagement query | Direct EDW SQL + pivot | Engagement semantic layer | Layer built |
| Success outcome | HIVE read + inline filters | Curated success data set | Success Library ready |
| All paths | Static in PATHS dict | Dynamic from metadata | Semantic layers available |

---

## ENGINE (Layer-Agnostic)

**These functions do NOT change when data sources change.**

### Code Blocks

| Function | Purpose | Lines |
|----------|---------|-------|
| `detect_success()` | Join Layer 1 (experiment) with Layer 4 (outcome) | 522-564 |
| `build_vintage_data()` | Aggregate successes by cohort, group, day | 618-628 |
| `calculate_ci()` | Calculate lift and confidence interval | 631-639 |
| `prepare_vintage_table()` | Create cumulative curves, fill gaps | 642-709 |
| `generate_summary()` | Final day metrics per cohort | 712-720 |
| `generate_engagement_summary()` | Email/fulfillment funnel metrics | 723-753 |
| `plot_vintage()` | All cohorts on one chart | 759-791 |
| `plot_grid()` | One subplot per cohort | 794-837 |

### Why These Don't Change

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ENGINE STABILITY                                                           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  These functions only care about:                                          │
│  • CLNT_NO - client identifier                                             │
│  • GROUP - Test or Control                                                 │
│  • COHORT - when they entered experiment                                   │
│  • SUCCESS_FLAG - did they convert (0/1)                                   │
│  • DAYS_TO_SUCCESS - how long it took                                      │
│  • EMAIL_SENT/OPENED/CLICKED/UNSUBSCRIBED - engagement flags (optional)    │
│                                                                            │
│  They don't care WHERE this data comes from.                               │
│  Whether it's hardcoded config or dynamic queries,                         │
│  the engine receives the same DataFrame structure.                         │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary: Layer Ownership

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LAYER OWNERSHIP SUMMARY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1 - Experiment Metadata                                              │
│  ├── Config: YEARS_TO_INCLUDE, TEST_GROUP_CODE                              │
│  ├── Path: PATHS["tactic_base_path"]                                        │
│  ├── Function: load_tactic()                                                │
│  └── Swap to: Experiment Metadata table                                     │
│                                                                             │
│  LAYER 2 - Campaign Metadata                                                │
│  ├── Config: CAMPAIGN_METADATA dict (6 campaigns)                           │
│  ├── Fields: campaign_name, success_type, primary_metric, channel           │
│  ├── Function: get_campaign_config()                                        │
│  └── Swap to: Mnemonic Mapping v2                                           │
│                                                                             │
│  LAYER 3 - Success Definitions                                              │
│  ├── Config: SUCCESS_DEFINITIONS dict (4 metrics)                           │
│  ├── Fields: table_path, date_field, filters, source                        │
│  ├── Function: get_success_definition()                                     │
│  ├── Logic: Filter application in load_success_outcome()                    │
│  └── Swap to: Success Library (GitHub or curated data)                      │
│                                                                             │
│  LAYER 4 - Client Journey                                                   │
│  ├── Paths: visa_dr_crd, pos_txn, token_source, email_source, fulfillment   │
│  ├── Functions: load_fulfillment(), load_email_engagement(),                │
│  │              load_success_outcome(), load_token_from_edw()               │
│  ├── Enrichment: enrich_with_engagement()                                   │
│  └── Swap to: Unified Client Journey semantic layer                         │
│                                                                             │
│  ENGINE (No Layer - Stable)                                                 │
│  ├── Core: detect_success(), build_vintage_data(), prepare_vintage_table()  │
│  ├── Stats: calculate_ci()                                                  │
│  ├── Summary: generate_summary(), generate_engagement_summary()             │
│  └── Viz: plot_vintage(), plot_grid()                                       │
│                                                                             │
│  ORCHESTRATION (No Layer - Stable)                                          │
│  ├── run_vintage_analysis() - runs single campaign through all layers       │
│  ├── run_all_campaigns() - runs multiple campaigns                          │
│  └── export_to_csv(), export_to_hdfs_csv() - output functions               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Migration Path by Layer

### When Experiment Metadata Table is Ready (Layer 1)
```python
# Before
YEARS_TO_INCLUDE = [2025, 2026]
TEST_GROUP_CODE = "TG4"

# After
exp_meta = query_experiment_metadata(mne)
YEARS_TO_INCLUDE = exp_meta["active_years"]
TEST_GROUP_CODE = exp_meta["test_group_code"]
```

### When Mnemonic Mapping v2 Has Metrics (Layer 2)
```python
# Before
config = CAMPAIGN_METADATA["VCN"]

# After
config = query_mnemonic_mapping_v2("VCN")
# Returns: primary_metric, secondary_metric, campaign_name, etc.
```

### When Success Library is Ready (Layer 3)
```python
# Before
definition = SUCCESS_DEFINITIONS["card_acquisition"]
# Then apply filters manually in load_success_outcome()

# After - Option A (GitHub %Run)
%run /success_library/metrics/card_acquisition.py
success_df = get_card_acquisition(spark, client_list)

# After - Option B (Curated Data)
success_df = spark.read.parquet("/semantic/success/card_acquisition")
```

### When Client Journey Layer is Ready (Layer 4)
```python
# Before
fulfillment_df = load_fulfillment(spark, tactic_ids)  # Direct EDW
email_df = load_email_engagement(spark, treatment_ids)  # Direct EDW
success_df = load_success_outcome(spark, config)  # Direct HIVE

# After
journey_df = query_client_journey(client_list, start_date, end_date)
# Returns all touchpoints: email, fulfillment, conversion, etc.
```

---

## Quick Reference: What's Hardcoded Where

| Layer | Hardcoded Items | Count |
|-------|-----------------|-------|
| Layer 1 | YEARS_TO_INCLUDE, TEST_GROUP_CODE, tactic path | 3 |
| Layer 2 | CAMPAIGN_METADATA (6 campaigns × 4 fields) | 24 |
| Layer 3 | SUCCESS_DEFINITIONS (4 metrics × 6 fields) | 24 |
| Layer 4 | PATHS (5 paths), EDW queries (3) | 8 |
| **Total** | | **59 swappable items** |

When SuperFact layers mature, these 59 items become dynamic queries instead of hardcoded values.
