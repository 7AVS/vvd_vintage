# Vintage Engine: Module Catalog

> **Created:** 2026-01-28
> **Status:** Design — under review
> **Scope:** Architecture for scaling to 300+ campaigns
> **Companion docs:** `HANDSHAKE_CONTRACTS.md`, `EXECUTION_FLOW.md`

---

## Architecture Overview

The Vintage Engine is composed of **two layers** and **seven modules**.

The **Context Layer** assembles everything the engine needs to know before any calculation happens: who is in the test, what to measure, how to calculate success, and what clients did.

The **Analysis Layer** consumes the Context Layer output and produces vintage curves and delivery artifacts.

```
+============================================================================+
|                          CONTEXT LAYER                                      |
|  "Build the complete picture before calculating anything"                   |
|                                                                             |
|  M1 Experiment ──→ M2 Campaign ──→ M3 Success ──┐                          |
|       │                                          │                          |
|       └──────────→ M5 Journey ──────────────────┤                          |
|                                                  │                          |
|                                                  ▼                          |
|                                        Standardized Context                 |
+============================================================================+
                                                  │
                                                  ▼
+============================================================================+
|                          ANALYSIS LAYER                                     |
|  "Transform context into insight"                                           |
|                                                                             |
|  M6 Vintage Engine ──→ M7 Output                                           |
+============================================================================+
```

---

## Module Inventory

### Context Layer

| Module | Name | Question It Answers | Source (Stage 1) | Source (Stage 2+) |
|--------|------|--------------------|--------------------|-------------------|
| **M1** | Experiment Metadata | "Who is in the test?" | tactic_evnt_hist (parquet) | Experiment Metadata table |
| **M2** | Campaign Mapping | "What do we measure?" | CAMPAIGN_METADATA dict | Mnemonic Mapping v2 table |
| **M3** | Success Definition | "How do we calculate success?" | SUCCESS_DEFINITIONS dict | Success Library (GitHub / curated) |
| **M5** | Client Journey | "What did clients do?" | EDW feedback tables | Engagement semantic layer |

### Analysis Layer

| Module | Name | Question It Answers | Notes |
|--------|------|---------------------|-------|
| **M6** | Vintage Engine | "What are the curves?" | Layer-agnostic. Does not know data sources. |
| **M7** | Output | "How do we deliver results?" | CSV, data lake, Tableau, Airflow handoff |

### Future Modules

| Module | Name | Purpose | Dependency |
|--------|------|---------|------------|
| **M4** | Enrichment | Client attributes: tenure, age, demographics, profitability | Stage 2+ data availability |

> **M4 is deferred.** At 300-campaign scale, adding enrichment dimensions per campaign is not viable for MVP. The architecture accommodates it — M4 would feed into M6 alongside M3 and M5 — but it is not in the active pipeline.

---

## Module Details

### M1: Experiment Metadata

**Question:** "Who is in the test?"

**What it does:** Given a list of campaign mnemonics and a date range, loads all clients who participated in those experiments. This is the starting point for everything — every other module operates on clients identified here.

| Attribute | Description |
|-----------|-------------|
| **Input** | List of MNEs + date range |
| **Source** | tactic_evnt_hist (parquet on HDFS) |
| **Output** | Client list with treatment dates, test groups, cohorts |
| **Key fields** | CLNT_NO, TACTIC_ID, TREATMT_STRT_DT, TREATMT_END_DT, TST_GRP_CD, RPT_GRP_CD, COHORT, WINDOW_DAYS |
| **Current function** | `load_tactic()` |
| **Stage 2 swap** | Query from Experiment Metadata table |

**Why it matters:** M1 is the authoritative source of "who is in this campaign." Every downstream module uses M1's client list. No client exists in the pipeline that wasn't identified here.

---

### M2: Campaign Mapping

**Question:** "What do we measure for this campaign?"

