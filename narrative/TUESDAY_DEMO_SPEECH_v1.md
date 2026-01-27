# Demo Presentation: Vintage Curves Engine

> **Date:** Tuesday Demo
> **Duration:** ~18-20 minutes
> **Audience:** Mixed - peers + directors
> **Generated:** 2026-01-26

---

## Full Spoken Delivery

---

**[Enter, settle, make eye contact with the room]**

Hi everyone. Thanks for making time for this.

[pause]

So. Roy asked me to take leadership on vintage automation. Today I want to show you what I've built and where it's going.

[pause]

This is a vintage curves engine. Six campaigns are running through it right now. The architecture is designed to scale. And—this is the part I'm most excited about—the work compounds. I'll show you what I mean by that.

**[shift tone slightly—setting context]**

Before I get into the mechanics, let me frame where this fits.

This engine is built to contribute to Roy's Super Fact Layer foundation and feed into Daniel's Success Library work. It's not a standalone thing. It's meant to plug into the ecosystem we're building as a team.

[pause]

Alright. Let me walk you through the architecture.

---

**[transition—the teaching section begins]**

I think of this as a four-layer model. Each layer answers a specific question.

[pause]

Layer One is Experiment Metadata. This answers: "Who is in the test?" Which customers, which cohorts, test versus control. The fundamental groupings.

Layer Two is Campaign Metadata. This answers: "What are we measuring?" What metrics matter for this particular campaign? And importantly—this layer is upgradable. As our measurement standards evolve, this layer evolves with them.

[pause]

Layer Three is Success Definitions. This answers: "How do we calculate it?" What's the actual logic behind, say, a card acquisition rate? How do we define an upgrade? This layer is both upgradable *and* swappable—meaning different teams could plug in different definitions if they needed to.

Layer Four is the Client Journey. "What did customers actually do?" The transactional data, the behaviors, the outcomes.

[pause]

And then there's the engine core itself. Here's the key design decision: the engine is layer-agnostic. It doesn't care where the data comes from. It just knows how to process whatever those four layers feed it.

**[pause—let this land]**

Why does that matter?

Because it means we can upgrade the data sources without rewriting the engine. The plumbing stays the same even as the water changes.

---

**[transition—maturity stages]**

Now, let me be direct about where we are today versus where we're headed.

I think of this in three stages.

[pause]

Stage One—where we are now—uses hardcoded Python dictionaries. All the version 2.x releases are Stage One. And I want to be clear: this is intentionally simple. I wanted a working system first, something we could actually run campaigns through, before optimizing data sources.

**[slight emphasis]**

The engine being layer-agnostic is what makes Stage Two possible without rewriting Stage One.

[pause]

Stage Two—near-term—pulls from Mnemonic Mapping version two and connects to Daniel's Success Library. This is where the ecosystem integration happens.

Stage Three—the target state—uses pre-curated data sets. Fully automated pipeline.

**[pause]**

Phase One is complete. Phase Two connects to Success Library. Phase Three is the long game.

---

**[transition—the "aha" moment]**

Okay. Here's the part I'm most excited about.

[pause]

I mentioned the work compounds. Let me show you what I mean.

When we onboard a campaign, we're not just running that campaign. We're enriching a shared metadata ecosystem.

[pause]

Campaign One defines what "card acquisition" means. How we calculate it. What the success criteria are.

Campaign Two comes along. Same metric?

**[snap fingers or gesture]**

Zero new work. We reuse the definition.

[pause]

Campaign Three needs a slight variation? We extend the definition, and now that extension is available for Campaign Four, Five, Six.

**[pause—let economics sink in]**

This is a virtuous cycle. Every campaign onboarded makes the next one easier. The metadata gets richer. The reusable definitions grow. Work that took hours the first time takes minutes the fifth time.

That's what I mean when I say the architecture scales and the work compounds. It's not just that it *can* handle more campaigns—it gets *better* at handling them.

---

**[transition—standardization]**

One more architectural point, then I'll show you what's actually built.

[pause]

This is a standardized layer.

What I mean is: the four-layer model and the engine core? They're not vintage-specific. You could hook up a different engine in the future—not just vintage curves. The interface is the same. The data contracts are the same.

**[measured tone]**

I'm not overselling this. That's not the immediate priority. But the design accommodates it. If we need it later, the foundation is there.

---

**[transition—tangible output]**

Alright. Let's talk about what's actually running today.

[pause]

Six campaigns are configured and flowing through the engine: VCN, VDA, VDT, VUI, VUT, and VAW.

Four success metrics are defined and calculating.

