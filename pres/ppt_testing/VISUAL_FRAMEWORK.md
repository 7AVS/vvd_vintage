# Visual Framework: Vintage Automation
## Diagram-First Thinking → PowerPoint Translation

**Source:** `../VINTAGE_AUTOMATION_MVD.md`
**Output:** `VINTAGE_AUTOMATION_v2.pptx`

---

## Color Philosophy: Minimalist Approach

### Hierarchy
```
PRIMARY (structure)     → White/Light Gray backgrounds
SECONDARY (text)        → Dark Blue (#003168)
ACCENT (emphasis)       → Used sparingly, 1-2 per slide
```

### When to Use Color
| Element | Treatment |
|---------|-----------|
| Backgrounds | White or Light Gray only |
| Boxes (default) | White fill + Dark Blue border |
| Headers/Titles | Dark Blue text, no fill |
| Key callouts | Border color ONLY (no fill) |
| Critical emphasis | Full color fill (1-2 per slide max) |
| Arrows/Flow | Thin, gray or light blue |

### Accent Colors (use sparingly)
| Purpose | Color | Usage |
|---------|-------|-------|
| "From Data" | Ocean Blue (#0091DA) | Border or small tag |
| "Swap Point" | Warm Yellow (#FFC72C) | Border or small tag |
| "Key Insight" | Sunburst (#FCA311) | One callout per slide |
| "Future/Growth" | Tundra (#07AFBF) | Subtle accent |

---

## Slide 1: Title

**Visual concept:** Clean, minimal, professional

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                                                                 │
│                    VINTAGE AUTOMATION                           │
│                                                                 │
│              Implementing the SuperFact Framework               │
│                                                                 │
│                         ─────────                               │
│                                                                 │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- White background
- Dark blue text (centered)
- Simple horizontal line as separator
- No boxes, no colors
```

---

## Slide 2: Big Picture

**Visual concept:** Flow diagram - LEFT to RIGHT

```
┌─────────────────────────────────────────────────────────────────┐
│  Vintage Automation - The Big Picture                           │
│                                                                  │
│                                                                  │
│   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                         │
│   │ L1  │   │ L2  │   │ L3  │   │ L4  │     SUPERFACT           │
│   │     │   │     │   │     │   │     │     LAYERS              │
│   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘                         │
│      │         │         │         │                             │
│      └─────────┴────┬────┴─────────┘                             │
│                     │                                            │
│                     ▼                                            │
│            ┌────────────────┐                                    │
│            │    ENGINE      │                                    │
│            │  6 Campaigns   │                                    │
│            └───────┬────────┘                                    │
│                    │                                             │
│           ┌────────┴────────┐                                    │
│           ▼                 ▼                                    │
│     ┌──────────┐      ┌──────────┐                              │
│     │ Track A  │      │ Track B  │      OUTPUT                  │
│     │ Official │      │ In-House │      TRACKS                  │
│     └──────────┘      └──────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Flow elements:
- 4 Layer boxes at top (white + border)
- Arrows converging down to Engine
- Engine box (slightly emphasized - light gray fill)
- Arrows diverging to two tracks
- Track boxes (white + border)

Color usage:
- L1, L4 boxes: Ocean Blue BORDER only
- L2, L3 boxes: Warm Yellow BORDER only
- Small tags next to boxes: "FROM DATA" / "SWAP POINT"
- Everything else: white/gray
```

### Spatial relationships to preserve:
1. **Layers are INPUTS** → flow INTO the engine
2. **Engine is CENTRAL** → the transformation point
3. **Tracks are OUTPUTS** → flow OUT from engine
4. **L1/L4 vs L2/L3** → visually distinct (border color)

---

## Slide 3: Virtuous Cycle

**Visual concept:** CIRCULAR flow + GROWTH timeline

```
┌─────────────────────────────────────────────────────────────────┐
│  The Virtuous Cycle                                              │
│                                                                  │
│       ┌──────────────────────────────────────────────────┐      │
│       │                                                   │      │
│       │    ┌─────────┐                                   │      │
│       │    │   New   │                                   │      │
│       │    │Campaign │                                   │      │
│       │    └────┬────┘                                   │      │
│       │         │                                        │      │
│       │         ▼                                        │      │
│       │    ┌─────────┐      ┌─────────┐                 │      │
│       │    │ Define  │ ───► │ Add to  │                 │      │
│       │    │ Success │      │ Library │                 │      │
│       │    └─────────┘      └────┬────┘                 │      │
│       │                          │                       │      │
│       │    ┌─────────┐           │                       │      │
│       │    │  Next   │ ◄─────────┘                       │      │
│       │    │ Faster  │     Library Grows                 │      │
│       │    └─────────┘                                   │      │
│       │         │                                        │      │
│       └─────────┼────────────────────────────────────────┘      │
│                 │                                                │
│                 └───────────► (loops back)                       │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  Campaign 1     Campaign 2     Campaign 3     ...    Campaign 6  │
│  [metric 1]     [reuse]        [+metric 2]           [4 metrics] │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Flow elements:
- Circular flow in top half (the cycle)
- Linear timeline in bottom half (growth)
- Arrows showing the loop

Spatial relationships:
1. **Cycle is CIRCULAR** → shows repetition
2. **Timeline is LINEAR** → shows growth over time
3. **Metrics ACCUMULATE** → visual stacking

Color usage:
- Cycle arrows: light gray, thin
- "Library Grows" step: Sunburst BORDER (the key moment)
- Timeline: subtle, metrics as small tags
- NEW metrics: Tundra border
- REUSED metrics: Gray (muted)
```

---

## Slide 4: Swap Points

**Visual concept:** TODAY → FUTURE transformation

```
┌─────────────────────────────────────────────────────────────────┐
│  Swap Points - Modular Architecture                              │
│                                                                  │
│  The engine has "swap points" - hardcoded today, dynamic later   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ LAYER 2: Campaign Metadata                                   ││
│  │                                                              ││
│  │   TODAY                          FUTURE                      ││
│  │   ┌──────────────┐              ┌──────────────┐            ││
│  │   │ Hardcoded    │    ────►     │ Query from   │            ││
│  │   │ Python dict  │    SWAP      │ Mnemonic     │            ││
│  │   │              │              │ Mapping v2   │            ││
│  │   └──────────────┘              └──────────────┘            ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ LAYER 3: Success Definitions                                 ││
│  │                                                              ││
│  │   TODAY                          FUTURE                      ││
│  │   ┌──────────────┐              ┌──────────────┐            ││
│  │   │ Hardcoded    │    ────►     │ Success      │            ││
│  │   │ filters &    │    SWAP      │ Library      │            ││
│  │   │ paths        │              │ (GitHub/DB)  │            ││
│  │   └──────────────┘              └──────────────┘            ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  KEY: Engine core doesn't change - only the inputs swap          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Flow elements:
- Two horizontal transformation flows
- TODAY → SWAP ARROW → FUTURE
- Container boxes for each layer

Spatial relationships:
1. **LEFT = TODAY** (current state)
2. **RIGHT = FUTURE** (target state)
3. **ARROW = transformation** (the swap)

Color usage:
- TODAY boxes: Warm Yellow BORDER (swap point indicator)
- FUTURE boxes: Tundra BORDER (future state)
- "SWAP" arrow: Sunburst color (the action)
- Everything else: white/gray
- Section headers: Dark Blue text only (no fill)
```

---

## Slide 5: Next Steps

**Visual concept:** Three pillars + decisions below

```
┌─────────────────────────────────────────────────────────────────┐
│  Next Steps                                                      │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │                 │  │                 │  │                 │  │
│  │  1. COHORTS     │  │  2. METRICS     │  │  3. HOSTING     │  │
│  │                 │  │                 │  │                 │  │
│  │  Add new        │  │  Expand what    │  │  Where does     │  │
│  │  cohorts for    │  │  we measure:    │  │  this live?     │  │
│  │  existing       │  │                 │  │                 │  │
│  │  campaigns      │  │  • Primary      │  │  • SharePoint   │  │
│  │                 │  │  • Secondary    │  │  • Tableau      │  │
│  │  Track A: auto  │  │  • Engagement   │  │  • Snowflake    │  │
│  │  Track B: manual│  │  • Segments     │  │                 │  │
│  │                 │  │                 │  │  [TBD]          │  │
│  │                 │  │  [TBD]          │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ─────────────────────────────────────────────────────────────   │
│                                                                  │
│  DECISIONS PENDING:                                              │
│  • Refresh cadence   • Metric priority   • Track A vs B         │
│                                                                  │
│  ─────────────────────────────────────────────────────────────   │
│  STATUS: ✓ Engine built  ◐ Dashboard ready  ○ Decisions pending │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Flow elements:
- Three equal pillars (the strategic areas)
- Horizontal line separator
- Decisions as simple list
- Status as simple indicators

Spatial relationships:
1. **Three pillars = equal weight** (no hierarchy)
2. **Below = supporting info** (decisions, status)

Color usage:
- Pillar headers: Dark Blue text, light gray background
- [TBD] tags: Warm Yellow text (needs decision)
- Status indicators: minimal color (✓ green, ◐ yellow, ○ gray)
- Everything else: white background, dark blue text
```

---

## Slide 6: High-Level One-Pager

**Visual concept:** Everything on one slide - summary view

```
┌─────────────────────────────────────────────────────────────────┐
│  VINTAGE AUTOMATION - Summary                                    │
│                                                                  │
│  ┌────────────┐                                                  │
│  │ LAYERS     │ ──► ┌──────────┐ ──► ┌──────────┐               │
│  │ 1,2,3,4    │     │  ENGINE  │     │ OUTPUTS  │               │
│  └────────────┘     └──────────┘     │ A & B    │               │
│                                       └──────────┘               │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  VIRTUOUS CYCLE: Campaign → Define → Library → Faster       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  SWAP POINTS: L2 & L3 hardcoded today → Dynamic when ready      │
│                                                                  │
│  NEXT: Cohorts | Metrics | Hosting                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Ultra-minimal
- Simple flow diagram
- One-line summaries
- No heavy colors
```

---

## Translation Rules: Diagram → PowerPoint

### Arrows and Flows
| Diagram | PowerPoint |
|---------|------------|
| Vertical arrow ↓ | Connector shape or "▼" text |
| Horizontal arrow → | Connector shape or "→" text |
| Curved/loop arrow | Describe with layout position |

### Containers
| Diagram | PowerPoint |
|---------|------------|
| Container with children | Group of shapes with header |
| Nested boxes | Layered rectangles |

### Emphasis
| Diagram | PowerPoint |
|---------|------------|
| Full color fill | Use ONLY for 1-2 key items per slide |
| Color border | Primary emphasis method |
| Bold text | Secondary emphasis |
| Gray/muted | De-emphasis |

---

## Implementation Notes

1. **White space matters** - Don't crowd, let elements breathe
2. **Alignment** - Everything grid-aligned, no random positions
3. **Consistency** - Same treatment for same type of element
4. **Flow direction** - Clear visual path (usually top→bottom or left→right)
5. **Color budget** - Max 2-3 colored elements per slide
