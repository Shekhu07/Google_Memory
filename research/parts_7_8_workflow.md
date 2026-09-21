# Parts 7, 8 and the workflow slide

Written 21 Sep against the brief, not the derived plans. Every number here is
traceable to `PROGRESS.md` or the deployed code; nothing is asserted.

Three deck slides come out of this document:

| Deck slide | Source |
|---|---|
| How the discovery engine works | §3 below — a **required** deliverable, not optional |
| Success metrics | §1 |
| Risks and limitations | §2 |

---

## 1. Part 7 — Define success

> *"Define appropriate leading and diagnostic metrics for your solution. Your final metric
> framework should reflect the solution you actually build."*

That last sentence is the constraint that matters. The metric framework in Plan 2 §5 was written
before the MVP existed and still contains a **Recovery** term. **The MVP does not ship recovery** —
stages 2 and 4 were cut because they serve 1.4% and 0.7% of observed failures. A framework claiming
credit for a term the product does not implement would be exactly the CS2 defect.

### 1.1 The outcome metric

**User Retrieval Rate (URR)** — of users who had at least one vague-intent retrieval task in a
28-day window, the share who reached the photo on at least one of them.

```
URR = Expression × [ 1 − (1 − Interpretation × Surfacing × Recognition)^n̄ ]
```

**Recovery is deliberately absent from the shipped model.** Plan 2's version had it. If the survey
returns a materially higher `cannot_refine` than the engine's 0.7%, the term comes back and stage 4
ships — that is written into the plan as a revision, not a surprise.

The unit underneath is a **retrieval task** (one target photo), not a query string, and the A/B
randomises **by user**. Both were corrected on 18 Sep and must not regress again: the concept doc,
its v2 and the wireframe have each reintroduced session-level success.

### 1.2 Leading metrics — move first, predict the outcome

Each maps to a term in URR and to an event the MVP already emits.

| Leading metric | URR term | Event | Why it leads |
|---|---|---|---|
| **Entry rate** after a vague query | Expression | `memory_reentry_started` | If people do not enter the surface, nothing downstream can help |
| **Clue-correction rate** — sessions where a chip was edited or removed | Interpretation | `memory_clue_removed`, `memory_recap_edited` | A high rate means the extractor is misreading; it moves before URR does |
| **Episode-open rate** | Surfacing | `episode_opened` | Did any candidate look recognisable enough to enter |
| **Confirm-after-open rate** | Recognition | `retrieval_confirmed` / `episode_opened` | Once inside a moment, can they tell |
| **Time to first episode** (p50, p95) | — | derived | The brief's own framing is retrieval *within five minutes* |

### 1.3 Diagnostic metrics — explain *why* the outcome moved

Leading metrics say something changed. These say what to fix.

| Diagnostic | What it isolates | Already measurable |
|---|---|---|
| **Recall@20 by cue type** | Which memories the index cannot serve | Yes — `engine/demo_eval.py` |
| **Window size distribution** | Filters too tight (zero results) or too loose (222 candidates) | Yes — `apply_filters` |
| **Zero-result rate, and which filter caused it** | Whether *our own* filtering is hiding the photo | Partly — needs the filter attributed |
| **Extraction source mix** (`llm` vs `rules`) | Silent degradation when the Groq cap is hit | Yes — `source` on every `/extract` |
| **Rejection rate by candidate position** | Whether ranking or recognisability is at fault | Yes — `episode_rejected` |
| **Episodes viewed before confirming** | Whether five candidates is the right cap | Yes — event trail |

### 1.4 Guardrails — the metrics that must *not* move

| Guardrail | Why it matters here |
|---|---|
| **False-confirmation rate** — confirmed, then kept searching | **The worst failure this product can produce.** Not finding a photo is annoying; believing you found it and being wrong ends the search while the problem remains |
| Sensitive-query exposure outside the explicit session | Medical and relationship memories; the flow is user-initiated and persists nothing |
| Added p95 latency vs plain search | An encoder cold start must not make ordinary retrieval worse |
| Abandonment before the first episode appears | Measures whether the recap step costs more than it earns |

### 1.5 What is measured today, and what is not

| | Value | Status |
|---|---|---|
| Baseline recall@20 (plain CLIP) | **0.053** | Measured, 30 tasks |
| Shipped extractor recall@20 | **0.612** | Measured, same 30 tasks |
| hit@1 | 0.000 → 0.200 | Measured |
| Seconds to confirm | 30.2s in a walkthrough | Instrumented, n=1 |
| **Every URR term** | — | **Modelled, not measured.** No Google telemetry exists |

**Say the last line on the slide.** Modelled baselines stated plainly are a strength; modelled
baselines presented as measurement are the defect rule C exists to catch.

---

## 2. Part 8 — Risks and mitigation

> *"Think about why your solution might fail. Identify the most important risks for **your specific
> solution** and propose mitigation plans."*

Six risks specific to this build, ordered by how much they would cost if real. Generic AI risks are
omitted deliberately.

### R1 — The headline number is measured on language we wrote the parser against
**0.612 is not a forecast.** The 30 evaluation tasks are synthetic, and the generator phrases vague
time exactly three ways (`"July 2025ish"`, `"sometime in 2024"`, `"around summer 2024"`). The
extractor was written knowing those forms and reuses the generator's own season mapping. Real
phrasing will score lower, possibly much lower.
**Mitigation:** re-score against the real sentences participants use in Part 6 testing, and report
that number beside 0.612 rather than replacing it. Until then, quote 0.612 as *"on these tasks"*.

