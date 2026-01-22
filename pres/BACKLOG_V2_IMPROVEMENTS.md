# Vintage Automation V2 - Improvement Backlog

Items identified for the next version of the vintage calculation engine. These are NOT to be coded immediately - this is a planning document.

**Last Updated:** January 2026

---

## Summary of Issues

| # | Area | Issue | Priority | Status |
|---|------|-------|----------|--------|
| 1 | Data Sources | Not leveraging all available fields from tactic/ODS | High | **PARTIAL** |
| 2 | Fulfillment | Logic is WRONG - no fulfillment code mapping | Critical | NOT DONE |
| 3 | Channel | Not using channel field - affects email calculation | High | **DONE** |
| 4 | Test Groups | Hardcoded TG4 = Test - doesn't support A/B tests | Medium | NOT DONE |
| 5 | Dashboard | Missing channel dropdown filter | Medium | PARTIAL (function exists) |
| 6 | Future Channels | Only email supported, need mobile/ONB/ONO | Future | NOT STARTED |
| 7 | Dashboard | Success metric dropdown - vintage curves for any metric | Med-High | PARTIAL |
| 8 | Dashboard | Channel tab - show vintage curves BY CHANNEL (not just counts) | High | NOT DONE |

---

## Item 1: Leverage Tactic & ODS Table Fields

### Problem
We're hardcoding information that could be pulled directly from tactic_evnt_hist and ODS tables.

### Action Required
**Step 1:** List ALL available fields from both tables
- `DTZTA_T_TACTIC_EVNT_HIST` (tactic)
- `ed10_im.prod_x610_crm.ods_mr_hist` (ODS)

**Step 2:** Identify which fields can replace hardcoded values

### Fields We Know Exist (need to verify & document)

**From Tactic:**
- `CHNL_CD` or similar - Channel code (EMAIL, MOBILE, ONB, etc.)
- `RPT_GRP_CD` - Reporting group code (for segmentation)
- `TST_GRP_CD` - Test group code (TG1, TG4, etc.)
- `ADDNL_DECISN_DATA1/2/3` - Flexible fields (may contain channel or other info)

**From ODS:**
- Need to investigate what additional fields are available
- May have fulfillment codes?
- May have more detailed channel info?

### Questions to Answer
- [ ] What is the full schema of tactic_evnt_hist?
- [ ] What is the full schema of ods_mr_hist?
- [ ] Where does channel info actually live?
- [ ] Can we get fulfillment codes from either table?

---

## Item 2: Fulfillment Logic is WRONG

### Problem
The current `load_fulfillment()` function is pulling data incorrectly:
- Each campaign (MNE) has specific fulfillment code(s)
- Some campaigns have MULTIPLE fulfillment codes (different offers/strategies)
- We don't know where fulfillment codes are stored
- Current code doesn't filter by fulfillment code at all

### What is Fulfillment?
Fulfillment = where client accepts an offer or provides feedback to the campaign
- Could be an offer acceptance
- Could be a response action
- Varies by campaign strategy

### Current (Wrong) Approach
```python
# Current code - just matches on tactic_id pattern, no fulfillment code
query = f"""
SELECT DISTINCT
    CAST(CLNT_NO AS VARCHAR(20)) AS CLNT_NO,
    1 AS FULFILLMENT_FLAG,
    ...
FROM DG6V01.TACTIC_EVNT_IP_AR_HIST
WHERE tactic_id LIKE '{tactic_id_pattern}'
"""
```

### What We Need
```python
# Future - need fulfillment code(s) per campaign
FULFILLMENT_CODES = {
    "VCN": ["FCODE1", "FCODE2"],  # Where do these come from?
    "VDA": ["FCODE3"],
    # ...
}
```

### Action Required
1. Find where fulfillment codes are documented/stored
2. Create mapping of MNE → fulfillment code(s)
3. Update `load_fulfillment()` to filter by fulfillment code
4. Handle campaigns with multiple fulfillment codes

### Questions to Answer
- [ ] Where are fulfillment codes defined? (Mnemonic Mapping? Campaign docs? Separate table?)
- [ ] What table contains fulfillment records with the fulfillment code?
- [ ] Is it `TACTIC_EVNT_IP_AR_HIST` or a different table?
- [ ] What is the column name for fulfillment code?
- [ ] Can one client have multiple fulfillments for same campaign?

---

## Item 3: Channel Field & Email Calculation - **COMPLETED**

