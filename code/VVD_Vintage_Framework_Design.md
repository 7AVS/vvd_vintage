# VVD Vintage Curve Framework - Architecture & Design Document

## 1. Objective

Build a scalable, reproducible framework to generate **vintage curves** for VVD campaigns. The framework should:

- Support multiple campaign types with different success metrics
- Handle different measurement windows
- Allow easy addition of new campaigns
- Produce consistent, auditable outputs

---

## 1.1 UNIVERSAL STANDARDS

These rules apply to ALL campaigns - no exceptions, no customization:

| Rule | Standard | Rationale |
|------|----------|-----------|
| **Aggregation Level** | MONTH (yyyy-MM) | Never weekly/daily - keeps plots readable |
| **Plot Structure** | One plot per campaign | Simple, one artifact per MNE |
| **Test vs Control** | Same plot, same color | Solid = Test, Dashed = Control |
| **Measurement Window** | TREATMT_END_DT - TREATMT_STRT_DT | Dynamic per deployment |
| **Test Group** | TST_GRP_CD = 'TG4' | All others = Control |

---

## 2. Campaign Definitions

### 2.1 Campaign Summary

| MNE | Campaign Name | Goal | Deployment Type | Measurement Window |
|-----|---------------|------|-----------------|-------------------|
| VCN | VVD Contextual Notification | Acquisition | Trigger (monthly) | TREATMT_END_DT - TREATMT_STRT_DT |
| VDA | VVD Black Friday Cyber Monday Targeted | Acquisition | Batch (seasonal/yearly) | TREATMT_END_DT - TREATMT_STRT_DT |
| VDT | VVD Activation Trigger | Activation | Trigger (with 15-day reminder) | TREATMT_END_DT - TREATMT_STRT_DT |
| VUI | VVD Usage Trigger | Usage/Engagement | Trigger | TREATMT_END_DT - TREATMT_STRT_DT |
| VUT | VVD Tokenization Usage Campaign | Tokenization/Usage | Trigger | TREATMT_END_DT - TREATMT_STRT_DT |
| VAW | VVD Add To Wallet Contextual Notification | Tokenization | Trigger | TREATMT_END_DT - TREATMT_STRT_DT |

### 2.2 Campaign Characteristics

**Trigger vs Batch:**
- **Trigger campaigns** (VCN, VDT): Recurring deployments (monthly/weekly), many cohorts, clients may appear in multiple cohorts (no rest period)
- **Batch campaigns** (VDA): One-off or seasonal, fewer cohorts, longer measurement windows

**Cohort Definition:**
- Each deployment (`TREATMT_STRT_DT`) = one cohort/wave
- Cohorts labeled as `yyyy-MM` format for readability

---

## 3. Success Metrics by Campaign Type

### 3.1 Success Configuration Table

| MNE | SUCCESS_TYPE | SUCCESS_TABLE | SUCCESS_DATE_FIELD | WINDOW | FILTERS |
|-----|--------------|---------------|--------------------|--------------|--------------------|
| VCN | ACQUISITION | DDWTA_VISA_DR_CRD | ISS_DT | TREATMT_END_DT - TREATMT_STRT_DT | STS_CD in [06,08], SRVC_ID=36, ISS_DT not null |
| VDA | ACQUISITION | DDWTA_VISA_DR_CRD | ISS_DT | TREATMT_END_DT - TREATMT_STRT_DT | STS_CD in [06,08], SRVC_ID=36, ISS_DT not null |
| VDT | ACTIVATION | DDWTA_VISA_DR_CRD | ACTV_DT | TREATMT_END_DT - TREATMT_STRT_DT | STS_CD in [06,08], SRVC_ID=36, ISS_DT not null |
| VUI | USAGE | DDWTA_T_PT_OF_SALE_TXN | TXN_DT | TREATMT_END_DT - TREATMT_STRT_DT | Complex (see below) |
| VUT | TOKENIZATION | TOKEN join (EDW) | TXN_DT | TREATMT_END_DT - TREATMT_STRT_DT | See EDW query |
| VAW | TOKENIZATION | TOKEN join (EDW) | TXN_DT | TREATMT_END_DT - TREATMT_STRT_DT | See EDW query |

