# Module Design Decisions

> **Created:** 2026-01-28
> **Status:** In Discussion — design phase, no code changes yet
> **Context:** Session discussion about making Layers 2 and 3 truly modular
> **Diagram:** `docs/architecture/MODULE_DESIGN_COMPARISON.drawio` (2 pages: Current vs Target)

---

## Problem Statement

The architecture documentation describes Layers 2 (Campaign Metadata) and 3 (Success Definitions) as "modular" and "upgradable." However, the code implementation does not match:

1. **Layer 3 logic is scattered** — the `SUCCESS_DEFINITIONS` dict (lines 152-210) defines *what* to filter, but `load_success_outcome()` (lines 419-454) in Layer 4 contains the *how* (filter interpretation logic).
2. **`wallet_provisioning` bypasses the framework** — `load_token_from_edw()` has hardcoded SQL that ignores `SUCCESS_DEFINITIONS` entirely. The definition says `filters: None` but the SQL has extensive filter logic.
3. **`get_full_config()` couples Layers 2 and 3** — directly accesses both dicts instead of using accessor functions.
4. **No client scoping** — success queries load entire tables (all clients in the source) and narrow via join. Should only query clients participating in the specific campaign.

---

## Design Decisions Made

### Decision 1: Success Metric = Complete Data Asset

The success metric is not just a dict of filter values. It is a **complete data asset package** containing everything needed to answer "did this client succeed?"

| Component | Description | Example (wallet_provisioning) |
|-----------|-------------|-------------------------------|
| Source paths | Where the data lives | `pos_log`, `token_list` |
| Joins | How tables connect | `TOKN_REQSTR_ID = TOKEN_ID` |
| Filters/constraints | Business rules | `AMT1=0`, `SRVC_CD=36`, `TOKEN_WALLET_IND='Y'` |
| Client key resolution | How to extract CLNT_NO | `SUBSTR(CLNT_CRD_NO, 7, 9)` |
| Date field | Success event date | `TXN_DT` |
| Entry point contract | What goes in, what comes out | Input: client list → Output: CLNT_NO + SUCCESS_DT |

**Rationale:** When this asset is eventually submitted to the Success Library, the whole package goes — not pieces scattered across the codebase.

### Decision 2: Hybrid Asset Model (Catalog + Execution)

Each success definition contains:
- **Cataloged metadata** (human-readable: description, tables, business rules, owner)
- **Execution artifact** (for the engine: filter config for Hive, SQL query for EDW)
- **Output contract** (enforced: always returns CLNT_NO + SUCCESS_DT)

**Why hybrid:** EDW SQL queries have SUBSTR expressions, CAST operations, and multi-table JOINs that don't decompose into simple key-value filters. Building a SQL generation DSL for 6 campaigns is over-engineering. Instead: catalog the semantics, keep the execution artifact in its native form (PySpark filters for Hive, SQL for EDW).

### Decision 3: Source Routing (HIVE / EDW / DUAL)

Each asset declares its source environment:
- `"source": "HIVE"` → engine uses Spark to read parquet + apply PySpark filters
- `"source": "EDW"` → engine uses Teradata cursor + executes cataloged SQL
- `"source": "DUAL"` → asset has both configs, engine picks based on preference/availability

The **connection infrastructure** (SparkSession, EDW cursor) already exists and stays as-is. The module just routes to the right protocol.

**Key principle:** If the asset has no EDW config, the EDW path does not activate. If it has no Hive config, the Hive path does not activate.

### Decision 4: Client-Scoped Queries (NOT Full Table Scans)

**Current state:** Success queries load entire source tables, then `detect_success()` joins to narrow to campaign clients.

**Target state:** Module 3 receives the client list from Module 1 and only queries clients participating in that specific campaign.

**Why this matters:**
- Performance: no reason to scan millions of records for a few thousand campaign clients
- Multi-campaign: when running 7 campaigns with 7 different success metrics from 7 different sources, each should only pull its own clients
- Correctness: client list comes from Module 1 (tactic_evnt_hist), which is the authoritative source of "who is in this campaign"

**Implementation consideration:** For EDW queries, client lists may be large (thousands of IDs). Need to handle this carefully — possibly temp tables or batched IN clauses for Teradata.

### Decision 5: Filter Logic Belongs With Definitions (Layer 3)

The filter interpretation code (`if "STS_CD"`, `if "TXN_TYPES"`, etc.) moves from `load_success_outcome()` (Layer 4) into a new function `apply_success_filters()` that lives next to `SUCCESS_DEFINITIONS` (Layer 3).

Layer 4 becomes pure I/O: load raw data, delegate filtering to Layer 3.

### Decision 6: Proper Cataloging is Required

This is NOT over-cataloging. The full asset definition — tables, joins, filters, business rules, output contract, source routing — is the **spec for the future curated pipeline** (Stage 3).

```
Stage 1 (now):     Asset definition in code → engine runs logic live
Stage 2 (library): Asset definition in Success Library → engine pulls and runs
Stage 3 (curated): Asset definition becomes ETL spec → pre-computed dataset
                   Library logic runs daily, results ready for consumption
```