The engine produces output. The dashboard renders it.

[pause]

On output: we have two tracks. One feeds CIDM for the enterprise dashboard—that's the official, visible layer. The other is an in-house visualization I built for the team, so we can see what's happening in more detail, iterate faster, and not wait on the enterprise pipeline for every question.

**[brief pause]**

Both tracks run off the same engine. Same source of truth, two views.

---

**[transition—acknowledgments, woven naturally]**

I want to be clear about the shoulders this stands on.

[pause]

Roy's Super Fact Layer foundation is what makes this possible. That's the bedrock.

Daniel's work on the Success Library is where Stage Two connects. The definitions I'm hardcoding today will pull from that library tomorrow.

And Akash's work on the GitHub repository—that's the infrastructure that lets this actually deploy and version properly.

[pause]

This engine is my contribution to a larger effort. The value multiplies when these pieces connect.

---

**[transition—the close, slightly slower pace]**

So.

[pause]

Where does this leave us?

[pause]

Phase One is complete. Six campaigns configured, engine functional, output flowing.

Phase Two connects to the Success Library and Mnemonic Mapping. That integration is the next milestone.

Phase Three is the fully automated pipeline. Pre-curated data, minimal manual touchpoints.

**[pause]**

I'll be scheduling deeper technical sessions for anyone who wants to get into the weeds—the actual code structure, the calculation logic, the data contracts. Today is the architecture overview. Those sessions are the implementation details.

[pause]

I have a question for the group.

**[direct, not defensive]**

What would you need to see to feel confident moving to Phase Two?

[pause—wait for responses or let silence sit]

---

**[if no immediate responses, pivot]**

Another way to ask it: What am I missing? What concerns do you have that I haven't addressed?

[pause—genuine openness]

I'm in Vancouver, so I don't get the hallway conversations. If something isn't landing right, I'd rather hear it now than find out later.

**[pause]**

Okay. I'll stop there.

Happy to go deeper on any piece of this. Architecture, the specific campaigns, the calculation logic, the dashboard itself—whatever's useful.

What questions do you have?

---

## The One Thing

**If they remember nothing else:**

> The engine is layer-agnostic and the work compounds—every campaign onboarded makes the next one easier. Phase One is complete with six campaigns running.

---

## Anticipated Hard Questions

### 1. "Why hardcoded dictionaries? That seems fragile for production."

**Response:** "Fair question. Stage One is intentionally simple—I wanted a working system before optimizing data sources. The key is that the engine itself doesn't care where the data comes from. It's layer-agnostic. So when we move to Stage Two and pull from Success Library, we're swapping the data source, not rewriting the engine. The architecture accommodates the upgrade. I'd rather have something running that we can improve than something elegant that's still theoretical."

---

### 2. "How does this connect to what Daniel/Akash are building? Are we duplicating work?"

**Response:** "We're not duplicating—we're building to connect. Daniel's Success Library is where my Stage Two pulls definitions from. Right now I'm hardcoding those definitions as a placeholder until that integration is ready. Akash's GitHub work is the deployment infrastructure. My engine is the calculation layer that sits between the data sources and the output. Think of it as: Daniel defines *what* to measure, I calculate *the result*, Akash makes sure it *deploys*. Three pieces, one pipeline."

---

### 3. "What happens if priorities change and we need to pivot away from vintage curves?"

**Response:** "The four-layer model and engine core are standardized—they're not vintage-specific. If we needed to run a different type of analysis through the same infrastructure, the interface stays the same. That said, I'm not overselling that. The immediate value is vintage curves. The extensibility is a design decision, not a promise. It's there if we need it; it's not the reason to invest."

---

## Delivery Notes Summary

| Aspect | Guidance |
|--------|----------|
| **Total time** | ~18 minutes (leaves room for questions) |
| **Key pauses** | After layer-agnostic reveal, after virtuous cycle, before closing question |
| **Tone shifts** | Teaching mode → enthusiasm → measured honesty → direct close |
| **Physical** | Eye contact when asking questions. Let silence sit. |
| **Vancouver line** | Once, briefly, in context of wanting feedback. Don't dwell. |

---

## Coaching Sources

This speech synthesizes guidance from:
- **Maverick (Bold):** Own what you built, Roy anchor opening, own the roadmap, lean into virtuous cycle economics
- **Sentinel (Measured):** Weave credits into narrative, create space for concerns, honest about Stage 1 simplicity, directed feedback questions

---

*Generated by Writer agent based on POLITICAL_CONTEXT.md, NARRATIVE_SKELETON.md, and coaching rounds.*
