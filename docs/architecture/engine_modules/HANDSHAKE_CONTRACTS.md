# Handshake Contracts: Inter-Module Data Specifications

> **Created:** 2026-01-28
> **Status:** Design — under review
> **Purpose:** Define the exact data schema passed between modules
> **Companion docs:** `MODULE_CATALOG.md`, `EXECUTION_FLOW.md`
> **Enforcement:** All contracts are validated at runtime (not documentation-only)

---

## Contract Principles

1. **Every module boundary has a contract.** No data passes between modules without a defined schema.
2. **Contracts are enforced at runtime.** A validation function checks required fields exist before the next module consumes the data. Missing fields fail the pipeline with a clear message.
3. **Required fields are strict. Optional fields are pass-through.** Core fields must exist. Additional fields (enrichment, debugging) pass through without breaking the contract.
4. **DataFrames are the interchange format.** PySpark DataFrames for large data, Python dicts for configuration. Pandas DataFrames for final output.

---

## Contract Map

```
M1 ──[C1]──→ M2 ──[C2]──→ M3 ──[C3]──┐
 │                                      │
 └──[C4]──→ M5 ──[C5]────────────────┤
                                       ▼
                                 M6 ←[C6]
                                  │
                                  └──[C7]──→ M7
```

| Contract | From | To | Data Type | Description |
|----------|------|----|-----------|-------------|
| **C1** | M1 | M2 | MNE list + metadata | Campaign mnemonics and date context |
| **C2** | M2 | M3 | Config dict | Metric names and campaign semantics |
| **C3** | M3 | M6 | PySpark DataFrame + config | Success outcome data |
| **C4** | M1 | M5 | PySpark DataFrame | Tactic IDs and treatment dates |
| **C5** | M5 | M6 | PySpark DataFrame | Engagement flags and dates |
| **C6** | M1+M3+M5 | M6 | Combined inputs | All context for curve building |
| **C7** | M6 | M7 | Pandas DataFrames | Vintage curves and channel breakdown |

---

## C1: M1 (Experiment) → M2 (Campaign)

**What passes:** The list of campaign mnemonics found in the experiment data, plus the experiment DataFrame itself.

**Direction:** M1 produces the client list. M2 is called per-MNE to get the campaign configuration.

### M1 Output: Experiment DataFrame

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| CLNT_NO | String | YES | Client identifier (leading zeros stripped) |
| TACTIC_ID | String | YES | Unique tactic identifier |
| TREATMT_STRT_DT | Date | YES | Treatment start date |
| TREATMT_END_DT | Date | YES | Treatment end date |
| TST_GRP_CD | String | YES | Test group code (raw, e.g., TG4) |
| RPT_GRP_CD | String | YES | Report group code (cell-level detail) |
| TREATMT_MN | String | YES | Treatment month |
| TACTIC_CELL_CD | String | YES | Channel code (e.g., EM = email) |
| STRTGY_SRC_CD | String | Optional | Strategy source code |
| ADDNL_DECISN_DATA1 | String | Optional | Additional decision data field 1 |
| ADDNL_DECISN_DATA2 | String | Optional | Additional decision data field 2 |
| ADDNL_DECISN_DATA3 | String | Optional | Additional decision data field 3 |
| MNE | String | YES | Campaign mnemonic (extracted from TACTIC_ID) |
| WINDOW_DAYS | Integer | YES | Days between treatment start and end |
| COHORT | String | YES | Year-month of treatment start (yyyy-MM) |

### M1 Output: MNE List

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mne_list | List[String] | YES | Distinct MNEs found in experiment data |

### Validation Rule (C1)

```
ASSERT: DataFrame is not empty
ASSERT: CLNT_NO column exists and has no nulls
ASSERT: TREATMT_STRT_DT column exists and has no nulls
ASSERT: TST_GRP_CD column exists
ASSERT: RPT_GRP_CD column exists
ASSERT: MNE column exists
ASSERT: WINDOW_DAYS column exists and all values > 0
ASSERT: COHORT column exists
```

---

## C2: M2 (Campaign) → M3 (Success)

**What passes:** A configuration dictionary that tells M3 which success metric to calculate.

**Direction:** M2 is called per-MNE. It returns a config dict. This dict is passed to M3 functions.

### M2 Output: Campaign Config Dict

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| campaign_name | String | YES | Human-readable campaign name |
| success_type | String | YES | Category: ACQUISITION, ACTIVATION, USAGE, TOKENIZATION |
| primary_metric | String | YES | Key into SUCCESS_DEFINITIONS (e.g., "card_acquisition") |
| secondary_metric | String | NO | Key into SUCCESS_DEFINITIONS, or None |

### Validation Rule (C2)

```
ASSERT: campaign_name is not None and not empty
ASSERT: success_type in ("ACQUISITION", "ACTIVATION", "USAGE", "TOKENIZATION")
ASSERT: primary_metric is not None and exists in SUCCESS_DEFINITIONS
ASSERT: if secondary_metric is not None, it exists in SUCCESS_DEFINITIONS
```

