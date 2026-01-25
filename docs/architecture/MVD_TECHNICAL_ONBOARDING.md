# Vintage Automation: Technical Onboarding

## Join Us in Building the Measurement Standard

**Audience:** Technical team members, peers, collaborators
**Purpose:** Collaboration + Adoption + Inspiration
**Key Message:** Here's what we built, here's how it works, and here's how YOUR work can plug into it.

---

## Why This Matters to YOU

You've probably done this before:
- Someone asks "how many cards were acquired for campaign X?"
- You write SQL, figure out the filters, find the right tables
- Three months later, someone else asks the same question
- They write their own SQL. Different filters. Different answer.

**We're fixing this.** And we need your help.

---

## The Architecture: SuperFact 4-Layer Framework

We built a modular engine where each layer has a clear responsibility:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUPERFACT 4-LAYER VIEW                               │
│                          vintage_all_in_one.py                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ╔═════════════════════════════════════════════════════════════════════╗   │
│  ║  LAYER 1: EXPERIMENT METADATA                                        ║   │
│  ║  "Who is in the test?"                                               ║   │
│  ║                                                                      ║   │
│  ║  Code:     load_tactic()                                             ║   │
│  ║  Config:   YEARS_TO_INCLUDE, TEST_GROUP_CODE                         ║   │
│  ║  Source:   tactic_evnt_hist (parquet)                                ║   │
│  ║  Swap to:  → Experiment Metadata table (when built)                  ║   │
│  ╚═════════════════════════════════════════════════════════════════════╝   │
│                                       │                                     │
│                                       ▼                                     │
│  ╔═════════════════════════════════════════════════════════════════════╗   │
│  ║  LAYER 2: CAMPAIGN METADATA                                          ║   │
│  ║  "What metric should we measure?"                                    ║   │
│  ║                                                                      ║   │
│  ║  Code:     get_campaign_config()                                     ║   │
│  ║  Config:   CAMPAIGN_METADATA dict (6 campaigns)                      ║   │
│  ║  Fields:   campaign_name, success_type, primary_metric               ║   │
│  ║  Swap to:  → Mnemonic Mapping v2 query                               ║   │
│  ╚═════════════════════════════════════════════════════════════════════╝   │
│                                       │                                     │
│                                       ▼                                     │
│  ╔═════════════════════════════════════════════════════════════════════╗   │
│  ║  LAYER 3: SUCCESS DEFINITIONS                                        ║   │
│  ║  "HOW do we calculate this metric?"                                  ║   │
│  ║                                                                      ║   │
│  ║  Code:     get_success_definition()                                  ║   │
│  ║  Config:   SUCCESS_DEFINITIONS dict (4 metrics)                      ║   │
│  ║  Fields:   table_path, date_field, filters, source                   ║   │
│  ║  Swap to:  → Success Library (GitHub %Run OR curated data set)       ║   │
│  ╚═════════════════════════════════════════════════════════════════════╝   │
│                                       │                                     │
│                                       ▼                                     │
│  ╔═════════════════════════════════════════════════════════════════════╗   │
│  ║  LAYER 4: CLIENT JOURNEY                                             ║   │
│  ║  "What did they actually do?"                                        ║   │
│  ║                                                                      ║   │
│  ║  Code:     load_fulfillment(), load_email_engagement(),              ║   │
│  ║            load_success_outcome()                                    ║   │
│  ║  Sources:  HIVE (VISA_DR_CRD, POS_TXN) + EDW (email, fulfillment)   ║   │
│  ║  Swap to:  → Unified Client Journey semantic layer                   ║   │
│  ╚═════════════════════════════════════════════════════════════════════╝   │
│                                       │                                     │
│                                       ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  VINTAGE ENGINE (Layer-agnostic - does NOT change)                   │   │
│  │                                                                      │   │
│  │  detect_success() → build_vintage_data() → prepare_vintage_table()   │   │
│  │  calculate_ci() → generate_summary() → plot_vintage()                │   │
│  │                                                                      │   │
│  │  This block is STABLE. It doesn't care where data comes from.        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                       │                                     │
│                    ┌──────────────────┴──────────────────┐                 │
│                    ▼                                     ▼                  │
│             ┌─────────────┐                       ┌─────────────┐          │
│             │  TRACK A    │      PARALLEL         │  TRACK B    │          │
│             │  Official   │ ◄──────────────────►  │  In-House   │          │
│             │  Tableau    │                       │  SharePoint │          │
│             └─────────────┘                       └─────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**One engine. Two delivery tracks. Both run in parallel.**

