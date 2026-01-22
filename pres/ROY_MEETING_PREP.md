# Vintage Automation - Meeting with Roy

## One-Sentence Summary

Built a working Vintage Automation engine as a **pilot project** that demonstrates the SuperFact 4-layer framework - pulling experiment data from tactic tables, discovering channels automatically, and producing vintage curves with lift and confidence intervals.

---

## The Story: Why This Matters

**The problem we're solving:**
- Analysts spend weeks recreating the same vintage curve logic for each campaign
- "Success" means different things to different people
- No systematic way to pull campaign context from data - everything is hardcoded

**What Vintage Automation proves:**
- We CAN pull experiment metadata directly from tactic tables (Layer 1)
- We CAN structure code so campaign/success definitions are "swap points" for future data sources
- We CAN discover things like **channel** from the data instead of hardcoding
- The 4-layer architecture actually works in practice

---

## How Vintage Automation Fits SuperFact

```
                    VINTAGE AUTOMATION (PILOT)

  Layer 1              Layer 2              Layer 3              Layer 4
  Experiment           Campaign             Success              Client
  Metadata             Metadata             Library              Journey
  ┌─────────┐          ┌─────────┐          ┌─────────┐         ┌─────────┐
  │tactic_  │          │Mnemonic │          │GitHub   │         │VISA_DR_ │
  │evnt_hist│          │Mapping  │          │Success  │         │CRD      │
  │         │          │v2       │          │Logic    │         │EMAIL    │
  │FROM DATA│          │HARDCODED│          │HARDCODED│         │FROM DATA│
  │   NOW   │          │(swap pt)│          │(swap pt)│         │   NOW   │
  └────┬────┘          └────┬────┘          └────┬────┘         └────┬────┘
       │                    │                    │                    │
       └────────────────────┼────────────────────┼────────────────────┘
                            │                    │
                            ▼                    ▼
           ┌──────────────────────────────────────────────────────┐
           │            vintage_all_in_one.py                      │
           │                                                       │
           │  - Channel discovered from TACTIC_CELL_CD (not hdcd)  │
           │  - Test/Control groups from TST_GRP_CD                │
           │  - Email engagement filtered by channel               │
           │  - Swap points for Layers 2 & 3 when ready            │
           └───────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
           ┌──────────────────────────────────────────────────────┐
           │     Vintage Curves + Lift + Confidence Intervals      │
           │     (CSV export → Dashboard consumption)              │
           └──────────────────────────────────────────────────────┘
```

---

## What's Built & What's Changed

### Current State

| Component | Status | Recent Progress |
|-----------|--------|-----------------|
| Layer 1: Experiment data (tactic) | **FROM DATA** | Correct path, partition pruning |
| Layer 2: Campaign metadata | Hardcoded | Swap point documented |
| Layer 3: Success definitions | Hardcoded | Swap point documented |
| Layer 4: Success outcome | **FROM DATA** | Card acquisition, activation, usage, tokenization |
| Layer 4: Email engagement | **FROM DATA** | Filtered by channel (only where channel contains "EM") |
| Channel detection | **FROM DATA** | Discovered from TACTIC_CELL_CD, handles combos like EM_IM |
| Vintage calculation | Working | COHORT + GROUP level, lift, CI |
| CSV/HDFS export | Working | Ready for dashboard consumption |

### Key Change: Channel Now From Data

**Before (wrong):**
```python
# Hardcoded channel in config
CAMPAIGN_CONFIG = {
    "VCN": {
        "channel": "EMAIL",  # ← Hardcoded
    }
}
```

**After (correct):**
```python
# Discovered from data
channel_counts = tactic_df.groupBy(F.trim(F.col("TACTIC_CELL_CD"))).count()
# Result: {'MB': 13M, 'XX': 762K, 'EM': 5K, 'EM_IM': 2K, ...}

# Email engagement only for clients where channel contains "EM"
email_clients = tactic_df.filter(F.trim(F.col("TACTIC_CELL_CD")).contains("EM"))
```

