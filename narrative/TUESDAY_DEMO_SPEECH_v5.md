# Vintage Curves Automation: Team Demo Speech (Version 5)

> **Date:** Tuesday Demo
> **Duration:** ~15-18 minutes + discussion
> **Audience:** Peers + directors
> **Generated:** 2026-01-26
> **Version:** 5 - Data Assets framing, more structured, strategic positioning

---

## Full Spoken Delivery

---

**[Walk in, settle]**

Hi guys.

[pause]

So I want to share with the team something I've been building. It's a vintage engine - but I want to frame it a little differently.

[pause]

Yes, it produces curves. But what it's really doing is **collecting data assets**.

[pause]

Every time we run a campaign through this engine, we're not just getting a vintage curve. We're consolidating success definitions. We're documenting campaign metadata. We're capturing semantic context that can be reused.

The curves are one output. The data assets are the long-term value.

[pause]

---

### Part 1: Why Data Assets

**[Setting the frame]**

Here's the problem I was trying to solve.

I have a bunch of campaign codes. A bunch of campaign logic. I need to run this monthly. And every time I do it, I'm re-writing the same definitions. Re-documenting the same metadata.

[pause]

So I thought - if I'm going to do this work anyway, I might as well capture it in a way that feeds back into our repositories.

This engine integrates with Roy's Super Fact pillars. It's designed to both **consume from** and **contribute to** the metadata layers we're building as a team.

[pause]

The vintage curves are what I need for my work. The data assets are what we all benefit from.

[pause]

---

### Part 2: The Architecture

**[Move to diagram]**

Let me walk you through the structure.

[pause]

**Layer 1: Context Layer**

This layer consumes from our existing data assets - the Super Fact pillars.

- **Experiment Metadata** - Who are we testing? This comes from existing sources. No hardcoding needed.

- **Campaign Metadata** - What are we testing? Campaign parameters, timing, cohorts. Currently hardcoded - but this becomes a data asset we can reuse.

- **Success Definitions** - How do we measure success? Card acquisition, wallet provisioning, whatever the metric. Currently hardcoded - but these definitions become assets for the Success Library.

- **Enrichment Metadata** - Optional segmentation. Tenure, region, profitability. Future capability.

[pause]

**Layer 2: Client Journey**

- **Email Feedback** - Opens, clicks, engagement signals.
- **Channel Feedback** - Currently email only. Expandable to ONB, ONO, other channels.
- **Fulfillment** - Was the contact delivered?

This layer also comes from existing sources. No hardcoding needed.

[pause]

---

### Part 3: The Data Asset Opportunity

**[This is the key reframe]**

Now look at the color coding.

[pause]

The modules in **blue** - Experiment Metadata, Client Journey - these pull from existing data. Stable. No campaign-specific hardcoding.

The modules in **yellow** - Campaign Metadata, Success Definitions, Enrichment - these are currently hardcoded. I write the logic for each campaign.

[pause]

But here's the opportunity.

**Every yellow module is a data asset waiting to be captured.**

[pause]

When I hardcode "card acquisition means X filter on Y table" - that's a success definition. That belongs in the Success Library.

When I hardcode "VCN measures activation over 90 days" - that's campaign metadata. That belongs in the metadata catalog.

[pause]

Right now I'm hardcoding because the repositories aren't ready yet. But the work isn't throwaway.

**Stage 1** - I hardcode. The engine runs. I get my curves. But I'm also documenting the logic.

**Stage 2** - We extract those definitions into the Success Library. The engine pulls from the library instead of hardcoded values. Now it's a shared asset.

**Stage 3** - Data engineering creates curated data sets. The engine pulls from those. Fully automated.

[pause]

The engine stays the same across all three stages. What changes is where the data assets live.

[pause]

---

### Part 4: What's Built

**[Concrete status]**

Let me show you what exists today.

[pause]

**Six campaigns running:** VCN, VDA, VDT, VUI, VUT, VAW.

**Four success metrics defined:** Card acquisition, card activation, card usage, wallet provisioning.

**Data assets captured:** Each of those metrics has documented logic. Filter conditions. Table references. Business rules.

[pause]

**Two output tracks:**

**Track A** - Enterprise dashboard. We're working with Frank and Kelvin's teams on how to integrate. Dedicated vintage dashboard or part of existing campaign metrics - still to be decided.

**Track B** - In-house HTML dashboard. I built this to visualize the complexity. How groups relate to channels, to reporting segments, to vintage periods. It's deployed. You can see it now.

