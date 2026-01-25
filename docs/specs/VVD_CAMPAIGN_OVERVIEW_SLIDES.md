---
marp: true
theme: default
paginate: true
header: 'VVD Campaign Overview'
footer: 'Marketing Analytics | January 2026'
style: |
  section {
    font-size: 24px;
  }
  h1 {
    color: #003366;
  }
  table {
    font-size: 18px;
  }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# VVD Campaign Overview

**Virtual Visa Debit Marketing Program**

Marketing Analytics Team
January 2026

---

# What is VVD?

**Virtual Visa Debit (VVD)** is a digital-first debit card product.

| Feature | Description |
|---------|-------------|
| **Instant Provisioning** | Card can be added to digital wallets immediately |
| **Digital Wallets** | Works with Apple Pay, Google Pay, Samsung Pay |
| **Contactless Ready** | Use right away for tap payments |
| **Online Shopping** | Works for e-commerce purchases |

> No need to wait for plastic card in the mail

---

# The Client Journey

We have **6 campaigns** that guide clients through the VVD lifecycle:

```
                        VVD CLIENT JOURNEY

    [Non-Holder] ──► [Card Issued] ──► [Card Activated] ──► [Card Used] ──► [In Wallet]
         │               │                  │                  │               │
         ▼               ▼                  ▼                  ▼               ▼
       VCN/VDA          ---               VDT                VUI           VUT/VAW
     (Acquisition)                     (Activation)        (Usage)      (Tokenization)
```

Each campaign targets a specific stage in the journey.

---

# Campaign Inventory

| Code | Campaign Name | Type | Primary Success | Secondary |
|------|---------------|------|-----------------|-----------|
| **VCN** | Contextual Notification | Trigger | Card issued | Usage |
| **VDA** | Black Friday / Cyber Monday | Batch | Card issued | Activation, Usage |
| **VDT** | Activation Trigger | Trigger | Card activated | - |
| **VUI** | Usage Trigger | Trigger | Purchase made | - |
| **VUT** | Tokenization Usage | Trigger | Added to wallet | Usage |
| **VAW** | Add To Wallet | Trigger | Added to wallet | Usage |

---

# Campaign Types

## Trigger Campaigns (5 of 6)
- Run **continuously** (monthly/weekly)
- Target clients when they meet criteria
- Many deployment waves over time
- VCN, VDT, VUI, VUT, VAW

## Batch Campaigns (1 of 6)
- Run at **specific times** (seasonal)
- Target a fixed population
- Fewer but larger deployments
- VDA (Black Friday / Cyber Monday)

---

# VCN & VDA: Acquisition

**Goal:** Get clients to open a VVD card

| Attribute | VCN | VDA |
|-----------|-----|-----|
| **Full Name** | Contextual Notification | Black Friday / Cyber Monday |
| **Type** | Trigger (monthly) | Batch (seasonal) |
| **Target** | Eligible non-holders | Eligible non-holders |
| **Success** | Card issued | Card issued |
| **Timing** | Ongoing | November (annual) |

**Success = Client receives a new VVD card**

---

# VDT: Activation

**Goal:** Get cardholders to activate their card

| Attribute | Details |
|-----------|---------|
| **Full Name** | VVD Activation Trigger |
| **Type** | Trigger |
| **Target** | Clients with unactivated VVD cards |
| **Success** | Card activated |
| **Special** | Includes 15-day reminder |

**Success = Client activates their VVD card**

---

# VUI: Usage

**Goal:** Get cardholders to use their card

| Attribute | Details |
|-----------|---------|
| **Full Name** | VVD Usage Trigger |
| **Type** | Trigger |
| **Target** | Clients with low/no usage |
| **Success** | Purchase transaction made |

**Success = Client makes a purchase with VVD**

---

# VUT & VAW: Tokenization

**Goal:** Get cardholders to add card to digital wallet

| Attribute | VUT | VAW |
|-----------|-----|-----|
| **Full Name** | Tokenization Usage | Add To Wallet |
| **Type** | Trigger | Trigger |
| **Target** | Cardholders without wallet | Cardholders without wallet |
| **Success** | Added to wallet | Added to wallet |

**Success = Client provisions VVD to Apple Pay, Google Pay, etc.**

---

# Test vs Control Design

All campaigns use an **experimental design**:

| Group | What Happens | Purpose |
|-------|--------------|---------|
| **Test (TG4)** | Receives marketing message | Measure conversion |
| **Control** | Eligible but held out | Baseline comparison |

## Why Control Groups?

- Measure **incremental impact** of marketing
- Answer: "How many conversions did the campaign actually drive?"
- Some clients would convert anyway without marketing

---

# How We Measure: Vintage Curves

A **vintage curve** shows how conversions accumulate over time.

```
Cumulative
Rate (%)
    │
  5%├─────────────────────────────────═══════
    │                          ═══════
  4%├─────────────────────═════
    │                ════
  3%├────────────════
    │         ═══
  2%├──────═══
    │    ══
  1%├──══
    │══
    └─────┬─────┬─────┬─────┬─────┬─────┬────
          5    10    15    20    25    30
                Days After Treatment
```

---

# What Vintage Curves Tell Us

| Question | Answer From Curve |
|----------|-------------------|
| **Final conversion rate?** | Where the curve plateaus |
| **How fast do clients convert?** | Steepness of the curve |
| **Is campaign working?** | Gap between Test & Control |
| **Consistent results?** | Do cohorts follow same pattern? |
| **Optimal measurement window?** | When does curve flatten? |

---

# Example: Test vs Control Comparison

```
Rate (%)
    │
  5%├───────────────────────────── Test (TG4)
    │                          ╱
  4%├─────────────────────────╱─────────────
    │                   ════════════ Control
  3%├─────────────────╱═════
    │             ═══╱
  2%├────────────╱═══
    │       ═══╱
  1%├─────╱═══
    │═══╱
    └─────┬─────┬─────┬─────┬─────┬─────┬────
          5    10    15    20    25    30

    Lift = Test Rate - Control Rate = 5% - 3% = 2% incremental
```

---

# Success Metrics Summary

| Campaign | Primary Success | Secondary Success |
|----------|-----------------|-------------------|
| VCN | Card Issued | Usage |
| VDA | Card Issued | Activation, Usage |
| VDT | Card Activated | - |
| VUI | Purchase Made | - |
| VUT | Added to Wallet | Usage |
| VAW | Added to Wallet | Usage |

---

# Segmentation Considerations

Campaigns **may** include breakdowns by:

| Dimension | Example |
|-----------|---------|
| **Channel** | Email, Push, OLB Banner |
| **Segment** | Client risk/value groupings |
| **Model Score** | Propensity model tier |

**Status:** Segmentation details vary by campaign.
Not all campaigns have complex segmentation.

---

# Key Questions

1. **Measurement windows**
   - How many days after treatment before we measure?

2. **Segmentation needs**
   - Which campaigns need segment breakdowns?

3. **Reporting cadence**
   - How often do we refresh results?

4. **Lift presentation**
   - How do we present Test vs Control comparisons?

---

<!-- _class: lead -->

# Next Steps

1. Confirm campaign definitions are accurate
2. Identify segmentation requirements
3. Align on measurement windows
4. Build the measurement framework

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Questions?

**VVD Campaign Overview**

Marketing Analytics Team
January 2026
