# Patch Notes v2.3
## Based on Code Review of Vintage Engine v2.2

**Review Date**: 2026-01-23
**Reviewer**: [Your Name]
**Code Version**: vintage_engine_v2.2.py
**Status**: [Production Ready / Blocked / Ready with Fixes]

---

## Executive Summary

v2.2 successfully refactored the engine to support:
- Raw test/report group codes (no TEST/CONTROL mapping)
- Secondary metrics for multi-metric campaigns
- Engagement curves folded into main output

**Production Ready?** [YES / NO / YES WITH FIXES]

**Key Blockers** (if any):
- [ ] [Critical issue 1]
- [ ] [Critical issue 2]

---

## Critical Issues (Must Fix)

These BLOCK production deployment. Fix before merging to main.

### 1. SQL Injection Risk in Email Engagement Query
- **Location**: Line 336, function `_load_email_engagement()`
- **Severity**: CRITICAL
- **Type**: BUG
- **Description**:
  ```python
  treatment_id_list = "','".join(treatment_ids)
  query = f"... WHERE TREATMENT_ID IN ('{treatment_id_list}')"  # ← String interpolation
  ```
  If `treatment_ids` contains special characters, query will break or allow injection.

- **Current Risk**: Malformed TACTIC_ID crashes pipeline; potential security issue
- **Proposed Fix**:
  ```python
  # Use parameterized query or escape input
  import re
  treatment_id_list = [re.escape(str(t)) for t in treatment_ids]
  treatment_id_str = "','".join(treatment_id_list)
  ```
  Or better: refactor to use Spark SQL directly (avoid EDW dependency)

- **Impact**: Data pipeline halt; incorrect results
- **Target v2.3**: YES

---

### 2. [Add other critical issues as you find them]

---

## Major Issues (Fix This Version)

These affect correctness or performance but have workarounds. Fix in v2.2 release.

### 1. Hardcoded YEARS_TO_INCLUDE Forces Annual Maintenance
- **Location**: Line 81
- **Severity**: MAJOR
- **Type**: DEBT
- **Description**:
  ```python
  YEARS_TO_INCLUDE = [2025, 2026]
  ```
  Every January, someone must update this hardcoded list.

- **Business Impact**: In 2027, code will silently miss 2027 data unless updated
- **Proposed Fix**:
  ```python
  from datetime import datetime
  current_year = datetime.now().year
  YEARS_TO_INCLUDE = [current_year - 1, current_year]
  ```

- **Test Case**: Run in January 2027; verify 2027 data included
- **Target v2.3**: YES (low effort, high value)

---

### 2. CLNT_NO Zero-Stripping Logic Could Lose Data
- **Location**: Lines 277, 370, 448
- **Severity**: MAJOR
- **Type**: BUG (potential)
- **Description**:
  Three places strip leading zeros from CLNT_NO:
  ```python
  F.regexp_replace(F.trim(F.col("TACTIC_EVNT_ID")), "^0+", "")  # Layer 1
  pdf['CLNT_NO'].str.lstrip('0')  # Layer 4a
  F.regexp_replace(F.substring(...), "^0+", "")  # Layer 4b
  ```
  If CLNT_NO is "00000000" (all zeros), becomes empty string.

- **Data Risk**: Clients with unusual CLNOs drop out of analysis
- **Proposed Fix**:
  ```python
  # Centralize in helper function
  def clean_clnt_no(col):
      """Strip leading zeros, but preserve 0."""
      return F.regexp_replace(F.trim(col), "^0+(?=.)", "")
  ```

- **Test Case**: Include test row with CLNT_NO='00123' and '00000'; verify handling
- **Target v2.3**: YES (correctness)

---

### 3. Inconsistent Data Source Schemas (EDW vs Hive)
- **Location**: Lines 415-450 (load_success_outcome)
- **Severity**: MAJOR
- **Type**: GOVERNANCE
- **Description**:
  Two code paths:
  - **Path 1 (EDW)**: Returns schema from `load_token_from_edw()` (line 421)
  - **Path 2 (Hive)**: Returns schema from Parquet with filters applied

  No guarantee schemas match downstream.

