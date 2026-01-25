# MNE Mapping Table Metadata

## Overview

This document captures the schema metadata for the `mne_mapping_table_lan` table, the current Mnemonic Mapping table (V1) referenced in the Success Library / SuperFact architecture. This table is central to Layer 2: Managed Campaign Metadata.

**Location:** `dw00_im.ddwutd03.mne_mapping_table_lan`

---

## Table: mne_mapping_table_lan

### Field Definitions

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| mnemonic | char(11) | Campaign mnemonic identifier (primary key) |
| mnemonic_description | char(200) | Full description of the campaign/mnemonic |
| category_cd | integer | Category code |
| category_name | char(65) | Category name |
| sub_category_cd | integer | Sub-category code |
| sub_category_name | char(75) | Sub-category name |
| communication_type | char(20) | Type of communication |
| rev_type | char(7) | Revenue type |
| lob_nba | char(65) | Line of Business for NBA |
| lob_group | char(40) | LOB group classification |
| lob_sub_group | char(40) | LOB sub-group classification |
| corp_ind | char(1) | Corporate indicator (Y/N) |
| welcome_ind | char(1) | Welcome campaign indicator (Y/N) |
| fulfillment_insight_survey_ind | char(7) | Fulfillment/insight/survey indicator |
| regulatory_compliance_ind | char(7) | Regulatory compliance indicator |
| operational_ind | char(7) | Operational indicator |
| low_volume_ind | char(7) | Low volume indicator |
| control_exemption | char(7) | Control group exemption flag |
| pilot_ind | char(7) | Pilot indicator |
| targeting_type | char(8) | Targeting type classification |
| initiative_type | char(7) | Initiative type |
| test_and_learn_owner | char(20) | Test & Learn owner/team |
| msr_status | char(35) | Measurement status |

---

## Current State Assessment

### Fields Currently Available (per Success Library deck)

These fields align with the "Currently Available" section in the Mnemonic Mapping V2 proposal:

| Current Field | Maps To |
|---------------|---------|
| mnemonic_description | Campaign Description |
| lob_nba, lob_group, lob_sub_group | LOB (Line of Business) |
| category_cd, category_name, sub_category_cd | Campaign Category |
| control_exemption | Control Exemption |
| msr_status | Measurement Category |

### Fields Missing for V2 Enhancement

The following fields are **not present** in the current schema and are proposed for V2:

| Proposed V2 Field | Purpose |
|-------------------|---------|
| primary_metric | Main success measure for the campaign |
| secondary_metric | Supporting success measure |
| tertiary_metric | Additional success measure |
| action_type | Type of marketing action |
| sub_action_type | Sub-type of marketing action |
| client_mindset | Where client sits in the journey / continuum |
| cta | Call to action |
| frequency | Campaign frequency |
| model | Targeting/propensity model used |

---

## Integration Points

### Relationship to Other Layers

```
Layer 1: Experiment Metadata (ODS / Tactic History)
         ↓
Layer 2: Campaign Metadata (THIS TABLE) ← Links success metrics
         ↓
Layer 3: Success Library (GitHub Logic Repo)
         ↓
Layer 4: Client Marketing Interaction Journey
```

### Key Join Fields

| This Table | Joins To | On Field |
|------------|----------|----------|
| mne_mapping_table_lan | ods_mr_hist | tactic_id → mnemonic (partial match) |
| mne_mapping_table_lan | TACTIC_IP_AR_HIST | TACTIC → mnemonic |
| mne_mapping_table_lan | Success Library | primary_metric → Success Code (future) |

---

## Data Governance Notes

### Current Gaps

1. **No metrics linkage** - Table lacks fields to tie campaigns to standardized success metrics
2. **Measurement status only** - `msr_status` indicates measurability but not what to measure
3. **No versioning** - No audit trail or version control fields visible
4. **Indicator proliferation** - Multiple char(7) indicator fields suggest inconsistent boolean handling

### Recommendations for V2

1. Add `primary_metric`, `secondary_metric`, `tertiary_metric` as foreign keys to Success Library
2. Standardize indicator fields to char(1) Y/N or boolean
3. Add `last_updated_dt` and `updated_by` for audit trail
4. Consider adding `metric_owner` for accountability

---

## Related Tables

| Table Name | Schema | Purpose |
|------------|--------|---------|
| DTZTAU.CIDM_MNEMONIC_ATTRS | Teradata | Alternative/related mnemonic attributes table |
| ods_mr_hist | ed10_im.prod_x610_crm | ODS marketing response history |
| TACTIC_IP_AR_HIST | DGNV01 | Tactic history for population identification |

---

## References

- Source: `dw00_im.ddwutd03.mne_mapping_table_lan`
- Context: Success Library - SuperFact Concept v2, Slide 9
- Related: Mnemonic Mapping V2 Enhancement Proposal

---

*Document created: January 2026*
*Source: Cluster Explorer schema screenshot*
