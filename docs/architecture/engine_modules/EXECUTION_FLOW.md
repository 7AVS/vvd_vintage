# Execution Flow: Module Pipeline

> **Created:** 2026-01-28
> **Status:** Design — under review
> **Purpose:** Visual reference for module execution order and data flow
> **Companion docs:** `MODULE_CATALOG.md`, `HANDSHAKE_CONTRACTS.md`

---

## DAG Overview

The Context Layer is a **DAG (Directed Acyclic Graph)**, not a pure sequential pipeline. M1 is the root. Two parallel branches fan out from M1 and converge at M6.

```
                    ┌─────────────────────────────┐
                    │         USER INPUT           │
                    │  MNEs + Date Range           │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
              ┌────────────────────────────────────────┐
              │  M1: EXPERIMENT METADATA               │
              │  "Who is in the test?"                 │
              │                                        │
              │  Input:  MNEs, date range              │
              │  Source: tactic_evnt_hist (parquet)     │
              │  Output: tactic_df (client list)       │
              │          + tactic_ids (list)            │
              │                                        │
              │  Contract C1: validated at exit         │
              └──────────┬─────────────┬───────────────┘
                         │             │
              ┌──────────┘             └──────────────┐
              │ C1 (MNE + config)        C4 (tactic   │
              │                           IDs + dates) │
              ▼                                        ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│  M2: CAMPAIGN MAPPING    │        │  M5: CLIENT JOURNEY      │
│  "What do we measure?"   │        │  "What did clients do?"  │
│                          │        │                          │
│  Input:  MNE             │        │  Input:  tactic_ids      │
│  Source: CAMPAIGN_META-  │        │  Source: EDW feedback     │
│          DATA dict       │        │          tables           │
│  Output: campaign config │        │  Output: engagement_df   │
│          (dict)          │        │                          │
│                          │        │  Contract C5: validated  │
│  Contract C2: validated  │        │  at exit                 │
└────────────┬─────────────┘        └────────────┬─────────────┘
             │                                    │
             │ C2 (metric names)                  │
             ▼                                    │
┌──────────────────────────┐                      │
│  M3: SUCCESS DEFINITION  │                      │
│  "How do we calculate?"  │                      │
│                          │                      │
│  Input:  metric_name     │                      │
│  Source: SUCCESS_DEFS    │                      │
│          dict (Stage 1)  │                      │
│  Output: success_df +    │                      │
│          flat config     │                      │
│                          │                      │
│  Contract C3: validated  │                      │
│  at exit (CLNT_NO +      │                      │
│  SUCCESS_DT enforced)    │                      │
└────────────┬─────────────┘                      │
             │                                    │
             │ C3 (success_df + config)           │ C5 (engagement_df)
             │                                    │
             └────────────────┬───────────────────┘
                              │
                              ▼
              ┌────────────────────────────────────────┐
              │  M6: VINTAGE ENGINE                    │
              │  "What are the curves?"                │
              │                                        │
              │  Receives SEPARATE inputs:             │
              │  - tactic_df     (from M1)             │
              │  - success_df    (from M3)             │
              │  - config        (from M2+M3)          │
              │  - engagement_df (from M5, or None)    │
              │                                        │
              │  Internal joins:                       │
              │  1. detect_success(M1 + M3)            │
              │  2. enrich_with_engagement(+ M5)       │
              │  3. build_vintage_curves()             │
              │  4. build_engagement_curves()          │
              │  5. build_channel_breakdown()          │
              │                                        │
              │  Output: results dict                  │
              │  Contract C7: validated at exit         │
              └──────────────────┬─────────────────────┘
                                 │
                                 │ C7 (vintage_curves + channel_breakdown)
                                 ▼
              ┌────────────────────────────────────────┐
              │  M7: OUTPUT                            │
              │  "How do we deliver?"                  │
              │                                        │
              │  Stage 1: CSV download (browser)       │
              │  Stage 2: HDFS write + dashboard feed  │
              │  Stage 3: Data lake + Airflow trigger  │
              └────────────────────────────────────────┘
```

---

## Logical Independence (Not Parallelism)

The DAG has one fork point and one join point:

```
        M1
       / \
      /   \
M2→M3     M5      ← These two branches are LOGICALLY INDEPENDENT
      \   /
       \ /
        M6
        |
        M7
```

**Left branch (M2 → M3):** Resolves campaign metadata and loads success outcome data. Sequential — M3 needs M2's metric names.

**Right branch (M5):** Loads engagement data from EDW. Independent — only needs M1's tactic IDs.

### What "logically independent" means

The DAG describes **data dependencies**, not execution parallelism. In the current Jupyter + PySpark environment, Python executes line by line — M5 and M2→M3 run sequentially. M5 specifically uses an EDW cursor (blocking call), not lazy Spark operations.

| What the DAG tells you | What it does NOT mean |
|------------------------|----------------------|
| M5 does not need M3's output | They run at the same time |
| You can change M3 without breaking M5 | There is a performance gain today |
| If M3 breaks, M5 still works | Python magically parallelizes |

### Why this matters despite sequential execution

1. **Architecture clarity:** When someone asks "does engagement depend on success definitions?" the DAG answers: no.
2. **Future execution model:** If this moves to Airflow or Databricks Jobs (300-campaign scale), each branch becomes a separate task that CAN run in parallel. The DAG is the blueprint.
3. **Debugging:** A failure in M3 does not affect M5. Fault isolation follows the DAG.
4. **Testing:** M5 can be tested independently of M3. No mock required for success definitions when testing engagement.

