# Vintage Curves Automation: Team Demo Speech (Version 2)

> **Date:** Tuesday Demo
> **Duration:** ~18-20 minutes
> **Audience:** Mixed - peers + directors
> **Generated:** 2026-01-26
> **Version:** 2 - Added execution details and next steps

---

## Full Spoken Delivery (~18-20 minutes)

---

[Walk to front of room, make eye contact, settle]

Hi everyone. Thanks for being here.

[pause]

Roy asked me to take leadership on vintage automation. So today I want to show you what I built... and more importantly, where it goes from here.

[pause]

Let me start with a confession. When I first looked at vintage curves two years ago, I thought it was a reporting problem. Pull some data, make some charts, move on.

I was wrong.

[pause]

Vintage curves is an *ecosystem* problem. And the reason we keep rebuilding the same analysis for every campaign... is because we've been solving it at the wrong level.

[slight pause]

So here's what I'm going to walk you through today. First, the architecture—how the pieces fit together. Then, what's actually built and running right now. And finally—and this is where I need your input—the decisions that will shape what happens next.

[pause]

---

### The Architecture

[move to diagram or screen]

Let me show you how this works.

The engine has four layers. And the key insight—the thing that makes this different from what we've done before—is that each layer is independent.

[point to each layer as you name it]

At the foundation, you have **Experiment Metadata**. This is where Roy's Super Fact Layer lives. Campaign IDs, treatment assignments, the structural data that tells us what we're measuring.

Above that, **Campaign Metadata**. Timing windows. Cohort definitions. The specific parameters for each experiment.

Then **Success Definitions**. What does "success" mean for this campaign? A conversion? An engagement? A retention event? This is where Daniel's Success Library will eventually plug in.

And at the top, **Client Journey**. The actual behavioral data. When did someone open an email? Make a purchase? Drop off?

[pause]

Now here's what matters.

[gesture to the engine layer]

The engine core sits *beneath* all of this. It's layer-agnostic. It doesn't care where the data comes from. It takes whatever you feed it and calculates the curves.

[pause]

Why does that matter?

Because it means as each layer matures—as Roy's foundation expands, as Daniel builds out the Success Library, as Akash develops the repository—the engine just... absorbs it. We don't rebuild. We reconnect.

[pause]

---

### The Maturity Model

Now, I want to be honest about where we are.

[hold up one finger]

Stage One is where we are today. And Stage One is intentionally simple. Success definitions are hardcoded. Campaign parameters are hardcoded. I can run an analysis, but I have to touch the code for each new campaign.

That was a deliberate choice. I wanted a working system first. Something that actually produces output. Not a perfect architecture on a whiteboard that never runs.

[pause]

[hold up two fingers]

Stage Two is where we connect to libraries. Daniel's Success Library. Akash's GitHub repository. Instead of hardcoding success definitions, we pull them dynamically. Instead of hardcoding campaign parameters, we query them.

[hold up three fingers]

Stage Three is full automation. Curated data layers. Self-service. Someone requests a vintage analysis, and it just... runs.

[pause]

But here's the thing I want you to see.

[lean forward slightly]

Each campaign we run in Stage One... makes Stage Two easier. The success definitions I'm hardcoding today? They become the seed data for Daniel's library. The campaign parameters I'm configuring? They become the schema for the catalog.

Nothing is throwaway work. Every campaign enriches the ecosystem.

[pause]

That's the virtuous cycle. And that's why I built it this way.

[pause]

---

### What's Actually Built

[shift to concrete mode]

Okay. Let me get specific about what exists right now. Because "I built something" is easy to say. Let me show you what that actually means.

[count on fingers or reference list]

**The engine is built and running.** Core calculation functions, confidence intervals, all the math—done and tested.

**Six pilot campaigns are live.** VCN, VDA, VDT, VUI, VUT, VAW. Real data. Real curves. Real output.

[pause]

**We have two output tracks.**

Track A goes to CIDM—enterprise integration, standardized data products.

Track B is in-house visualization. And that dashboard? It's deployed. HTML files generated. You can see the curves today.

[pause]

So when I say "Phase One is complete"... I mean we have a working system producing real analysis for real campaigns.

[let that land]

---

### What's Next: The Immediate Priorities

[transition to forward-looking]

Now let me tell you what's on deck. Not someday. Not eventually. The actual next steps.

[tick through these with purpose]

**Success Library setup.** We need to stand up the GitHub repository for success definitions. That's the bridge to Stage Two.

**Semantic Catalog schema.** How do we organize campaign metadata so it's queryable? That design work needs to happen.

**CIDM alignment.** I need to meet with the CIDM team to make sure Track A is pointed in the right direction.

**Refresh process documentation.** Track B works, but the "how to refresh" workflow isn't documented yet. That's a gap.

[pause]

**Campaign module enhancement.** We need to add a measurement_period field. Right now I'm handling that manually. It should be in the data.

**Enrichment catalog.** What additional data do we want to layer onto the curves? Segment breakdowns? Channel attribution? That catalog needs to be designed.

[pause]

Those are the next steps. Concrete. Actionable. I can start on all of them this week.

---

### What's Next: Stage Two and Beyond

[slightly longer time horizon]

Looking further out... Stage Two looks like this.