---

## What's Hardcoded Today (The Swap Points)

Here's where YOUR work can plug in:

### Layer 1: Experiment Metadata
```python
# TODAY (hardcoded)
YEARS_TO_INCLUDE = [2025, 2026]
TEST_GROUP_CODE = "TG4"

# FUTURE (dynamic - when Experiment Metadata table is built)
exp_meta = query_experiment_metadata(mne)
YEARS_TO_INCLUDE = exp_meta["active_years"]
TEST_GROUP_CODE = exp_meta["test_group_code"]
```

**Your opportunity:** If you're building the Experiment Metadata table, these variables swap to your queries.

---

### Layer 2: Campaign Metadata
```python
# TODAY (hardcoded)
CAMPAIGN_METADATA = {
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
    },
    # ... 6 campaigns hardcoded
}

# FUTURE (dynamic - when Mnemonic Mapping v2 has metric fields)
config = spark.sql("""
    SELECT primary_metric, secondary_metric, description
    FROM mnemonic_mapping_v2
    WHERE mne = 'VCN'
""")
```

**Your opportunity:** If you're enhancing Mnemonic Mapping v2 with primary/secondary metric fields, the engine will automatically use your work.

---

### Layer 3: Success Definitions (THIS IS THE BIG ONE)

```python
# TODAY (hardcoded)
SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "description": "Client acquired a new VVD card",
        "source": "HIVE",
        "table_path": "/prod/sz/.../DDWTA_VISA_DR_CRD/",
        "date_field": "ISS_DT",
        "filters": {
            "STS_CD": ["06", "08"],
            "SRVC_ID": 36,
            "ISS_DT_NOT_NULL": True
        },
    },
    # ... 4 metrics hardcoded
}

# FUTURE (Option A - GitHub %Run)
%run /success_library/metrics/card_acquisition.py
success_df = get_card_acquisition(spark, client_list)

# FUTURE (Option B - Curated Data Set)
success_df = spark.read.parquet("/semantic/success/card_acquisition")
```

**Your opportunity:**
- Have a metric definition? Share it! It goes in the Success Library.
- Have curated data sets? We can point the engine to them.
- Know the "real" filters for a metric? Document them!

---

### Layer 4: Client Journey
```python
# TODAY (direct queries)
email_df = load_email_engagement(spark, treatment_ids)  # Direct EDW query
success_df = load_success_outcome(spark, config)  # Direct HIVE read

# FUTURE (semantic layers)
journey_df = spark.read.parquet("/semantic/client_journey")
```

**Your opportunity:** If you're building semantic layers (engagement, fulfillment, etc.), the engine can point to them.

---

## The Virtuous Cycle: Why Your Contribution Matters

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      HOW THE LIBRARY GROWS                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   You define "card_acquisition" once                                    │
│            │                                                            │
│            ▼                                                            │
│   It goes in the Success Library                                        │
│            │                                                            │
│            ▼                                                            │
│   Campaign 1 uses it ✓                                                  │
│   Campaign 2 uses it ✓ (no new work!)                                   │
│   Campaign 5 uses it ✓ (still no new work!)                             │
│            │                                                            │
│            ▼                                                            │
│   Another team needs "card_acquisition"?                                │
│   They use YOUR definition. Consistency. Trust.                         │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────     │
│   RESULT: Define once, reuse forever                                    │
│   YOUR CONTRIBUTION: Multiplied across the organization                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**We've run 6 campaigns with only 4 unique metrics.** Campaign 7, 8, 9 will be even easier.

---

## Track A + Track B: Both Running in Parallel

The engine produces output that feeds BOTH delivery tracks:

| | Track A (Official) | Track B (In-House) |
|---|---|---|
| **What** | Tableau dashboards via CIDM | HTML/Plotly on SharePoint |
| **Status** | Pending CIDM alignment | Ready NOW |
| **Refresh** | Automated (when aligned) | Re-run engine, deploy |
| **Control** | CIDM governs | We control |

**Why both?**
- Track B lets us prove value immediately
- Track A gives us enterprise credibility when ready
- Same engine, same data, two delivery mechanisms

