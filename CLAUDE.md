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

## Current Status

- [x] High-level campaign inventory created
- [x] Dashboard requirements defined
- [ ] Calculation logic for each metric
- [ ] Dashboard prototype
