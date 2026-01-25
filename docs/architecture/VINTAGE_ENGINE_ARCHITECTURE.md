# Vintage Engine: Complete Architecture

## Document Purpose

This is the **single source of truth** for the Vintage Engine architecture. It describes the vision, the 4-layer framework, the 3 maturity stages, and the path from current state to target state.

**Key principle:** This document describes the ARCHITECTURE and VISION, not a specific version. Engine versions (v2.3, v2.4, etc.) are iterations within the current stage. The architecture remains stable across versions.

---

## Quick Reference

| Concept | Summary |
|---------|---------|
| **What it does** | Calculates vintage curves (cumulative success rates over time) for marketing campaigns |
| **Current stage** | Stage 1 (Hardcoded) |
| **Campaigns** | 6 VVD campaigns (VCN, VDA, VDT, VUI, VUT, VAW) |
| **Metrics** | 4 success types (card_acquisition, card_activation, card_usage, wallet_provisioning) |
| **Architecture** | 4-layer model aligned to SuperFact pillars |

---

## The 3 Stages of Maturity

The stages describe WHERE data and configuration come from, not engine logic changes.

```
STAGE 1                STAGE 2                    STAGE 3
(Hardcoded)            (Libraries & Tables)       (Curated Data Sets)

    v                      v                          v
+---------+           +-------------+           +--------------+
| Python  |    --->   | MM v2 Table |    --->   | Pre-Curated  |
|  Dicts  |           | + Success   |           |  Data Sets   |
|         |           |   Library   |           |              |
+---------+           +-------------+           +--------------+

<- WE ARE HERE          Near-term                  Target State
  (all v2.x)
```

### Stage 1: Hardcoded (Current)

**All engine versions (v2.0, v2.1, v2.2, v2.3, ... v2.10) are Stage 1.**

| What | How It Works |
|------|--------------|
| Campaign metadata | `CAMPAIGN_METADATA` Python dict (6 campaigns) |
| Success definitions | `SUCCESS_DEFINITIONS` Python dict (4 metrics) |
| Paths and tables | `HIVE_PATHS`, `EDW_TABLES` dicts in code |
| Enrichment | Not available (placeholder only) |
| Reuse model | Copy-paste between projects |

**What we are doing:** Building the framework, iterating on logic, proving the model works.

### Stage 2: Libraries and Tables (Near-term)

**Trigger:** Mnemonic Mapping v2 and Success Library become operational.

| What | How It Works |
|------|--------------|
| Campaign metadata | Query from Mnemonic Mapping v2 table |
| Success definitions | Pull CODE from Success Library (GitHub `%Run`) |
| Enrichment | Code available but data sets not ready |
| User experience | Self-service begins for known metrics |

**What changes:** Hardcoded dicts become dynamic queries. Engine functions remain the same.

### Stage 3: Curated Data Sets (Target State)

**Trigger:** Data engineering builds curated semantic layers.

| What | How It Works |
|------|--------------|
| Success metrics | Pre-calculated curated data sets |
| Enrichment | Curated data sets (tenure, profitability, region, demographics) |
| Campaign config | From tables or curated layers |
| Execution | Minimal - data already processed |

**Key insight:** Stage 2 code becomes Stage 3 ETL. Work compounds.

---

## The 4-Layer Model

The engine is built on 4 semantic layers, aligned to the SuperFact framework.

