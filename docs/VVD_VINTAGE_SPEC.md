---
marp: true
theme: default
paginate: true
style: |
  section {
    font-size: 22px;
  }
  h1 {
    color: #003366;
    border-bottom: 3px solid #003366;
    padding-bottom: 10px;
  }
  table {
    font-size: 18px;
    width: 100%;
  }
  th {
    background: #003366;
    color: white;
  }
  .highlight {
    background: #e8f4fc;
    padding: 15px;
    border-left: 4px solid #003366;
  }
---

# VVD Vintage Curves
## Campaign Inventory & Dashboard Requirements

Marketing Analytics Team
January 2026

---

# Campaign Inventory

| Campaign | Primary Metric | Secondary | Type | Window | Cohorts |
|----------|----------------|-----------|------|--------|---------|
| **VCN** | Acquisition | Usage | Batch | 30 days | Monthly |
| **VDA** | Acquisition | Activation, Usage | Batch | 90 days | Seasonal (2x/yr) |
| **VDT** | Activation | - | Trigger | 30 days | Weekly → Monthly |
| **VUI** | Usage | - | Trigger | 30 days | Trigger |
| **VUT** | Tokenization | Usage | Trigger | 30 days | Trigger |
| **VAW** | Tokenization | Usage | Batch | 90 days | Batch |

**Total: 6 campaigns**

---

# Dashboard View - What's Always Visible

These elements are **always displayed** on every dashboard view:

| Element | Description |
|---------|-------------|
| **Test vs Control** | Both curves shown side-by-side for comparison |
| **Primary Success Metric** | Default view shows primary metric (Acquisition, Activation, etc.) |
| **Lift Calculation** | Difference between Test and Control rates |
| **Cohort Lines** | Multiple cohort curves on same chart |

> Test vs Control is NOT a dropdown - it's always visible for comparison

---

# Dashboard View - Toggleable Options

These elements can be **selected/filtered** by the user:

| Filter | Options | Notes |
|--------|---------|-------|
| **Campaign** | VCN, VDA, VDT, VUI, VUT, VAW | Select one campaign at a time |
| **Metric** | Primary / Secondary | Toggle between metrics (where available) |
| **Cohort** | All / Select specific | Filter to specific deployment waves |
| **Channel** | Email, Push, OLB, etc. | If segmentation exists |
| **Segment** | Client segments | If segmentation exists |
| **Window** | 30 / 60 / 90 days | Adjust measurement window |

---

# Dashboard Controls Summary

| Control | Type | Description |
|---------|------|-------------|
| **Campaign** | Dropdown | Select: VCN, VDA, VDT, VUI, VUT, VAW |
| **Metric** | Toggle | Switch between Primary / Secondary success |
| **Cohort** | Dropdown | Select deployment wave (or All) |
| **Segment** | Dropdown | Filter by RPT_GRP_CD (if available) |
| **Channel** | Dropdown | Filter by channel (if available) |

**Always Visible:** Test vs Control comparison on every view

---

# Metric Types (Reusable Logic)

| Metric Type | Definition | Used By |
|-------------|------------|---------|
| **Acquisition** | Card Issued | VCN, VDA |
| **Activation** | Card Activated | VDA, VDT |
| **Usage** | Purchase Made | VCN, VDA, VUI, VUT, VAW |
| **Tokenization** | Added to Wallet | VUT, VAW |

Same calculation logic reused across campaigns - just filter by campaign.

<div class="highlight">

**Next Step:** Discuss how to calculate each metric type.

</div>

---

# Questions for Discussion

1. **Segmentation** - Which campaigns have channel/segment breakdowns?

2. **Cohort Grouping** - Confirm weekly → monthly grouping for VDT

3. **Measurement Windows** - Are 30/90 day defaults correct?

4. **Data Access** - Confirm we can access all required tables

---

# Next Steps

| # | Action |
|---|--------|
| 1 | Confirm campaign definitions |
| 2 | Identify segmentation requirements |
| 3 | Build calculation logic for each metric |
| 4 | Create dashboard prototype |

