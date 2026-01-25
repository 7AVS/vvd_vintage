# Code Review Walkthrough: Vintage Engine v2.2

## Version Context
**From v2.1 to v2.2**: Moved from test/control grouping to raw TST_GRP_CD/RPT_GRP_CD. Dashboard now handles lift calculation. Secondary metrics added.

---

## SECTION 1: User Configuration & Paths (Lines 40-101)

### What It Does
Centralizes user settings (HDFS paths, output folder) and channel/year configuration.

### Key Code
```python
USER_CONFIG = {
    "user_id": "427966379",
    "hdfs_base_path": "/user/427966379",
    "output_folder": "vintage_output_v2",
}

YEARS_TO_INCLUDE = [2025, 2026]  # ← Hardcoded

SUPPORTED_CHANNELS = {
    "EMAIL": {"status": "ACTIVE", ...},
    "MOBILE": {"status": "PLANNED", ...},
}
```

### Review Questions
- **Q1**: Is the user_id hardcoded for production or just for development? Should this come from environment variables?
- **Q2**: YEARS_TO_INCLUDE is hardcoded to 2025-2026. What happens in 2027? Is this intentional?
- **Q3**: SUPPORTED_CHANNELS shows MOBILE and BANNER as PLANNED. How do we ensure they won't accidentally run?
- **Q4**: Are these paths tested? What if paths don't exist on the cluster?

### Findings to Log
- [ ] **Hardcoded User ID**: Production risk if multiple users share code
- [ ] **Hardcoded Years**: Annual maintenance burden; consider dynamic logic
- [ ] **Path Validation**: No checks that paths exist or are readable

---

## SECTION 2: Campaign & Success Metadata (Lines 104-208)

### What It Does
Defines the 4-layer architecture:
- Layer 2: Campaign metadata (what campaigns, what metrics)
- Layer 3: Success definitions (how to measure each metric)

### Key Code
```python
CAMPAIGN_METADATA = {
    "VCN": {"primary_metric": "card_acquisition", "secondary_metric": None},
    "VAW": {"primary_metric": "wallet_provisioning", "secondary_metric": "card_usage"},
    ...
}

SUCCESS_DEFINITIONS = {
    "card_acquisition": {
        "source": "HIVE",
        "table_path": PATHS["visa_dr_crd"],
        "date_field": "ISS_DT",
        "filters": {"STS_CD": ["06", "08"], ...}
    }
}
```

### Review Questions
- **Q1**: Are all 6 campaigns defined? Check: VCN, VDA, VDT, VUI, VUT, VAW.
- **Q2**: For campaigns with secondary metrics (VUI, VUT, VAW), are the definitions complete?
- **Q3**: Are the filter values documented? Why STS_CD: ["06", "08"]? Are these VVD-specific status codes?
- **Q4**: "wallet_provisioning" has source="EDW" but table_path=None. Is this a placeholder?
- **Q5**: Are date fields correct? ISS_DT for issuance, ACTV_DT for activation, TXN_DT for transaction?
- **Q6**: The filters use SRVC_ID=36. Is this always correct for VVD?

### Findings to Log
- [ ] **Undocumented Filter Values**: STS_CD ["06", "08"] needs business glossary
- [ ] **Incomplete Definition**: wallet_provisioning marked as EDW but table_path is None
- [ ] **Semantic Gap**: No data dictionary linking SRVC_ID to products
- [ ] **Version Control**: No version field on SUCCESS_DEFINITIONS; hard to track changes

---

## SECTION 3: Experiment Module / Layer 1 (Lines 259-304)

### What It Does
Loads experiment roster from tactic_evnt_hist. Returns raw TST_GRP_CD and RPT_GRP_CD (no mapping to TEST/CONTROL).

### Key Code
```python
def load_tactic(spark, mne):
    tactic = spark.read.parquet(*paths) \
        .filter(F.substring(F.col("TACTIC_ID"), 8, 3) == mne)

    tactic = tactic \
        .withColumn("MNE", F.substring(F.col("TACTIC_ID"), 8, 3)) \
        .withColumn("CLNT_NO", F.regexp_replace(...)) \
        .withColumn("TST_GRP_CD", F.trim(F.col("TST_GRP_CD")))

    tactic = tactic.withColumn("COHORT", F.date_format(F.col("TREATMT_STRT_DT"), "yyyy-MM"))
    tactic = tactic.distinct()
```

