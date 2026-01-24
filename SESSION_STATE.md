# Session State

Last updated: 2026-01-23

## What We Were Doing

Building VVD Vintage Curves Dashboard

## Current File State

| File | Status | Version |
|------|--------|---------|
| vintage_dashboard.py | DELETED | - |
| vvd_dashboard_v0.1.html | TO CREATE | v0.1 |
| engine | ACTIVE | v2.3 |

## Pending Decision

**How should Test vs Control mapping work?**

Three options:
1. **User selects in dashboard** - Dropdown where user picks which group is "Control" (most flexible)
2. **Hardcode mapping per campaign** - Dashboard has a config object mapping TST_GRP_CD to TEST/CONTROL
3. **Add GROUP_TYPE column in engine** - Engine outputs TEST/CONTROL alongside raw codes

Decision needed before implementing lift calculation.

## Next Actions (Priority Order)

1. Decide Test vs Control mapping approach
2. Implement lift calculation
3. Build dashboard prototype as vvd_dashboard_v0.1.html

## Context for Next Session

- Dashboard shows 6 campaigns: VCN, VDA, VDT, VUI, VUT, VAW
- Test vs Control comparison must always be visible
- Toggle between Primary/Secondary metrics
- Filter by cohort, segment, channel

## Workflow Rule

**Consultant reviews EVERY response** - I draft, Consultant challenges, then combined response to user. No exceptions.

---

**To resume:** Say "pick up where we left off" or "continue"