### R2 — Our own filter can hide the photo
A clue is a **hard gate**. If someone says "last year" and it was fourteen months ago, the target is
excluded and the app says *"no close match"*. **We would be reproducing `not_surfaced` — the 41.7%
failure this product exists to fix — with our own mechanism.**
**Mitigation:** score metadata as a bonus instead of gating on it, so a near-miss clue demotes the
photo rather than deleting it. Until that ships: the widen-one-dimension empty state, and a
zero-result rate with the responsible filter attributed.

### R3 — The index cannot represent three of the cue types
Measured: on `object`, `text_in_image` and `place_named`, **the oracle scores no better than the
baseline** — 0.250, 0.000, 0.000. Perfect clue extraction retrieves nothing, because CLIP cannot
read text inside an image or resolve a place name. `text_in_image` is the fourth most-retained real
cue (12 of 144).
**Mitigation:** OCR or captions over the library, indexed lexically beside the embeddings. Until
then, **state which memories this feature serves and which it does not** rather than implying it
handles all of them.

### R4 — False confirmation
The product asks the user to say *"That's the one"*. A confident wrong answer ends the search and
leaves the person believing the photo is filed where it is not. This is worse than failing to find
it, and no amount of retrieval accuracy compensates.
**Mitigation, already built:** nothing is auto-confirmed, the surrounding sequence stays visible so
the choice is made in context, and *"Not this moment"* costs nothing. **To add:** measure
confirmed-then-continued-searching as a guardrail.

### R5 — We cut recovery on a number that may be wrong
Stages 2 and 4 were cut because `cannot_refine` is 0.7% of 144 episodes. That figure comes from a
corpus that is **86.2% Play Store reviews**, where people rarely narrate what they tried next. The
true rate could be higher, and the audit's `hypotheses` field did lead with H3.
**Mitigation:** the survey measures it directly, and stage 4 is designed and specified — shipping it
is UI work, not rethinking. **On the slide, state the cut *and* the number**: a scoped decision with
a measured reason reads as judgement; an unexplained gap reads as omission.

### R6 — The incumbent may already be enough
Ask Photos is Google's own answer to this problem and is live in India. If it already handles
vague-memory retrieval well, the opportunity is smaller than claimed.
**Mitigation:** the survey's Ask Photos block measures what it already solves and where it still
fails, from users rather than assertion. Verified 21 Sep: Ask Photos has no editable clue chips, no
episode-grouped results and no match explanations, and search returns reverse-chronological results.
**Name Ask Photos on the slide and say what it does well** — silence reads as not having checked.

### Limitations to state plainly (strengths if stated, liabilities if discovered)
- **Play Store is 86.2%** of extracted episodes, against the plan's own 60% per-source cap
- The two models agree only moderately on where retrieval broke (**κ 0.509**) and poorly on which
  hypothesis it supports (**Jaccard 0.347**) — which is exactly why the ranking does not come from
  the engine
- **H4 was never tested**, not overturned: `query_language` returned "en" for all 203 audited posts
- Extraction was **deliberately closed** at 720 of 819 relevant posts, when the budget bound
- The MVP's library is **synthetic metadata over real Creative Commons photographs** — dates, places
  and episodes are invented, and describe nothing real about those images
- The episode-ranking weights are **judgement, not measurement**

---

## 3. The required workflow slide — how the discovery engine works

> Deliverable: *"A 1-slide explanation inside the final deck outlining how the workflow works."*

**Live:** https://retrieval-discovery-engine.vercel.app

### The pipeline, with its real numbers

```
4 public sources                     85,140 posts
   Play Store · App Store · YouTube · Reddit
        │
        ▼  Gate A — keyword filter (regex, free)
                                      5,305 candidates
        │
        ▼  Gate B — relevance screen (gpt-oss-120b, binary)
                                      1,333 labelled → 819 relevant
        │
        ▼  Extraction — fixed schema, exact-quote check
                                      720 episodes → 144 specific attempts
        │
        ▼  Blind audit — qwen3.8-27b, a different model family
                                      203 pairs re-read independently
        │
        ▼  Pre-registered ranking rule
                                      H1–H6 scored, verdicts written
```

### The two things that make it more than summarisation

The brief asks for a workflow that *"goes beyond summarising reviews or performing sentiment
analysis"*. Two design choices do that work:

**1. A fixed schema and a ranking rule registered before the data was seen.** Every post is read
into the same fields — what the person still remembered, what they had forgotten, where retrieval
broke, how it ended. The rule that turns those fields into a hypothesis ranking was written first,
so the engine had to **choose between competing explanations rather than confirm a favourite**.

**2. A second model from a different family, reading blind, allowed to overturn the first.**
It did. The primary model's top-2 moved from [H1, H2] to [H3, H1] after the re-run, and the audit
put H3 first. That disagreement is *the finding* — it is why the hypothesis ranking is not claimed
from the engine, and why `failure_stage` (κ 0.509) decided the verdict rather than `hypotheses`
(Jaccard 0.347).

### What the engine answers — the brief's own four questions

| Question | Answer from 144 specific attempts |
|---|---|
| What kinds of old photos do users struggle to retrieve? | ordinary photos 80 · multiple 26 · video 16 · screenshots 7 |
| What do people actually remember? | **approximate time 40** · object 17 · exact date 14 · text in image 12 |
| What have they forgotten? | **the exact date 37** · which album 29 · the words to search 10 |
| How do they formulate searches when memory is incomplete? | classic search 27 · Ask Photos 10 · both 4 |

**The line the slide should carry:** people remember roughly *when*, and forget the exact date.
That is the one thing the index cannot use — and it is the whole thesis in a sentence.
