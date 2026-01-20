# Vintage Pipeline - Context Document

**Created:** January 2026
**Purpose:** Capture architecture decisions and understanding for VVD vintage curve pipeline

---

## Project Goal

Build a **modular vintage curve pipeline** for VVD campaigns that:
1. Aligns with the Success Library / SuperFact 4-layer architecture
2. Pulls from **source tables** (not user directory files)
3. Is ready to integrate with governed layers when they're built
4. Produces vintage curves, lift calculations, and visualizations

---

## Two Versions Conceptually

| Version | Description |
|---------|-------------|
| **Future (Ideal)** | Pull from curated Layer 1 tables, governed Success Library |
| **Today (Practical)** | Hardcode lookup values, go to source tables, calculate manually |

We are building the pipeline **as if** the governed layers exist, but with hardcoded placeholders that will be replaced when the layers are built.

---

## The 4 Layers (Success Library Architecture)

### Layer 1: Experiment Metadata
**What it is:** The experiment design documentation - contains EVERYTHING about a campaign test.

**Contains:**
- Population definition (who is targeted)
- Segments (RPT_GRP_CD meanings)
- Treatment codes and their meanings
- Channels
- Exclusions
- Success metrics / hypothesis
- Expected lift
- Models used

**Source tables:**
- `prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist`
- `ed10_im.prod_x610_crm.ods_mr_hist`

**Key fields from tactic_evnt_hist:**
| Field | Purpose |
|-------|---------|
| tactic_id | Campaign identifier |
| tactic_evnt_id | Client linkage |
| rpt_grp_cd | Segment grouping |
| tst_grp_cd | Test vs Control assignment |
| treatmt_mn | Treatment description |
| treatmt_strt_dt | Treatment start date |
| treatmt_end_dt | Treatment end date |
| tactic_cell_cd | Tactic cell code |
| addnl_decisn_data1/2/3 | Flexible fields |

**Current state:** Not governed. Design info lives in Word docs, Excel, PowerPoints.
**For now:** Hardcode lookup values from design documents.
**Pending:** Find a rich campaign with multiple channels, segments, models, success metrics to use as example.

---

### Layer 2: Mnemonic Mapping (Campaign Metadata)
**What it is:** One row per campaign with high-level info.

**Source table:** `dw00_im.ddwutd03.mne_mapping_table_lan`

**For vintages:** SKIP - not critical. Used for QBR/MBR campaign-level reporting.

---

### Layer 3: Success Library
**What it is:** Governed SQL logic for each success type.

**Success types for VVD:**
| Type | Definition | Source Table | Access |
|------|------------|--------------|--------|
| ACQUISITION | VVD card issued | VISA_DR_CRD | Hive/Spark |
| ACTIVATION | VVD card activated | VISA_DR_CRD | Hive/Spark |
| USAGE | VVD card used | POS_TXN | Hive/Spark |
| TOKENIZATION | Added to wallet | CLNT_CRD_POS_LOG + TOKEN_LIST | **EDW cursor** |

---

### Layer 4: Client Marketing Interaction Journey
**What it is:** Tracks what actually HAPPENED vs what was DECISIONED.

**Components:**
| Component | Purpose | Source Tables | Access |
|-----------|---------|---------------|--------|
| Email Feedback | Confirm email delivery | VENDOR_FEEDBACK_MASTER + EVENT | Teradata |
| Fulfillment | Confirm reward delivery | TACTIC_EVNT_IP_AR_HIST | Teradata |
| Other Channels | Banner, OLB, etc. | TBD | TBD |

**Key insight:** tactic_evnt_hist captures DECISIONED, not DELIVERED. Layer 4 closes this gap.

---

## Source Table Paths Summary

**Note:** All data is in the same data warehouse. Access methods:
- **Hive tables** → `spark.read` or `spark.sql()`
- **EDW tables** → `EDW.cursor()` (already available in Lumina, no connection code needed)

| Table | Path/Schema | Access | Status |
|-------|-------------|--------|--------|
| Tactic Event History | `prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist` | Spark | Have metadata |
| ODS MR History | `ed10_im.prod_x610_crm.ods_mr_hist` | Spark | Have metadata |
| MNE Mapping | `dw00_im.ddwutd03.mne_mapping_table_lan` | Spark | Have metadata |
| VISA DR CRD | `/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/` | Spark | In code |
| POS TXN | `/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/` | Spark | In code |
| Token/Provisioning | `DDWV05.CLNT_CRD_POS_LOG` + `DL_DECMAN.TOKEN_LIST` | EDW.cursor() | Have logic |
| Email Feedback | `DTZV01.VENDOR_FEEDBACK_MASTER` + `DTZV01.VENDOR_FEEDBACK_EVENT` | EDW.cursor() | Have logic |
| Fulfillment | `DG6V01.TACTIC_EVNT_IP_AR_HIST` | EDW.cursor() | Have logic |

---

## Layer 3 & 4 Source Logic Details