### Problem (RESOLVED)
The email engagement calculation currently includes ALL clients in the experiment, but:
- Not all clients in a deployment receive email
- Some clients may be targeted by other channels (mobile, ONB, etc.)
- Including non-email clients in email metrics is wrong

### Solution Implemented

**Channel field:** `TACTIC_CELL_CD` in tactic_evnt_hist

**Key findings:**
- Channel codes: EM (email), IM (internet), MB (mobile banking), XX (control)
- Channels can be combos like `EM_IM` (email + internet banking)
- CONTROL group has no real channel (they receive no contact)
- Values may have trailing spaces - use `F.trim()`

**Code changes:**
1. Channel discovered from `TACTIC_CELL_CD` (not hardcoded)
2. Email engagement filtered to clients where `TACTIC_CELL_CD.contains("EM")`
3. Vintage curves calculated at COHORT + GROUP level (not by channel)
4. `build_channel_breakdown()` function created for dashboard visibility
5. Channel breakdown shows distribution by channel (TEST group only meaningful)

**Remaining:**
- [ ] Integrate channel breakdown into dashboard
- [ ] Add channel dropdown filter to dashboard

---

## Item 4: Test Group Flexibility

### Problem
Currently hardcoded:
```python
TEST_GROUP_CODE = "TG4"  # Hardcoded as the only "Test" group
tactic = tactic.withColumn("GROUP",
    F.when(F.col("TST_GRP_CD") == TEST_GROUP_CODE, "TEST").otherwise("CONTROL"))
```

### Reality
- TG1 = ACTION (Test)
- TG4 = ACTION (Test)
- Other TG codes = Could be control or other variants
- Some campaigns have A/B tests (Champion vs Challenger)
- Both Champion and Challenger are "action" groups but need to be compared separately

### Example: A/B Test
```
Campaign XYZ:
- TG1 = Champion (existing creative)
- TG4 = Challenger (new creative)
- TG0 = Control (no contact)

Current approach: TG4 = Test, TG1 = Control (WRONG!)
Correct approach: Show TG1, TG4, TG0 separately
```

### What We Need
Two options:

**Option A: Keep simple Test/Control but make configurable**
```python
# Per-campaign config
CAMPAIGN_METADATA = {
    "VCN": {
        "test_groups": ["TG4"],
        "control_groups": ["TG0", "TG1", "TG2", "TG3"]
    },
    "XYZ": {  # A/B test campaign
        "test_groups": ["TG1", "TG4"],  # Both are action
        "control_groups": ["TG0"]
    }
}
```

**Option B: Don't label, just show each TG separately**
```python
# Don't assign "TEST" or "CONTROL"
# Just keep TST_GRP_CD as-is and let user see TG1, TG4, etc. in dashboard
# User interprets what each TG means
```

### Action Required
1. Get list of all possible TST_GRP_CD values and their meanings
2. Decide on approach (A or B)
3. Update code to support multiple test groups or no labeling
4. Update dashboard to handle multiple groups

### Known Test Group Codes
| Code | Meaning | Notes |
|------|---------|-------|
| TG1 | ACTION | Test group |
| TG4 | ACTION | Test group |
| TG0 | ? | Likely control |
| Others | ? | Need to investigate |

---

## Item 5: Dashboard - Channel Dropdown

### Problem
Dashboard doesn't have channel filter.

### What We Need
Add dropdown: "Channel" with options:
- All Channels
- EMAIL
- MOBILE
- ONB (Online Banking)
- ONO (Offer and Opportunity - Advisory Centre)

When channel selected:
- Filter vintage curves to only show that channel's clients
- Engagement funnel shows only that channel's metrics

### Depends On
- Item 3 (Channel field must be in the data first)

---

## Item 6: Future - Multi-Channel Support

### Current State
Only EMAIL channel has engagement tracking:
- Source: VENDOR_FEEDBACK_MASTER + VENDOR_FEEDBACK_EVENT
- Metrics: sent, opened, clicked, bounced

### Future Channels Needed

| Channel | Name | Feedback Source | Metrics |
|---------|------|-----------------|---------|
| EMAIL | Email | VENDOR_FEEDBACK | sent, opened, clicked |
| MOBILE | Mobile Banner | ? | view rate, dismiss rate, click rate |
| ONB | Online Banking | ? | impression, click |
| ONO | Offer & Opportunity | Advisory Centre | lead viewed, lead actioned |