**What it does:** Given a campaign mnemonic, returns the semantic definition: what is the primary success metric, what is the secondary, what type of success is it (acquisition, activation, usage, tokenization), and what the campaign is called.

| Attribute | Description |
|-----------|-------------|
| **Input** | MNE (campaign mnemonic) |
| **Source** | CAMPAIGN_METADATA dict (Stage 1) / Mnemonic Mapping v2 table (Stage 2+) |
| **Output** | Campaign config: metric names, success type, campaign name |
| **Key fields** | campaign_name, success_type, primary_metric, secondary_metric |
| **Current function** | `get_campaign_config()` |
| **Stage 2 swap** | `query_mnemonic_mapping_v2(mne)` |

**Why it matters:** M2 provides the semantic layer — it tells M3 *what* to calculate. Without M2, M3 doesn't know which success metric to look up. At 300 campaigns, this mapping is what enables self-service: configure the campaign once, the engine does the rest.

**Relationship to M3:** M2 feeds M3. M3 cannot execute without M2's output (it needs the metric names). They remain separate modules because they have different sources (campaign config vs. success definitions) and different upgrade paths (Mnemonic Mapping v2 vs. Success Library).

---

### M3: Success Definition

**Question:** "How do we calculate whether a client succeeded?"

**What it does:** Given a metric name (from M2), loads the complete definition of how to calculate success: which data source, what filters, what the output looks like. Then executes the definition to produce success outcome data.

| Attribute | Description |
|-----------|-------------|
| **Input** | Metric name (from M2) |
| **Source** | SUCCESS_DEFINITIONS dict (Stage 1) / Success Library (Stage 2) / Curated data set (Stage 3) |
| **Output** | Success outcome DataFrame: which clients succeeded and when |
| **Key fields** | CLNT_NO, SUCCESS_DT |
| **Current functions** | `get_success_definition()`, `get_full_config()`, `apply_success_filters()`, `load_success_outcome()` |
| **Stage 2 swap** | `%run /success_library/metrics/{metric_name}.py` |
| **Stage 3 swap** | `spark.read.parquet("/curated/success/{metric_name}")` |

**Why it matters:** This is the most complex module. Each success metric is a complete data asset — source routing (Hive vs EDW), filters, joins, client key resolution, and output contract. At 300 campaigns, many will share the same success metrics (e.g., card_acquisition). The Success Library ensures each metric is defined once, reused everywhere.

**Output contract:** Every metric, regardless of source, must produce a DataFrame with at minimum: `CLNT_NO` (client identifier) and `SUCCESS_DT` (date of success event). This contract is **enforced at runtime**.

---

### M5: Client Journey

**Question:** "What did clients do in response to the campaign?"

**What it does:** Loads engagement and fulfillment data — did the client receive the email? Open it? Click? Unsubscribe? Future: mobile engagement, push notifications.

| Attribute | Description |
|-----------|-------------|
| **Input** | Tactic IDs (from M1), channels detected in M1 data |
| **Source** | EDW feedback tables (Stage 1) / Engagement semantic layer (Stage 2+) |
| **Output** | Engagement DataFrame: flags and dates for each engagement event |
| **Key fields** | CLNT_NO, EMAIL_SENT, EMAIL_OPENED, EMAIL_CLICKED, EMAIL_UNSUBSCRIBED + date fields |
| **Current functions** | `load_channel_engagement()`, `_load_email_engagement()` |
| **Stage 2 swap** | Query from Engagement semantic layer |

**Why it matters:** Engagement metrics (EMAIL_SENT, EMAIL_OPEN, EMAIL_CLICK, EMAIL_UNSUB) are produced as vintage curves alongside success metrics. They answer "did the channel work?" vs. M3's "did the client convert?"

**Dependency:** M5 depends on M1 only (needs tactic IDs and treatment dates). It does NOT depend on M3 — engagement data is loaded independently of success definitions. This means M5 runs in parallel with the M2→M3 chain.

