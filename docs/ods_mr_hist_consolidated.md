# ODS MR HIST - Consolidated Reference

## Overview

The `ods_mr_hist` table (ODS Marketing Response History) is a key source table for the Success Library / SuperFact architecture. It contains client-level marketing offer records with treatment details.

---

## Table Identifiers

| Attribute | Value |
|-----------|-------|
| **Full Qualified Name** | `ed10_im.prod_x610_crm.ods_mr_hist` |
| **Hive Database** | `prod_x610_crm` |
| **Hive Table** | `ods_mr_hist` |
| **PySpark Path** | `/prod/01347/app/LS20/data/SparkJobData/effectDate=YYYY-MM-DD` |
| **Format** | Parquet |
| **Partition Column** | `effectdate` |
| **Partitions** | 1000+ |

---

## Partition Behavior

**Type:** Snapshot with rolling window (records can expire)

**Recommendation:** Use latest partition for current campaigns. Be aware that older records may be purged.

**Diagnostic Results (2026-01-19 vs 2026-01-20):**
| Metric | Count |
|--------|-------|
| Records in 2026-01-20 | 8,655,616 |
| Records in 2026-01-19 | 14,437,360 |
| Overlapping records | 650,987 |
| Only in 2026-01-20 | 1,648,320 |
| Only in 2026-01-19 | 2,223,917 |

---

## Schema

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| offr_id | string | Offer identifier |
| clnt_id | int | Client identifier |
| chnl_cd | int | Channel code |
| acct_no | string | Account number |
| tactic_id | string | Tactic identifier |
| camp_reg_id | string | Campaign registration ID |
| lang_cd | string | Language code |
| tr_no | int | Transaction number |
| acct_sufx_no | int | Account suffix number |
| prod_id | string | Product identifier |
| prod_mn | string | Product mnemonic |
| est_mail_dt | string | Estimated mail date |
| campgn_cd | int | Campaign code |
| delvry_mthd_cd | string | Delivery method code |
| foll_up_mthd_cd | string | Follow-up method code |
| offr_strt_dt | string | Offer start date |
| offr_end_dt | string | Offer end date |
| updt_untl_dt | string | Update until date |
| offr_displ_cd | string | Offer display code |
| offr_sts_cd | int | Offer status code |
| offr_reas_cd | int | Offer reason code |
| updt_tmstmp | string | Update timestamp |
| updt_emp_no | int | Update employee number |
| updt_chnl_cd | int | Update channel code |
| msg_creat_tmstmp | string | Message creation timestamp |
| prirty_scor | string | Priority score |
| cr_crd_no | string | Credit card number |
| oper_id | string | Operator ID |
| instrmt_no | string | Instrument number |
| csdb_offr_strt_dt | string | CSDB offer start date |
| csdb_offr_end_dt | string | CSDB offer end date |
| csdb_tactic_id | string | CSDB tactic identifier |
| trgt_typ_cd | string | Target type code |
| treatmt_dtl | string | Treatment detail |
| treatmt_dtl_en | string | Treatment detail (English) |
| treatmt_dtl_fr | string | Treatment detail (French) |
| treatmt_adnl_dtl | string | **Treatment additional detail (JSON field for experiment metadata)** |
| effectdate | date | Effective date (partition column) |

---

## Key Fields for Success Library Integration

### Population Identification

| Field | Purpose |
|-------|---------|
| tactic_id | Unique identifier for the tactic/campaign |
| clnt_id | Client identifier |
| acct_no | Account number |
| chnl_cd | Channel code |
| offr_strt_dt | Offer/treatment start date |
| treatmt_dtl | Treatment description |

### Experiment Tagging (Layer 1)

The `treatmt_adnl_dtl` field is the designated JSON field for storing experiment metadata when standard ODS fields are insufficient. This enables tagging clients to multiple experiments with varying attributes.

**JSON Structure Example:**
```json
{
  "Experiments": ["TestABC01_overall_test", "TestABC12_banner_challenger"],
  "TestABC01_overall_test": {
    "type": "Test vs Control",
    "performance": "Campaign Performance",
    "level": "Campaign Level",
    "impact": "Campaign Impact",
    "method": "Frequentist Causal"
  }
}
```