```
+-----------------------------------------------------------------------------+
|                         SUPERFACT 4-LAYER VIEW                               |
+-----------------------------------------------------------------------------+
|                                                                             |
|  +=====================================================================+   |
|  ||  LAYER 1: EXPERIMENT METADATA                                      ||   |
|  ||  "Who is in the test?"                                             ||   |
|  ||                                                                    ||   |
|  ||  Source:   tactic_evnt_hist (parquet)                              ||   |
|  ||  Function: load_tactic()                                           ||   |
|  ||  Output:   client_id, segment, treatment, cohort, window_days      ||   |
|  ||  Swap:     -> Experiment Metadata table (Stage 2)                  ||   |
|  +=====================================================================+   |
|                                    |                                        |
|                                    v                                        |
|  +=====================================================================+   |
|  ||  LAYER 2: CAMPAIGN METADATA                         [UPGRADABLE]   ||   |
|  ||  "What to measure?"                                                ||   |
|  ||                                                                    ||   |
|  ||  Stage 1:  CAMPAIGN_METADATA dict                                  ||   |
|  ||  Stage 2+: Query from Mnemonic Mapping v2                          ||   |
|  ||  Output:   primary_metric, secondary_metric, action_type           ||   |
|  +=====================================================================+   |
|                                    |                                        |
|                                    v                                        |
|  +=====================================================================+   |
|  ||  LAYER 3: SUCCESS DEFINITIONS              [UPGRADABLE+SWAPPABLE]  ||   |
|  ||  "How to calculate?"                                               ||   |
|  ||                                                                    ||   |
|  ||  Stage 1:  SUCCESS_DEFINITIONS dict + inline filters               ||   |
|  ||  Stage 2:  Pull code from Success Library (GitHub %Run)            ||   |
|  ||  Stage 3:  Query pre-curated success data sets                     ||   |
|  ||  Output:   table_path, filters, calculation logic                  ||   |
|  +=====================================================================+   |
|                                    |                                        |
|                                    v                                        |
|  +=====================================================================+   |
|  ||  LAYER 4: CLIENT JOURNEY                                           ||   |
|  ||  "What did they actually do?"                                      ||   |
|  ||                                                                    ||   |
|  ||  Components:                                                       ||   |
|  ||  - Fulfillment: Was contact delivered?                             ||   |
|  ||  - Engagement: Email opens/clicks, mobile, banner                  ||   |
|  ||  - Outcome: Did they convert?                                      ||   |
|  ||                                                                    ||   |
|  ||  Functions: load_channel_engagement(), load_success_outcome()      ||   |
|  ||  Swap:     -> Unified Client Journey semantic layer (Stage 2/3)    ||   |
|  +=====================================================================+   |
|                                    |                                        |
|                                    v                                        |
|  +---------------------------------------------------------------------+   |
|  |  VINTAGE ENGINE (Layer-agnostic - does NOT change)                   |   |
|  |                                                                      |   |
|  |  detect_success() -> build_vintage_curves() -> output                |   |
|  |                                                                      |   |
|  |  These functions only care about standardized fields.                |   |
|  |  They don't know or care WHERE the data came from.                   |   |
|  +---------------------------------------------------------------------+   |
|                                    |                                        |
|                                    v                                        |
|  +---------------------------------------------------------------------+   |
|  |  OUTPUT                                                              |   |
|  |                                                                      |   |
|  |  vintage_curves -> Dashboard (Tableau or HTML)                       |   |
|  +---------------------------------------------------------------------+   |
|                                                                             |
+-----------------------------------------------------------------------------+
```

### SuperFact Pillar Alignment

| Pillar | Layer | Question |
|--------|-------|----------|
| Experiment Metadata | Layer 1 | "Who is in the test?" |
| Campaign Metadata (MM v2) | Layer 2 | "What to measure?" |
| Success Library (SoT) | Layer 3 | "How to calculate?" |
| Client Journey | Layer 4 | "What did they do?" |

---

## Layer Details

### Layer 1: Experiment Metadata

**Question:** "Who is in the test?"

| Attribute | Stage 1 (Current) | Stage 2+ |
|-----------|-------------------|----------|
| Data source | tactic_evnt_hist parquet | Same or Experiment Metadata table |
| Years to include | Hardcoded list `[2025, 2026]` | Query "active between dates" |
| Test group definition | Raw TST_GRP_CD codes | Query per-experiment |
| Segment definitions | RPT_GRP_CD raw codes | Segment lookup table |