### 3.2 Success Definitions

**ACQUISITION (VCN, VDA):**
- Success = New Visa Virtual Debit card **issued** to the client
- Field: `ISS_DT` (issue date)
- Source: `DDWTA_VISA_DR_CRD`
- Filters:
  - `STS_CD IN ('06', '08')` - Valid status codes
  - `SRVC_ID = 36` - Service ID for VVD
  - `ISS_DT IS NOT NULL` - Must have issue date
- Card Type classification: `VISA_DR_CRD_BRND_CD = '03'` → Digital, else Hybrid/Plastic

**ACTIVATION (VDT):**
- Success = Card **activated** by the client
- Field: `ACTV_DT` (activation date)
- Source: `DDWTA_VISA_DR_CRD`
- Filters: Same as Acquisition
- Note: Campaign sends reminder at day 15 if no response

**USAGE (VUI):**
- Success = Client makes a **purchase transaction** with their VVD card
- Field: `TXN_DT` (transaction date)
- Source: `DDWTA_T_PT_OF_SALE_TXN`
- Filters:
  - `SRVC_CD = 36` - Service code for VVD
  - Transaction type combinations (purchase transactions):
    - `(TXN_TP = 10 AND MSG_TP = '0210')` OR
    - `(TXN_TP = 13 AND MSG_TP = '0210')` OR
    - `(TXN_TP = 12 AND MSG_TP = '0220')`
  - `AMT1 > 0` - Positive transaction amount
- CLNT_NO extraction: `regexp_replace(substring(CLNT_CRD_NO, 7, 9), '^0+', '')`
- POS_MODE extraction: `substring(POS_ENTRY_MODE_CD_NON_EMV, 1, 2)`

**TOKENIZATION (VUT, VAW):**
- Success = Card **provisioned to digital wallet** (Apple Pay, Google Pay, etc.)
- Source: `DDWV05.CLNT_CRD_POS_LOG` joined with `DL_DECMAN.TOKEN_LIST`
- EDW Query:
```sql
SELECT DISTINCT
    SUBSTR(B.CLNT_CRD_NO, 7, 9) AS CLNT_NO,
    B.TXN_DT
FROM DDWV05.CLNT_CRD_POS_LOG AS B
INNER JOIN DL_DECMAN.TOKEN_LIST C
    ON B.TOKN_REQSTR_ID = C.TOKEN_ID
WHERE B.AMT1 = 0
    AND SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190'
    AND SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'
    AND SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0'
    AND B.POS_ENTR_MODE_CD_NON_EMV = '000'
    AND B.SRVC_CD = 36
    AND C.TOKEN_WALLET_IND = 'Y'
```

---

## 4. Data Sources

### 4.1 Campaign Deployments (Tactic)

- **Source**: `/user/427966379/tactic.parquet`
- **Original Table**: `DTZTA_T_TACTIC_EVNT_HIST`
- **Key Fields**: 
  - `CLNT_NO` - Client identifier (via bus_clnt_cntct_id)
  - `TACTIC_ID` - Deployment identifier
  - `TREATMT_STRT_DT` - Treatment start date (defines cohort start)
  - `TREATMT_END_DT` - Treatment end date (defines measurement window)
  - `TREATMT_EFF_DT` - Treatment effective date
  - `MNE` - Campaign code (via treatmt_mn)
  - `CAMPAIGN_NAME` - Campaign name
  - `CHANNEL` - Deployment channel
  - `TST_GRP_CD` - Test group code (TG4 = Test/Action, others = Control)
  - `TST_GRP_EFF_DT` - Test group effective date
  - `RPT_GRP_CD` - Reporting group code (for custom segmentation)
  - `RPT_GRP_EFF_DT` - Reporting group effective date
  - `TACTIC_CELL_CD` - Tactic cell code
  - `STRTGY_SRC_CD` - Strategy source code
  - `TRGT_TYP_CD` - Target type code

