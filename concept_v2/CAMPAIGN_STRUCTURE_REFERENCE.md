# Campaign Structure Reference

**Purpose:** Document how marketing campaigns are structured, using SLC as a real-world example.
**Source:** Technical specification screenshots from campaign documentation.
**Created:** 2026-01-23

---

## Overview

Marketing campaigns have a hierarchical structure with multiple dimensions for testing and measurement. Understanding this structure is critical for building vintage analysis that supports meaningful comparisons.

---

## Key Fields in Tactic Table

| Field | Purpose | Example Values |
|-------|---------|----------------|
| **TST_GRP_CD** | Test group allocation (A/B creative test, control holdout) | TG1, TG4, TG7 |
| **RPT_GRP_CD** | Report group (channel strategy segmentation) | PSLCRG01, PSLCRG02, PSLCRG03 |
| **TREATMT_MN** | Treatment mnemonic (specific creative/offer combination) | 1SLC001A, 1SLC002A, PSLCNMAA |
| **TACTIC_CELL_CD** | Channel code | IM, EM, IM_EM, XX (control) |

---

## Real Example: SLC Campaign

### Test Group Allocation (TST_GRP_CD)

| Code | Allocation | Purpose |
|------|------------|---------|
| TG1 | 40% | Treatment - Creative/Offer 2 (ITAOFFER2) |
| TG4 | 40% | Treatment - Creative/Offer 1 (ITAOFFER1) |
| TG7 | 20% | Control - Random holdout (no treatment) |

**Key insight:** TG1 and TG4 are NOT just "test groups" - they represent an A/B creative test. TG7 is the shared control.

### Report Group Codes (RPT_GRP_CD)

| Code | Description | Channel Strategy |
|------|-------------|------------------|
| PSLCRG01 | SLC Acquisition OLB and Mobile | Digital only (IM, IM_MB) |
| PSLCRG02 | SLC Acquisition EM | Email only |
| PSLCRG03 | SLC Acquisition OLB/Mobile/EM | Multi-channel (EM_IM, IM_EM_MB) |

**Key insight:** Report groups represent channel strategy segments, not arbitrary groupings.

### Treatment Codes (TREATMT_MN)

| Code | Description | Channel | Creative |
|------|-------------|---------|----------|
| 1SLC001A | OLB and Mobile - test 1 | IM_MB | ITAOFFER1 |
| 1SLC002A | EM only | EM | - |
| 1SLC003A | OLB/Mobile/EM - test 1 | IM_EM_MB | ITAOFFER1 |
| 1SLC004A | OLB and Mobile - test 2 | IM_MB | ITAOFFER2 |
| 1SLC005A | OLB/Mobile/EM - test 2 | IM_EM_MB | ITAOFFER2 |
| PSLCNMAA | Control | XX | None |

---

## Campaign Hierarchy

```
                        SLC CAMPAIGN
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
     TG4 (40%)            TG1 (40%)            TG7 (20%)
    ITAOFFER1             ITAOFFER2             CONTROL
        │                    │                    │
   ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
   │         │          │         │          │         │
PSLCRG01  PSLCRG03   PSLCRG01  PSLCRG03   PSLCRG01  PSLCRG03
(Digital) (Multi-ch) (Digital) (Multi-ch) (Digital) (Multi-ch)
   │         │          │         │          │         │
1SLC001A  1SLC003A   1SLC004A  1SLC005A   PSLCNMAA  PSLCNMAA
```

### The 6 Analysis Cells

| Cell | TST_GRP_CD | RPT_GRP_CD | TREATMT_MN | Description |
|------|------------|------------|------------|-------------|
| 1 | TG4 | PSLCRG01 | 1SLC001A | Offer1 + Digital |
| 2 | TG4 | PSLCRG03 | 1SLC003A | Offer1 + Multi-channel |
| 3 | TG1 | PSLCRG01 | 1SLC004A | Offer2 + Digital |
| 4 | TG1 | PSLCRG03 | 1SLC005A | Offer2 + Multi-channel |
| 5 | TG7 | PSLCRG01 | PSLCNMAA | Control + Digital |
| 6 | TG7 | PSLCRG03 | PSLCNMAA | Control + Multi-channel |

---

## What This Campaign Can Test

### Valid Comparisons

| Question | Comparison | Method |
|----------|------------|--------|
| "Does the campaign work?" | (TG1 + TG4) vs TG7 | Pool treatments, compare to control |
| "Which offer performs better?" | TG1 vs TG4 | Compare within same RPT_GRP_CD |
| "Does adding email help?" | PSLCRG01 vs PSLCRG03 | Compare within same TST_GRP_CD |
| "Best performing cell?" | All 6 cells | Full granularity |