**Output fields:** CLNT_NO, TACTIC_ID, TREATMT_STRT_DT, TREATMT_END_DT, TST_GRP_CD, RPT_GRP_CD, COHORT, WINDOW_DAYS

**Data flow:**
```
tactic_evnt_hist (parquet)
         |
         v
    load_tactic()
         |
         +-- Extract MNE from TACTIC_ID[8:10]
         +-- Clean CLNT_NO (trim, remove leading zeros)
         +-- Create COHORT (year-month)
         |
         v
    tactic_df
```

### Layer 2: Campaign Metadata

**Question:** "What to measure?"

| Attribute | Stage 1 (Current) | Stage 2+ |
|-----------|-------------------|----------|
| Campaign config | `CAMPAIGN_METADATA` dict | Query Mnemonic Mapping v2 |
| Primary metric | Hardcoded per MNE | `SELECT primary_metric FROM mm_v2` |
| Secondary metric | Hardcoded per MNE | `SELECT secondary_metric FROM mm_v2` |
| Campaign discovery | 6 campaigns listed | Query all with measurement flag |

**Current campaigns configured:**

| MNE | Campaign Name | Success Type | Primary Metric | Secondary Metric |
|-----|---------------|--------------|----------------|------------------|
| VCN | Contextual Notification | ACQUISITION | card_acquisition | - |
| VDA | Black Friday Cyber Monday | ACQUISITION | card_acquisition | - |
| VDT | Activation Trigger | ACTIVATION | card_activation | - |
| VUI | Usage Trigger | USAGE | card_usage | wallet_provisioning |
| VUT | Tokenization Usage | TOKENIZATION | wallet_provisioning | card_usage |
| VAW | Add To Wallet | TOKENIZATION | wallet_provisioning | card_usage |

**Data flow:**
```
CAMPAIGN_METADATA (dict)
         |
         v
  get_campaign_config(mne)
         |
         +-- Returns: campaign_name, success_type, primary_metric, secondary_metric
         |
         v
  primary_metric value -> used to lookup Layer 3
```

### Layer 3: Success Definitions

**Question:** "How to calculate?"

| Attribute | Stage 1 (Current) | Stage 2 | Stage 3 |
|-----------|-------------------|---------|---------|
| Definition source | `SUCCESS_DEFINITIONS` dict | GitHub %Run | Curated data set |
| Filter logic | Inline in Python | Code in library file | Pre-filtered data |
| Table paths | Hardcoded in dict | In library code | Curated table path |

**Current metrics defined:**

| Metric | Source | Table | Key Filters |
|--------|--------|-------|-------------|
| card_acquisition | HIVE | VISA_DR_CRD | STS_CD in (06,08), SRVC_ID=36, ISS_DT not null |
| card_activation | HIVE | VISA_DR_CRD | STS_CD in (06,08), SRVC_ID=36, ACTV_DT not null |
| card_usage | HIVE | POS_TXN | SRVC_CD=36, specific TXN_TP/MSG_TP combos |
| wallet_provisioning | EDW | CLNT_CRD_POS_LOG + TOKEN_LIST | Token wallet indicator |

**Data flow:**
```
SUCCESS_DEFINITIONS (dict)
         |
         v
  get_success_definition(metric_name)
         |
         +-- Returns: table_path, filters, date_field, source
         |
         v
  load_success_outcome() applies filters
         |
         v
  success_df with SUCCESS_FLAG, SUCCESS_DT
```

### Layer 4: Client Journey

**Question:** "What did they actually do?"

Three sub-components:

| Component | Purpose | Source | Output |
|-----------|---------|--------|--------|
| Fulfillment | Was contact delivered? | EDW (for email, EMAIL_SENT serves this role) | FULFILLMENT_FLAG |
| Engagement | Email opens, clicks, etc. | EDW VENDOR_FEEDBACK tables | EMAIL_SENT/OPENED/CLICKED with dates |
| Outcome | Did they convert? | HIVE or EDW per metric | SUCCESS_FLAG, DAYS_TO_SUCCESS |