### Review Questions
- **Q1**: TACTIC_ID substring [8:10]—is this always the MNE? What if format changes?
- **Q2**: CLNT_NO extraction uses regexp_replace(..., "^0+", ""): Why strip leading zeros? What about CLN_NO with all zeros?
- **Q3**: TST_GRP_CD is trimmed—are there trailing spaces in source data?
- **Q4**: COHORT is yyyy-MM granularity. Could campaigns span multiple cohorts?
- **Q5**: Why distinct()? Are there duplicates in tactic_evnt_hist?
- **Q6**: What validation happens if TACTIC_ID is malformed?

### Findings to Log
- [ ] **Magic Substring**: TACTIC_ID[8:10] is hardcoded; brittle if format changes
- [ ] **Zero Stripping**: Leading-zero removal on CLNT_NO could lose valid data
- [ ] **No Format Validation**: Assumes TACTIC_ID is well-formed; should add checks
- [ ] **Distinct Logic**: No comment explaining why duplicates are expected

---

## SECTION 4: Journey Module / Layer 4a (Lines 311-381)

### What It Does
Loads email engagement data (sent, opened, clicked) from EDW for email campaigns.

### Key Code
```python
def load_channel_engagement(spark, treatment_ids, channel):
    if channel_upper == "EMAIL":
        return _load_email_engagement(spark, treatment_ids)

def _load_email_engagement(spark, treatment_ids):
    query = f"""
    SELECT DISTINCT ...
    FROM DTZV01.VENDOR_FEEDBACK_MASTER FEEDBACK_MASTER
    INNER JOIN DTZV01.VENDOR_FEEDBACK_EVENT FEEDBACK_EVENT ...
    WHERE FEEDBACK_MASTER.TREATMENT_ID IN ('{treatment_id_list}')
    """
```

### Review Questions
- **Q1**: String interpolation in SQL query (line 336): Is treatment_id_list sanitized? SQL injection risk?
- **Q2**: The query uses EDW (Teradata?). What happens if EDW is unavailable?
- **Q3**: CLNT_NO casting and stripping (line 370): Same issue as Layer 1—why strip leading zeros?
- **Q4**: What if no email records found? Returns None—is this handled upstream?
- **Q5**: The disposition_cd mapping (1=SENT, 2=OPENED, 3=CLICKED): Is this documented?

### Findings to Log
- [ ] **SQL Injection Risk**: String interpolation in query (line 336) should use parameterized query
- [ ] **EDW Availability**: No timeout or retry logic; exception handling is silent
- [ ] **Disposition Code**: Magic numbers (1, 2, 3) not defined; should be constants
- [ ] **Zero Stripping Again**: Redundant with Layer 1; centralize this logic

---

## SECTION 5: Journey Module / Layer 4b (Lines 388-450)

### What It Does
Loads success outcome data (card acquisition, activation, usage, wallet provisioning).

### Key Code
```python
def load_success_outcome(spark, config):
    if config["success_source"] == "EDW":
        token_pdf = load_token_from_edw()
        return spark.createDataFrame(token_pdf)

    paths = [f"{config['success_table_path']}{year}*" for year in years_str]
    df = spark.read.parquet(*paths)

    # Apply filters
    if "STS_CD" in filters:
        df = df.filter(F.col("STS_CD").isin(filters["STS_CD"]))
    if "TXN_TYPES" in filters:
        for t in filters["TXN_TYPES"]:
            c = (F.col("TXN_TP") == t["TXN_TP"]) & (F.col("MSG_TP") == t["MSG_TP"])
            txn_cond = c if txn_cond is None else txn_cond | c
        df = df.filter(txn_cond)
```

### Review Questions
- **Q1**: Two branches: EDW vs Hive. Are the resulting schemas consistent?
- **Q2**: load_token_from_edw() (line 388) is complex. Is it actually used? Can we test it?
- **Q3**: The TXN_TYPES filter (lines 437-442) is clunky. Should we use F.expr() or UDF?
- **Q4**: EXTRACT_CLNT_NO flag (line 447): Why only for some paths? Inconsistent behavior?
- **Q5**: No data quality checks: What if filtered data is empty?