### Action Required (Future)
1. Identify feedback source tables for each channel
2. Understand schema and metrics available
3. Build `load_mobile_engagement()`, `load_onb_engagement()`, etc.
4. Consolidate into unified engagement layer
5. Update dashboard to show channel-specific funnels

### Not Needed Now
This is for future phases. Current focus:
- Get EMAIL working correctly (with proper channel filtering)
- Other channels come later when their feedback sources are available

---

## Item 7: Success Metric Dropdown (Vintage Any Metric)

### Problem
Email engagement metrics (open rate, click rate, unsubscribe) are shown as **overall summary** - one number for the whole campaign. Over 2 years of cohorts, this is useless. Need to see the **curve per cohort** for any metric.

### What Director Wants to See
"Show me the unsubscribe rate curve by cohort" - not just "overall unsubscribe rate is 2%"

### Solution
Add **metric dropdown** to dashboard:
- Primary success (card acquisition, activation, etc.)
- Open rate curve (by cohort)
- Click rate curve (by cohort)
- Unsubscribe rate curve (by cohort)
- Bounce rate curve (by cohort)

Same vintage curve structure, different Y-axis metric.

### Implementation Notes
- Email engagement already captured per client with dates (EMAIL_OPENED_DT, EMAIL_CLICKED_DT, etc.)
- Need to build vintage curves for engagement metrics same way we do for success
- `DAYS_TO_OPEN`, `DAYS_TO_CLICK`, etc. instead of `DAYS_TO_SUCCESS`
- Dashboard dropdown switches which curve to display

### Priority
Medium-High - Important for understanding cohort-level engagement trends

---

## Item 8: Channel Tab - Vintage Curves by Channel

### Problem
Current channel tab shows bar chart of client counts. User wants to see **vintage curves by channel** - success rate over days, broken down by channel.

### Challenge
Too many lines if showing all cohorts × all channels:
- 6 cohorts × 3 channels = 18 lines (unreadable)

### Solution Options
1. **Single cohort view** - Force user to pick ONE cohort, show channel curves for that cohort
2. **Latest cohort default** - Auto-select most recent cohort
3. **Small multiples** - Grid of mini-charts, one per channel
4. **Limit cohorts** - "Show last N cohorts" option

### Decision Needed
Which approach to implement? Recommend Option 1 (single cohort selection).

### Implementation
- Need vintage curves grouped by COHORT + CHANNEL (not COHORT + GROUP)
- Only for TEST group (CONTROL has no real channel)
- Add cohort selector that defaults to latest when on channel tab

### Priority
High - User specifically requested this

---

## Item 9: Reporting Group Code (RPT_GRP_CD)

### Problem
RPT_GRP_CD is available in tactic but not being used.

### What is RPT_GRP_CD?
- Used for segmentation
- Groups clients by some criteria (need to understand what)
- Could be used for segment filtering in dashboard

### Action Required
1. Understand what RPT_GRP_CD values mean
2. Find lookup table for RPT_GRP_CD descriptions
3. Add to output data
4. Add segment dropdown to dashboard (if useful)

### Priority
Medium - Need to understand meaning first

---

## Priority Order

### Phase 1: Critical Fixes
1. **List tactic/ODS fields** - Need this first to understand what's available
2. **Fix fulfillment logic** - Currently wrong, need correct mapping
3. **Add channel to tactic load** - Required for proper email calculation
4. **Filter email by channel** - Fix the email metric calculation

### Phase 2: Enhancements
5. **Test group flexibility** - Support A/B tests
6. **Dashboard channel filter** - User can filter by channel
7. **RPT_GRP_CD segmentation** - Add segment filtering

### Phase 3: Future
8. **Multi-channel engagement** - Mobile, ONB, ONO feedback

---

## Questions for Next Session

1. Can you pull the full schema of `tactic_evnt_hist`?
2. Can you pull the full schema of `ods_mr_hist`?
3. Where are fulfillment codes documented?
4. What are all the TST_GRP_CD values and their meanings?
5. What does RPT_GRP_CD represent? Is there a lookup table?
6. Which column in tactic has the channel code?

---

## Notes

- Don't code anything yet - need to investigate data sources first
- Email calculation is currently inflated (includes non-email clients)
- Fulfillment logic is fundamentally broken - needs complete rework
- Test group logic works for simple Test/Control but fails for A/B tests