**Data flow:**
```
                    +---------------------+
                    |     Layer 4         |
                    |   Client Journey    |
                    +---------------------+
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
+---------------+   +-----------------+   +-------------------+
| Fulfillment   |   | Email Engagement|   | Success Outcome   |
+-------+-------+   +--------+--------+   +---------+---------+
        |                    |                      |
        +--------------------+----------------------+
                             |
                             v
                 +-----------------------+
                 | enrich_with_engagement|
                 | Join all to experiment|
                 +-----------------------+
                             |
                             v
                    Enriched success_df
```

---

## The Engine (Layer-Agnostic)

The engine functions do NOT change when data sources change. They only care about standardized fields.

### Input Fields Expected

| Field | Type | Description |
|-------|------|-------------|
| CLNT_NO | String | Client identifier |
| TST_GRP_CD | String | Test group code (raw) |
| RPT_GRP_CD | String | Report group code (raw) |
| COHORT | String | Year-month when entered experiment |
| SUCCESS_FLAG | Int | 0 or 1 |
| DAYS_TO_SUCCESS | Int | Days from treatment to success |
| EMAIL_SENT/OPENED/CLICKED | Int | Engagement flags (optional) |

### Core Functions

| Function | Purpose |
|----------|---------|
| `detect_success()` | Join experiment (Layer 1) with outcome (Layer 4) |
| `build_vintage_curves()` | Calculate cumulative success rates by day |
| `build_engagement_curves()` | Calculate email engagement curves |
| `build_channel_breakdown()` | Summary by channel (not daily) |

### Why the Engine is Stable

```
+----------------------------------------------------------------------------+
| ENGINE STABILITY                                                           |
+----------------------------------------------------------------------------+
|                                                                            |
|  The engine receives standardized DataFrames from the 4 layers.            |
|  It doesn't know or care:                                                  |
|  - Whether data came from hardcoded dict or dynamic query                  |
|  - Whether filters were applied inline or in curated ETL                   |
|  - Whether it's Stage 1, 2, or 3                                           |
|                                                                            |
|  This separation is what makes upgrades possible without engine rewrites.  |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## Output Schema

The engine produces a standardized output format for dashboard consumption.

### Primary Output: vintage_curves

```
MNE | COHORT | TST_GRP_CD | RPT_GRP_CD | METRIC | DAY | WINDOW_DAYS | CLIENT_CNT | SUCCESS_CNT | RATE
```

| Column | Description |
|--------|-------------|
| MNE | Campaign mnemonic (VCN, VDA, etc.) |
| COHORT | Year-month of treatment start |
| TST_GRP_CD | Raw test group code (engine does NOT map to Test/Control) |
| RPT_GRP_CD | Raw report group code (cell-level detail) |
| METRIC | PRIMARY, SECONDARY, EMAIL_OPEN, EMAIL_CLICK |
| DAY | Days since treatment start (0, 1, 2, ... up to WINDOW_DAYS) |
| WINDOW_DAYS | Maximum measurement window for this cohort |
| CLIENT_CNT | Number of clients in this cell |
| SUCCESS_CNT | Cumulative successes by this day |
| RATE | SUCCESS_CNT / CLIENT_CNT as percentage |

### Secondary Output: channel_breakdown

```
MNE | COHORT | TST_GRP_CD | RPT_GRP_CD | CHANNEL | CLIENT_CNT | SUCCESS_CNT | RATE
```

### Design Decisions

- **Engine outputs raw codes** - No Test/Control mapping in engine
- **Dashboard handles comparisons** - Lift calculation, confidence intervals, visualization
- **METRIC column enables flexibility** - Primary, secondary, and engagement metrics in same structure

---

## Future Module: Enrichment

**Not available in Stage 1. Available in Stage 2+.**

| Attribute | Stage 1 | Stage 2 | Stage 3 |
|-----------|---------|---------|---------|
| Tenure | Not available | Pull code from library | Curated data set |
| Profitability | Not available | Pull code from library | Curated data set |
| Region | Not available | Pull code from library | Curated data set |
| Demographics | Not available | Pull code from library | Curated data set |

**Output impact:** Selected enrichments become additional SEGMENT dimensions in output.

---

## Swap Points Summary

These are the hardcoded items that become dynamic queries in Stage 2+:

| Layer | What's Hardcoded | Count |
|-------|------------------|-------|
| Layer 1 | YEARS_TO_INCLUDE, tactic path | 2 |
| Layer 2 | CAMPAIGN_METADATA (6 campaigns x 4 fields) | 24 |
| Layer 3 | SUCCESS_DEFINITIONS (4 metrics x 6 fields) | 24 |
| Layer 4 | HIVE_PATHS, EDW_TABLES, inline queries | 8 |
| **Total** | | **~58** |

### Migration Examples

**Layer 2 swap (when MM v2 ready):**
```python
# Before (Stage 1)
config = CAMPAIGN_METADATA["VCN"]

