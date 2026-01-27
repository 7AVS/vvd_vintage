# Narrative Skeleton - Tuesday Demo

> **Purpose:** Backbone of the presentation narrative, captured as testimony
> **Tone:** Collaborative but leading. "My take, come join me."

---

## The Opening Frame

This is my approach to vintage curves. I built this because I wanted to start contributing to the Super Fact Layer that Roy built. I wanted to understand how I can help leverage the information we already have in some of the campaigns I've built, in order to feed into the Success Library.

At the same time, I wanted to build a measurement engine that adapts to this whole framework—one that consumes from all the layers, the information, the metadata, and also feeds it back to improve the next queries.

---

## The Engine Architecture

This is my take. I built two different layers in the vintage engine.

As you can see here, they're all somewhat straightforward:
- Pulling data from the Pillars and the Super Fact Layer
- We have the Experiment Campaign Metadata module
- We have the Enrichment module
- We have the Success module
- Then we have the Client Journey

From there, we build everything else.

This is what I wanted to show at a high level—not going to go too deep into the details.

---

## The Standardization Point

Right now this has just the vintage engine, but this is a standardized layer. We can hook up any engine here in the future. Once you leverage the standardized process, you can plug in other measurement needs. That's how I see this when I built it.

---

## The Output

Currently, the outcomes we have are through an output module that works together with the dashboard.

This module adapts according to the visualization needs of each campaign. What it does is not necessarily too customizable—it's very rigid. I tried to write code that is as standard as possible so it can run any campaign.

This output generates two tracks that we are pursuing for how to deliver this information:

**Track A:** The conventional enterprise-wide dashboard through CIDM

**Track B:** The in-house dashboard that I'm building

The in-house dashboard is not supposed to be official outside of the team. This is just for me to help visualize how the curves would look like when the dashboard is ready.

---

## The Why - Success Library Integration

This all initiated because I wanted to be able to leverage the code I already built and give it to the Success Library, so the Success Library can start consuming and cataloging all this logic we have.

Next time someone is going to use this—or even myself in a future campaign—I can leverage that information and start to modularize. We can start getting away from hard-coding variables into our code so we can automate the process.

That is the whole idea. It's still a journey to walk that way.

**Key point:** One of the ideas with this whole framework and project is to stop relying on hard-coded variables and start using metadata information from different tables.

---

## The People (Strategic Acknowledgments)

### Roy
Roy built the Super Fact Layer. I'm framing this as: I am building upon Roy's design. This is the foundation, and I wanted to contribute to what he's already established.

### Daniel
Daniel is working on the Success Library. I don't know exactly how far he's gone into building and designing it, but I know he's been recognized as responsible for it. I wanted to tie his work and his name into this—I wanted to contribute to what Daniel is building.

### Akash
Akash is developing the GitHub repository for our team. We're going to learn how to set this up and distribute it to whoever wants to start contributing, so we can have a centralized version. Everyone contributes to one codebase—no branching off into multiple versions. The idea is to build from here.

---

## The Close

So this is my take on how to build my curves, but at the same time help enrich the Success Library. This way I can shift the reliance from hard-coded variables to metadata-driven code—easier to automate, easier to maintain.

Right now, the next steps: we're setting things up together with Akash.

Glad to have any chats, any meetings to go into more details.

That's it.

---

## Tone Notes

- **Say:** "This is my approach" / "This is my take" / "I built this"
- **Don't say:** "I'm leading this" (let the work speak)
- **Imply:** Come join, collaborate, contribute
- **Acknowledge:** Building on others' work (Roy), contributing to others' efforts (Daniel), working with others (Akash)
