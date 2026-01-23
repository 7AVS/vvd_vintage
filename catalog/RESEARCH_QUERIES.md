# Research Queries

Queries to run at work to gather catalog data.

---

## 1. Get All LOBs from Mnemonic Mapping

```sql
-- What LOBs exist in the mnemonic mapping table?
SELECT DISTINCT
    LOB,
    COUNT(*) AS MNE_COUNT
FROM DTZTAU.CIDM_MNEMONIC_ATTRS
GROUP BY LOB
ORDER BY MNE_COUNT DESC;
```

---

## 2. Get All MNEs by LOB

```sql
-- List all MNEs with their LOB and description
SELECT
    LOB,
    MNE,
    CAMPAIGN_DESCRIPTION,
    MEASUREMENT_CATEGORY
FROM DTZTAU.CIDM_MNEMONIC_ATTRS
ORDER BY LOB, MNE;
```

---

## 3. Get Campaign Categories

```sql
-- What campaign categories exist?
SELECT DISTINCT
    CAMPAIGN_CATEGORY,
    COUNT(*) AS COUNT
FROM DTZTAU.CIDM_MNEMONIC_ATTRS
GROUP BY CAMPAIGN_CATEGORY
ORDER BY COUNT DESC;
```

---

## 4. Get Measurable Campaigns Only

```sql
-- Which campaigns are marked as measurable?
SELECT
    LOB,
    MNE,
    CAMPAIGN_DESCRIPTION,
    MEASUREMENT_CATEGORY
FROM DTZTAU.CIDM_MNEMONIC_ATTRS
WHERE MEASUREMENT_CATEGORY = 'Measurable'
ORDER BY LOB, MNE;
```

---

## 5. Explore Tactic Data for Active MNEs

```python
# PySpark - Get distinct MNEs from tactic data
tactic_df = spark.read.parquet("/prod/sz/tsz/00150/cc/DTZTA_T_TACTIC_EVNT_HIST/EVNT_STRT_DT=2025*")

# Count by MNE
tactic_df.withColumn("MNE", F.substring(F.col("TACTIC_ID"), 8, 3)) \
    .groupBy("MNE") \
    .count() \
    .orderBy("count", ascending=False) \
    .show(50)
```

---

## 6. Cross-Reference: MNEs in Tactic vs Mnemonic Mapping

```python
# Which MNEs in tactic data are NOT in mnemonic mapping?
# (and vice versa)
```

---

## Results

### LOB Inventory
*Paste results here*

| LOB | MNE Count |
|-----|-----------|
| | |

### MNE Inventory
*Paste results here*

---

## Notes

*Add observations here*

