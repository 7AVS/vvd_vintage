# Field Analysis: Tactic & ODS Tables

Mapping of all available fields, what we're currently using, and what we should leverage.

---

## Quick Summary

| Need | Field | Source | Currently Using? |
|------|-------|--------|------------------|
| **Channel** | `chnl_cd` | ODS_MR_HIST | NO |
| **Test Group** | `tst_grp_cd` | TACTIC_EVNT_HIST | YES (hardcoded TG4) |
| **Segment** | `rpt_grp_cd` | TACTIC_EVNT_HIST | NO |
| **Delivery Method** | `delvry_mthd_cd` | ODS_MR_HIST | NO |
| **Offer Status** | `offr_sts_cd` | ODS_MR_HIST | NO |
| **Fulfillment Code** | `?` | UNKNOWN | NO - Need to find |
| **Client ID** | `tactic_evnt_id` / `clnt_id` | TACTIC / ODS | YES |
| **Treatment Window** | `treatmt_strt_dt`, `treatmt_end_dt` | TACTIC_EVNT_HIST | YES |

---

## Table 1: TACTIC_EVNT_HIST

**Location:** `/prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/`

### All Available Fields

| Field | Type | Description | Using? | Should Use? |
|-------|------|-------------|--------|-------------|
| `tactic_evnt_id` | string | Client identifier | YES | YES - client linkage |
| `tactic_evnt_id_typ_cd` | int | ID type code | NO | Maybe - understand what it means |
| `tactic_evnt_srvc_id` | int | Service identifier | NO | Maybe - could identify VVD? |
| `tactic_id` | string | Tactic identifier (MNE in positions 8-10) | YES | YES |
| `strtgy_src_cd` | string | Strategy source code | Partial | **YES - may indicate channel/strategy** |
| `trgt_typ_cd` | string | Target type code | NO | Maybe - understand what it means |
| `visa_clnt_srce_ind` | int | Visa client source indicator | NO | NO |
| `treatmt_mn` | string | Treatment mnemonic | YES | YES |
| `treatmt_eff_dt` | date | Treatment effective date | NO | Maybe |
| `tactic_cell_cd` | string | Tactic cell code | YES (select) | **YES - may contain segment/variant info** |
| `tst_grp_cd` | string | **Test group code** | YES (hardcoded TG4) | **YES - need flexible handling** |
| `tst_grp_eff_dt` | date | Test group effective date | NO | NO |
| `rpt_grp_cd` | string | **Report group code** | YES (select) | **YES - for segmentation** |
| `rpt_grp_eff_dt` | date | Report group effective date | NO | NO |
| `bus_mkt_id` | int | Business market identifier | NO | Maybe |
| `tactic_decisn_vrb_info` | string | Decision variable info | NO | Maybe - explore content |
| `amt` | decimal | Amount | NO | Maybe - offer amount? |
| `bus_clnt_cntct_id` | int | Client contact identifier | NO | NO |
| `selt_affinity_mdl_scor` | decimal | Model score | NO | NO |
| `tactic_adnc_typ_cd` | int | Audience type code | NO | Maybe |
| `addnl_decisn_data1` | string | **Flexible field 1** | YES (select) | **YES - may contain channel** |
| `addnl_decisn_data2` | string | **Flexible field 2** | YES (select) | **YES - explore content** |
| `addnl_decisn_data3` | string | **Flexible field 3** | YES (select) | **YES - explore content** |
| `purge_dt` | date | Purge date | NO | NO |
| `load_downstrm_dest_cd` | string | Downstream destination | NO | NO |
| `tsys_src_cd` | string | TSYS source code | NO | NO |
| `visa_adjudcn_cd` | string | Visa adjudication code | NO | NO |
| `addnl_data_dt` | date | Additional data date | NO | NO |
| `treatmt_strt_dt` | date | **Treatment start date** | YES | YES |
| `treatmt_end_dt` | date | **Treatment end date** | YES | YES |
| `evnt_strt_dt` | date | Event start date (partition) | YES | YES |

### Fields to Investigate

```
Priority 1 - Likely contain what we need:
├── strtgy_src_cd      → May indicate channel/strategy
├── tactic_cell_cd     → May contain segment/variant info
├── addnl_decisn_data1 → Flexible - may have channel
├── addnl_decisn_data2 → Flexible - explore
└── addnl_decisn_data3 → Flexible - explore

Priority 2 - Understand for context:
├── tactic_evnt_srvc_id → Could identify VVD service?
├── trgt_typ_cd         → Target type
├── tactic_adnc_typ_cd  → Audience type
└── tactic_decisn_vrb_info → Decision variables
```

---

## Table 2: ODS_MR_HIST

**Location:** `/prod/01347/app/LS20/data/SparkJobData/effectDate=YYYY-MM-DD`

### All Available Fields

