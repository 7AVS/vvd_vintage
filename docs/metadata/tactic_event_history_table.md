# Tactic Event History Table Documentation

## Table Overview

**Table Name:** `TACTIC_EVNT_IP_AR_HIST` (Tactic Details Validation)

**Purpose:** This table stores client-level tactic/campaign event data including treatment assignments, experiment metadata, and client identifiers. It is a core source for the Success Library's Experiment Metadata Semantic Layer.

---

## Column Structure

### Tactic Identification Fields

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `TACTIC_EVNT_ID_TYP_CD` | 100 | Tactic event ID type code |
| `TACTIC_EVNT_SRVC_ID` | 0 | Tactic event service ID |
| `TACTIC_ID` | 20241965LC | Unique tactic identifier |
| `STRTGY_SRC_CD` | PM | Strategy source code |
| `TRGT_TYP_CD` | MO | Target type code |
| `TACTIC_ADNC_TYP_CD` | 1 | Tactic audience type code |
| `TACTIC_CELL_CD` | IM | Tactic cell code |

### Treatment & Test Group Fields

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `TREATMT_MN` | 1SLC001A | Treatment mnemonic |
| `TREATMT_EFF_DT` | 26JUN2024 | Treatment effective date |
| `TREATMT_STRT_DT` | 08JUL2024 | Treatment start date |
| `TREATMT_END` | 31OCT2024 | Treatment end date |
| `TST_GRP_CD` | TG4 | Test group code |
| `TST_GRP_EFF_DT` | 01JAN2005 | Test group effective date |
| `RPT_GRP_CD` | PSLCRG01 | Report group code |
| `RPT_GRP_EFF_DT` | 01JAN2005 | Report group effective date |

### Client & Account Identifiers

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `VISA_CLNT_SRCE_IND` | 0 | VISA client source indicator |
| `VISA_ACCT_NO` | 0 | VISA account number |
| `VISA_SRVC_ID` | 0 | VISA service ID |
| `VISA_ADJUDCN_CD` | 0 | VISA adjudication code |
| `MIF_ACCT_NO` | 20202020202020 | MIF account number (masked) |
| `MIF_SRVC_ID` | 0 | MIF service ID |
| `HOUSEHLD_ID` | 20202020202020 | Household ID (masked) |
| `HOUSEHLD_SYS_SRC_ID` | 0 | Household system source ID |
| `CARD_NO` | 400 | Card number identifier |

### MDM (Master Data Management) Fields

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `MDM_PROD_TYPE` | (null) | MDM product type |
| `MDM_BKG_PT` | (null) | MDM booking point |
| `MDM_PROD_NO` | (null) | MDM product number |

### Data Warehouse Fields

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `DW_SYS_SRC_ID` | 0 | Data warehouse system source ID |
| `DW_SRVC_ID` | 0 | Data warehouse service ID |
| `AR_ID` | 0 | AR identifier |
| `LOAD_DOWNSTRM_DEST_CD` | 611 | Load downstream destination code |

### Additional Decision Data Fields

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `ADDNL_DATA_DT` | 26JUN2024 | Additional data date |
| `ADDNL_DECISN_DATA1` | IM | Additional decision data 1 |
| `ADDNL_DECISN_DATA2` | 400 | Additional decision data 2 |
| `ADDNL_DECISN_DATA3` | 430 | Additional decision data 3 |

### Scoring & Model Fields

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `SELT_AFFINITY_MDL_SCOR` | 0.760000 | Selection affinity model score |
| `BUS_CLNT_CNTCT_ID` | 0 | Business client contact ID |
| `AMT` | 0.00 | Amount |

### Tactic Decision Verbose Info

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `TACTIC_DECISN_VRB_INFO` | Student NG: N Student SB: Y Student IR: Y Grad Date: 2018-08-01 EM Ind: N OLB Ind: Y Full_Channel: IM_MB | Verbose decision information containing targeting criteria |

### Event & Purge Fields

