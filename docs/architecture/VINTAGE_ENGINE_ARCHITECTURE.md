# Vintage Engine: Complete Architecture

## Document Purpose

This is the **single source of truth** for the Vintage Engine architecture. It covers naming conventions, module structure, the three maturity stages, and the end-game vision.

---

## Two Levels of Abstraction

| Level | Scope | Components |
|-------|-------|------------|
| **SuperFact Pillars** | Team-wide strategic initiatives | 4 Pillars |
| **Vintage Engine** | Our implementation | Context Layer + Analysis Layer |

---

## SuperFact Pillars (Team-Wide)

These are **parallel workstreams** the team is building:

| # | Pillar | Purpose | Key Question |
|---|--------|---------|--------------|
| 1 | **Experiment Metadata** | Standardized test/client identification | "Who is in the test?" |
| 2 | **Campaign Metadata (MM v2)** | Enhanced mnemonic mapping | "What metric to measure?" |
| 3 | **Success Library (SoT)** | Curated metric definitions | "How to calculate success?" |
| 4 | **Client Journey** | End-to-end touchpoint mapping | "What did they do?" |

---

## Vintage Engine Architecture

The engine has two main layers:

```
┌─────────────────────────────────────────────────────────────────┐
│  CONTEXT LAYER (Upgradable Modules)                             │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │Experiment│ │ Campaign │ │ Success  │ │Enrichment│ │Journey ││
│  │  Module  │ │  Module  │ │  Module  │ │  Module  │ │ Module ││
│  │          │ │(upgrade) │ │(upgrade) │ │(optional)│ │        ││
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘│
│       └────────────┴────────────┴────────────┴───────────┘     │
│                              │                                  │
│                    STANDARDIZED DATA                            │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  ANALYSIS LAYER (Pluggable Engines)                             │
│                                                                 │
│  ┌──────────────┐  ┌ ─ ─ ─ ─ ─ ─ ┐  ┌ ─ ─ ─ ─ ─ ─ ┐            │
│  │   VINTAGE    │     Future          Future                    │
│  │    ENGINE    │  │   Engine    │  │   Engine    │            │
│  │   (built)    │     (slot)          (slot)                    │
│  └──────┬───────┘  └ ─ ─ ─ ─ ─ ─ ┘  └ ─ ─ ─ ─ ─ ─ ┘            │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │    OUTPUT    │                                               │
│  │  (Adaptive)  │                                               │
│  └──────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             ┌───────────┐         ┌───────────┐
             │  TRACK A  │PARALLEL │  TRACK B  │
             │  Tableau  │◄───────►│ SharePoint│
             └───────────┘         └───────────┘
```

---

## Context Layer: The 5 Modules

### Module 1: Experiment Module
| Attribute | Value |
|-----------|-------|
| **Question** | "Who is in the test?" |
| **Data** | Client-level: segments, treatment, channel, dates, frequency |
| **Source** | Parquet files, tactic data |
| **Upgradable** | No (stable data load) |
| **Connects to** | Experiment Metadata pillar |

### Module 2: Campaign Module *(Upgradable)*
| Attribute | Value |
|-----------|-------|
| **Question** | "What is being tested?" |
| **Data** | Campaign-level: primary/secondary/tertiary metrics, action type, measurement period |
| **Current** | Hardcoded Python dict |
| **Future** | Query from Mnemonic Mapping v2 |
| **Upgradable** | Yes |
| **Connects to** | Campaign Metadata pillar |

### Module 3: Success Module *(Upgradable + Swappable)*
| Attribute | Value |
|-----------|-------|
| **Question** | "How do we calculate success?" |
| **Data** | Table paths, filters, logic, conditions |
| **Current** | Hardcoded Python dict |
| **Stage 2** | Pull CODE from GitHub library |
| **Stage 3** | Query DATA from curated table |
| **Upgradable** | Yes (source evolves) |
| **Swappable** | Yes (multiple definitions can exist for same metric) |
| **Connects to** | Success Library pillar |

### Module 4: Enrichment Module *(Optional, Attachable)*
| Attribute | Value |
|-----------|-------|
| **Question** | "What context do we add?" |
| **Data** | Tenure, profitability, region, demographics, attrition |
| **Current** | Not available |
| **Future** | Select from catalog, pull code/data |
| **Optional** | Yes - user selects what they need |
| **Output impact** | Selected enrichments become SEGMENTS |
| **Connects to** | Extends Success Library |

### Module 5: Journey Module
| Attribute | Value |
|-----------|-------|
| **Question** | "What did clients actually do?" |
| **Data** | Channel interactions: email opens/clicks, mobile engagement, banner exposure |
| **Current** | Code activates per detected channel |
| **Future** | Auto-detect channels, pull interaction code |
| **Connects to** | Client Journey pillar |

---

## Analysis Layer: Pluggable Engines

The Context Layer feeds into the Analysis Layer. Currently one engine exists:

### Vintage Engine (Built)
- **Purpose:** Calculate maturation curves over time
- **Functions:** detect_success(), build_vintage_data(), calculate_ci(), prepare_vintage_table(), generate_summary()
- **Output:** Vintage curves with confidence intervals

### Future Engine Slots
The architecture supports adding other engines:
- Funnel Engine (conversion analysis)
- Attribution Engine (channel credit)
- Segment Comparison Engine

**Note:** Don't build until needed. The slots exist; the abstraction doesn't need to be coded yet.

---

## Output Layer

### Adaptive Output
Output shape changes based on inputs:

| Input | Output Behavior |
|-------|-----------------|
| 1 success metric | Single vintage curve |
| Multiple success metrics | Multiple curves (primary, secondary, tertiary) |
| Enrichment selected | Segments added (tenure → segment, region → segment) |
| Channels detected | Interaction stats included |

### Dual Track Delivery
| Track | Platform | Status |
|-------|----------|--------|
| **Track A** | Tableau / CIDM | Pending alignment |
| **Track B** | SharePoint / HTML | Ready now |

Both tracks run in **parallel** from the same engine output.

---

## Three Stages of Maturity

```
STAGE 1              STAGE 2                STAGE 3
(Hardcoded)          (GitHub Library)       (Curated Data)
                           │
              ┌────────────┴────────────┐
              │   FINAL VISION STARTS   │
              └────────────┬────────────┘
                           │
     ▼                     ▼                      ▼
┌─────────┐          ┌─────────┐           ┌─────────┐
│Hardcoded│   ───►   │ GitHub  │    ───►   │ Curated │
│in Python│          │ Library │           │  Data   │
└─────────┘          └─────────┘           └─────────┘

← WE ARE HERE        Near-term              End Game
```

### Stage 1: Hardcoded (Current)
| Aspect | How It Works |
|--------|--------------|
| Success metrics | Hardcoded in Python dict |
| Enrichment | Not available |
| Reuse | Copy/paste |
| What we're doing | Building library as we go |

### Stage 2: GitHub Library (Near-Term Goal)
| Aspect | How It Works |
|--------|--------------|
| Success metrics | Pull CODE from GitHub → Execute |
| Enrichment | Pull CODE from GitHub → Execute |
| Semantic catalog | Points to `code_path` |
| User experience | Self-service begins |

### Stage 3: Curated Data Sets (End Game)
| Aspect | How It Works |
|--------|--------------|
| Success metrics | Query DATA from curated table |
| Enrichment | Query DATA from curated table |
| Semantic catalog | Points to `table_path` |
| Execution | None - data pre-calculated |

**Key insight:** Stage 2 code becomes Stage 3 ETL. Work compounds.

---

## Semantic Asset Catalog

The catalog that enables automation (Stage 2 and Stage 3):

```
┌─────────────────────────────────────────────────────────────────┐
│  ASSET: card_acquisition                                        │
│                                                                 │
│  metric_id: SUC_001                                             │
│  standardized_name: card_acquisition                            │
│  business_description: "Client acquired new VVD card"           │
│  owner: Marketing Analytics                                     │
│                                                                 │
│  STAGE 2:                                                       │
│    code_path: github.com/team/success-library/card_acquisition.py│
│                                                                 │
│  STAGE 3:                                                       │
│    table_path: /curated/success/card_acquisition                │
│                                                                 │
│  output_schema: [client_id, success_date, success_flag]         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Multiple versions can exist:** If two teams have different definitions for `card_acquisition`, both live in the catalog. The campaign metadata specifies which version to use.

---

## End Game User Experience

When fully realized (Stage 2+):

```
USER PROVIDES:
  • Campaign names (VCN, VDA, VDT)
  • Date range (last 3 months, full year, append)
  • Enrichment (optional: tenure, region, profitability)

ENGINE AUTO-DETECTS:
  • Channels from campaign metadata → pulls interaction code
  • Success metrics from campaign config → pulls calculation code
  • Missing items → prompts for semantic definition

ENGINE ADAPTS OUTPUT:
  • Curves per success metric
  • Segments per enrichment variable
  • Channel interaction stats
  • Dashboard-ready format
```

**No SQL. No code editing. No filter guessing.**

---

## Naming Conventions

| Term | Definition |
|------|------------|
| **Pillar** | Team-wide strategic initiative (SuperFact) |
| **Module** | Component in Context Layer |
| **Upgradable** | Module that evolves (hardcoded → GitHub → curated) |
| **Swappable** | Module where multiple implementations can exist |
| **Context Layer** | The 5 modules that gather data/config |
| **Analysis Layer** | Pluggable engines that process data |
| **Engine** | Specific analysis type (Vintage Engine) |
| **Adaptive Output** | Output that shapes to inputs |

---

## Color Scheme (For Diagrams)

| Element | Color | Hex |
|---------|-------|-----|
| From Data (Experiment, Journey) | Ocean Blue border | #0091DA |
| Upgradable (Campaign, Success) | Warm Yellow border | #FFC72C |
| Optional (Enrichment) | Sunburst border/fill | #FCA311 |
| Future State | Tundra | #07AFBF |
| Engine Core | Light Gray fill, Dark Blue border | #F5F5F5, #003168 |
| Stable/Structural | Gray border | #CCCCCC |

---

## What's Built vs. Future

| Component | Status |
|-----------|--------|
| Context Layer modules | First version (hardcoded) |
| Vintage Engine | Built |
| Dashboard output | First version |
| GitHub Success Library | Setting up |
| Semantic Catalog | Designing |
| Curated data sets | Future |
| Other analysis engines | Future (slots documented) |

---

## Open Items

| Item | Status | Notes |
|------|--------|-------|
| Vintage Calculation Type 2 | ON HOLD | Monthly aggregation (time series) - needs more thought |
| Measurement period | TO ADD | Should be in Campaign Metadata (90 days, end of treatment) |
| Enrichment catalog | TO BUILD | List of available enrichment variables |

---

## Document History

- **Created:** 2026-01-22
- **Consolidated from:** ARCHITECTURE_SEMANTICS.md, MVD_ENGINE_ARCHITECTURE.md, VINTAGE_ENGINE_VISION.md
- **Purpose:** Single source of truth for Vintage Engine architecture