# After (Stage 2)
config = query_mnemonic_mapping_v2("VCN")
# Returns: primary_metric, secondary_metric, campaign_name, etc.
```

**Layer 3 swap (when Success Library ready):**
```python
# Before (Stage 1)
definition = SUCCESS_DEFINITIONS["card_acquisition"]
# Then apply filters manually in load_success_outcome()

# After - Option A (GitHub %Run)
%run /success_library/metrics/card_acquisition.py
success_df = get_card_acquisition(spark, client_list)

# After - Option B (Curated Data)
success_df = spark.read.parquet("/semantic/success/card_acquisition")
```

---

## The Virtuous Cycle

Every campaign onboarded enriches the metadata ecosystem.

```
+-----------------------------------------------------------------------------+
|                           THE VIRTUOUS CYCLE                                 |
+-----------------------------------------------------------------------------+
|                                                                             |
|   +--------------+                          +----------------------+        |
|   | New Campaign |                          |  Richer Metadata     |        |
|   |   Onboarded  | ---------------------->  |    Catalog           |        |
|   +--------------+                          +----------------------+        |
|          |                                           |                      |
|          |                                           |                      |
|          |    +--------------------------------------+                      |
|          |    |                                                             |
|          |    v                                                             |
|          |   +----------------------------------------+                     |
|          |   |  Success Library grows with:           |                     |
|          |   |  - New metric definitions              |                     |
|          |   |  - Documented business rules           |                     |
|          |   |  - Reusable calculation logic          |                     |
|          |   +----------------------------------------+                     |
|          |                                           |                      |
|          |                                           |                      |
|          v                                           v                      |
|   +----------------------+              +----------------------+            |
|   | Mnemonic Mapping v2  |              | Future Projects      |            |
|   | gets more campaigns  |              | can reuse all this   |            |
|   +----------------------+              +----------------------+            |
|                                                                             |
+-----------------------------------------------------------------------------+
```

### What Gets Captured With Each Campaign

| What We Capture | Where It Goes | Benefit |
|-----------------|---------------|---------|
| Campaign to metric mapping | Mnemonic Mapping v2 | Anyone can look up what VCN measures |
| Success metric definition | Success Library | Reusable across all projects |
| Filter logic (STS_CD, SRVC_ID) | Success Library code | No more tribal knowledge |
| Data source paths | Documented in Layer 4 | Clear data lineage |
| Test group definitions | Experiment Metadata | Standardized across experiments |

### The Compounding Effect

```
Campaign 1 (VCN):
  -> Defines card_acquisition metric
  -> Documents VISA_DR_CRD filters
  -> Establishes baseline architecture

Campaign 2 (VDA):
  -> Reuses card_acquisition (already defined!)
  -> Zero new metric work needed

Campaign 3 (VDT):
  -> Needs card_activation (new metric)
  -> Success Library grows by 1 metric
  -> Future activation campaigns benefit

