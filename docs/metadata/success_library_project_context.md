# Success Library - SuperFact Project Context

## Purpose of This Document

This document serves as a working reference for developing standardized campaign measurement code that aligns with the future Success Library framework. It captures the architecture, constraints, and scope for building prototype code that can integrate with the governed infrastructure once it's in place.

---

## Executive Summary

The Marketing Analytics team is building a "Source of Truth" transformation initiative to standardize metrics across 200-300 active marketing campaigns. The core problem: metrics are currently defined ad-hoc per experiment in technical specification documents, with no single source that defines "here's what Cross-Sell means, here's how it's calculated" flowing consistently from design through to reporting.

The solution is a four-layer semantic architecture (Success Library / SuperFact) that governs experiment metadata, campaign metadata, calculation logic, and client journey data. This enables automated reporting, consistent metrics, and scalability.

---

## The Four Semantic Layers

### Layer 1: Governed Experiment Metadata Semantic Layer

**Purpose:** Link experiments to clients using existing data structures, enabling traceability from experiment design to client-level outcomes.

**Current Mechanism:**
The Tactic History table contains four contextual fields that serve as unique identifiers:

| Field | Description |
|-------|-------------|
| Report Group Code | Groups related tactics/campaigns |
| Treatment Meaning | Describes the treatment being applied |
| Test Group | Identifies test vs control assignment |
| Tactic ID OR Treatment Start | Unique identifier or timestamp for treatment initiation |

These fields, combined with Channel, Account #, and Client #, enable linking clients to specific experiments.

**Experiment Metadata Attributes:**
- Experiment Name
- Experiment Type
- Test Purpose
- Hypothesis
- Lift / Impact Type
- Measurement Method
- "Active between Dates" (experiment duration)

**Limitation:** The four contextual fields approach works for the majority of experiments but does not work for complex campaigns requiring more granular tagging.

**JSON Solution for Complex Campaigns:**

The ODS table (`ed10_im.prod_x610_crm.ods_mr_hist`) has legacy constraints — certain fields are limited to 150 bytes, restricting metadata to 150 predefined slots. The workaround: use the "Additional Detail" field to store JSON-formatted text.

Standard ODS fields:
- Tactic
- Channel
- Effective Date
- Additional Detail (flexible text field — no byte limit)
- Treatment Detail

JSON structure in Additional Detail:
```json
{
  "Experiments": ["TestABC01_overall_test", "TestABC12_banner_challenger"],
  "TestABC01_overall_test": {
    "type": "Test vs Control",
    "performance": "Campaign Performance",
    "level": "Campaign Level",
    "impact": "Campaign Impact",
    "method": "Frequentist Causal"
  },
  "TestABC12_banner_challenger": {
    "type": "Champion Challenger",
    "performance": "Foundational",
    "level": "Channel Test",
    "impact": "Banner Impact",
    "method": "Frequentist Causal"
  }
}
```

This approach allows tagging clients to multiple experiments with varying attributes without schema changes to the ODS table.

---

### Layer 2: Managed Campaign Metadata (Mnemonic Mapping V2)

**Purpose:** Classify campaigns for reporting oversight and map to the Success Library. This is where success metrics get formally tied to campaigns.

**Main Source Table:** `DTZTAU.CIDM_MNEMONIC_ATTRS`

**Currently Available Fields:**
- Campaign Description
- LOB (Line of Business)
- Campaign Category (Fulfillment/Regulatory)
- Control Exemption
- Measurement Category (Measurable, Operational, etc.)

**Proposed Enhancements (V2):**

| New Field | Description |
|-----------|-------------|
| Primary Metric | Main success measure for the campaign |
| Secondary Metric | Supporting success measure |
| Tertiary Metric | Additional success measure |
| Action / Sub-Action Type | Type of marketing action |
| Client Mindset / Continuum | Where client sits in the journey |
| CTA | Call to action |
| Frequency | Campaign frequency |
| Model | Targeting/propensity model used |

**Integration Point:** When a campaign is created, the Primary/Secondary/Tertiary metrics are selected from the governed Source of Truth Metrics library (see below), not defined ad-hoc. This creates traceability from campaign setup to measurement.

---

### Layer 3: Centralized Logic Repo (Success Library)

**Purpose:** GitHub-based repository containing standardized SQL/PySpark code that defines how each metric is calculated. Replaces ad-hoc analyst scripts with governed, reusable code assets.

