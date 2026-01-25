# Tactic Event History Table Metadata

## Overview

This document captures the schema metadata for the `tsz_00150_cc_dtzta_t_tactic_evnt_hist` table, the primary Tactic History table used for experiment identification and client-level treatment tracking. This is a core source for Layer 1 (Governed Experiment Metadata) and Layer 4 (Client Marketing Interaction Journey) in the Success Library architecture.

**Location:** `prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist`

---

## Table: tsz_00150_cc_dtzta_t_tactic_evnt_hist

### Field Definitions

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| tactic_evnt_id | string | Tactic event identifier |
| tactic_evnt_id_typ_cd | int | Tactic event ID type code |
| tactic_evnt_srvc_id | int | Tactic event service identifier |
| tactic_id | string | **Tactic identifier (key field)** |
| strtgy_src_cd | string | Strategy source code |
| trgt_typ_cd | string | Target type code |
| visa_clnt_srce_ind | int | Visa client source indicator |
| treatmt_mn | string | **Treatment mnemonic** |
| treatmt_eff_dt | date | Treatment effective date |
| tactic_cell_cd | string | Tactic cell code |
| tst_grp_cd | string | **Test group code (key field)** |
| tst_grp_eff_dt | date | Test group effective date |
| rpt_grp_cd | string | **Report group code (key field)** |
| rpt_grp_eff_dt | date | Report group effective date |
| bus_mkt_id | int | Business market identifier |
| tactic_decisn_vrb_info | string | Tactic decision variable info |
| amt | decimal(18,2) | Amount |
| bus_clnt_cntct_id | int | Business client contact identifier |
| selt_affinity_mdl_scor | decimal(15,6) | Selection affinity model score |
| tactic_adnc_typ_cd | int | Tactic audience type code |
| addnl_decisn_data1 | string | **Additional decision data 1 (flexible field)** |
| purge_dt | date | Purge date |
| load_downstrm_dest_cd | string | Load downstream destination code |
| tsys_src_cd | string | TSYS source code |
| visa_adjudcn_cd | string | Visa adjudication code |
| addnl_data_dt | date | Additional data date |
| addnl_decisn_data2 | string | **Additional decision data 2 (flexible field)** |
| addnl_decisn_data3 | string | **Additional decision data 3 (flexible field)** |
| treatmt_strt_dt | date | **Treatment start date (key field)** |
| treatmt_end_dt | date | Treatment end date |
| evnt_strt_dt | date | Event start date |

---

## Four Contextual Fields for Experiment Identification

Per the Success Library architecture, these four fields serve as unique identifiers to link experiments to clients:

| Field | Purpose | Notes |
|-------|---------|-------|
| rpt_grp_cd | Report Group Code | Groups related tactics/campaigns |
| treatmt_mn | Treatment Meaning | Describes the treatment being applied |
| tst_grp_cd | Test Group | Identifies test vs control assignment |
| tactic_id OR treatmt_strt_dt | Unique Identifier | Tactic ID or timestamp for treatment initiation |

**Combined with:** `tactic_evnt_id` (client linkage), this enables tracing from experiment design to client-level outcomes.

### Limitation

> "Leveraging the four contextual fields is enough to identify majority of the experiments as of today. However, does not work for complex campaigns."

For complex campaigns requiring more granular tagging, the JSON solution in `ods_mr_hist.treatmt_adnl_dtl` is the workaround.

---

## Flexible Data Fields

The table includes three `addnl_decisn_data` fields that can store additional context:

| Field | Type | Potential Use |
|-------|------|---------------|
| addnl_decisn_data1 | string | Experiment metadata overflow |
| addnl_decisn_data2 | string | Secondary attributes |
| addnl_decisn_data3 | string | Tertiary attributes |

These are referenced in the hybrid PySpark+SQL solution pattern:
```python
fact2_df = read_teradata("""
    SELECT clnt_no, tactic_id, ADDNL_DECISN_DATA1 AS metric2 
    FROM DGNV01.TACTIC_EVNT_IP_AR_HIST
    ...
""")
```

---

## Related Tables in Schema

| Table Name | Purpose |
|------------|---------|
| tsz_00150_cc_dtzta_t_tactic_ip_arngmnt_reltn_hist | Tactic IP arrangement relationship history |
| tsz_00150_data_dtzta_t_tactic_cell | Tactic cell definitions |
| tsz_00150_data_dtzta_t_tactic_rpt_grp | Tactic report group definitions |

---

## Integration with Success Library Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: Governed Experiment Metadata                           │
│ ─────────────────────────────────────                           │
│ THIS TABLE provides:                                            │
│   • rpt_grp_cd → Experiment grouping                            │
│   • tst_grp_cd → Test/Control assignment                        │
│   • treatmt_mn → Treatment description                          │
│   • treatmt_strt_dt → Experiment timing                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: Client Marketing Interaction Journey                   │
│ ─────────────────────────────────────────────                   │
│ THIS TABLE provides:                                            │
│   • tactic_evnt_id → Client linkage                             │
│   • treatmt_strt_dt / treatmt_end_dt → Treatment window         │
│   • evnt_strt_dt → Event timing                                 │
│   • amt → Offer/transaction amount                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Limitation: Decisions vs. Delivery

> "Limitation of tactic_hist, only the decisions, not client who received."

This table captures **what was decided to send**, not which client **actually received** the treatment. This creates a gap in measurement accuracy for treatment effects. The Client Marketing Interaction Journey enhancement aims to close this gap by adding:

- Leads actions
- Client response
- Channel response
- Status of applications

---

## Comparison with Other Tactic Tables

| Table | Location | Use Case |
|-------|----------|----------|
| tsz_00150_cc_dtzta_t_tactic_evnt_hist | prod_yg80_pcbsharedzone | **This table** - Primary tactic event history |
| TACTIC_IP_AR_HIST | - | Tactic IP/AR history |
| DGNV01.TACTIC_EVNT_IP_AR_HIST | Teradata | Referenced in PySpark code patterns |
| ods_mr_hist | ed10_im.prod_x610_crm | ODS marketing response (has JSON field) |

---

## References

- Source: `prod_yg80_pcbsharedzone.tsz_00150_cc_dtzta_t_tactic_evnt_hist`
- Context: Success Library - SuperFact Concept v2, Slides 7, 10, 15
- Related: Layer 1 Experiment Metadata, Layer 4 Client Journey

---

*Document created: January 2026*
*Source: Cluster Explorer schema screenshot (prod_yg80_pcbsharedzone)*
