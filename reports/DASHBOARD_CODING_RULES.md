# Dashboard Coding Rules

**Purpose:** Guidelines for coding the Vintage Dashboard Pilot
**Created:** 2026-01-24
**Version:** 1.0

---

## Core Principles

1. **Schema-Driven** - All logic derives from the data, never hardcoded values
2. **Campaign-Agnostic** - Must work across any campaign (VCN, VAW, VDA, etc.)
3. **Scalable** - Handle any number of cohorts, test groups, report groups

---

## Rule 1: No Hardcoded Group Names

**NEVER** tie logic to specific codes like TG1, TG7, PSLCRG01.

```javascript
// BAD - Hardcoded
if (group === 'TG1') { ... }
if (group === 'TG7') { lineStyle = 'dotted'; }

// GOOD - Dynamic by index
const lineStyle = LINE_STYLES[index % LINE_STYLES.length];
```

---

## Rule 2: No Hardcoded Cohort Values

**NEVER** assume specific cohort dates.

```javascript
// BAD - Hardcoded
if (cohort === '2025-09') { ... }

// GOOD - Dynamic
const newestCohort = allCohorts[allCohorts.length - 1];
const selectedCohorts = allCohorts.slice(-n);
```

---

## Rule 3: Derive Values from Data

Extract unique values from loaded data, don't assume them.

```javascript
// GOOD
allCohorts = [...new Set(data.map(d => d.COHORT))].sort();
allTestGroups = [...new Set(data.map(d => d.TST_GRP_CD))].sort();
allReportGroups = [...new Set(data.map(d => d.RPT_GRP_CD))].sort();
```

---

## Rule 4: Use Index-Based Assignment

Assign styles, colors, opacity by position, not by name.

```javascript
// Line styles by index
groups.forEach((group, index) => {
    const style = LINE_STYLES[index % LINE_STYLES.length];
});

// Opacity by cohort age (index)
cohorts.forEach((cohort, index) => {
    const opacity = 0.3 + (index / (cohorts.length - 1)) * 0.7;
});
```

---

## Rule 5: Control Group Detection

Don't hardcode control group. Use convention or let user select.

```javascript
// ACCEPTABLE - Convention: last group alphabetically is control
controlGroup = allTestGroups[allTestGroups.length - 1];

// BETTER - User selects control in dropdown
controlGroup = document.getElementById('control-selector').value;
```

---

## Rule 6: Use RBC Color Scheme

Reference the RBC color constants, don't use arbitrary colors.

```javascript
// GOOD - Use RBC object
const RBC = {
    blue: '#0051A5',
    darkBlue: '#003168',
    gray: '#9EA2A2',
    tundra: '#07AFBF',
    sunburst: '#FCA311',
    coolWhite: '#E7EEF1'
};

// Positive lift
cardClass = 'positive';  // Uses tundra (#07AFBF)

// Negative lift
cardClass = 'negative';  // Uses sunburst (#FCA311)
```

---

## Rule 7: Handle Edge Cases

Always check for empty data, missing values.

```javascript
// GOOD
if (!rows.length) return null;
if (cohorts.length === 0) return;
const rate = clients > 0 ? (successes / clients * 100) : 0;
```

---

## Rule 8: Consistent Aggregation Logic

Use the same aggregation pattern everywhere.

```javascript
// Standard aggregation function
function aggregateFinalDay(rows) {
    if (!rows.length) return null;

    const byDay = {};
    rows.forEach(row => {
        if (!byDay[row.DAY]) byDay[row.DAY] = { clients: 0, successes: 0 };
        byDay[row.DAY].clients += row.CLIENT_CNT;
        byDay[row.DAY].successes += row.SUCCESS_CNT;
    });

    const maxDay = Math.max(...Object.keys(byDay).map(Number));
    const final = byDay[maxDay];

    return {
        clients: final.clients,
        successes: final.successes,
        rate: final.clients > 0 ? (final.successes / final.clients * 100) : 0
    };
}
```

---

## Rule 9: Schema Column Names

Use exact column names from v2.2 schema. Don't rename.

| Column | Type | Use |
|--------|------|-----|
| MNE | STRING | Campaign filter |
| COHORT | STRING | Time period |
| TST_GRP_CD | STRING | Test group |
| RPT_GRP_CD | STRING | Report group |
| METRIC | STRING | PRIMARY, SECONDARY, etc. |
| DAY | INTEGER | X-axis |
| CLIENT_CNT | BIGINT | Denominator |
| SUCCESS_CNT | BIGINT | Numerator |
| RATE | DOUBLE | Pre-calculated rate |

---

## Rule 10: Recycle When Exhausted

If more items than styles/colors, recycle using modulo.

```javascript
// 4 line styles, but 6 groups? Recycle.
const style = LINE_STYLES[index % LINE_STYLES.length];

// Works for any number of groups
```

---

## Rule 11: Linked Plot Behavior

Plot 2 inherits from Plot 1. Changes in Plot 1 cascade.

```javascript
function updateAllCharts() {
    updatePlot1();   // Primary selections
    updatePlot2();   // Inherits + adds Report Group filter
    updateKPI();
    updateSummaryTable();
}
```

---

## Rule 12: No Magic Numbers

Define constants at top of script.

```javascript
// GOOD - Named constants
const LINE_STYLES = [
    { dash: [], name: 'solid' },
    { dash: [8, 4], name: 'dashed' },
    { dash: [2, 3], name: 'dotted' },
    { dash: [8, 4, 2, 4], name: 'dashdot' }
];

// BAD - Magic numbers inline
borderDash: [8, 4]  // What does this mean?
```

---

## Checklist Before Committing

- [ ] No hardcoded group names (TG1, TG7, etc.)
- [ ] No hardcoded cohort dates
- [ ] Uses RBC color scheme
- [ ] Handles empty data gracefully
- [ ] Line styles assigned by index
- [ ] Works with 1 cohort or 12 cohorts
- [ ] Works with 2 test groups or 6 test groups
- [ ] Plot 2 inherits from Plot 1

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-24 | Initial rules based on v2.5 learnings |
