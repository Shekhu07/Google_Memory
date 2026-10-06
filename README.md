# Memory Trails — a memory re-entry surface for a photo library

> *"The challenge is not to improve search in general. We make retrieval work when the date, place, album or words are missing."*

A product case study on a specific failure: **you remember a photo exists, but you cannot precisely describe when it was taken, where it was taken, what album it belongs to, or the exact words to find it.**

**Live**

| | |
|---|---|
| **The MVP** (cited link) | https://memory-trails-v2.vercel.app |
| The MVP, mirror (same build) | https://memory-trails-demo.vercel.app |
| The Discovery Engine | https://retrieval-discovery-engine.vercel.app |
| About, and how it relates to Ask Photos | https://memory-trails-v2.vercel.app/about |
| Photo credits | https://memory-trails-v2.vercel.app/attribution |

---

## The measured results

### 1. Cue-Dropout Benchmark (E1: 120 tasks across 4 cue levels)
Directly measures retrieval success as human memory degrades from a fully described photo down to pure content description (30 base tasks evaluated on the 1,282-photo library):

| Level | What the query keeps | baseline recall@20 | soft recall@20 | soft moment@5 | soft found | n |
|---|---|---:|---:|---:|---:|---:|
| **L3 (fully described)** | Vague time + exact place + library word | 0.172 | **0.962** | **0.933** | **1.000** | 30 |
| **L2 (two vague cues)** | Paraphrased content + two of (time/place/ep) | 0.209 | **0.276** | **0.333** | 0.333 | 30 |
| **L1 (one vague cue)** | Paraphrased content + one vague time cue | 0.242 | **0.309** | **0.333** | 0.367 | 30 |
| **L0 (content only)** | Pure scene description, no metadata | 0.312 | **0.312** | **0.267** | 0.367 | 30 |

*Key Findings:*
- **Episode re-entry win:** At L2, `moment@5` (**0.333**) beats flat photo `recall@20` (**0.276**), showing that grouping into coherent visual moments rescues degraded memories that flat ranking misses.
- **Honest baseline match:** At L0 (pure content description), soft scoring exactly matches baseline (0.312) because no false filters are invented, keeping semantic CLIP unconstrained.
- **Rules vs LLM:** Rules are the deployed default (`notice: null`, <1s response). Exact numeric dates are frozen; real user language relies on vague-time anchors and visual moments.

### 2. Fully Described Real-Phrasing Benchmark (60 tasks, Cue Level L3)
60 template-rendered queries using phrasing patterns seen in real user verbatims (Hinglish time `pichle saal`, relative seasons `last winter`, festival anchors `Diwali 2023`, trip-relative offsets `3 weeks after Goa`, and colloquial questions). Every query contains the target's place and category word, measuring performance on **fully described photos (L3)**:

| Strategy | Split | recall@20 | hit@1 | Found |
|---|---|---|---|---|
| Baseline (Plain CLIP) | real_dev (n=30) | 0.170 | 0.033 | 0.200 |
| Inferred (Hard Rules) | real_dev (n=30) | 0.773 | 0.033 | 0.800 |
| Soft Scoring (A4) | real_dev (n=30) | 0.873 | 0.033 | 0.900 |
| Baseline (Plain CLIP) | **real_test (n=30, held-out)** | 0.172 | 0.000 | 0.200 |
| Date oracle (±45 d) | **real_test (n=30, held-out)** | 0.742 | 0.267 | 0.767 |
| Inferred LLM (Groq) | **real_test (n=30, held-out)** | 0.718 | 0.433 | 0.767 |
| Inferred (Hard Rules) | **real_test (n=30, held-out)** | 0.718 | 0.433 | 0.767 |
| **Soft Scoring (A4, Deployed Default)** | **real_test (n=30, held-out)** | **0.866** | **0.467** | **0.900** |

*Corrected 28 Sep:* the hard-rules row and the hit@1 column were stale — the committed result files
did not match the committed code. Re-running that code gives the values above.

*Methodology & Verification:* The held-out `real_test` split was evaluated **strictly once** (no tuning on test). Soft scoring beat hard rules (**0.866 vs 0.718** recall@20), improving `temporal_approx` from 0.724 to 0.871 and `event_anchor` from 0.267 to 0.484, while `exact_date` remained guarded at 1.000. 27 of 30 queries surfaced the target photo in top 20.

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
tests/           214 tests, plus 91 retrieval service tests (305 total)
plans/           implementation_plan.md (the working plan), PROGRESS.md (decision log), research plans, fix plans
design/          MVP concept PDFs, design specification, enhancement roadmap, screenshots
research/
  survey/        survey form script, survey design
  testing/       MVP test form script, scoring guide, log and analysis
  analysis/      facts table, Part 4 and Parts 7/8 drafts, concept reconciliation
deck/            final deck source: build_deck.py writes index.html and NL_GooglePhotos.pdf
brief/           the brief and prior scorecards (gitignored, kept local)
```

New documents go into the matching folder above, never the repo root.

## Running it

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt

# Encoder weights are NOT in this repo - they are a 126 MB build artifact.
.venv/bin/python -m engine.export_onnx     # needs torch; writes the ONNX text tower
.venv/bin/python -m engine.export_web      # builds every artifact the site serves

PYTHONPATH=. .venv/bin/pytest -q tests    # 214 tests

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

**Encoder parity.** The image vectors came from `sentence-transformers/clip-ViT-B-32`. If the
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

Other documents reference `brief/SCORECARDS_AND_LESSONS.md` — grading feedback from two earlier case
studies, and the rules drawn from it. That file and the fellowship's own brief are kept locally
and deliberately not published. The references are left in place because they explain *why*
several decisions were made.

The CLIP text encoder weights are also absent; regenerate them with `engine.export_onnx`.
