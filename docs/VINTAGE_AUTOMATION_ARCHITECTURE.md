# VVD Vintage Automation - SuperFact Framework Alignment

## Overview

This document maps the VVD Vintage Automation to the SuperFact 4-layer architecture, showing where VVD fits and the path from current state to future state.

---

## SuperFact 4-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              SUPERFACT - 4 SEMANTIC LAYERS                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │      LAYER 1        │  │      LAYER 2        │  │      LAYER 3        │              │
│  │                     │  │                     │  │                     │              │
│  │  Governed Experiment│  │  Managed Campaign   │  │  Centralized Logic  │              │
│  │  Metadata           │  │  Metadata           │  │  Repo               │              │
│  │                     │  │  (Mnemonic Mapping  │  │  (Success Library)  │              │
│  │  "Who is in test?"  │  │   v2)               │  │                     │              │
│  │                     │  │                     │  │  "How to calculate?"│              │
│  │  Source:            │  │  "What to measure?" │  │                     │              │
│  │  tactic_evnt_hist   │  │                     │  │  Source:            │              │
│  │                     │  │  Source:            │  │  GitHub repo        │              │
│  │                     │  │  CIDM_MNEMONIC_ATTRS│  │                     │              │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘              │
│            │                        │                        │                          │
│            │                        │                        │                          │
│            └────────────────────────┼────────────────────────┘                          │
│                                     │                                                   │
│                                     ▼                                                   │
│                         ┌─────────────────────┐                                         │
│                         │      LAYER 4        │                                         │
│                         │                     │                                         │
│                         │  Client Marketing   │                                         │
│                         │  Interaction Journey│                                         │
│                         │                     │                                         │
│                         │  "What did client   │                                         │
│                         │   actually do?"     │                                         │
│                         │                     │                                         │
│                         │  Sources:           │                                         │
│                         │  VISA_DR_CRD        │                                         │
│                         │  TACTIC_IP_AR_HIST  │                                         │
│                         │  Email Vendor       │                                         │
│                         │  RPT_PME_DSKTP      │                                         │
│                         └─────────────────────┘                                         │
│                                     │                                                   │
└─────────────────────────────────────┼───────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DATA ASSETS (Outputs)                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Semantic Results Layer 1:  Daily Experiment Results  |  Daily Campaign Results   │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                         │                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Semantic Staging Layer:  Engagement Layer  |  Cross-Sell/Share of Wallet Layer   │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                         │                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Daily for VINTAGE and Dashboard Trending  ◄──── VVD VINTAGE AUTOMATION SITS HERE │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                         │                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Aggregated Measurement Results:  MBR / QBR / PowerPack                           │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                             CONSUMPTION (Outside Framework)                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │
│  │  Dashboards   │  │   MBR/QBR     │  │  Gen AI/LLM   │  │  Deep Dives   │            │
│  │  (Tableau or  │  │   Reports     │  │   Inputs      │  │               │            │
│  │   HTML)       │  │               │  │               │  │               │            │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Where VVD Vintage Automation Fits

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      VVD VINTAGE AUTOMATION - LAYER TOUCHPOINTS                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  LAYER 1                    LAYER 2                    LAYER 3                          │
│  Experiment Metadata        Campaign Metadata          Success Library                  │
│  ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐            │
│  │ tactic_evnt_hist │       │ Mnemonic Mapping │       │ GitHub Success   │            │
│  │                  │       │ v2               │       │ Logic            │            │
│  │ • TACTIC_ID      │       │                  │       │                  │            │
│  │ • TST_GRP_CD     │       │ MNE → Campaign   │       │ %Run Success1    │            │
│  │ • CLNT_NO        │       │ MNE → Metrics    │       │ SQL definitions  │            │
│  │ • TREATMT_STRT_DT│       │ MNE → Segments   │       │ Filter rules     │            │
│  └────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘            │
│           │                          │                          │                       │
│           │  "Who is in test?"       │  "What to measure?"      │  "How to calculate?" │
│           │                          │                          │                       │
│           └──────────────────────────┼──────────────────────────┘                       │
│                                      │                                                  │
│                                      ▼                                                  │
│                           ┌──────────────────┐                                          │
│                           │     LAYER 4      │                                          │
│                           │ Client Journey   │                                          │
│                           │                  │                                          │
│                           │ VISA_DR_CRD      │                                          │
│                           │ (card issuance)  │                                          │
│                           │                  │                                          │
│                           │ "Did they open   │                                          │
│                           │  a card?"        │                                          │
│                           └────────┬─────────┘                                          │
│                                    │                                                    │
│                                    │  "What did client actually do?"                    │
│                                    │                                                    │
│                                    ▼                                                    │
│           ┌─────────────────────────────────────────────────────────────────┐          │
│           │                  VVD VINTAGE CURVES ENGINE                       │          │
│           │                  (vintage_all_in_one.py)                         │          │
│           │                                                                  │          │
│           │  Combines all 4 layers:                                          │          │
│           │  • Layer 1: Get test/control assignments                         │          │
│           │  • Layer 2: Know which metrics apply to campaign                 │          │
│           │  • Layer 3: Apply success calculation logic                      │          │
│           │  • Layer 4: Check if client actually succeeded                   │          │
│           │                                                                  │          │
│           │  Produces: Cumulative curves, lift, confidence intervals         │          │
│           └─────────────────────────────────────────────────────────────────┘          │
│                                    │                                                    │
│                                    ▼                                                    │
│           ┌─────────────────────────────────────────────────────────────────┐          │
│           │            DAILY FOR VINTAGE AND DASHBOARD TRENDING             │          │
│           │                      (Data Asset)                                │          │
│           │                                                                  │          │
│           │  CSV/Parquet with: COHORT | DAY | TEST_RATE | CTRL_RATE | LIFT  │          │
│           └─────────────────────────────────────────────────────────────────┘          │
│                                    │                                                    │
│                                    ▼                                                    │
│           ┌─────────────────────────────────────────────────────────────────┐          │
│           │                       DASHBOARDS                                 │          │
│           │                                                                  │          │
│           │  Track A: Tableau (CIDM)    Track B: HTML (Self-Sufficient)     │          │
│           └─────────────────────────────────────────────────────────────────┘          │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Current State vs Future State

