# SuperFact 4-Layer Framework - Detailed Mental Map

Based on presentation images reviewed January 21, 2026.

---

## Layer 1: Governed Experiment Metadata

**Question:** "Who is in the test?"

### Source that EXISTS today
- `tactic_evnt_hist` (Tactic History / ODS)
- `ed10_im.prod_x610_crm.ods_mr_hist`

### Fields that EXIST in the data

| Field | Exists? |
|-------|---------|
| Report Group Code | Yes |
| Treatment Meaning | Yes |
| Test Group | Yes |
| Tactic ID | Yes |
| Treatment Start Date | Yes |
| Channel | Yes |
| Account # | Yes |
| Client # | Yes |
| Additional Detail (JSON) | Yes (150Byte field) |

### What NEEDS TO BE BUILT (Experiment Metadata table)

| Field | Status |
|-------|--------|
| Experiment Name | To be created |
| Experiment Type | To be created |
| Test Purpose | To be created |
| Hypothesis | To be created |
| Lift / Impact Type | To be created |
| Measurement Method | To be created |
| "Active between Dates" | To be created |

**Note from slide:** "Leveraging the four contextual fields is enough to identify majority of the experiments as of today. However, does not work for complex campaigns."

---

## Layer 2: Managed Campaign Metadata (Mnemonic Mapping v2)

**Question:** "What to measure?"

### Source that EXISTS today
- `DTZTAU.CIDM_MNEMONIC_ATTRS`

### Fields that EXIST

| Field | Exists? |
|-------|---------|
| Campaign Description | Yes |
| LOB | Yes |
| Campaign Category (Fulfillment/Regulatory) | Yes |
| Control Exemption | Yes |
| Measurement Category (Measurable, Operational) | Yes |

### Fields that NEED TO BE ADDED (Enhancements)

| Field | Status |
|-------|--------|
| Primary Metric | To be added |
| Secondary Metric | To be added |
| Tertiary Metric | To be added |
| Action / Sub-Action Type | To be added |
| Client Mindset / Continuum | To be added |
| CTA | To be added |
| Frequency | To be added |
| Model | To be added |

**What Layer 2 produces:** The mapping of Campaign → which metrics to use (links to Layer 3)

---

## Layer 3: Centralized Logic Repo (Success Library)

**Question:** "How to calculate?"

### Source
GitHub repository (to be created)

### What it will GOVERN (metric categories)

#### Conversion
| Metric | Status |
|--------|--------|
| Cheque Account Opening | Logic exists somewhere, not centralized |
| Credit Card Opening | Logic exists somewhere, not centralized |
| Mortgage Funded | Logic exists somewhere, not centralized |
| Loan Approved | Logic exists somewhere, not centralized |

#### Share of Wallet
| Metric | Status |
|--------|--------|
| Glue Activities | To be defined |
| Utilization | To be defined |
| Avg Balance | To be defined |
| PAC Indicator | To be defined |
| Number of Transactions | To be defined |

#### Engagement
| Metric | Status |
|--------|--------|
| Email Unsubscribe Rate | To be defined |
| Banner View Rate | To be defined |
| Banner Dismiss Rate | To be defined |
| Number of Mobile Logins | To be defined |
| Number of Branch Visits | To be defined |

#### Retention
| Metric | Status |
|--------|--------|
| Account Closure | To be defined |
| Client Attrition | To be defined |
| Change in Products | To be defined |
| Change in Services | To be defined |

#### Profitability
| Metric | Status |
|--------|--------|
| Account Level | To be defined |
| Client Level | To be defined |

### What Layer 3 produces

`%Run Success1`, `%Run Success2`, `%Run Success3` functions containing SQL like:
```sql
SELECT SRF, Treatment Start - Change Date, Mortgage Open and Funded
FROM HEF_TABLE
```

**Current Status (from Timeline slide):** "Limited Metrics Coverage - Metrics are defined for only 40 MVP Actions. The remaining actions need to be reviewed."

---

## Layer 4: Client Marketing Interaction Journey

**Question:** "What did client actually do?"

### Sources that EXIST today

| Source | What it has |
|--------|-------------|
| `TACTIC_IP_AR_HIST` | Tactic data |
| `Master Email Vendor` | Email data |
| `RPT_PME_DSKTP` | Desktop/branch data |
| `VISA_DR_CRD` | Card issuance data |

