# Coding Spec: vintage_engine v2.6

> **Purpose:** Implementation instructions for a coding agent.
> **Input:** This file + `src/vintage_engine.py` (v2.5)
> **Output:** `src/vintage_engine_v2.6.py` (new file — do NOT overwrite v2.5)
> **Design reference:** `docs/architecture/MODULE_DESIGN_DECISIONS.md`

---

## Overview

Refactor Layer 2 (Campaign Metadata) and Layer 3 (Success Definitions) to be truly modular. The engine core does NOT change. The output must be identical to v2.5.

**What "modular" means:** You can remove the Layer 3 block from the file and replace it with a different implementation (e.g., one that queries an external source), and the engine keeps working — as long as the output contract is met.

---

## CHANGE 1: Restructure SUCCESS_DEFINITIONS

**Replace lines 148-210** (the entire Layer 3 section) with the new schema below.

Every metric now has: identity, source routing, output contract, and environment-specific config.

```python
# =============================================================================
# LAYER 3: SUCCESS DEFINITIONS
# =============================================================================
# Each metric is a COMPLETE DATA ASSET: identity + source routing + execution
# config + output contract. Everything needed to calculate success lives here.
#
# Output contract: Every metric, regardless of source, must produce a DataFrame
# with at minimum: CLNT_NO (client identifier) and a success date field.
#
# Source routing: "HIVE" = Spark parquet read + PySpark filters
#                 "EDW"  = Teradata cursor + SQL query
#                 "DUAL" = both available, engine picks based on preference
# =============================================================================

SUCCESS_DEFINITIONS = {

    "card_acquisition": {
        # ── Identity ──────────────────────────────────────────
        "metric_id": "card_acquisition",
        "description": "Client acquired a new VVD card (issued in active/approved status)",
        "version": "1.0",
        "owner": "marketing_analytics",

        # ── Source Routing ────────────────────────────────────
        "source": "HIVE",

        # ── Output Contract ───────────────────────────────────
        "output_contract": {
            "client_key": "CLNT_NO",
            "date_key": "SUCCESS_DT",
        },

        # ── Hive Config ──────────────────────────────────────
        "hive": {
            "table_path": HIVE_PATHS["visa_debit_card"],
            "date_field": "ISS_DT",
            "client_field": "CLNT_NO",
            "filters": {
                "STS_CD": ["06", "08"],
                "SRVC_ID": 36,
                "ISS_DT_NOT_NULL": True,
            },
            "add_card_type": True,
        },

        # ── EDW Config ───────────────────────────────────────
        "edw": None,

        # ── Business Rules (human-readable) ───────────────────
        "business_rules": [
            "Card status code 06 (Active) or 08 (Approved)",
            "Service ID 36 (Visa Direct)",
            "Issue date must not be null (card was actually issued)",
        ],
    },

    "card_activation": {
        # ── Identity ──────────────────────────────────────────
        "metric_id": "card_activation",
        "description": "Client activated their VVD card",
        "version": "1.0",
        "owner": "marketing_analytics",

        # ── Source Routing ────────────────────────────────────
        "source": "HIVE",

        # ── Output Contract ───────────────────────────────────
        "output_contract": {
            "client_key": "CLNT_NO",
            "date_key": "SUCCESS_DT",
        },

        # ── Hive Config ──────────────────────────────────────
        "hive": {
            "table_path": HIVE_PATHS["visa_debit_card"],
            "date_field": "ACTV_DT",
            "client_field": "CLNT_NO",
            "filters": {
                "STS_CD": ["06", "08"],
                "SRVC_ID": 36,
                "ISS_DT_NOT_NULL": True,
            },
            "add_card_type": True,
        },

        # ── EDW Config ───────────────────────────────────────
        "edw": None,

        # ── Business Rules (human-readable) ───────────────────
        "business_rules": [
            "Card status code 06 (Active) or 08 (Approved)",
            "Service ID 36 (Visa Direct)",
            "Issue date must not be null",
            "Activation date (ACTV_DT) is the success event date",
        ],
    },

    "card_usage": {
        # ── Identity ──────────────────────────────────────────
        "metric_id": "card_usage",
        "description": "Client used their VVD card for a point-of-sale transaction",
        "version": "1.0",
        "owner": "marketing_analytics",

        # ── Source Routing ────────────────────────────────────
        "source": "HIVE",

        # ── Output Contract ───────────────────────────────────
        "output_contract": {
            "client_key": "CLNT_NO",
            "date_key": "SUCCESS_DT",
        },

        # ── Hive Config ──────────────────────────────────────
        "hive": {
            "table_path": HIVE_PATHS["pos_transactions"],
            "date_field": "TXN_DT",
            "client_field": "CLNT_NO",
            "filters": {
                "SRVC_CD": 36,
                "TXN_TYPES": [
                    {"TXN_TP": 10, "MSG_TP": "0210"},
                    {"TXN_TP": 13, "MSG_TP": "0210"},
                    {"TXN_TP": 12, "MSG_TP": "0220"},
                ],
                "AMT1_GT": 0,
                "EXTRACT_CLNT_NO": True,
            },
            "add_card_type": False,
        },

        # ── EDW Config ───────────────────────────────────────
        "edw": None,

        # ── Business Rules (human-readable) ───────────────────
        "business_rules": [
            "Service code 36 (Visa Direct)",
            "Transaction types: purchase (10/0210), refund (13/0210), cash-back (12/0220)",
            "Amount must be greater than 0",
            "Client number extracted from card number: SUBSTR(CLNT_CRD_NO, 7, 9)",
        ],
    },

    "wallet_provisioning": {
        # ── Identity ──────────────────────────────────────────
        "metric_id": "wallet_provisioning",
        "description": "Client provisioned their VVD card to a digital wallet",
        "version": "1.0",
        "owner": "marketing_analytics",

        # ── Source Routing ────────────────────────────────────
        "source": "EDW",

        # ── Output Contract ───────────────────────────────────
        "output_contract": {
            "client_key": "CLNT_NO",
            "date_key": "SUCCESS_DT",
        },

        # ── Hive Config ──────────────────────────────────────
        "hive": None,

        # ── EDW Config ───────────────────────────────────────
        "edw": {
            "tables": [
                {"alias": "B", "schema": "DDWV05", "table": "CLNT_CRD_POS_LOG", "role": "primary"},
                {"alias": "C", "schema": "DL_DECMAN", "table": "TOKEN_LIST", "role": "join"},
            ],
            "query": """
                SELECT DISTINCT
                    CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER) AS CLNT_NO,
                    B.TXN_DT AS SUCCESS_DT
                FROM {pos_log} AS B
                INNER JOIN {token_list} C
                    ON B.TOKN_REQSTR_ID = C.TOKEN_ID
                WHERE B.AMT1 = 0
                    AND SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190'
                    AND SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'
                    AND SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0'
                    AND B.POS_ENTR_MODE_CD_NON_EMV = '000'
                    AND B.SRVC_CD = 36
                    AND C.TOKEN_WALLET_IND = 'Y'
            """,
            "query_params": {
                "pos_log": "DDWV05.CLNT_CRD_POS_LOG",
                "token_list": "DL_DECMAN.TOKEN_LIST",
            },
            "client_key_logic": "CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER)",
            "date_field_source": "B.TXN_DT",
        },

        # ── Business Rules (human-readable) ───────────────────
        "business_rules": [
            "Zero-amount transactions only (AMT1 = 0)",
            "Card BIN prefix 45190 on CLNT_CRD_NO",
            "Visa debit BIN prefix 45199 on VISA_DR_CRD_NO",
            "Valid token requestor (first character > '0')",
            "Non-EMV POS entry mode (000)",
            "Service code 36 (Visa Direct)",
            "Token wallet indicator = Y (from TOKEN_LIST join)",
            "Client number extracted: SUBSTR(CLNT_CRD_NO, 7, 9) cast to INTEGER",
        ],
    },
}
```

