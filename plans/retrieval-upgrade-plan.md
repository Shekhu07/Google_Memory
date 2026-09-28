# Retrieval Upgrade — Implementation Plan (23 Sep → 5 Oct)

**Scope:** build the four ⭐ ideas from `plans/retrieval-ideas.md` (A1–A4), optionally A5, then run the
required MVP tests. **This file does not replace `plans/implementation_plan.md`** (the master execution plan);
it adds a work block to its Phase 4/5 and follows its rules.

**Hard stop on new building: end of Sun 27 Sep.** After that, only testing, interviews and the deck.

## Guardrails (apply to every task)

1. **Every change argues the locked problem.** Each task below names the failure stage it serves.
2. **Tune on dev, report on test.** Never quote a number from the split used for tuning.
3. **0.479 stays as the synthetic-phrasing number.** New numbers are added beside it; nothing gets overwritten.
4. **Parity gates stay green:** `tests/test_service_parity.py` and `tests/test_export_onnx.py`.
   Suite green before stopping each day: `.venv/bin/python -m pytest -q tests` and the retrieval tests.
5. **One value per number** (rule C): every new figure goes into the deck facts table the day it is measured.
6. **Groq budget:** the LLM scoring run uses the demo model (`gpt-oss-20b`), never the pipeline models. Don't launch at 05:30 IST.

---

## Schedule

| Day | Task | Output |
|---|---|---|
| Wed 23 Sep | T1 real-phrasing eval | `tasks_real.jsonl`, first honest numbers |
| Thu 24 Sep | T2 festivals, numeric dates, Hinglish, relative seasons | `clues.py` + tests; dev → test scores |
| Fri 25 Sep | T3 trip-relative time · start T4 | `clues.py`; soft-mode scorer |
| Sat 26 Sep | T4 soft filters + "just outside your dates" strip | service + UI; parity extended |
| Sun 27 Sep | T5 deploy + re-measure + docs · T6 test kit ready · (A5 if time) | live MVP, updated README/PROGRESS |
| 28 Sep – 2 Oct | T6 delayed-recall MVP tests (≥3) alongside interviews (5–6) | evaluation report |
| 3 – 5 Oct | Deck (per `plans/implementation_plan.md` §8) | `NL_GooglePhotos.pdf` |

---

## T1 — Real-phrasing evaluation set (idea A1) · ~0.5 day

**Serves:** `system_misunderstood` 35.4% · Risk #1 · Data & Metrics

**Files:** new `engine/demo_tasks_real.py`, new `data/eval/tasks_real.jsonl`, edit `engine/demo_eval.py`, new `tests/test_demo_tasks_real.py`

**Steps**
1. Build a **phrasing bank** of templates, each labelled with its source:
   - `real`: drawn from the 32 `query_verbatim` values and the `evidence` quotes in `data/interim/episodes.jsonl`
     (e.g. "about {n} years ago", "last {season}", "{festival} {year}", "{dd}/{mm}/{yyyy}", "{month} {year}", "the {category} we visited in {place} last {season}")
   - `survey`: from survey free text, if responses exist
   - `constructed`: Hinglish forms ("pichle saal", "{festival} ke time") until the survey supplies real ones. **Label them constructed on the slide.**
2. For each of the 30 tasks, render 2 queries from templates whose fields fit the target's date, place, category and episode. Keep `answer_ids` unchanged. Fix `today = 2026-09-23` so relative phrases are reproducible.
3. **Split by phrasing family**, not by task: about 60% of families go to dev, 40% to test. The test families are never opened while tuning T2–T4.
4. Add strategies to `demo_eval.py`: `baseline`, `oracle`, `inferred_rules`, `inferred_llm` (calls `llm_clues.py`, caching results to `data/eval/llm_cache.json`), and later `soft`. Add `--tasks {synthetic,real_dev,real_test}`.
5. Record the **before** numbers for every strategy × task set, with a per-cue breakdown.

**Done when:** `tasks_real.jsonl` has ~60 queries with source labels; a before-table exists for all strategies; tests cover template rendering and the split being fixed and deterministic.

---

## T2 — Festivals, numeric dates, relative seasons, Hinglish (idea A2) · ~0.5–1 day

**Serves:** `system_misunderstood` · H1 · first test of H4

**Files:** `webapp/apps/retrieval/clues.py`, `webapp/apps/retrieval/tests/test_clues.py` (and `engine/demo_eval.py` if it imports its own copy)

**Steps**
1. `FESTIVAL_DATES`: per-year dates, 2016–2026, for Holi, Diwali, Onam, Ganesh Chaturthi, Eid-ul-Fitr, Navratri/Dussehra. Take them from a published calendar and verify each; don't write them from memory. Fixed-date holidays by rule: Christmas, New Year, Halloween, Aug 15, Jan 26. Thanksgiving = 4th Thursday of November. Window: **date ± 3 days**.
2. A festival with no year ("last Diwali", "Diwali ke time") resolves to the most recent one before `today`.
3. Numeric dates: `DD/MM/YYYY`, `DD-MM-YYYY`, `DD.MM.YY`. Assume day-first (Indian convention); if the day is ≤12 and the month ≤12, still read day-first, but widen the window to ±3 days.
4. Relative seasons: "last winter" = the most recent full Dec–Feb before today; "this monsoon" = Jul–Sep of the current year; "last summer" = May–Jun. The winter window crosses the year boundary but stays contiguous.
5. "N years ago" / "about N years ago" → that calendar year ±3 months.
6. Hinglish time vocabulary: pichle/pichhle saal, is saal, pichle mahine, do/teen saal pehle, {festival} ke time/pe.
7. **Don't break the synthetic forms.** "sometime in 2024" and "July 2025ish" must return exactly what they return today, or `test_service_parity.py` fails.
8. Tune on `real_dev`. Then run `real_test` **once** and record it.

