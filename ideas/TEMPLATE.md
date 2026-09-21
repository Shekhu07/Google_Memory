# NNN — <idea name>

> One sentence: what changes for the person using it.

**Status:** build now · next iteration · rejected
**Overlaps:** <one of the ten in the Additional MVP Ideas PDF, or "new">

---

## 1. Which measured failure does it serve?

Name the stage and carry the number and denominator from `README.md` in this folder.

> e.g. `not_surfaced` — 60 of 144 specific attempts, 41.7%.

If it serves a stage under 2%, say so here rather than leaving it to be discovered. A small stage
is not disqualifying — it is a stated choice, the way stages 2 and 4 were cut at 1.4% and 0.7%
with the numbers on the slide.

## 2. Can the index represent it?

What exists today: CLIP image vectors over 494 images, plus four metadata fields per photo —
`location`, `category`, `date`, `episode_id`.

If the idea needs anything else — text inside an image, faces, who was present, GPS traces, a
second modality — that is **new infrastructure**, and it is the real cost of the idea. Say which.

## 3. What already exists that this reuses

Most ideas are smaller than they look. Already built and tested:

- the 494-image library and its CLIP index (`engine/demo_index.py`)
- `filtered_search` — metadata window then similarity inside it
- episode grouping and `episode_facts` (`webapp/apps/retrieval/search.py`)
- clue extraction from free text, LLM with a rules fallback (`llm_clues.py`, `clues.py`)
- the phone shell, the gallery and the baseline search tab
- a 30-task evaluation harness (`engine/demo_eval.py`)

## 4. Build cost

What it touches, roughly how long, and **explicitly: does it touch the measured retrieval path?**
Anything that changes ranking, filtering or the index does.

## 5. How would you know it worked?

An evaluation change, not an opinion. Which number moves, measured how, on which tasks.
"It feels better" is not an answer; neither is a number with no denominator.

## 6. What would make this a mistake?

The strongest argument against building it. If there isn't one, the idea has not been thought
about hard enough yet.

## 7. Verdict

Build now / next iteration / rejected — **and why**, in one or two sentences.

Every idea gets a verdict including the ones that lose (rule B). An idea rejected with a measured
reason reads as judgement; an idea quietly dropped reads as omission.
