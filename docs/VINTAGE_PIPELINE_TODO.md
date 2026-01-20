# Vintage Pipeline - TODO List

**Created:** January 2026
**Status:** In Progress

---

## PHASE 1: Information Gathering

### 1.1 Source Table Paths
- [x] Token/Provisioning: `DDWV05.CLNT_CRD_POS_LOG` + `DL_DECMAN.TOKEN_LIST` (EDW cursor)
- [x] Email feedback: `DTZV01.VENDOR_FEEDBACK_MASTER` + `VENDOR_FEEDBACK_EVENT` (Teradata)
- [x] Fulfillment: `DG6V01.TACTIC_EVNT_IP_AR_HIST` (Teradata)

### 1.2 Hardcoded Lookup Values (PENDING)
**Status:** Looking for a rich campaign with variety (multiple channels, reporting groups, models, success metrics)

For each campaign (VCN, VDA, VDT, VUI, VUT, VAW):
- [ ] Valid RPT_GRP_CD values and their segment meanings
- [ ] Valid TST_GRP_CD values (which is test, which is control)
- [ ] Channel codes and meanings
- [ ] Treatment codes and meanings
- [ ] Any exclusion rules
- [ ] Model information (if applicable)

### 1.3 Diagnostic Queries
- [ ] Run diagnostic on `tactic_evnt_hist` for VVD campaigns
- [ ] Determine primary tactic table (`tactic_evnt_hist` vs `ods_mr_hist`)
- [ ] Determine filter pattern for VVD campaigns

---

## PHASE 2: Build Modular Pipeline

### 2.1 Module 1: Experiment Metadata (Layer 1)
- [ ] Create component to pull from source `tactic_evnt_hist`
- [ ] Build hardcoded lookup table (placeholder)
- [ ] Output: Client list + segment + test/control + window
- [ ] Add diagnostic summary

### 2.2 Module 3: Success Capture (Layer 3)
- [ ] ACQUISITION/ACTIVATION: Use VISA_DR_CRD (Spark)
- [ ] USAGE: Use POS_TXN (Spark)
- [ ] TOKENIZATION: Use EDW cursor (special handling needed)
- [ ] Parameterize by success type

### 2.3 Module 4: Validation (Layer 4)
- [ ] Email feedback component (Teradata connection)
- [ ] Fulfillment component (Teradata connection)
- [ ] Output: DELIVERED_FLAG, FULFILLED_FLAG

### 2.4 Module 5 & 6: Calculation + Visualization
- [ ] Keep existing logic from all-in-one file
- [ ] Add option for adjusted denominators

---

## PHASE 3: Documentation

- [ ] Document each module with inputs/outputs
- [ ] Mark placeholder sections for future integration
- [ ] Prepare demo for director showing modular design

---

## IMMEDIATE NEXT STEPS (Tomorrow)

**You provide:**
1. Rich campaign example with design doc details
2. Confirm access to Teradata/EDW from Lumina

**I build:**
1. Diagnostic script for tactic_evnt_hist
2. Module 1 skeleton with hardcoded placeholders
3. Updated config with source paths

---

## QUESTIONS TO RESOLVE

1. Which tactic table is primary? `tactic_evnt_hist` vs `ods_mr_hist`?
2. How to connect to Teradata from Lumina for Email/Fulfillment?
3. How to use EDW cursor from Lumina for Token?
4. Is TG4 always the test group for all VVD campaigns?

---

## ACCESS METHODS SUMMARY

| Data | Method | Notes |
|------|--------|-------|
| Tactic/Population | Hive/Spark | Standard |
| VISA_DR_CRD | Hive/Spark | Standard |
| POS_TXN | Hive/Spark | Standard |
| Token/Provisioning | **EDW cursor** | Not in Hive |
| Email Feedback | **Teradata** | Need connection |
| Fulfillment | **Teradata** | Need connection |

---

## COMPLETED

- [x] Read all architecture documents (01-07)
- [x] Read ODS, MNE Mapping, Tactic metadata
- [x] Understand 4-layer architecture
- [x] Clarify Layer 1 vs Layer 2 roles
- [x] Clarify Layer 4 (decisioned vs happened)
- [x] Get Token/Email/Fulfillment source logic
- [x] Create context document
- [x] Create this TODO document

---

*Last updated: January 2026*