| Field | Type | Description | Using? | Should Use? |
|-------|------|-------------|--------|-------------|
| `offr_id` | string | Offer identifier | NO | Maybe - for offer tracking |
| `clnt_id` | int | **Client identifier** | NO | **YES - join key** |
| `chnl_cd` | int | **CHANNEL CODE** | NO | **YES - CRITICAL** |
| `acct_no` | string | Account number | NO | NO |
| `tactic_id` | string | Tactic identifier | NO | **YES - join key** |
| `camp_reg_id` | string | Campaign registration ID | NO | Maybe |
| `lang_cd` | string | Language code | NO | NO |
| `tr_no` | int | Transaction number | NO | NO |
| `acct_sufx_no` | int | Account suffix | NO | NO |
| `prod_id` | string | Product identifier | NO | Maybe - VVD product? |
| `prod_mn` | string | Product mnemonic | NO | Maybe |
| `est_mail_dt` | string | Estimated mail date | NO | Maybe - for email tracking |
| `campgn_cd` | int | Campaign code | NO | Maybe |
| `delvry_mthd_cd` | string | **Delivery method code** | NO | **YES - alternative to channel** |
| `foll_up_mthd_cd` | string | Follow-up method code | NO | Maybe |
| `offr_strt_dt` | string | Offer start date | NO | YES - treatment window |
| `offr_end_dt` | string | Offer end date | NO | YES - treatment window |
| `updt_untl_dt` | string | Update until date | NO | NO |
| `offr_displ_cd` | string | Offer display code | NO | Maybe |
| `offr_sts_cd` | int | **Offer status code** | NO | **MAYBE - fulfillment?** |
| `offr_reas_cd` | int | **Offer reason code** | NO | **MAYBE - fulfillment?** |
| `updt_tmstmp` | string | Update timestamp | NO | NO |
| `updt_emp_no` | int | Update employee number | NO | NO |
| `updt_chnl_cd` | int | Update channel code | NO | Maybe |
| `msg_creat_tmstmp` | string | Message creation timestamp | NO | NO |
| `prirty_scor` | string | Priority score | NO | NO |
| `cr_crd_no` | string | Credit card number | NO | NO |
| `oper_id` | string | Operator ID | NO | NO |
| `instrmt_no` | string | Instrument number | NO | NO |
| `csdb_offr_strt_dt` | string | CSDB offer start date | NO | NO |
| `csdb_offr_end_dt` | string | CSDB offer end date | NO | NO |
| `csdb_tactic_id` | string | CSDB tactic identifier | NO | NO |
| `trgt_typ_cd` | string | Target type code | NO | Maybe |
| `treatmt_dtl` | string | Treatment detail | NO | Maybe |
| `treatmt_dtl_en` | string | Treatment detail (English) | NO | Maybe |
| `treatmt_dtl_fr` | string | Treatment detail (French) | NO | NO |
| `treatmt_adnl_dtl` | string | **Treatment additional detail (JSON)** | NO | **YES - experiment metadata** |
| `effectdate` | date | Effective date (partition) | NO | YES |

### Fields to Investigate

```
Priority 1 - Critical for our needs:
├── chnl_cd           → CHANNEL CODE (what values? lookup table?)
├── delvry_mthd_cd    → Delivery method (alternative to channel?)
├── offr_sts_cd       → Offer STATUS - could be fulfillment?
└── offr_reas_cd      → Offer REASON - could be fulfillment?

Priority 2 - For enrichment:
├── treatmt_adnl_dtl  → JSON field - experiment metadata
├── prod_id / prod_mn → Product identification
└── offr_id           → Offer tracking
```

---

## Channel Analysis

### Where is Channel?

| Source | Field | Type | Notes |
|--------|-------|------|-------|
| ODS_MR_HIST | `chnl_cd` | INT | **Most likely source** - need lookup table |
| ODS_MR_HIST | `delvry_mthd_cd` | STRING | Delivery method - may map to channel |
| TACTIC | `strtgy_src_cd` | STRING | Strategy source - may indicate channel |
| TACTIC | `addnl_decisn_data1` | STRING | Flexible - may contain channel |

### Expected Channel Codes

| Code | Channel | Notes |
|------|---------|-------|
| ? | EMAIL | Email channel |
| ? | MOBILE | Mobile banner |
| ? | ONB | Online banking |
| ? | ONO | Offer & Opportunity (Advisory Centre) |
| ? | DM | Direct mail |
| ? | BRANCH | Branch |

**Action:** Need to run diagnostic to see actual `chnl_cd` values

---

## Fulfillment Analysis

### Where is Fulfillment Code?

**Current assumption was TACTIC_EVNT_IP_AR_HIST** but that may be wrong.

| Possible Source | Field | Notes |
|-----------------|-------|-------|
| ODS_MR_HIST | `offr_sts_cd` | Offer STATUS - could indicate acceptance |
| ODS_MR_HIST | `offr_reas_cd` | Offer REASON code |
| TACTIC | `tactic_decisn_vrb_info` | Decision variable info |
| ? | ? | May need separate fulfillment table |

### What is Fulfillment?
- Each campaign (MNE) has specific fulfillment code(s)
- Fulfillment = client accepted/responded to offer
- Can have multiple fulfillment codes per campaign (different offers/strategies)

**Action:** Need to find where fulfillment codes are documented or stored

---

## Test Group Analysis