**Your opportunity:** If you're on CIDM team, help us align Track A. If you're on our team, help us iterate Track B.

---

## How to Contribute

### If you have a metric definition:
1. Document the filters, source tables, and logic
2. Share with us - we'll add it to SUCCESS_DEFINITIONS
3. Future: It becomes a Success Library code file

### If you have a curated data set:
1. Tell us what it contains and where it lives
2. We can point Layer 3 or Layer 4 to it
3. Engine automatically uses your work

### If you're building semantic layers:
1. Let us know the schema and path
2. We'll create a swap point to your layer
3. When ready, we flip the switch

### If you know "the right way" to calculate something:
1. Tell us! Tribal knowledge needs to be documented
2. We'll codify it in the Success Library
3. Everyone benefits from your expertise

---

## What We've Built So Far

| Component | Status | Lines of Code |
|-----------|--------|---------------|
| Layer 1: load_tactic() | Done | ~60 |
| Layer 2: CAMPAIGN_METADATA | 6 campaigns | Dict |
| Layer 3: SUCCESS_DEFINITIONS | 4 metrics | Dict |
| Layer 4: Email engagement | Done | ~70 |
| Layer 4: Success outcome | Done | ~100 |
| Engine: Vintage curves | Done | ~200 |
| Engine: Statistics | Done | ~50 |
| Plotting | Done | ~100 |
| Track B: HTML Dashboard | Done | Separate file |

**Total: ~600 lines of Python that measure campaigns.**

---

## The Code Structure (For Reference)

```
vintage_all_in_one.py
│
├── Lines 31-38:   Configuration (YEARS, TEST_GROUP)
├── Lines 40-60:   Paths (HIVE, EDW sources)
├── Lines 62-110:  CAMPAIGN_METADATA (Layer 2)
├── Lines 112-177: SUCCESS_DEFINITIONS (Layer 3)
│
├── Lines 213-280: load_tactic() (Layer 1)
├── Lines 282-339: load_fulfillment() (Layer 4)
├── Lines 341-419: load_email_engagement() (Layer 4)
├── Lines 421-516: load_success_outcome() (Layer 4)
│
├── Lines 518-564: detect_success() (Join)
├── Lines 611-754: Vintage Engine (stable)
├── Lines 756-837: Plotting (stable)
└── Lines 839-967: run_vintage_analysis() (orchestrator)
```

---

## Quick Reference: What Swaps to What

| Layer | Hardcoded Items | Count | Swaps To | Trigger |
|-------|-----------------|-------|----------|---------|
| Layer 1 | Years, test group, path | 3 | Experiment Metadata table | Table built |
| Layer 2 | Campaign config | 24 | Mnemonic Mapping v2 | MM v2 has metric fields |
| Layer 3 | Success definitions | 24 | Success Library | Library established |
| Layer 4 | Paths, EDW queries | 8 | Semantic layers | Layers built |
| **Total** | | **59** | | |

**59 items ready to swap when YOUR work is ready.**

---

## The Ask: Join Us

We're building measurement infrastructure that scales. It's not just our project - it's a foundation for the team.

**We need you to:**
1. **Share** - If you have metric definitions, share them
2. **Collaborate** - Help us fill the gaps in the Success Library
3. **Adopt** - Use these definitions instead of writing your own
4. **Contribute** - Your semantic layers can plug right in

**What you get:**
- Your definitions become the standard
- Your work gets reused across campaigns
- Less "can you pull this data?" requests
- Consistency across the team

---

## Next Steps (For Contributors)

| If You Have... | Do This | Contact |
|----------------|---------|---------|
| Metric definition | Document filters + tables | [Team] |
| Curated data set | Share path + schema | [Team] |
| Semantic layer | Tell us when it's ready | [Team] |
| Suggestions | Open an issue or PR | [Repo] |
| Questions | Reach out! | [Team] |

---

## Summary

**What we built:** A modular measurement engine with clear swap points.

**Why it matters to you:**
- Your work can plug in without re-architecture
- Your definitions become the standard
- Your contributions get multiplied across campaigns

**What we need from you:** Collaboration. Share what you're building. Let's make this the measurement standard together.

---

*"We're not just measuring campaigns. We're building the metadata ecosystem that makes measurement easy for everyone."*
