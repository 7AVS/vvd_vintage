# Changelog

All notable changes to the Vintage Engine will be documented in this file.

---

## [v2.5] - 2026-01-25

### Added
- `EMAIL_SENT` engagement metric (sent rate vs clients targeted with email channel)
- `EMAIL_UNSUB` engagement metric (unsubscribe rate)
- `UNSUBSCRIBED` and `UNSUBSCRIBED_DT` fields from EDW feedback query

### Changed
- `build_engagement_curves()` now accepts `email_channel_df` parameter for EMAIL_SENT denominator
- Engagement metrics now use correct denominators:
  - EMAIL_SENT: clients with email channel (targeted)
  - EMAIL_OPEN, EMAIL_CLICK, EMAIL_UNSUB: clients who received email

---

## [v2.4] - 2026-01-25

### Changed
- Split `PATHS` dict into `HIVE_PATHS` and `EDW_TABLES` for clarity
- `HIVE_PATHS`: File system paths for Hive/Parquet tables (tactic_events, visa_debit_card, pos_transactions)
- `EDW_TABLES`: Database schema.table references (feedback_master, feedback_event, pos_log, token_list)
- Updated all SQL queries to reference `EDW_TABLES` instead of hardcoded strings
- Updated `SUCCESS_DEFINITIONS` to reference `HIVE_PATHS`

### Why
- Hive paths and EDW tables behave differently (paths get date suffixes, tables go into SQL as-is)
- Centralizing all data source references improves maintainability and auditability
- Separation prevents accidental misuse (e.g., appending dates to a table name)

### No Functional Changes
- Same behavior, better organization

---

## [v2.3] - 2026-01-23

### Removed
- METRIC_TYPES constant (unused, not modular)
- SUPPORTED_CHANNELS dict (redundant - code already checks channel prefix in TACTIC_CELL_CD)

### Changed
- Simplified load_channel_engagement() - routes directly based on channel name, no dict lookup

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


