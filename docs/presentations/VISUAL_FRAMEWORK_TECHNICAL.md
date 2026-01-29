# Visual Framework: Technical Onboarding

## Source & Output
**MVD:** `MVD_TECHNICAL_ONBOARDING.md`
**Output:** `TECHNICAL_ONBOARDING.pptx`

---

## Color Assignments

| Element Category | Treatment |
|-----------------|-----------|
| Layers (L1, L4) - From Data | Border: Ocean Blue (#0091DA) |
| Layers (L2, L3) - Swap Points | Border: Warm Yellow (#FFC72C) |
| Engine (Stable Core) | Fill: Light Gray, Border: Dark Blue |
| Code/Technical details | Monospace font, gray background |
| YOUR Opportunity callouts | Fill: Sunburst (#FCA311) |
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
│               Technical Onboarding Guide                        │
│                                                                 │
│                         ─────────                               │
│                                                                 │
│             Join Us in Building the Measurement Standard        │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- White background
- Dark blue text (centered)
- Subtitle: inspiring tone
```

---

## Slide 2: Why This Matters to YOU

**Pattern:** Problem statement with code example

```
┌─────────────────────────────────────────────────────────────────┐
│  Why This Matters to YOU                                        │
│                                                                 │
│  You've probably done this before:                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Someone asks: "How many cards acquired for campaign X?"  │ │
│  │                                                           │ │
│  │     You                        Someone else               │ │
│  │     ┌─────────────┐            ┌─────────────┐           │ │
│  │     │ Write SQL   │            │ Write SQL   │           │ │
│  │     │ Find tables │            │ Find tables │           │ │
│  │     │ Add filters │            │ Add filters │           │ │
│  │     └──────┬──────┘            └──────┬──────┘           │ │
│  │            │                          │                   │ │
│  │            ▼                          ▼                   │ │
│  │     ┌─────────────┐            ┌─────────────┐           │ │
│  │     │  Answer A   │     ≠      │  Answer B   │           │ │
│  │     │  Different  │            │  Different  │           │ │
│  │     │  filters    │            │  filters    │           │ │
│  │     └─────────────┘            └─────────────┘           │ │
│  │                                                           │ │
│  │          Same question. Different answers. 🤔             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│   We're fixing this. And we need your help.                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Problem box: gray border
- "Answer A" / "Answer B" boxes: red-ish border (problem indicator)
- Bottom message: bold, Sunburst color
```

---

## Slide 3: The 4-Layer Architecture (Detailed)

**Pattern:** Full architecture diagram with code references

```
┌─────────────────────────────────────────────────────────────────┐
│  The Architecture: SuperFact 4-Layer Framework                  │
│  vintage_all_in_one.py                                          │
│                                                                 │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║  LAYER 1: EXPERIMENT METADATA                              ║ │
│  ║  "Who is in the test?"                                     ║ │
│  ║  Code: load_tactic()  |  Config: YEARS, TEST_GROUP_CODE    ║ │
│  ║  Swap to: → Experiment Metadata table                      ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
│                              │                                  │
│                              ▼                                  │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║  LAYER 2: CAMPAIGN METADATA                                ║ │
│  ║  "What metric to measure?"                                 ║ │
│  ║  Code: get_campaign_config()  |  Config: CAMPAIGN_METADATA ║ │
│  ║  Swap to: → Mnemonic Mapping v2 query                      ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
│                              │                                  │
│                              ▼                                  │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║  LAYER 3: SUCCESS DEFINITIONS                              ║ │
│  ║  "How to calculate?"                                       ║ │
│  ║  Code: get_success_definition()  |  Config: SUCCESS_DEFS   ║ │
│  ║  Swap to: → Success Library (GitHub or curated data)       ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
│                              │                                  │
│                              ▼                                  │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║  LAYER 4: CLIENT JOURNEY                                   ║ │
│  ║  "What did they actually do?"                              ║ │
│  ║  Code: load_fulfillment(), load_email_engagement(),...     ║ │
│  ║  Swap to: → Unified Client Journey semantic layer          ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- L1, L4: Ocean Blue border
- L2, L3: Warm Yellow border
- Code references: monospace, gray
```

---

## Slide 4: Engine + Two Tracks

**Pattern:** Flow with branching to parallel outputs

```
┌─────────────────────────────────────────────────────────────────┐
│  Engine + Delivery Tracks                                       │
│                                                                 │
│                    4 LAYERS                                     │
│                        │                                        │
│                        ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  VINTAGE ENGINE (Stable - does NOT change)              │  │
│   │                                                         │  │
│   │  detect_success() → build_vintage_data()                │  │
│   │  → calculate_ci() → prepare_vintage_table()             │  │
│   │  → generate_summary() → plot_vintage()                  │  │
│   │                                                         │  │
│   │  This block doesn't care WHERE data comes from.         │  │
│   └─────────────────────────┬───────────────────────────────┘  │
│                             │                                   │
│                     CSV / HDFS                                  │
│                             │                                   │
│              ┌──────────────┴──────────────┐                   │
│              ▼                             ▼                    │
│       ┌─────────────┐               ┌─────────────┐            │
│       │  TRACK A    │   PARALLEL    │  TRACK B    │            │
│       │  Tableau    │ ◄───────────► │  SharePoint │            │
│       │  CIDM       │               │  HTML/Plotly│            │
│       │  (pending)  │               │  (ready)    │            │
│       └─────────────┘               └─────────────┘            │
│                                                                 │
│   Same engine feeds BOTH. No duplicate work.                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Engine box: Light Gray fill, Dark Blue border
- Function names: monospace
- Track A, Track B: equal, gray border
- "PARALLEL" emphasized
```

---

## Slide 5: Swap Point - Layer 2

**Pattern:** Code transformation (Today → Future)

```
┌─────────────────────────────────────────────────────────────────┐
│  Swap Point: Layer 2 - Campaign Metadata                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  TODAY (hardcoded)                                        │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ CAMPAIGN_METADATA = {                               │ │ │
│  │  │     "VCN": {                                        │ │ │
│  │  │         "campaign_name": "VVD Contextual...",       │ │ │
│  │  │         "success_type": "ACQUISITION",              │ │ │
│  │  │         "primary_metric": "card_acquisition",       │ │ │
│  │  │     },                                              │ │ │
│  │  │     # ... 6 campaigns hardcoded                     │ │ │
│  │  │ }                                                   │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                         SWAP ▼                                  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  FUTURE (dynamic)                                         │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ config = spark.sql("""                              │ │ │
│  │  │     SELECT primary_metric, secondary_metric         │ │ │
│  │  │     FROM mnemonic_mapping_v2                        │ │ │
│  │  │     WHERE mne = 'VCN'                               │ │ │
│  │  │ """)                                                │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  YOUR OPPORTUNITY: Enhancing MM v2 with metric fields?    │ │
│  │  The engine will automatically use your work.             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- TODAY box: Warm Yellow border
- Code: monospace, light gray background
- FUTURE box: Tundra border
- YOUR OPPORTUNITY: Sunburst fill (key callout)
```

---

## Slide 6: Swap Point - Layer 3 (The Big One)

**Pattern:** Code transformation with options

```
┌─────────────────────────────────────────────────────────────────┐
│  Swap Point: Layer 3 - Success Definitions (THE BIG ONE)        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  TODAY                                                    │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ SUCCESS_DEFINITIONS = {                             │ │ │
│  │  │     "card_acquisition": {                           │ │ │
│  │  │         "table_path": "/prod/.../VISA_DR_CRD/",     │ │ │
│  │  │         "filters": {"STS_CD": ["06","08"],          │ │ │
│  │  │                     "SRVC_ID": 36},                 │ │ │
│  │  │     }, # ... 4 metrics × 6 fields = 24 items        │ │ │
│  │  │ }                                                   │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                         SWAP ▼                                  │
│                                                                 │
│  ┌──────────────────────────┐  ┌──────────────────────────┐   │
│  │  FUTURE: Option A        │  │  FUTURE: Option B        │   │
│  │  GitHub %Run             │  │  Curated Data            │   │
│  │  ┌────────────────────┐  │  │  ┌────────────────────┐  │   │
│  │  │ %run /success_lib/ │  │  │  │ spark.read.parquet │  │   │
│  │  │   card_acquisition │  │  │  │ ("/semantic/       │  │   │
│  │  │   .py              │  │  │  │  card_acquisition")│  │   │
│  │  └────────────────────┘  │  │  └────────────────────┘  │   │
│  └──────────────────────────┘  └──────────────────────────┘   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  YOUR OPPORTUNITY: Have metric definitions? Curated data? │ │
│  │  Share them! They become the standard.                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- TODAY box: Warm Yellow border
- FUTURE options: Tundra border, side by side
- YOUR OPPORTUNITY: Sunburst fill
```

---

## Slide 7: The Virtuous Cycle (Technical View)

**Pattern:** Linear growth showing reuse

```
┌─────────────────────────────────────────────────────────────────┐
│  The Virtuous Cycle: Why Your Contribution Matters              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │   You define "card_acquisition" once                      │ │
│  │              │                                            │ │
│  │              ▼                                            │ │
│  │   It goes in the Success Library                          │ │
│  │              │                                            │ │
│  │              ▼                                            │ │
│  │   Campaign 1 uses it ✓                                    │ │
│  │   Campaign 2 uses it ✓  (no new work!)                    │ │
│  │   Campaign 5 uses it ✓  (still no new work!)              │ │
│  │              │                                            │ │
│  │              ▼                                            │ │
│  │   Another team needs "card_acquisition"?                  │ │
│  │   They use YOUR definition.                               │ │
│  │   Consistency. Trust. YOUR name on it.                    │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  RESULT: Define once, reuse forever                       │ │
│  │  YOUR CONTRIBUTION: Multiplied across the organization    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Flow: vertical, gray arrows
- Checkmarks: Tundra color
- RESULT box: Sunburst border
```

---

## Slide 8: 59 Swap Points Summary

**Pattern:** Table with layer breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│  What's Hardcoded Today: 59 Items Ready to Swap                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Layer    │ Hardcoded Items          │ Count │ Swaps To     ││
│  ├───────────┼──────────────────────────┼───────┼──────────────┤│
│  │  Layer 1  │ Years, test group, path  │   3   │ Experiment   ││
│  │           │                          │       │ Metadata     ││
│  ├───────────┼──────────────────────────┼───────┼──────────────┤│
│  │  Layer 2  │ Campaign config          │  24   │ Mnemonic     ││
│  │           │ (6 campaigns × 4 fields) │       │ Mapping v2   ││
│  ├───────────┼──────────────────────────┼───────┼──────────────┤│
│  │  Layer 3  │ Success definitions      │  24   │ Success      ││
│  │           │ (4 metrics × 6 fields)   │       │ Library      ││
│  ├───────────┼──────────────────────────┼───────┼──────────────┤│
│  │  Layer 4  │ Paths, EDW queries       │   8   │ Semantic     ││
│  │           │                          │       │ Layers       ││
│  ├───────────┼──────────────────────────┼───────┼──────────────┤│
│  │  TOTAL    │                          │  59   │              ││
│  └───────────┴──────────────────────────┴───────┴──────────────┘│
│                                                                 │
│   59 items ready to swap when YOUR work is ready.              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Table: clean, gray borders
- Layer 1, 4 rows: Ocean Blue left border
- Layer 2, 3 rows: Warm Yellow left border
- TOTAL row: bold
- Bottom message: Sunburst color
```

---

## Slide 9: How to Contribute

**Pattern:** Four paths

```
┌─────────────────────────────────────────────────────────────────┐
│  How to Contribute                                              │
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │  IF YOU HAVE...      │  │  DO THIS...          │            │
│  ├──────────────────────┼──────────────────────────┤            │
│  │                      │                          │            │
│  │  Metric definition   │  Document filters +      │            │
│  │                      │  tables, share with us   │            │
│  │                      │  → Goes in Success Lib   │            │
│  │                      │                          │            │
│  ├──────────────────────┼──────────────────────────┤            │
│  │                      │                          │            │
│  │  Curated data set    │  Share path + schema     │            │
│  │                      │  → Engine points to it   │            │
│  │                      │                          │            │
│  ├──────────────────────┼──────────────────────────┤            │
│  │                      │                          │            │
│  │  Semantic layer      │  Tell us when ready      │            │
│  │                      │  → We flip the switch    │            │
│  │                      │                          │            │
│  ├──────────────────────┼──────────────────────────┤            │
│  │                      │                          │            │
│  │  "The right way"     │  Tell us! Document it    │            │
│  │  to calculate        │  → Tribal knowledge      │            │
│  │  something           │     becomes standard     │            │
│  │                      │                          │            │
│  └──────────────────────┴──────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- Table: clean layout
- Left column: bold, gray background
- Right column: action-oriented
- Arrows (→): Tundra color
```

---

## Slide 10: The Ask

**Pattern:** Call to action with benefits

```
┌─────────────────────────────────────────────────────────────────┐
│  The Ask: Join Us                                               │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  WE NEED YOU TO:                                          │ │
│  │                                                           │ │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │ │
│  │   │  SHARE  │  │COLLAB-  │  │  ADOPT  │  │CONTRIB- │     │ │
│  │   │         │  │  ORATE  │  │         │  │   UTE   │     │ │
│  │   │ Your    │  │ Fill    │  │ Use the │  │ Your    │     │ │
│  │   │ metric  │  │ gaps in │  │ standard│  │ semantic│     │ │
│  │   │ defs    │  │ Success │  │ instead │  │ layers  │     │ │
│  │   │         │  │ Library │  │ of own  │  │ plug in │     │ │
│  │   └─────────┘  └─────────┘  └─────────┘  └─────────┘     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  WHAT YOU GET:                                            │ │
│  │                                                           │ │
│  │  • Your definitions become THE standard                   │ │
│  │  • Your work gets reused across campaigns                 │ │
│  │  • Less "can you pull this data?" requests                │ │
│  │  • Consistency across the entire team                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  "We're not just measuring campaigns. We're building the       │
│   metadata ecosystem that makes measurement easy for everyone."│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Treatment:
- WE NEED YOU: four pillars, equal weight
- WHAT YOU GET: bullet list, checkmarks
- Quote at bottom: italic, centered
```

---

## Implementation Notes

1. **10 slides** - more detail than executive version
2. **Code examples:** Use monospace font, light gray background
3. **YOUR OPPORTUNITY:** Sunburst fill boxes - these are the key callouts
4. **Technical details:** Include function names, line numbers, etc.
5. **Tone:** Collaborative, inspiring - "join us" not "here's what we did"