The catalog we build now becomes the blueprint for Stage 3 ETL without additional work.

---

## Proposed Asset Schema

```python
SUCCESS_DEFINITIONS["wallet_provisioning"] = {

    # ── Identity ──────────────────────────────────────────
    "metric_id": "wallet_provisioning",
    "description": "Digital wallet provisioning via token-based transactions",
    "owner": "marketing_analytics",

    # ── Source Routing ────────────────────────────────────
    "source": "EDW",                    # "HIVE" | "EDW" | "DUAL"

    # ── Output Contract (enforced by engine) ──────────────
    "output_contract": {
        "client_key": "CLNT_NO",
        "date_key": "SUCCESS_DT",
        "deduplicate": True,
    },

    # ── Hive Config (None if EDW-only) ────────────────────
    "hive": None,

    # ── EDW Config ────────────────────────────────────────
    "edw": {
        "tables": [
            {"alias": "B", "schema": "DDWV05", "table": "CLNT_CRD_POS_LOG", "role": "primary"},
            {"alias": "C", "schema": "DL_DECMAN", "table": "TOKEN_LIST", "role": "join"},
        ],
        "business_rules": [
            "Zero-amount transactions only (AMT1 = 0)",
            "Card BIN prefix 45190 on CLNT_CRD_NO",
            "Visa debit BIN prefix 45199 on VISA_DR_CRD_NO",
            "Valid token requestor (first char > '0')",
            "Non-EMV POS entry mode (000)",
            "Service code 36 (Visa Direct)",
            "Token wallet indicator = Y (from TOKEN_LIST)",
        ],
        "query": "SELECT DISTINCT ... FROM ... WHERE ...",
        "client_key_logic": "CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER)",
        "date_field_source": "B.TXN_DT",
    },
}
```

### Hive Example (card_acquisition)

```python
SUCCESS_DEFINITIONS["card_acquisition"] = {
    "metric_id": "card_acquisition",
    "description": "New VVD card issuance in active/approved status",
    "owner": "marketing_analytics",

    "source": "HIVE",

    "output_contract": {
        "client_key": "CLNT_NO",
        "date_key": "SUCCESS_DT",
        "deduplicate": True,
    },

    "hive": {
        "table_path": "/prod/sz/.../DDWTA_VISA_DR_CRD/...",
        "date_field": "ISS_DT",
        "client_field": "CLNT_NO",
        "filters": {
            "STS_CD": ["06", "08"],
            "SRVC_ID": 36,
            "ISS_DT_NOT_NULL": True,
        },
    },

    "edw": None,
}
```

---

## Pipeline Flow (Target State)

```
MNE Input (e.g., "VAW") + Date Range
         │
         ▼
┌─────────────────────────────────────────────┐
│  MODULE 1: EXPERIMENT METADATA              │
│  "Who is in the test?"                      │
│  Output: client list + treatment dates      │
└─────────────────┬───────────────────────────┘
                  │ passes client list
                  ▼
┌─────────────────────────────────────────────┐
│  MODULE 2: CAMPAIGN METADATA                │
│  "What to measure?"                         │
│  Output: primary_metric, secondary_metric   │
└─────────────────┬───────────────────────────┘
                  │ passes metric_name
                  ▼
┌─────────────────────────────────────────────┐
│  MODULE 3: SUCCESS DEFINITION               │
│  "How to calculate?"                        │
│                                             │
│  ┌─ Asset Identity ─────────────────┐       │
│  │  metric_id, description, source  │       │
│  └──────────────┬───────────────────┘       │
│                 ▼                            │
│  ┌─ Source Router ──────────────────┐       │
│  │  source = "HIVE" | "EDW" | "DUAL"│      │
│  └──────┬───────────────┬───────────┘       │
│         ▼               ▼                   │
│  ┌─ HIVE Path ─┐  ┌─ EDW Path ────┐        │
│  │ parquet      │  │ SQL query     │        │
│  │ + PySpark    │  │ + cursor      │        │
│  │   filters    │  │ + joins       │        │
│  └──────┬───────┘  └──────┬────────┘        │
│         ▼                 ▼                  │
│  ┌─ Output Contract ───────────────┐        │
│  │  CLNT_NO + SUCCESS_DT (always)  │        │
│  └─────────────────────────────────┘        │
│  ** Only queries campaign clients **        │
│  ** Client list from Module 1 **            │
└─────────────────┬───────────────────────────┘
                  │ passes success_df
                  ▼
┌─────────────────────────────────────────────┐
│  MODULE 4: CLIENT JOURNEY                   │
│  "What actually happened?"                  │
│  Joins experiment + success + engagement    │
│  NOW CLEAN: no Layer 3 logic here           │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│  VINTAGE ENGINE (Unchanged)                 │
│  build_vintage_curves() → output            │
│  Does not know or care about sources        │
└─────────────────────────────────────────────┘
```

---

## Changes Required (Code)

### What Changes

