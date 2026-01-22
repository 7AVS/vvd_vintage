---
title: Vintage Automation Engine - Layer Architecture
author: Marketing Analytics
---

# Vintage Automation Engine

## The 4-Layer Architecture

---

# What Problem Are We Solving?

- We measure 6 VVD campaigns (VCN, VDA, VDT, VUI, VUT, VAW)
- Each campaign needs: experiment data, metrics config, success logic, client journey
- Today: All hardcoded in one Python file (59 items!)
- Future: Dynamic, swappable layers from semantic tables

---

# The SuperFact 4-Layer Model

| Layer | Question | Source Today | Source Future |
|-------|----------|--------------|---------------|
| Layer 1 | Who is in the test? | tactic_evnt_hist | Experiment Metadata table |
| Layer 2 | What to measure? | Hardcoded dict | Mnemonic Mapping v2 |
| Layer 3 | How to calculate? | Hardcoded dict | Success Library |
| Layer 4 | What did they do? | EDW + HIVE queries | Client Journey layer |

---

# Data Flow Overview

1. **Layer 1** loads experiment participants (Test vs Control)
2. **Layer 2** tells us which metric to measure for each campaign
3. **Layer 3** defines HOW to calculate that metric (filters, tables)
4. **Layer 4** gets the actual client behavior data
5. **Engine** combines everything and calculates lift

---

# Layer 1: Experiment Metadata

## "Who is in the test?"

---

# Layer 1: What It Does

- Reads from `tactic_evnt_hist` (parquet files)
- Identifies which clients are in Test vs Control groups
- Extracts campaign MNE from TACTIC_ID
- Creates COHORT based on treatment start date

---

# Layer 1: Key Components

| Component | Type | Description |
|-----------|------|-------------|
| `load_tactic()` | Function | Main loader for experiment data |
| `YEARS_TO_INCLUDE` | Config | Which years to read [2025, 2026] |
| `TEST_GROUP_CODE` | Config | Which code = Test group ("TG4") |
| `tactic_base_path` | Path | HIVE location of tactic data |

---

# Layer 1: Data Flow

**Input:** tactic_evnt_hist parquet files

**Processing:**
- Extract MNE from TACTIC_ID positions 8-10
- Clean CLNT_NO (trim, remove leading zeros)
- Assign GROUP based on TEST_GROUP_CODE
- Create COHORT (year-month format)

**Output:** tactic_df with CLNT_NO, GROUP, COHORT, WINDOW_DAYS

---

# Layer 1: Current vs Future

| Today (Hardcoded) | Future (Dynamic) |
|-------------------|------------------|
| `YEARS_TO_INCLUDE = [2025, 2026]` | Query "active between dates" from Experiment Metadata |
| `TEST_GROUP_CODE = "TG4"` | Query test group definition per experiment |
| Static HIVE path | Same path OR semantic layer |

---

# Layer 2: Campaign Metadata

## "What to measure?"

---

# Layer 2: What It Does

- Maps each campaign (MNE) to its configuration
- Defines which success metric to use
- Provides campaign name, channel, success type

---

# Layer 2: Key Components

| Component | Type | Description |
|-----------|------|-------------|
| `CAMPAIGN_METADATA` | Dict | 6 campaigns with 4 fields each |
| `get_campaign_config()` | Function | Lookup config by MNE |
| `ALL_MNES` | List | List of all campaign codes |

---

# Layer 2: Campaign Configuration

| MNE | Campaign Name | Success Type | Primary Metric |
|-----|---------------|--------------|----------------|
| VCN | Contextual Notification | ACQUISITION | card_acquisition |
| VDA | Black Friday Cyber Monday | ACQUISITION | card_acquisition |
| VDT | Activation Trigger | ACTIVATION | card_activation |
| VUI | Usage Trigger | USAGE | card_usage |
| VUT | Tokenization Usage | TOKENIZATION | wallet_provisioning |
| VAW | Add To Wallet | TOKENIZATION | wallet_provisioning |

