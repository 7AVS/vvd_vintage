# Success Library - SuperFact Concept v2

## Slide 2: Summary

### Background

To improve measurement team's efficiency and lift the biggest bottleneck to scale; there are **four critical semantic layers** that elevate the information prior to a proper platform implementation.

1. **Governed Experiment Metadata Semantic Layer**
2. **Managed Campaign Metadata (Mnemonic Mapping v2)**
3. **Centralized Logic Repo (Success Library)**
4. **Client Marketing Interaction Journey**

### Impact Areas

1. Automation of QBR/MBR/PowerPack
2. Fast turn around on ADT Measurement and Vintages
3. Resolve MVP feedback loop
4. Skip initial ETL for deep dive / insights
5. Feed dashboards to enable quicker delivery
6. Input into Natural Language Querying/Agentic AI

### High-Level Implementation Plan

Proposal adopts a two foundational approaches:

1. Harness the **scalable processing of the Lumina PySpark** cluster
2. Leverage **SQL to extract / transform data**

> This centralized data warehouse solution remains largely **platform agnostic** and **high accessibility** for a more seamless adoption across various skill levels.

---

## Slide 3: Enhanced Experimentation Framework

**Enhanced experimentation framework: faster, clearer, traceable results**

| Dimension | Current State | Future State |
|-----------|---------------|--------------|
| **Traceability** | **No centralized tracking of in-market and past experiments** creates gaps in traceability, leading to inefficiencies and data debt for all collaborating teams | **A centralized database of all in-market and past experiments**, with additional fields regarding purpose, design, and inference method |
| **Reportability** | **Test group logic and client targeting are inconsistently stored across multiple platforms**: confluence, spreadsheets, or informal communication channels | **Consolidated additional data required for reporting is prepopulated in above database**, before deployment to assist in generating Day 1 reporting |
| **Speed to Market** | **Inconsistent methodologies, designs, and scattered documentation** result in data debt, manual reporting, and unreliable outcomes | With the experimentation framework, **the added governance on data will significantly improve the reporting and speed to market** |

---

## Slide 4: Evolving Experimentation

**Evolving experimentation: accelerating and elevating quality for faster insights**

| Dimension | Current State | Future State |
|-----------|---------------|--------------|
| **Experiment Measurement** | **Manual data transformations from E2E**: from design to report back, including identification of test population and code QA | **Automated Day 1 Reporting**: All transformations standardized and automated with experiments and success pre-determined to create daily report back for measurement and MVP |
| **Vintage and Daily Trending** | **Measurement primarily designed for end of experiment** so queries need to be adapted to be able to create daily trending | **Daily available by default** where trendlines will be available on demand and ready for dashboarding |
| **One-Pagers & Documentation** | **Due to non-standard practices in deployments and experiment designs**, documentation is scattered, inconsistent and generally not available on demand | **Test groups and experiments documented in a database** for consistency as part of the creation and deployment process |

---

## Slide 5: Tech Stack Roadmap

**Tech stack roadmap: options ranked for creating a platform for long-term vision**

| Short Term: ending Jan | Medium Term (6+ months) | Long Term (12+ months) |
|------------------------|-------------------------|------------------------|
| **1. Teradata Datalab** | **1. Orchestration: Airflow + Dagster** | **1. Spark Teradata ETL to Iceberg + Snowflake Analytics Layer** |
| | **Transformations: Spark SQL** | |
| | **2. AWS S3** | **2. Amazon S3+Redshift** |
| | **3. CDA YG80 Shared Zone or UQ20** | **+ Trino / dbt where necessary** |

---

## Slide 6: A) Source of Truth Metrics

**A Metrics Library that predefine and schedule weekly runs to ensure low latency on measurement**

### Conversion
- Cheque Account Opening
- Credit Card Opening
- Mortgage Funded
- Loan Approved
- ....

### Share of Wallet
- Glue Activities
- Utilization
- Avg Balance
- PAC Indicator
- Number of Transactions
- ....