**Concept:** Like LEGO bricks — the connectors between dimension and fact tables are consistent and enable limitless joins. Campaign metadata points to the right calculation logic via a naming convention.

**Pattern:**
```
Success1 = SQL(
  SELECT SRF, Mortgage
  FROM [source_table]
)

Daily Success1 = SQL(
  SELECT SRF, Treatment Start - Change Date, Mortgage Open and Funded
  FROM HEF_TABLE
)
```

The daily version can aggregate to save compute while maintaining consistency.

**Tactical Solutioning Components:**
1. **PySpark compute and TempView Function** — For scalable processing
2. **SQL to manage the database ETL** — For accessibility across skill levels
3. **GitHub for centralized logic repository** — Version control and governance
4. **Experiment Layer on top of client marketing interaction journey** — Links experiments to client touchpoints
5. **Mnemonic Mapping to call success measure** — Campaign metadata dictates which Success code to pull

**Why SQL over pure PySpark:** SQL allows for easier transition to an experimentation platform and broader accessibility. The hybrid approach leverages Lumina PySpark cluster for scalable processing while maintaining SQL compatibility.

---

### Layer 4: Client Marketing Interaction Journey

**Purpose:** Map end-to-end client touchpoints from decision to fulfillment, enabling accurate measurement of treatment effect and funnel analysis.

**Current Source Tables:**
- `TACTIC_IP_AR_HIST`
- Master Email Vendor
- `RPT_PME_DSKTP`

**Currently Available:**
- TACTIC
- LOB
- Campaign Category (Fulfillment/Regulatory)
- Control Exemption
- Measurement Category (Measurable, Operational, etc.)

**Proposed Enhancements:**

| Enhancement | Description |
|-------------|-------------|
| Leads actions | Track lead generation activities |
| Offer Details | Capture offer specifics |
| Client response | Record client reactions/decisions |
| Channel response | Track channel-level outcomes |
| Status of applications | Monitor application progress |
| More accurate measurement on treatment effect | Improved attribution |

**Key Limitation:** `TACTIC_HIST` only captures decisions (what was decided to send), not which client actually received the treatment. This creates a gap in measurement accuracy for treatment effects.

---

## Source of Truth Metrics Library

A predefined metrics library with scheduled weekly runs to ensure low latency on measurement. Five core pillars:

### Conversion
- Cheque Account Opening
- Credit Card Opening
- Mortgage Funded
- Loan Approved
- (additional metrics to be defined)

### Share of Wallet
- Glue Activities
- Utilization
- Avg Balance
- PAC Indicator
- Number of Transactions
- (additional metrics to be defined)

### Engagement
- Email Unsubscribe Rate
- Banner View Rate
- Banner Dismiss Rate
- Number of Mobile Logins
- Number of Branch Visits
- (additional metrics to be defined)

### Retention
- Account Closure
- Client Attrition
- Change in Products
- Change in Services
- (additional metrics to be defined)

### Profitability
- Account Level
- Client Level

**On-by-default Metrics (NBA OKRs):**
These metrics run automatically for all campaigns:
- Attrition
- 2 or More Products
- Engagement Score >30
- New Products

**Digital Footprint Metrics:**
- Thumbs Up
- Email Unsub

---

## Vision of Final Data Output

The target reporting table structure when all layers are connected:

| Column Group | Fields |
|--------------|--------|
| Metadata | Campaign, Experiment |
| Campaign Success (Mnemonic Mapping V2) | Primary, Secondary, Tertiary |
| NBA OKRs (On-by-default) | Attrition, 2+ Products, Engagement Score >30, New Products |
| Digital Footprint | Thumbs Up, Email Unsub |

**Example Row:**
| Campaign | Experiment | Primary | Secondary | Tertiary | Attrition | 2+ Products | Engagement | New Products | Thumbs Up | Email Unsub |
|----------|------------|---------|-----------|----------|-----------|-------------|------------|--------------|-----------|-------------|
| FTH: FHSA Lead | Expansion | Mortgage Funded 4% | Application Started 6% | Appointment 10% | 1% | 30% | 40% | 0.1 | 70% | N/A |
| MVP: TPA Nurture | Education Value Proposition | Card Open 0.4% | N/A | N/A | 1% | 20% | 45% | 0.1 | 60% | 0.2% |

**Cross-Campaign Patterns:** With this structure, patterns can emerge across campaigns (e.g., "opening a new mortgage results in fewer PACs").