- **Data Risk**: Downstream code expects consistent schema; variations cause silent failures
- **Proposed Fix**:
  ```python
  def load_success_outcome(spark, config):
      # ... load from both sources ...

      # Standardize schema
      required_cols = ["CLNT_NO", config["success_date_field"]]
      result = result.select([col for col in result.columns if col in required_cols])
      return result
  ```

- **Test Case**: Load PRIMARY (card_acquisition) and SECONDARY (wallet_provisioning); verify same schema
- **Target v2.3**: YES (data consistency)

---

### 4. Window Functions Switched to Pandas; Scalability Risk
- **Location**: Lines 569-611 (build_vintage_curves)
- **Severity**: MAJOR
- **Type**: IMPROVEMENT
- **Description**:
  Cumulative calculation switches from Spark to Pandas:
  ```python
  pdf = vintage.toPandas()  # ← Converts to single machine
  for (cohort, tst_grp, rpt_grp), group_data in pdf.groupby(group_cols):
      ...
  ```
  Works for millions of rows but inefficient. Spark can do this natively.

- **Performance Impact**: Slow for large datasets; OOM risk on driver node
- **Proposed Fix**:
  Use Spark Window functions:
  ```python
  from pyspark.sql.window import Window

  w = Window.partitionBy(group_cols).orderBy("DAY")
  result = vintage \
      .withColumn("CUM_SUCCESS", F.sum("SUCCESSES_ON_DAY").over(w)) \
      .withColumn("RATE", F.col("CUM_SUCCESS") / F.col("CLIENT_CNT") * 100)
  ```

- **Test Case**: Run on large campaign (>1M clients); benchmark time/memory
- **Target v2.3**: YES (performance, scalability)

---

### 5. Missing Data Quality Gates
- **Location**: Lines 804-841 (run_vintage_analysis)
- **Severity**: MAJOR
- **Type**: RISK
- **Description**:
  No validation that:
  - Tactic data is non-empty (only checked for 0 records, line 774)
  - Success data has expected schema
  - Curves contain data before export

- **Risk**: Silent pipeline completion with zero results
- **Proposed Fix**:
  ```python
  def validate_results(result_dict):
      for dataset, df in result_dict.items():
          if df.empty:
              raise ValueError(f"{dataset} is empty; something failed silently")
          required_cols = [...specify...]
          if not all(c in df.columns for c in required_cols):
              raise ValueError(f"{dataset} missing columns")
      return result_dict
  ```

- **Test Case**: Intentionally break engagement loader; verify error surfaces
- **Target v2.3**: YES (data quality)

---

## Minor Issues (Backlog for v2.3+)

These improve code quality but don't affect current functionality.

### 1. Magic Numbers and Undocumented Filter Values
- **Location**: Lines 159-160 (STS_CD), 187-191 (TXN_TYPES)
- **Type**: DEBT (Documentation)
- **Issue**: Filter values like STS_CD=["06", "08"] have no business context
- **Fix**: Add module-level documentation or reference to data dictionary
- **Priority**: LOW (nice to have)

---

### 2. Engagement Denominator Could Include Control Group
- **Location**: Line 626 (EMAIL_SENT=1 filter)
- **Type**: GOVERNANCE
- **Issue**: EMAIL_OPEN and EMAIL_CLICK curves use email_sent as denominator. Should control group be excluded?
- **Fix**: Document assumption or add parameter to control behavior
- **Priority**: LOW (design decision needed)

---

### 3. Missing Docstrings on Key Functions
- **Location**: Functions `detect_success()`, `enrich_with_engagement()`, `_build_engagement_metric_curve()`
- **Type**: DEBT (Documentation)
- **Issue**: No docstrings; behavior unclear without reading code
- **Fix**: Add comprehensive docstrings including assumptions, edge cases, output schema
- **Priority**: LOW (maintenance)

---

