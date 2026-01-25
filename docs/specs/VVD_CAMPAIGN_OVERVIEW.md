# VVD Campaign Overview

**Purpose:** High-level summary of VVD (Virtual Visa Debit) marketing campaigns for stakeholder alignment.

---

## What is VVD?

Virtual Visa Debit (VVD) is a digital-first debit card product. Unlike traditional plastic cards, VVD can be provisioned instantly to digital wallets (Apple Pay, Google Pay) and used immediately for online or contactless purchases.

---

## The VVD Marketing Program

The VVD marketing program consists of **6 campaigns** that guide clients through the product lifecycle:

```
CLIENT JOURNEY:

    [Non-Holder] → [Card Issued] → [Card Activated] → [Card Used] → [Added to Wallet]
         ↑              ↑               ↑                ↑              ↑
        VCN            VDA             VDT              VUI          VUT/VAW
        VDA         (acquisition)   (activation)      (usage)      (tokenization)
```

---

## Campaign Inventory

### Summary Table

| # | Code | Campaign Name | Deployment | Primary Success | Secondary |
|---|------|---------------|------------|-----------------|-----------|
| 1 | VCN | Contextual Notification | Trigger | Card issued | Usage |
| 2 | VDA | Black Friday / Cyber Monday | Batch | Card issued | Activation, Usage |
| 3 | VDT | Activation Trigger | Trigger | Card activated | - |
| 4 | VUI | Usage Trigger | Trigger | Purchase made | - |
| 5 | VUT | Tokenization Usage | Trigger | Added to wallet | Usage |
| 6 | VAW | Add To Wallet | Trigger | Added to wallet | Usage |

---

## Detailed Campaign Descriptions

### 1. VCN - Contextual Notification (Acquisition)

**Business Goal:** Encourage eligible clients to open a VVD card.

**Who receives it:** Clients who are identified as good candidates for VVD but don't have one yet.

**Deployment Type:** **Trigger** - Runs monthly, sending targeted messages to eligible clients.

**Success Metric:** Client opens (is issued) a VVD card.

**How we measure success:**
- Did the client receive a VVD card after receiving the marketing message?
- We track "card issue date" to determine success.

---

### 2. VDA - Black Friday / Cyber Monday (Acquisition)

**Business Goal:** Drive VVD card acquisition during high-shopping season.

**Who receives it:** Eligible clients targeted during the Black Friday / Cyber Monday period.

**Deployment Type:** **Batch** - Seasonal campaign, typically runs once per year around November.

**Success Metric:** Client opens (is issued) a VVD card.

**How we measure success:**
- Same as VCN - track "card issue date"
- Longer measurement window due to seasonal nature

---

### 3. VDT - Activation Trigger

**Business Goal:** Get clients who have been issued a VVD card to activate it.

**Who receives it:** Clients who have a VVD card but haven't activated it yet.

**Deployment Type:** **Trigger** - Ongoing, targets clients shortly after card issuance. Includes a 15-day reminder if no response.

**Success Metric:** Client activates their VVD card.

**How we measure success:**
- Did the client activate their card after receiving the message?
- We track "card activation date" to determine success.

---

### 4. VUI - Usage Trigger

**Business Goal:** Encourage VVD cardholders to make purchases with their card.

**Who receives it:** Clients with an activated VVD card who haven't used it (or haven't used it recently).

**Deployment Type:** **Trigger** - Ongoing, targets inactive or low-usage cardholders.

**Success Metric:** Client makes a purchase transaction with their VVD card.

**How we measure success:**
- Did the client make a purchase after receiving the message?
- We track "transaction date" for qualifying purchases.

---

### 5. VUT - Tokenization Usage

**Business Goal:** Get VVD cardholders to add their card to a digital wallet (Apple Pay, Google Pay, etc.).

**Who receives it:** Clients with a VVD card who haven't added it to a digital wallet yet.

**Deployment Type:** **Trigger** - Ongoing, targets eligible cardholders.

**Success Metric:** Client provisions their VVD card to a digital wallet.

**How we measure success:**
- Did the client add their card to Apple Pay, Google Pay, or similar?
- We track "wallet provisioning date" to determine success.