### Token/Wallet Provisioning (Layer 3 - TOKENIZATION success)
**Access:** EDW cursor (not available in Hive/EDL)
```sql
SELECT DISTINCT
    SUBSTR(B.CLNT_CRD_NO, 7, 9) AS CLNT_NO,
    B.TXN_DT
FROM DDWV05.CLNT_CRD_POS_LOG AS B
INNER JOIN DL_DECMAN.TOKEN_LIST C ON B.TOKN_REQSTR_ID = C.TOKEN_ID
WHERE B.AMT1 = 0
    AND SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190'
    AND SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'
    AND SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0'
    AND B.POS_ENTR_MODE_CD_NON_EMV = '000'
    AND B.SRVC_CD = 36
    AND C.TOKEN_WALLET_IND = 'Y'
```

### Email Feedback (Layer 4 - Channel Validation)
**Access:** Teradata
**Disposition codes:** 1=sent, 2=opened, 3=clicked, 4=unsubscribed, 5=hardbounce
```sql
SELECT DISTINCT
    FEEDBACK_MASTER.TREATMENT_ID,
    FEEDBACK_MASTER.CLNT_NO,
    Max(CASE WHEN disposition_cd=1 THEN 1 ELSE 0 END) AS email_sent,
    Max(CASE WHEN disposition_cd=2 THEN 1 ELSE 0 END) AS email_opened,
    Max(CASE WHEN disposition_cd=3 THEN 1 ELSE 0 END) AS email_clicked,
    Max(CASE WHEN disposition_cd=4 THEN 1 ELSE 0 END) AS email_unsubscribed,
    Max(CASE WHEN disposition_cd=5 THEN 1 ELSE 0 END) AS email_hardbounce
    -- dates also available
FROM DTZV01.VENDOR_FEEDBACK_MASTER FEEDBACK_MASTER
INNER JOIN DTZV01.VENDOR_FEEDBACK_EVENT FEEDBACK_EVENT
    ON FEEDBACK_MASTER.consumer_id_hashed = FEEDBACK_EVENT.consumer_id_hashed
    AND FEEDBACK_MASTER.TREATMENT_ID = FEEDBACK_EVENT.TREATMENT_ID
WHERE FEEDBACK_MASTER.TREATMENT_ID IN (...)
GROUP BY 1,2
```

### Fulfillment (Layer 4 - Reward Validation)
**Access:** Teradata
```sql
SELECT
    CLNT_NO,
    AMT AS fflmnt_amt,
    ADDNL_DATA_DT AS fflmnt_dt
FROM DG6V01.TACTIC_EVNT_IP_AR_HIST
WHERE tactic_id LIKE '2025%120'  -- pattern varies by campaign
```

---

## Modular Pipeline Design

```
MODULE 1: EXPERIMENT METADATA (Layer 1)
├── Source: tactic_evnt_hist (RAW)
├── Output: Client list + RPT_GRP_CD + TST_GRP_CD + treatment window
├── Current: Hardcode lookup from design docs
└── Future: Pull from governed Layer 1 table

MODULE 2: SKIP (Layer 2 not needed for vintages)

MODULE 3: SUCCESS CAPTURE (Layer 3)
├── Source: VISA_DR_CRD, POS_TXN, Token (RAW)
├── Note: Token requires EDW cursor, not Spark
├── Logic: Join clients with success outcomes
└── Output: SUCCESS_FLAG, SUCCESS_DT, DAYS_TO_SUCCESS

MODULE 4: VALIDATION (Layer 4)
├── Source: Email feedback, Fulfillment (Teradata)
├── Output: DELIVERED_FLAG, FULFILLED_FLAG
└── Enables: Adjusted denominators, accurate measurement

MODULE 5: VINTAGE CALCULATION
├── Input: Outputs from Modules 1, 3, 4
└── Output: Cumulative rates, lift, confidence intervals

MODULE 6: VISUALIZATION
└── Plots, summaries, exports

REPORTING (Separate from layers)
└── Sits on TOP of the 4 layers - consumes their outputs
```

---

## VVD Campaigns

| MNE | Campaign Name | Success Type | Deployment |
|-----|---------------|--------------|------------|
| VCN | VVD Contextual Notification | ACQUISITION | Trigger |
| VDA | VVD Black Friday Cyber Monday | ACQUISITION | Batch |
| VDT | VVD Activation Trigger | ACTIVATION | Trigger |
| VUI | VVD Usage Trigger | USAGE | Trigger |
| VUT | VVD Tokenization Usage | TOKENIZATION | Trigger |
| VAW | VVD Add To Wallet | TOKENIZATION | Trigger |

---

## Key Decisions Made

1. **Experiment Design doc is the source of truth** - contains everything for a campaign test
2. **Skip Layer 2** for vintage building - it's for QBR/MBR, not client-level analysis
3. **Pull from source tables** - not user directory files
4. **Modular design** - each layer is a separate component
5. **Two versions** - ideal (governed) and practical (hardcoded)
6. **Reporting is separate** - not a 5th layer, sits on top of the foundation

---

## Current Code Location

**All-in-one file (needs refactoring):**
`/mnt/c/Users/andre/New_projects/Vintage/Vvd/code/vintage_simple/vintage_all_in_one.py`

---

## Reference Documents

| Doc | Purpose |
|-----|---------|
| 01-07 md files | Success Library architecture |
| ods_mr_hist_metadata.md | ODS table schema |
| mne_mapping_table_metadata.md | MNE mapping schema |
| tactic_evnt_hist_metadata.md | Tactic table schema |
| provisioning_email_fulfilment_success_metric.md | Token, Email, Fulfillment logic |

---

*Last updated: January 2026*