---

# Layer 2: Data Flow

**Input:** MNE code (e.g., "VCN")

**Processing:**
- Lookup in CAMPAIGN_METADATA dictionary
- Return configuration object

**Output:** campaign_name, success_type, primary_metric, channel

**Key link:** `primary_metric` value is used to lookup Layer 3

---

# Layer 2: Current vs Future

| Today (Hardcoded) | Future (Dynamic) |
|-------------------|------------------|
| `CAMPAIGN_METADATA["VCN"]["primary_metric"]` | `SELECT primary_metric FROM mnemonic_mapping_v2 WHERE mne = 'VCN'` |
| 6 campaigns manually defined | Query all measurable campaigns with measurement flag |

---

# Layer 3: Success Definitions

## "How to calculate?"

---

# Layer 3: What It Does

- Defines the calculation logic for each metric
- Specifies which table to read
- Lists all filters to apply
- Configures date fields and special logic

---

# Layer 3: Key Components

| Component | Type | Description |
|-----------|------|-------------|
| `SUCCESS_DEFINITIONS` | Dict | 4 metrics with 6 fields each |
| `get_success_definition()` | Function | Lookup definition by metric name |
| Filter logic | Code | Applied in `load_success_outcome()` |

---

# Layer 3: Metrics Defined

| Metric | Source | Table | Key Filters |
|--------|--------|-------|-------------|
| card_acquisition | HIVE | VISA_DR_CRD | STS_CD in (06,08), SRVC_ID=36, ISS_DT not null |
| card_activation | HIVE | VISA_DR_CRD | STS_CD in (06,08), SRVC_ID=36, ACTV_DT |
| card_usage | HIVE | POS_TXN | SRVC_CD=36, specific TXN_TP/MSG_TP combos |
| wallet_provisioning | EDW | CLNT_CRD_POS_LOG + TOKEN_LIST | Token wallet indicator |

---

# Layer 3: Definition Structure

Each metric definition contains:

- **description**: What this metric measures
- **source**: HIVE or EDW
- **table_path**: Where to read data from
- **date_field**: Which field indicates success date
- **filters**: All conditions to apply
- **add_card_type**: Whether to include card type breakdown

---

# Layer 3: Filter Logic Example

**card_acquisition filters:**

1. `STS_CD` must be in ['06', '08'] (active statuses)
2. `SRVC_ID` must equal 36 (VVD service)
3. `ISS_DT` must not be null (card was issued)

These filters are currently inline in `load_success_outcome()` function.

---

# Layer 3: Current vs Future

| Today (Hardcoded) | Future Option A | Future Option B |
|-------------------|-----------------|-----------------|
| `SUCCESS_DEFINITIONS["card_acquisition"]` | `%Run /success_library/card_acquisition.py` | `SELECT * FROM semantic.card_acquisition` |
| Inline filter logic in Python | Logic in GitHub code file | Pre-filtered curated data set |

---

# Layer 4: Client Journey

## "What did they actually do?"

---

# Layer 4: What It Does

- Gets actual client behavior data
- Three main components:
  - **Fulfillment**: Was the contact delivered?
  - **Email Engagement**: Did they open/click?
  - **Success Outcome**: Did they convert?

---

# Layer 4: Key Components

| Component | Type | Description |
|-----------|------|-------------|
| `load_fulfillment()` | Function | Query fulfillment from EDW |
| `load_email_engagement()` | Function | Query email metrics from EDW |
| `load_success_outcome()` | Function | Load conversion data from HIVE/EDW |
| `load_token_from_edw()` | Function | Token-specific query |
| `enrich_with_engagement()` | Function | Join all journey data |

---

# Layer 4: Fulfillment

**Source:** DG6V01.TACTIC_EVNT_IP_AR_HIST (EDW/Teradata)

**Output fields:**
- FULFILLMENT_FLAG (was contact delivered?)
- FULFILLMENT_DT (when?)
- FULFILLMENT_AMT (any value associated?)

