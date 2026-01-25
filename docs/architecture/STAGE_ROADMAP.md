# Vintage Engine: Stage Roadmap

**Purpose:** Practical pathway from where we are (v2.1) to where we want to be (curated architecture).

**Audience:** Marketing analytics team building VVD campaign measurement.

---

## 1. Current State: What v2.1 CAN Do Today

v2.1 is a working Stage 1 implementation. It runs, it produces output, and it is ready to demo.

### What Works

| Capability | Status | Details |
|------------|--------|---------|
| Load experiment data | Working | 6 campaigns (VCN, VDA, VDT, VUI, VUT, VAW) from tactic_evnt_hist |
| Test vs Control split | Working | Uses TST_GRP_CD = TG4 for Test |
| Cohort assignment | Working | Monthly cohorts from TREATMT_STRT_DT |
| Success detection | Working | 4 metrics: card_acquisition, card_activation, card_usage, wallet_provisioning |
| Vintage curves | Working | Cumulative conversion rates over treatment window |
| Confidence intervals | Working | 95% CI with statistical significance flag |
| Channel breakdown | Working | Counts by TACTIC_CELL_CD |
| Email engagement | Working | Sent/Opened/Clicked from EDW (fixed in v2.1) |
| HDFS export | Working | CSV files with clickable download links |
| Validation summary | Working | Spot-checks data after each run |

### Why This Is the Right Starting Point

1. **It works end-to-end.** You can run `run_vintage_analysis(spark, 'VCN')` and get a complete result.

2. **It demonstrates the architecture concepts.** The 4-layer structure (Experiment, Campaign, Success, Journey) is visible in the code, even though it is all in one file.

3. **It produces stakeholder-ready output.** Vintage curves, lift calculations, and summaries can be demoed today.

4. **The "swap points" are identified.** Each hardcoded dictionary (CAMPAIGN_METADATA, SUCCESS_DEFINITIONS) has a comment pointing to its future source.

---

## 2. Stage Definitions

### Stage 1: Hardcoded Single-File (Current - v2.1)

**What it is:**
- One Python file, ~1600 lines
- All configuration hardcoded in dictionaries
- Copy-paste to reuse in another project
- Runs in Jupyter/Hue notebook

**What it does well:**
- Produces correct results
- Documents business logic inline
- Easy to modify and experiment
- No external dependencies beyond Spark/Pandas

**Limitations:**
- Cannot share improvements across projects
- Configuration changes require code edits
- No formal testing
- Business logic mixed with technical implementation

---

### Stage 1.5: Incremental Improvements (Next)

**What it is:**
- Still single-file
- Still runs the same way
- Better organized internally
- Adds documentation without changing functionality

**Goal:** Make v2.1 more maintainable WITHOUT breaking it.

See Section 4 for specific quick wins.

---

### Stage 2: GitHub Library

**What it means:**
- Success metric definitions live in separate Python files
- A semantic catalog points to those files
- The engine pulls code at runtime: `from success_library import card_acquisition`
- Changes to metric definitions auto-propagate to all consumers

**What triggers Stage 2:**
- Another team wants to use the same success definitions
- We have 5+ metrics that are stable and tested
- There is a shared repository (even just a team GitHub)

**What changes:**
```
# Stage 1 (current)
SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "table_path": "/prod/sz/...",
        "filters": {"STS_CD": ["06", "08"], ...},
        ...
    }
}

# Stage 2 (future)
SUCCESS_CATALOG = {
    "card_acquisition": {
        "code_path": "success_library/card_acquisition.py",
        "version": "1.2",
        ...
    }
}
# Engine imports and executes: card_acquisition.calculate(spark, client_df)
```

**What does NOT change:**
- The analysis logic (detect_success, build_vintage_data, calculate_ci)
- The output format
- How users call the engine

---

### Stage 3: Curated Data

**What it means:**
- Success metrics are pre-calculated and stored in governed tables
- The engine queries data instead of calculating
- Semantic catalog points to table paths, not code paths

**What triggers Stage 3:**
- Enterprise data governance approval
- Pre-calculated success flags are available in curated datasets
- Performance requires avoiding repeated calculation

