# Vintage Curves Automation: Team Demo Speech (Version 4)

> **Date:** Tuesday Demo
> **Duration:** ~15-18 minutes + discussion
> **Audience:** Peers - they know the work, nervous environment, collaborative tone
> **Generated:** 2026-01-26
> **Version:** 4 - User's authentic voice and flow, captures actual presentation style

---

## Full Spoken Delivery

---

**[Walk in, casual, settle]**

Hi guys.

[pause]

Alright. So what I want to share with you today - I want to share with the team the vintage engine that I've been building.

This helps me not only build my curves, but it also integrates with the Super Fact pillars that Roy presented last week.

[pause]

The whole idea here is - yes, of course, help me build my vintage curves - but also integrate this process with the existing framework. The layers that have been built.

I realized... I already have a bunch of campaign codes, a bunch of campaign logic. I'm going to have to find a way to run this monthly, right? So I might as well find a way to create pipes that move information from these layers into the code... and vice versa.

[pause]

I also want to provide information back to those layers. Keep them updated with the new content we generate. Because that's the whole idea of these layers - to become a catalog, a repository of metadata, semantic context.

[pause]

---

### The Architecture

**[Move to diagram]**

So the way I built this - I'm separating it into two different layers.

[pause]

We have the **Context Layer**. This is basically consuming information from the Super Fact pillars.

We have **Experiment Metadata** - who are we testing.

We have **Campaign Metadata** - what are we testing.

We have **Success Library** - how are we testing. How do we define success.

We have **Enrichment Metadata** - if you want to add any layer of contextualization to some of the campaigns.

[pause]

And then we have the final layer - **Client Journey**. This is where we're going to have the email feedback, the channel feedback, any fulfillment options.

[pause]

---

### The Color Coding

**[Point to diagram]**

Now, you can see here - the colors are different for these modules.

The two modules at the very beginning and the very end - these are modules where we don't have to hardcode anything. We just provide the campaign range, and whatever we're getting out of these modules... it doesn't require hardcoding. It doesn't change depending on the campaign.

[pause]

Now, the modules in yellow - they do change depending on the campaign.

Right now, like I said, it's hardcoded variables. I have to go there, write the code for the success metrics. How do I define card acquisition? How do I define wallet provisioning? Provide some semantics. The period that we are measuring. I have to write that down.

Similar to the campaign metadata. Similar to the success library. Similar to the enrichment metadata.

[pause]

---

### The Upgradable Part

**[This is key]**

As you can see here - they're tagged as **upgradable**.

The whole idea is to move away from hardcoding.

[pause]

In the future, as we keep expanding... whether it's the Success Library or our metadata mapping... this engine supports that. Because as we keep adding information to this engine, we keep consolidating logic. We keep consolidating semantic metadata.

The idea is to find a way to transmit this information that we're consolidating into the repository. Find the handshake. Build the pipeline that consumes this information from our work - from the vintage that we're building - and enriches the library.

[pause]

So they're upgradable because...

**Stage Two** - we're going to pull this logic from the repository.

**Stage Three** - we're going to pull data from a curated data set. No longer hardcoding information.

[pause]

---

### The Engine Stays the Same

**[Important point]**

Once we standardize our data - regardless of how they come to be...

If we pull the data via hardcoded variables...

If we pull the campaign data via repository in a future stage...

If we pull the data from a curated data set in our own environment...

The semantic layer is going to be standardized data. Meaning - **the engine will still be the same**.

[pause]

The engine at the end of the day is just calculating the curves. Building the curves. Additional information like lift, confidence level...

We can always expand that once we have a better grasp on the feedback. Currently the Client Journey layer - the email feedback and channel feedback - only contains email. But we want to expand to as many channels as we can have that kind of feedback. Including ONB, ONO...

[pause]

Anyway - I'm diverging a little bit.

[pause]

---

### The Output

**[Move to output section]**

So the engine consumes data from the standardized layer, and then there's the **Output Module**.

This is going to provide us with the variables we need for visualization.

Right now I'm creating the CSV that I download... and then I'm pursuing two different tracks when it comes to delivering this. Making this available for visualization.

[pause]

**Track A** - the official route. This is where we submit to the enterprise-wide dashboard team to ingest. We send to Frank or Kelvin's teams. We're still figuring out the details - how this is going to look. Are we going to have a dedicated vintage dashboard for the team? Are we going to submit this into their own campaign metrics that they're measuring? We don't know yet. That's still to be discussed.

[pause]

**Track B** - meanwhile, what I built is an in-house way for us to see this. An HTML dashboard. I built this mainly to support me - to understand the complexity of the interactions of the variables. How I want to display this. How the groups relate to the channels, to the reporting, to the vintage... There's a lot of variables we can play around with, but we need to be... this helps me visualize.

