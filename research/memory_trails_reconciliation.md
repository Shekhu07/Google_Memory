# Memory Trails — reconciliation with the evidence

**Status: CHOSEN and built (21 Sep).** The 26 Sep lock was removed; the verdicts are written in
`implementation_plan.md` §5 and the core module is **episode-first retrieval (H1/H2)**, deployed at
https://memory-trails-demo.vercel.app. Stages 2 and 4 are **cut**, not held. This document reconciles the MVP concept files with what
the engine actually measured, so the deck can show the evidence *led* to a design rather than the
design arriving first.

**Authoritative version: `Google_Photos_—_Memory_Trails-2.pdf` (v2, 20 Sep 18:09).** It supersedes
`Google_Photos_—_Memory_Trails.pdf` (v1). `…Additional_MVP_Ideas…pdf` and
`google-photos-memory-trails.html` are still v1-era. **§1 below was rewritten on 20 Sep after v2
landed** — the v1 critique it replaced is preserved in the note at the end of §1, because the deck
may want to show the concept moving toward the evidence rather than pretend it started there.

---

## 1. How v2's named failures map to the measured ones

v2 rewrote all three failure modes. **Two of the three moved toward what the engine measured.**

| # | v1 wording | v2 wording | Engine field | Observed (of 144) |
|---|---|---|---|---|
| 1 | "The search box asks for exactness too early" | "The library has no memory-based **re-entry point**" | `cannot_express` → *partly* `system_misunderstood` | 1.4% → *straddles 35.4%* |
| 2 | "no useful recovery path after a **miss**" | "no useful recovery path after a **near miss**" | `cannot_refine` | **0.7% — unchanged, still rare** |
| 3 | "Results hide their reasoning" | "The library is organized around **assets, not remembered episodes**" | `cannot_evaluate_results` → **`not_surfaced`** | 1.4% → **41.7%** |

**#3 is now a clean match.** v2's sentence — *"a visually plausible photo may be buried among
thousands because the user cannot see the surrounding sequence, place, or event that would make it
recognizable"* — is a description of `not_surfaced`, the single largest failure stage in the corpus
(60 of 144). This is no longer a concept arguing past the data.

**#1 is a partial move; do not claim a clean mapping on a slide.** Reframing from "the user cannot
express it" to "the library offers no starting point" shifts the blame from user to system, which is
closer to `system_misunderstood` (51 of 144). But it still describes an expression problem in its
second sentence. Honest line for the deck: *"v2 reframes this from user-side to system-side; the
measured field it most resembles is `system_misunderstood`, though the mapping is not exact."*

**#2 did not move.** Near-miss recovery is still `cannot_refine` at **0.7%** — 1 episode in 144.

### The reference numbers

All 144 `specific_attempt` episodes, every stage, verified against `data/interim/episodes.jsonl`
on 20 Sep. Shares are of 144 — **carry that denominator** (rule C).

| Failure stage | Count | Share of 144 |
|---|---|---|
| **`not_surfaced`** | **60** | **41.7%** |
| **`system_misunderstood`** | **51** | **35.4%** |
| `none` (no failure recorded) | 14 | 9.7% |
| `browse_path_changed` | 12 | 8.3% |
| `cannot_evaluate_results` | 2 | 1.4% |
| `slow_or_broken_ui` | 2 | 1.4% |
| `cannot_express` | 2 | 1.4% |
| `cannot_refine` | 1 | 0.7% |
| **Total** | **144** | **100%** |

**77% of observed failures happen before the user ever needs to recover** (41.7 + 35.4 = 77.1).

Two rows the deck should not skip over: `none` at 9.7% is the share where the model recorded no
failure stage at all, and **`browse_path_changed` at 8.3%** is the only other stage above 2% — it is
the H6 (learned path broken) signal, and H6 was in the audit model's top-2. Neither changes the
build order, but omitting them from a slide invites the question.

### Why `failure_stage` is the field to trust