**What changes:**
```
# Stage 2
SUCCESS_CATALOG = {
    "card_acquisition": {
        "code_path": "success_library/card_acquisition.py"
    }
}

# Stage 3
SUCCESS_CATALOG = {
    "card_acquisition": {
        "table_path": "/curated/success/card_acquisition"
    }
}
# Engine reads table directly: spark.read.parquet(table_path)
```

**Key insight:** Stage 2 code becomes Stage 3 ETL. The `card_acquisition.py` file becomes the job that populates `/curated/success/card_acquisition`.

---

## 3. Transition Triggers

### When to Move from Stage 1 to Stage 1.5

Move when ANY of these are true:

| Trigger | Signal |
|---------|--------|
| Code review feedback | Someone says "I don't understand what this does" |
| Bug found | Root cause was unclear documentation or naming |
| New metric request | Adding a metric feels harder than it should |
| Handoff needed | Another person needs to run/modify the code |

**Stage 1.5 has no downside.** It improves maintainability without changing behavior.

---

### When to Move from Stage 1.5 to Stage 2

Move when ALL of these are true:

| Trigger | Why It Matters |
|---------|----------------|
| 5+ success metrics that are stable | Worth the overhead of separate files |
| Another team wants the same metrics | Copy-paste creates drift |
| Shared repository exists | Need somewhere to put the library |
| Team agrees on interface | `calculate(spark, client_df) -> DataFrame` |

**Do NOT move to Stage 2 if:**
- Metrics are still changing frequently (iterate faster in Stage 1)
- You are the only consumer (no reuse benefit)
- No shared repository exists (nowhere to put it)

---

### When to Move from Stage 2 to Stage 3

Move when ALL of these are true:

| Trigger | Why It Matters |
|---------|----------------|
| Data governance approval | Curated tables have ownership and SLAs |
| ETL pipeline exists | Someone is populating the tables |
| Performance matters | Pre-calculation is faster than on-demand |
| Multiple consumers exist | Worth the governance overhead |

**Do NOT move to Stage 3 if:**
- Metrics are still evolving (harder to change curated tables)
- Only one consumer (governance overhead not justified)
- No ETL support (who will populate the tables?)

---

## 4. Stage 1.5 Quick Wins

These improve v2.1 without breaking it. Each is independent - do any subset in any order.

### Documentation Improvements (Small Effort)

| Change | What | Why |
|--------|------|-----|
| Add docstrings to SUCCESS_DEFINITIONS | Each metric gets a multi-line description | Explains business logic, not just code |
| Document filter logic | Comment explaining WHY STS_CD = ['06', '08'] | Future maintainer needs context |
| Add data lineage comments | Where does each field come from? | Traceability |

**Example:**
```python
SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "description": """
        Client acquired a new VVD card.

        Business Definition:
        - Card is considered acquired when ISS_DT is populated
        - Status must be Active (06) or Approved (08)
        - Only VVD cards (SRVC_ID = 36)

        Data Source: DDWTA_VISA_DR_CRD (Latest partition)
        Owner: Marketing Analytics
        Last Validated: 2026-01
        """,
        ...
    }
}
```

---

### Code Organization (Small Effort)

| Change | What | Why |
|--------|------|-----|
| Group related functions | All vintage calculations together | Easier to navigate |
| Consistent naming | All loading functions start with `load_` | Predictable |
| Separate concerns | Configuration at top, functions in middle, execution at bottom | Current structure, keep it |

**No refactoring needed.** v2.1 already has good structure. Just add section comments if helpful.

---

### Validation Improvements (Medium Effort)

| Change | What | Why |
|--------|------|-----|
| Add row count checks | Log expected vs actual record counts | Catch data issues early |
| Add date range validation | Are all dates within expected window? | Prevent stale data |
| Add metric sanity checks | Is conversion rate reasonable (0-100%)? | Catch calculation bugs |

**Example addition to `print_validation_summary()`:**
```python
# Sanity check: conversion rates should be 0-100%
if vintage_df is not None:
    max_rate = vintage_df["TEST_RATE"].max()
    if max_rate > 100 or max_rate < 0:
        issues.append(f"WARNING: Invalid conversion rate: {max_rate}")
```

---

### Output Improvements (Medium Effort)