### Findings to Log
- [ ] **Dual Data Sources**: EDW and Hive branches not aligned; could produce different results
- [ ] **Messy Filter Logic**: TXN_TYPES loop should be refactored (use F.expr or simpler iteration)
- [ ] **Inconsistent CLNT_NO Logic**: Only applied if EXTRACT_CLNT_NO flag; could cause mismatches
- [ ] **No Data Quality Gate**: No checks for empty or null datasets

---

## SECTION 6: Success Detection & Enrichment (Lines 457-536)

### What It Does
Joins experiment roster with success outcomes. Enriches with engagement data.

### Key Code
```python
def detect_success(tactic_df, success_df, config):
    joined = tactic_alias.join(
        success_select,
        (F.col("t.CLNT_NO") == F.col("s.SUCCESS_CLNT_NO")) &
        (F.col("s.SUCCESS_DT") >= F.col("t.TREATMT_STRT_DT")) &
        (F.col("s.SUCCESS_DT") <= F.col("t.TREATMT_END_DT")),
        how="left"  # ← Left join: keep all tactic records
    )

    result = joined.groupBy(groupby_cols).agg(
        F.max(F.when(F.col("s.SUCCESS_DT").isNotNull(), 1).otherwise(0)).alias("SUCCESS_FLAG")
    )
```

### Review Questions
- **Q1**: Left join keeps all tactic records. Is this correct? Should we use inner join?
- **Q2**: Date range: TREATMT_STRT_DT to TREATMT_END_DT. Does "success during treatment" make sense for all metrics?
- **Q3**: SUCCESS_FLAG logic uses max(when(...)). Correct? What if multiple successes within window?
- **Q4**: DAYS_TO_SUCCESS is min(). What about multiple successes on different days?
- **Q5**: enrich_with_engagement() joins with email data. What if engagement data has duplicates?

### Findings to Log
- [ ] **Join Type Assumption**: Left join assumes we want all tactic records; should document rationale
- [ ] **Date Range Logic**: Assumes treatment window is success window; may not hold for activation/usage
- [ ] **Multiple Successes**: If client succeeds twice, do we capture both or just first?
- [ ] **Engagement Join**: No deduplication before join; could inflate engagement metrics

---

## SECTION 7: Vintage Curves (Lines 543-611)

### What It Does
Core calculation: groups by cell and day, computes cumulative success rates.

### Key Code
```python
def build_vintage_curves(success_df, mne, metric_type="PRIMARY"):
    totals = success_df.groupBy(group_cols).agg(
        F.count("*").alias("CLIENT_CNT"),
        F.expr("percentile_approx(WINDOW_DAYS, 0.5)").alias("WINDOW_DAYS")
    )

    successes = success_df.filter(F.col("SUCCESS_FLAG") == 1).groupBy(
        group_cols + ["DAYS_TO_FIRST_SUCCESS"]
    ).agg(F.count("*").alias("SUCCESSES_ON_DAY"))

    # Pandas for cumulative calculation
    pdf = pdf.sort_values(group_cols + ["DAY"])
    cum_successes += day_successes[day]
    RATE = round(cum_successes / client_cnt * 100, 4)
```

### Review Questions
- **Q1**: WINDOW_DAYS uses percentile_approx(0.5)—median window days. Why not use TREATMT_END_DT - TREATMT_STRT_DT directly?
- **Q2**: Switching to pandas (line 569): Why not use Spark window functions for cumulative? Performance at scale?
- **Q3**: Fill missing days (line 593): Assumes 0 successes for missing days. Correct?
- **Q4**: DAY range: 0 to window_days. What about successes after window_days ends?
- **Q5**: Rounding RATE to 4 decimals: Is this precision adequate?
- **Q6**: What if client_cnt is 0? Check line 607.

### Findings to Log
- [ ] **Window Days Calculation**: Using median; could hide outliers. Consider percentile + explicit logic
- [ ] **Pandas Scalability**: Switching to pandas may not scale. Consider Spark window functions
- [ ] **Missing Days Assumption**: Fills with 0; doesn't validate this is correct
- [ ] **Division by Zero**: Line 607 has check (client_cnt > 0) but should be explicit guard
- [ ] **Post-Window Data**: Any successes after window ends are dropped silently