---

### 6. VAW - Add To Wallet Contextual Notification

**Business Goal:** Same as VUT - encourage digital wallet adoption.

**Who receives it:** Similar to VUT, but with different targeting or messaging approach.

**Deployment Type:** **Trigger** - Contextual notification approach.

**Success Metric:** Client provisions their VVD card to a digital wallet.

**How we measure success:**
- Same as VUT - track "wallet provisioning date"

---

## Campaign Types Explained

### Trigger Campaigns (VCN, VDT, VUI, VUT, VAW)

- Run on an **ongoing basis** (monthly, weekly, or event-driven)
- Target clients when they meet specific criteria or timing
- Produce **many cohorts** (deployment waves) over time
- Example: Every month, we identify newly eligible clients and send them a VCN message

### Batch Campaigns (VDA)

- Run at **specific points in time** (seasonal, annual)
- Target a defined population for a specific promotional period
- Produce **fewer cohorts** but often larger populations
- Example: Black Friday campaign runs once per year in November

---

## Segmentation

Campaigns may include segmentation based on:

- **Channel:** How the message is delivered (email, push notification, OLB banner, etc.)
- **Segment codes:** Groupings based on client characteristics (e.g., risk profile, product holdings)
- **Model scores:** Propensity or targeting model scores

**Current Status:** Segmentation details are defined in individual campaign technical specifications. Not all campaigns have complex segmentation.

---

## Test vs Control Groups

All campaigns use a **Test vs Control** experimental design:

| Group | Description |
|-------|-------------|
| **Test (TG4)** | Clients who receive the marketing treatment |
| **Control** | Clients who are eligible but held out from treatment |

Comparing Test vs Control allows us to measure the **incremental impact** of the marketing campaign - how many conversions are attributable to the campaign vs what would have happened anyway.

---

## How We Measure: Vintage Curves

### What is a Vintage Curve?

A vintage curve shows **how conversions accumulate over time** after clients receive a marketing message.

```
Example: Acquisition Campaign (30-day window)

Cumulative
Conversion
Rate (%)
    |
  5%│                         ___________
    │                    ____/
  4%│               ____/
    │          ____/
  3%│     ____/
    │____/
  2%│
    │
  1%│
    │
    └────────────────────────────────────────
       0    5    10   15   20   25   30
              Days After Treatment
```

### Why Vintage Curves?

1. **See how quickly clients convert** - Some campaigns drive fast action, others are slower
2. **Compare cohorts** - Are newer deployment waves performing better or worse than older ones?
3. **Compare Test vs Control** - Is the campaign driving incremental conversions?
4. **Determine optimal measurement windows** - How long should we wait before measuring results?

### What a Vintage Curve Answers

| Question | What the Curve Shows |
|----------|---------------------|
| What's the final conversion rate? | The endpoint (plateau) of the curve |
| How fast do clients convert? | The steepness/slope of the curve |
| Is Test outperforming Control? | Gap between Test and Control curves |
| Are results consistent? | Do multiple cohorts follow similar patterns? |

---

## Success Metrics Summary

| Campaign | Primary Success | Secondary Success |
|----------|-----------------|-------------------|
| VCN | Card Issued | Usage |
| VDA | Card Issued | Activation, Usage |
| VDT | Card Activated | - |
| VUI | Purchase Made | - |
| VUT | Added to Wallet | Usage |
| VAW | Added to Wallet | Usage |

---

## Key Questions for Discussion

1. **Measurement windows:** How many days after treatment do we wait before declaring a campaign "done"?

2. **Segmentation needs:** Which campaigns require breakdowns by segment, channel, or model?

3. **Reporting cadence:** How often do we need to refresh vintage curves? Monthly? After each deployment?

4. **Lift calculation:** How should we calculate and present the Test vs Control lift?

---

## Next Steps

1. Confirm campaign definitions and success metrics are accurate
2. Identify any missing campaigns or success metrics
3. Determine segmentation requirements for each campaign
4. Align on measurement windows and reporting cadence
5. Build the measurement framework

---

*Document created: January 2026*
*Status: Draft for stakeholder review*
