# Retrieval survey — design and mapping

**Script:** `research/survey_form.gs` (run it at script.google.com, same as the screener)
**Not a replacement for** `research/screener_form.gs` — that stays 9 questions and goes to your
personal network for fast bookings. This one goes wide.

---

## Why a second form

The engine's Sep 20 finding: **8.6% of extracted posts are scoreable, and the rate does not move
with the source** (Play Store 20.1% / 8.5%, Reddit 19.4% / 9.7%). People do not narrate a complete
retrieval attempt in public text, anywhere. More collection cannot fix that.

A survey can, because it *structures* the narration instead of hoping to find it. Every respondent
who had a failure is walked through cue → query → failure stage → outcome. Yield goes from 8.6% to
roughly 100% of qualifying responses.

At n=30 this roughly doubles your scoreable episode pool (62 → ~90) and, unlike the engine corpus,
it is not 86% Play Store.

---

## What it measures that nothing else does

| Question | Feeds | Status before this form |
|---|---|---|
| Q3 how often you hunt for old photos | **n̄** in the URR formula | Modelled slot |
| Q4 what you do first | **Expression** term | Modelled slot |
| Q14 did you find it | Outcome distribution → URR numerator proxy | Modelled slot |
| Q10 language you type in | **H4** | *Not tested* — `query_language` returned `en` for all 142 audited posts |
| Q15/Q16 time spent, consequence | Part 4's "why this matters", measured | Asserted |

Rule D of `SCORECARDS_AND_LESSONS.md`: measured beats modelled, and Data & Metrics is the weakest
competency at 27.08/40. Three modelled slots becoming measured is the cheapest available gain.

---

## Vocabulary mapping

Every closed-choice option maps 1:1 onto `engine/extract.py` `VOCAB`, so responses merge into
`episodes.jsonl` instead of forming a separate silo. **Do not reword an option without updating
this table.**

| Q | Engine field | Notes |
|---|---|---|
| Q1 | — | Segment; mirrors screener Q1 so the two datasets pool |
| Q2 | — | Segment (5,000+ = the brief's long-tenure user) |
| Q3 | — | n̄ |
| Q4 | `workaround` (partial) | First-move, not fallback — Expression term |
| Q5 | free text | Deck quotes |
| Q6 | `asset_type` | Tests **H5** |
| Q7 | `cues_retained` | 12 options, all vocabulary values except `activity`/`emotional`. Tests **H1** |
| Q8 | `cues_lost` | All 6 values |
| Q9 | `query_verbatim` | Real query strings |
| Q9b | `search_count` (survey-only) | Added 23 Sep: "How many times did you search?" Optional; blank for the 5 pilot rows. Tests **H3** |
| Q10 | `query_language` | Tests **H4** |
| Q11 | `search_mode` | Ask Photos vs classic, per respondent |
| Q12 | `failure_stage` | All 8 values; option order follows the URR decomposition. `cannot_refine` = **H3**, `browse_path_changed` = **H6**. 23 Sep: the refine option was reworded to "I didn't know what to try next" (it overlapped with "got nothing back"); import maps both wordings |
| Q13 | `workaround` | Adds three values not in VOCAB: *re-acquired the document*, and (23 Sep) `requery` and `narrowed`, the refinement moves — decide whether to extend the vocabulary before merging |
| Q14 | `outcome` | All 4 values |
| Q15 | — | Time cost |
| Q16 | — | Consequence: separates nostalgia loss from utility loss |

`specificity` is implicitly `specific_attempt` for anyone who answers Section 2 — the section
instruction forces one specific incident. Record it that way on import.

---

## How to run it

1. Run the script, get the live link.
2. **Screener → personal network / WhatsApp** (fast bookings, the critical path).
   **Survey → LinkedIn, r/googlephotos, r/india** (wide reach, no booking friction).
3. The survey's last two questions route willing respondents into the interview funnel, so it also
   works as a low-friction top of funnel if the screener under-delivers.

---

## Caveats to carry to the deck

- **Self-reported recall of a past search**, not observed behaviour. People misremember what they
  typed. Interviews and the self-run tasks are the corrective; say which evidence came from which.
- **Self-selection**: people who answer a survey about failing to find photos have failed to find
  photos. Prevalence figures from this form describe respondents, not all users — carry the
  denominator, per rule C.
- **Q12 forces a single failure stage** where a real session may cross several. That is deliberate
  for countability; note it rather than over-reading thin differences between stages.
- Three workaround values (`re_acquired`, `requery`, `narrowed`) are not in the engine vocabulary.
  Decide before merging with engine rows.
- **Pilot cut, 23 Sep.** The first 5 responses came before the refinement edits (new search-count
  question, reworded Q12 refine option, two new Q13 options). Report them as the pilot and build
  the failure-stage ranking from later responses, or say plainly that the two are pooled.