Connect the Campaign Module to MM v2. Pull success codes dynamically from GitHub instead of hardcoding. Add secondary and tertiary success metrics—not just primary conversion, but the supporting behaviors.

Email engagement curves. Segment breakdowns in the output. Automate the Track A pipeline so CIDM integration doesn't require manual handoffs.

[pause]

That's the roadmap. Phase One is done. Phase Two connects to the libraries. Phase Three is self-service.

---

### Where I Need Your Input

[slow down here—this is the collaboration invitation]

Now. Here's where I need help from this room.

[pause]

There are three decision areas that will shape what happens next. And I don't think these are decisions I should make alone.

[hold up one finger]

**First: Refresh cadence.**

How often should these curves update? Daily? Weekly? Monthly? Who triggers a refresh—is it automated, or does someone request it?

I have opinions, but this affects how people consume the data. So I want to hear what makes sense for how you'd actually use this.

[pause]

[hold up two fingers]

**Second: Metric prioritization.**

Right now we're running primary success metrics. Conversions, mainly. But what secondary metrics matter? Which engagement signals should we track? What segment breakdowns would actually be useful?

I can build the capability to add these. What I need to know is which ones are worth the investment.

[pause]

[hold up three fingers]

**Third: Track strategy.**

We have two output tracks. CIDM enterprise, and in-house visualization. Right now I'm running them in parallel. But eventually... does Track A take over? Does Track B sunset? Do they serve different audiences permanently?

I need to understand how this fits into the broader data product strategy.

[pause]

---

### Closing

[bring it home]

So. Let me summarize.

The architecture is designed for growth. Four independent layers. Engine that doesn't care where the data comes from. Each layer can mature at its own pace.

Phase One is complete. Six campaigns. Working engine. Dashboard deployed.

Phase Two connects to the libraries Roy, Daniel, and Akash are building. The foundation they've laid is what makes this possible.

[pause]

And I have a clear set of next steps I can execute on immediately... once we align on those three decision areas.

[pause]

[look around room]

So. What questions do you have?

[pause]

And specifically—on refresh cadence, metric prioritization, and track strategy—what am I missing? What concerns do you have that I haven't addressed?

[pause]

The floor is yours.

[step back, open posture, ready for Q&A]

---

## Talking Points Summary

1. **Roy asked me to lead; here's what I built** — working system, not theory
2. **Four independent layers** — each matures at its own pace, engine absorbs changes
3. **Stage One intentionally simple** — working system first, perfect architecture later
4. **Virtuous cycle** — every campaign enriches the ecosystem
5. **Concrete progress** — 6 campaigns, CI calculation, dashboard deployed
6. **Clear next steps** — Success Library, CIDM alignment, documentation gaps
7. **Three decisions need input** — refresh cadence, metric priorities, track strategy

---

## The One Thing

**If they remember nothing else:**

> "The engine is layer-agnostic. As our data foundations mature, the engine absorbs them. Nothing we build today becomes throwaway work."

---

## Anticipated Hard Questions

### Q1: "Why hardcode success definitions if we're building a Success Library anyway?"

**Response:**
"Fair question. The honest answer is: I needed to ship something that works. If I waited for every library to be built before starting, we'd still be planning. The hardcoded definitions I'm using today become seed data for Daniel's library tomorrow. They're not throwaway—they're the first entries in the catalog. Stage One was always meant to be scaffolding, not permanent architecture."

---

### Q2: "How does this connect to what already exists? Are we duplicating effort?"

**Response:**
"This is designed specifically to *not* duplicate. Roy's Super Fact Layer is the foundation for Experiment Metadata—I'm building on it, not beside it. Daniel's Success Library slots directly into the Success Definitions layer. Akash's repository gives us version control for the configurations. I've tried to design this as a consumer of what's being built, not a competitor to it. If there's overlap I'm not seeing, I want to know—that's exactly the kind of input that would change my next steps."

---

### Q3: "What happens if priorities shift? Is this work wasted if we pivot?"

**Response:**
"That's why the layer-agnostic design matters. If priorities shift on which campaigns to analyze—fine, we point it at different data. If success metrics change—fine, we update the definitions. The engine itself doesn't care. The only way this work gets wasted is if we decide vintage analysis itself isn't valuable. And if that happens... we have bigger questions to answer than my architecture choices."

---

## Delivery Notes

| Aspect | Guidance |
|--------|----------|
| **Total time** | ~18 minutes spoken, leaves 2+ for Q&A |
| **Pace** | Slow on architecture (let it land). Faster through "what's built" checklist. |
| **Energy shift** | Collaborative on "decisions pending" - asking for partnership, not permission |
| **Watch for** | Nodding at specific decision areas - cue for Q&A focus |
| **If time short** | Cut Stage Two/Beyond section. Immediate priorities + pending decisions matter more. |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-01-26 | Initial speech from coaching synthesis |
| v2 | 2026-01-26 | Added execution details, next steps, pending decisions from NEXT_STEPS.drawio |

---

*Generated by Writer agent based on POLITICAL_CONTEXT.md, NARRATIVE_SKELETON.md, VINTAGE_ENGINE_ARCHITECTURE.md, NEXT_STEPS.drawio, and coaching rounds (Maverick + Sentinel).*
