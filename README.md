# Memory Trails — a memory re-entry surface for a photo library

A product case study on a narrow failure: **you remember a photo, but you cannot get back
to the moment that contains it.** Not general photo search — the step before it.

**Live**

| | |
|---|---|
| **The MVP** | https://memory-trails-demo.vercel.app |
| The Discovery Engine | https://retrieval-discovery-engine.vercel.app |
| Photo credits | https://memory-trails-demo.vercel.app/attribution |

---

## The measured result

A clue-to-window step, over the same CLIP embeddings and the same 494 images:

| Strategy | recall@20 | hit@1 |
|---|---|---|
| Baseline — plain CLIP over everything | 0.053 | 0.000 |
| Oracle — ±45 days around the answer's own date | 0.583 | 0.233 |
| **Inferred — filters read from the query text alone** | **0.612** | 0.200 |

The inferred strategy is what the deployed service runs. It **beats the oracle**, which means
the oracle was never an upper bound: `filters_for` is a ±45-day heuristic that happens to hold
the answer's date, not an optimal policy. A month-precise reading of *"July 2025ish"* is both
more faithful to the query and narrower, and at k=20 narrower wins.

**Read these caveats before quoting 0.612.** The 30 tasks are synthetic and phrase vague time
exactly three ways, which the extractor was written knowing; `recall@20` mechanically rewards
narrow windows; and the win is uneven — *"sometime in 2024"* widens to 222 candidates and loses.
It measures the mechanic, not real-language performance. See `PROGRESS.md`.

## Where the problem statement comes from

85,140 public posts → 5,305 keyword-filtered → 1,333 model-screened → 819 relevant →
**720 structured episodes**, of which **144** are specific retrieval attempts.

Across those 144, **77% of failures happen before recovery is even possible**: the photo never
surfaced (41.7%) or the query was misread (35.4%). Every episode was read twice by two
independent model families; they agree moderately on *where* retrieval broke (κ 0.509) and
poorly on *which hypothesis* it supports (Jaccard 0.347), so the hypothesis ranking deliberately
does **not** come from this engine.

## The interface

Built to three user-authored specifications: a flow wireframe, a design specification and an
enhancement roadmap.

The state model is `compose → recap → moments → episode → confirmed`, with `empty` and exit from
anywhere. A memory breadcrumb — *"Your memory → goa trip → Goa → café"* — stays editable and visible
through episode browsing, so the system's current interpretation is never hidden. Episode cards carry
density cues (*"14 photos · 5 street scenes · 3 match your clues"*) so a moment can be judged without
opening it, and *"See evidence"* names each dimension, how certain it is, and where it came from.

Episodes are ranked by **coverage × coherence × recognizability × evidence quality**, never by a
user-facing score. **The weights in that formula are judgement, not measurement** — the evaluation
scores photo recall, not episode ordering, so it cannot validate them.

Two things are deliberately absent: a clarifying question and near-miss recovery. They serve
`cannot_express` (1.4%) and `cannot_refine` (0.7%) — the rarest failures in the corpus — and wait on
interview evidence rather than being built because a design document asked for them.

## Layout

```
engine/          collection, screening, extraction, audit, evaluation, export
webapp/
  apps/web/      Next.js — the MVP, the evidence tabs, photo credits
  apps/retrieval/FastAPI — clue extraction and episode-grouped search
tests/           164 tests, including two parity gates
research/        recruitment, survey design, concept-vs-evidence reconciliation
docs/superpowers/ the design spec and the implementation plan
```

## Running it

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt

# Encoder weights are NOT in this repo - they are a 126 MB build artifact.
.venv/bin/python -m engine.export_onnx     # needs torch; writes the ONNX text tower
.venv/bin/python -m engine.export_web      # builds every artifact the site serves

.venv/bin/python -m pytest -q tests        # 164 tests

cd webapp/apps/web && npm install && PROXY_PY=1 npm run build
```

`PROXY_PY=1` forwards `/api/py/*` to a local retrieval service on port 8000. On Vercel that route
is owned by `webapp/vercel.json`, and the flag is never set.

## Where retrieval still fails

Per-cue on the 30 tasks, the clue-to-window step transformed time and did nothing for content:

| Cue | baseline | inferred | oracle |
|---|---:|---:|---:|
| `temporal_approx` | 0.062 | **0.688** | 0.438 |
| `exact_date` | 0.000 | **1.000** | 1.000 |
| `object` | 0.250 | 0.250 | **0.250** |
| `text_in_image` | 0.000 | 0.000 | **0.000** |
| `place_named` | 0.000 | 0.000 | **0.000** |

On the bottom three the *oracle* does no better than the baseline. Perfect knowledge of the answer's
own date, place and category still retrieves nothing, so the limit is not clue extraction — **the
index cannot represent those cues.** CLIP cannot read text inside an image, and `text_in_image` is
the fourth most-retained real cue. OCR or captions is the highest-value work remaining.

## Two gates worth knowing about

**Encoder parity.** The 494 image vectors came from `sentence-transformers/clip-ViT-B-32`. If the
ONNX text tower lands in a different space, results look plausible and mean nothing.
`tests/test_export_onnx.py` proves cosine > 0.999 before anything depends on it. int8 quantization
was tried and rejected: cosine stayed ≥ 0.979 while **0 of 30 tasks kept an identical top-20 set**
and hit@1 fell 0.233 → 0.200. High cosine does not imply stable ranking.

**Service parity.** `tests/test_service_parity.py` asserts the deployed service returns exactly
what the offline evaluation returns across all 30 tasks, in both modes. This is the mechanism that
stops the live demo and the written numbers from drifting apart, and it is why the backend is
Python rather than TypeScript.

## Data

Photographs are Creative Commons from Openverse and belong to their creators — see the credits
page. Dates, places and episodes attached to them are **synthetic**, invented to build a testable
library, and describe nothing real about those photographs.

Collected posts are public reviews and comments with author data stripped at collection: records
carry only text, date, source and era. Retrieval-rate baselines are modelled, not measured — there
is no telemetry behind them.

## Not in this repo

Other documents reference `SCORECARDS_AND_LESSONS.md` — grading feedback from two earlier case
studies, and the rules drawn from it. That file and the fellowship's own brief are kept locally
and deliberately not published. The references are left in place because they explain *why*
several decisions were made.

The CLIP text encoder weights are also absent; regenerate them with `engine.export_onnx`.
