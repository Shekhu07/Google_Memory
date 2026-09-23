# Memory Trails — Ideas Backlog

**Written:** 23 Sep 2026 · **Companion:** `implementation-plan.md` (what gets built, in order)
**Filter every idea must pass:** does it argue the locked problem statement?

> People remember *when-ish* and *what happened*, and Google Photos indexes *items*. 77% of observed
> failures happen before the user ever needs to recover: the query is misread (`system_misunderstood`
> 35.4%) or the photo never appears (`not_surfaced` 41.7%).

An idea that doesn't serve one of those two failure stages adds breadth, and breadth is how CS2 lost
14.35 Clarity points. It goes on the roadmap slide, not into the build.

---

## 0. The evidence that started this: real phrasing breaks the parser

The deployed rule-based extractor (`webapp/apps/retrieval/clues.py`) was probed on 23 Sep with
real-style queries, including verbatims from the 32 `query_verbatim` values in the 144 specific attempts.

| Query | Extracted filters | Problem |
|---|---|---|
| "July 2025ish" | 2025-07-01 → 2025-07-31 | ✅ one of the three synthetic forms |
| "restaurant we visited in Udaipur **last winter**" | `category: cafe` | no date |
| "**Halloween 2024**" *(real verbatim)* | `{}` | nothing |
| "**25/12/2024**" *(real verbatim)* | `{}` | numeric dates unparsed; `exact_date` is 14 of 144 |
| "**Diwali 2024**" | `category: festival` | no date, even though the library has a `diwali 2025` episode |
| "Holi last year" | all of 2025 | should be about a week in March |
| "**pichle saal** wali Goa trip ki photo" | Goa episode, no date | Hinglish time word ignored |
| "beach photo **a few weeks after** the Goa trip" | `episode: goa trip` | **restricts to the episode, which rules out the answer** |

**What this means:** 0.479 recall@20 is real, but it measures the three phrasings the parser was
written against. The LLM path (`llm_clues.py`) has never been scored, and neither has real phrasing.

---

## A. New ideas (brainstorm, 23 Sep)

Ranked by value for this submission: failure stage served × scorecard competency × days left.

### A1. Real-phrasing evaluation set ⭐ build first
- **What:** Rewrite the 30 tasks' query text using phrasing patterns taken from the real corpus
  ("about 5 years ago", "last winter", "Halloween 2024", "25/12/2024", "restaurant we visited in X").
  Keep the same targets. Split by *phrasing family* into dev (tune on it) and test (never look at it).
  Score baseline, oracle, the rule-based parser **and** the LLM parser.
- **Serves:** `system_misunderstood` 35.4% · Risk #1 on the risk slide · **Data & Metrics** (the gap to median is −2.46)
- **Implement:** `engine/demo_tasks_real.py` → `data/eval/tasks_real.jsonl`; add strategy flags to `engine/demo_eval.py`
- **Effort:** ~0.5 day · **Deck:** turns the caveat "measured on synthetic phrasing" into a number

### A2. Time anchored to events and festivals ⭐
- **What:** Resolve festivals and holidays to dates (Holi, Diwali, Onam, Ganesh Chaturthi, Eid,
  Christmas, Halloween, Thanksgiving, New Year, Aug 15, Jan 26). Also handle DD/MM/YYYY dates,
  relative seasons ("last winter", "this monsoon"), "N years ago", and Hinglish time words
  ("pichle saal", "is saal", "pichle mahine", "do saal pehle", "Diwali ke time").
- **Serves:** `system_misunderstood` · H1 (the most-retained cue is `temporal_approx`, 40 of 144; `event_anchor` 9; `exact_date` 14) · **gives H4 its first test**
- **Implement:** `clues.py`: `FESTIVAL_DATES` table (verified against a published calendar, 2016–2026), numeric-date regex, relative-season resolver, Hinglish time vocabulary
- **Effort:** ~0.5–1 day · **Deck:** India-specific, grounded in real verbatims

### A3. Time relative to the user's own trips ⭐
- **What:** "a few weeks after the Goa trip", "just before the wedding", "shaadi ke baad". Look up
  the episode's dates, then **shift the window**. Do not filter to the episode.
- **Serves:** `not_surfaced`. Today the parser *creates* this failure by locking onto the named episode.
- **Implement:** `clues.py` detects `before|after|pehle|baad` + an episode mention → offset window from `search.episode_facts`; drop the episode and location filters in that case
- **Effort:** ~0.5 day · **Deck:** "the user's own trips are their calendar", the H1 thesis made concrete

### A4. Filters that score instead of gate ⭐
- **What:** A date/place/category match *raises* rank; a miss doesn't exclude. Scoring outside the
  window fades with distance. Add a "Just outside your dates" strip (top 3–5, e.g. "+9 days").
- **Serves:** `not_surfaced`. This is the fix for Risk #2 (a hard filter can hide the right photo and recreate
  the 41.7% failure). It also helps the 546-candidate vague-year window, which currently loses.
