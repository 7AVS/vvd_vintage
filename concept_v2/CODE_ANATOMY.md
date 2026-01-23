# Vintage Engine v2.1 - Code Anatomy

**Purpose:** Reference document for understanding code structure and identifying optimization opportunities.

**Last Updated:** 2026-01-23

**File Analyzed:** `code/vintage_simple/vintage_engine_v2.1.py`

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Lines** | 1,590 |
| **Core Logic** | 572 (36%) |
| **Minimum Viable** | ~700 lines |
| **Recommended Slim** | ~1,300 lines |

---

## 1. Essential Core - Cannot Remove

These functions DO the actual work. Removing any breaks functionality.

| Function | Lines | Location | Purpose |
|----------|-------|----------|---------|
| `load_tactic()` | 43 | 422-464 | Layer 1: Load experiment data from Hive |
| `_load_email_engagement()` | 62 | 506-567 | Layer 4: Query EDW for email engagement |
| `load_token_from_edw()` | 24 | 579-603 | Layer 4: Query EDW for tokenization |
| `load_success_outcome()` | 39 | 606-644 | Layer 4: Load success data with dynamic filters |
| `detect_success()` | 38 | 694-731 | Join experiment + success, compute days-to-success |
| `enrich_with_engagement()` | 57 | 734-792 | Add email metrics to success dataframe |
| `build_vintage_data()` | 12 | 799-811 | Aggregate successes by cohort/group/day |
| `prepare_vintage_table()` | 68 | 907-974 | Compute cumulative rates + lift + CI |
| `calculate_ci()` | 8 | 896-904 | Statistical confidence interval |
| `run_vintage_analysis()` | 171 | 1180-1350 | Main orchestration function |
| `run_all_campaigns()` | 50 | 1353-1402 | Multi-campaign runner |

**TOTAL: ~572 lines**

---

## 2. Configuration - Should Keep

| Section | Lines | Location | Notes |
|---------|-------|----------|-------|
| `PATHS` | 12 | 218-230 | Data source paths |
| `USER_CONFIG` | 8 | 63-70 | User-configurable HDFS paths |
| `SUPPORTED_CHANNELS` | 5 | 234-238 | Channel definitions |
| `CAMPAIGN_METADATA` | 44 | 244-287 | 6 campaigns defined |
| `SUCCESS_DEFINITIONS` | 66 | 293-359 | 4 metrics defined |
| Config accessors | 27 | 378-403 | `get_campaign_config()`, etc. |

**TOTAL: ~162 lines**

**Recommendation:** Keep. Clean separation of config from logic.

---

## 3. Scaffolding - Helpful But Optional

| Section | Lines | Location | What You Lose If Removed |
|---------|-------|----------|--------------------------|
| `MODULE_REGISTRY` | 54 | 137-190 | Self-documenting module status |
| `OUTPUT_SCHEMA` | 14 | 198-210 | Schema documentation |
| `load_channel_engagement()` dispatcher | 18 | 484-503 | Could inline EMAIL case |

**TOTAL: ~86 lines**

**Recommendation:** Keep for maintainability. Remove if minimizing is priority.

---

## 4. Placeholder/Stub Code - Safe to Remove

These provide NO current functionality. All return None or are never called.

| Item | Lines | Location | Status |
|------|-------|----------|--------|
| `ENRICHMENT_CATALOG` | 5 | 365-369 | All items "PLANNED" |
| `load_enrichment()` | 20 | 651-672 | Always returns None |
| `enrich_with_segments()` | 10 | 675-688 | Always returns None |
| `load_fulfillment()` | 7 | 471-477 | Always returns None |
| `load_email_engagement()` alias | 3 | 569-572 | Backward compat wrapper |

**TOTAL: ~45 lines**

**Recommendation:** Remove. Re-add when features are built.

---

## 5. Output/Logging - Could Condense

| Section | Lines | Location | Notes |
|---------|-------|----------|-------|
| `print_module_status()` | 10 | 406-415 | Nice-to-have display |
| `print_validation_summary()` | 57 | 1117-1173 | QA validation |
| Inline `log()` calls | ~35 | scattered | Progress messages |
| Inline `print()` | ~15 | scattered | Status updates |
| ASCII banner + usage | 32 | 1558-1589 | End-of-file instructions |