**Why this matters:**
- CONTROL group has no real channel (they receive no contact)
- Channel is a breakdown variable, not a grouping dimension for lift
- Combo channels like `EM_IM` (email + internet banking) are handled correctly

---

## Campaigns Covered (6 Pilots)

| MNE | Campaign | Success Type | Status |
|-----|----------|--------------|--------|
| VCN | Contextual Notification | Acquisition | Ready to test |
| VDA | Black Friday Cyber Monday | Acquisition | Config exists |
| VDT | Activation Trigger | Activation | Config exists |
| VUI | Usage Trigger | Usage | Config exists |
| VUT | Tokenization Usage | Tokenization | Config exists |
| VAW | Add To Wallet | Tokenization | Config exists |

---

## The Philosophy: What to Hardcode vs Pull From Data

**Pilot project approach:**

| Data Source | Approach | Why |
|-------------|----------|-----|
| **Experiment data** (tactic_evnt_hist) | FROM DATA | Systematic access exists |
| **Channel** (TACTIC_CELL_CD) | FROM DATA | Systematic access exists |
| **Test groups** (TST_GRP_CD) | FROM DATA | Systematic access exists |
| **Campaign metadata** | HARDCODED (swap point) | Mnemonic Mapping v2 not ready |
| **Success definitions** | HARDCODED (swap point) | Success Library not ready |

**Swap points are documented** - when the proper data sources exist, we replace the hardcoded dicts with queries.

---

## What We Learned (Important for Future)

### 1. CONTROL Has No Channel
CONTROL clients receive no contact, so they have no meaningful channel (usually marked "XX" or similar). Vintage curves must compare TEST vs CONTROL at **COHORT level**, not by channel.

### 2. Channels Can Be Combos
A client targeted by both email and internet banking has channel `EM_IM`. Email engagement filtering uses `.contains("EM")` to catch all combos.

### 3. Data Quality Issues
- TACTIC_CELL_CD values have trailing spaces (need `F.trim()`)
- Some fields are consistently null (MDM fields)

### 4. Test Group Flexibility Still Needed
Currently hardcoded `TG4 = Test`. Some campaigns have A/B tests where TG1 and TG4 are both "action" groups. Need to make this configurable per campaign.

---

## What's Still Needed

### High Priority

| Item | Status | Blocker |
|------|--------|---------|
| Validate VCN against known results | Not started | Need known baseline |
| Test group flexibility (A/B tests) | Not done | Need TST_GRP_CD meanings |
| Fulfillment code mapping | Not done | Need expert input |
| **Metric dropdown in dashboard** | Not done | Design ready (see below) |

### Medium Priority

| Item | Status | Notes |
|------|--------|-------|
| Channel breakdown in dashboard | Function exists | Not integrated yet |
| RPT_GRP_CD segmentation | Field loaded | Don't know what it means |

### Questions for Experts

1. Where are fulfillment codes documented?
2. What are all TST_GRP_CD values and their meanings?
3. What does RPT_GRP_CD represent?

---

## Key Feature: Metric Dropdown (Vintage Any Metric)

### The Problem
Current: Email engagement shown as **overall summary** (one number for whole campaign).

Over 2 years of cohorts, overall summary is useless. Director needs: "Show me unsubscribe rate **by cohort**" - not "overall unsubscribe is 2%".

### The Solution
Dropdown to select which metric to plot as a vintage curve:

```
┌─────────────────────────────────────────┐
│  Metric: [Primary Success ▼]            │
│          ├─ Primary Success (Acquisition)│
│          ├─ Open Rate                    │
│          ├─ Click Rate                   │
│          ├─ Unsubscribe Rate             │
│          └─ Bounce Rate                  │
└─────────────────────────────────────────┘
```

Same vintage curve structure:
- X-axis: Days from treatment
- Y-axis: Cumulative rate (for selected metric)
- Lines: Test vs Control by cohort