**Done when:** every query in the §0 probe table of `plans/retrieval-ideas.md` returns a correct window; synthetic recall is unchanged at 0.479; the test-split number is recorded.

---

## T3 — Time relative to the user's own trips (idea A3) · ~0.5 day

**Serves:** `not_surfaced`. The current parser creates this failure itself.

**Files:** `clues.py`, `search.py` (reuse `episode_facts` for start/end dates), `test_clues.py`

**Steps**
1. Detect `(a few|N) (days|weeks|months) (before|after)`, `just before/after`, `right after`, `pehle`, `baad`, `ke baad`, next to an episode mention.
2. Windows: *after* → [episode end, end + 6 weeks] (or the stated amount); *just after* → [end, end + 14 days]; *before* mirrors these from the start date.
3. **Drop the `episode` and `location` filters** when the time is relative. The photo is by definition not in that episode.
4. Chip label reads "6 weeks after Goa trip" so the breadcrumb shows the interpretation (it stays correctable).

**Done when:** "beach photo a few weeks after the Goa trip" returns a window after the trip with no episode lock; tests cover before/after/just/numeric/Hinglish forms.

---

## T4 — Filters that score instead of gate (idea A4) · ~1 day

**Serves:** `not_surfaced` · mitigation for Risk #2

**Files:** `engine/demo_index.py` (new `soft_search`), `webapp/apps/retrieval/search.py` (new `mode="soft"`), `main.py`, `MemoryTrails.tsx`, `tests/test_service_parity.py`, `tests/test_demo_index.py`

**Steps**
1. Score = `cos(query, photo) + β_date·w_date + β_place·[place match] + β_cat·[category match]`,
   where `w_date = 1` inside the window and `exp(−days_outside / τ)` outside.
2. Grid-search β and τ on `real_dev` plus the synthetic set. Keep the grid small (e.g. β ∈ {0.05, 0.1, 0.2}, τ ∈ {7, 21, 45}).
3. **Guard per cue:** `exact_date` must stay at 1.000 and `temporal_approx` must not fall below its hard-filter value. If either drops, raise β_date or keep hard gating for exact dates only.
4. Service: add `soft` beside `filtered`/`baseline`; the product uses `soft` only if it wins on `real_test`.
5. UI: a "Just outside your dates" strip under the moments list, showing the top 3–5 photos outside the window with the offset ("+9 days"). New event `outside_window_opened`.
6. Extend the parity test to assert offline = service for `soft` on all task sets.

**Done when:** soft vs hard is reported on synthetic, `real_dev` and `real_test` with per-cue rows; the parity test covers soft; the strip renders and is measured at 320px (spec §11).

---

## T5 — Deploy, re-measure, update the record · Sun 27 Sep

1. `engine.export_web` → deploy `memory-trails-demo`; open it in an incognito window and run the 8 probe queries live.
2. Update `README.md` ("The measured result" table gets a real-phrasing row) and `plans/PROGRESS.md` (decisions and numbers).
3. Add to the deck facts table: rule-based vs LLM on `real_test`, soft vs hard, each figure's denominator, and each phrasing's source label.
4. **Optional A5** (vague-query catch in Search), only if T1–T4 finished by Saturday.

---

## T6 — Delayed-recall MVP tests · kit ready 27 Sep, run 28 Sep – 2 Oct

**Why:** the brief requires ≥3 MVP tests (never-cut). Participants can't search a library they don't own, so we *create* a vague memory in the demo library instead of asking for one.

**Protocol (per participant, ~45 min, remote)**
1. **Exposure (3 min):** a short story slideshow of 6–8 photos from 3 library episodes, told as a friend's year ("this was around Diwali", "a few weeks after they got back from Goa"). No dates on screen.
2. **Distraction (20–25 min):** the brief's Part 3 interview about *their own* retrieval failures. One session does both jobs.
3. **Retrieval (15 min):** 3 tasks ("find the café photo from the Goa story"). Arm order alternates between participants: plain Search tab vs Memory Trails. 5-minute cap per task. Think aloud.
4. **Debrief (2 min):** "Did the moments match how you remembered it?" (tests assumption #1).

**Measure:** success within 5 minutes · time to the first plausible moment · steps (from `track.ts` events) · **false confirmations** (guardrail) · unprompted switches from Search to the memory flow (assumption #3).

**Kit files:** `research/testing/mvp_test_protocol.md` (script, story, task cards, consent line), `research/mvp_test_results.md` (template).

**Disclose on the slide:** memories created in a session are shallower than real ones; n is small; tasks come from the synthetic library.

---

## Cut order if behind

A5 → T4's UI strip (keep the scorer and the numbers) → T3 → T2's Hinglish part.
**Never cut:** T1 (it's the honest number) and T6 (the brief requires it).

## What goes on the deck

| Slide | Addition |
|---|---|
| MVP + evidence | Real-phrasing row next to 0.479; rule-based vs LLM |
| Risks | Risk #1 now measured; Risk #2 mitigated by soft scoring, with numbers |
| Testing | Delayed-recall results: success, time, false confirmations |
| Roadmap | A7 captions/OCR, justified by oracle = 0 on text/place cues; A5, A6 |
