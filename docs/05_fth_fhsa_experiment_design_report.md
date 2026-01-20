# Experiment Design Report: FTH – FHSA Mortgage Leads Expansion

**Author:** Daniel Chin

**Created:** September 25, 2025  
**Last updated:** October 22, 2025

**Version:** v1.0  
**Audience:** Prepared for: Executive Oversight – [Names if known]  
**Confidentiality:** Internal Document – Do Not Distribute Externally

---

## 1. Executive Summary

### Why are we Testing?

The purpose of this A/B experiment is to determine if, with the modified selection rules, the program will still be as successful at driving funded mortgages. If successful, this campaign will increase the number of mortgages acquired by a minimum of two-fold due to the volume of additional leads. Historically from past data, the expansion universe also has a higher likelihood to make a purchase than the existing targeting rules.

### What is being Tested and measured?

The test is to measure the hypothesized difference in client behaviour in opening a mortgage, through a random assignment of eligible leads and a no contact control to measure absolute lift. If available in sufficient sampling, other segmentations will be looked at.

### What will success look like?

Statistically significant difference (α=0.05 with power ≥0.8) in the number of mortgages funded between the treatment group and the no contact control group.

### How long and how safe?

Observation window will be for 300 days **for 5,000 test leads (more may be included from further expansion)**. To reduce any business risk, the test will require only a subset of the leads deployed to have statistical significance. The half remaining in control will likely redeploy soon after measurement is complete and proven, followed after with a lower control hold back rate.

---

## 2. Strategic Context

### Purpose

Mortgages has three primary campaigns to drive the funnel of mortgage opens: Mortgage Switch, New Mortgage and FHSA. This test will inform if the strategy of relaxing the rules to clients likely to convert (based on historical data) can capture additional incremental mortgages. Each converted account is valued at **$3100**.

---

## 3. Hypothesis & Objectives

### Primary Hypothesis

With the new targeting, the campaign will continue to have influence in their decision on getting a mortgage funded.

**H0:** the mortgage specialist contact does not influence a client's mortgage decision.

**H1:** the mortgage specialist contact does influence a client's mortgage decision.

### Success Criteria

Identification of statistically significant treatment effect at (at α=0.05) with power ≥0.8.

**ATE:** τ = E [Y(MS contact) − Y(no contact)]

### Hypothesis

**Main effect (causal)**

H₀ : τ = 0 vs H₁ : τ ≠ 0

---

## 4. Experiment Design & Assignment

### Design Type

The campaign will be structured as a randomized controlled trial (RCT) or A/B test. To ensure measurement out of the completed experiment, the design will include a 1:1 randomization on campaign eligible clients after all exclusions have been completed. Channel is not a factor here as being call eligible is mandatory for this campaign.

### Randomization Unit

The unit of randomization is at an individual client record (one record per eligible client). Randomization occurs independently during the last step after all exclusions and eligibilities have been applied.

### Eligibility Rules

The eligibility criteria are the following (not exhaustive, all themes captured):

- Enterprise-wide CPC (Marcrit)
- Valid contact and address
- Personal information such as residency, not deceased
- Not FP managed
- Not: Fraudulent, high-risk, write-offs, declined recently, collections, etc.
- Resting last 12 months from any mortgage or credit line campaign contact
- Household resting and deduping

### Treatment Arms

```
                                           ┌─ Action Group (50%) ─┬─ New Expansion (89%)
                                           │                      └─ BAU (94% Maxed) (11%)
Entire Audience ─┬─ >$7,000 Contributions ─┤
                 │    (Targeted)           └─ No Contact Control Group (50%)
                 │
                 └─ <$7,000 Contributions ─┬─ TBC: Model           ┐
                      (Not Targeted)       │  Decile               │ Model Group not
                                           │  (Target)             ├─ in consideration
                                           │                       │ due to waterfall
                                           └─ Not in Model         │ volume <900
                                                (Not Targeted)     ┘
```

*89% and 11% are based on past deployments of 1000 new leads and 125 existing leads*

### Platform & Implementation

Execution is on SAS, leads will be passed to CMENT (mortgage lead deployment system) and mortgage specialists will be managing the leads using Linx/C360.

---

## 5. Sample Size & Power Analysis

### Baseline Conversion Rate

Expected results and control based on last 4 months of FTH results as of April 2025. Control does vary and can be as high as 3-4% a year ago. Business case assumes a 0.5% lift over the existing 2.7% response. Due to the small sample of the existing leads, the measurement of new vs. existing is likely not measurable and not considered success.

#### Aggressive Control Scenario

