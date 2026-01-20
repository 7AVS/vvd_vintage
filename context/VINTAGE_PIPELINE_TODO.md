# Vintage Pipeline - TODO List

**Created:** January 2026
**Status:** In Progress

---

## PHASE 1: Information Gathering

### 1.1 Source Table Paths Needed
- [ ] Token/Provisioning table path (Layer 3)
- [ ] Email feedback table path (Layer 4)
- [ ] Fulfillment table path (Layer 4)
- [ ] Digital channels feedback table path (Layer 4)

### 1.2 Hardcoded Lookup Values Needed (from design docs)
For each campaign (VCN, VDA, VDT, VUI, VUT, VAW):
- [ ] Valid RPT_GRP_CD values and their segment meanings
- [ ] Valid TST_GRP_CD values (which is test, which is control)
- [ ] Channel codes and meanings
- [ ] Any exclusion rules
- [ ] Treatment codes and meanings

### 1.3 Diagnostic Queries
- [ ] Run diagnostic on `tactic_evnt_hist` for VVD campaigns
  - What values exist for RPT_GRP_CD?
  - What values exist for TST_GRP_CD?
  - What date ranges are available?
  - Volume counts per campaign
- [ ] Determine primary tactic table to use (`tactic_evnt_hist` vs `ods_mr_hist`)
- [ ] Determine how to filter for VVD campaigns (MNE prefix? SRVC_ID?)

---

## PHASE 2: Build Modular Pipeline

### 2.1 Module 1: Experiment Metadata (Layer 1)
- [ ] Create component to pull from source `tactic_evnt_hist`
- [ ] Build hardcoded lookup table (placeholder for future Layer 1)
- [ ] Output: Client list with RPT_GRP_CD, TST_GRP_CD, treatment window
- [ ] Add diagnostic/summary output showing:
  - Total clients
  - Breakdown by segment
  - Breakdown by test/control
  - Date range

### 2.2 Module 3: Success Capture (Layer 3)
- [ ] Refactor success detection to use source table paths
- [ ] Parameterize success logic by type (ACQUISITION, ACTIVATION, USAGE, TOKENIZATION)
- [ ] Join client list from Module 1 with success outcomes
- [ ] Output: SUCCESS_FLAG, SUCCESS_DT, DAYS_TO_SUCCESS

### 2.3 Module 4: Validation (Layer 4)
- [ ] Add email feedback component (when table path provided)
- [ ] Add fulfillment component (when table path provided)
- [ ] Add channel delivery confirmation
- [ ] Output: DELIVERED_FLAG, FULFILLED_FLAG
- [ ] Enable adjusted denominators (delivered vs decisioned)

### 2.4 Module 5: Vintage Calculation
- [ ] Keep existing calculation logic
- [ ] Add option to use adjusted denominators from Module 4
- [ ] Output: Cumulative rates, lift, confidence intervals

### 2.5 Module 6: Visualization
- [ ] Keep existing plot functions
- [ ] Add breakdowns by segment (using RPT_GRP_CD)
- [ ] Add breakdowns by channel

---

## PHASE 3: Documentation & Handoff

### 3.1 Code Documentation
- [ ] Document each module with clear inputs/outputs
- [ ] Mark placeholder sections for future Layer 1 integration
- [ ] Add comments showing where hardcoded values will be replaced

### 3.2 Director Presentation
- [ ] Show modular architecture diagram
- [ ] Demonstrate: "Here is where we pull from Layer 1"
- [ ] Demonstrate: "Here is where Success Library logic runs"
- [ ] Show diagnostic outputs

---

## IMMEDIATE NEXT STEPS (Tomorrow Morning)

1. **You provide:**
   - Token table source path
   - Email feedback table source path
   - Fulfillment table source path
   - Hardcoded lookup values from VVD design docs (or the docs themselves)

2. **I build:**
   - Diagnostic script for tactic_evnt_hist
   - Module 1 skeleton with placeholder lookups
   - Refactored Module 3 using source paths

3. **We validate:**
   - Run diagnostics on Lumina
   - Confirm source tables are accessible
   - Verify field names match metadata docs

---

## QUESTIONS TO RESOLVE

1. Which tactic table is primary? `tactic_evnt_hist` or `ods_mr_hist`?
2. How do we identify VVD campaigns in tactic? (TACTIC_ID starts with VCN/VDA/etc.?)
3. Is TG4 always the test group for all VVD campaigns?
4. Do all VVD campaigns use the same success table filters (SRVC_ID=36)?

---

## FILES TO CREATE/UPDATE

| File | Purpose | Status |
|------|---------|--------|
| `vintage_modular/module1_experiment.py` | Layer 1 component | To create |
| `vintage_modular/module3_success.py` | Layer 3 component | To create |
| `vintage_modular/module4_validation.py` | Layer 4 component | To create |
| `vintage_modular/module5_vintage.py` | Calculation component | To create |
| `vintage_modular/module6_viz.py` | Visualization component | To create |
| `vintage_modular/config.py` | Hardcoded lookups + paths | To create |
| `vintage_modular/diagnostics.py` | Diagnostic queries | To create |
| `vintage_modular/run_pipeline.py` | Main runner | To create |

---

## COMPLETED ITEMS

- [x] Read all architecture documents (01-07)
- [x] Read ODS, MNE Mapping, Tactic metadata
- [x] Understand 4-layer architecture
- [x] Clarify Layer 1 vs Layer 2 roles
- [x] Clarify Layer 4 (decisioned vs happened)
- [x] Identify fulfillment as Layer 4 component
- [x] Create context document
- [x] Create this TODO document

---

*Last updated: January 2026*