| # | What | Current Location | Action |
|---|------|-----------------|--------|
| 1 | `apply_success_filters()` | Does not exist | **Create** — new function next to SUCCESS_DEFINITIONS |
| 2 | `load_success_outcome()` | Lines 419-454 | **Simplify** — remove filter block, call `apply_success_filters()` |
| 3 | `wallet_provisioning` entry | Lines 200-209 | **Expand** — full asset with EDW config, business rules, SQL |
| 4 | `load_token_from_edw()` | Lines 392-416 | **Add docstring** cross-referencing SUCCESS_DEFINITIONS |
| 5 | SUCCESS_DEFINITIONS schema | Lines 152-210 | **Restructure** — all metrics get identity, source routing, output contract |
| 6 | Client scoping | Not implemented | **Add** — Module 3 receives client list from Module 1, filters queries |
| 7 | All existing Hive metrics | Lines 153-199 | **Restructure** — migrate to new schema with hive/edw config blocks |

### What Does NOT Change

- `detect_success()` — engine core, untouched
- `build_vintage_curves()` — engine core, untouched
- `build_engagement_curves()` — engine core, untouched
- `run_vintage_analysis()` call flow — same sequence, cleaner internals
- Output schema — identical: MNE | COHORT | TST_GRP_CD | RPT_GRP_CD | METRIC | DAY | RATE

### Version

- Current: `vintage_engine.py` (v2.5)
- New version: `vintage_engine_v2.6.py` (do NOT overwrite existing)

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Filter logic regression (silent wrong results) | HIGH | Capture golden output before changes, compare row-by-row after |
| Client scoping misses clients | MEDIUM | Client list from Module 1 is authoritative — if they're in the experiment, they're in the list |
| EDW client list too large for WHERE IN | MEDIUM | Batch into chunks or use temp table approach for Teradata |
| wallet_provisioning SQL drift from definition | LOW | Docstring cross-reference + human review |
| New filter types not handled by apply_success_filters | MEDIUM | Add unrecognized filter key warning |

---

## Testing Strategy

1. **Before any changes:** Run all 6 campaigns on current engine, save output as golden baseline
2. **After changes:** Run same 6 campaigns on new version, compare:
   - Row counts per campaign
   - Join on all dimension columns, assert RATE matches
   - Special attention to wallet_provisioning (EDW path)
3. **Client scoping validation:** Compare client counts — scoped query should produce same join result as full table scan

---

## Open Questions

1. **EDW Client Scoping Strategy (BLOCKING for large tables):**
   - Current code queries entire EDW tables, narrows via join in Spark
   - This works for wallet_provisioning (filters narrow it enough) but will fail for large tables with fewer filters
   - Three possible strategies:
     - **A. Temp table in Teradata:** Upload client list → JOIN inside Teradata. Best performance. Requires CREATE TABLE permissions.
     - **B. Batched WHERE IN:** Split client list into chunks of ~1,000, run N queries. No permissions needed but slower.
     - **C. Status quo (full scan):** Pull everything, join in Spark. Works today but doesn't scale.
   - **Action needed:** Check if temp table creation is allowed in the Teradata environment. This determines the strategy.
   - **Ideal long-term:** Analysts provide success data from sources Hive/EDL can access. No EDW needed. But that's not today's reality.

2. **Client number format differences:** Some sources have account numbers, not client numbers. Should the asset definition include the key resolution logic (e.g., SUBSTR to extract CLNT_NO), or should that be a separate mapping module?

3. **Mnemonic recycling:** Same MNE reused across time periods. Date range + MNE combination is the true key. How does this affect asset lookup? (flagged for future consideration)

---

## Work Sequence

The dependencies between the work items:

```
Phase 1: MODULARITY FIX (no behavior change)
  ├── Restructure SUCCESS_DEFINITIONS to new schema
  ├── Create apply_success_filters()
  ├── Simplify load_success_outcome()
  ├── Bring wallet_provisioning into framework
  └── Validate: output identical to v2.5

Phase 2: CLIENT SCOPING (behavior improvement)
  ├── Resolve: Teradata temp table permissions?
  ├── Implement client list passthrough from Module 1 to Module 3
  ├── Hive path: filter by client list (Spark join — easy)
  ├── EDW path: implement chosen strategy (temp table or batch)
  └── Validate: same results, fewer rows queried

Phase 3: FUTURE (when external sources ready)
  ├── Swap Module 2 source → Mnemonic Mapping v2
  ├── Swap Module 3 source → Success Library
  └── Assets become ETL specs for curated datasets
```

Phase 1 can proceed independently.
Phase 2 requires an infrastructure answer (Teradata permissions).
Phase 3 waits for external teams.

---

## Relationship to Stages

This design work is **Stage 1.5** — improving modularity without changing behavior. It makes the Stage 2 transition (external libraries/tables) a swap of the asset source, not a code rewrite.

```
Stage 1.5 (this work):  Assets defined in code, properly modular
Stage 2:               Assets pulled from Success Library / MM v2
Stage 3:               Assets = pre-computed datasets (library runs as ETL)
```

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-28 | Created from session discussion |
