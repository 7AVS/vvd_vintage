# Changelog

All notable changes to the Vintage Engine will be documented in this file.

---

## [v2.3] - 2026-01-23

### Removed
- METRIC_TYPES constant (unused, not modular)
- SUPPORTED_CHANNELS dict (redundant - code already checks channel prefix in TACTIC_CELL_CD)

### Changed
- Simplified load_channel_engagement() - routes directly based on channel name, no dict lookup

### Review Notes (candidates for next version)
- PATHS vs EDW paths: inconsistent location (some in PATHS dict, some in SQL queries)

---

## [v2.2] - 2026-01-23

### Added
- METRIC column (PRIMARY, SECONDARY, EMAIL_OPEN, EMAIL_CLICK)
- Secondary metrics for VAW, VUT, VUI campaigns
- Raw TST_GRP_CD and RPT_GRP_CD in output (no TEST/CONTROL mapping)
- dashboard_v2.2.html with Test Group and Report Group views

### Changed
- Output schema: now groups by TST_GRP_CD x RPT_GRP_CD x METRIC x DAY
- Engagement metrics folded into main vintage_curves output

### Removed
- Lift calculation (moved to dashboard)
- calculate_ci() function
- generate_summary() function
- GROUP column (replaced by raw TST_GRP_CD)

---

## [v2.1] - 2026-01-22

### Fixed
- [:5] bug that limited email engagement to 5 tactic IDs

### Added
- Browser download functions (base64 encoded)
- Validation summary at end of run

### Removed
- Plot functions (moved to separate file)
- MODULE_CONTRACTS (visual clutter)

---

## [v2.0] - 2026-01-21

### Added
- MODULE_REGISTRY documenting all modules
- OUTPUT_SCHEMA definition
- Channel-agnostic engagement loading pattern
- Enrichment placeholder

---

## Code Review Notes (v2.3 candidates)

<!-- Add findings from code review session here -->