### Current Implementation
```python
TEST_GROUP_CODE = "TG4"  # Hardcoded
GROUP = "TEST" if TST_GRP_CD == "TG4" else "CONTROL"
```

### Known Test Group Codes
| Code | Meaning | Source |
|------|---------|--------|
| TG1 | ACTION (Test) | User knowledge |
| TG4 | ACTION (Test) | User knowledge |
| TG0 | Control? | Assumption |
| TG2, TG3, etc. | ? | Need to investigate |

### What We Need
- Full list of TST_GRP_CD values
- Meaning of each code
- Per-campaign test group configuration

**Action:** Run diagnostic to see all TST_GRP_CD values in VVD campaigns

---

## Segment Analysis (RPT_GRP_CD)

### Current Status
- Field exists in TACTIC: `rpt_grp_cd`
- We SELECT it but don't use it
- No lookup table identified

### Questions
- What values does RPT_GRP_CD have?
- Is there a lookup table for descriptions?
- How should we use it for segmentation?

**Action:** Run diagnostic to see RPT_GRP_CD values and find lookup table

---

## Join Strategy: TACTIC + ODS

Currently we only use TACTIC. To get channel, we need to join with ODS.

### Join Keys
```
TACTIC.tactic_id = ODS.tactic_id
TACTIC.tactic_evnt_id = ODS.clnt_id  (need to verify - may need transformation)
```

### Proposed Flow
```
┌──────────────────────┐
│   TACTIC_EVNT_HIST   │
│                      │
│  • tactic_evnt_id    │
│  • tactic_id         │
│  • tst_grp_cd        │
│  • rpt_grp_cd        │
│  • treatmt_strt_dt   │
│  • treatmt_end_dt    │
│  • addnl_decisn_data │
└──────────┬───────────┘
           │
           │ JOIN on tactic_id + clnt_id
           │
           ▼
┌──────────────────────┐
│     ODS_MR_HIST      │
│                      │
│  • chnl_cd           │  ← CHANNEL
│  • delvry_mthd_cd    │
│  • offr_sts_cd       │  ← FULFILLMENT?
│  • offr_reas_cd      │
│  • treatmt_adnl_dtl  │  ← JSON metadata
└──────────────────────┘
```

---

## Diagnostic Queries Needed

### 1. Channel Codes in ODS
```python
# What channel codes exist?
ods_df.select("chnl_cd").distinct().show()

# Count by channel
ods_df.groupBy("chnl_cd").count().orderBy("count", ascending=False).show()
```

### 2. Test Group Codes in TACTIC
```python
# For VVD campaigns (MNE in VCN, VDA, VDT, VUI, VUT, VAW)
tactic_df.filter(tactic_df.MNE.isin(["VCN", "VDA", "VDT", "VUI", "VUT", "VAW"])) \
    .groupBy("tst_grp_cd").count().orderBy("count", ascending=False).show()
```

### 3. Flexible Fields Content
```python
# What's in addnl_decisn_data1?
tactic_df.filter(tactic_df.addnl_decisn_data1.isNotNull()) \
    .select("addnl_decisn_data1").distinct().show(50, truncate=False)
```

### 4. Report Group Codes
```python
# What RPT_GRP_CD values exist?
tactic_df.groupBy("rpt_grp_cd").count().orderBy("count", ascending=False).show()
```

### 5. Offer Status/Reason Codes in ODS
```python
# Could these be fulfillment?
ods_df.groupBy("offr_sts_cd", "offr_reas_cd").count() \
    .orderBy("count", ascending=False).show(50)
```

---

## Action Items

### Immediate (Need to Run at Work)

| # | Action | Query/Code |
|---|--------|------------|
| 1 | Get all `chnl_cd` values from ODS | See diagnostic query 1 |
| 2 | Get all `tst_grp_cd` values from TACTIC | See diagnostic query 2 |
| 3 | Explore `addnl_decisn_data1/2/3` content | See diagnostic query 3 |
| 4 | Get all `rpt_grp_cd` values | See diagnostic query 4 |
| 5 | Explore `offr_sts_cd` / `offr_reas_cd` | See diagnostic query 5 |

### Follow-up

| # | Action | Depends On |
|---|--------|------------|
| 6 | Find channel code lookup table | After #1 |
| 7 | Find fulfillment code documentation | After #5 |
| 8 | Update load_tactic() to join ODS | After #1 confirms channel in ODS |
| 9 | Update test group handling | After #2 |

---

## Summary: What We Know vs Don't Know

### KNOW
- Test group is in `tst_grp_cd` (TACTIC)
- Report group is in `rpt_grp_cd` (TACTIC)
- Channel is likely in `chnl_cd` (ODS)
- Treatment window is in TACTIC
- Client linkage is `tactic_evnt_id` (TACTIC) / `clnt_id` (ODS)

### DON'T KNOW
- What are the actual `chnl_cd` values? (need lookup)
- Where are fulfillment codes? (not clear)
- What's in `addnl_decisn_data` fields?
- What does `rpt_grp_cd` represent? (need lookup)
- Full list of `tst_grp_cd` values and meanings