### 4.2 Success Tables

**DDWTA_VISA_DR_CRD** (Acquisition & Activation):
- Path: `/prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/PartitionColumn=Latest/CAPTR_DT={year}*`
- Key Fields: `CLNT_NO`, `ISS_DT`, `ACTV_DT`

**DDWTA_T_PT_OF_SALE_TXN** (Usage):
- Path: `/prod/sz/tsz/00050/data/DDWTA_T_PT_OF_SALE_TXN/SNAP_DT={year}*`
- Key Fields: `CLNT_NO`, `TXN_DT`, `AMT1`, `SRVC_CD`

**Token Tables** (Tokenization):
- `DDWV05.CLNT_CRD_POS_LOG` joined with `DL_DECMAN.TOKEN_LIST`
- Key Fields: `CLNT_NO`, `TXN_DT`, `TOKEN_WALLET_IND`

---

## 5. Vintage Curve Specifications

### 5.1 Vintage Curve Definition

A vintage curve shows **cumulative success rate over time** from treatment date:
- **X-axis**: Days from treatment (0 to measurement window)
- **Y-axis**: Cumulative success rate (%)
- **Lines**: One per cohort (deployment wave)

### 5.2 Output Fields (Standardized)

Every campaign should produce a standardized output with these fields:

| Field | Description |
|-------|-------------|
| CLNT_NO | Client identifier |
| TACTIC_ID | Deployment identifier |
| TREATMT_STRT_DT | Treatment start date |
| COHORT | Cohort label (yyyy-MM) |
| MNE | Campaign code |
| CAMPAIGN_NAME | Campaign name |
| CHANNEL | Deployment channel |
| TST_GRP_CD | Test group |
| measurement_end_dt | End of measurement window |
| SUCCESS_FLAG | 1 if success achieved, 0 otherwise |
| FIRST_SUCCESS_DT | Date of first success (if any) |
| DAYS_TO_FIRST_SUCCESS | Days from treatment to first success |
| SUCCESS_COUNT | Total successes in window (for volume) |
| *All other tactic fields* | Preserved for segmentation |

### 5.3 Aggregation for Vintage Plotting

```
COHORT | DAYS_TO_FIRST_SUCCESS | SUCCESSES_ON_DAY | CUMULATIVE_SUCCESSES | TOTAL_CLIENTS | CUMULATIVE_SUCCESS_RATE
```

---

## 6. Proposed Architecture

### 6.1 Directory Structure

```
vvd_vintage_framework/
├── config/
│   └── campaign_config.py       # Campaign definitions (one place to update)
├── modules/
│   ├── data_loader.py           # Load tactic and success tables
│   ├── success_detector.py      # Generic success detection by campaign type
│   ├── vintage_calculator.py    # Compute vintage curves
│   └── vintage_plotter.py       # Plotting functions
├── notebooks/
│   ├── 01_vcn_vintage.ipynb     # VCN analysis
│   ├── 02_vda_vintage.ipynb     # VDA analysis
│   ├── 03_vdt_vintage.ipynb     # VDT analysis
│   └── xx_all_campaigns.ipynb   # Combined view
└── outputs/
    ├── data/                    # Parquet outputs
    └── plots/                   # Vintage curve images
```

### 6.2 Configuration-Driven Approach

**campaign_config.py:**
```python
CAMPAIGN_CONFIG = {
    "VCN": {
        "success_type": "ACQUISITION",
        "success_table": "DDWTA_VISA_DR_CRD",
        "success_date_field": "ISS_DT",
        "window_days": 30,
        "deployment_type": "trigger",
        "filters": None
    },
    "VDA": {
        "success_type": "ACQUISITION",
        "success_table": "DDWTA_VISA_DR_CRD",
        "success_date_field": "ISS_DT",
        "window_days": 90,
        "deployment_type": "batch",
        "filters": None
    },
    "VDT": {
        "success_type": "ACTIVATION",
        "success_table": "DDWTA_VISA_DR_CRD",
        "success_date_field": "ACTV_DT",
        "window_days": 30,
        "deployment_type": "trigger",
        "filters": None
    },
    # Add more campaigns as needed
}
```

