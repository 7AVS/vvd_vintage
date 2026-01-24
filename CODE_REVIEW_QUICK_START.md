# Code Review Quick Start: Vintage Engine v2.2

## What We're Doing

Structured walkthrough of `vintage_engine_v2.2.py` to:
1. Identify bugs, risks, governance gaps
2. Validate production readiness
3. Build backlog for v2.3

**Time**: ~90 min | **Output**: Patch notes + findings log

---

## Three Files You'll Use

| File | Purpose | Use When |
|------|---------|----------|
| `CODE_REVIEW_FRAMEWORK.md` | Philosophy & categories | Kickoff; reference during review |
| `REVIEW_WALKTHROUGH.md` | Section-by-section guide | Main event; I explain, you ask questions |
| `CODE_REVIEW_LOG.csv` | Track findings | Log each issue as you find it |
| `PATCH_NOTES_v2.3_TEMPLATE.md` | Consolidated backlog | End of session; transfer findings here |

---

## Finding Categories (Use These)

| Type | Example | When to Log |
|------|---------|------------|
| **BUG** | Join loses data, calculation wrong, null not handled | Incorrect behavior |
| **RISK** | Could fail at scale, edge case unhandled, hardcoded value | Potential issue |
| **IMPROVEMENT** | Pandas → Spark window functions, refactor for clarity | Performance/quality |
| **GOVERNANCE** | Undocumented filter, missing lineage, inconsistent semantics | Data management |
| **DEBT** | Magic numbers, duplicated code, missing docstrings | Maintainability |

---

## Severity Levels (Use These)

| Level | Meaning | Action |
|-------|---------|--------|
| **CRITICAL** | Breaks pipeline, data wrong, security risk | Fix before v2.2 ships |
| **MAJOR** | Incorrect results, big perf hit, affects downstream | Fix in v2.2 |
| **MINOR** | Workaround exists, nice-to-have | v2.3+ backlog |
| **INFO** | FYI, design question | Document, decide later |

---

## Review Checklist

### Before Starting (5 min)
- [ ] Read `CODE_REVIEW_FRAMEWORK.md` sections 1-3
- [ ] Open `vintage_engine_v2.2.py` and `REVIEW_WALKTHROUGH.md` side-by-side
- [ ] Have `CODE_REVIEW_LOG.csv` ready to edit

### During Review (section by section)
- [ ] Read "What It Does" summary
- [ ] Read "Key Code" block
- [ ] Go through "Review Questions"
- [ ] For each finding, log to CSV:
  - Finding ID (R001, R002, ...)
  - Section + line number
  - Type (BUG/RISK/IMPROVEMENT/GOVERNANCE/DEBT)
  - Severity (CRITICAL/MAJOR/MINOR)
  - Title + description
  - Proposed fix (if obvious)
  - Status: "pending"

### After Review (15 min)
- [ ] Tally findings by severity
- [ ] Transfer critical/major findings to PATCH_NOTES_v2.3_TEMPLATE.md
- [ ] Make recommendation: Production Ready? Blocked? Ready with Fixes?

---

## How to Log a Finding

### In CSV Format
```
R001,2026-01-23,Layer 4a,336,BUG,CRITICAL,SQL Injection Risk,"String interpolation in treatment_id_list allows injection",Data pipeline halt,"Use parameterized query or escape input",pending
R002,2026-01-23,Config,81,DEBT,MAJOR,Hardcoded YEARS_TO_INCLUDE,"Annual maintenance burden; becomes stale in 2027","Maintenance burden in 2027","Use dynamic: current_year - 1, current_year",pending
```

### Template
```
finding_id, date, section, line_number, type, severity, title, description, impact, proposed_fix, status
```

---

## Questions to Ask for Each Section

### If it's DATA LOADING:
- Are we filtering correctly?
- Could we lose records in the join?
- What if the source data is malformed?
- Is the schema consistent downstream?

### If it's CALCULATION:
- What happens with edge cases (empty data, division by zero)?
- Is this business logic correct or an assumption?
- Could this fail at scale?
- Is rounding/precision adequate?

### If it's OUTPUT:
- Does the schema match requirements?
- Could downstream break if column is null?
- Is this auditable?

---

## Red Flags to Watch For

| Red Flag | Questions | Check |
|----------|-----------|-------|
| **Hardcoded value** | Does this change? Is it production-safe? | YEARS_TO_INCLUDE, USER_ID, filter values |
| **String interpolation in SQL** | Could this allow injection? Should use params | Line 336, 358 |
| **Pandas conversion** | Will this scale? Is it performant? | Line 569 (toPandas) |
| **Silent exception** | Could bugs hide? Should we fail fast? | Line 892 (except Exception) |
| **Left join / optional filter** | Are we losing data intentionally? | Line 472, 566 |
| **Magic number** | Where does this come from? Documented? | STS_CD, TXN_TP values |
| **Assumed column** | What if it's null or missing? | EMAIL_SENT, TACTIC_CELL_CD |

---

## Decision Tree: Is This a Bug?

```
Does it produce WRONG results?
  ├─ YES → BUG (CRITICAL/MAJOR)
  └─ NO → Could it produce wrong results in edge cases?
          ├─ YES → RISK (MAJOR)
          └─ NO → Is it inefficient or unclear?
                  ├─ YES → IMPROVEMENT or DEBT (MINOR)
                  └─ NO → Is it a documentation/governance gap?
                          ├─ YES → GOVERNANCE (MINOR/INFO)
                          └─ NO → Not a finding; move on
```

---

## Example Findings (Already Pre-Identified)

### Critical
1. **Line 336**: SQL injection in treatment_id_list (string interpolation)
2. **Line 277, 370, 448**: CLNT_NO zero-stripping could lose data

### Major
1. **Line 81**: Hardcoded YEARS_TO_INCLUDE (annual maintenance burden)
2. **Line 569**: Pandas cumulative (scalability risk)
3. **Line 415-450**: Inconsistent schemas (EDW vs Hive)
4. **Line 774-841**: No data quality gates (silent pipeline completion)

### Minor
1. **Line 159**: Undocumented filter values (STS_CD)
2. **Line 892**: Too-broad exception handling

---

## At the End of Session

You should have:
1. **CODE_REVIEW_LOG.csv** with 5-15 findings logged
2. **PATCH_NOTES_v2.3_TEMPLATE.md** filled in with:
   - Critical issues (fix or blocked)
   - Major issues (backlog for v2.2)
   - Minor issues (v2.3+)
3. **Go/No-Go Decision**: Production ready or blocked?

---

## Pro Tips

1. **Don't over-optimize**: Focus on correctness first, performance second, nice-to-haves third
2. **Ask stupid questions**: If the code is confusing, it probably needs docs
3. **Compare to requirements**: Is v2.2 doing what the spec (VVD_VINTAGE_SPEC.pptx) says?
4. **Test your findings**: "Would this break if...?" is a good test
5. **Propose fixes**: Don't just complain; suggest concrete improvements
6. **Document assumptions**: If you see a choice (left join vs inner, percentile vs median), ask why

---

## Need Help?

**Questions about:**
- **Finding category**: See CODE_REVIEW_FRAMEWORK.md section 2
- **What to review**: See REVIEW_WALKTHROUGH.md for each section
- **How to log**: See CODE_REVIEW_LOG.csv template above
- **Making a call**: See "Decision Tree" section

---

## Let's Go

**Ready to start?** Pick a section from REVIEW_WALKTHROUGH.md and let's walk through it.

Which is your biggest concern about this code?
- Performance/scalability?
- Correctness/data quality?
- Governance/lineage?
- All of the above?

Start there.