---

## CHANGE 2: Create `apply_success_filters()`

**Insert this new function immediately after SUCCESS_DEFINITIONS** (after the closing `}` of the dict, before the HELPER FUNCTIONS section).

This function extracts the filter interpretation logic that currently lives in `load_success_outcome()` (lines 433-452 of v2.5). It is a direct extraction — same logic, same behavior.

```python
def apply_success_filters(spark_df, metric_name):
    """
    Layer 3: Apply success definition filters to a raw DataFrame.

    This function owns the filter interpretation logic for Hive-sourced
    success metrics. It translates the declarative filter config in
    SUCCESS_DEFINITIONS[metric]["hive"]["filters"] into PySpark filter
    operations.

    EDW-sourced metrics do NOT use this function — their filtering is
    embedded in the SQL query within the "edw" config block.

    Args:
        spark_df: Raw PySpark DataFrame from Hive/parquet read.
        metric_name: Key into SUCCESS_DEFINITIONS (e.g., "card_acquisition").

    Returns:
        Filtered PySpark DataFrame.
    """
    definition = SUCCESS_DEFINITIONS[metric_name]
    hive_config = definition.get("hive")

    if hive_config is None:
        return spark_df

    filters = hive_config.get("filters")
    if not filters:
        return spark_df

    df = spark_df

    if "STS_CD" in filters:
        df = df.filter(F.col("STS_CD").isin(filters["STS_CD"]))
    if "SRVC_ID" in filters:
        df = df.filter(F.col("SRVC_ID") == filters["SRVC_ID"])
    if "SRVC_CD" in filters:
        df = df.filter(F.col("SRVC_CD") == filters["SRVC_CD"])
    if "TXN_TYPES" in filters:
        txn_cond = None
        for t in filters["TXN_TYPES"]:
            c = (F.col("TXN_TP") == t["TXN_TP"]) & (F.col("MSG_TP") == t["MSG_TP"])
            txn_cond = c if txn_cond is None else txn_cond | c
        df = df.filter(txn_cond)
    if filters.get("ISS_DT_NOT_NULL"):
        df = df.filter(F.col("ISS_DT").isNotNull())
    if "AMT1_GT" in filters:
        df = df.filter(F.col("AMT1") > filters["AMT1_GT"])
    if filters.get("EXTRACT_CLNT_NO"):
        df = df.withColumn(
            "CLNT_NO",
            F.regexp_replace(F.substring(F.col("CLNT_CRD_NO"), 7, 9), "^0+", "")
        )

    # Governance: warn on unrecognized filter keys
    recognized_keys = {
        "STS_CD", "SRVC_ID", "SRVC_CD", "TXN_TYPES",
        "ISS_DT_NOT_NULL", "AMT1_GT", "EXTRACT_CLNT_NO",
    }
    unrecognized = set(filters.keys()) - recognized_keys
    if unrecognized:
        print(f"    [Layer 3] WARNING: Unrecognized filter keys for '{metric_name}': {unrecognized}")

    return df
```