### Engagement
- Email Unsubscribe Rate
- Banner View Rate
- Banner Dismiss Rate
- Number of Mobile Logins
- Number of Branch Visits
- ....

### Retention
- Account Closure
- Client Attrition
- Change in Products
- Change in Services
- ...

### Profitability
- Account Level
- Client Level

---

## Slide 7: B) Experiment Metadata

**B) Experiment Metadata: enhance current data to identify tests and clients**

Leverage existing data that is currently inferred to speed up and democratize experiment information

### Tactic History

| Unique Identifiers to Drive Metadata |
|--------------------------------------|
| Report Group Code |
| Treatment Meaning |
| Test Group |
| Tactic ID OR Treatment Start |

Additional fields:
- Channel
- Account #
- Client #

### Experiment Metadata
- Experiment Name
- Experiment Type
- Test Purpose
- Hypothesis
- Lift / Impact Type
- Measurement Method
- "Active between Dates"

> Leveraging the four contextual fields is enough to identify majority of the experiments as of today. However, does not work for complex campaigns.

---

## Slide 8: B) Experiment Metadata - JSON Solution

**B) Experiment Metadata: a standardized, auditable framework for documenting experimentation details**

As a mandatory standardized campaign deployment, JSON field flexibility¹ over the 150Byte will flag critical tags

### ODS Table Structure

| ODS Fields |
|------------|
| Tactic |
| Channel |
| Effective Date |
| Additional Detail ← *flexible text field* |
| Treatment Detail |

### ODS "treatment additional detail" JSON

**Client Level Experiment Metadata**

The additional tagging will link to the Experimentation Layer

```
ClientXYZ
{
"Experiments":
TestABC01_overall_test,
TestABC12_banner_challenger
}
```

| Attribute | TestABC01_overall_test | TestABC12_banner_challenger |
|-----------|------------------------|----------------------------|
| Type | Test vs Control | Champion Challenger |
| Performance | Campaign Performance | Foundational |
| Level | Campaign Level | Channel Test |
| Impact | Campaign Impact | Banner Impact |
| Method | Frequentist Causal | Frequentist Causal |

**ODS:** `ed10_im.prod_x610_crm.ods_mr_hist`

> ¹150Byte requires metadata be defined in 1 of 150 slots, while JSON offers a more modern approach by allowing variable name-value pairs anywhere

---

## Slide 9: C) Campaign Metadata Enhancements

**C) Campaign Metadata Enhancements: creating Mnemonic Mapping V2**

The managed semantic layer will classify campaigns for reporting oversight and **map** the success library

### Currently Available

- Campaign Description
- LOB
- Campaign Category:
  - Fulfillment/Regulatory
- Control Exemption
- Measurement Category
  - Measurable, Operational etc.

**Main Source:** `DTZTAU.CIDM_MNEMONIC_ATTRS`

### Enhancements

- **Primary Metric**
- **Secondary Metric**
- **Tertiary Metric**
- Action / Sub-Action Type
- Client Mindset / Continuum
- CTA
- Frequency
- Model

---

## Slide 10: C) Client Marketing Interaction Journey

**C) Client Marketing Interaction Journey:** Map end-to-end client touchpoints across channels to analyze and optimize the marketing-to-sales funnel.

The client marketing interaction journey will capture all touchpoints from decision to fulfillment, enable accurate measurement on treatment effect and funnel analysis

### Currently Available

- TACTIC
- LOB
- Campaign Category:
  - Fulfillment/Regulatory
- Control Exemption
- Measurement Category
  - Measurable, Operational etc.

**Main Source:**
- `TACTIC_IP_AR_HIST`
- `Master Email Vendor`
- `RPT_PME_DSKTP`
- ...

### Enhancements

**Create an aggregate view of leads' feedback loop**

- Leads actions
- Offer Details
- Client response
- Channel response
- Status of applications
- More accurate measurement on treatment effect

> ⚠️ Limitation of tactic_hist, only the decisions, not client who received.

---

## Slide 11: Vision of Final Data

**Vision of Final Data – automated reporting from the two metadata layers**

With the setup established appropriately, metrics beyond the usual primary or secondary will be readily available