---

# Layer 4: Email Engagement

**Source:** DTZV01.VENDOR_FEEDBACK_MASTER + VENDOR_FEEDBACK_EVENT (EDW)

**Output fields:**
- EMAIL_SENT (disposition code 1)
- EMAIL_OPENED (disposition code 2)
- EMAIL_CLICKED (disposition code 3)
- EMAIL_BOUNCED (disposition code 5)

---

# Layer 4: Success Outcome

**Source:** VISA_DR_CRD, POS_TXN (HIVE) or EDW for token

**Output fields:**
- SUCCESS_DT (when did conversion happen?)
- SUCCESS_FLAG (0 or 1)
- DAYS_TO_SUCCESS (how long from treatment to conversion?)

---

# Layer 4: Data Flow

1. **load_fulfillment()** - Was contact delivered?
2. **load_email_engagement()** - Email sent/opened/clicked?
3. **load_success_outcome()** - Did they convert?
4. **enrich_with_engagement()** - Join all to experiment records

**Output:** Enriched success_df with full client journey

---

# Layer 4: Data Sources

| Data | Source System | Table/Path |
|------|---------------|------------|
| Fulfillment | EDW (Teradata) | TACTIC_EVNT_IP_AR_HIST |
| Email engagement | EDW (Teradata) | VENDOR_FEEDBACK_MASTER/_EVENT |
| Card acquisition/activation | HIVE | VISA_DR_CRD |
| Card usage | HIVE | POS_TXN |
| Token provisioning | EDW (Teradata) | CLNT_CRD_POS_LOG + TOKEN_LIST |

---

# Layer 4: Current vs Future

| Today | Future |
|-------|--------|
| Direct EDW query for fulfillment | Client Journey semantic layer |
| Direct EDW query + pivot for email | Engagement semantic layer |
| Direct HIVE read + filters for success | Success Library curated data set |
| Static paths in PATHS dict | Dynamic from metadata |

---

# The Engine

## Layer-Agnostic Processing

---

# Engine: What It Does

- Receives data from all 4 layers
- Performs vintage curve calculations
- Calculates lift and confidence intervals
- Generates summaries and visualizations

**Key point:** The engine does NOT change when data sources change.

---

# Engine: Core Functions

| Function | Purpose |
|----------|---------|
| `detect_success()` | Join experiment (L1) with outcome (L4) |
| `build_vintage_data()` | Aggregate by cohort, group, day |
| `calculate_ci()` | Calculate lift and confidence interval |
| `prepare_vintage_table()` | Create cumulative curves, fill gaps |

---

# Engine: Output Functions

| Function | Purpose |
|----------|---------|
| `generate_summary()` | Final day metrics per cohort |
| `generate_engagement_summary()` | Email/fulfillment funnel metrics |
| `plot_vintage()` | All cohorts on one chart |
| `plot_grid()` | One subplot per cohort |

---

# Engine: Why It's Stable

The engine only cares about these fields:

- **CLNT_NO** - client identifier
- **GROUP** - Test or Control
- **COHORT** - when they entered experiment
- **SUCCESS_FLAG** - did they convert (0/1)
- **DAYS_TO_SUCCESS** - how long it took
- **EMAIL_SENT/OPENED/CLICKED** - engagement flags (optional)
- **FULFILLMENT_FLAG** - was contact delivered (optional)

It doesn't care WHERE the data comes from.

---

# Orchestration

## Putting It All Together

---

# Orchestration Functions

| Function | Purpose |
|----------|---------|
| `run_vintage_analysis()` | Run single campaign through all layers |
| `run_all_campaigns()` | Run multiple campaigns |
| `export_to_csv()` | Export results to CSV |
| `export_to_hdfs_csv()` | Export to HDFS |

---

# Summary: What's Hardcoded Today

