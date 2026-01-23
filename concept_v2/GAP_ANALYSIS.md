# Gap Analysis: vintage_all_in_one.py vs VINTAGE_ENGINE_ARCHITECTURE.md

**Date:** 2026-01-22
**Purpose:** Identify gaps between current implementation and target architecture, recommend improvements
**Outcome:** New version `vintage_engine_v2.py` with structural improvements

---

## Executive Summary

The current code (`vintage_all_in_one.py`) is functional and well-commented, but lacks the modular structure described in the architecture document. Key gaps:

1. No formal module boundaries or contracts
2. Enrichment module does not exist
3. Journey module is hardcoded for email only
4. Output structure is implicit, not extensible
5. No registry documenting module status

**Recommendation:** Keep single-file approach (appropriate for statistician team), but add lightweight contracts and consistent patterns that make future scaling easier.

---

## Detailed Gap Analysis

### GAP 1: No Module Boundaries or Contracts

| Architecture | Current Code | Impact |
|--------------|--------------|--------|
| 5 Context Layer modules with clear responsibilities | Functions grouped by comments, no formal interface | Adding new modules requires understanding implicit contracts |
| Modules are "swappable" | Swap points documented in comments only | No mechanism to actually swap - requires code editing |

**What's Missing:**
- No definition of what each module must INPUT and OUTPUT
- `get_full_config()` merges Layer 2 + Layer 3, breaking separation
- No registry of available modules and their status

**Severity:** MEDIUM - Code works, but scaling requires tribal knowledge

---

### GAP 2: Enrichment Module - Does Not Exist

| Architecture | Current Code |
|--------------|--------------|
| Module 4: Enrichment - tenure, profitability, region, demographics | Nothing implemented |
| "Optional, user selects what they need" | No selection mechanism exists |
| "Selected enrichments become SEGMENTS" | Output has no segment dimension |

**What's Missing:**
- No placeholder or interface definition
- No concept of "optional modules" in the runner
- Output structure doesn't accommodate segments

**Severity:** HIGH for future contextual analysis, LOW for current campaigns

**Recommendation:** Don't build empty module, but DO define the interface and where it would plug in.

---

### GAP 3: Journey Module - Email Only, Not Extensible

| Architecture | Current Code |
|--------------|--------------|
| "Auto-detect channels, pull interaction code" | Channels detected, but only email engagement implemented |
| Module handles all touchpoints | `load_email_engagement()` is standalone, no pattern for other channels |

**What's There:**
- Channel detection works (line 997-999, reads `TACTIC_CELL_CD`)
- Email engagement fully implemented
- Handles channel combos (EM_IM, EM_MB)

**What's Missing:**
- No `load_mobile_engagement()`, `load_banner_engagement()`
- No common interface that all channel functions follow
- Adding a channel requires modifying `run_vintage_analysis()`

**Severity:** MEDIUM - Email works, but adding channels is manual

**Recommendation:** Refactor to channel-agnostic pattern with consistent interface.

---

### GAP 4: Output Layer - Implicit, Not Adaptive

| Architecture | Current Code |
|--------------|--------------|
| "Adaptive Output" - shape changes based on inputs | Fixed output: vintage_df, summary_df, channel_breakdown_df, engagement_vintage_df |
| "Segments added per enrichment variable" | No segment dimension in output |
| Separate Output Layer | Output generation scattered across multiple functions |

**What's There:**
- Output works and is consistent
- Export functions handle the structure

**What's Missing:**
- No definition of output schema/contract
- No mechanism to add dimensions (e.g., SEGMENT)
- Output functions don't know about optional enrichments

**Severity:** MEDIUM - Works for current use, but not extensible

**Recommendation:** Define OUTPUT_SCHEMA explicitly, add optional dimension support.

---

### GAP 5: No Plugin Architecture for Engines

| Architecture | Current Code |
|--------------|--------------|
| "Pluggable Engines" - Vintage, Funnel, Attribution as slots | One monolithic `run_vintage_analysis()` |
| "Future engines can be added" | No abstraction - would require copy/paste |

**What's There:**
- Vintage Engine works well
- Core calculations are stable

**What's Missing:**
- No interface defining what an "engine" must do
- No way to swap engines without rewriting the runner

**Severity:** LOW - Only one engine exists or is planned near-term

**Recommendation:** Document what an engine interface would look like, but don't build it.

---

### GAP 6: Semantic Asset Catalog - Does Not Exist

| Architecture | Current Code |
|--------------|--------------|
| Catalog with metric_id, code_path, table_path, output_schema | `SUCCESS_DEFINITIONS` dict with hardcoded paths |
| Multiple versions of same metric can exist | Single definition per metric |
| Enables Stage 2 (GitHub) and Stage 3 (Curated Data) | Stage 1 only (hardcoded) |

**What's There:**
- `SUCCESS_DEFINITIONS` captures the essential metadata
- Swap points are documented in comments

**What's Missing:**
- No version concept
- No code_path or table_path for future stages
- No output_schema definition

**Severity:** HIGH for Stage 2+, LOW for Stage 1

**Recommendation:** Extend SUCCESS_DEFINITIONS schema to include future fields (as None/placeholder).