Campaign 6 (VAW):
  -> Reuses wallet_provisioning from VUT
  -> Only config changes, no logic work
```

---

## Target State User Experience

When fully realized (Stage 2+):

```
USER PROVIDES:
  - Campaign names (VCN, VDA, VDT)
  - Date range (last 3 months, full year, append)
  - Enrichment (optional: tenure, region, profitability)

ENGINE AUTO-DETECTS:
  - Channels from campaign metadata -> pulls interaction code
  - Success metrics from campaign config -> pulls calculation code
  - Missing items -> prompts for semantic definition

ENGINE ADAPTS OUTPUT:
  - Curves per success metric
  - Segments per enrichment variable
  - Channel interaction stats
  - Dashboard-ready format
```

**No SQL. No code editing. No filter guessing.**

---

## Semantic Asset Catalog (Stage 2+)

The catalog that enables automation:

```
+------------------------------------------------------------------+
|  ASSET: card_acquisition                                          |
|                                                                   |
|  metric_id: SUC_001                                               |
|  standardized_name: card_acquisition                              |
|  business_description: "Client acquired a new VVD card"           |
|  owner: Marketing Analytics                                       |
|                                                                   |
|  STAGE 2:                                                         |
|    code_path: github.com/team/success-library/card_acquisition.py |
|                                                                   |
|  STAGE 3:                                                         |
|    table_path: /curated/success/card_acquisition                  |
|                                                                   |
|  output_schema: [client_id, success_date, success_flag]           |
|                                                                   |
+------------------------------------------------------------------+
```

**Multiple versions can exist:** If two teams have different definitions for `card_acquisition`, both live in the catalog. The campaign metadata specifies which version to use.

---

## Dashboard Delivery

The engine feeds two parallel dashboard tracks:

| Track | Platform | Status | Use Case |
|-------|----------|--------|----------|
| **Track A** | Tableau / CIDM | Pending alignment | Official enterprise location |
| **Track B** | SharePoint / HTML | Ready now | Self-sufficient, shareable |

Both tracks consume the same engine output. This ensures consistency regardless of delivery method.

---

## Color Scheme for Diagrams

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| From Data (stable) | Ocean Blue | #0091DA | Layer 1, Layer 4 borders |
| Upgradable | Warm Yellow | #FFC72C | Layer 2, Layer 3 borders |
| Optional/Future | Sunburst | #FCA311 | Enrichment module |
| Future State | Tundra | #07AFBF | Stage 2/3 indicators |
| Engine Core | Light Gray + Dark Blue | #F5F5F5, #003168 | Engine functions |
| Stable/Structural | Gray | #CCCCCC | Orchestration |

---

## What's Built vs. Planned

| Component | Stage 1 Status | Stage 2 Dependency | Stage 3 Dependency |
|-----------|----------------|--------------------|--------------------|
| Experiment Module | BUILT | Experiment Metadata table | Same |
| Campaign Module | BUILT (dict) | Mnemonic Mapping v2 | Curated config |
| Success Module | BUILT (dict) | Success Library | Curated data sets |
| Enrichment Module | PLACEHOLDER | Code library | Curated data sets |
| Journey Module | BUILT | Engagement semantic layer | Client Journey layer |
| Vintage Engine | BUILT | No change needed | No change needed |
| Dashboard output | BUILT | No change needed | No change needed |

---

## Naming Conventions

| Term | Definition |
|------|------------|
| **Stage** | Maturity level (1=hardcoded, 2=library, 3=curated) |
| **Layer** | Semantic component of the 4-layer model |
| **Module** | Code implementation of a layer |
| **Upgradable** | Module that evolves across stages |
| **Swappable** | Module where multiple implementations can exist |
| **Engine** | The layer-agnostic calculation logic |
| **Pillar** | SuperFact team-wide strategic initiative |

---

## Open Items

| Item | Status | Notes |
|------|--------|-------|
| Vintage Type 2 (monthly aggregation) | ON HOLD | Time series view - needs more thought |
| Measurement period in metadata | TO ADD | Should be in Campaign Metadata (90 days, end of treatment) |
| Enrichment catalog | TO BUILD | List of available enrichment variables |
| Secondary metric implementation | PARTIAL | Some campaigns have, some don't |

---

## Visual Resources

| Diagram | File | Best For |
|---------|------|----------|
| Detailed architecture | `ENGINE_ARCHITECTURE_DETAILED.drawio` | Technical deep-dive |
| Executive brief | `EXECUTIVE_BRIEF.drawio` | Leadership summary |
| Virtuous cycle | `VIRTUOUS_CYCLE.drawio` | Why this matters |
| Technical onboarding | `TECHNICAL_ONBOARDING.drawio` | New team members |

All diagrams in `docs/architecture/` folder. Open in Draw.io (diagrams.net).

---

## Document History

| Date | Change | By |
|------|--------|-----|
| 2026-01-22 | Created | - |
| 2026-01-25 | Consolidated from VINTAGE_ENGINE_ARCHITECTURE.md, LAYER_VIEW_DOCUMENTATION.md | Consultant |

**Archived sources:** `archive/docs/VINTAGE_ENGINE_ARCHITECTURE_OLD.md`, `archive/docs/LAYER_VIEW_DOCUMENTATION_OLD.md`

**Purpose:** Single source of truth for Vintage Engine architecture and vision

---

## Future Considerations

Items under evaluation for future implementation. These are operational enhancements that do not change the core 4-layer model or 3-stage maturity path.

### Near-Term: Operational Modes

#### Delta/Incremental Processing

**Current state:** Each engine run processes the entire campaign history (all cohorts).

**Future state:** Run only recent/active cohorts and append to existing output.

| Mode | Behavior | Use Case |
|------|----------|----------|
| Full refresh | Process all cohorts, overwrite output | Initial run, major logic changes |
| Delta/Incremental | Process only active cohorts, append to output | Regular updates, scheduled runs |

**Key consideration:** Cohort lifecycle - cohorts remain "active" until their measurement window closes. A cohort started 2 weeks ago still needs Day 14, 21, 28 data calculated on subsequent runs.

**Output implications:**
- Move from single CSV to partitioned storage (by cohort)
- Add metadata columns: `RUN_DATE`, `COHORT_STATUS`
- Dashboard must consume partitioned data

#### Scheduled Automation

**Current state:** Manual execution in Jupyter notebooks.

**Future state:** Unattended runs on schedule (weekly/monthly).

| Aspect | Interactive (Current) | Scheduled (Future) |
|--------|----------------------|-------------------|
| Trigger | Manual notebook execution | Scheduled job (Airflow, Oozie, etc.) |
| Spark context | Notebook-managed | Explicit creation |
| Credentials | User session | Service account |
| Output | Browser download | Direct to storage |
| Logging | Print statements | Structured logging |

**Key consideration:** Scheduling platform depends on existing infrastructure. Decision required: Airflow, Oozie, Databricks Jobs, or other.

### Longer-Term Considerations

| Item | Description | Dependency |
|------|-------------|------------|
| Multi-channel engagement | Mobile, ONB, ONO engagement tracking | Channel data source availability |
| Vintage Type 2 | Monthly aggregation view | Business requirements clarification |
| Real-time refresh | Near-real-time curve updates | Platform capability |

---

## Relationship to Stages

These operational modes are **orthogonal** to the 3-stage maturity model:

```
                    Stage 1         Stage 2         Stage 3
                   (Hardcoded)    (Libraries)     (Curated)

Full Refresh          ✓              ✓               ✓
Delta Processing      ✓              ✓               ✓
Scheduled             ✓              ✓               ✓
```

You can implement delta processing or scheduling at any stage. They are execution patterns, not architectural changes.

However, **scheduled automation becomes more valuable** as you move to Stage 2+, when multiple consumers depend on reliable, regular data updates.