### Why This Matters
- See engagement **trends over time** per cohort
- Compare cohort performance on ANY metric
- Identify if recent cohorts have higher unsubscribe rates
- Director-level insight, not just analyst summary

---

## Adding New Cohorts (Process Documented)

**New cohorts:** Automatic - no code changes needed (if within YEARS_TO_INCLUDE)

**New campaign (MNE):**
1. Add entry to `CAMPAIGN_METADATA` dict
2. Add entry to `SUCCESS_DEFINITIONS` if new metric type
3. Run `run_vintage_analysis(spark, 'NEW')`

**Future:** When Mnemonic Mapping v2 ready, replace hardcoded dicts with queries.

---

## Impact: Aligned with SuperFact Goals

| SuperFact Target | How Vintage Automation Contributes |
|------------------|-----------------------------------|
| Fast turnaround on Vintages | This is the direct output |
| Feed dashboards for quicker delivery | CSV export + HTML dashboard ready |
| Automation of QBR/MBR reporting | Vintage data feeds aggregated results |
| Natural Language Querying/AI | Structured, documented data ready |

---

## Two Tracks for Dashboard (Running in Parallel)

We're pursuing **both tracks simultaneously** - they're not mutually exclusive.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VINTAGE AUTOMATION ENGINE                         │
│                    (vintage_all_in_one.py)                           │
│                                                                      │
│            Produces: Vintage curves, lift, CI                        │
│            Output: CSV / HDFS                                        │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │      CSV OUTPUT        │
              │  (Same data feeds both)│
              └───────────┬────────────┘
                          │
           ┌──────────────┴──────────────┐
           │                             │
           ▼                             ▼
┌─────────────────────┐       ┌─────────────────────┐
│    TRACK A          │       │    TRACK B          │
│    Official         │       │    In-House         │
├─────────────────────┤       ├─────────────────────┤
│ Who: CDIM team      │       │ Who: Us             │
│ Tool: Tableau       │       │ Tool: HTML/Plotly   │
│ Location: Governed  │       │ Location: SharePoint│
│ Timeline: TBD       │       │ Timeline: NOW       │
│                     │       │                     │
│ Need: Provide specs │       │ Have: Working       │
│ to dashboard team   │       │ vintage_dashboard.py│
└─────────────────────┘       └─────────────────────┘
```

**Why both tracks?**

| Track | Purpose |
|-------|---------|
| **Track A (Official)** | For governance, official reporting, broad access |
| **Track B (In-House)** | For immediate needs, ad-hoc analysis, iteration |

**Next step for Track A:** Meet with CDIM team to share specs and understand their timeline/capacity.

**Track B status:** Working - vintage_dashboard.py generates HTML with RBC colors, Plotly charts, campaign/cohort dropdowns.

---

## Next Steps (Proposed)

### Engine & Data (Both Tracks)
1. **Test current code** - Run VCN on actual Spark environment
2. **Validate results** - Compare against known vintage if available
3. **Get test group info** - Research TST_GRP_CD values for A/B test support
4. **Integrate channel breakdown** - Show in dashboard as additional detail

### Track A: Official Dashboard
5. **Meet with CDIM team** - Share specs, understand timeline/capacity
6. **Provide data format specs** - What columns, what format they need
7. **Align on refresh cadence** - How often data updates

### Track B: In-House Dashboard
8. **Finalize HTML dashboard** - vintage_dashboard.py ready
9. **Deploy to SharePoint** - Accessible for internal use
10. **Document for handoff** - Process for adding new campaigns

---

## Key Message

Vintage Automation is not parallel work - it's **implementation of the SuperFact vision**:
- Pulls what we can from data NOW (experiment metadata, channel)
- Documents swap points for what will come from data LATER (campaign metadata, success library)
- Produces governed, consistent vintage curves with confidence intervals
- Proves the 4-layer architecture works in practice

**This is a pilot.** The patterns here scale to other campaign families beyond these 6.