**Note:** This is the PROPOSED structure. Run diagnostics to verify what's actually populated.

---

## Access Code

### Basic Read (Latest Partition)

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ODS MR HIST Query") \
    .getOrCreate()

# Use latest partition
data_path = "/prod/01347/app/LS20/data/SparkJobData/effectDate=2026-01-20"
df = spark.read.parquet(data_path)
```

### Check JSON Field Content

```python
# Diagnostic: What's in the treatmt_adnl_dtl field?
df.filter(df.treatmt_adnl_dtl.isNotNull()) \
  .select("tactic_id", "treatmt_adnl_dtl") \
  .distinct() \
  .show(50, truncate=False)
```

### Partition Diagnostic Code

Use this to validate partition behavior (snapshot vs append):

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, countDistinct, lit

spark = SparkSession.builder \
    .appName("ODS Partition Diagnostic") \
    .getOrCreate()

# Read two specific partitions - update dates as needed
df_date1 = spark.read.parquet("/prod/01347/app/LS20/data/SparkJobData/effectDate=2026-01-20") \
    .withColumn("partition_date", lit("2026-01-20"))

df_date2 = spark.read.parquet("/prod/01347/app/LS20/data/SparkJobData/effectDate=2026-01-19") \
    .withColumn("partition_date", lit("2026-01-19"))

# Count records in each
print("Records in date1:", df_date1.count())
print("Records in date2:", df_date2.count())

# Check overlap - do same CLNT_ID + OFFR_ID appear in both?
keys_date1 = df_date1.select("CLNT_ID", "OFFR_ID").distinct()
keys_date2 = df_date2.select("CLNT_ID", "OFFR_ID").distinct()

overlap = keys_date1.intersect(keys_date2).count()
only_in_date1 = keys_date1.subtract(keys_date2).count()
only_in_date2 = keys_date2.subtract(keys_date1).count()

print(f"\nOverlapping records (in both): {overlap}")
print(f"Only in date1: {only_in_date1}")
print(f"Only in date2: {only_in_date2}")

# Interpretation
if overlap > 0 and only_in_date1 > 0:
    print("\n--> Looks like SNAPSHOT with incremental adds. Use latest partition.")
elif overlap == 0:
    print("\n--> Looks like APPEND. Use date range based on treatment window.")
else:
    print("\n--> Check results - may need more investigation.")
```

---

## Related Tables in Schema

The following tables exist in the same schema/zone and may be relevant:

| Table Name | Notes |
|------------|-------|
| brms_decision | Business rules management decisions |
| bucketed_cln | Bucketed client data |
| bucketed_rule | Bucketed rule data |
| client_critical | Client critical indicators |
| clnt_rbc_relat | Client RBC relationship |
| days_since_cl | Days since client activity |
| decision | Decision table |
| ga_pagehits_i | Google Analytics page hits |
| ig_mr_hist | IG marketing response history |
| model_ncalead | Model NCA lead scoring |
| monolith_days | Monolith days tracking |
| new_bucketed_ | New bucketed data |
| ods_hist | ODS history |
| ods_hist_latestrec | ODS history latest record |
| parquet_campaign | Parquet campaign data |
| temp_client_table | Temporary client table |
| temp_rules_model | Temporary rules model |

---

## Data Quality Notes

- **Date Fields:** Multiple date fields stored as strings rather than date types - consider standardization for reporting
- **Code Fields:** Several coded fields (chnl_cd, offr_sts_cd, etc.) require lookup tables for interpretation
- **Bilingual Support:** Treatment details available in both English (treatmt_dtl_en) and French (treatmt_dtl_fr)
- **Legacy Constraint:** Standard ODS fields limited to 150 bytes / 150 predefined slots

---

## References

- Full Path: `ed10_im.prod_x610_crm.ods_mr_hist`
- PySpark Path: `/prod/01347/app/LS20/data/SparkJobData/effectDate=YYYY-MM-DD`
- Related Context: Success Library - SuperFact Concept v2

---

*Document consolidated: January 2026*
*Sources: ods_mr_hist_metadata.md, ods_mr_hist_reference.md*
