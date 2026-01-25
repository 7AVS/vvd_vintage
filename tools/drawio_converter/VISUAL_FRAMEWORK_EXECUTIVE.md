# Visual Framework: Executive Brief

## Source & Output
**MVD:** `MVD_EXECUTIVE_BRIEF.md`
**Output:** `EXECUTIVE_BRIEF.pptx`

---

## Color Assignments

| Element Category | Treatment |
|-----------------|-----------|
| Layers (L1, L4) - From Data | Border: Ocean Blue (#0091DA) |
| Layers (L2, L3) - Swap Points | Border: Warm Yellow (#FFC72C) |
| Engine (Stable Core) | Fill: Light Gray, Border: Dark Blue |
| Track A / Track B | Border: Gray, equal treatment |
| Key Emphasis (1-2 per slide) | Fill: Sunburst (#FCA311) |
| Future State | Border: Tundra (#07AFBF) |

---

## Slide 1: Title

**Pattern:** Minimal centered title

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                                                                 │
│                    VINTAGE AUTOMATION                           │
│                                                                 │
│           Building Measurement Infrastructure That Scales       │
│                                                                 │
│                         ─────────                               │
│                                                                 │
│                      Executive Brief                            │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- White background
- Dark blue text (centered)
- Simple horizontal line separator
- "Executive Brief" as subtitle in gray
```

---

## Slide 2: The Problem

**Pattern:** Pain points list with visual

```
┌─────────────────────────────────────────────────────────────────┐
│  The Problem We Solved                                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  TODAY: Every measurement request means...                  ││
│  │                                                             ││
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     ││
│  │   │   Manual     │  │   Tribal     │  │   Weeks of   │     ││
│  │   │   Data       │  │   Knowledge  │  │   Work per   │     ││
│  │   │   Extraction │  │   "How to    │  │   Campaign   │     ││
│  │   │              │  │   calculate" │  │              │     ││
│  │   └──────────────┘  └──────────────┘  └──────────────┘     ││
│  │                                                             ││
│  │   Result: Inconsistent definitions across teams             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│                              ▼                                  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  WE BUILT AN ENGINE THAT CHANGES THIS                   │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Problem boxes: gray border, white fill
- "We built" callout: Sunburst border (key emphasis)
```

---

## Slide 3: The 4-Layer Architecture

**Pattern:** Flow diagram - Top to Bottom with branching

```
┌─────────────────────────────────────────────────────────────────┐
│  The Vintage Automation Engine                                  │
│  SuperFact 4-Layer Framework                                    │
│                                                                 │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│   │ Layer 1 │  │ Layer 2 │  │ Layer 3 │  │ Layer 4 │          │
│   │   Who   │  │  What   │  │   How   │  │  What   │          │
│   │   is in │  │ metric? │  │   to    │  │  did    │          │
│   │  test?  │  │         │  │ calc?   │  │ they do?│          │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘          │
│        │            │            │            │                 │
│        └────────────┴─────┬──────┴────────────┘                 │
│                           │                                     │
│                           ▼                                     │
│                  ┌─────────────────┐                           │
│                  │  VINTAGE ENGINE │                           │
│                  │  (Stable Core)  │                           │
│                  └────────┬────────┘                           │
│                           │                                     │
│              ┌────────────┴────────────┐                       │
│              ▼                         ▼                        │
│       ┌─────────────┐           ┌─────────────┐                │
│       │  TRACK A    │  PARALLEL │  TRACK B    │                │
│       │  Tableau    │◄─────────►│  SharePoint │                │
│       └─────────────┘           └─────────────┘                │
│                                                                 │
│   One engine. Two delivery tracks. Running in parallel.        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- L1, L4 boxes: Ocean Blue border (From Data)
- L2, L3 boxes: Warm Yellow border (Swap Points)
- Engine: Light Gray fill, Dark Blue border
- Track A, Track B: Gray border, equal weight
- "PARALLEL" label between tracks
- Key message at bottom: Dark blue, bold
```

---

## Slide 4: Current State

**Pattern:** Status dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  Current State: Proven and Ready                                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │ │
│  │   │     6       │   │     4       │   │   Engine    │    │ │
│  │   │  Campaigns  │   │   Metrics   │   │   Built     │    │ │
│  │   │  Measured   │   │  Defined    │   │     ✓       │    │ │
│  │   │             │   │             │   │             │    │ │
│  │   │ VCN VDA VDT │   │ card_acq    │   │             │    │ │
│  │   │ VUI VUT VAW │   │ card_act    │   │             │    │ │
│  │   │             │   │ card_use    │   │             │    │ │
│  │   │             │   │ wallet_prov │   │             │    │ │
│  │   └─────────────┘   └─────────────┘   └─────────────┘    │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│   ┌─────────────────────────┐   ┌─────────────────────────┐   │
│   │  Track A: Pending       │   │  Track B: Ready NOW     │   │
│   │  Alignment with CIDM    │   │  HTML on SharePoint     │   │
│   └─────────────────────────┘   └─────────────────────────┘   │
│                                                                 │
│   We're not waiting. Track B delivers value TODAY.             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Metric boxes: gray border
- Track B "Ready NOW": Tundra border (emphasis)
- Track A "Pending": gray border
- Bottom message: bold
```

---

## Slide 5: The Virtuous Cycle

**Pattern:** Cycle + Timeline growth

```
┌─────────────────────────────────────────────────────────────────┐
│  The Virtuous Cycle: Why This Scales                            │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  THE CYCLE                                                 │ │
│  │                                                           │ │
│  │   ┌──────────┐    ┌──────────┐    ┌──────────┐           │ │
│  │   │   New    │ ─► │  Define  │ ─► │  Add to  │           │ │
│  │   │ Campaign │    │  Metric  │    │  Library │           │ │
│  │   └──────────┘    └──────────┘    └─────┬────┘           │ │
│  │        ▲                                │                 │ │
│  │        │          ┌──────────┐          │                 │ │
│  │        └───────── │   Next   │ ◄────────┘                 │ │
│  │                   │  Faster  │                            │ │
│  │                   └──────────┘                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  GROWTH: 6 campaigns, only 4 unique metrics               │ │
│  │                                                           │ │
│  │  VCN ──► defines card_acq                                 │ │
│  │  VDA ──► reuses card_acq ✓                                │ │
│  │  VDT ──► adds card_act                                    │ │
│  │  VAW ──► reuses wallet_prov ✓                             │ │
│  │                                                           │ │
│  │  Campaign 7, 8, 9... become trivial if metrics exist      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Cycle: gray arrows, "Add to Library" box: Sunburst border (key moment)
- "Next Faster" box: Tundra border
- Growth section: gray container
- Reused items: checkmark, muted color
- New items: Tundra tag
```

---

## Slide 6: Modular Architecture (Swap Points)

**Pattern:** Today → Future transformation

```
┌─────────────────────────────────────────────────────────────────┐
│  Modular Architecture: Built for the Future                     │
│                                                                 │
│  53 hardcoded items → Dynamic when infrastructure ready         │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  LAYER 2: Campaign Metadata                                │ │
│  │                                                           │ │
│  │   TODAY                          FUTURE                   │ │
│  │   ┌──────────────┐              ┌──────────────┐         │ │
│  │   │ Python dict  │    ────►     │ Query        │         │ │
│  │   │ 6 campaigns  │    SWAP      │ Mnemonic     │         │ │
│  │   │ hardcoded    │              │ Mapping v2   │         │ │
│  │   └──────────────┘              └──────────────┘         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  LAYER 3: Success Definitions                              │ │
│  │                                                           │ │
│  │   TODAY                          FUTURE                   │ │
│  │   ┌──────────────┐              ┌──────────────┐         │ │
│  │   │ Filters in   │    ────►     │ Success      │         │ │
│  │   │ code (24     │    SWAP      │ Library      │         │ │
│  │   │ items)       │              │ (GitHub)     │         │ │
│  │   └──────────────┘              └──────────────┘         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│   Engine core doesn't change - only the inputs swap            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Section containers: Warm Yellow border (swap point indicator)
- TODAY boxes: gray border
- FUTURE boxes: Tundra border
- SWAP arrows: Sunburst color
```

---

## Slide 7: Two Tracks

**Pattern:** Side-by-side comparison

```
┌─────────────────────────────────────────────────────────────────┐
│  Two Tracks: Speed AND Governance                               │
│                                                                 │
│  One engine feeds both. We're not choosing - we get BOTH.      │
│                                                                 │
│  ┌───────────────────────────┐   ┌───────────────────────────┐ │
│  │                           │   │                           │ │
│  │     TRACK A               │   │     TRACK B               │ │
│  │     Official              │   │     In-House              │ │
│  │                           │   │                           │ │
│  │  Platform:                │   │  Platform:                │ │
│  │  Tableau via CIDM         │   │  HTML/Plotly + SharePoint │ │
│  │                           │   │                           │ │
│  │  Status:                  │   │  Status:                  │ │
│  │  Pending alignment        │   │  READY NOW                │ │
│  │                           │   │                           │ │
│  │  Strength:                │   │  Strength:                │ │
│  │  Governed, trusted        │   │  Fast, controlled         │ │
│  │                           │   │                           │ │
│  │  Refresh:                 │   │  Refresh:                 │ │
│  │  Automated (when ready)   │   │  Manual re-run            │ │
│  │                           │   │                           │ │
│  └───────────────────────────┘   └───────────────────────────┘ │
│                                                                 │
│              ◄──────── PARALLEL ────────►                       │
│                                                                 │
│   Track B proves value NOW. Track A becomes official when ready.│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Both tracks: equal width, equal treatment (gray border)
- Track B "READY NOW": Tundra text color
- "PARALLEL" label: centered, bold
- Bottom message: key takeaway
```

---

## Slide 8: What We Need

**Pattern:** Three pillars (asks)

```
┌─────────────────────────────────────────────────────────────────┐
│  What We Need: Support and Buy-In                               │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │                 │  │                 │  │                 │ │
│  │  LEADERSHIP     │  │  CIDM /         │  │  OTHER          │ │
│  │                 │  │  INFRASTRUCTURE │  │  TEAMS          │ │
│  │  • Awareness    │  │                 │  │                 │ │
│  │  • Support      │  │  • Alignment    │  │  • Adoption     │ │
│  │  • Champion     │  │  • Prioritize   │  │  • Contribute   │ │
│  │    this as      │  │    integration  │  │    definitions  │ │
│  │    standard     │  │  • Collaborate  │  │  • Use Success  │ │
│  │                 │  │                 │  │    Library      │ │
│  │                 │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Three pillars: equal width, gray border
- Headers: Light gray fill
```

---

## Slide 9: The Vision

**Pattern:** Future state callout

```
┌─────────────────────────────────────────────────────────────────┐
│  The Vision: Self-Service Measurement                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      FUTURE STATE                          │ │
│  │                                                           │ │
│  │   Marketing wants to measure a new campaign:              │ │
│  │                                                           │ │
│  │   1. Look up metric in Success Library    ✓ Already exists│ │
│  │   2. Add row to Mnemonic Mapping v2       ✓ Self-service  │ │
│  │   3. Run Vintage Engine                   ✓ No code change│ │
│  │   4. View results in dashboard            ✓ Same day      │ │
│  │                                                           │ │
│  │   ─────────────────────────────────────────────────────   │ │
│  │   Total effort: MINUTES, not weeks                        │ │
│  │   Engineering involvement: ZERO (for existing metrics)    │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  "Every campaign onboarded enriches our metadata          │ │
│  │   ecosystem. We're not just measuring - we're building    │ │
│  │   the source of truth."                                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Future state box: Sunburst border (key emphasis)
- Checkmarks: Tundra color
- MINUTES, ZERO: bold
- Quote at bottom: italic, dark blue
```

---

## Implementation Notes

1. **9 slides total** - concise for executive attention
2. **Color budget per slide:** 1-2 accent elements max
3. **Flow:** Problem → Solution → Proof → Vision → Ask
4. **Key messages reinforced:** Virtuous cycle, parallel tracks, scales over time
