# Vintage Automation - Consolidated Review & Next Steps

*Last Updated: January 2026*

---

## Current State Summary

### What Works Now

| Component | Status | Notes |
|-----------|--------|-------|
| Layer 1: Tactic Loading | **DONE** | Loads from tactic_evnt_hist partitions |
| Layer 2: Campaign Metadata | **Hardcoded** | SWAP POINT for Mnemonic Mapping v2 |
| Layer 3: Success Definitions | **Hardcoded** | SWAP POINT for Success Library |
| Layer 4: Success Outcome | **DONE** | Card acquisition, activation, usage, tokenization |
| Layer 4: Email Engagement | **DONE** | Opens, clicks, bounces from VENDOR_FEEDBACK |
| Channel Detection | **DONE** | From TACTIC_CELL_CD (handles combos like EM_IM) |
| Vintage Curves | **DONE** | COHORT + GROUP level, lift + CI |
| Plotting | **DONE** | Inline Jupyter plots |
| CSV Export | **DONE** | Local and HDFS |

### What's Still Hardcoded (Intentionally - Swap Points)

```python
# These are designed to be swapped later when systematic data access exists

CAMPAIGN_METADATA = {
    "VCN": {
        "campaign_name": "VVD Contextual Notification",
        "success_type": "ACQUISITION",
        "primary_metric": "card_acquisition",
    },
    # ... other campaigns
}

SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "source": "HIVE",
        "table_path": PATHS["visa_dr_crd"],
        "filters": {...},
    },
    # ... other metrics
}

TEST_GROUP_CODE = "TG4"  # <-- Still needs flexibility for A/B tests
```

---

## Backlog Status

| # | Item | Priority | Status | Notes |
|---|------|----------|--------|-------|
| 1 | Leverage tactic/ODS fields | High | **PARTIAL** | Channel done, RPT_GRP_CD not used yet |
| 2 | Fix fulfillment logic | Critical | **NOT DONE** | Need fulfillment code mapping |
| 3 | Channel field & email filter | High | **DONE** | TACTIC_CELL_CD, contains("EM") |
| 4 | Test group flexibility | Medium | **NOT DONE** | Still hardcoded TG4=Test |
| 5 | Dashboard channel dropdown | Medium | **NOT DONE** | Function exists, not integrated |
| 6 | Multi-channel engagement | Future | Not started | Mobile, ONB, ONO |
| 7 | RPT_GRP_CD segmentation | Medium | **NOT DONE** | Field loaded but not used |

---

## Detailed Review by Layer

### Layer 1: Experiment Metadata (TACTIC_EVNT_HIST)

**Current:** Loading from parquet partitions for 2025/2026.

**Fields we extract:**
- CLNT_NO (from TACTIC_EVNT_ID)
- TACTIC_ID, TREATMT_STRT_DT, TREATMT_END_DT
- TST_GRP_CD, RPT_GRP_CD, TREATMT_MN
- TACTIC_CELL_CD (channel)
- STRTGY_SRC_CD
- ADDNL_DECISN_DATA1/2/3

**Improvements needed:**
- [ ] Use RPT_GRP_CD for segmentation
- [ ] Flexible test group assignment (not just TG4)

### Layer 2: Campaign Metadata

**Current:** Hardcoded dict `CAMPAIGN_METADATA`

**SWAP POINT:** When Mnemonic Mapping v2 has Primary/Secondary/Tertiary metric fields:
```sql
SELECT primary_metric, secondary_metric
FROM mnemonic_mapping_v2
WHERE mne = '{mne}'
```

### Layer 3: Success Definitions

**Current:** Hardcoded dict `SUCCESS_DEFINITIONS`

**SWAP POINT:** When Success Library exists:
- Option A: GitHub repo with SQL snippets
- Option B: Curated data set query

### Layer 4: Client Journey

**Email Engagement:** DONE
- Source: VENDOR_FEEDBACK_MASTER + VENDOR_FEEDBACK_EVENT
- Filters to clients where TACTIC_CELL_CD contains "EM"
- Tracks: sent, opened, clicked, unsubscribed, bounced

**Fulfillment:** BROKEN
- Current code returns None for email (uses EMAIL_SENT instead)
- Needs proper fulfillment code mapping per campaign

**Success Outcome:** DONE
- Card acquisition/activation: VISA_DR_CRD
- Card usage: POS_TXN
- Wallet provisioning: EDW token query

---

## Questions for Experts

### High Priority

1. **Fulfillment Codes**
   - Where are fulfillment codes documented/stored?
   - What table contains fulfillment records?
   - What is the column name for fulfillment code?
   - Can one client have multiple fulfillments?

2. **Test Group Definitions**
   - What are ALL possible TST_GRP_CD values and meanings?
   - How to identify control vs action groups per campaign?
   - Are there campaigns with A/B tests (multiple action groups)?

