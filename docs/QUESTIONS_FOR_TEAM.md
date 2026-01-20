# Questions for Director / Team - Vintage Pipeline

**Created:** January 2026
**Purpose:** Questions that need answers before finalizing the vintage pipeline architecture

---

## 1. Martech Data Pipeline (Critical for Layer 1)

### The Core Question

When Martech deploys a campaign, they create codes (RPT_GRP_CD, TST_GRP_CD, channel codes, etc.). These codes appear in `tactic_evnt_hist`, but **what do the codes MEAN?**

| What We See in Database | What We Need to Know |
|-------------------------|---------------------|
| RPT_GRP_CD = 'A01' | What segment is A01? (e.g., "High Value Digital") |
| TST_GRP_CD = 'TG4' | Is TG4 always Test? What are Control codes? |
| CHNL_CD = '5' | What channel is 5? (e.g., "Email", "Mobile") |
| TACTIC_CELL_CD = 'XYZ' | What does this cell represent? |

### Questions for Martech

| Question | Why It Matters |
|----------|----------------|
| Does Martech feed the MEANING of campaign codes into any database table? | If yes, we can automate Layer 1 |
| Is there a lookup table that maps RPT_GRP_CD → Segment Name? | Enables segment breakdowns |
| Is there a table that captures Channel codes → Channel description? | Enables channel analysis |
| Can we access the deployment pipeline to capture settings at creation time? | Real-time Layer 1 population |

### If No Structured Data Exists

We must manually extract from technical specification documents and create hardcoded lookups. This is what we're doing now for VVD.

**Recommendation:** If this information doesn't exist in a table, propose that Martech add it to their pipeline. It would benefit all downstream reporting.

---

## 2. Tactic Table Selection

| Question | Options |
|----------|---------|
| Which tactic table should be primary? | `tactic_evnt_hist` vs `ods_mr_hist` |
| How do we filter for VVD campaigns specifically? | TACTIC_ID prefix? SRVC_ID? Other? |
| Are there campaigns that span multiple MNEs? | Affects how we structure queries |

---

## 3. Test/Control Group Standards

| Question | Context |
|----------|---------|
| Is TG4 always the Test group for ALL campaigns? | Or does it vary by campaign? |
| What TST_GRP_CD values indicate Control? | TG1, TG2, TG3? All non-TG4? |
| Are there campaigns with multiple test groups? | e.g., TG4 = Treatment A, TG5 = Treatment B |

---

## 4. Channel Feedback Data

| Question | Context |
|----------|---------|
| Do we have access to feedback tables for all channels? | We have Email, need to confirm others |
| How do we join channel feedback to tactic data? | TREATMENT_ID? CLNT_NO + date? |
| What's the latency on channel feedback? | Same day? Next day? Weekly? |

---

## 5. Fulfillment Data

| Question | Context |
|----------|---------|
| Which campaigns have fulfillment (rewards/cashback)? | Not all campaigns have offers |
| How do we identify fulfillment records for a specific campaign? | TACTIC_ID pattern? Other? |
| What's the typical lag between success and fulfillment? | Affects measurement window |

---

## 6. Access & Connectivity

| Question | Context |
|----------|---------|
| Can we use EDW.cursor() from Lumina for all EDW tables? | Token, Email, Fulfillment need EDW |
| Are there any tables we don't have access to? | Need to confirm before building |
| Any rate limits or query restrictions? | For large historical pulls |

---

## 7. Existing Work / Avoiding Duplication

| Question | Context |
|----------|---------|
| Has anyone already built Layer 1 lookup tables? | Don't want to duplicate effort |
| Are there existing vintage pipelines we should reference? | Learn from existing approaches |
| Who else is working on Success Library / SuperFact? | Coordinate efforts |

---

## Summary: Top 3 Critical Questions

1. **Does Martech have a structured table with code meanings?**
   - If yes → automate Layer 1
   - If no → hardcode + propose they add it

2. **Which tactic table is primary and how do we filter for VVD?**
   - Determines Module 1 structure

3. **Is TG4 always Test across all campaigns?**
   - Affects Test/Control logic

---

*Document created: January 2026*