[pause]

Both tracks consume the same data. Same source of truth.

[pause]

---

### Pause

**[Stop here]**

I'm going to pause here for questions.

[wait]

Because the next part is what I'm most excited about.

[pause]

---

### Part 5: The Virtuous Cycle

**[After questions]**

Here's why I framed this as data assets.

[pause]

Every campaign we run through this engine creates a virtuous cycle.

[pause]

**Campaign 1** - I define card acquisition. I document the logic. I hardcode it for now. Engine runs. I get curves.

**Campaign 2** - Same metric? I reuse the definition. Zero new work on that asset.

**Campaign 3** - New metric needed? I define it. Document it. Now we have another asset.

[pause]

As we keep running campaigns, we keep consolidating:

- Success definitions
- Campaign metadata
- Business rules
- Semantic context

[pause]

This isn't just producing curves. It's **building a catalog**.

[pause]

The handshake with the Success Library - how we formalize this, the governance - that's not defined yet. I don't want to imply anything about that.

But the work is being captured. The assets are being documented. When the library is ready, we have content to contribute.

[pause]

---

### Part 6: Where I Need Help

**[Collaboration ask]**

So. This is where I am.

[pause]

This is where I can't go alone.

[pause]

**The handshake** - How do we formalize the connection to the Success Library? To the metadata catalog? I need input on governance and process.

**Automation** - I heard Joseline has experience with automation. There's opportunity to schedule and automate the refresh. I could use help thinking through that.

**Track A alignment** - The enterprise dashboard integration needs decisions. Refresh cadence. Data format. Ownership.

**Metric prioritization** - What secondary metrics matter? What segment breakdowns would be useful? I can build the capability - I need to know what's worth capturing as an asset.

[pause]

---

### Part 7: Sharing

**[Final piece]**

I'm going to share all of this on SharePoint.

And Akash is helping set up the GitHub repository for our team. I want this to be a project everyone can contribute to. But with a centralized source of truth - so we don't branch too far off.

[pause]

I'll be honest - the GitHub workflow is a learning curve. I had to watch tutorials myself. We'll make it easy to work with everyone collaboratively.

[pause]

---

### Close

So that's the frame.

Yes, it's a vintage engine. Yes, it produces curves.

But what it's really building is a **data asset catalog**. Success definitions. Campaign metadata. Reusable logic.

The curves are the output. The assets are the value.

[pause]

Questions?

---

## The One Thing

**If they remember nothing else:**

> "The curves are one output. The data assets - success definitions, campaign metadata, documented logic - are the long-term value. Every campaign we run builds the catalog."

---

## Key Reframes in v5

| v4 Frame | v5 Frame |
|----------|----------|
| "Vintage engine that produces curves" | "Data asset collection that also produces curves" |
| "Hardcoded for now" | "Data assets waiting to be captured" |
| "Integrates with Super Fact pillars" | "Consumes from AND contributes to data assets" |
| "Virtuous cycle enriches metadata" | "Virtuous cycle builds a catalog" |
| "I built this" | "This is what we're building together" |

---

## Structure Summary

| Part | Content | Time |
|------|---------|------|
| 1 | Why Data Assets - the frame | 2 min |
| 2 | Architecture - two layers | 3 min |
| 3 | Data Asset Opportunity - yellow modules | 3 min |
| 4 | What's Built - concrete status | 2 min |
| **[PAUSE]** | Questions | 2-3 min |
| 5 | Virtuous Cycle | 3 min |
| 6 | Where I Need Help | 2 min |
| 7 | Sharing / GitHub | 1 min |
| Close | Restate the frame | 1 min |

---

## Delivery Notes

| Aspect | Guidance |
|--------|----------|
| **Key phrase** | "The curves are one output. The data assets are the long-term value." |
| **Repeat** | Use "data assets" throughout - it's the new frame |
| **Tone** | Strategic but accessible. You're not overselling - you're reframing. |
| **Pause placement** | After "data assets waiting to be captured" - let it land |
| **Collaboration** | Frame help-asks as "building assets together" |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-01-26 | Initial speech from coaching synthesis |
| v2 | 2026-01-26 | Added execution details, next steps, pending decisions |
| v3 | 2026-01-26 | Removed education, peer-to-peer tone, shorter |
| v4 | 2026-01-26 | User's authentic voice and flow |
| v5 | 2026-01-26 | Data Assets framing, more structured |

---

*Written with Writer persona - Data Assets strategic reframe.*