**TOTAL: ~149 lines**

**Recommendation:** Route all through single `log()` function with `verbose` flag. Keep `print_validation_summary()` - it catches real issues.

---

## 6. Plotting - Could Separate

| Function | Lines | Location |
|----------|-------|----------|
| `plot_vintage()` | 32 | 1030-1062 |
| `plot_grid()` | 44 | 1065-1108 |

**TOTAL: ~76 lines**

**Recommendation:** Move to separate `vintage_plots.py` file. Import when needed.

---

## 7. Export Utilities - Could Separate

| Function | Lines | Location |
|----------|-------|----------|
| `rename_spark_output()` | 27 | 77-103 |
| `display_download_links()` | 12 | 118-129 |
| `export_to_hdfs_csv()` | 38 | 1409-1446 |
| `export_all_to_hdfs()` | 99 | 1449-1546 |

**TOTAL: ~176 lines** (includes HDFS helpers)

**Recommendation:** Move to separate `vintage_export.py` file. Import when needed.

---

## 8. Documentation - Keep Minimum

| Type | Lines | Notes |
|------|-------|-------|
| Section headers (`# ===`) | ~45 | Navigation aid |
| Docstrings | ~60 | Function documentation |
| Inline comments | ~30 | Logic explanation |
| Top changelog | 19 | Version history |

**TOTAL: ~154 lines**

**Recommendation:** Keep docstrings on public functions. Section headers are personal preference - helpful for 1500+ line file.

---

## Optimization Paths

### Path A: Slim Version (~1,300 lines)

Remove/move without losing functionality:

| Action | Lines Saved |
|--------|-------------|
| Remove placeholder stubs | -45 |
| Move plotting to `vintage_plots.py` | -76 |
| Move export to `vintage_export.py` | -176 |
| Condense banner to 5 lines | -27 |
| **Total saved** | **-324** |

**Result:** ~1,266 lines, same functionality, cleaner separation.

### Path B: Lean Version (~1,000 lines)

Path A plus:

| Action | Lines Saved |
|--------|-------------|
| Remove MODULE_REGISTRY | -54 |
| Remove OUTPUT_SCHEMA | -14 |
| Condense logging (verbose flag) | -80 |
| Remove section headers | -45 |
| **Additional saved** | **-193** |

**Result:** ~1,073 lines. Loses self-documenting features.

### Path C: Minimum Viable (~700 lines)

Strip to absolute essentials:

- Core functions only
- Inline all config
- No logging
- No documentation
- No validation

**Result:** ~700 lines. Hard to maintain, requires tribal knowledge.

---

## Trade-Off Matrix

| Version | Lines | Maintainability | Extensibility | Debugging | Onboarding |
|---------|-------|-----------------|---------------|-----------|------------|
| Current | 1,590 | High | High | Easy | Easy |
| Slim (A) | 1,300 | High | High | Easy | Easy |
| Lean (B) | 1,000 | Medium | Medium | Medium | Medium |
| Minimum (C) | 700 | Poor | Low | Hard | Hard |

---

## Recommended Structure (If Splitting)

```
vintage_simple/
├── vintage_engine.py      # Core engine (~1,100 lines)
│   ├── Configuration
│   ├── Layer functions
│   ├── Vintage calculations
│   └── Main runner
│
├── vintage_export.py      # Export utilities (~180 lines)
│   ├── HDFS helpers
│   ├── export_to_hdfs_csv()
│   ├── export_all_to_hdfs()
│   └── display_download_links()
│
├── vintage_plots.py       # Visualization (~80 lines)
│   ├── plot_vintage()
│   └── plot_grid()
│
└── vintage_diagnostics.py # Already exists (~145 lines)
    ├── diagnose_results()
    └── test_export_ready()
```

**Note:** Single-file approach is still valid for Jupyter deployment. Splitting is optional.

---

## Update Log

| Date | Change | By |
|------|--------|-----|
| 2026-01-23 | Initial anatomy analysis | Consultant |
| | | |

---

## Related Documents

- `VINTAGE_ENGINE_ARCHITECTURE.md` - Target architecture (north star)
- `GAP_ANALYSIS.md` - Gaps between v2.1 and architecture
- `STAGE_ROADMAP.md` - Pathway from Stage 1 to Stage 3