### Layer 1: Experiment Metadata

| Aspect | Current State | Future State |
|--------|---------------|--------------|
| Data Source | tactic_evnt_hist (parquet) | Same |
| Test Group | Hardcoded: TG4 = Test | From metadata table |
| Campaign Name | Hardcoded: MNE lookup | From Mnemonic Mapping v2 |
| Segments | RPT_GRP_CD exists, meaning hardcoded | Segment lookup table |

**Current Code:**
```python
# Hardcoded in CAMPAIGN_CONFIG dict
"test_group": "TG4"  # From Word documents
```

**Future Code:**
```python
# Query Mnemonic Mapping v2
test_group = spark.sql("SELECT test_group FROM mnemonic_mapping WHERE mne = 'VCN'")
```

---

### Layer 2: Campaign Metadata (Mnemonic Mapping v2)

| Aspect | Current State | Future State |
|--------|---------------|--------------|
| Campaign → Metric | Hardcoded dict | CIDM_MNEMONIC_ATTRS table |
| Primary Metric | Inline definition | metric_id reference |
| Secondary Metric | Not captured | Defined in mapping |

**What Should Exist in Mnemonic Mapping v2:**
- Campaign Description
- LOB
- Campaign Category
- **Primary Metric** (new)
- **Secondary Metric** (new)
- **Action/Sub-Action Type** (new)
- **Client Mindset/Continuum** (new)

---

### Layer 3: Success Library

| Aspect | Current State | Future State |
|--------|---------------|--------------|
| Logic Location | Hardcoded in Python | GitHub repo |
| Format | Inline filters | SQL / %Run functions |
| Governance | None | Version controlled |

**Current Code:**
```python
# Hardcoded in vintage_all_in_one.py
CAMPAIGN_CONFIG = {
    "VCN": {
        "success_table_path": "/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/",
        "filters": {"STS_CD": ["06","08"], "SRVC_ID": 36}
    }
}
```

**Future: Pull from Success Library**
```python
# Success Library defines
# metric_id: VVD_ACQ_001
# sql_logic: SELECT ... WHERE STS_CD IN ('06','08') AND SRVC_ID = 36
success_logic = spark.sql("SELECT sql_logic FROM success_library WHERE metric_id = 'VVD_ACQ_001'")
```

---

### Layer 4: Client Marketing Interaction Journey

| Aspect | Current State | Future State |
|--------|---------------|--------------|
| Data Sources | VISA_DR_CRD only | Multiple sources unified |
| Coverage | Card issuance only | Full journey: email → click → apply → complete |
| Limitation | Only "decisions" | Full touchpoints |

**Current:**
- We check VISA_DR_CRD for card issuance (did they open a card?)

**Future:**
- Email open/click from vendor
- App visits from TACTIC_IP_AR_HIST
- Branch visits from RPT_PME_DSKTP
- Full funnel: awareness → consideration → application → approval → funding

---

## The Virtuous Cycle

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           GOVERNANCE GROWTH CYCLE                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│                    ┌──────────────────────────┐                                         │
│                    │  New Campaign Onboarded  │                                         │
│                    │  (e.g., add VAW)         │                                         │
│                    └────────────┬─────────────┘                                         │
│                                 │                                                       │
│                                 ▼                                                       │
│                    ┌──────────────────────────┐                                         │
│                    │ Build Vintage Curves     │                                         │
│                    └────────────┬─────────────┘                                         │
│                                 │                                                       │
│              ┌──────────────────┼──────────────────┐                                    │
│              ▼                  ▼                  ▼                                    │
│   ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐                       │
│   │ Document in      │ │ Add to           │ │ Define success   │                       │
│   │ Mnemonic Mapping │ │ Experiment       │ │ in Success       │                       │
│   │ v2 (Layer 2)     │ │ Metadata (L1)    │ │ Library (L3)     │                       │
│   └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘                       │
│            │                    │                    │                                  │
│            └────────────────────┼────────────────────┘                                  │
│                                 │                                                       │
│                                 ▼                                                       │
│            ┌──────────────────────────────────────────┐                                 │
│            │  ALL 4 LAYERS GROW TOGETHER              │                                 │
│            │                                          │                                 │
│            │  Each campaign onboarded:                │                                 │
│            │  • Captures experiment setup (L1)        │                                 │
│            │  • Documents campaign metadata (L2)      │                                 │
│            │  • Defines success calculation (L3)      │                                 │
│            │  • Maps to client journey data (L4)      │                                 │
│            │                                          │                                 │
│            │  Result: Next campaign faster to build   │                                 │
│            └──────────────────────────────────────────┘                                 │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Source of Truth Metrics (From Success Library)

