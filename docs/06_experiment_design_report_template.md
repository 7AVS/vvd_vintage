# Experiment Design Report: [Test Name]

**[Full name and role of lead writer(s)]**

**Date:** August 2, 2025

**Version:** v1.0  
**Audience:** Prepared for: Executive Oversight – [Names if known]  
**Confidentiality:** Internal Document – Do Not Distribute Externally

---

## 1. Executive Summary

*Purpose: Provide a one-page "at-a-glance" for executives—focused on clarity, not complexity.*

### Why are we testing?
*Example: "To determine whether personalized credit card recommendations increase conversion among new Avion Rewards users."*

### What is being tested and measured?
*Example: "Clients will receive one of two message types. We will measure uplift in application rates over 30 days."*

### What will success look like?
*Example: "If Treatment A improves the application rate by at least 1.5 percentage points over control (p < 0.05), it will be adopted."*

### How long and how safe?
*Example: "The test will run for 6 weeks. Weekly monitoring and SRM checks are in place. No client-level harm is expected."*

---

## 2. Strategic Context

*Purpose: Help executives and analysts understand the test's business rationale and historical context.*

- [Summarize the problem or opportunity this test is addressing.]
- [Include prior data or insights that led to this test.]
- [Define what's at stake if we get this wrong or delay implementation.]
- [State the test's alignment to larger goals, e.g., "Supports NIBT targets via uplift modeling and NBA optimization."]

---

## 3. Hypothesis & Objectives

*Purpose: Lock in what you're testing and how you'll know if it worked.*

### Primary Hypothesis
[State a clear, directional, and testable hypothesis.]

*Example: "Offering Card A with personalized copy will increase application rates compared to generic copy."*

### Success Criteria
[Define the specific outcome that confirms the hypothesis.]

*Example: "≥1.5pp lift, p < 0.05, 95% CI not overlapping zero."*

### Secondary Hypotheses (optional)
[List any pre-specified secondary hypotheses here.]

---

## 4. Experiment Design & Assignment

*Purpose: Lay out exactly how the test will work, from audience eligibility to how treatments are assigned.*

### Design Type
*Example: "Parallel A/B test, with clients randomly assigned to one of two treatments or a control group."*

### Randomization Unit
*Example: "Clients, using persistent IDs in bucket assignment logic."*

### Eligibility Rules
[Define who qualifies for this test. Attach SQL/criteria in Appendix if needed.]

### Treatment Arms:

- **Treatment A:** *Example: "Personalized copy with recommended card."*
- **Treatment B:** *Example: "Generic product carousel."*
- **Control:** *Example: "No NBA."*

### Allocation Split
*Example: "Split 45/45/10 to Treatments A, B, and Control."*

### Platform & Implementation
[Describe who is assigning treatment (e.g., Borealis orchestrator) and how exposure is controlled.]

---

## 5. Sample Size & Power Analysis

*Purpose: Show that the test is statistically powered to detect a meaningful result.*

### Baseline Conversion Rate
*Example: "2.5% baseline card application rate."*

### Minimum Detectable Effect (MDE)
*Example: "We want to detect at least a 1.5pp increase."*

### Power Calculation
[State Power and Alpha. Include the output from the calculator (Python, G*Power, etc.).]

- Power: 80%
- Alpha: 0.05

### Final Sample Size Required
*Example: "We require ~9,500 clients per group. At current flow, this will take ~6 weeks."*

---

## 6. Analysis Plan

*Purpose: Lock in the exact method you'll use to measure success and protect the test's validity.*

### Primary Test
[State the specific statistical test.]

*Example: "Two-proportion z-test comparing Treatment A vs Control."*

### Assumptions & Checks
[List assumptions (Independence, normality) and plan for fallbacks (e.g., Mann-Whitney U).]

### Confidence Intervals
*Example: "Report 95% CI for the lift."*

### Multiple Testing Adjustment (if >1 group)
*Example: "Apply Bonferroni for 2 comparisons."*

### Subgroup Analysis (if applicable)
[List pre-specified subgroups.]

*Example: "Effect by digital savviness quartile."*

---

## 7. Randomization & Quality Checks

*Purpose: Prove your test is valid before launch and monitor throughout.*

### Sample Ratio Mismatch (SRM) Test
[Describe plan and trigger.]

*Example: "Use Chi-square test weekly to detect allocation imbalance. Trigger if p < 0.01."*

### Covariate Balance
[Describe how you will check for balance on key features.]

*Example: "Use standardized mean difference (SMD) across key features and visualize with histograms."*

### Monitoring
*Example: "Weekly dashboard to monitor SRM, conversion lag, and bounce rate anomalies."*

---

## 8. Risks & Mitigation Plan

*Purpose: Anticipate problems and show you're ready for them.*

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SRM due to override logic | Medium | High | SRM alerts + override audit |
| Control exposed to treatment | Low | High | Channel segregation rules enforced |
| Data lag >3 days | Medium | Medium | 1-week buffer on final readout |
| [Add other potential risks] | | | |

---

## 9. Final Decision Path

*Purpose: Clearly identify who can stop, modify, or declare winners.*

- **Test Owner:** [Name]
- **Weekly Monitoring By:** [Name/Team]
- **Change Approval By:** [Name/Committee]
- **Final Decision Authority:** [Name/Committee]

---

## 10. Appendix

- [Power calculation screenshots]
- [SQL logic for eligibility]
- [Randomization script or bucket logic]
- [Data dictionary]
- [SRM code]

---

*Document: Experiment Design Report Template*
*Version: v1.0*