---

## CHANGE 3: Update helper functions

**Replace lines 212-254** (the HELPER FUNCTIONS section including `ALL_MNES`, `get_campaign_config`, `get_success_definition`, `get_full_config`) with:

```python
# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

ALL_MNES = list(CAMPAIGN_METADATA.keys())


def get_campaign_config(mne):
    """Layer 2: Get campaign metadata."""
    return CAMPAIGN_METADATA[mne]


def get_success_definition(metric_name):
    """Layer 3: Get success definition (full asset)."""
    return SUCCESS_DEFINITIONS[metric_name]


def get_full_config(mne, metric_type="PRIMARY"):
    """
    Get combined config for a specific metric type.

    Merges Layer 2 (campaign) and Layer 3 (success) into a flat config
    dict consumed by Layer 4 and the engine.

    Returns None if the requested metric_type does not exist for this campaign.
    """
    campaign = get_campaign_config(mne)

    if metric_type == "PRIMARY":
        metric = campaign["primary_metric"]
    elif metric_type == "SECONDARY":
        metric = campaign.get("secondary_metric")
        if metric is None:
            return None
    else:
        return None

    definition = get_success_definition(metric)

    # Build flat config from the new schema
    config = {
        "campaign_name": campaign["campaign_name"],
        "success_type": campaign["success_type"],
        "metric_name": metric,
        "metric_type": metric_type,
        "success_source": definition["source"],
        "add_card_type": False,
    }

    # Source-specific fields
    if definition["source"] in ("HIVE", "DUAL"):
        hive = definition["hive"]
        config["success_table_path"] = hive["table_path"]
        config["success_date_field"] = hive["date_field"]
        config["filters"] = hive["filters"]
        config["add_card_type"] = hive.get("add_card_type", False)
    elif definition["source"] == "EDW":
        edw = definition["edw"]
        config["success_table_path"] = None
        config["success_date_field"] = definition["output_contract"]["date_key"]
        config["filters"] = None
        config["edw_config"] = edw

    return config
```