From the SuperFact framework, these are the metric categories:

| Category | Examples | VVD Relevance |
|----------|----------|---------------|
| **Conversion** | Cheque Account Opening, Credit Card Opening, Mortgage Funded, Loan Approved | ✅ Primary for VCN, VDA |
| **Share of Wallet** | Glue Activities, Utilization, Avg Balance, PAC Indicator, Transactions | ✅ Primary for VUI, VUT |
| **Engagement** | Email Unsubscribe Rate, Banner View/Dismiss, Mobile Logins, Branch Visits | Secondary metrics |
| **Retention** | Account Closure, Client Attrition, Change in Products/Services | Secondary metrics |
| **Profitability** | Account Level, Client Level | Future consideration |

---

## VVD Campaigns Mapped to Layers

| MNE | Campaign | Layer 4 (Success Check) | Primary Metric Category |
|-----|----------|-------------------------|------------------------|
| VCN | Contextual Notification | VISA_DR_CRD (card issuance) | Conversion |
| VDA | Black Friday Cyber Monday | VISA_DR_CRD (card issuance) | Conversion |
| VDT | Activation Trigger | VISA_DR_CRD (activation) | Conversion |
| VUI | Usage Trigger | Transaction data | Share of Wallet |
| VUT | Tokenization Usage | Tokenization events | Engagement |
| VAW | Add To Wallet | Tokenization events | Engagement |

---

## Tech Stack Roadmap Alignment

From SuperFact roadmap:

| Timeframe | Platform | VVD Vintage Position |
|-----------|----------|---------------------|
| **Short Term (Now)** | Teradata Datalab | Current: YARN/Spark Jupyter |
| **Medium Term (6+ months)** | Orchestration: Airflow + Dagster<br>Transformations: Spark SQL | Scheduled jobs possible |
| **Long Term (12+ months)** | Iceberg + Snowflake Analytics Layer<br>Trino/dbt | Full automation |

---

## Two Tracks for Dashboard Delivery

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            DASHBOARD DELIVERY OPTIONS                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  TRACK A: Official Channel              TRACK B: Self-Sufficient                        │
│  ┌─────────────────────────┐            ┌─────────────────────────┐                     │
│  │                         │            │                         │                     │
│  │  CIDM / Tableau Team    │            │  vintage_dashboard.py   │                     │
│  │                         │            │                         │                     │
│  │  • Official location    │            │  • HTML + Plotly.js     │                     │
│  │  • Governed refresh     │            │  • RBC brand colors     │                     │
│  │  • Requires handoff     │            │  • Can share anywhere   │                     │
│  │                         │            │  • No dependencies      │                     │
│  │  Blocker: Need to       │            │                         │                     │
│  │  define data format     │            │  Status: Built, testing │                     │
│  │                         │            │                         │                     │
│  └─────────────────────────┘            └─────────────────────────┘                     │
│                                                                                         │
│  Both tracks consume from same data asset:                                              │
│  "Daily for Vintage and Dashboard Trending"                                             │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary: What VVD Vintage Automation Does

1. **Pulls from Layer 1** - Gets experiment population (tactic_evnt_hist)
2. **Applies Layer 2** - Knows what metric applies to campaign (currently hardcoded)
3. **Executes Layer 3** - Runs success calculation logic (currently hardcoded)
4. **Checks Layer 4** - Looks at actual client outcomes (VISA_DR_CRD)
5. **Produces Data Asset** - Vintage curves for trending
6. **Feeds Dashboards** - Track A or Track B

**Current state:** Layers 2 and 3 are hardcoded in Python dict (CAMPAIGN_CONFIG)

**Future state:** Layers 2 and 3 pull from governed tables/GitHub

**What doesn't change:** Layer 1 source, Layer 4 source, vintage calculation engine

---

## Key Takeaway

VVD Vintage Automation is a **working implementation** that:
- Consumes all 4 SuperFact layers
- Produces "Daily for Vintage and Dashboard Trending" data asset
- Is architected for transition from hardcoded → data-driven
- Grows governance with each campaign onboarded

The hardcoded parts (CAMPAIGN_CONFIG) are **documented swap points** that can be replaced when Mnemonic Mapping v2 and Success Library infrastructure are ready.