| Experiment | Treatment (Expected) | Control | Lift |
|------------|---------------------|---------|------|
| Lead vs. No Contact | 3.20% | 0.00% | 3.20% |
| New Lead vs. Existing | 3.20% | 2.70% | 0.50% |

#### Conservative Control Scenario

| Experiment | Treatment (Expected) | Control | Lift |
|------------|---------------------|---------|------|
| Lead vs. No Contact | 4.50% | 4.00% | 0.50% |
| New Lead vs. Existing | 4.50% | 2.70% | 1.80% |

### Minimum Detectable Effect (MDE)

#### Aggressive Control Scenario

| Experiment | MDE | Power | Confidence | Test | Control | Total |
|------------|-----|-------|------------|------|---------|-------|
| Lead vs. No Contact | **0.12%** | 80% | 95% | 5,000 | 5,000 | 10,000 |
| New Lead vs. Existing | **2.24%** | 80% | 95% | 4,500 | 500 | 5,000 |

#### Conservative Control Scenario

| Experiment | MDE | Power | Confidence | Test | Control | Total |
|------------|-----|-------|------------|------|---------|-------|
| Lead vs. No Contact | **1.03%** | 80% | 95% | 5,000 | 5,000 | 10,000 |
| New Lead vs. Existing | **2.24%** | 80% | 95% | 4,500 | 500 | 5,000 |

### Power Calculation

Sample size per arm for a two-proportion z-test:

$$n_1 = \frac{(r + 1) \sigma^2 (Z_{power} + Z_{\alpha/2})^2}{r \cdot difference^2}$$

Where:
- **n1** = Required sample size
- **R** = Ratio of the larger sample size to the smaller sample size
- **σ** = The variance of the average proportion
- **Z power:** 80% power = Z=0.84
- **Zα/2:** Significance level; α=0.05 (95% Significance)

**Difference/MDE = 1.03%**

### Final Sample Size Required

**7,223**

---

## 6. Analysis Plan

### Primary Test

Two proportion z-test (Test vs Control).

### Assumptions & Checks

Independent samples, sufficient sample size for normal approximation.

### Confidence Intervals

- α=0.05 (95% Significance)
- α=0.10 (90% Significance)
- α=0.20 (80% Significance)

### Multiple Testing Adjustments

*[To be specified if applicable]*

### Subgroup Analysis (if applicable)

*[To be specified if applicable]*

---

## 7. Randomization & Quality Checks

### Sample Ratio Mismatch (SRM) Test (2 waves in)

| Test Group | Observed | Expected | Difference | Difference Squared | Difference Squared / Expected | Results |
|------------|----------|----------|------------|-------------------|------------------------------|---------|
| Test | 2,252 | 2,250 | 2 | 4 | 0 | |
| Control | 2,248 | 2,250 | (2) | 4 | 0 | |
| **Total:** | | | | **0** | **SRM Does not Exist** | |

### Covariate Balance

The Standardized Mean Difference (SMD) test completed on several continuous indicators.

All SMD expectation under 0.1 so that impact on outcome is small.

| Variable | SMD | Result |
|----------|-----|--------|
| age | -0.009313 | pass |
| tenure_rbc_years | 0.036552 | pass |
| actv_prod_cnt | 0.018281 | pass |

Cramers V also passed for categorical covariates.

| Variable | Chi-square Statistic | P-value | Degrees of Freedom | Cramer's V | Result |
|----------|---------------------|---------|-------------------|------------|--------|
| age_rng | 3.042499 | 0.693434 | 5 | 0.017384 | Pass |
| credit_score_rng | 5.487021 | 0.139417 | 3 | 0.023620 | Pass |
| digital_trans_ind | 0.868835 | 0.351278 | 1 | 0.009290 | Pass |
| new_imgrnt_seg_cd | 0.071884 | 0.788614 | 1 | 0.002672 | Pass |
| subcntry_cd | 8.575562 | 0.804191 | 13 | 0.029185 | Pass |

*\*python code in sharepoint*

### Monitoring

TBD – metric logic being built (on hold due to access issues), will have regular readouts.

---

## 8. Risk & Mitigation Plan

**Risks:** Control response may come high or low, real estate market dependence on seasonality and hot/cool market; SRM; campaign delivery issues.

**Mitigation:** utilize 50/50 ratio to decrease measurement MDE and time to detect lift, reserve the 50% control group for deployment in the following year for the spring/summer market; monitor SRM for each deployment.

---

## 9. Final Decision Path

- Test Owner
- Weekly Monitoring
- Change Approval
- Final decision

---

*Document: FTH – FHSA Mortgage Leads Expansion Experiment Design Report*
*Author: Daniel Chin*
*Version: v1.0*