### Lift Calculations

| Lift Type | Formula |
|-----------|---------|
| Overall Treatment Lift | Rate(TG1+TG4) - Rate(TG7) |
| Offer1 Lift | Rate(TG4) - Rate(TG7) |
| Offer2 Lift | Rate(TG1) - Rate(TG7) |
| Offer2 vs Offer1 | Lift(TG1) - Lift(TG4) |

**Important:** TG1 vs TG4 directly gives you relative creative performance, but NOT absolute lift. You need TG7 (control) for absolute lift.

---

## Design Pattern: Two Dimensions Being Tested

This campaign tests **two things simultaneously**:

1. **Creative/Offer Test** (between TST_GRP_CD)
   - TG4 = Offer 1 (ITAOFFER1)
   - TG1 = Offer 2 (ITAOFFER2)
   - TG7 = Control (shared)

2. **Channel Strategy Test** (between RPT_GRP_CD)
   - PSLCRG01 = Digital only
   - PSLCRG03 = Multi-channel

This is a **2×2 factorial design** with a shared control arm.

---

## Implications for Vintage Engine

### Phase 1: Raw Codes (Pilot)

For the initial build, use raw codes from the tactic table:

```
COHORT | DAY | TST_GRP_CD | RPT_GRP_CD | TEST_CLIENTS | TEST_RATE | CTRL_CLIENTS | CTRL_RATE
2024-06| 30  | TG4        | PSLCRG01   | 15000        | 4.5%      | 5000         | 3.2%
2024-06| 30  | TG1        | PSLCRG01   | 15000        | 5.2%      | 5000         | 3.2%
```

- Dashboard shows codes (TG1, TG4, PSLCRG01, etc.)
- User selects which codes to compare
- No semantic labels yet

### Phase 2: Semantic Layer (Future)

Add a metadata table that maps codes to human-readable labels:

```python
CAMPAIGN_SEMANTICS = {
    "SLC": {
        "TST_GRP_CD": {
            "TG1": {"label": "Offer 2", "type": "treatment"},
            "TG4": {"label": "Offer 1", "type": "treatment"},
            "TG7": {"label": "Control", "type": "control"}
        },
        "RPT_GRP_CD": {
            "PSLCRG01": {"label": "Digital Only", "channel": "IM"},
            "PSLCRG03": {"label": "Multi-channel", "channel": "EM_IM"}
        }
    }
}
```

Engine pulls labels from this table at runtime.

---

## Key Learnings

1. **TST_GRP_CD is not just "test vs control"** - it can represent A/B creative tests with a shared control.

2. **RPT_GRP_CD represents meaningful business segments** (channel strategies), not arbitrary reporting buckets.

3. **TREATMT_MN is the most granular** but can collapse (e.g., same control code across report groups).

4. **Store at TST_GRP_CD × RPT_GRP_CD level** for maximum flexibility in comparisons.

5. **Control is shared** across test groups - each test group's lift is measured against the same control.

6. **Semantic layer is separate** from the analysis engine - allows flexibility without hardcoding.

---

## Reference: Tactic Table Data (From Screenshot)

```
TACTIC_ID    | TST_GRP_CD | RPT_GRP_CD | TREATMT_MN | TACTIC_CELL_CD | TREATMT_STRT_DT | TREATMT_END_DT
2025196SLC   | TG1        | PSLCRG01   | 1SLC004A   | IM             | 08Jul2025       | 03Nov2025
2025196SLC   | TG1        | PSLCRG03   | 1SLC005A   | EM_IM          | 08Jul2025       | 03Nov2025
2025196SLC   | TG4        | PSLCRG01   | 1SLC001A   | IM             | 08Jul2025       | 03Nov2025
2025196SLC   | TG4        | PSLCRG03   | 1SLC003A   | EM_IM          | 08Jul2025       | 03Nov2025
2025196SLC   | TG7        | PSLCRG01   | 1SLCNMAA   | XX             | 08Jul2025       | 03Nov2025
2025196SLC   | TG7        | PSLCRG03   | 1SLCNMAA   | XX             | 08Jul2025       | 03Nov2025
```

---

## Document History

- **2026-01-23**: Created based on SLC campaign technical specification screenshots
- Source images: `/context/pics/PXL_20260123_*.jpg`