### Fields that EXIST

| Field | Exists? |
|-------|---------|
| TACTIC | Yes |
| LOB | Yes |
| Campaign Category | Yes |
| Control Exemption | Yes |
| Measurement Category | Yes |

### Fields that NEED TO BE ADDED (Enhancements)

| Field | Status |
|-------|--------|
| Leads actions | To be added |
| Offer Details | To be added |
| Client response | To be added |
| Channel response | To be added |
| Status of applications | To be added |

**Limitation noted:** "tactic_hist only the decisions, not client who received"

---

## Data Assets PRODUCED (Downstream of 4 Layers)

From the "Extremely Critical Element" slide:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Semantic Results Layer 1                                           │
│  ├── Daily Experiment Measurement Results    ← To be built         │
│  └── Daily Campaign Measurement Results      ← To be built         │
├─────────────────────────────────────────────────────────────────────┤
│  Semantic Staging Layer                                             │
│  ├── Engagement Layer                        ← To be built         │
│  └── Cross-Sell, Share of Wallet Layer       ← To be built         │
├─────────────────────────────────────────────────────────────────────┤
│  Daily for Vintage and Dashboard Trending    ← To be built         │
├─────────────────────────────────────────────────────────────────────┤
│  Aggregated Measurement Results                                     │
│  └── MBR / QBR / PowerPack                   ← To be built         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Vision of Final Output

The end table will have:

| Source | Columns |
|--------|---------|
| Metadata | Campaign, Experiment |
| Success Library (via Mnemonic Mapping v2) | Primary, Secondary, Tertiary |
| NBA OKRs (on-by-default for all campaigns) | Attrition, 2+ Products, Engagement Score >30, New Products |
| Digital Footprint | Thumbs Up, Email Unsub |

---

## Summary: What Exists vs What's Being Built

| Layer | Data Source | EXISTS | TO BE BUILT |
|-------|-------------|--------|-------------|
| Layer 1 | tactic_evnt_hist | Raw fields (Tactic ID, Test Group, Client #, dates) | Experiment Metadata table with enriched fields |
| Layer 2 | CIDM_MNEMONIC_ATTRS | Basic campaign info (Description, LOB, Category) | Primary/Secondary/Tertiary metric mapping |
| Layer 3 | GitHub | Scattered logic in various places | Centralized repo with %Run functions |
| Layer 4 | Multiple sources | Tactic data, email vendor, card data | Unified client journey with full touchpoints |
| Output | Data Assets | Nothing centralized | All semantic layers and aggregated results |

---

## Timeline

### Current Status
- Manual Data Extraction using SAS
- No Client Marketing Interaction Journey framework
- Experiment management in Excel
- Incomplete MNE Mapping (no metrics definitions)
- Only 40 MVP Actions defined

### Intermediate (2 Quarters)
- Automated Data Pipeline
- Journey Visualization Prototype
- Centralized Experiment Tracker (Confluence)
- Enhanced MNE Mapping
- Expanded Metrics Coverage

### Long Term (3 Quarters)
- Fully Automated Metrics Dashboard
- Dynamic Client Journey Platform
- Enterprise Experimentation Hub
- Governance-Driven MNE Framework
- Comprehensive Metrics Library

---

## Tech Stack Roadmap

| Timeframe | Platform |
|-----------|----------|
| Short Term (ending Jan) | Teradata Datalab |
| Medium Term (6+ months) | Orchestration: Airflow + Dagster, Transformations: Spark SQL, AWS S3, CDA YG80 Shared Zone or UQ20 |
| Long Term (12+ months) | Spark Teradata ETL to Iceberg + Snowflake Analytics Layer, Amazon S3+Redshift, Trino/dbt where necessary |

---

## Key Insight: How Layers Connect

```
Layer 1                    Layer 2                    Layer 3
Experiment Metadata        Mnemonic Mapping v2        Success Library
       │                          │                         │
       │                          │                         │
   "Client 123                "Campaign VCN            "Card Acquisition =
    is in Test                 uses metric             STS_CD IN ('06','08')
    Group TG4"                 Card Acquisition"       AND SRVC_ID = 36"
       │                          │                         │
       └──────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                              Layer 4
                         Client Journey
                                  │
                         "Client 123 got
                          card issued on
                          Day 10"
                                  │
                                  ▼
                           Data Assets
                     (Vintage, Dashboard, MBR)
```