- **Implement:** new `soft` mode in `engine/demo_index.py` + `search.py`; tune β/τ on the dev split only; extend `test_service_parity.py`
- **Effort:** ~1 day · **Deck:** the risk slide gets a mitigation that's built and measured, not just promised

### A5. Catch vague queries in the normal Search tab
- **What:** When a Search-tab query has vague-memory language ("ish", "around", "after the trip",
  festival names) or CLIP's top scores come back flat, show an inline offer:
  *"Sounds like a moment — see it by trip and time"*. Don't rely on the separate "Can't describe it?" card.
- **Serves:** the **Expression** term of URR, which assumes users find the mode. Nobody discovers a separate mode on their own.
- **Implement:** `PhotoApp.tsx` → call `/extract` on submit; if the extracted filters contain a date or episode, render the offer; new event `reentry_suggested` in `track.ts`
- **Effort:** ~0.5 day · **Priority:** only if time allows

### A6. Start with no typing: a trips-and-months rail
- **What:** The opposite of a query: enter by tapping a trip or month and recognise the moment from there.
- **Serves:** `not_surfaced`. Tests whether typing adds anything for vague-time tasks.
- **Implement:** mostly built already (anchors and the time ribbon); needs an entry state that skips the composer
- **Effort:** ~0.5 day · **Priority:** follow-up, but a strong test arm for the MVP study

### A7. Captions and OCR inside the window
- **What:** Precompute OCR (tesseract/easyocr) and short captions (e.g. Florence-2) for the 1,250
  images offline, then blend word matching with CLIP *inside* the window.
- **Serves:** the cues where even the oracle scores 0: `text_in_image` 0.000, `place_named` 0.000, `object` 0.250. Also hit@1 (0.133).
- **Framing that keeps the thesis:** *the window finds the moment; captions find the photo inside it.*
- **Risk:** drifts toward H5. Adds a new build artifact, so the parity gate has to cover it.
- **Effort:** 1.5–2 days · **Verdict:** **roadmap slide**, quoting the oracle-zero numbers as the reason

---

## B. Ideas already in the project: status

| Idea | Source | Status | Why |
|---|---|---|---|
| Episode-first retrieval ("Open the episode") | Additional Ideas #5, roadmap §1.2 | ✅ Built | Core module; serves `not_surfaced` |
| Editable clue chips + memory breadcrumb | Design spec, roadmap §2.5 | ✅ Built | Serves `system_misunderstood` |
| Memory anchors | Additional Ideas #2 | ✅ Built (22 Sep) | `AnchorPicker.tsx` |
| "Show me around that time" ribbon | Additional Ideas #1 | ✅ Built (22 Sep) | Monthly chapters + Earlier/Later |
| Density cues, evidence expansion | Roadmap §3.2, §5.1 | ✅ Built | Trust guardrail |
| Clarifying question | Design spec §2.3 | ✂️ Cut | Serves `cannot_express`, **1.4%** |
| "Not this, but nearby" recovery + mismatch reason | Additional Ideas #3, roadmap §4.1 | ✂️ Cut | Serves `cannot_refine`, **0.7%** |
| Confidence ladder | Additional Ideas #10 | ◐ Partly covered | Evidence expansion gives certainty per dimension; no separate ladder needed |
| Visual memory board | Additional Ideas #4 | ⏸ Set aside | A new surface; overlaps anchors |
| Search by "what was happening" | Additional Ideas #6 | ⏸ Set aside | Sensitive inference; partly covered by A2/A3 |
| OCR resurfacing for documents | Additional Ideas #7 | → becomes **A7** | Roadmap slide |
| Ask someone who was there | Additional Ideas #8 | ⏸ Later | Social/privacy scope; single-user flow not yet validated |
| Camera-to-memory bridge | Additional Ideas #9, roadmap P2 | ⏸ Later | New pipeline; not in the thesis |
| Durable personal memory graph | Roadmap P2 | ❌ Not in MVP | Privacy risk |

---

## C. Assumptions to test (riskiest first)

| # | Assumption | If wrong | Cheapest test |
|---|---|---|---|
| 1 | Users' idea of "the moment" matches our episode boundaries | Episode cards feel arbitrary; recognition fails | Delayed-recall MVP test (see plan, Task 6) |
| 2 | Real users phrase time in ways we can parse | 0.479 doesn't hold in use | A1: real-phrasing eval, held-out split |
| 3 | Users will find a separate memory mode | Expression term collapses URR | A5 plus the MVP test: count unprompted switches from Search |
| 4 | Soft scoring doesn't bury exact-date hits | `exact_date` falls from 1.000 | A4 eval, reported per cue |
| 5 | Hinglish time words matter (H4) | A2's Hinglish part is wasted | Survey Q10 + interview quota |

---

## D. The one-line pitch for each built idea (for the deck)

- **A1:** "We measured on real phrasing, not just ours: rule-based X, LLM Y, on a held-out split."
- **A2 + A3:** "People date memories by festivals and trips. The parser now does too."
- **A4:** "A wrong window no longer hides the right photo; it lowers its rank."
