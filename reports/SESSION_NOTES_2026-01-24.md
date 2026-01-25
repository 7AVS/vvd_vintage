# Session Notes: 2026-01-24

**Dashboard Version:** v2.5 (complete)
**Next Version:** v2.6 (pending)

---

## Current State

### v2.5 Features
- Title: "Vintage Dashboard Pilot"
- Two plots: Test Group Comparison + Report Group Breakdown
- Line styles by index (solid, dashed, dotted, dash-dot)
- Opacity by cohort age
- Cohort dropdown: Most Recent 1, Last 3, Last 6, All
- Test group chips for selection
- KPI cards with lift calculation
- RBC color scheme
- Plot 2 inherits from Plot 1 + Report Group filter

### Files Created
- `reports/dashboard.html` (v2.5)
- `reports/versions/v2.2/` through `v2.5/`
- `reports/DASHBOARD_CODING_RULES.md`

---

## Brainstorming (NOT Confirmed for v2.6)

These are ideas discussed, NOT planned features. User will decide if/when to include.

| Idea | What It Does | Status |
|------|--------------|--------|
| Lift area visualization | Shaded area between curves | Just an idea |
| Data labels on chart | Values at milestones | Just an idea |
| Enhanced tooltips | More info in tooltips | Just an idea |
| Channel breakdown | Like Report Group but for channel | Deferred - need reliable field |

**None of these are committed to v2.6.**

---

## Open Questions

### Channel Field
- `RPT_GRP_CD` - Campaign-specific, not always channel
- `TREATMT_MN` - Campaign-specific codes
- `TACTIC_CELL_CD` - Actual channel codes (IM, EM, XX)
  - But not in current vintage output
  - Control is always XX (no channel)

**Decision:** Deferred. Need to find reliable channel field or add to engine output.

### Control vs Channel Comparison
- Control group has `TACTIC_CELL_CD = XX` (no treatment)
- Cannot fairly compare "TG1 Email" vs "TG7 Email" (TG7 never got email)
- Report Group comparison IS valid (control split by RPT_GRP_CD)

---

## Coding Rules Established

See: `reports/DASHBOARD_CODING_RULES.md`

Key rules:
1. No hardcoded group names (TG1, TG7, etc.)
2. No hardcoded cohort values
3. Derive values from data
4. Use index-based assignment for styles
5. Use RBC color scheme
6. Handle edge cases
7. Recycle styles with modulo when exhausted

---

## Reference Documents

- `docs/architecture/V2.2_OUTPUT_SCHEMA.md` - Engine output format
- `docs/architecture/CAMPAIGN_STRUCTURE_REFERENCE.md` - How campaigns are structured
- `docs/RBC_COLOR_SCHEME.md` - Brand colors

---

## Next Session

Pick up from:
1. Decide on v2.6 features (lift area? data labels? tooltips?)
2. Channel breakdown decision
3. Any other feedback after testing v2.5

---

## Version History

| Version | Key Changes |
|---------|-------------|
| v2.2 | Baseline |
| v2.3 | + Lift calculation, KPI cards |
| v2.4 | + Multi-cohort, dual plots, RBC colors |
| v2.5 | + Line styles, per-plot controls, renamed to Pilot |
| v2.6 | TBD |
