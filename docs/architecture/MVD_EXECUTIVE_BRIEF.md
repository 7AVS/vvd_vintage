# Vintage Automation: Executive Brief

## Building Measurement Infrastructure That Scales

**Audience:** Directors, Leadership
**Purpose:** Awareness + Support + Buy-in
**Key Message:** We built something that scales, pays dividends over time, and is ready to deliver value now.

---

## The Problem We Solved

Marketing runs campaigns. We need to measure them. But every measurement request today means:
- Manual data extraction
- Tribal knowledge about "how to calculate success"
- Weeks of work per campaign
- Inconsistent definitions across teams

**We built an engine that changes this.**

---

## What We Built: The Vintage Automation Engine

A modular measurement system based on the **SuperFact 4-Layer Framework**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE 4-LAYER ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   LAYER 1              LAYER 2              LAYER 3              LAYER 4│
│   Experiment           Campaign             Success              Client │
│   Metadata             Metadata             Library              Journey│
│                                                                         │
│   "Who is in          "What metric         "How do we           "What  │
│    the test?"          to measure?"         calculate it?"       did   │
│                                                                  they  │
│                                                                  do?"  │
│                                                                         │
│   ───────────────────────────────────────────────────────────────────  │
│                                    │                                    │
│                                    ▼                                    │
│                          ┌─────────────────┐                           │
│                          │ VINTAGE ENGINE  │                           │
│                          │  (Stable Core)  │                           │
│                          └────────┬────────┘                           │
│                                   │                                     │
│                    ┌──────────────┴──────────────┐                     │
│                    ▼                             ▼                      │
│             ┌─────────────┐               ┌─────────────┐              │
│             │  TRACK A    │   PARALLEL    │  TRACK B    │              │
│             │  Official   │ ◄───────────► │  In-House   │              │
│             │  Tableau    │               │  SharePoint │              │
│             └─────────────┘               └─────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**One engine. Two delivery tracks. Running in parallel.**

---

## Current State: Proven and Ready

| Metric | Status |
|--------|--------|
| Campaigns measured | 6 pilots (VCN, VDA, VDT, VUI, VUT, VAW) |
| Unique success metrics | 4 defined and documented |
| Engine | Built and running |
| Track B (In-House) | Ready now - HTML dashboards on SharePoint |
| Track A (Official) | Pending CIDM alignment |

**We're not waiting. Track B is delivering value today while we align Track A.**

---

## The Virtuous Cycle: Why This Scales

Every campaign we onboard enriches our metadata ecosystem:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE VIRTUOUS CYCLE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    Campaign 1 (VCN)                                                     │
│    └── Defines "card_acquisition" metric                                │
│        └── Documents filters, logic, source tables                      │
│                                                                         │
│    Campaign 2 (VDA)                                                     │
│    └── REUSES "card_acquisition" ✓                                      │
│        └── Zero new metric work needed                                  │
│                                                                         │
│    Campaign 3 (VDT)                                                     │
│    └── Adds "card_activation" to library                                │
│        └── Success Library grows by 1                                   │
│                                                                         │
│    Campaign 6 (VAW)                                                     │
│    └── REUSES "wallet_provisioning" from VUT ✓                          │
│        └── Only config changes, no logic work                           │
│                                                                         │
│    ─────────────────────────────────────────────────────────────────    │
│    RESULT: 6 campaigns measured with only 4 unique metrics              │
│    FUTURE: Campaign 7, 8, 9... become trivial if metrics exist          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**The more we use it, the more valuable it becomes.**

---

## Modular Architecture: Built for the Future

The engine has **swap points** - hardcoded components today that become dynamic when infrastructure matures:

| Layer | Today (Hardcoded) | Future (Dynamic) | Trigger |
|-------|-------------------|------------------|---------|
| Layer 2 | Campaign config in Python dict | Query Mnemonic Mapping v2 | MM v2 has metric fields |
| Layer 3 | Success definitions in code | Success Library (GitHub) | Library established |

**Total: 53 hardcoded items ready to swap when infrastructure is ready.**

The engine core doesn't change - only the inputs swap. This means:
- No re-architecture needed
- Incremental adoption
- Risk-free migration path

---

## Two Tracks: Speed AND Governance

We're not choosing between agility and governance. We're delivering both:

| | Track A (Official) | Track B (In-House) |
|---|---|---|
| **Platform** | Tableau via CIDM | HTML/Plotly on SharePoint |
| **Status** | Pending alignment | Ready NOW |
| **Strength** | Governed, enterprise-trusted | Fast, controlled, iterative |
| **Refresh** | Automated (when aligned) | Manual re-run |
| **Audience** | Leadership, cross-functional | Team, stakeholders |

**Strategic value:**
- Track B proves value immediately, builds credibility
- Track A becomes the official source of truth when aligned
- Same engine feeds both - no duplicate work

---

## What We Need: Support and Buy-In

### From Leadership
1. **Awareness** - Understand what we've built and its strategic value
2. **Support** - Champion this as the measurement standard
3. **Patience** - Track A alignment takes time; Track B delivers now

### From CIDM/Infrastructure
1. **Alignment** - Prioritize integration with Vintage Engine output
2. **Collaboration** - Help define the path to Track A adoption

### From Other Teams
1. **Adoption** - Use the Success Library definitions for consistency
2. **Contribution** - Share metric definitions to grow the library

---

## The Vision: Self-Service Measurement

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            FUTURE STATE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Marketing wants to measure a new campaign:                            │
│                                                                         │
│   1. Look up metric in Success Library          ✓ Already exists        │
│   2. Add row to Mnemonic Mapping v2             ✓ Self-service          │
│   3. Run Vintage Engine                         ✓ No code changes       │
│   4. View results in dashboard                  ✓ Same day              │
│                                                                         │
│   ─────────────────────────────────────────────────────────────────     │
│   Total effort: Minutes, not weeks                                      │
│   Engineering involvement: Zero (for existing metrics)                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

| Priority | Action | Owner | Dependency |
|----------|--------|-------|------------|
| 1 | Continue Track B delivery for 6 pilots | Team | None - ready now |
| 2 | Add new cohorts for existing campaigns | Team | None |
| 3 | Expand metrics (Primary/Secondary/Tertiary) | Team | TBD |
| 4 | Align with CIDM for Track A | Team + CIDM | CIDM prioritization |
| 5 | Formalize Success Library governance | Team | Collaboration |

---

## Summary

**What we built:** A modular measurement engine based on SuperFact 4-layer framework.

**Why it matters:**
- Scales with every campaign onboarded (virtuous cycle)
- Built for the future with swap points
- Delivers value NOW via Track B while aligning Track A

**What we need:** Your awareness, support, and buy-in to make this the measurement standard.

---

*"Every campaign onboarded enriches our metadata ecosystem. We're not just measuring - we're building the source of truth."*