| Field | Agreement | Use it? |
|---|---|---|
| `search_mode` | κ 0.522 | Yes |
| **`failure_stage`** | **κ 0.509** | **Yes — the ranking rests on this** |
| `specificity` | κ 0.464 | Yes |
| **`hypotheses`** | **Jaccard 0.347** | **No — lowest of the three list-valued fields** |

Compare like with like: `hypotheses` (0.347) is the lowest of the three Jaccard-scored list fields —
`cues_retained` is 0.557 and `cues_lost` 0.673. It is **not** the worst field overall (`query_language`
κ 0.002 is broken, `outcome` κ 0.161 is lower still), and a Jaccard is not comparable to a κ. The
defensible claim is narrower and still decisive: **the ranking rests on the weakest of the fields it
could have rested on**, while the "recovery is rare" finding rests on one of the strongest.

**Where they disagree, `failure_stage` wins**, and the deck says so in one line. Rule B rewards
exactly this kind of explicit reasoning.

### Build order — unchanged, but now the concept agrees

| Stage | Addresses | Observed share | Priority |
|---|---|---|---|
| 1. Reflect the memory into editable clue chips | `system_misunderstood` | **35.4%** | **First** |
| 3. Show a visual trail (episodes, not a grid) | `not_surfaced` | **41.7%** | **First** |
| 2. Ask one high-value follow-up | `cannot_express` | 1.4% | Stretch |
| 4. Let the user steer / "not this, but nearby" | `cannot_refine` | 0.7% | Stretch |

Stages 1 and 3 cover 77% of observed failures. **Build those; 2 and 4 are stretch.**

> **What v1 said, and why the change is worth showing.** Against v1, this section read: *"the concept
> names three failure modes and all three are the rarest in the data."* That was accurate then. v2
> moved two of the three onto the measured failures without changing the four stages. If the deck
> shows this, it shows a design being corrected by evidence — which is what Part 2 is scored on.

---

## 2. Corrections still outstanding in v2

**Both of the defects flagged before v2 survive verbatim.** Checked against the v2 text on 20 Sep.

### 2.1 The metric is still session-level — fix this first

v2 still reads *"percentage of eligible **sessions** where the user opens the intended photo within
five minutes"* (executive summary and measurement plan, unchanged from v1).

The brief (p.2) counts *"percentage of **users**"*, and Plan 2 §5 defines user-level **URR**, with
the A/B randomising **by user**. Session-level is the exact defect §3D of the lessons doc says to fix
before Part 2. Left as-is, the MVP slide contradicts slide 2 — the CS2 Clarity failure in miniature.

> **Replace with:** URR — of users who had at least one vague-intent retrieval task in a 28-day
> window, the share who reached the photo on at least one of them. Report task-success beside it as
> the mechanism, never on its own.

### 2.2 "Current performance is unknown" — it is not, as of 20 Sep

v2 still says the target *"should be set after baseline instrumentation, because current
vague-memory retrieval performance is unknown."*

| v2 says | Measured 20 Sep |
|---|---|
| "current vague-memory retrieval performance is unknown" | baseline recall@20 **0.053**, hit@1 **0.000** |
| "the exact target should be set after baseline instrumentation" | oracle **0.583**, hit@1 **0.233** → headroom **+0.530** |

The oracle *is* Memory Trails' core mechanic — turn a clue into a window, then search inside it —
measured on 494 real images and 30 evidence-derived tasks.

**Corrected 21 Sep:** the MVP's own extractor scores **0.612**, *above* the oracle's 0.583, so 0.583
is **not** an upper bound — `filters_for` is a ±45-day heuristic handed the answer's date. Quote
**0.053 → 0.612** as the measured lift, with the caveats in `PROGRESS.md`: synthetic tasks, an
extractor written against their known phrasings, and a recall@20 metric that rewards narrow windows
mechanically.

### 2.3 The cue taxonomy is asserted; we have it measured

v2 keeps v1's taxonomy table unchanged. The engine measured the same thing across 144 specific
attempts, and **the two broadly agree** — a genuine validation worth stating:

| Cue | Measured | In the doc? |
|---|---|---|
| `temporal_approx` | **40** | Yes ("relative time") |
| `object` | 17 | Yes |
| `exact_date` | 14 | Partly |
| `text_in_image` | 12 | Yes |
| `who_with` | 10 | Yes ("people") |
| `event_anchor` | 9 | Yes ("event") |
| `place_named` | 6 | Yes |

**The headline:** the most-retained cue is an approximate time (40), and the most-*lost* cue is the
exact date (37). People remember roughly when, and that is exactly what the index cannot use. Rule D
awards measured over asserted, and Data & Metrics is the weakest competency at 27.08/40.

### 2.4 The prototype is scripted; the brief requires functional

`google-photos-memory-trails.html` is still v1-era and fully static — a regex
(`/medicine|sick|prescription|tablet/`) selects one of two hardcoded scenarios and the thumbnails are
CSS gradients. As an **interaction mock for user testing it is genuinely useful**, and the "why this
matches" panel is the best idea in the set.

But Part 5 requires the MVP be *"sufficiently functional that another person can use it to attempt a
retrieval task."* A scripted demo does not clear that bar on its own.

**The missing half already exists.** Phase 1 built the working retrieval; the HTML has the interface.
Joined, they clear the bar. This is what the Vercel build does.

### 2.5 Vocabulary changes v2 introduced — carry them into the UI

| v1 | v2 | Where it shows up |
|---|---|---|
| "why this matches" | **"why this episode is here"** | Result card explanation |
| "result clusters" | **"visual episodes"** | Funnel metric, results view |
| "recovery loop" | **"memory-reconstruction loop"** | Positioning |
| "transparent match explanations" | **"transparent episode explanations"** | Differentiator line |
| "an opt-in search mode" | **"an opt-in memory re-entry mode"** | Product definition |

---

## 3. What is already built vs genuinely new

| Memory Trails needs | Status | Where |
|---|---|---|
| A real library with episodes | **Built** | 494 images, 25 episodes, `data/demo/library.jsonl` |
| Similarity search | **Built** | `demo_index.baseline_search` |
| Clue → metadata window | **Built** | `demo_index.filtered_search`, `demo_eval.filters_for` |
| Episode clusters ("visual episodes") | **Built** | `episode_id` on every record |
| Measured baseline to beat | **Built** | 0.053 → 0.583 |
| **Clue extraction from free text** | **NEW** | An LLM call: "July 2025ish" → a date window |
| **"Why this episode is here"** | **NEW** | Cheap: name the filters that fired |
| **UI wiring the two together** | **NEW** | The interface, pointed at the real index |
| Adaptive follow-up question | Stretch | Addresses 1.4% of failures |
| Steering / "not this, but nearby" | Stretch | Addresses 0.7% of failures |

Three genuinely new pieces, not ten. The oracle already proves the mechanic works; what is missing
is inferring the window from text instead of being handed it.

---

## 4. Settled (21 Sep)

`failure_stage` decided it, and the MVP was built on that reading: stages 1 and 3, covering
`not_surfaced` (41.7%) and `system_misunderstood` (35.4%). Stages 2 and 4 are cut, and the deck
should **state the cut with its 1.4% / 0.7% reason** — a scoped-out feature with a measured
justification reads as judgement.

The reasoning below is kept because the deck has to reproduce it: the H3 lead came from the weakest
field on the form, and saying which field decided the call is what rule B rewards.

**If the interviews had confirmed what `failure_stage` says** — that failures are dominated by "not
understood" and "never surfaced" rather than "could not recover" — then v2 is the right shape and
stages 1 and 3 are the product.

**If the interviews instead surface a lot of `cannot_refine`**, the `hypotheses` field was right, H3
stands, and stages 2 and 4 matter more.

**Risk v2 introduced, now resolved (20–21 Sep).** v2 deliberately moved *away* from H3: v1's "adds a recovery
loop around retrieval … correction → retrieval" became "adds a memory-reconstruction loop around the
library … recognition → retrieval". That is the right direction if `failure_stage` holds, and the
wrong direction if H3 had held. It did not: `cannot_refine` is 0.7%, and the verdict says which
field decided and why.

Either way, say which field decided it. An overturned hypothesis stated plainly scores; a quiet
switch does not.
