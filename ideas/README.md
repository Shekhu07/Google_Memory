# MVP ideas

Ideas for the Memory Trails MVP that are not yet built, each checked against what the engine
actually measured before anything gets written in code.

**This does not replace `Google_Photos_—_Additional_MVP_Ideas_for_Memory_Retrieval.pdf`** at the
repo root. That document holds ten earlier concepts with a prioritisation matrix and a recommended
bundle of four — but it is v1-era and was **never reconciled with the evidence**
(`research/memory_trails_reconciliation.md:10-11`). Ideas in *this* folder are reconciled as they
are written. Where an idea here overlaps one of those ten, it says so.

Those ten, for reference: "Show me around that time" · Memory anchors · "Not this, but nearby"
recovery · Visual memory board · "Open the episode" · Search by "what was happening" · OCR
resurfacing · "Ask someone who was there" · Camera-to-memory bridge · "Memory mode" confidence
ladder.

---

## Status

| # | Idea | Serves | Verdict | Built |
|---|---|---|---|---|
| — | *none yet* | | | |

---

## The measured evidence every idea is checked against

**Failure stage**, across the 144 specific retrieval attempts in `data/interim/episodes.jsonl`.
All eight rows with counts and the denominator, per rule C of `SCORECARDS_AND_LESSONS.md` — one
value per number. Verified 21 Sep.

| Failure stage | n | Share of 144 |
|---|---:|---:|
| `not_surfaced` | 60 | **41.7%** |
| `system_misunderstood` | 51 | **35.4%** |
| `none` | 14 | 9.7% |
| `browse_path_changed` | 12 | 8.3% |
| `cannot_evaluate_results` | 2 | 1.4% |
| `slow_or_broken_ui` | 2 | 1.4% |
| `cannot_express` | 2 | 1.4% |
| `cannot_refine` | 1 | 0.7% |

**77% of failures happen before recovery is even possible** — the photo never surfaced, or the
query was misread. An idea serving the bottom four rows is serving under 5% of observed failures.
That is allowed, but it has to be a stated choice, the way stages 2 and 4 were cut with their
numbers on the slide.

**Cues people still remember**, same 144 attempts — this decides what the index can serve at all:

`temporal_approx` 40 · `object` 17 · `exact_date` 14 · **`text_in_image` 12** · `who_with` 10 ·
`event_anchor` 9

**Where retrieval still fails**, per cue on the 30 evaluation tasks. **Read the denominators
before using any of this** — `README.md`'s version of this table is the single-cue subset and does
not say so, and two of its cells rest on one task each.

Over **all 30 tasks**, counting a task under every cue it carries:

| Cue | n | baseline | oracle |
|---|---:|---:|---:|
| `temporal_approx` | 21 | 0.052 | **0.571** |
| `exact_date` | 5 | 0.000 | **1.000** |
| `text_in_image` | 4 | 0.000 | **0.750** |
| `object` | 2 | 0.250 | 0.250 |
| `place_named` | 2 | 0.000 | **0.500** |
| `event_anchor` | 2 | 0.050 | **1.000** |

Over **single-cue tasks only** — this is the table in `README.md`:

| Cue | n | baseline | oracle |
|---|---:|---:|---:|
| `temporal_approx` | 16 | 0.062 | 0.438 |
| `exact_date` | 4 | 0.000 | 1.000 |
| `object` | 2 | 0.250 | 0.250 |
| `text_in_image` | **1** | 0.000 | 0.000 |
| `place_named` | **1** | 0.000 | 0.000 |
| `event_anchor` | **1** | 0.000 | 1.000 |

**The two tables support opposite conclusions, and this matters before anything is built.**
`README.md` reads the single-cue rows and concludes the oracle does no better than the baseline on
`text_in_image` and `place_named`, therefore *"the index cannot represent those cues"*, therefore
OCR or captions is the highest-value work remaining. Those two cells are **n=1 each**. Across all
tasks the oracle scores **0.750** on `text_in_image` and **0.500** on `place_named` — a large gain
over baseline, not a flat zero.

So the honest version is: **the OCR case is plausible but not established.** CLIP genuinely scores
0.000 on `text_in_image` at baseline across all 4 tasks, which is real. What is *not* supported is
that a metadata window cannot rescue it — with all 4 tasks the window recovers three of them.

Before building anything that depends on "the index cannot represent text", either widen the task
set for that cue or state the n=1 on the slide. Both are defensible; silently quoting 0.000 is not.
Verified against `data/eval/{baseline,oracle}_report.json` on 21 Sep by recomputing from
`tasks_detail`.

---

## The rule for anything that gets built

`tests/test_service_parity.py` asserts the deployed service returns exactly what the offline
evaluation returns, across all 30 tasks, in both modes. It is the mechanism that stops the live
demo and the written 0.612 from drifting apart.

**An idea implemented into `webapp/` must keep that gate green.** If it changes ranking, filtering
or the index, re-run the evaluation and write down the new `recall@20` and `hit@1` — then update
every number that moved, in `README.md`, `PROGRESS.md` and any drafted slide. A changed mechanism
with a stale number on a slide is exactly the drift that cost CS2 14.35 Clarity points.

## How to add one

Copy `TEMPLATE.md` to `NNN-slug.md`, fill it in, add a row to the status table above.
Every idea gets a verdict, including the ones that lose — rule B.