| Layer | What's Hardcoded | Count |
|-------|------------------|-------|
| Layer 1 | YEARS_TO_INCLUDE, TEST_GROUP_CODE, tactic path | 3 |
| Layer 2 | CAMPAIGN_METADATA (6 campaigns x 4 fields) | 24 |
| Layer 3 | SUCCESS_DEFINITIONS (4 metrics x 6 fields) | 24 |
| Layer 4 | PATHS (5 paths), EDW queries (3) | 8 |
| **Total** | | **59 items** |

---

# Migration Path

## When Each Layer Becomes Dynamic

---

# Migration: Layer 1

**When Experiment Metadata Table is Ready:**

Before:
- `YEARS_TO_INCLUDE = [2025, 2026]`
- `TEST_GROUP_CODE = "TG4"`

After:
- Query experiment metadata for active years
- Query test group code per experiment

---

# Migration: Layer 2

**When Mnemonic Mapping v2 Has Metrics:**

Before:
- `config = CAMPAIGN_METADATA["VCN"]`

After:
- `config = query_mnemonic_mapping_v2("VCN")`
- Returns: primary_metric, secondary_metric, campaign_name, etc.

---

# Migration: Layer 3

**When Success Library is Ready:**

Before:
- `definition = SUCCESS_DEFINITIONS["card_acquisition"]`
- Apply filters manually in load_success_outcome()

After (Option A - GitHub):
- `%run /success_library/metrics/card_acquisition.py`
- `success_df = get_card_acquisition(spark, client_list)`

After (Option B - Curated):
- `success_df = spark.read.parquet("/semantic/success/card_acquisition")`

---

# Migration: Layer 4

**When Client Journey Layer is Ready:**

Before:
- `fulfillment_df = load_fulfillment(spark, tactic_ids)` (Direct EDW)
- `email_df = load_email_engagement(spark, treatment_ids)` (Direct EDW)
- `success_df = load_success_outcome(spark, config)` (Direct HIVE)

After:
- `journey_df = query_client_journey(client_list, start_date, end_date)`
- Returns all touchpoints: email, fulfillment, conversion, etc.

---

# Key Takeaways

1. **4 layers** separate concerns: who, what, how, behavior
2. **59 hardcoded items** today will become dynamic queries
3. **Engine is stable** - doesn't change when sources change
4. **Migration is incremental** - swap one layer at a time
5. **SuperFact alignment** - each layer maps to a semantic table

---

# Questions?

## Next Steps

- Prioritize which layer to migrate first
- Validate Mnemonic Mapping v2 has required fields
- Confirm Success Library structure
- Plan Client Journey semantic layer

---

# Appendix: Layer Ownership Quick Reference

---

# Layer 1 Ownership

**Config:** YEARS_TO_INCLUDE, TEST_GROUP_CODE

**Path:** PATHS["tactic_base_path"]

**Function:** load_tactic()

**Swap to:** Experiment Metadata table

---

# Layer 2 Ownership

**Config:** CAMPAIGN_METADATA dict (6 campaigns)

**Fields:** campaign_name, success_type, primary_metric, channel

**Function:** get_campaign_config()

**Swap to:** Mnemonic Mapping v2

---

# Layer 3 Ownership

**Config:** SUCCESS_DEFINITIONS dict (4 metrics)

**Fields:** table_path, date_field, filters, source

**Functions:** get_success_definition(), filter logic in load_success_outcome()

**Swap to:** Success Library (GitHub or curated data)

---

# Layer 4 Ownership

**Paths:** visa_dr_crd, pos_txn, token_source, email_source, fulfillment

**Functions:** load_fulfillment(), load_email_engagement(), load_success_outcome(), load_token_from_edw()

**Enrichment:** enrich_with_engagement()

**Swap to:** Unified Client Journey semantic layer

---

# Engine Ownership (Stable)

**Core:** detect_success(), build_vintage_data(), prepare_vintage_table()

**Stats:** calculate_ci()

**Summary:** generate_summary(), generate_engagement_summary()

**Viz:** plot_vintage(), plot_grid()

**Does NOT change when data sources change.**
