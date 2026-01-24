# Code Review Framework for Vintage Engine v2.2

## Purpose
Structured walkthrough of vintage_engine_v2.2.py with documented findings for next version iteration.

---

## 1. Industry Standard Approach

This framework follows:
- **Google Code Review Standards** (clarity, maintainability, safety)
- **DAMA-DMBOK** (data governance & lineage)
- **Palantir's Code Review Model** (categorical findings, severity)

### Three Review Tracks (Run in Parallel)
1. **Technical Soundness**: Logic, algorithms, error handling
2. **Data Governance**: Semantics, lineage, auditability
3. **Maintainability**: Code quality, documentation, patterns

---

## 2. Finding Categories & Severity Levels

### Finding Types
| Type | Description | Example |
|------|-------------|---------|
| **BUG** | Logic error, incorrect calculation, wrong data flow | Join condition error, off-by-one in cumulative |
| **RISK** | Potential issue under edge cases or scale | Division by zero not handled, partition strategy |
| **IMPROVEMENT** | Better approach, performance, maintainability | Use window functions vs pandas, add caching |
| **GOVERNANCE** | Semantic clarity, documentation, lineage | Missing metric definition, unclear business logic |
| **DEBT** | Technical debt, refactoring needed | Duplicated code, magic numbers, loose typing |

### Severity Levels
| Level | Definition | Action |
|-------|-----------|--------|
| **CRITICAL** | Breaks functionality, data integrity risk, halts pipeline | Fix before merge |
| **MAJOR** | Incorrect results, significant performance impact | Fix in this version |
| **MINOR** | Workaround exists, affects readability | Fix in next version |
| **INFO** | FYI for future design | Document for next iteration |

---

## 3. Review Session Structure

### Pre-Review (5 min)
- Establish context: What changed from v2.1?
- What questions do we want answered?
- Who's the reviewer? (peer, lead, external)

### Live Review (Section by Section)
For each code block:
1. **What it does** (1-2 sentences)
2. **Why it matters** (to stakeholders/downstream)
3. **Questions** (clarify intent)
4. **Findings** (issues, improvements, risks)

### Post-Review (5 min)
- Categorize findings
- Assess if v2.2 is production-ready
- Create backlog for v2.3+

---

## 4. Finding Log Template

Create a file: `PATCH_NOTES_v2.3.md`

```markdown
# Findings from v2.2 Code Review
Date: 2026-01-23
Reviewer: [Name]
Target Version: v2.3

## Critical Issues (Must Fix)
- [ ] **Issue Title**: Description | Location: line X | Category: BUG

## Major Issues (Fix This Version)
- [ ] **Issue Title**: Description | Location: line X | Category: IMPROVEMENT

## Minor Issues (Backlog for v2.3)
- [ ] **Issue Title**: Description | Location: line X | Category: DEBT

## Governance Notes
- **Semantic Gap**: Description

## Performance Notes
- **Optimization**: Description

---

## Summary
- **Status**: Ready for Production / Needs Fixes / Blocked
- **Blockers**: [List]
- **Next Steps**: [List]
```

---

## 5. Quick Reference: Key Questions for Each Section

### Configuration Section (Lines 40-101)
- Are all user config parameters externalized?
- Are paths correct and tested?
- Is YEARS_TO_INCLUDE dynamic or hardcoded?

### Metadata Layers (Lines 104-208)
- Are all 6 campaigns fully defined?
- Do secondary metrics make sense?
- Are success definitions complete and auditable?

### Layer 1: Experiment Module (Lines 259-304)
- How do we validate TST_GRP_CD and RPT_GRP_CD?
- What if TACTIC_ID format changes?
- Is COHORT granularity sufficient?

### Layer 4: Journey Modules (Lines 311-450)
- Email engagement: Are we handling nulls correctly?
- EDW queries: Are they performant at scale?
- Success detection: Join logic is clear?

### Engine Core (Lines 543-737)
- Cumulative calculation: Does it handle all edge cases?
- Engagement curves: Are denominators correct?
- Channel breakdown: Is TACTIC_CELL_CD reliable?

### Main Runner & Export (Lines 743-970)
- Error handling: What happens if a campaign fails?
- Output schema: Is it correctly documented?
- Download function: Size limits adequate?

---

## 6. Actionable Checklist for This Session

### Before You Start
- [ ] Read sections 1-3 of this document
- [ ] Open vintage_engine_v2.2.py and CODE_REVIEW_LOG.csv side-by-side
- [ ] Note any questions that come up

### During Review
- [ ] For each major function, ask: "Could this fail at scale?"
- [ ] For each join, ask: "Are we losing data?"
- [ ] For each calculation, ask: "Is this business-logic correct?"
- [ ] For each output, ask: "Will downstream trust this?"

### After Each Finding
- [ ] Record in CODE_REVIEW_LOG.csv
- [ ] Mark severity and type
- [ ] Add line number and proposed fix
- [ ] Move to appropriate section of PATCH_NOTES_v2.3.md

### At the End
- [ ] Tally findings by type and severity
- [ ] Make go/no-go recommendation
- [ ] Identify blockers for production

---

## 7. Example Finding (Well-Formatted)

### ✗ FINDING: Hardcoded YEARS_TO_INCLUDE

**Type**: DEBT
**Severity**: MINOR
**Location**: Line 81
**Current Code**:
```python
YEARS_TO_INCLUDE = [2025, 2026]
```

**Issue**: This changes every year but is hardcoded. When we run in 2027, we'll miss 2027 data unless someone manually updates this.

**Proposed Fix**:
```python
from datetime import datetime
YEARS_TO_INCLUDE = [datetime.now().year - 1, datetime.now().year]
```

**Impact**: Maintenance burden, potential data loss risk if forgotten
**Next Step**: Add to v2.3 backlog (LOW priority)

---

## 8. How to Run This Session

1. **Kickoff** (5 min): Agree on scope and questions
2. **Walk Through by Section** (60 min):
   - You ask questions about each code block
   - I explain the logic, intent, and data flow
   - We identify gaps, risks, improvements
3. **Log Findings** (15 min):
   - Categorize all findings by type/severity
   - Draft PATCH_NOTES_v2.3.md
4. **Recommendation** (5 min):
   - Is v2.2 production-ready?
   - What must be fixed?
   - What should wait for v2.3?

---

## 9. Outputs You'll Get

By end of session, you'll have:

1. **CODE_REVIEW_LOG.csv** - Structured table of all findings
2. **PATCH_NOTES_v2.3.md** - Prioritized backlog for next version
3. **Production Decision** - Go/no-go recommendation
4. **Documentation** - Gaps identified in the code comments

---

## Start Here

**Are you ready to begin?**

Tell me:
1. What's your primary concern about this code? (performance, correctness, scale, maintenance?)
2. Who's the audience for the findings? (dev team, leadership, compliance?)
3. Should we focus on any particular section first?

Then we'll walk through section-by-section and build the review log together.
