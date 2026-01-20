# Experimentation Process v1.2

## 1. Define the Objectives and Hypothesis

### a. Testing goals:
   - i. Primary: ATE – Average Treatment Effect
   - ii. Secondary *(optional)*

### b. Define randomized unit (client, household, account, etc.)

### c. Define Success Criteria (conversion, revenue impact, liability reduction, cost-to-serve, etc.)

### d. State the Null and Alternate Hypothesis
   - i. H₀ = No difference between treatment and control
   - ii. H₁ = NBA treatment produces measurable lift

---

## 2. Details about the experiment:

### a. State the test design type
   - i. Continuous outcome → T-Test
   - ii. Categorical outcome → Chi-Square Test

### b. Draw the graph to visualize the split

### c. Power Analysis to determine the sample size & MDE
   - i. Baseline (Control Response) - Calculate base conversion rate (infer from previous campaign or data)
   - ii. Define/Calculate Minimum Detectable Effect (MDE).
   - iii. Document the calculation steps.

### d. Limitations
   - i. Identify known constraints (population bias, timing, external noise, etc.)

---

## 3. Guardrails

### a. Eligibility Rules
   - i. Review & document eligibility rules

### b. Randomization
   - i. Run-to-split validation
   - ii. Hypothesis testing:
      1. T-test for continuous covariates
      2. Chi-Square for categorical covariates
   - iii. Effect Size Check (for large N)
      1. Cramer-V for Categorical
      2. SMD for continuous

### c. Sample Size Mismatch Check
   - i. If Imbalance Detected - Apply remediation (re-weighting, CUPED, or stratification)

### d. Design Report
   - i. Complete "One-Page Test Charter" for executive visibility

---

## 4. Implementation

### a. Launch with Monitored Execution
   - i. Document the TEST GROUP CODE
   - ii. Ensure population intake matches design assumptions
   - iii. Monitor assignment and treatment delivery integrity in real time

---

## 5. Data Collection & Monitoring

### a. Integrity
   - i. Validate source-of-truth data pipelines
   - ii. Check for missing values, duplicates, late arrivals

### b. Leading Indicators
   - i. Engagement (views, clicks, opens, logins, etc.)

### c. Primary Business Metrics
   - i. Conversion, balances, cross-sell, attrition, etc.

---

## 6. Analysis:

### a. Statistical Inference
   - i. P-value calculation
   - ii. Confidence Interval

### b. Effect Size:
   - i. Lift = Treatment - Control
   - ii. Cohen's d == (Mean_Treatment - Mean_Control) / Pooled_SD

### c. Financial Translation
   - i. Convert lift into incremental revenue, cost savings, liability impact, etc.
   - ii. Aggregate to NIBT contribution

### d. Deeper Analysis
   - i. Segment-based results (who responds, who does not)
   - ii. Causal Inference for high-value or complex programs

---

## 7. Report:

### a. Executive Decision Output
   - i. Quantified incremental NIBT impact (with confidence bounds)

---

*Document: Experimentation Process v1.2*
