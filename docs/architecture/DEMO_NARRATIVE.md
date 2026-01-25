# Vintage Engine: Inception Demo

**Format:** Speaker notes with narrative flow + bullet point reference
**Duration:** ~30 minutes
**Approach:** Sharing work, gathering feedback, collaborative discussion

---

## Opening (How I'd Say It)

Hey everyone. So I've been working on something and I wanted to share it with you guys and get your thoughts.

You all know we've been doing vintage analysis for a while - that's not new. What I've been working on is a way to consolidate how we do it. Instead of the project-based approach where we rebuild things each time, I wanted to see if we could create something more serialized, more repeatable.

This is based on the framework that [senior directors] have been developing - the SuperFact layers, the metadata foundation, all of that. What I'm showing today is my take on implementing that. It's my approach, and I'm here to share it and see what you guys think.

I'm not here to sell you on a vision. I built something, it works, and I want to walk you through it and hear your feedback. If there's something I'm not seeing, I want to know.

---

## What This Is (And What It Is Not)

**What this is:**
- My take on implementing the vintage measurement framework
- A first pass - proof of concept, not a finished product
- A foundation that depends on metadata work being completed
- Something I built and want to share with the team

**What this is not:**
- A polished, production-ready system
- Complete - there is significant hardcoding and much more to build
- A pitch asking for approval
- The only way to do this - I'm open to feedback and other approaches

**Why I'm sharing now:**
- To show what inception looks like
- To get your input before going further
- To surface blind spots I may not be seeing
- Because your feedback now is more valuable than a "perfect" demo later

---

## What I Built (Narrative)

So here's what I've been doing.

I took the vintage process and tried to organize it into layers - the same layers from the framework. You've got your experiment metadata - who's in the test. Your campaign metadata - what are we measuring. The success library - how do we calculate it. And the client journey - what did customers actually do.

The idea is that these layers separate what changes from campaign to campaign versus what stays the same. Right now, a lot of this is still hardcoded - I'll be honest about that. But the structure is there.

I also started building out the metadata piece - the dictionary, the catalog. This is where we define what each metric actually means, where the data comes from, who owns it. This work is conceptual right now - it's a first pass. But it's the foundation that makes everything else possible.

And then I connected it to VVD. Six campaigns - VCN, VDA, VDT, VUI, VUT, VAW. The engine runs, it produces the vintage curves, and we've got a dashboard to visualize it.

---

## Reference: What's New (Bullet Points)

**The Modular Approach:**
- Organized vintage into layers (Experiment, Campaign, Success, Journey)
- Separates what changes per campaign from what's constant
- Based on the SuperFact framework from leadership
- Goal: make each layer swappable (not fully there yet)

**The Metadata Foundation:**
- Dictionary/catalog defining metrics, sources, ownership
- Exists in separate project, conceptual first pass
- Key dependency for scaling the engine

**Serialized Measurement:**
- Campaigns become configurations, not custom code
- 6 campaigns measured with 4 unique metrics (reuse)
- Campaign 7 becomes easier if metric already exists

---

## What I'll Show You (Narrative)

Let me walk you through what we've got.

First, the vintage curves themselves. You've seen these before - Test vs Control over time, cumulative conversion, lift. What's different is how they were produced. Instead of ad-hoc scripts, this came through the engine framework.

Second, the dashboard. It's an HTML file - interactive, you can explore the curves, filter by cohort, toggle metrics. This is what I'm calling Track B - something we can share on SharePoint right now while Track A with Tableau and CIDM is being worked out.

Third, the metadata structure. This is more conceptual - I'll show you what the dictionary looks like, how we're thinking about organizing metric definitions. This part is early, but it's important because everything depends on it.

---

## Reference: Demo Artifacts (Bullet Points)

| Artifact | What It Is | Status |
|----------|------------|--------|
| Vintage Curves | Test vs Control conversion over time | Working - VVD campaigns measured |
| HTML Dashboard | Interactive visualization, shareable | Working - Track B delivery |
| Metadata Structure | Dictionary/catalog foundation | Conceptual - first pass |

---

## How This Connects to the Team (Narrative)

One thing I want to mention - this isn't just about vintage in isolation.

The metadata work I'm doing connects to what the broader team is building. The dictionary, the semantic definitions - that's a shared foundation. When I define what "card_acquisition" means, that definition should be the same whether we're doing vintage analysis, funnel analysis, or attribution.

So what I'm showing you today is one piece of a bigger picture. The vintage engine is my part. But it depends on and contributes to what everyone else is working on. That's why I wanted to share this - to make sure we're aligned and to see how my work fits with yours.

---

## Where We Are Honestly (Narrative)

Let me be real about where things stand.

The engine works. It produces correct results. We've measured the VVD campaigns and the output looks good.

But there's a lot of hardcoding. The metric definitions, the filters, the paths - a lot of that is still embedded in the code. That's not where we want to be long term.

The metadata piece is conceptual. I've got a first pass, but there's much more work to do there.

And the modular layers - the structure is there, but the swap points aren't fully implemented. You can't just plug in a new metric without touching the code. That's the goal, but we're not there yet.

So this is inception. It's a proof of concept. It shows that the approach works, but it's not production-ready.

---

## Reference: Current State (Bullet Points)

| Aspect | Status | Honest Assessment |
|--------|--------|-------------------|
| Engine code | Functional | Works, produces correct results |
| Hardcoding | High | Many variables embedded in code |
| Metadata catalog | Conceptual | First pass, much work remaining |
| Modular layers | Partial | Structure exists, swap points incomplete |
| Documentation | In progress | Architecture documented, gaps identified |

---

## What I'm Asking (Narrative)

So here's what I'm hoping to get from this.

First, your feedback. I've been heads down in this and I know I have blind spots. If you see something I'm missing, or if something doesn't make sense, I want to hear it.

Second, your input on direction. Is this the right approach? Does it align with what you're working on? Are there dependencies I haven't thought about?

And third, just your thoughts in general. This is a first pass. It's going to evolve. I'd rather course-correct now based on your feedback than keep building in the wrong direction.

I'm not asking for approval or sign-off. I'm sharing what I've done and asking: what do you think?

---

## Reference: The Ask (Bullet Points)

**Feedback:**
- What am I missing?
- What blind spots do you see?
- Does this make sense?

**Input:**
- Does this align with your work?
- Are there dependencies I haven't considered?
- What would you do differently?

**Discussion:**
- This is collaborative, not a pitch
- First pass, open to change
- Your perspective helps

---

## Closing (How I'd Say It)

So that's what I've been working on. The vintage engine - my take on implementing the framework we've been talking about.

It works. It's not finished. There's a lot more to do, especially on the metadata side.

But I wanted to share it with you guys now rather than wait until it's "perfect" - because your input will make it better.

What do you think? What questions do you have? What am I not seeing?

---

## Quick Reference Summary

**What this is:** My implementation of the vintage measurement framework - first pass, proof of concept.

**What's new:** Modular layers, metadata foundation, serialized approach (vs project-based).

**What works:** Engine runs, VVD campaigns measured, dashboard built.

**What's not done:** Hardcoding, metadata still conceptual, swap points incomplete.

**What I'm asking:** Your feedback, your input, your thoughts.

**The approach:** Sharing, not selling. Collaborative, not prescriptive.

---

*"I built something. It works. I want to show you and hear what you think."*
