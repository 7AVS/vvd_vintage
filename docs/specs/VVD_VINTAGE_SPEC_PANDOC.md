---
title: VVD Vintage Curves
subtitle: Campaign Inventory & Dashboard Requirements
author: Marketing Analytics Team
date: January 2026
---

# Campaign Inventory

| Campaign | Primary Metric | Secondary | Type | Window | Cohorts |
|----------|----------------|-----------|------|--------|---------|
| VCN | Acquisition | Usage | Batch | 30 days | Monthly |
| VDA | Acquisition | Activation, Usage | Batch | 90 days | Seasonal (2x/yr) |
| VDT | Activation | - | Trigger | 30 days | Weekly → Monthly |
| VUI | Usage | - | Trigger | 30 days | Trigger |
| VUT | Tokenization | Usage | Trigger | 30 days | Trigger |
| VAW | Tokenization | Usage | Batch | 90 days | Batch |

**Total: 6 campaigns**

# Dashboard - Always Visible

These elements are always displayed:

| Element | Description |
|---------|-------------|
| Test vs Control | Both curves shown side-by-side |
| Primary Success | Default metric view |
| Lift Calculation | Difference between Test and Control |

Test vs Control is NOT a dropdown - always visible for comparison.

# Dashboard - Toggleable Options

| Control | Type | Description |
|---------|------|-------------|
| Campaign | Dropdown | VCN, VDA, VDT, VUI, VUT, VAW |
| Metric | Toggle | Primary / Secondary success |
| Cohort | Dropdown | Select deployment wave (or All) |
| Segment | Dropdown | Filter by RPT_GRP_CD |
| Channel | Dropdown | Filter by channel |

# Metric Types (Reusable Logic)

| Metric Type | Definition | Used By |
|-------------|------------|---------|
| Acquisition | Card Issued | VCN, VDA |
| Activation | Card Activated | VDA, VDT |
| Usage | Purchase Made | VCN, VDA, VUI, VUT, VAW |
| Tokenization | Added to Wallet | VUT, VAW |

Same calculation logic reused across campaigns.

# Questions for Discussion

1. Which campaigns have segment breakdowns?
2. Confirm weekly → monthly grouping for VDT
3. Are 30/90 day windows correct?
4. Confirm data access for all tables

# Next Steps

| # | Action |
|---|--------|
| 1 | Confirm campaign definitions |
| 2 | Identify segmentation requirements |
| 3 | Build calculation logic for each metric |
| 4 | Create dashboard prototype |