---

## Current State vs Future State

### Traceability

| Current State | Future State |
|---------------|--------------|
| No centralized tracking of in-market and past experiments | Centralized database of all in-market and past experiments |
| Gaps in traceability leading to inefficiencies | Additional fields for purpose, design, and inference method |
| Data debt for all collaborating teams | Full lineage from experiment design to results |

### Reportability

| Current State | Future State |
|---------------|--------------|
| Test group logic and client targeting stored inconsistently | Consolidated data required for reporting prepopulated |
| Scattered across Confluence, spreadsheets, informal channels | Prepopulated in database before deployment |
| Manual hunting for documentation | Day 1 reporting enabled |

### Speed to Market

| Current State | Future State |
|---------------|--------------|
| Inconsistent methodologies and designs | Governance on data improves reporting speed |
| Scattered documentation | Standardized framework |
| Manual reporting and unreliable outcomes | Reliable, automated outcomes |

### Experiment Measurement

| Current State | Future State |
|---------------|--------------|
| Manual data transformations end-to-end | Automated Day 1 Reporting |
| From design to report back requires manual intervention | All transformations standardized and automated |
| Identification of test population and code QA done manually | Experiments and success pre-determined |
| | Daily report back for measurement and MVP |

### Vintage and Daily Trending

| Current State | Future State |
|---------------|--------------|
| Measurement primarily designed for end of experiment | Daily available by default |
| Queries need adaptation for daily trending | Trendlines available on demand |
| | Ready for dashboarding |

### One-Pagers and Documentation

| Current State | Future State |
|---------------|--------------|
| Non-standard practices in deployments and experiment designs | Test groups and experiments documented in database |
| Documentation scattered, inconsistent | Part of creation and deployment process |
| Generally not available on demand | Consistent and accessible |

---

## Tech Stack Roadmap

### Short Term (Ending January)
- **Platform:** Teradata Datalab
- **Status:** Working within existing infrastructure

### Medium Term (6+ Months)
Three parallel tracks:

1. **Orchestration & Transformation**
   - Airflow + Dagster for orchestration
   - Spark SQL for transformations

2. **Storage**
   - AWS S3

3. **Shared Zones**
   - CDA YG80 Shared Zone
   - OR UQ20

### Long Term (12+ Months)

1. **Primary Path**
   - Spark Teradata ETL to Iceberg + Snowflake Analytics Layer

2. **Alternative Path**
   - Amazon S3 + Redshift

3. **Additional Tooling**
   - Trino / dbt where necessary

**Design Principle:** Build on existing infrastructure (Teradata) but architect for portability to cloud-native tooling without rewriting everything. The solution remains platform agnostic with high accessibility for seamless adoption across skill levels.

---

## Timeline and Milestones

### Current Status
- **Manual Data Extraction:** Metrics pulled manually using SAS, time-consuming and error-prone
- **Lack of Integrated Journey Tracking:** Client Marketing Interaction Journey framework does not exist, forcing reliance on TACTIC_HIST for ad-hoc manual analysis
- **Fragmented Experiment Management:** Experiment status tracking and documentation managed in Excel, leading to inconsistencies and version control issues
- **Incomplete MNE Mapping:** The MNE Mapping table lacks clear metrics definitions and program details, hindering alignment and scalability
- **Limited Metrics Coverage:** Metrics defined for only 40 MVP Actions. Remaining actions need to be reviewed.

### Intermediate Status (2 Quarters)
*Requires Data Engineering Resource to build and schedule the pipelines*

- **Automated Data Pipeline:** Transition from manual SAS data pulls to scheduled, automated ETL process for metrics extraction, reducing human error and time spent
- **Journey Visualization Prototype:** Develop preliminary framework for the Client Marketing Interaction Journey using historical TACTIC HIST data, enabling basic path analysis
- **Centralized Experiment Tracker:** Migrate Excel-based experiment documentation to a collaborative platform (e.g., Confluence) with version control and stakeholder access
- **Enhanced MNE Mapping:** Update the MNE Mapping table to include standardized metrics definitions and high-level program details, ensuring alignment across teams
- **Expanded Metrics Coverage:** Extend metrics definitions beyond 40 MVP Actions to all actions, with clear version control and validation protocols

### Long Term Status (3 Quarters)
*Requires Data Engineering, BI Resource, and dedicated person to manage data pipeline, dashboards, and tracking for ADT*