**Key change:** `get_full_config` now calls `get_campaign_config()` and `get_success_definition()` instead of accessing the dicts directly. It also reads from the new nested schema (`definition["hive"]`, `definition["edw"]`) instead of the flat structure.

---

## CHANGE 4: Update `load_token_from_edw()`

**Replace lines 392-416** with this updated version that reads the SQL from the definition:

```python
def load_token_from_edw(edw_config=None):
    """
    Layer 4: Load token/provisioning data from EDW.

    If edw_config is provided (from SUCCESS_DEFINITIONS), uses the
    cataloged query. Otherwise falls back to hardcoded query for
    backward compatibility.

    The SQL filters in the query must stay in sync with the
    wallet_provisioning entry in SUCCESS_DEFINITIONS.
    See: SUCCESS_DEFINITIONS["wallet_provisioning"]["business_rules"]

    Args:
        edw_config: Optional dict from SUCCESS_DEFINITIONS[metric]["edw"].
                    Contains "query" and "query_params".

    Returns:
        pandas DataFrame with CLNT_NO and SUCCESS_DT columns.
    """
    if edw_config and "query" in edw_config:
        query = edw_config["query"].format(**edw_config["query_params"])
    else:
        # Fallback: hardcoded query (backward compatibility)
        query = f"""
        SELECT DISTINCT
            CAST(SUBSTR(B.CLNT_CRD_NO, 7, 9) AS INTEGER) AS CLNT_NO,
            B.TXN_DT AS SUCCESS_DT
        FROM {EDW_TABLES['pos_log']} AS B
        INNER JOIN {EDW_TABLES['token_list']} C
            ON B.TOKN_REQSTR_ID = C.TOKEN_ID
        WHERE B.AMT1 = 0
            AND SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190'
            AND SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'
            AND SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0'
            AND B.POS_ENTR_MODE_CD_NON_EMV = '000'
            AND B.SRVC_CD = 36
            AND C.TOKEN_WALLET_IND = 'Y'
        """

    cursor = EDW.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()

    return pd.DataFrame(rows, columns=columns)
```

**Key change:** Accepts optional `edw_config` parameter. If provided, uses the cataloged query from the definition. If not, falls back to the hardcoded SQL (backward compatibility during transition).

**IMPORTANT:** The SQL in the definition's `edw.query` now aliases `B.TXN_DT AS SUCCESS_DT` to match the output contract. The hardcoded fallback also adds this alias for consistency.

---

## CHANGE 5: Simplify `load_success_outcome()`

**Replace lines 419-454** with:

```python
def load_success_outcome(spark, config):
    """
    Layer 4: Load success outcome data.

    Routes to the appropriate data source based on config.
    - HIVE: reads parquet, delegates filtering to Layer 3 (apply_success_filters)
    - EDW: delegates to load_token_from_edw with cataloged query

    Args:
        spark: SparkSession.
        config: Dict from get_full_config().

    Returns:
        PySpark DataFrame with success outcome data.
    """
    years_str = [str(y) for y in YEARS_TO_INCLUDE]

    if config["success_source"] == "EDW":
        print(f"    [Layer 4] Loading success outcome from EDW ({config['metric_name']})...")
        edw_config = config.get("edw_config")
        token_pdf = load_token_from_edw(edw_config)
        print(f"    [Layer 4] Retrieved {len(token_pdf):,} records")
        return spark.createDataFrame(token_pdf)

    paths = [f"{config['success_table_path']}{year}*" for year in years_str]
    print(f"    [Layer 4] Loading success outcome from partitions: {years_str}")
    df = spark.read.parquet(*paths)

    # Layer 3 owns filter interpretation
    df = apply_success_filters(df, config["metric_name"])

    return df
```

**What changed:**
- The 15-line filter block (lines 433-452 in v2.5) is replaced by one call: `apply_success_filters(df, config["metric_name"])`
- EDW path now passes `edw_config` to `load_token_from_edw()`
- Layer 4 does ONLY I/O. Layer 3 does filter semantics.

---

## CHANGE 6: Update `detect_success()` for output contract

