# Layer 1 & Layer 2 Assessment

## Purpose
Understand what we can leverage from existing tables vs what needs to be built.

---

## Layer 1: Experiment Metadata

**Source:** `tactic_evnt_hist` (DTZTA_T_TACTIC_EVNT_HIST)

### Fields Available

| Field | Available | Using Now | Notes |
|-------|-----------|-----------|-------|
| TACTIC_ID | Yes | Yes | MNE extracted from positions 8-10 |
| TST_GRP_CD | Yes | Yes | Test group code (TG4 = Test) |
| CLNT_NO | Yes | Yes | Via TACTIC_EVNT_ID |
| TREATMT_STRT_DT | Yes | Yes | Treatment start |
| TREATMT_END_DT | Yes | Yes | Treatment end |
| TACTIC_CELL_CD | Yes | Yes | Channel (EM, MB, etc.) |
| RPT_GRP_CD | Yes | No | Segment - need to understand meaning |
| ADDNL_DECISN_DATA1/2/3 | Yes | No | Flexible fields - explore |

### Fields Missing (Need to Build)

| Field | Purpose | Source |
|-------|---------|--------|
| Experiment Name | Human-readable name | Need Experiment Metadata table |
| Experiment Type | A/B, Champion/Challenger | Need Experiment Metadata table |
| Hypothesis | What we're testing | Need Experiment Metadata table |
| Test Group Definition | Which TST_GRP_CD = Test | Need per-experiment config |

---

## Layer 2: Campaign Metadata

**Source:** `CIDM_MNEMONIC_ATTRS` (Mnemonic Mapping)

### Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| MNE | Yes | Campaign code |
| CAMPAIGN_DESCRIPTION | Yes | Name |
| LOB | Yes | Line of business |
| CAMPAIGN_CATEGORY | Yes | Fulfillment, Regulatory, etc. |
| MEASUREMENT_CATEGORY | Yes | Measurable, Operational |
| CONTROL_EXEMPTION | Yes | |

### Fields Missing (Need to Add)

| Field | Purpose | Status |
|-------|---------|--------|
| PRIMARY_METRIC | What success metric to use | NOT in table - hardcoded now |
| SECONDARY_METRIC | Secondary measurement | NOT in table |
| TERTIARY_METRIC | Third measurement | NOT in table |
| ACTION_TYPE | Type of action | NOT in table |
| PRODUCT | Which product | NOT clear |

---

## Gap Analysis

### What We Have
- Basic experiment data from tactic_evnt_hist
- Basic campaign info from mnemonic mapping
- Channel from TACTIC_CELL_CD

### What We're Missing
1. **MNE → Metric mapping** (currently hardcoded in CAMPAIGN_METADATA)
2. **Flexible test group definition** (currently hardcoded TG4)
3. **Product categorization** (which product does each MNE belong to)
4. **Success metric library** (definitions scattered, not centralized)

---

## Action Items

- [ ] Confirm all fields in CIDM_MNEMONIC_ATTRS
- [ ] Request PRIMARY_METRIC field to be added
- [ ] Document TST_GRP_CD values and meanings
- [ ] Map MNEs to products
- [ ] Build Success Library for each product