### Current execution order (sequential)

```
M1 → M5 → M2 → M3 → M6 → M7
```

The code currently runs M5 (engagement) before M2→M3 (success). This is an implementation detail, not an architectural requirement. The order could be reversed without affecting results.

---

## Per-MNE Execution

For a single campaign (`run_vintage_analysis(spark, mne)`):

```
Step 1: M1
  load_tactic(spark, mne)
  → tactic_df (persisted)
  → extract tactic_ids

Step 2: M2 + M5 (can be parallel)
  M2: get_campaign_config(mne)
      → campaign config dict
  M5: load_channel_engagement(spark, email_tactic_ids, "EMAIL")
      → engagement_df (or None)

Step 3: M3 (needs M2)
  get_full_config(mne, "PRIMARY")
  load_success_outcome(spark, primary_config)
  → success_df + flat config

Step 4: M6 (needs M1 + M3 + M5)
  detect_success(tactic_df, success_df, config)
  enrich_with_engagement(success_df, engagement_df)
  build_vintage_curves(enriched_df, mne, "PRIMARY")
  → primary_curves

Step 5: SECONDARY (repeat Steps 3-4 if secondary_metric exists)
  get_full_config(mne, "SECONDARY")
  load_success_outcome(spark, secondary_config)
  detect_success(tactic_df, secondary_success_df, secondary_config)
  build_vintage_curves(secondary_df, mne, "SECONDARY")
  → secondary_curves

Step 6: Engagement curves (part of M6)
  build_engagement_curves(enriched_df, mne, email_channel_df)
  → engagement_curves

Step 7: M7
  Combine all curves
  download_results(results)
```

---

## Multi-Campaign Execution

For all campaigns (`run_all_campaigns(spark)`):

```
for each MNE in campaign list:
    run_vintage_analysis(spark, mne)
    → collect results

Combine all results into _combined_curves and _combined_channel
```

**Current:** Sequential loop. Each campaign runs the full M1→M6 pipeline.

**Future optimization (300 campaigns):** M1 could load all campaigns at once (one parquet read with multiple MNE filters), then fan out per-MNE for M2→M6. This reduces I/O from 300 parquet reads to 1.

---

## Decision Points

```
                     M1
                      │
           ┌──── Has email channel? ────┐
           │ YES                   NO   │
           ▼                            │
          M5                            │
           │                            │
           ▼                            ▼
     engagement_df               engagement_df = None
           │                            │
           └──────────┬─────────────────┘
                      ▼
                     M6
                      │
           ┌── Has secondary metric? ──┐
           │ YES                  NO   │
           ▼                           │
     Run M3+M6 again                   │
     for SECONDARY                     │
           │                           │
           └──────────┬────────────────┘
                      ▼
                     M7
```

| Decision Point | Condition | Path A | Path B |
|---------------|-----------|--------|--------|
| Email engagement | `TACTIC_CELL_CD` contains "EM" | Load M5, enrich in M6 | Skip M5, no engagement curves |
| Secondary metric | `campaign.secondary_metric` is not None | Run M3+M6 again for SECONDARY | Skip secondary curves |
| EDW vs Hive | `config.success_source` | M3 uses EDW cursor | M3 uses Spark parquet |

---

## Contract Validation Points

Validation runs at these exact points in the pipeline:

```
M1 ──[VALIDATE C1]──→ M2 ──[VALIDATE C2]──→ M3 ──[VALIDATE C3]──→
                                                                    ├──→ M6 ──[VALIDATE C7]──→ M7
M1 ──[VALIDATE C4]──→ M5 ──[VALIDATE C5]──→ ─────────────────────┘
```

| Point | What is validated | Failure message example |
|-------|-------------------|------------------------|
| After M1 | Experiment DataFrame has required columns | `"C1: CLNT_NO column missing from experiment data for MNE='VCN'"` |
| After M2 | Campaign config has valid metric names | `"C2: primary_metric 'card_xyz' not found in SUCCESS_DEFINITIONS"` |
| After M3 | Success DataFrame has CLNT_NO + SUCCESS_DT | `"C3: SUCCESS_DT column missing from success output for metric 'card_acquisition'"` |
| After M5 | Engagement DataFrame has required flag columns | `"C5: EMAIL_SENT column missing from engagement data"` |
| After M6 | Curves have all required output columns | `"C7: RATE column missing from vintage curves output"` |

---

## Data Volume Estimates (300-Campaign Scale)

| Module | Current (6 campaigns) | Projected (300 campaigns) | Bottleneck |
|--------|----------------------|---------------------------|------------|
| M1 | ~500K rows | ~25M rows | Parquet read (HDFS I/O) |
| M2 | 6 dict lookups | 300 dict/table lookups | Negligible |
| M3 | 6-12 success loads | 300-600 success loads | Hive parquet reads + EDW queries |
| M5 | 6 EDW queries | 300 EDW queries | EDW connection pool |
| M6 | 6 curve builds | 300 curve builds | Pandas cumulative loop |
| M7 | 1 CSV export | Partitioned write or DB insert | Write I/O |

**Critical path at scale:** M3 (300+ success data loads) and M5 (300+ EDW engagement queries). M1 optimization (single read, multi-MNE filter) is the highest-impact performance change.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-28 | Created from architecture redesign session |