---

## Summary: Gap Severity Matrix

| Component | Gap Severity | Action |
|-----------|--------------|--------|
| Experiment Module | LOW | Minor: add output contract |
| Campaign Module | MEDIUM | Add swap-ready structure |
| Success Module | MEDIUM | Extend schema for future stages |
| Enrichment Module | HIGH (future) | Define interface, add placeholder |
| Journey Module | MEDIUM | Refactor to channel-agnostic |
| Vintage Engine | LOW | Stable, document interface |
| Output Layer | MEDIUM | Define schema, add optional dimensions |
| Plugin Architecture | LOW | Document only, don't build |
| Semantic Catalog | HIGH (future) | Extend existing dicts |

---

## Recommendations

### DO NOW (Improves Current + Enables Future)

1. **Add MODULE_REGISTRY**
   - Document what modules exist, their status, swap targets
   - Makes architecture visible in the code itself

2. **Define Module Contracts**
   - INPUT: What each module expects (DataFrame schema, parameters)
   - OUTPUT: What each module returns (DataFrame schema)
   - Document as docstrings + constants

3. **Refactor Journey to Channel-Agnostic Pattern**
   - `load_channel_engagement(spark, ids, channel)` dispatcher
   - `_load_email_engagement()` as implementation
   - Clear interface for future `_load_mobile_engagement()`

4. **Define Output Schema**
   - Required dimensions: MNE, COHORT, GROUP, DAY
   - Required metrics: CUMULATIVE_RATE, ABS_LIFT, CI_LOWER, CI_UPPER
   - Optional dimensions: CHANNEL, SEGMENT (for enrichment)

5. **Add Enrichment Placeholder**
   - Not a working module, but:
   - Interface definition (what it would accept/return)
   - Where it plugs into the runner (marked with comment)
   - Entry in MODULE_REGISTRY with status="PLANNED"

6. **Extend SUCCESS_DEFINITIONS Schema**
   - Add `code_path: None` (for Stage 2)
   - Add `table_path_curated: None` (for Stage 3)
   - Add `version: "1.0"` (for future versioning)

### DON'T DO (Over-Engineering)

1. **Don't split into multiple files** - Breaks notebook deployment, adds cognitive load
2. **Don't build abstract base classes** - Python overhead, confusing for non-developers
3. **Don't build real plugin system** - One engine exists, no near-term second engine
4. **Don't build working Enrichment module** - No data available yet

### DOCUMENT ONLY (Future Reference)

1. **Engine interface** - What a Funnel Engine or Attribution Engine would need
2. **Semantic Catalog full schema** - What Stage 2/3 would look like
3. **Multi-version metric handling** - How two definitions of "card_acquisition" would coexist

---

## Implementation Plan

### New File: `vintage_engine_v2.py`

Structure:
```
1. MODULE_REGISTRY (new)
2. MODULE CONTRACTS (new)
3. Configuration
4. Paths
5. Layer 2: Campaign Metadata (extended schema)
6. Layer 3: Success Definitions (extended schema)
7. Layer 1: Experiment Module (with contract)
8. Layer 4: Journey Module (channel-agnostic refactor)
9. Layer 4: Enrichment Module (placeholder + interface)
10. Success Detection
11. Vintage Engine (unchanged)
12. Output Layer (with schema)
13. Plotting
14. Main Runner (with enrichment hook)
15. Export
16. Setup & Usage
```

### Changes Summary

| Section | Change Type | Description |
|---------|-------------|-------------|
| MODULE_REGISTRY | NEW | Documents all modules, status, swap targets |
| MODULE_CONTRACTS | NEW | Defines INPUT/OUTPUT schemas for each module |
| CAMPAIGN_METADATA | EXTENDED | Added future fields (secondary_metric, tertiary_metric) |
| SUCCESS_DEFINITIONS | EXTENDED | Added code_path, table_path_curated, version |
| load_tactic() | MINOR | Added output contract in docstring |
| Journey functions | REFACTORED | Channel-agnostic dispatcher pattern |
| Enrichment | NEW PLACEHOLDER | Interface defined, not implemented |
| OUTPUT_SCHEMA | NEW | Explicit schema with optional dimensions |
| run_vintage_analysis() | MODIFIED | Added enrichment hook (commented placeholder) |

---

## Success Criteria

After implementing v2:

1. **Visible Architecture** - MODULE_REGISTRY shows what exists and what's planned
2. **Clear Contracts** - Each module has documented INPUT/OUTPUT
3. **Extensible Journey** - Adding mobile engagement follows existing pattern
4. **Enrichment-Ready** - Clear where enrichment would plug in
5. **Output Schema** - Explicit definition of output dimensions
6. **No Breaking Changes** - v2 produces identical output to v1
7. **Single File** - Still works as copy-paste into Jupyter

---

## Open Questions

1. **Enrichment Data** - When will tenure/profitability data be available?
2. **Secondary Metrics** - Should v2 support primary + secondary in single run?
3. **Mobile/Banner Engagement** - Is data available? What's the source?
4. **Stage 2 Timeline** - When might GitHub Success Library be established?

---

## Document History

- **2026-01-22** - Created based on gap analysis discussion