**In `detect_success()` (around line 466 in v2.5)**, the success date column aliasing needs to handle the new output contract. Currently it uses `config["success_date_field"]` to find the date column.

**The change is small.** In the `success_select` block, where it creates `SUCCESS_DT`:

```python
    # Check if the data already has SUCCESS_DT (EDW path provides it)
    if "SUCCESS_DT" in [f.name for f in success_df.schema.fields]:
        success_date_col = "SUCCESS_DT"
    else:
        success_date_col = config["success_date_field"]

    success_select = success_df.select(
        F.col("CLNT_NO").alias("SUCCESS_CLNT_NO"),
        F.col(success_date_col).alias("SUCCESS_DT")
    ).alias("s")
```

This handles both:
- Hive path: date column is ISS_DT, ACTV_DT, or TXN_DT → aliased to SUCCESS_DT
- EDW path: query already returns SUCCESS_DT (from the `AS SUCCESS_DT` alias in the SQL)

**Replace only the `success_select` line and the line above it.** Do not change anything else in `detect_success()`.

---

## CHANGE 7: Update file header

**Replace lines 1-29** (the docstring and header) to reflect v2.6:

```python
"""
Vintage Engine v2.6
===================

Changes from v2.5:
- RESTRUCTURED: SUCCESS_DEFINITIONS uses new hybrid asset schema
  - Each metric has: identity, source routing, output contract, env config, business rules
  - Hive and EDW configs are separate blocks within each definition
- CREATED: apply_success_filters() — Layer 3 owns its filter interpretation logic
- SIMPLIFIED: load_success_outcome() — Layer 4 does I/O only, delegates filtering to Layer 3
- UPDATED: load_token_from_edw() — reads SQL from cataloged definition
- UPDATED: get_full_config() — uses accessor functions, reads new schema
- UPDATED: detect_success() — handles output contract (SUCCESS_DT alias)
- NO CHANGE: Engine core (build_vintage_curves, build_engagement_curves, etc.)
- NO CHANGE: Output schema — identical to v2.5

Modularity improvement: Layers 2 and 3 are now truly liftable blocks.
The success metric is a complete data asset: identity + execution config +
output contract. Filter logic lives WITH the definitions, not scattered
in Layer 4.

Architecture: SuperFact 4-Layer Framework
- Layer 1: Experiment Metadata (tactic_evnt_hist) - "Who is in test?"
- Layer 2: Campaign Metadata (CAMPAIGN_METADATA) - "What to measure?"
- Layer 3: Success Definitions (SUCCESS_DEFINITIONS) - "How to calculate?"
- Layer 4: Client Journey (fulfillment, engagement, outcome) - "What actually happened?"

Output Schema:
  MNE | COHORT | TST_GRP_CD | RPT_GRP_CD | METRIC | DAY | WINDOW_DAYS | CLIENT_CNT | SUCCESS_CNT | RATE

Copy this entire file into a Jupyter notebook cell and run.
"""
```

---

## CHANGE 8: Update startup message

**At the bottom of the file** (around line 1030 in v2.5), update the version number in the startup print block:

Change `VINTAGE ENGINE v2.4` to `VINTAGE ENGINE v2.6` (note: v2.5 had a typo that said v2.4 in the print block).

Change the CHANGES section to:
```
CHANGES IN v2.6:
  - SUCCESS_DEFINITIONS restructured as complete data assets
  - Filter logic moved to Layer 3 (apply_success_filters)
  - EDW queries read from cataloged definitions
  - Modularity: Layers 2 and 3 are now liftable blocks
```

---

## WHAT DOES NOT CHANGE

Copy these sections from v2.5 EXACTLY as they are — do not modify:

| Section | v2.5 Lines | Description |
|---------|-----------|-------------|
| Imports | 31-37 | All import statements |
| `%matplotlib inline` | 40 | Jupyter magic |
| USER_CONFIG | 46-50 | User settings |
| `get_hdfs_output_path()` | 53-55 | Output path helper |
| OUTPUT_SCHEMA | 62-73 | Output schema definition |
| YEARS_TO_INCLUDE | 79 | Global config |
| HIVE_PATHS | 86-90 | Hive file paths |
| EDW_TABLES | 98-103 | EDW table references |
| CAMPAIGN_METADATA | 109-146 | Layer 2 (unchanged) |
| `load_tactic()` | 261-306 | Layer 1 experiment module |
| `load_channel_engagement()` | 313-329 | Layer 4 engagement router |
| `_load_email_engagement()` | 332-385 | Layer 4 email engagement |
| `enrich_with_engagement()` | 502-544 | Engagement enrichment |
| `build_vintage_curves()` | 551-619 | Engine core |
| `build_engagement_curves()` | 622-705 | Engine core |
| `_build_engagement_metric_curve()` | 708-764 | Engine helper |
| `build_channel_breakdown()` | 767-787 | Engine core |
| `run_vintage_analysis()` | 794-926 | Main runner (call sites unchanged) |
| `run_all_campaigns()` | 929-953 | Multi-campaign runner |
| `_detect_result_structure()` | 960-971 | Export helper |
| `download_csv()` | 974-992 | Export function |
| `download_results()` | 995-1021 | Export function |
| `spark = SparkSession...` | 1028 | Spark initialization |

---

## VALIDATION CHECKLIST

After producing v2.6, verify:

1. [ ] `SUCCESS_DEFINITIONS` has all 4 metrics with new schema
2. [ ] Each metric has: metric_id, description, version, owner, source, output_contract, hive, edw, business_rules
3. [ ] `apply_success_filters()` exists after SUCCESS_DEFINITIONS
4. [ ] `apply_success_filters()` contains identical filter logic to v2.5 lines 433-452
5. [ ] `load_success_outcome()` does NOT contain filter logic — only calls `apply_success_filters()`
6. [ ] `load_token_from_edw()` accepts optional `edw_config` parameter
7. [ ] `load_token_from_edw()` fallback SQL is identical to v2.5 (with SUCCESS_DT alias added)
8. [ ] `get_full_config()` calls `get_campaign_config()` and `get_success_definition()` (not direct dict access)
9. [ ] `get_full_config()` reads from new nested schema (`definition["hive"]`, `definition["edw"]`)
10. [ ] `get_full_config()` passes `edw_config` in the returned dict for EDW sources
11. [ ] `detect_success()` handles both SUCCESS_DT (EDW) and config date field (Hive)
12. [ ] `run_vintage_analysis()` call sites are UNCHANGED
13. [ ] Engine core functions are UNCHANGED
14. [ ] File header says v2.6
15. [ ] Startup message says v2.6

---

## FILE STRUCTURE (target)

```
vintage_engine_v2.6.py
│
├── Docstring (v2.6 header)
├── Imports (unchanged)
├── USER_CONFIG (unchanged)
├── OUTPUT_SCHEMA (unchanged)
├── YEARS_TO_INCLUDE (unchanged)
├── HIVE_PATHS (unchanged)
├── EDW_TABLES (unchanged)
│
├── LAYER 2: CAMPAIGN_METADATA (unchanged)
│
├── LAYER 3: SUCCESS_DEFINITIONS (NEW SCHEMA — Change 1)
├── apply_success_filters() (NEW — Change 2)
│
├── HELPER FUNCTIONS (UPDATED — Change 3)
│   ├── ALL_MNES
│   ├── get_campaign_config()
│   ├── get_success_definition()
│   └── get_full_config() (updated)
│
├── LAYER 1: load_tactic() (unchanged)
│
├── LAYER 4: JOURNEY MODULE
│   ├── load_channel_engagement() (unchanged)
│   ├── _load_email_engagement() (unchanged)
│   ├── load_token_from_edw() (UPDATED — Change 4)
│   └── load_success_outcome() (SIMPLIFIED — Change 5)
│
├── SUCCESS DETECTION
│   ├── detect_success() (MINOR UPDATE — Change 6)
│   └── enrich_with_engagement() (unchanged)
│
├── ENGINE CORE (all unchanged)
│   ├── build_vintage_curves()
│   ├── build_engagement_curves()
│   ├── _build_engagement_metric_curve()
│   └── build_channel_breakdown()
│
├── MAIN RUNNER (unchanged)
│   ├── run_vintage_analysis()
│   └── run_all_campaigns()
│
├── EXPORT FUNCTIONS (unchanged)
│   ├── _detect_result_structure()
│   ├── download_csv()
│   └── download_results()
│
└── SETUP & USAGE (updated version in print — Change 8)
```