- **Fully Automated Metrics Dashboard:** Implement a real-time Tableau dashboard pulling data from automated pipelines to visualize Metrics and Vintages
- **Dynamic Client Journey Platform:** Launch an interactive tool mapping the Client Marketing Interaction Journey, integrating real-time data feeds and predictive analytics
- **Enterprise Experimentation Hub:** Establish a centralized system (e.g., Experimentation Management Platform) for end-to-end experiment tracking, including hypothesis logging, results, and ROI analysis
- **Governance-Driven MNE Framework:** Finalize a governed MNE Mapping table with metrics definitions, program details, and audit trails, integrated into broader marketing operations
- **Comprehensive Metrics Library:** Define metrics for all critical marketing actions (targeting 100% of high-impact activities), with documentation and training for cross-functional teams

---

## Impact Areas

The fully-developed Success Library (SuperFact) enables:

1. **Real-time view for ADT Value Capture** — Immediate visibility into campaign performance
2. **Faster MBR / QBR / PowerPack / Vintages** — Automated recurring reports
3. **Inputs for MVP feedback loop** — Data-driven iteration on campaigns
4. **Initial ETL for Quicker Deep Dives / Insights** — Skip manual data prep
5. **Foundational Data to Dashboards** — Direct feed to visualization layer
6. **Future Inputs to Natural Language Querying LLM** — If metadata is clean, an LLM could query it directly

---

## Hybrid PySpark + SQL Solution Pattern

The final solution adopts a dual-advantage approach:

**Code Structure:**
```python
treatmt_strt_dt = '2025-06-01'
tactic = ['FTH', 'NOW', 'WPO']
tactic_str = "', '".join(tactic)

# Read population from Teradata
population_df = read_teradata("""
    SELECT clnt_no, tactic_id 
    FROM DGNV01.TACTIC_EVNT_IP_AR_HIST
    WHERE substr(TACTIC_ID,0,3) IN ('{tactic_str}') 
    AND treatmt_strt_dt > '{treatmt_strt_dt}'
""")

# Read metric facts from Teradata
fact1_df = read_teradata("""
    SELECT clnt_no, tactic_id, treatmt_strt_dt AS metric1 
    FROM DGNV01.TACTIC_EVNT_IP_AR_HIST
    WHERE substr(TACTIC_ID,0,3) IN ('{tactic_str}') 
    AND treatmt_strt_dt > '{treatmt_strt_dt}'
""")

fact2_df = read_teradata("""
    SELECT clnt_no, tactic_id, ADDNL_DECISN_DATA1 AS metric2 
    FROM DGNV01.TACTIC_EVNT_IP_AR_HIST
    WHERE substr(TACTIC_ID,0,3) IN ('{tactic_str}') 
    AND treatmt_strt_dt > '{treatmt_strt_dt}'
""")

# Register DataFrames as temp views
population_df.createOrReplaceTempView("population")
fact1_df.createOrReplaceTempView("fact1")
fact2_df.createOrReplaceTempView("fact2")

# SQL query to join and aggregate
query = """
    SELECT p.clnt_no, p.tactic_id, f1.metric1, f2.metric2
    FROM population p
    LEFT JOIN fact1 f1 ON p.clnt_no = f1.clnt_no AND p.tactic_id = f1.tactic_id
    LEFT JOIN fact2 f2 ON p.clnt_no = f2.clnt_no AND p.tactic_id = f2.tactic_id
"""

from pyspark.sql.functions import md5, col
result_df = spark.sql(query)
result_df = result_df.withColumn("clnt_no", md5(col("clnt_no").cast("string")))

result_df.show()
```

**Key Principles:**
1. **Code comes from GIT repo** — Ensures governance and standardization
2. **Aggregation logic stays consistent** — Can be scheduled
3. **Experimentation layer identifies population** — Who is in the test
4. **Campaign layer dictates which "success" to pull from Git** — What to measure

**Why This Approach:**
- Harnesses the scalable processing power of the Lumina PySpark cluster
- Maintains SQL compatibility for platform agnosticism
- Ensures broad accessibility across skill levels
- Reduces technical barriers for seamless adoption across teams

---

# CURRENT SCOPE: Prototype Implementation

## Objective

Build standardized campaign measurement code for 6-8 campaigns that aligns with the future Success Library framework, even though the infrastructure doesn't exist yet. The code should be structured so it can plug into the governed infrastructure when available, rather than being thrown away.