3. **RPT_GRP_CD Meaning**
   - What does RPT_GRP_CD represent?
   - Is there a lookup table for descriptions?
   - Should it be a dashboard filter?

### Medium Priority

4. **Other Channel Engagement**
   - What table has Mobile banner feedback?
   - What table has ONB impression data?
   - What table has ONO lead data?

5. **Additional Metrics**
   - Are there secondary/tertiary metrics per campaign?
   - Where is this documented?

---

## Process: Adding New Cohorts

### When a New Cohort Starts

New cohorts are automatically included if:
1. The treatment start date falls within `YEARS_TO_INCLUDE` (currently 2025, 2026)
2. The tactic_id contains the MNE code (e.g., "VCN" for VVD Contextual Notification)

**No code changes needed** - just run the analysis.

### When a New Campaign (MNE) is Added

You need to add entries to two dictionaries:

**Step 1: Add to CAMPAIGN_METADATA**
```python
CAMPAIGN_METADATA = {
    # ... existing campaigns ...
    "NEW": {
        "campaign_name": "New Campaign Name",
        "success_type": "ACQUISITION",  # or ACTIVATION, USAGE, TOKENIZATION
        "primary_metric": "card_acquisition",  # must exist in SUCCESS_DEFINITIONS
    },
}
```

**Step 2: If new success metric, add to SUCCESS_DEFINITIONS**
```python
SUCCESS_DEFINITIONS = {
    # ... existing metrics ...
    "new_metric": {
        "description": "Description of what success means",
        "source": "HIVE",  # or "EDW"
        "table_path": PATHS["some_path"],
        "date_field": "DATE_COLUMN",
        "client_field": "CLNT_NO",
        "filters": {...},
        "add_card_type": False,
    },
}
```

**Step 3: Run**
```python
results = run_vintage_analysis(spark, 'NEW')
```

### Future: Automated New Cohort Detection

When Mnemonic Mapping v2 is ready:
```python
# Replace hardcoded CAMPAIGN_METADATA with:
def get_campaign_config(mne):
    query = f"SELECT * FROM mnemonic_mapping_v2 WHERE mne = '{mne}'"
    # ... execute query and return config
```

---

## Immediate Next Steps

### Priority 1: Test Current Code
- [ ] Run `run_vintage_analysis(spark, 'VCN')` on actual data
- [ ] Verify channel detection works (should show MB, XX, EM, etc.)
- [ ] Verify vintage curves generate (COHORT + GROUP level)
- [ ] Verify lift/CI calculations

### Priority 2: Dashboard Integration
- [ ] Integrate `build_channel_breakdown()` into output
- [ ] Pass channel breakdown to dashboard
- [ ] Add channel dropdown to dashboard (filter, not replacement)

### Priority 3: Test Group Flexibility
- [ ] Research all TST_GRP_CD values and meanings
- [ ] Decide approach: configurable per-campaign or show all groups
- [ ] Update code to support multiple test groups

### Priority 4: Fulfillment (When Info Available)
- [ ] Get fulfillment code mapping from experts
- [ ] Update `load_fulfillment()` with proper logic
- [ ] Add fulfillment metrics to output

---

## Code Quality Notes

### Good Patterns
- 4-layer architecture with clear separation
- SWAP POINT comments for future migration
- Verbose logging for debugging
- Error handling with informative messages
- Channel detection from data (not hardcoded)

### Areas to Watch
- `TEST_GROUP_CODE = "TG4"` still hardcoded
- `build_channel_breakdown()` exists but not integrated
- Email engagement limits to first 5 tactic IDs (`email_tactic_ids[:5]`)
- No validation of required fields before processing

---

## Files Reference

| File | Purpose |
|------|---------|
| `code/vintage_simple/vintage_all_in_one.py` | Main engine - copy to Jupyter |
| `code/vintage_simple/vintage_dashboard.py` | Dashboard HTML generator |
| `docs/BACKLOG_V2_IMPROVEMENTS.md` | Full backlog details |
| `docs/CODE_BLOCK_DOCUMENTATION.md` | Code block explanations |
| `docs/LAYER_VIEW_DOCUMENTATION.md` | Layer architecture docs |
| `docs/tactic_event_history_table.md` | Tactic table structure |
| `docs/FIELD_ANALYSIS_TACTIC_ODS.md` | Field mapping analysis |

---

## Summary for Stakeholder

**2-sentence answer:**
We built an automated vintage curve engine that calculates Test vs Control lift for VVD campaigns with confidence intervals. The engine is modular with "swap points" for future data source migrations, and currently supports 6 campaigns (VCN, VDA, VDT, VUI, VUT, VAW).

**What's working:** Vintage curves at cohort level, email engagement tracking (for email channels only), export to CSV/HDFS.

**What's pending:** Test group flexibility (A/B tests), fulfillment tracking, channel breakdown in dashboard, multi-channel engagement.