### Table Output (Illustration Purposes):

| Metadata | | Success Library | | | | | | | | |
|----------|------------|---------|-----------|----------|-----------|-------------|------------|--------------|-----------|-------------|
| | | **Campaign Success in Mnemonic Mapping V2** | | | **NBA OKRs** (On-by-default for All Campaigns) | | | | **Digital Footprint** | |
| Campaign | Experiment | Primary | Secondary | Tertiary | Attrition | 2 or More Products | Engagement Score >30 | New Products | Thumbs Up | Email Unsub |
| **FTH:** FHSA Lead | Expansion | Mortgage Funded 4% | Application Started 6% | Appointment 10% | 1% | 30% | 40% | 0.1 | 70% | N/A |
| **MVP:** TPA Nurture | Education Value Proposition | Card Open 0.4% | N/A | N/A | 1% | 20% | 45% | 0.1 | 60% | 0.2% |

> If there is appetite, there is likely some patterns from other campaign's success measures, ex: *opening a new mortgage results in less PACs*

*All figures only for illustration purposes*

---

## Slide 12: Success Library "SuperFact"

**Success Library "SuperFact" – concept for scalability and portability**

Concept is like LEGO bricks; the connectors between dimension and fact are consistent and will have limitless joins

### Architecture Flow

```
Client Level:                          Primary           Secondary      Tertiary
Experiment Metadata         Client # → "%Run Success1"  "%Run Success2" "%Run Success3"
        +                       ↑
Campaign Metadata          Tactic ←
                                            ↓
TestABC12_banner_challenger              Success1 =
                                         SQL(
                                         Select
                                         SRF,                Daily Success1 =
                                         Mortgage            SQL(
                                         From...             Select
                                                            SRF, Treatment Start – Change Date
                                         Can aggregate      ,Mortgage Open and Funded
                                         daily version      From HEF_TABLE)
                                         to save compute
```

### Tactical Solutioning

1. **PySpark** compute and TempView Function
2. **SQL** to manage the database ETL¹
3. **GitHub** for centralized logic repository
4. **Experiment Layer** on top of client marketing interaction journey
5. **Mnemonic Mapping** to call success measure

> ¹Leveraging SQL and not PySpark querying is critical as the solution as it allows for easier transition to an experimentation platform
> Depending on how the GIT is set up, the call (or %run) function may look different.

---

## Slide 13: Impact

**Impact: Success Library is the foundational gateway to democratizing results**

Establishing the **four key semantic layers** will significantly impact many pain points and opportunities, driving **scale**, **efficiencies** and **sustainable growth** across the organization.

### Fully-Developed Success Library SuperFact enables:

- **Real time view for ADT Value Capture**
- **Faster MBR / QBR / PowerPack / Vintages**
- **Inputs for MVP feedback loop**
- **Initial ETL for Quicker Deep Dives / Insights**
- **Foundational Data to Dashboards**
- **Future Inputs to Natural Language Querying LLM**

---

## Slide 14: Timeline

### Current Status

- **Manual Data Extraction**: Metrics are currently pulled manually using SAS, which is time-consuming and prone to errors.
- **Lack of Integrated Journey Tracking**: The *Client Marketing Interaction Journey* framework does not exist, forcing reliance on *TACTIC HIST* for ad-hoc, manual analysis.
- **Fragmented Experiment Management**: Experiment status tracking and documentation are managed in Excel, leading to inconsistencies and version control issues.
- **Incomplete MNE Mapping**: The *MNE Mapping table* lacks clear metrics definitions and program details, hindering alignment and scalability.
- **Limited Metrics Coverage**: Metrics are defined for only **40 MVP Actions**. The remaining actions need to be reviewed.

### Intermediate Status (2 Quarters)

*Require Data Engineering Resource to build and schedule the pipelines*