---

## C3: M3 (Success) → M6 (Engine)

**What passes:** Two things — a success outcome DataFrame and a flat config dict.

**Direction:** M3 loads and filters the success data. It passes the filtered DataFrame and the merged config to M6.

### M3 Output: Success Outcome DataFrame

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| CLNT_NO | String | YES | Client identifier (must match M1's CLNT_NO format) |
| SUCCESS_DT | Date | YES | Date of success event |

> **Output contract enforcement:** Every success metric, regardless of source (Hive or EDW), must produce exactly these two columns. This is validated at runtime at the exit of `load_success_outcome()`.

**Additional columns may exist** (e.g., card type, transaction amount) but are not part of the contract. M6 ignores them.

### M3 Output: Flat Config Dict

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| campaign_name | String | YES | From M2 |
| success_type | String | YES | From M2 |
| metric_name | String | YES | Key used to look up the definition |
| metric_type | String | YES | "PRIMARY" or "SECONDARY" |
| success_source | String | YES | "HIVE", "EDW", or "DUAL" |
| success_date_field | String | YES | Original date field name before aliasing to SUCCESS_DT |
| success_table_path | String | HIVE only | Parquet path for Hive-sourced metrics |
| filters | Dict | HIVE only | Filter configuration |
| edw_config | Dict | EDW only | EDW query configuration |
| add_card_type | Boolean | YES | Whether to include card type enrichment |

### Validation Rule (C3)

```
ASSERT: DataFrame has column "CLNT_NO"
ASSERT: DataFrame has column "SUCCESS_DT"
ASSERT: CLNT_NO has no nulls
ASSERT: SUCCESS_DT type is Date or Timestamp
ASSERT: config["metric_name"] is not None
ASSERT: config["success_source"] in ("HIVE", "EDW", "DUAL")
```

---

## C4: M1 (Experiment) → M5 (Journey)

**What passes:** Tactic IDs and the experiment DataFrame (for clients targeted with specific channels).

**Direction:** M1's experiment data is filtered for email-channel clients. Tactic IDs are extracted and passed to M5.

### M1 → M5 Output

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| tactic_ids | List[String] | YES | Distinct TACTIC_IDs for email-channel clients |
| email_channel_df | PySpark DataFrame | YES | Subset of M1 output filtered to email-channel clients |

The `email_channel_df` has the same schema as the full M1 output (C1), but filtered to rows where `TACTIC_CELL_CD` contains "EM".

### Validation Rule (C4)

```
ASSERT: tactic_ids is a non-empty list
ASSERT: email_channel_df has column "CLNT_NO"
ASSERT: email_channel_df has column "TREATMT_STRT_DT"
ASSERT: email_channel_df has column "TACTIC_ID"
```

---

## C5: M5 (Journey) → M6 (Engine)

**What passes:** Engagement DataFrame with flags and dates for each engagement event.

**Direction:** M5 loads engagement data from EDW. It returns a DataFrame that M6 joins to the success data.

### M5 Output: Engagement DataFrame

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| CLNT_NO | String | YES | Client identifier (must match M1's CLNT_NO format) |
| TREATMENT_ID | String | Optional | Tactic/treatment identifier |
| CHANNEL | String | Optional | Channel name (e.g., "EMAIL") |
| EMAIL_SENT | Integer (0/1) | YES | Was email sent to this client? |
| EMAIL_OPENED | Integer (0/1) | YES | Did client open the email? |
| EMAIL_CLICKED | Integer (0/1) | YES | Did client click in the email? |
| EMAIL_UNSUBSCRIBED | Integer (0/1) | YES | Did client unsubscribe? |
| EMAIL_SENT_DT | Date | Optional | Date email was sent |
| EMAIL_OPENED_DT | Date | Optional | Date email was opened |
| EMAIL_CLICKED_DT | Date | Optional | Date email was clicked |
| EMAIL_UNSUBSCRIBED_DT | Date | Optional | Date client unsubscribed |

> **Future expansion:** When mobile engagement is added, M5 will also produce MOBILE_SENT, MOBILE_OPENED, etc. The contract extends — it does not break.

### Validation Rule (C5)

```
ASSERT: DataFrame has column "CLNT_NO"
ASSERT: EMAIL_SENT column exists and contains only 0 or 1
ASSERT: EMAIL_OPENED column exists and contains only 0 or 1
ASSERT: EMAIL_CLICKED column exists and contains only 0 or 1
ASSERT: EMAIL_UNSUBSCRIBED column exists and contains only 0 or 1
```

If engagement data is unavailable (EDW error, no email channel), M5 returns `None`. M6 handles this gracefully — engagement enrichment is skipped.

---

## C6: Context Layer → M6 (Engine) — Combined Input

**What passes:** M6 receives separate inputs from three modules and joins them internally.

**This is NOT a single merged handshake.** M6 receives:

| Input | From | Joined On | Purpose |
|-------|------|-----------|---------|
| tactic_df | M1 | — (base) | Experiment clients and treatment windows |
| success_df | M3 | CLNT_NO + date range | Who succeeded and when |
| config | M3 | — (metadata) | How to interpret the success data |
| engagement_df | M5 | CLNT_NO | Engagement flags per client |

### Join Logic (inside M6)

```
Step 1: detect_success()
    tactic_df LEFT JOIN success_df
    ON tactic.CLNT_NO = success.CLNT_NO
    AND success.SUCCESS_DT BETWEEN tactic.TREATMT_STRT_DT AND tactic.TREATMT_END_DT

Step 2: enrich_with_engagement()
    result LEFT JOIN engagement_df
    ON result.CLNT_NO = engagement.CLNT_NO
```

**Why LEFT JOIN:** Every experiment client appears in the output, whether they succeeded or not. Success and engagement are "did it happen?" flags, not filters.

---

## C7: M6 (Engine) → M7 (Output)

**What passes:** A results dictionary containing Pandas DataFrames.

### M6 Output: Results Dict

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| vintage_curves | Pandas DataFrame | YES | Cumulative success curves |
| channel_breakdown | Pandas DataFrame | YES | Summary by channel |

### vintage_curves Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| MNE | String | YES | Campaign mnemonic |
| COHORT | String | YES | Year-month cohort |
| TST_GRP_CD | String | YES | Test group code |
| RPT_GRP_CD | String | YES | Report group code |
| METRIC | String | YES | PRIMARY, SECONDARY, EMAIL_SENT, EMAIL_OPEN, EMAIL_CLICK, EMAIL_UNSUB |
| DAY | Integer | YES | Days since treatment start (0, 1, 2, ...) |
| WINDOW_DAYS | Integer | YES | Maximum measurement window |
| CLIENT_CNT | Integer | YES | Clients in this cell |
| SUCCESS_CNT | Integer | YES | Cumulative successes by this day |
| RATE | Float | YES | SUCCESS_CNT / CLIENT_CNT * 100 |

### channel_breakdown Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| MNE | String | YES | Campaign mnemonic |
| COHORT | String | YES | Year-month cohort |
| TST_GRP_CD | String | YES | Test group code |
| RPT_GRP_CD | String | YES | Report group code |
| CHANNEL | String | YES | Channel code |
| CLIENT_CNT | Integer | YES | Clients in this channel |
| SUCCESS_CNT | Integer | YES | Successes in this channel |
| RATE | Float | YES | Success rate percentage |

### Validation Rule (C7)

```
ASSERT: vintage_curves is a non-empty Pandas DataFrame
ASSERT: vintage_curves contains all required columns
ASSERT: RATE values are between 0 and 100
ASSERT: CLIENT_CNT > 0 for all rows
ASSERT: SUCCESS_CNT >= 0 for all rows
ASSERT: SUCCESS_CNT <= CLIENT_CNT for all rows
ASSERT: DAY >= 0 for all rows
```

---

## CLNT_NO Format Agreement

**Critical cross-module contract:** CLNT_NO must be in the same format across all modules.

| Module | How CLNT_NO is produced | Format |
|--------|------------------------|--------|
| M1 | `REGEXP_REPLACE(TRIM(TACTIC_EVNT_ID), "^0+", "")` | String, no leading zeros |
| M3 (Hive) | Direct from source column, or `REGEXP_REPLACE(SUBSTR(CLNT_CRD_NO, 7, 9), "^0+", "")` | String, no leading zeros |
| M3 (EDW) | `CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER)` then converted to String | String, no leading zeros (via integer cast) |
| M5 | `CAST(CLNT_NO AS VARCHAR(20))` then `.str.strip().str.lstrip('0')` | String, no leading zeros |

> **All modules strip leading zeros.** Joins on CLNT_NO depend on this. If any module produces CLNT_NO with leading zeros, the join will silently drop matches. This is the most common source of data loss in the pipeline.

---

## Validation Implementation

Each contract should be implemented as a Python function:

```python
def validate_contract(name, df=None, config=None, rules=None):
    """
    Validate a handshake contract at a module boundary.

    Args:
        name: Contract identifier (e.g., "C1", "C3").
        df: DataFrame to validate (if applicable).
        config: Config dict to validate (if applicable).
        rules: List of (condition, error_message) tuples.

    Raises:
        ContractViolation with clear module and field identification.
    """
```

**Placement:** Validation runs at the EXIT of each module, before passing data to the next module. The producing module is responsible for meeting the contract.

**Failure behavior:** Pipeline stops with a clear error: `"Contract C3 violation: SUCCESS_DT column missing from M3 output for metric 'card_acquisition'"`. No silent failures. No fallbacks.

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-28 | Created from architecture redesign session |
