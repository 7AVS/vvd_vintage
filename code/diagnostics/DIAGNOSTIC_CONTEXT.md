# ODS & Tactic Table Diagnostics

## Purpose

Investigate Layer 1/Layer 2 tables to determine if experiment metadata is already being populated in JSON fields, which would eliminate the need for hardcoded lookups in the vintage curve pipeline.

## Target Fields

| Table | Field | Size | Purpose |
|-------|-------|------|---------|
| ods_hist | `treatmt_adnl_dtl` | varchar(8000) | JSON field for experiment metadata |
| ods_hist | `treatmt_dtl` | varchar(4000) | Treatment detail |
| ods_mr_hist | Same fields | Same | Alternative ODS table |
| tactic_evnt_hist | `addnl_decisn_data1/2/3` | Flexible fields | Additional decision data |

## Key Findings

### Column Names Are UPPERCASE
All Hive table columns are uppercase. Use:
```python
col("TREATMT_ADNL_DTL")  # Not treatmt_adnl_dtl
col("TACTIC_ID")         # Not tactic_id
```

### VVD Mnemonics Are at END of TACTIC_ID
Filter using `endswith`, not `startswith`:
```python
# Correct
df.filter(expr("right(TACTIC_ID, 3)").isin(['VDA', 'VCN', 'VDT']))

# Wrong
df.filter(col("TACTIC_ID").startswith("VDA"))
```

### Partition Columns
| Table | Partition Column | Format |
|-------|-----------------|--------|
| ods_hist | `effectdate` | YYYY-MM-DD |
| ods_mr_hist | `effectdate` | YYYY-MM-DD |
| tactic_evnt_hist | `evnt_strt_dt` | YYYY-MM-DD |

### ods_hist Table Is Broken
The `ods_hist` Hive table cannot be read directly because the underlying HDFS directory contains `odsbackup/` folders mixed with `effectDate=` partitions. Spark's partition discovery fails with:
```
java.lang.AssertionError: Conflicting directory structures detected
```

**Workaround:** Read parquet directly from a specific partition:
```python
# Instead of: spark.table("prod_x610_crm.ods_hist")
spark.read.parquet("/prod/01347/app/ls20/data/sparkjobdata/effectDate=2025-11-01")
```

### ods_mr_hist Works Fine
Use `spark.table("prod_x610_crm.ods_mr_hist")` with partition filtering.

---

## Scripts

| Script | Table | Status |
|--------|-------|--------|
| `ods_json_field_diagnostic.py` | ods_mr_hist | Ready to run |
| `ods_hist_diagnostic.py` | ods_hist | Uses direct parquet read |
| `ods_hist_simple_test.py` | ods_hist | Confirms table exists but can't read |
| `ods_hist_direct_read.py` | ods_hist | Bypasses Hive, reads parquet directly |
| `tactic_evnt_hist_diagnostic.py` | tactic_evnt_hist | Ready to run |

---

## How to Run

```bash
spark-submit ods_json_field_diagnostic.py      # ODS MR HIST
spark-submit ods_hist_direct_read.py           # ODS HIST (direct parquet)
spark-submit tactic_evnt_hist_diagnostic.py    # Tactic Event History
```

If `ods_hist_direct_read.py` fails on partition date, it will list available partitions. Adjust `EFFECTDATE` in the script to a valid date.

---

## Configuration

All scripts use these defaults:
- **Date range:** 2025-10-01 to 2025-12-31
- **Campaign filter:** VDA (can expand to VCN, VDT, VUI, VUT, VAW)
- **Database:** prod_x610_crm

---

## What to Look For in Results

1. **Is `treatmt_adnl_dtl` populated?** (not_empty > 0)
2. **Does it contain JSON?** (has_brace > 0)
3. **What keys exist?** (Experiments, type, Test, Control)
4. **How much of the 8000 char capacity is used?**
5. **Are `addnl_decisn_data` fields populated in tactic table?**

If these fields contain experiment metadata, we can parse them instead of hardcoding campaign lookups.
