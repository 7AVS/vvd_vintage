# Project Instructions

## Trigger: "stakeholder brief"

When the user says **"stakeholder brief"** (or "executive summary" or "high-level"), STOP and ask these questions before building anything:

1. **Who is the audience?** (Director, team, executive, technical peer)
2. **What do they already know?** (Nothing, some context, deep in it)
3. **What's the one thing you want them to walk away with?**
4. **What decision do you need from them?** (Approval, feedback, resources, just awareness)

Then build the right artifact for that audience - slides, 1-pager, or talking points.

Different audience = different output.

---

## Stakeholder Check (Do This First)

Before diving into technical work, always ask:

> "If your director walked in right now and asked 'what are you working on?', what's the 2-sentence answer?"

If the answer isn't clear, stop and clarify before proceeding.

## Project Summary (Keep Updated)

**What:** VVD Vintage Curves Dashboard
**Who cares:** Director, Marketing Analytics leadership
**What they want to see:**
- 6 campaigns (VCN, VDA, VDT, VUI, VUT, VAW)
- Test vs Control comparison (always visible)
- Toggle between Primary/Secondary metrics
- Filter by cohort, segment, channel

**High-level spec:** `docs/VVD_VINTAGE_SPEC.pptx`

## Working Agreement

1. **Start high-level** - Build the 2-slide summary before the code
2. **Stakeholder-first** - What do they need to see? Then how do we build it
3. **Keep it simple** - If it can't be explained in 2 sentences, it's not ready
4. **Check periodically** - "Could you explain this to your director right now?"

---

## Consultant Rule (MANDATORY)

**Before making any code changes or architectural decisions, ALWAYS bring in the Consultant agent to:**
1. Review the proposed change
2. Challenge the approach - ask "is this necessary?" and "is there a simpler way?"
3. Verify the reasoning is sound

**Process:**
1. User identifies issue or request
2. I propose a solution
3. **Consultant reviews and challenges** (do NOT skip this)
4. User approves
5. Then implement

**Do NOT:**
- Make changes without Consultant verification
- Invent justifications for things I don't actually know
- Wait for user to ask for Consultant - bring them in proactively

If I ever skip this step, the user should say "where's the Consultant?" and I must stop and get their input.

---

## VizStrategist Rule (MANDATORY for Visualization)

**Whenever the conversation touches ANY of these topics, ALWAYS bring in the VizStrategist agent:**
- Dashboard layout or design
- Chart/plot selection or styling
- Output file structure that affects visualization
- Engine calculations that determine what can be visualized
- Color schemes, legends, axes, labels
- Presentation of metrics (rates, lifts, confidence intervals)
- Comparison views (Test vs Control, cohort vs cohort)

**What VizStrategist does:**
1. Challenges proposed approaches with counterarguments
2. Provides pros AND cons for every design decision
3. Searches for real-world examples and best practices
4. Recommends evidence-based approaches (Tufte, Few, Cairo, etc.)
5. Asks "What decision should this visualization help someone make?"

**Do NOT:**
- Finalize any visualization design without VizStrategist review
- Accept aesthetic choices that sacrifice clarity
- Skip the "what's the business question?" check

If I ever skip this step for visualization work, the user should say "where's the VizStrategist?" and I must stop and get their input.

---

## Current Status

- [x] High-level campaign inventory created
- [x] Dashboard requirements defined
- [ ] Calculation logic for each metric
- [ ] Dashboard prototype

---

## DrawIO Toolkit

**Location:** `tools/drawio_converter/`

**FIRST:** Read `tools/drawio_converter/GUIDE.md` to understand the full toolkit before taking any action.

### Overview

The DrawIO Toolkit has **2 work streams**:

| Work Stream | Purpose | Trigger Phrases |
|-------------|---------|-----------------|
| **CREATE** | Design DrawIO diagrams using brand guidelines | "create a diagram", "design slides for [topic]" |
| **CONVERT** | Transform DrawIO → PowerPoint (native shapes) | "convert [file].drawio to PowerPoint" |

---

### Work Stream 1: CREATE

**When user wants to create/design a DrawIO diagram:**

1. Read `tools/drawio_converter/GUIDE.md` (Part 1: Creating)
2. Read the relevant framework file:
   - Executive audience → `docs/architecture/VISUAL_FRAMEWORK_EXECUTIVE.md`
   - Technical audience → `docs/architecture/VISUAL_FRAMEWORK_TECHNICAL.md`
3. Read `docs/RBC_COLOR_SCHEME.md` for brand colors
4. Create the diagram following the patterns

---

### Work Stream 2: CONVERT

**When user says "convert [file].drawio to PowerPoint":**

Execute these 3 steps in order:

**Step 1: Run DrawIOReadAgent**
```
Task tool:
  subagent_type: "DrawIOReadAgent"
  description: "Parse DrawIO structure"
  prompt: "Parse this file: [path to .drawio file]"
```
Output: `tools/drawio_converter/read_output.json`

**Step 2: Run DrawIOLayoutAgent**
```
Task tool:
  subagent_type: "DrawIOLayoutAgent"
  description: "Calculate PowerPoint layout"
  prompt: "Calculate layout for PowerPoint conversion"
```
Output: `tools/drawio_converter/layout_output.json`

**Step 3: Generate PowerPoint**
```bash
cd tools/drawio_converter && python3 converter.py layout_output.json [output_name].pptx
```

---

### Configuration

Edit `tools/drawio_converter/config.json` to adjust:
- `work_area`: Target dimensions for content
- `spacing`: Gaps between elements
- `text`: Font scaling rules