## What Is Available

| Resource | Status |
|----------|--------|
| Jupyter + PySpark | ✅ Available |
| Access to source data (e.g., visa debit activation tables) | ✅ Available |
| Tech specs for campaigns with success metrics defined | ✅ Available |
| Existing standardization patterns from prior work | ✅ Available |
| Hive/Hadoop shared zone | ✅ Available |

## What Is Not Available

| Resource | Status |
|----------|--------|
| Curated data layer / Success Library | ❌ Not yet built |
| Snowflake or modern tooling | ❌ Not accessible |
| Mnemonic Mapping V2 structure | ❌ Not yet implemented |
| GitHub-based centralized logic repo | ❌ Not yet established |
| Dashboard team access to Hive | ❌ They only have SAS/SQL |

## Workflow Being Built

```
Tech Spec (design)
    ↓
    Success metrics defined per campaign
    ↓
Source Data (e.g., visa debit activation)
    ↓
    Pull from raw tables (no curated layer yet)
    ↓
Success Metric Calculations
    ↓
    PySpark code in Jupyter
    ↓
Vintage Curves
    ↓
    Analysis output
    ↓
Dashboard [HANDOFF GAP]
    ↓
    Requires intermediate output for dashboard team
    ↓
Tableau
```

## Handoff Gap: Dashboard Integration

**The Problem:**
- Your workflow: PySpark in Jupyter → Hive/Hadoop shared zone → vintage curves and analysis
- Dashboard team's workflow: SAS/SQL → Tableau
- They cannot read from Hive

**Current Workaround:**
Two separate code artifacts required:
1. Deep dive analysis code (PySpark, full complexity)
2. Simplified extract for dashboard team (output format they can consume via SAS/SQL)

**Status:** Pending verification. The dashboard team may be adopting new tools, but this is unconfirmed.

## Code Structure Principles

To align with the future state, the prototype code should:

1. **Separate population identification from metric calculation** — Mirrors the Experimentation Layer / Success Library split
2. **Use TempViews and SQL for aggregation** — Ensures portability to future SQL-based platforms
3. **Parameterize campaign/tactic identifiers** — Allows same code pattern to be reused across campaigns
4. **Document success metric definitions clearly** — These should map to the future Mnemonic Mapping V2 structure
5. **Structure output tables consistently** — Column naming and structure should anticipate the final data vision (Campaign, Experiment, Primary, Secondary, Tertiary, etc.)

## Campaigns in Scope

| Campaign | Product | Success Metrics | Status |
|----------|---------|-----------------|--------|
| (To be populated) | | | |
| (To be populated) | | | |
| (To be populated) | | | |
| (To be populated) | | | |
| (To be populated) | | | |
| (To be populated) | | | |

---

## Metric Definition Template

For each success metric, document the following attributes:

| Attribute | Description |
|-----------|-------------|
| Metric Name | Governed name (e.g., "Credit Card Opening") |
| Metric ID | Unique identifier |
| Pillar | Conversion / Share of Wallet / Engagement / Retention / Profitability |
| Business Definition | Plain language description of what it measures |
| Calculation Logic | SQL/PySpark code or formula |
| Source Table(s) | Where the raw data comes from |
| Grain | Client level / Account level / Transaction level |
| Frequency | Daily / Weekly / Monthly / End of experiment |
| Owner | Who is responsible for the definition |
| Version | For tracking changes |

---

## Open Questions

1. What is the exact process for new campaign setup? Who defines success metrics in the tech spec, and what template do they use?
2. How will the JSON experiment tagging be implemented? Is there a process for populating the Additional Detail field?
3. What validation is needed before the dashboard handoff gap can be resolved?
4. Which 40 MVP Actions currently have defined metrics? Is there a reference list?
5. What is the timeline for Data Engineering resources to build the automated pipelines?

---

## References

- Success Library - SuperFact Concept v2 (15-slide deck)
- ODS Table: `ed10_im.prod_x610_crm.ods_mr_hist`
- Mnemonic Attributes Table: `DTZTAU.CIDM_MNEMONIC_ATTRS`
- Tactic History Sources: `TACTIC_IP_AR_HIST`, `DGNV01.TACTIC_EVNT_IP_AR_HIST`
- Email/Digital Sources: Master Email Vendor, `RPT_PME_DSKTP`

---

*Document created: January 2026*
*Last updated: [Date]*
*Author: Marketing Analytics Team*