### 4. Exception Handling in run_all_campaigns() Is Too Broad
- **Location**: Line 892
- **Type**: DEBT
- **Issue**: `except Exception as e` catches all errors, prints, and continues. Hides bugs.
- **Fix**: Catch specific exceptions; consider fail-fast for data quality issues
- **Priority**: LOW (design decision)

---

### 5. Channel Breakdown Loses Daily Granularity
- **Location**: Lines 716-736 (build_channel_breakdown)
- **Type**: GOVERNANCE
- **Issue**: Summary aggregates across days; downstream can't see temporal patterns
- **Fix**: Consider keeping daily breakdown or document rationale
- **Priority**: LOW (requirements question)

---

## Governance Findings

### Data Lineage
- **Current State**: 4-layer architecture is clear but not explicitly versioned
- **Gap**: No metadata columns (loaded_dt, model_version, source_system)
- **Recommendation for v2.3**: Add audit columns to outputs

### Semantic Consistency
- **Current State**: SUCCESS_DEFINITIONS are clear but scattered
- **Gap**: No centralized data dictionary linking to EDW/Hive schemas
- **Recommendation for v2.3**: Link to upstream data lineage documentation

### Documentation
- **Current State**: Module has good high-level comments (lines 1-23)
- **Gap**: Function-level docstrings are minimal
- **Recommendation for v2.3**: Add comprehensive docstrings with I/O contracts

---

## Performance Notes

### Identified Inefficiencies
1. **Pandas cumulative calculation** (line 569): Consider Spark window functions
2. **Engagement data size**: If EDW query returns 100M+ records, toPandas() will OOM
3. **No indexing on join keys**: CLNT_NO joins could benefit from broadcast for small tactic_df

### Optimization Recommendations for v2.3
- [ ] Benchmark cumulative calculation on 10M+ row datasets
- [ ] Add broadcast hint for small dataframes
- [ ] Profile EDW query performance
- [ ] Cache intermediate results (tactic_df after distinct)

---

## Testing Checklist

Before v2.2 production release, ensure:

- [ ] All 6 campaigns run without errors
- [ ] PRIMARY metric curves are non-empty for all campaigns
- [ ] SECONDARY metrics produce reasonable data (VAW, VUI, VUT)
- [ ] Engagement curves only appear when EMAIL_SENT > 0
- [ ] Results are reproducible (same input → same output)
- [ ] Channel breakdown sums correctly
- [ ] Compare v2.1 vs v2.2 on sample data (are raw codes correct?)
- [ ] Test with large dataset (10M+ clients); check performance

---

## Blockers for v2.2 Production

**Status**: [Clear to Proceed / Blocked]

If blocked, list blockers here:
1. [ ] SQL Injection fix (if critical)
2. [ ] CLNT_NO zero-strip validation
3. [ ] Data source schema reconciliation

---

## Deferred to v2.4+

- [ ] Refactor to Spark window functions (perf optimization)
- [ ] Centralized data dictionary
- [ ] Comprehensive docstrings
- [ ] Exception handling redesign

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Code Author | [Name] | | |
| Reviewer | [Your Name] | 2026-01-23 | |
| QA Lead | [Name] | | |
| Data Governance | [Name] | | |

---

## Appendix: Findings Summary

| Category | Count | Severity Breakdown |
|----------|-------|-------------------|
| Bugs | ? | CRITICAL: ? | MAJOR: ? |
| Improvements | ? | CRITICAL: ? | MAJOR: ? |
| Governance | ? | - |
| Debt | ? | - |
| Total | ? | |

---

## Version History

- **v2.2** (2026-01-23): Raw TST_GRP_CD/RPT_GRP_CD, secondary metrics, engagement folded in
- **v2.1** (prior): TEST/CONTROL mapping, dashboard calculated lift
- **v2.0** (prior): Initial framework

---

## References

- **Design Spec**: docs/VVD_VINTAGE_SPEC.pptx
- **Architecture**: archive/MVD_ENGINE_ARCHITECTURE.md
- **Data Catalog**: catalog/PRODUCT_CATALOG.md