---

## SECTION 8: Engagement Curves (Lines 614-713)

### What It Does
Separate curves for email opens and clicks. Denominator = email recipients (SENT=1).

### Key Code
```python
def build_engagement_curves(success_df, mne):
    email_df = success_df.filter(F.col("EMAIL_SENT") == 1)

    email_df = email_df.withColumn(
        "DAYS_TO_OPEN",
        F.when(F.col("EMAIL_OPENED") == 1,
               F.datediff(F.col("EMAIL_OPENED_DT"), F.col("TREATMT_STRT_DT"))).otherwise(None)
    )

    open_curve = _build_engagement_metric_curve(email_df, mne, "DAYS_TO_OPEN", "EMAIL_OPENED", "EMAIL_OPEN")
```

### Review Questions
- **Q1**: EMAIL_SENT=1 filter: What if engagement data has no EMAIL_SENT column?
- **Q2**: Date calculation: TREATMT_STRT_DT to EMAIL_OPENED_DT. Correct baseline?
- **Q3**: EMAIL_OPENED=1 but EMAIL_OPENED_DT is null: Can this happen? Line 632 checks isNotNull.
- **Q4**: Why two separate curves (open, click) instead of one combined metric?
- **Q5**: What's the relationship between PRIMARY metric and engagement metrics? Are they orthogonal?

### Findings to Log
- [ ] **Column Assumption**: CODE assumes EMAIL_SENT column exists; should validate
- [ ] **Engagement Denominator**: Using email_sent as denominator; what about control group?
- [ ] **Metric Definition**: EMAIL_OPEN vs EMAIL_CLICK relationship unclear; should document
- [ ] **Null Dates**: DAYS_TO_OPEN can be None; ensure cumulative logic handles this

---

## SECTION 9: Channel Breakdown (Lines 716-736)

### What It Does
Summary by channel (not daily curves). Groups by cell + channel.

### Key Code
```python
def build_channel_breakdown(success_df, mne):
    breakdown = success_df.withColumn(
        "CHANNEL",
        F.trim(F.coalesce(F.col("TACTIC_CELL_CD"), F.lit("UNKNOWN")))
    )

    breakdown = breakdown.groupBy("COHORT", "TST_GRP_CD", "RPT_GRP_CD", "CHANNEL").agg(
        F.count("*").alias("CLIENT_CNT"),
        F.sum("SUCCESS_FLAG").alias("SUCCESS_CNT")
    )
```

### Review Questions
- **Q1**: TACTIC_CELL_CD as CHANNEL: Is this reliable? What if null or malformed?
- **Q2**: No daily breakdown in channel_breakdown—is this intentional? Flatten for dashboard?
- **Q3**: SUCCESS_FLAG uses sum(): Assumes 0/1 flags. Correct?
- **Q4**: Missing WINDOW_DAYS in this output. Should it be included?

### Findings to Log
- [ ] **Channel Source**: TACTIC_CELL_CD may not be reliable; consider validation
- [ ] **Granularity Loss**: Channel breakdown removes day dimension; some data loss
- [ ] **Documentation Gap**: Should explain why channel_breakdown is not daily

---

## SECTION 10: Main Runner (Lines 743-874)

### What It Does
Orchestrates all layers for a single campaign. Calls: load_tactic → load_success → detect_success → build_curves.

### Key Code
```python
def run_vintage_analysis(spark, mne, verbose=True, include_engagement=True):
    # Layer 2: Get config
    campaign = get_campaign_config(mne)

    # Layer 1: Load tactic
    tactic_df = load_tactic(spark, mne)
    tactic_df.persist(StorageLevel.MEMORY_AND_DISK)

    # Layer 4: Load success + engagement
    success_table_primary = load_success_outcome(spark, primary_config)
    success_df_primary = detect_success(tactic_df, success_table_primary, primary_config)

    # Build curves
    primary_curves = build_vintage_curves(success_df_primary, mne, "PRIMARY")

    # Secondary metric
    if secondary_config is not None:
        secondary_curves = build_vintage_curves(success_df_secondary, mne, "SECONDARY")
```