---

### M6: Vintage Engine

**Question:** "What are the cumulative success curves?"

**What it does:** Joins experiment data (M1) with success outcomes (M3) and engagement data (M5). Detects which clients succeeded within their treatment window. Builds cumulative vintage curves by day, grouped by cohort, test group, and report group.

| Attribute | Description |
|-----------|-------------|
| **Input** | tactic_df (M1), success_df (M3), engagement_df (M5), config (M2+M3) |
| **Source** | Context Layer outputs — M6 does not access any data sources directly |
| **Output** | Vintage curves DataFrame + channel breakdown DataFrame |
| **Key fields** | MNE, COHORT, TST_GRP_CD, RPT_GRP_CD, METRIC, DAY, WINDOW_DAYS, CLIENT_CNT, SUCCESS_CNT, RATE |
| **Current functions** | `detect_success()`, `build_vintage_curves()`, `build_engagement_curves()`, `build_channel_breakdown()`, `run_vintage_analysis()` |

**Why it matters:** M6 is layer-agnostic. It does not know or care whether data came from hardcoded dicts, a success library, or curated datasets. It receives standardized DataFrames and produces curves. This is why M6 does not change across stages.

**Design principle:** M6 should never import, reference, or know about SUCCESS_DEFINITIONS, CAMPAIGN_METADATA, HIVE_PATHS, or EDW_TABLES. It consumes only what the Context Layer gives it through the handshake contracts.

---

### M7: Output

**Question:** "How do we deliver results to consumers?"

**What it does:** Takes vintage curves and channel breakdown from M6 and delivers them to the appropriate destination: CSV download, HDFS storage, data lake, Tableau, Airflow pipeline.

| Attribute | Description |
|-----------|-------------|
| **Input** | Results dict from M6 (vintage_curves DataFrame, channel_breakdown DataFrame) |
| **Source** | M6 output — no external data sources |
| **Output** | Delivered artifacts (CSV files, HDFS parquet, database tables) |
| **Current functions** | `download_csv()`, `download_results()` |
| **Stage 2+ additions** | HDFS write, Tableau extract, Airflow trigger |

**Why it matters:** At 300 campaigns, manual CSV download is not viable. M7 evolves from browser downloads to automated pipeline delivery. The engine output schema stays the same — only the delivery mechanism changes.

---

## Module Numbering

M4 (Enrichment) is intentionally skipped in the active pipeline. The numbering is preserved so that future documentation, code, and conversations remain consistent when M4 is eventually activated.

| Number | Module | Status |
|--------|--------|--------|
| M1 | Experiment Metadata | Active |
| M2 | Campaign Mapping | Active |
| M3 | Success Definition | Active |
| M4 | Enrichment | Future (Stage 2+) |
| M5 | Client Journey | Active |
| M6 | Vintage Engine | Active |
| M7 | Output | Active |

---

## Relationship to Existing Architecture

This module catalog **supersedes** the 4-layer model in `VINTAGE_ENGINE_ARCHITECTURE.md` for module-level design decisions. The architecture doc remains the source of truth for the 3-stage maturity model and the strategic vision.

| Old Concept | New Concept | What Changed |
|-------------|-------------|--------------|
| Layer 1 | M1: Experiment Metadata | Same scope, now a named module |
| Layer 2 | M2: Campaign Mapping | Same scope, clearer name |
| Layer 3 | M3: Success Definition | Same scope, with output contract enforcement |
| Layer 4 | M5: Client Journey | Scoped to engagement only (success outcome moved to M3) |
| Engine | M6: Vintage Engine | Same scope, formally separated from Context Layer |
| Export functions | M7: Output | Elevated to formal module for 300-campaign delivery |
| Enrichment (placeholder) | M4: Enrichment (Future) | Deferred — not in MVP pipeline |
| (none) | Context Layer / Analysis Layer | New grouping concept |

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-28 | Created from architecture redesign session |