- **Automated Data Pipeline**: Transition from manual SAS data pulls to a scheduled, automated ETL process for metrics extraction, reducing human error and time spent.
- **Journey Visualization Prototype**: Develop preliminary framework for the *Client Marketing Interaction Journey* using historical TACTIC HIST data, enabling basic path analysis.
- **Centralized Experiment Tracker**: Migrate Excel-based experiment documentation to a collaborative platform (e.g., Confluence) with version control and stakeholder access.
- **Enhanced MNE Mapping**: Update the MNE Mapping table to include standardized metrics definitions and high-level program details, ensuring alignment across teams.
- **Expanded Metrics Coverage**: Extend metrics definitions beyond 40 MVP Actions to all actions, with clear version control and validation protocols.

### Long Term Status (3 Quarters)

*Require Data Engineering, BI Resource, and dedicate person to manage data pipeline, dashboards, and tracking for ADT*

- **Fully Automated Metrics Dashboard**: Implement a real-time Tableau dashboard pulling data from automated pipelines, to visualize Metrics and Vintages.
- **Dynamic Client Journey Platform**: Launch an interactive tool mapping the *Client Marketing Interaction Journey*, integrating real-time data feeds and predictive analytics.
- **Enterprise Experimentation Hub**: Establish a centralized system (e.g., Experimentation Management Platform) for end-to-end experiment tracking, including hypothesis logging, results, and ROI analysis.
- **Governance-Driven MNE Framework**: Finalize a governed MNE Mapping table with metrics definitions, program details, and audit trails, integrated into broader marketing operations.
- **Comprehensive Metrics Library**: Define metrics for all critical marketing actions (targeting 100% of high-impact activities), with documentation and training for cross-functional teams.

---

## Slide 15: Potential Hybrid PySpark+SQL Solution

```python
treatmt_strt_dt = '2025-06-01'
tactic = ['FTH', 'NOW', 'WPO']
tactic_str = "', '".join(tactic)

population_df = read_teradata("""select clnt_no, tactic_id from DGNV01.TACTIC_EVNT_IP_AR_HIST
where substr(TACTIC_ID,0,3) IN ('{tactic_str}') and treatmt_strt_dt > '{treatmt_strt_dt}'""")

fact1_df = read_teradata("""select clnt_no, tactic_id, treatmt_strt_dt as metric1 from DGNV01.TACTIC_EVNT_IP_AR_HIST
where substr(TACTIC_ID,0,3) IN ('{tactic_str}') and treatmt_strt_dt > '{treatmt_strt_dt}'""")

fact2_df = read_teradata("""select clnt_no, tactic_id, ADDNL_DECISN_DATA1 as metric2 from DGNV01.TACTIC_EVNT_IP_AR_HIST
where substr(TACTIC_ID,0,3) IN ('{tactic_str}') and treatmt_strt_dt > '{treatmt_strt_dt}'""")

# Register DataFrames as temp views
population_df.createOrReplaceTempView("population")
fact1_df.createOrReplaceTempView("fact1")
fact2_df.createOrReplaceTempView("fact2")

# Connect the Successes to the target pop
query = """
SELECT p.clnt_no, p.tactic_id, f1.metric1, f2.metric2
FROM population p
LEFT JOIN fact1 f1 ON p.clnt_no = f1.clnt_no and p.tactic_id = f1.tactic_id
LEFT JOIN fact2 f2 ON p.clnt_no = f2.clnt_no and p.tactic_id = f2.tactic_id
"""

from pyspark.sql.functions import md5, col
result_df = spark.sql(query)
result_df = result_df.withColumn("clnt_no", md5(col("clnt_no").cast("string")))

result_df.show()
```

### Key Points

- This code will come from GIT repo to ensure governance and standardization
- Aggregation logic that stays consistent and can be scheduled

### In the final solution:

1. Experimentation layer will identify population
2. Campaign layer will dictate which "success" to pull from Git

> This proposal adopts a **dual-advantage approach**: harnessing the **scalable processing** power of the Lumina PySpark cluster while maintaining SQL compatibility. This ensures **platform agnosticism**, **broad accessibility**, and reduced technical barriers for a more seamless adoption across teams.

---

*Document: Success Library - SuperFact Concept v2*
*Slides 2-15 of 15*
