# Vintage Automation - High Level MVD (Director View)

## Purpose
Single-page diagram showing how Vintage Automation implements the SuperFact 4-layer framework.

## Audience
Director - knows the SuperFact framework well, needs to see how it's being implemented.

---

## ONE-PAGE DIAGRAM: "Vintage Automation Overview"

### Layout (Left to Right Flow)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         VINTAGE AUTOMATION                                               │
│                    Implementing the SuperFact Framework                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌──────────────────────┐                                                              │
│   │   SUPERFACT LAYERS   │                                                              │
│   │                      │                                                              │
│   │  ┌────────────────┐  │         ┌──────────────────┐        ┌──────────────────┐    │
│   │  │ L1: Experiment │──┼────────▶│                  │        │   TRACK A        │    │
│   │  │    Metadata    │  │         │                  │        │   (Official)     │    │
│   │  │   [FROM DATA]  │  │         │    VINTAGE       │        │                  │    │
│   │  └────────────────┘  │         │   AUTOMATION     │───────▶│  • Tableau/CIDM  │    │
│   │                      │         │     ENGINE       │        │  • Governed      │    │
│   │  ┌────────────────┐  │         │                  │        │  • Official      │    │
│   │  │ L2: Campaign   │──┼────────▶│  ┌────────────┐  │        └──────────────────┘    │
│   │  │    Metadata    │  │         │  │ 6 Pilot    │  │                                │
│   │  │  [SWAP POINT]  │  │         │  │ Campaigns  │  │        ┌──────────────────┐    │
│   │  └────────────────┘  │         │  │ VCN VDA    │  │        │   TRACK B        │    │
│   │                      │         │  │ VDT VUI    │  │───────▶│   (In-House)     │    │
│   │  ┌────────────────┐  │         │  │ VUT VAW    │  │        │                  │    │
│   │  │ L3: Success    │──┼────────▶│  └────────────┘  │        │  • HTML/Plotly   │    │
│   │  │    Library     │  │         │                  │        │  • SharePoint    │    │
│   │  │  [SWAP POINT]  │◀─┼─────────│  Vintage Curves  │        │  • Immediate     │    │
│   │  └────────────────┘  │    ▲    │  Lift + CI       │        └──────────────────┘    │
│   │         │            │    │    └──────────────────┘                                │
│   │  ┌────────────────┐  │    │                                                        │
│   │  │ L4: Client     │──┼────┼───▶                                                    │
│   │  │    Journey     │  │    │                                                        │
│   │  │   [FROM DATA]  │  │    │                                                        │
│   │  └────────────────┘  │    │                                                        │
│   │                      │    │                                                        │
│   └──────────────────────┘    │                                                        │
│                               │                                                        │
│   ┌───────────────────────────┴────────────────────────────────────────────────────┐   │
│   │                        VIRTUOUS CYCLE                                           │   │
│   │                                                                                 │   │
│   │    New Campaign ──▶ Define Success ──▶ Add to Library ──▶ Library Grows        │   │
│   │         ▲                                                        │              │   │
│   │         └──── Next Campaign Faster ◀── More Governance ◀─────────┘              │   │
│   │                                                                                 │   │
│   │    Success Library: 4 metrics today → grows with each campaign                  │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │  LEGEND:  [FROM DATA] = Pulling from tactic/ODS tables now                      │   │
│   │           [SWAP POINT] = Hardcoded today, will connect to metadata when ready   │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Visual Elements

### Color Coding (RBC Brand)
| Element | Color | Hex |
|---------|-------|-----|
| FROM DATA layers (L1, L4) | Ocean Blue | #0091DA |
| SWAP POINT layers (L2, L3) | Warm Yellow | #FFC72C |
| Engine | Dark Blue | #003168 |
| Track A | Bright Blue | #0051A5 |
| Track B | Tundra | #07AFBF |
| Virtuous Cycle | Sunburst | #FCA311 |

### Key Visual Features
1. **Left side**: SuperFact 4 layers stacked vertically
2. **Center**: Vintage Automation Engine box with 6 campaigns listed
3. **Right side**: Two output tracks
4. **Bottom**: Virtuous Cycle banner with circular arrow

### Arrows
- Solid arrows from L1, L2, L3, L4 into Engine
- **Special arrow**: L3 has bidirectional arrow (feeds in AND receives updates)
- Two output arrows from Engine to Track A and Track B

---

## Key Messages (One per Section)

| Section | Message |
|---------|---------|
| SuperFact Layers | "Using your 4-layer framework" |
| FROM DATA | "Layers 1 & 4 already pulling from tactic tables" |
| SWAP POINT | "Layers 2 & 3 hardcoded now, designed to swap when metadata ready" |
| Engine | "6 pilot campaigns proving the architecture" |
| Outputs | "Same data feeds both official and in-house dashboards" |
| Virtuous Cycle | "Success Library grows with each campaign" |

---

---

## NEXT STEPS Section (Right Side of Diagram)

### Layout
Compact vertical list on right side showing strategic roadmap.

### Content

**1. Adding New Cohorts** (Ocean Blue header)
*For existing campaigns*
- Track A: Automated refresh with CIDM
- Track B: Re-run engine, update HTML

**2. Expand Metrics & Comparisons** (Sunburst header)
*What else can we vintage?*
- Primary / Secondary / Tertiary success
- Email engagement curves
- Segment breakdowns & comparisons
- **TBD** - needs to be figured out

**3. Hosting & Technology** (Tundra header)
*Where does this live long-term?*
- SharePoint (in-house, quick)
- Tableau/CIDM (official, governed)
- Snowflake / New tech (modern)
- **TBD** - decision pending

**DECISIONS PENDING** (Dark Blue header)
- Refresh cadence (how often?)
- Metric prioritization (what matters?)
- Track A vs Track B balance

### Status Indicators
- ✓ Engine built
- ◐ Dashboard ready
- ○ Decisions pending

### Key Message (Bottom Banner)
"Engine is built. Next steps: refresh process, expand metrics, decide on hosting."

---

## Bottom Line
This is the SuperFact framework in action - a modular engine that pulls what it can from data now, has swap points for future metadata sources, and builds the Success Library as campaigns are added.
