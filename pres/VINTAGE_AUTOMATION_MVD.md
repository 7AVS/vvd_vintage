# MVD: Vintage Automation Architecture Diagram

**Purpose:** Visual documentation for director presentation
**Created:** January 2026
**Status:** Ready for Draw.io creation

---

## Overview

This MVD (Minimum Viable Document) defines the content and structure for the Vintage Automation architecture diagrams. The diagrams explain:

1. How Vintage Automation implements the SuperFact 4-layer framework
2. The modular "swap point" architecture with SPECIFIC details on what swaps to what
3. The virtuous cycle - how building vintages GROWS the Success Library and enriches metadata
4. Output tracks (Official vs In-house dashboards)

---

## Target Audience

**Who:** Director (developed the SuperFact 4-layer framework)
**What they know:** SuperFact deeply - they created it
**What they need to see:** Working pilot that proves the architecture works
**Decision needed:** None - awareness and alignment

---

## Diagram Pages

---

# PAGE 1: The Big Picture

**Title:** Vintage Automation Engine - SuperFact Implementation

**Layout:** Top-to-bottom flow

**Content:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUPERFACT 4-LAYER FRAMEWORK                          │
│                                                                              │
│   Layer 1              Layer 2              Layer 3              Layer 4     │
│   Experiment           Campaign             Success              Client      │
│   Metadata             Metadata             Library              Journey     │
│                                                                              │
│   "Who's in test?"     "What to measure?"   "How to calculate?"  "What did  │
│                                                                   they do?" │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VINTAGE AUTOMATION ENGINE                             │
│                         (vintage_all_in_one.py)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INPUTS FROM LAYERS:                                                        │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │  Layer 1    │  │  Layer 2    │  │  Layer 3    │  │  Layer 4    │        │
│   │             │  │             │  │             │  │             │        │
│   │ tactic_evnt │  │ Campaign    │  │ Success     │  │ VISA_DR_CRD │        │
│   │ _hist       │  │ Config      │  │ Definitions │  │ Email Data  │        │
│   │             │  │             │  │             │  │             │        │
│   │ FROM DATA   │  │ SWAP POINT  │  │ SWAP POINT  │  │ FROM DATA   │        │
│   │     🔵      │  │     🟡      │  │     🟡      │  │     🔵      │        │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                                              │
│   ENGINE CORE (stable - doesn't change when sources change):                 │
│   ├── detect_success()                                                       │
│   ├── build_vintage_data()                                                   │
│   ├── calculate_ci()                                                         │
│   └── generate_summary()                                                     │
│                                                                              │
│   PILOTS: VCN, VDA, VDT, VUI, VUT, VAW (6 campaigns)                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │   CSV / HDFS    │
                            │     OUTPUT      │
                            └────────┬────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      │                             │
                      ▼                             ▼
         ┌─────────────────────┐       ┌─────────────────────┐
         │     TRACK A         │       │     TRACK B         │
         │     Official        │       │     In-House        │
         ├─────────────────────┤       ├─────────────────────┤
         │ Who: CIDM team      │       │ Who: Us             │
         │ Tool: Tableau       │       │ Tool: HTML/Plotly   │
         │ Location: Governed  │       │ Location: SharePoint│
         │ Status: Pending     │       │ Status: Ready       │
         └─────────────────────┘       └─────────────────────┘
```

---

# PAGE 2: The Virtuous Cycle - Success Library Growth

**Title:** Building the Source of Truth Through Success Library

**Key Message:** As we add campaigns, we MUST understand their success metrics. When we do that, we document them in the Success Library. The Success Library GROWS. Governance improves. Next campaign is FASTER.

**THIS IS THE CORE VALUE PROPOSITION**

## The Cycle Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│                           THE VIRTUOUS CYCLE                                             │
│                   Building the Source of Truth                                           │
│                                                                                          │
│                                                                                          │
│                          ┌─────────────────────┐                                         │
│                          │                     │                                         │
│                          │   NEW CAMPAIGN      │                                         │
│                          │   ONBOARDED         │                                         │
│                          │   (e.g., VCN)       │                                         │
│                          │                     │                                         │
│                          └──────────┬──────────┘                                         │
│                                     │                                                    │
│                                     ▼                                                    │
│                          ┌─────────────────────┐                                         │
│                          │                     │                                         │
│                          │   UNDERSTAND THE    │                                         │
│                          │   SUCCESS METRIC    │                                         │
│                          │                     │                                         │
│                          │   "What does        │                                         │
│                          │    success mean     │                                         │
│                          │    for this         │                                         │
│                          │    campaign?"       │                                         │
│                          │                     │                                         │
│                          └──────────┬──────────┘                                         │
│                                     │                                                    │
│                                     ▼                                                    │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                                  │   │
│   │                    DOCUMENT IN SUCCESS LIBRARY (Layer 3)                         │   │
│   │                                                                                  │   │
│   │   For VCN (Card Acquisition), we document:                                       │   │
│   │                                                                                  │   │
│   │   ┌──────────────────────────────────────────────────────────────────────────┐  │   │
│   │   │  METRIC: card_acquisition                                                 │  │   │
│   │   │                                                                           │  │   │
│   │   │  SOURCE TABLE: VISA_DR_CRD                                                │  │   │
│   │   │  PATH: /prod/sz/tsz/00050/data/DDWTA_VISA_DR_CRD/                         │  │   │
│   │   │                                                                           │  │   │
│   │   │  FILTERS:                                                                 │  │   │
│   │   │    • STS_CD IN ('06', '08')  -- Active card statuses                      │  │   │
│   │   │    • SRVC_ID = 36            -- VVD service ID                            │  │   │
│   │   │    • ISS_DT IS NOT NULL      -- Card was actually issued                  │  │   │
│   │   │                                                                           │  │   │
│   │   │  DATE FIELD: ISS_DT (issuance date)                                       │  │   │
│   │   │  CLIENT FIELD: CLNT_NO                                                    │  │   │
│   │   │                                                                           │  │   │
│   │   │  BUSINESS RULE: Client acquired a new VVD card                            │  │   │
│   │   └──────────────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                                  │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                     │                                                    │
│                                     ▼                                                    │
│                          ┌─────────────────────┐                                         │
│                          │                     │                                         │
│                          │  SUCCESS LIBRARY    │                                         │
│                          │  GROWS              │                                         │
│                          │                     │                                         │
│                          │  • Metric defined   │                                         │
│                          │  • Logic documented │                                         │
│                          │  • Reusable now     │                                         │
│                          │                     │                                         │
│                          └──────────┬──────────┘                                         │
│                                     │                                                    │
│                                     ▼                                                    │
│                          ┌─────────────────────┐                                         │
│                          │                     │                                         │
│                          │  GOVERNANCE         │                                         │
│                          │  IMPROVES           │                                         │
│                          │                     │                                         │
│                          │  • Single source    │                                         │
│                          │    of truth         │                                         │
│                          │  • Audit trail      │                                         │
│                          │  • Version control  │                                         │
│                          │                     │                                         │
│                          └──────────┬──────────┘                                         │
│                                     │                                                    │
│                                     ▼                                                    │
│                          ┌─────────────────────┐                                         │
│                          │                     │                                         │
│                          │  NEXT CAMPAIGN      │◄────────────────────────────────────┐   │
│                          │  IS FASTER          │                                     │   │
│                          │                     │                                     │   │
│                          │  • Reuse existing   │                                     │   │
│                          │    metrics          │                                     │   │
│                          │  • Only define new  │                                     │   │
│                          │    ones if needed   │                                     │   │
│                          │                     │                                     │   │
│                          └─────────────────────┘                                     │   │
│                                                                                      │   │
│                                                                                      │   │
│   ◄──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## The Progression: Success Library Growth

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        SUCCESS LIBRARY GROWTH OVER TIME                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  CAMPAIGN 1: VCN (Contextual Notification)                                               │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Need to measure: Card Acquisition                                                │   │
│  │  Action: DEFINE new metric "card_acquisition"                                     │   │
│  │                                                                                   │   │
│  │  SUCCESS LIBRARY AFTER: 1 metric                                                  │   │
│  │  ┌─────────────────┐                                                              │   │
│  │  │ card_acquisition│                                                              │   │
│  │  └─────────────────┘                                                              │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                            │                                             │
│                                            ▼                                             │
│  CAMPAIGN 2: VDA (Black Friday Cyber Monday)                                             │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Need to measure: Card Acquisition                                                │   │
│  │  Action: REUSE "card_acquisition" - already defined!                              │   │
│  │                                                                                   │   │
│  │  SUCCESS LIBRARY AFTER: 1 metric (no change)                                      │   │
│  │  ┌─────────────────┐                                                              │   │
│  │  │ card_acquisition│  ← REUSED                                                    │   │
│  │  └─────────────────┘                                                              │   │
│  │                                                                                   │   │
│  │  TIME SAVED: 100% - zero metric definition work                                   │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                            │                                             │
│                                            ▼                                             │
│  CAMPAIGN 3: VDT (Activation Trigger)                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Need to measure: Card Activation (different from acquisition!)                   │   │
│  │  Action: DEFINE new metric "card_activation"                                      │   │
│  │                                                                                   │   │
│  │  SUCCESS LIBRARY AFTER: 2 metrics                                                 │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                                         │   │
│  │  │ card_acquisition│  │ card_activation │  ← NEW                                  │   │
│  │  └─────────────────┘  └─────────────────┘                                         │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                            │                                             │
│                                            ▼                                             │
│  CAMPAIGN 4: VUI (Usage Trigger)                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Need to measure: Card Usage (transactions)                                       │   │
│  │  Action: DEFINE new metric "card_usage"                                           │   │
│  │                                                                                   │   │
│  │  SUCCESS LIBRARY AFTER: 3 metrics                                                 │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                    │   │
│  │  │ card_acquisition│  │ card_activation │  │ card_usage      │  ← NEW             │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                    │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                            │                                             │
│                                            ▼                                             │
│  CAMPAIGN 5: VUT (Tokenization Usage)                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Need to measure: Wallet Provisioning (tokenization)                              │   │
│  │  Action: DEFINE new metric "wallet_provisioning"                                  │   │
│  │                                                                                   │   │
│  │  SUCCESS LIBRARY AFTER: 4 metrics                                                 │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐│   │
│  │  │ card_acquisition│  │ card_activation │  │ card_usage      │  │wallet_provision││   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └────────────────┘│   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                            │                                             │
│                                            ▼                                             │
│  CAMPAIGN 6: VAW (Add To Wallet)                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Need to measure: Wallet Provisioning                                             │   │
│  │  Action: REUSE "wallet_provisioning" - already defined!                           │   │
│  │                                                                                   │   │
│  │  SUCCESS LIBRARY AFTER: 4 metrics (no change)                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐│   │
│  │  │ card_acquisition│  │ card_activation │  │ card_usage      │  │wallet_provision││   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └────────────────┘│   │
│  │                                                                        ↑          │   │
│  │                                                                     REUSED        │   │
│  │  TIME SAVED: 100% - zero metric definition work                                   │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  RESULT: 6 campaigns onboarded, only 4 unique metrics defined                           │
│                                                                                          │
│  FUTURE: Campaign 7, 8, 9... likely REUSE existing metrics                              │
│          Only define new metrics when truly new success criteria needed                  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Key Callout Box

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│   "Every campaign onboarded enriches our metadata ecosystem.                             │
│    We're not just measuring campaigns - we're BUILDING THE SOURCE OF TRUTH.              │
│                                                                                          │
│    The Success Library grows.                                                            │
│    Governance improves.                                                                  │
│    Future campaigns onboard faster.                                                      │
│    The organization benefits."                                                           │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# PAGE 3: Swap Points - DETAILED

**Title:** Modular Swap Architecture - What Swaps To What

**Key Message:** Each hardcoded component has a SPECIFIC future replacement. When infrastructure is ready, we swap - no engine rewrite.

## Layer 2: Campaign Metadata - DETAILED SWAP

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│  LAYER 2: Campaign Metadata                                                              │
│  Question: "What metric should we measure for this campaign?"                            │
│                                                                                          │
├────────────────────────────────────────┬────────────────────────────────────────────────┤
│                                        │                                                 │
│  TODAY: HARDCODED                      │  FUTURE: QUERY MNEMONIC MAPPING v2              │
│                                        │                                                 │
│  ┌──────────────────────────────────┐  │  ┌──────────────────────────────────────────┐  │
│  │                                  │  │  │                                          │  │
│  │  CAMPAIGN_METADATA = {           │  │  │  SELECT                                  │  │
│  │      "VCN": {                    │  │  │      primary_metric,                     │  │
│  │          "campaign_name":        │  │  │      secondary_metric,                   │  │
│  │            "Contextual           │  │  │      campaign_name,                      │  │
│  │             Notification",       │  │  │      measurement_category                │  │
│  │          "success_type":         │  │  │  FROM CIDM_MNEMONIC_ATTRS                │  │
│  │            "ACQUISITION",        │  │  │  WHERE mne = 'VCN'                       │  │
│  │          "primary_metric":       │  │  │                                          │  │
│  │            "card_acquisition"    │  │  │  -- Returns the same info but from       │  │
│  │      },                          │  │  │  -- governed metadata table              │  │
│  │      "VDA": {...},               │  │  │                                          │  │
│  │      "VDT": {...},               │  │  │  When Mnemonic Mapping v2 has:           │  │
│  │      "VUI": {...},               │  │  │  • Primary Metric field                  │  │
│  │      "VUT": {...},               │  │  │  • Secondary Metric field                │  │
│  │      "VAW": {...}                │  │  │  • Tertiary Metric field                 │  │
│  │  }                               │  │  │                                          │  │
│  │                                  │  │  │  ...this dict becomes a query            │  │
│  └──────────────────────────────────┘  │  └──────────────────────────────────────────┘  │
│                                        │                                                 │
│  WHAT'S HARDCODED:                     │  WHAT IT SWAPS TO:                              │
│  • 6 campaigns × 3 fields = 18 items   │  • Single query function                        │
│  • Adding new campaign = edit code     │  • Adding new campaign = add row to table       │
│                                        │                                                 │
├────────────────────────────────────────┴────────────────────────────────────────────────┤
│                                                                                          │
│  SWAP TRIGGER: When Mnemonic Mapping v2 table has Primary/Secondary metric fields       │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Layer 3: Success Definitions - DETAILED SWAP

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│  LAYER 3: Success Definitions                                                            │
│  Question: "HOW do we calculate this metric?"                                            │
│                                                                                          │
├────────────────────────────────────────┬────────────────────────────────────────────────┤
│                                        │                                                 │
│  TODAY: HARDCODED                      │  FUTURE: SUCCESS LIBRARY                        │
│                                        │                                                 │
│  ┌──────────────────────────────────┐  │  ┌──────────────────────────────────────────┐  │
│  │                                  │  │  │  OPTION A: GitHub %Run                   │  │
│  │  SUCCESS_DEFINITIONS = {         │  │  │  ─────────────────────────               │  │
│  │      "card_acquisition": {       │  │  │                                          │  │
│  │          "description":          │  │  │  %run /success_library/metrics/          │  │
│  │            "Client acquired      │  │  │        card_acquisition.py               │  │
│  │             a new VVD card",     │  │  │                                          │  │
│  │          "source": "HIVE",       │  │  │  # Code file contains:                   │  │
│  │          "table_path":           │  │  │  # - Table path                          │  │
│  │            "/prod/.../           │  │  │  # - All filters                         │  │
│  │             VISA_DR_CRD/",       │  │  │  # - Business rules                      │  │
│  │          "date_field": "ISS_DT", │  │  │  # - Version history                     │  │
│  │          "client_field":         │  │  │                                          │  │
│  │            "CLNT_NO",            │  │  │  def get_success(spark, clients):        │  │
│  │          "filters": {            │  │  │      return spark.read(...)              │  │
│  │              "STS_CD":           │  │  │          .filter(STS_CD in ...)          │  │
│  │                ["06", "08"],     │  │  │          .filter(SRVC_ID == 36)          │  │
│  │              "SRVC_ID": 36,      │  │  │                                          │  │
│  │              "ISS_DT_NOT_NULL":  │  │  ├──────────────────────────────────────────┤  │
│  │                True              │  │  │  OPTION B: Curated Dataset               │  │
│  │          }                       │  │  │  ──────────────────────────              │  │
│  │      },                          │  │  │                                          │  │
│  │      "card_activation": {...},   │  │  │  SELECT * FROM                           │  │
│  │      "card_usage": {...},        │  │  │    semantic.success_card_acquisition     │  │
│  │      "wallet_provisioning":{...} │  │  │  WHERE clnt_no IN (...)                  │  │
│  │  }                               │  │  │                                          │  │
│  │                                  │  │  │  -- Pre-filtered, curated data           │  │
│  │                                  │  │  │  -- Just join, no filter logic needed    │  │
│  └──────────────────────────────────┘  │  └──────────────────────────────────────────┘  │
│                                        │                                                 │
│  WHAT'S HARDCODED:                     │  WHAT IT SWAPS TO:                              │
│  • 4 metrics × 6 fields = 24 items     │  • GitHub repo with versioned code files        │
│  • Filter logic inline in Python       │  • OR curated semantic layer tables             │
│  • Business rules as comments          │  • Self-documenting, governed, reusable         │
│                                        │                                                 │
├────────────────────────────────────────┴────────────────────────────────────────────────┤
│                                                                                          │
│  SWAP TRIGGER: When Success Library GitHub repo OR curated semantic layer exists         │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Layer 1 & 4: Already From Data (Minor Swaps)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│  LAYER 1: Experiment Metadata - ALREADY FROM DATA                                        │
│                                                                                          │
├────────────────────────────────────────┬────────────────────────────────────────────────┤
│                                        │                                                 │
│  TODAY                                 │  FUTURE (minor enhancement)                     │
│                                        │                                                 │
│  ┌──────────────────────────────────┐  │  ┌──────────────────────────────────────────┐  │
│  │  Source: tactic_evnt_hist        │  │  │  Same source, but enriched with:         │  │
│  │          (parquet files)         │  │  │                                          │  │
│  │                                  │  │  │  • Experiment Metadata table             │  │
│  │  What we pull:                   │  │  │    (experiment name, hypothesis,         │  │
│  │  • CLNT_NO (client)              │  │  │     test purpose, active dates)          │  │
│  │  • TST_GRP_CD (test group)       │  │  │                                          │  │
│  │  • TREATMT_STRT_DT (start)       │  │  │  • Dynamic test group definitions        │  │
│  │  • TREATMT_END_DT (end)          │  │  │    (not hardcoded TG4 = Test)            │  │
│  │  • TACTIC_CELL_CD (channel)      │  │  │                                          │  │
│  │                                  │  │  │  • Dynamic year filtering                │  │
│  │  Minor hardcoding:               │  │  │    (based on active dates)               │  │
│  │  • YEARS_TO_INCLUDE = [2025,2026]│  │  │                                          │  │
│  │  • TEST_GROUP_CODE = "TG4"       │  │  │                                          │  │
│  └──────────────────────────────────┘  │  └──────────────────────────────────────────┘  │
│                                        │                                                 │
└────────────────────────────────────────┴────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│  LAYER 4: Client Journey - ALREADY FROM DATA                                             │
│                                                                                          │
├────────────────────────────────────────┬────────────────────────────────────────────────┤
│                                        │                                                 │
│  TODAY                                 │  FUTURE (unified layer)                         │
│                                        │                                                 │
│  ┌──────────────────────────────────┐  │  ┌──────────────────────────────────────────┐  │
│  │  Multiple separate sources:      │  │  │  Unified Client Journey semantic layer:  │  │
│  │                                  │  │  │                                          │  │
│  │  • VISA_DR_CRD (card issuance)   │  │  │  • All touchpoints in one place          │  │
│  │  • POS_TXN (transactions)        │  │  │  • Standardized schema                   │  │
│  │  • VENDOR_FEEDBACK (email)       │  │  │  • Pre-joined client journey             │  │
│  │  • CLNT_CRD_POS_LOG (token)      │  │  │                                          │  │
│  │                                  │  │  │  query_client_journey(                   │  │
│  │  Direct HIVE + EDW queries       │  │  │      clients, start_date, end_date)      │  │
│  │                                  │  │  │                                          │  │
│  └──────────────────────────────────┘  │  └──────────────────────────────────────────┘  │
│                                        │                                                 │
└────────────────────────────────────────┴────────────────────────────────────────────────┘
```

## Summary: All Swap Points

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                             SWAP POINTS SUMMARY                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  LAYER    │ WHAT'S HARDCODED           │ SWAPS TO                    │ TRIGGER          │
│  ─────────┼────────────────────────────┼─────────────────────────────┼─────────────────  │
│           │                            │                             │                   │
│  Layer 1  │ YEARS_TO_INCLUDE           │ Query from Experiment       │ Experiment        │
│           │ TEST_GROUP_CODE            │ Metadata table              │ Metadata table    │
│           │ (3 items)                  │                             │ built             │
│           │                            │                             │                   │
│  Layer 2  │ CAMPAIGN_METADATA dict     │ Query Mnemonic Mapping v2   │ MM v2 has         │
│           │ (6 campaigns × 3 fields)   │                             │ metric fields     │
│           │ (18 items)                 │                             │                   │
│           │                            │                             │                   │
│  Layer 3  │ SUCCESS_DEFINITIONS dict   │ GitHub Success Library      │ Success Library   │
│           │ (4 metrics × 6 fields)     │ OR Curated semantic layer   │ repo/layer        │
│           │ (24 items)                 │                             │ exists            │
│           │                            │                             │                   │
│  Layer 4  │ Separate source paths      │ Unified Client Journey      │ Client Journey    │
│           │ (5 paths + 3 EDW queries)  │ semantic layer              │ layer built       │
│           │ (8 items)                  │                             │                   │
│           │                            │                             │                   │
│  ─────────┴────────────────────────────┴─────────────────────────────┴─────────────────  │
│                                                                                          │
│  TOTAL: 53 hardcoded items → Dynamic queries when infrastructure ready                   │
│                                                                                          │
│  ENGINE CORE: Does NOT change. Only cares about CLNT_NO, GROUP, COHORT, SUCCESS_FLAG    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## RBC Brand Colors

| Element | Color Name | Hex Code | Usage |
|---------|------------|----------|-------|
| Headers / Titles | Dark Blue | #003168 | All titles and headers |
| Primary boxes | Bright Blue | #0051A5 | Engine, main components |
| FROM DATA (working) | Ocean | #0091DA | Layer 1, Layer 4 boxes |
| HARDCODED (swap points) | Warm Yellow | #FFC72C | Layer 2, Layer 3 boxes |
| FUTURE state | Tundra | #07AFBF | Future replacement boxes |
| Arrows / Flow lines | Bright Blue Tint | #006AC3 | All connecting arrows |
| Backgrounds | Cool White | #E7EEF1 | Page backgrounds |
| Key callouts | Sunburst | #FCA311 | Important messages |
| Secondary / Pending | Gray | #9EA2A2 | Track A (pending) |

---

## Key Messages to Convey

1. **Vintage Automation is SuperFact in action** - not a parallel effort
2. **Virtuous Cycle is the core value** - we're BUILDING the Success Library as we measure
3. **Success Library grows with each campaign** - reuse metrics, only define new when needed
4. **Swap points are SPECIFIC** - we know exactly what's hardcoded and what it becomes
5. **Engine core is stable** - swap data sources without rewriting calculation logic
6. **6 pilot campaigns prove it works** - VCN, VDA, VDT, VUI, VUT, VAW

---

---

# PAGE 4: Next Steps

**Title:** Vintage Automation - Next Steps

**Key Message:** Engine is built. Now we need to decide: how do we refresh, what else do we measure, and where does it live?

## Layout

Three columns for the main strategic areas, plus Decisions section below.

## Content

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              VINTAGE AUTOMATION - NEXT STEPS                             │
│                           Strategic roadmap and decisions to be made                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐│
│  │ 1. Adding New Cohorts    │  │ 2. Expand Metrics &      │  │ 3. Hosting & Technology  ││
│  │                          │  │    Comparisons           │  │                          ││
│  │ For existing campaigns   │  │ What else can we vintage?│  │ Where does this live?    ││
│  ├──────────────────────────┤  ├──────────────────────────┤  ├──────────────────────────┤│
│  │                          │  │                          │  │                          ││
│  │ TRACK A (Official):      │  │ SUCCESS METRICS:         │  │ Option A: SharePoint     ││
│  │ • Define refresh cadence │  │ • Primary success        │  │ • Static HTML files      ││
│  │   with CIDM              │  │ • Secondary success (TBD)│  │ • Manual refresh         ││
│  │ • Automated pipeline     │  │ • Tertiary success (TBD) │  │ • Quick to deploy        ││
│  │ • New cohorts appear     │  │                          │  │                          ││
│  │   automatically          │  │ ENGAGEMENT METRICS:      │  │ Option B: Tableau/CIDM   ││
│  │                          │  │ • Email open rate curves │  │ • Governed, official     ││
│  │ TRACK B (In-House):      │  │ • Click rate curves      │  │ • Automated refresh      ││
│  │ • Re-run engine          │  │ • Unsubscribe curves     │  │ • Broader access         ││
│  │ • Regenerate HTML        │  │                          │  │                          ││
│  │ • Deploy to SharePoint   │  │ SEGMENT BREAKDOWNS:      │  │ Option C: Snowflake/New  ││
│  │                          │  │ • By channel             │  │ • Modern data platform   ││
│  │                          │  │ • By segment             │  │ • Scalable, integrated   ││
│  │                          │  │ • Other comparisons      │  │ • Requires decision      ││
│  │                          │  │                          │  │                          ││
│  │                          │  │ [TO BE FIGURED OUT]      │  │ [DECISION PENDING]       ││
│  └──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘│
│                                                                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                    DECISIONS TO MAKE                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────┐ │
│  │ Cohort Refresh    │  │ Metric            │  │ Technology        │  │ Track A vs B  │ │
│  │ Process           │  │ Prioritization    │  │ Platform          │  │ Priority      │ │
│  ├───────────────────┤  ├───────────────────┤  ├───────────────────┤  ├───────────────┤ │
│  │                   │  │                   │  │                   │  │               │ │
│  │ • How often?      │  │ • What secondary  │  │ • SharePoint good │  │ • Both tracks │ │
│  │ • Who triggers?   │  │   metrics matter? │  │   enough?         │  │   parallel?   │ │
│  │ • Automated vs    │  │ • Which engage-   │  │ • Move to         │  │ • When does A │ │
│  │   manual?         │  │   ment metrics?   │  │   Snowflake?      │  │   take over?  │ │
│  │ • How to notify   │  │ • What segment    │  │ • What's the org  │  │ • Does B      │ │
│  │   stakeholders?   │  │   breakdowns?     │  │   direction?      │  │   sunset?     │ │
│  │                   │  │ • Director input  │  │                   │  │               │ │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘  └───────────────┘ │
│                                                                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                    CURRENT STATUS                                        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ✓ DONE                  ◐ IN PROGRESS              ○ TO DO                              │
│  • Engine built          • Track B dashboard        • Track A alignment                  │
│  • 6 pilot campaigns     • Success Library (4)      • Hosting decision                   │
│  • Channel detection     • Swap points documented   • Metric expansion                   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Key Callout Box

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│  Engine is built. Now we need to decide:                                                 │
│  • How do we refresh? (cohort cadence)                                                   │
│  • What else do we measure? (metrics expansion)                                          │
│  • Where does it live? (hosting technology)                                              │
│                                                                                          │
│  These decisions shape the next phase of Vintage Automation.                             │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Files to Create

1. `VINTAGE_ARCHITECTURE_DIAGRAMS.drawio` - Multi-page Draw.io file
   - Page 1: Big Picture (overview)
   - Page 2: Virtuous Cycle (Success Library growth)
   - Page 3: Swap Points (detailed what-to-what)
   - Page 4: Next Steps (roadmap)