[pause]

Of course - like you've seen - everything here is a pilot. This still needs to prove itself.

[pause]

---

### Pause for Questions

**[Stop here - genuine pause]**

I'm going to pause here because I've been talking too much already.

[pause]

Let you guys have any questions.

[wait for questions]

Because if not - I want to talk about my favorite part.

[pause]

---

### The Virtuous Cycle

**[After questions, continue]**

I think I already touched on this - but this is the part I'm most excited about.

[pause]

As we keep ingesting data into this engine, into this process... we create this **virtuous cycle** where we enrich our metadata repository.

Whether it's the Success Library or the campaign metadata... I don't know exactly how the updates are going to go. But I feel like right now we can support the library enrichment by providing the codes that we have - the codes we've inserted here.

[pause]

Of course - the handshake and the governance around that is not defined. I don't want to imply anything.

[pause]

But this is the best part.

It not only integrates with the whole process... it supports the Success Library that feeds information to all kinds of measurements that we can do.

And not only that - it makes our life easier. Less reliant on fixed variables in our code. Which - that's not what we want.

[pause]

---

### Wrap Up

**[Bringing it home]**

Yeah. I'm going to stop here.

[pause]

Any questions?

[pause]

So just to wrap it up...

This is what I have right now. You've seen the demo. You've seen what's being built. You've seen the limitations.

This is where I want to go.

[pause]

And this is where I can't decide or do it alone.

[pause]

This is where I would like... any collaboration from everyone. Anyone that can and wants to figure out how we're going to go next.

Whether it's how we're going to provide the handshake with the other metadata teams...

How we're going to automate... I think I heard Joseline has worked with automation, maybe that's something...

[pause]

So I might need help to move to the next stages.

[pause]

---

### Sharing and GitHub

**[Final piece]**

Yeah. And that's it.

I'm going to share this in SharePoint as you guys know.

But also - I think Akash is helping with the GitHub repository for our team. And I want to be able to make this a project that everyone can contribute to. But we also have a centralized, unique source of truth. So people don't branch too far off in the code. And all the improvements are shared for everyone that's using it.

[pause]

So we're going to build this repo and I'm going to share all that.

And I do acknowledge that... you know, making sure the GitHub transition is user-friendly... I understand. Myself, until not so long ago, I wasn't too... I've been using other stuff for a long time. I had to watch classes and tutorials.

[pause]

So we're going to make it easy to work with everyone in a collaborative environment.

[pause]

Yeah. So this is what I have in place.

[pause]

Any questions?

---

## The One Thing

**If they remember nothing else:**

> "As we keep adding information to this engine, we keep consolidating logic and metadata. The engine stays the same - but our libraries get richer. That's the virtuous cycle."

---

## Key Names Mentioned

| Person | Context | How Mentioned |
|--------|---------|---------------|
| Roy | Super Fact Layer foundation | "The pillars Roy presented last week" |
| Daniel | Success Library | Implied in Success Library references |
| Akash | GitHub repository | "Akash is helping with the GitHub repository" |
| Joseline | Automation experience | "I heard Joseline has worked with automation" |
| Frank/Kelvin | CIDM teams | "We send to Frank or Kelvin's teams" |

---

## Delivery Notes

| Aspect | Guidance |
|--------|----------|
| **Tone** | Conversational. This is you talking, not presenting. |
| **Pauses** | Real pauses. Let things land. |
| **"Anyway, I'm diverging"** | Keep this - it's natural, it's you. |
| **Questions pause** | Actually stop. Wait. Don't fill silence. |
| **"I don't want to imply anything"** | Important - shows you're not overstepping on governance. |
| **GitHub acknowledgment** | Humble - you're learning too. Peer-to-peer. |

---

## Structure Summary

1. **Opening** - Share the engine, acknowledge Roy's foundation
2. **Architecture** - Two layers, context + client journey
3. **Color coding** - Blue (stable) vs Yellow (hardcoded, upgradable)
4. **Upgradable concept** - Move away from hardcoding, 3 stages
5. **Engine stability** - Standardized layer means engine doesn't change
6. **Output** - Two tracks (CIDM vs in-house HTML)
7. **[PAUSE FOR QUESTIONS]**
8. **Virtuous cycle** - Your favorite part
9. **Wrap up** - Where you need collaboration
10. **GitHub/sharing** - Akash, collaborative environment

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-01-26 | Initial speech from coaching synthesis |
| v2 | 2026-01-26 | Added execution details, next steps, pending decisions |
| v3 | 2026-01-26 | Removed education, peer-to-peer tone, shorter |
| v4 | 2026-01-26 | User's authentic voice and flow, natural speech patterns |

---

*Written with Writer persona using user's actual walkthrough as source material.*