### Review Questions
- **Q1**: Error handling: What if load_tactic() returns empty? Line 774 has check.
- **Q2**: persist(MEMORY_AND_DISK): Correct choice? What if tactic_df is huge?
- **Q3**: Secondary metric is optional. What if campaign has no secondary_metric?
- **Q4**: unpers()ist(): When should this happen? After each metric?
- **Q5**: The run_vintage_analysis() returns dict with "vintage_curves" and "channel_breakdown". Why no separate structure validation?

### Findings to Log
- [ ] **Error Propagation**: Silently returns None on error; should log or raise
- [ ] **Resource Management**: Persist/unpersist logic is manual; could forget calls
- [ ] **Secondary Metric Optional**: No clear docs on which campaigns have secondary
- [ ] **Output Validation**: No checks that output DataFrames are non-empty

---

## SECTION 11: Batch Runner (Lines 877-901)

### What It Does
Runs analysis for all 6 campaigns and combines results.

### Key Code
```python
def run_all_campaigns(spark, mnes=None, include_engagement=True):
    mnes = mnes or ALL_MNES

    for mne in mnes:
        try:
            result = run_vintage_analysis(spark, mne, include_engagement=include_engagement)
            if result:
                results[mne] = result
                all_curves.append(result["vintage_curves"])
        except Exception as e:
            print(f"ERROR {mne}: {str(e)}")

    if all_curves:
        results["_combined_curves"] = pd.concat(all_curves, ignore_index=True)
```

### Review Questions
- **Q1**: Exception handling: Catches all exceptions, prints, and continues. Should we fail fast for some errors?
- **Q2**: Combining curves: Different campaigns may have different metrics. Is concat sufficient?
- **Q3**: What if some campaigns fail? Combined results are partial—is this acceptable?
- **Q4**: ALL_MNES is hardcoded (line 214). Should be parameterized?

### Findings to Log
- [ ] **Silent Failures**: Exceptions caught and printed; could hide bugs
- [ ] **Partial Results**: If campaign fails, combined results are incomplete; no flag
- [ ] **Campaign List**: ALL_MNES is list copy; should use reference or parameter

---

## SECTION 12: Export Functions (Lines 908-970)

### What It Does
Detects result structure (flat vs nested) and creates download links.

### Key Code
```python
def download_csv(data, filename="vintage_results.csv"):
    csv_data = data.to_csv(index=False)
    size_mb = len(csv_data.encode('utf-8')) / (1024 * 1024)

    if size_mb > 50:
        print(f"Data too large ({size_mb:.1f} MB). Filter before exporting.")
        return

    b64 = base64.b64encode(csv_data.encode()).decode()
    link = f'<a download="{filename}" href="data:text/csv;base64,{b64}">'
```

### Review Questions
- **Q1**: 50 MB limit for Jupyter download: Is this reasonable? What if results are larger?
- **Q2**: Base64 encoding in URL: Correct for Jupyter? Performance at scale?
- **Q3**: No error handling for large files. User just gets message—is this UX acceptable?
- **Q4**: CSV format: What about precision loss? Should we export Parquet?

### Findings to Log
- [ ] **Download Size Limit**: 50 MB is arbitrary; should be configurable
- [ ] **Format Choice**: CSV may lose precision; consider Parquet for production
- [ ] **Error UX**: Silently fails if too large; should suggest alternative formats

---

## Summary: Running This Walkthrough

1. **Start with your concerns**: Which section worries you most?
2. **Go section-by-section**: For each, read the questions and findings
3. **Ask me to explain**: I'll walk through logic, data flow, assumptions
4. **Log findings**: Use the template above to capture issues
5. **Prioritize**: Separate critical bugs from nice-to-have improvements
6. **Decide**: Is v2.2 production-ready or blocked?

---

## Next Steps

After we finish this review:
- Consolidate findings into CODE_REVIEW_LOG.csv
- Draft PATCH_NOTES_v2.3.md with prioritized backlog
- Create GitHub issue or Jira ticket if needed
- Decide: v2.2 Production? v2.2 + Fixes? Or v2.3 required?
