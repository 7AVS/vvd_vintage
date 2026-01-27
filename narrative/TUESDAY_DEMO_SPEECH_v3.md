# Vintage Curves Automation: Team Demo Speech (Version 3)

> **Date:** Tuesday Demo
> **Duration:** ~10-12 minutes (more time for discussion)
> **Audience:** Peers + directors - they know the work, they're anxious about roles
> **Generated:** 2026-01-26
> **Version:** 3 - Direct, no education, peer-to-peer tone, collaboration focus

---

## Full Spoken Delivery

---

**[Walk in, settle, no fanfare]**

Hi everyone.

[pause]

Roy asked me to share where I am on vintage automation. I'll keep this tight and leave time for discussion.

[pause]

---

### The Architecture

**[Direct into it - no preamble]**

The engine has four layers. Each one is independent.

Experiment Metadata - who's in the test. This builds on Roy's Super Fact Layer.

Campaign Metadata - what we're measuring. Timing, cohorts, parameters.

Success Definitions - how we calculate it. This is where Daniel's Success Library plugs in.

Client Journey - what customers actually did.

[pause]

The engine core is layer-agnostic. It doesn't care where the data comes from. As each layer matures, the engine absorbs it. No rebuilding.

[pause]

---

### Where We Are

**[Honest, not boastful]**

Right now we're in Stage One. Hardcoded definitions. I touch the code for each campaign.

That's intentional. Working system first. The definitions I'm hardcoding become seed data for the libraries.

Six campaigns are running: VCN, VDA, VDT, VUI, VUT, VAW.

Two output tracks: CIDM enterprise, and an in-house dashboard that's deployed now.

[pause]

---

### What's Next

**[This is where others come in]**

Here's what's next.

[pause]

Success Library setup - standing up the GitHub repo. **This is where the success definitions live long-term. Daniel, I'd want your eyes on how this connects to what you're building.**

Semantic Catalog schema - how we organize campaign metadata. **This needs design work. If anyone's thinking about metadata standards, this is the place.**

CIDM alignment - making sure Track A is pointed right.

Refresh process - Track B works, but the workflow isn't documented.

[pause]

Enrichment catalog - what additional data layers matter? Segments? Channels? **I don't know what breakdowns would actually be useful to people. That's input I need.**

[pause]

---

### Decisions I Can't Make Alone

**[Genuine invitation, not performance]**

Three things I can't decide alone.

[pause]

**Refresh cadence.** How often should this update? Who triggers it? This affects how you'd actually use the output.

**Metric prioritization.** We're running primary metrics. What secondary metrics matter? What engagement signals? I can build the capability - I need to know what's worth it.

**Track strategy.** Two tracks running parallel. Does Track A eventually take over? Does Track B serve a different purpose? I need to understand where this fits.

[pause]

---

### Close

**[Short, open]**

That's where I am.

Phase One works. Phase Two connects to the libraries. The architecture is designed so each piece can evolve independently.

[pause]

What questions do you have? And on those three decision areas - what am I missing?

[pause]

[open posture, step back]

---

## The One Thing

**If they remember nothing else:**

> "The architecture is designed so each piece can evolve independently. As the libraries mature, the engine absorbs them."

---

## Anticipated Questions

### "How does this connect to what I'm working on?"

**Response:** "That's exactly what I want to figure out. The layers are designed to plug into existing work - Roy's Super Fact Layer, Daniel's Success Library, Akash's repo. If you're working on something that touches campaign metadata, success definitions, or client journey data - there's probably a connection point. Let's talk after."

---

### "Who maintains this?"

**Response:** "Right now, me. But the goal is that as we move to Stage Two, the maintenance shifts to the libraries themselves. Update a success definition in Daniel's library, and the engine picks it up. That's the design intent."

---

### "What do you need from us?"

**Response:** "Input on those three decision areas - refresh cadence, metric priorities, track strategy. And honestly, if you see overlap with what you're doing, or gaps I'm not seeing, I want to know. I'm building this from Vancouver - I don't have the hallway context."

---

## Delivery Notes

| Aspect | Guidance |
|--------|----------|
| **Total time** | ~10-12 minutes. Leaves room for real discussion. |
| **No education** | They know vintage curves. Zero explanation of basics. |
| **No showboating** | State facts, don't celebrate them. |
| **Named collaboration** | Call out Daniel directly. Open invitations for others. |
| **Tone** | Peer-to-peer. You're sharing status, not presenting an achievement. |
| **Body language** | Open. Not defensive. Genuinely want input. |
| **If silence** | Let it sit. Don't fill it nervously. |

---

## Key Differences from v2

| Element | v2 | v3 |
|---------|----|----|
| Opening | "Let me start with a confession..." | Direct: "Roy asked me to share where I am" |
| Education | Explained ecosystem problem | Removed - they know |
| Tone | Presenter energy | Peer-to-peer, status update |
| Length | ~18 minutes | ~10-12 minutes |
| Collaboration | Invited at the end | Woven throughout with names |
| Energy | Building to insight | Flat, factual, open |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-01-26 | Initial speech from coaching synthesis |
| v2 | 2026-01-26 | Added execution details, next steps, pending decisions |
| v3 | 2026-01-26 | Removed education, peer-to-peer tone, shorter, collaboration focus |

---

*Written with Writer persona (full conversation context) - not subagent.*
