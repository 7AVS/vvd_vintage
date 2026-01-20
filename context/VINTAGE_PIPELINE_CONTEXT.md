# Vintage Pipeline - Context Document

**Created:** January 2026
**Purpose:** Capture architecture decisions and understanding for VVD vintage curve pipeline

---

## Project Goal

Build a **modular vintage curve pipeline** for VVD (Virtual Visa Debit) campaigns that:
1. Aligns with the Success Library / SuperFact 4-layer architecture
2. Pulls from **source tables** (not user directory files)
3. Is ready to integrate with governed layers when they're built
4. Produces vintage curves, lift calculations, and visualizations

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
| chnl_cd | Channel code |
| addnl_decisn_data1/2/3 | Flexible fields |

**Current state:** Not governed. Design info lives in Word docs, Excel, PowerPoints.
**For now:** Hardcode lookup values from design documents.

---

### Layer 2: Mnemonic Mapping (Campaign Metadata)
**What it is:** One row per campaign with high-level info.

**Source table:** `dw00_im.ddwutd03.mne_mapping_table_lan`

**Contains:**
- Campaign description
- LOB
- Category
- Measurement status
- (Future V2: primary/secondary/tertiary metrics)

**For vintages:** SKIP - not critical. Used for QBR/MBR campaign-level reporting.

---

### Layer 3: Success Library
**What it is:** Governed SQL logic for each success type.

**Success types for VVD:**
| Type | Definition | Source Table | Key Fields |
|------|------------|--------------|------------|
| ACQUISITION | VVD card issued | VISA_DR_CRD | ISS_DT, STS_CD in (06,08), SRVC_ID=36 |
| ACTIVATION | VVD card activated | VISA_DR_CRD | ACTV_DT, STS_CD in (06,08), SRVC_ID=36 |
| USAGE | VVD card used | POS_TXN | TXN_DT, SRVC_CD=36, specific TXN_TP/MSG_TP |
| TOKENIZATION | Added to wallet | Token table | TXN_DT |

**Source paths:**
- VISA_DR_CRD: `/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT=`
- POS_TXN: `/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT=`
- Token: TBD (need source path)

**Current state:** Logic exists in analyst notebooks, not centralized.

---

### Layer 4: Client Marketing Interaction Journey
**What it is:** Tracks what actually HAPPENED vs what was DECISIONED.

**Components:**

| Component | Purpose | Source |
|-----------|---------|--------|
| Channel Feedback | Confirm delivery | Email feedback, Digital channels, OLB |
| Success Detection | Confirm conversion | Success Library tables |
| Fulfillment | Confirm reward delivery | Fulfillment tables |
| Demographics | Enable breakdowns | Client attributes |

**Key insight:**
> "Limitation of tactic_hist, only the decisions, not client who received."

tactic_evnt_hist captures what was DECISIONED, not what was DELIVERED. Layer 4 closes this gap.

**Example:**
```
Decisioned:     10,000 clients
Delivered:       8,500 (confirmed via email/channel feedback)
Converted:         425 (success library)
Fulfilled:         410 (reward processed)
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
├── Logic: Join clients with success outcomes
└── Output: SUCCESS_FLAG, SUCCESS_DT, DAYS_TO_SUCCESS

MODULE 4: VALIDATION (Layer 4)
├── Source: Email feedback, Digital channels, Fulfillment (RAW)
├── Output: DELIVERED_FLAG, FULFILLED_FLAG
└── Enables: Adjusted denominators, accurate measurement

MODULE 5: VINTAGE CALCULATION
├── Input: Outputs from Modules 1, 3, 4
└── Output: Cumulative rates, lift, confidence intervals

MODULE 6: VISUALIZATION
└── Plots, summaries, exports
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
4. **Modular design** - each layer is a separate component that can be swapped when governed versions are ready
5. **Reporting is separate** - the 4 layers are data foundations; reporting sits on top

---

## Current Code Location

**All-in-one file (needs refactoring):**
`/mnt/c/Users/andre/New_projects/Vintage/Vvd/code/vintage_simple/vintage_all_in_one.py`

**Modular framework (reference):**
`/mnt/c/Users/andre/New_projects/Vintage/Vvd/code/vintage_framework/`

---

## Source Table Paths Summary

| Table | Path | Status |
|-------|------|--------|
| Tactic Event History | `prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist` | Have metadata |
| ODS MR History | `ed10_im.prod_x610_crm.ods_mr_hist` | Have metadata |
| MNE Mapping | `dw00_im.ddwutd03.mne_mapping_table_lan` | Have metadata |
| VISA DR CRD | `/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/` | In code |
| POS TXN | `/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/` | In code |
| Token | TBD | Need source path |
| Email Feedback | TBD | Need from user |
| Fulfillment | TBD | Need from user |

---

## Reference Documents

| Doc | Location | Purpose |
|-----|----------|---------|
| 01_success_library_superfact_concept_v2.md | docs/ | 4-layer architecture |
| 02_experimentation_process_v1.2.md | docs/ | Experiment methodology |
| 03_experiment_design_workflow.md | docs/ | Team workflow |
| 04_pcq_email_test_onepager.md | docs/ | One-pager template |
| 05_fth_fhsa_experiment_design_report.md | docs/ | Full design example |
| 06_experiment_design_report_template.md | docs/ | Blank template |
| 07_success_library_data_assets.md | docs/ | Data flow diagram |
| ods_mr_hist_metadata.md | docs/ | ODS table schema |
| mne_mapping_table_metadata.md | docs/ | MNE mapping schema |
| tactic_evnt_hist_metadata.md | docs/ | Tactic table schema |

---

*Last updated: January 2026*