| Change | What | Why |
|--------|------|-----|
| Add metadata to exports | Include run timestamp, version, parameters | Audit trail |
| Add campaign names to output | MNE column + full campaign name | Stakeholder clarity |
| Standardize column order | Dimensions first, then metrics | Dashboard consistency |

**Example metadata row:**
```python
# Add to export functions
metadata = {
    "engine_version": "2.1",
    "run_timestamp": datetime.now().isoformat(),
    "years_included": YEARS_TO_INCLUDE,
    "confidence_level": CONFIDENCE_LEVEL
}
```

---

### Testing Hooks (Medium Effort)

| Change | What | Why |
|--------|------|-----|
| Add sample data mode | Run with mock data, no Spark | Test logic locally |
| Add assertion mode | Verify intermediate results match expectations | Regression testing |
| Extract pure functions | `calculate_ci()` already testable | Build test coverage |

**Not a full test suite.** Just make it possible to test later.

---

## 5. Stage 2 Prerequisites Checklist

Before Stage 2 makes sense, verify:

### Technical Prerequisites

- [ ] 5+ success metrics defined and stable
- [ ] Consistent interface for all metrics: `calculate(spark, client_df) -> DataFrame`
- [ ] Output schema defined: `[client_id, success_date, success_flag]`
- [ ] Each metric tested with sample data
- [ ] Version numbering convention established

### Organizational Prerequisites

- [ ] Shared repository exists (GitHub, BitBucket, etc.)
- [ ] At least one other team wants to use the metrics
- [ ] Agreement on ownership (who maintains the library?)
- [ ] Agreement on change process (how do updates get approved?)
- [ ] Documentation standard agreed (README, docstrings, etc.)

### Governance Prerequisites

- [ ] Metric definitions approved by business stakeholders
- [ ] Semantic naming conventions agreed (e.g., `card_acquisition` vs `new_card_acq`)
- [ ] Versioning policy defined (when to create v2 vs update v1)

---

## 6. What NOT To Do Yet

### Over-Engineering Traps

| Temptation | Why to Wait |
|------------|-------------|
| Build a plugin architecture | Only one engine exists. Add abstraction when you have 2+ engines. |
| Create a configuration service | Hardcoded config is fine until there are multiple consumers. |
| Build a web UI | Jupyter notebooks work. Build UI when you have non-technical users. |
| Abstract the data layer | Current Spark/EDW pattern works. Abstract when you need multiple backends. |
| Implement enrichment module | Placeholder is fine. Build when enrichment data is available. |

### Premature Optimizations

| Temptation | Why to Wait |
|------------|-------------|
| Cache everything | Current caching (`persist()`) is appropriate. Add more when performance is an issue. |
| Parallelize campaign runs | Sequential is fine for 6 campaigns. Parallelize when it takes too long. |
| Pre-aggregate vintage data | On-demand calculation is fast enough. Pre-aggregate when it is not. |

### Governance Overhead

| Temptation | Why to Wait |
|------------|-------------|
| Create formal data contracts | Document informally first. Formalize when contracts provide value. |
| Build semantic catalog | A README is enough until you have 20+ assets. |
| Implement data lineage tracking | Comments in code are enough for now. |

---

## Summary: The Path Forward

```
TODAY                    NEXT                     LATER                    FUTURE
---------               ----------               ----------               ----------
Stage 1                 Stage 1.5                Stage 2                  Stage 3
(v2.1)                  (Documentation)          (GitHub Library)         (Curated Data)

What exists:            What to add:             What to build:           What to integrate:
- Working engine        - Better docstrings      - Separate metric files  - Pre-calculated tables
- 6 campaigns           - Validation checks      - Semantic catalog       - Governed datasets
- 4 metrics             - Metadata in exports    - Import mechanism       - ETL pipelines
- HDFS export           - Testing hooks          - Version control        - Data quality checks

Trigger: None           Trigger: Any feedback    Trigger: Reuse demand    Trigger: Governance approval
(already here)          or maintenance need      + 5 stable metrics       + ETL support
```

---

## Document History

- **Created:** 2026-01-23
- **Purpose:** Practical roadmap from v2.1 to architecture vision
- **Related:** VINTAGE_ENGINE_ARCHITECTURE.md (north star), vintage_engine_v2.1.py (current code)