| Column Name | Sample Value | Description |
|-------------|--------------|-------------|
| `EVNT_STRT_DT` | 03JUL2024 | Event start date |
| `PURGE_DT` | 03JUL2029 | Purge date |
| `TSYS_CD` | 0 | TSYS code |
| `TSYS_SRC_CD` | 0 | TSYS source code |

---

## Sample Data Row

```
TACTIC_EVNT_ID_TYP_CD: 100
TACTIC_EVNT_SRVC_ID: 0
TACTIC_ID: 20241965LC
STRTGY_SRC_CD: PM
TRGT_TYP_CD: MO
TACTIC_ADNC_TYP_CD: 1
VISA_CLNT_SRCE_IND: 0
PURGE_DT: 03JUL2029
TREATMT_MN: 1SLC001A
TREATMT_EFF_DT: 26JUN2024
TACTIC_CELL_CD: IM
TST_GRP_CD: TG4
TST_GRP_EFF_DT: 01JAN2005
RPT_GRP_CD: PSLCRG01
TREATMT_STRT_DT: 08JUL2024
TREATMT_END: 31OCT2024
MIF_ACCT_NO: 20202020202020 (masked)
HOUSEHLD_ID: 20202020202020 (masked)
ADDNL_DATA_DT: 26JUN2024
ADDNL_DECISN_DATA2: 400
ADDNL_DECISN_DATA3: 430
SELT_AFFINITY_MDL_SCOR: 0.760000
LOAD_DOWNSTRM_DEST_CD: 611
```

---

## TACTIC_DECISN_VRB_INFO Field Structure

This verbose field contains targeting/eligibility criteria in a structured text format:

| Attribute | Sample Value | Meaning |
|-----------|--------------|---------|
| `Student NG` | N | Student NG indicator (Y/N) |
| `Student SB` | Y | Student SB indicator (Y/N) |
| `Student IR` | Y | Student IR indicator (Y/N) |
| `Grad Date` | 2018-08-01 | Graduation date |
| `EM Ind` | N | Email indicator (Y/N) |
| `OLB Ind` | Y | Online banking indicator (Y/N) |
| `Full_Channel` | IM_MB | Full channel designation |

**Note:** Grad dates observed range from 2016 through 2033, and some records show "N/A" for Grad Date.

---

## Key Fields for Success Library Integration

### Four Contextual Fields (Experiment Identification)

Per the Success Library architecture, these four fields serve as unique identifiers for linking experiments to clients:

1. **`RPT_GRP_CD`** (Report Group Code) — Groups related tactics/campaigns
2. **`TREATMT_MN`** (Treatment Meaning) — Describes the treatment being applied
3. **`TST_GRP_CD`** (Test Group) — Identifies test vs control assignment
4. **`TACTIC_ID`** or **`TREATMT_STRT_DT`** (Treatment Start) — Unique identifier or timestamp

### Client Linkage Fields

- `MIF_ACCT_NO` — Account-level identifier
- `HOUSEHLD_ID` — Household-level identifier
- Channel identifier via `TACTIC_CELL_CD` or `Full_Channel`

---

## Data Quality Observations

1. **Masked Values:** Client identifiers appear as repeated patterns (20202020202020) indicating masking/anonymization
2. **Null Columns:** Several MDM fields appear consistently null in sample data
3. **Date Formats:** Dates use DDMMMYYYY format (e.g., 26JUN2024)
4. **Sparse Columns:** Many ID fields show 0 values, suggesting optional population

---

## Related Tables

| Table | Relationship |
|-------|--------------|
| `DTZTAU.CIDM_MNEMONIC_ATTRS` | Campaign metadata via TREATMT_MN |
| `ed10_im.prod_x610_crm.ods_mr_hist` | ODS table with Additional Detail JSON field |
| Master Email Vendor | Channel-level exposure data |
| `RPT_PME_DSKTP` | Desktop/digital touchpoint data |

---

*Documentation based on Tactic Details Validation data extract, January 2026*