### 6.3 Generic Functions

**detect_success(tactic_df, mne, config):**
1. Read config for the campaign
2. Load appropriate success table
3. Apply join logic with correct date field
4. Return standardized DataFrame

**build_vintage_curve(success_df, group_by_col="COHORT"):**
1. Calculate total clients per group
2. Aggregate successes by day
3. Compute cumulative rates
4. Return vintage DataFrame

**plot_vintage_curve(vintage_df, title, save_path):**
1. Plot one line per group
2. Format axes and legend
3. Save to file

---

## 7. Implementation Phases

### Phase 1: Acquisition Campaigns (VCN, VDA) ✓
- [x] Define success logic (ISS_DT)
- [x] Build join with DDWTA_VISA_DR_CRD
- [x] Output standardized fields
- [x] Generate vintage curve by cohort

### Phase 2: Activation Campaign (VDT)
- [ ] Confirm success logic (ACTV_DT)
- [ ] Adjust code for 30-day window
- [ ] Generate vintage curve by cohort

### Phase 3: Usage Campaign (VUI)
- [ ] Define success logic (TXN_DT with filters)
- [ ] Build join with DDWTA_T_PT_OF_SALE_TXN
- [ ] Generate vintage curve by cohort

### Phase 4: Tokenization Campaigns (VUT, VAW)
- [ ] Define success logic (TOKEN join)
- [ ] Build complex join with TOKEN_LIST
- [ ] Generate vintage curve by cohort

### Phase 5: Framework Consolidation
- [ ] Refactor into modular config-driven structure
- [ ] Create reusable functions
- [ ] Document for team use

---

## 8. Open Questions / TBD

1. **ISS_DT vs other fields**: Confirm ISS_DT is correct for acquisition success
2. **Usage metrics**: What defines "usage" success for VUI? Transaction count? Dollar amount?
3. **Tokenization details**: Confirm join logic for VUT/VAW
4. **Multiple successes**: Currently using first success for vintage. Should we also track "time to Nth success"?
5. **Control groups**: Do we need vintage curves for control groups (not just TG4)?
6. **Segmentation dimensions**: What dimensions beyond cohort should we slice by? (Channel, demographic, etc.)

---

## 9. Sample Output

### Vintage Curve Data (VCN TG4 Example):

```
COHORT   | DAYS | SUCCESSES_ON_DAY | CUMULATIVE_SUCCESSES | TOTAL_CLIENTS | CUM_RATE
---------|------|------------------|----------------------|---------------|----------
2024-01  | 0    | 50               | 50                   | 15,000        | 0.33%
2024-01  | 1    | 120              | 170                  | 15,000        | 1.13%
2024-01  | 2    | 95               | 265                  | 15,000        | 1.77%
...      | ...  | ...              | ...                  | ...           | ...
2024-01  | 30   | 25               | 450                  | 15,000        | 3.00%
2024-02  | 0    | 55               | 55                   | 14,500        | 0.38%
...
```

### Final Rates by Cohort:

```
COHORT   | TOTAL_CLIENTS | TOTAL_SUCCESSES | FINAL_SUCCESS_RATE
---------|---------------|-----------------|-------------------
2024-01  | 15,000        | 450             | 3.00%
2024-02  | 14,500        | 493             | 3.40%
2024-03  | 16,200        | 535             | 3.30%
...
```

---

## 10. Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-17 | Andre | Initial draft - Acquisition campaigns |
| 2026-01-17 | Andre | Added VDT activation (30-day window) |
| TBD | TBD | Add usage/tokenization campaigns |
