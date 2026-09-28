# Deck skeleton: NL_GooglePhotos

**Started 28 Sep 2026.** Ten slides, no separate title slide, because a title slide would count
against the ten. Every number comes from `research/analysis/facts_table.md`, and the reference in brackets (§B, §E…) is the facts-table row.
**`[GAP]` marks content that waits on interviews, the survey or MVP tests. Do not fill a gap with an
assumption.**

## Constraints (brief p.8–9, lessons doc §4)

- 10 slides max · each title states the message · min 14 pt (Slides/PPT) · colour-blind-safe palette
- No name anywhere, **including PDF metadata** · file `NL_GooglePhotos.pdf` · under 40 MB
- Every linked artefact opens for the reader in an incognito window
- The phrase *"users find it difficult to search for old photos"* appears nowhere

## Brief coverage: every required item has a slide

| Brief deliverable (p.7–8) | Slide |
|---|---|
| Business metric decomposition | 2 |
| 1-slide explanation of the discovery workflow + link | 3 |
| Discovery-engine findings | 4 |
| User research and observed retrieval tasks | 5 |
| Chosen target segment · Root cause | 6 |
| Problem definition · Solution rationale | 7 |
| MVP (+ link) | 8 |
| User testing | 9 |
| Success metrics · Risks and limitations | 10 |
| Thinking evolved: metric → outcomes → discovery → behaviour → problem (Part 4) | spine of 2 → 7, made explicit on 7 |

**The one test for every slide (rule A):** does it argue the locked problem statement?

> People remember *when-ish* and *what happened*; Google Photos indexes *items*. So the photo is
> there, the person can describe the moment but not the photo, and it never surfaces.

---

## Slide 1: The goal and the answer, in one screen

**Title:** People keep the moment and lose the date, but Photos indexes photos, not moments

- The strategic goal, quoted: *increase the percentage of users who successfully retrieve a photo
  they remember but cannot precisely describe.*
- The answer in one line: 77% of observed failed attempts break **before** recovery could help. The
  clue is misread (35.4%) or the photo never surfaces (41.7%). §B
- What was built: an evidence engine over 85,140 public posts, and an MVP that turns "roughly when
  and where" into moments to browse. §A
- Two links, hyperlinked: Discovery engine · Memory Trails MVP
- **Visual:** one MVP screenshot (`design/mvp-screenshots/4-moments.jpg`) beside the 77% number

## Slide 2: Business metric decomposition

**Title:** Retrieval breaks at interpretation and surfacing, not at expression or recovery

- **URR** = share of users with a vague-intent retrieval task in 28 days who reached the photo on at
  least one. The unit underneath is one **target photo**, not one query. A/B randomises by user.
- `URR = Expression × [1 − (1 − Interpretation × Surfacing × Recognition × Recovery)^n̄]`
- Where the 144 real attempts broke: Expression 1.4% · **Interpretation 35.4%** · **Surfacing
  41.7%** · Recognition 1.4% · Recovery 0.7%. §B
- Where Google has already invested: Ask Photos, the hybrid, and the classic/AI toggle all work on routing and speed. Episodes and event-relative time are still open.
- **Label on slide:** every baseline is modelled, not measured, because there is no Google telemetry.
  `[GAP: survey Q3 → n̄, Q4 → Expression, Q14 → outcome mix, which turn three modelled slots into measured ones]`
- **Visual:** the five terms as a horizontal chain, bar under each showing its failure share

## Slide 3: How the discovery engine works (required 1-slide explanation)

**Title:** A pre-registered engine read 85,140 posts, then a second model family was allowed to overturn it

- Funnel: 85,140 posts (Play Store, App Store, YouTube, Reddit) → 5,305 Gate A → 1,333 screened,
  819 relevant → 720 episodes → **144 specific attempts** → 62 scoreable. §A
- **What makes it more than summarisation:**
  1. A fixed schema (remembered · forgotten · where it broke · outcome) and a ranking rule written
     **before** seeing the data, so it had to choose between explanations
  2. A blind audit by `qwen3.8-27b`, a different model family, on 203 pairs. It **did** overturn the
     first ranking. §C
- Link: https://retrieval-discovery-engine.vercel.app
- **Footnote disclosures:** Play Store 86.2% of episodes · evidence-verified 85.2% on the audit
  sample (n=203) · extraction closed at 720 of 819 deliberately. §C §D
- **Visual:** the vertical funnel with counts; a side box for the audit loop

## Slide 4: Discovery-engine findings

**Title:** People remember roughly when and forget the exact date, which is the one thing search can't use

- The brief's four questions, answered from 144 attempts. §B §B2
  - Struggle to retrieve: photos 80 · multiple 26 · video 16 · screenshots 7
  - Remember: **approximate time 40** · object 17 · exact date 14 · text in image 12
  - Forget: **exact date 37** · album 29 · the words to search 10
  - How they search: classic 27 · Ask Photos 10 · both 4 (103 don't say)
- **Hypothesis verdicts (rule B, every one stated):** H1 episodic time **supported, root cause** ·
  H2 recognition supported, secondary · **H3 dead end refined, not the lead** · H4 code-mixed **not
  tested** · H5 nothing to index weakly supported · H6 learned path present, minor
- **The audit overturning itself, stated:** both models ranked H3 first, but from the least reliable
  field (`hypotheses`, Jaccard 0.347). The reliable field (`failure_stage`, κ 0.509) puts
  `cannot_refine` at 0.7%. We trusted `failure_stage`. §C
- **Visual:** paired bars "remembered vs forgotten" by cue; verdict table beneath

## Slide 5: User research and observed retrieval tasks: **[GAP, whole slide]**

**Title (draft, rewrite from what the interviews show):** In their own words, participants placed the photo by event or season, never by date

- **Method:** 5–6 interviews, 40 min: critical incident → self-run searches with camera off →
  timeline probe → recognition probe. Screener: 2+ years, 5,000+ items, a failed search in the last 3 months.
  ≥3 Hindi–English speakers (H4).
- `[GAP: interviews n=__; one row per participant: what they wanted · what they remembered · exact query typed · where it broke · outcome]`
- `[GAP: timeline probe: how many placed it by event / season / relative time / calendar → confirms or overturns H1]`
- `[GAP: survey n=__, shown next to the engine and never pooled with it (hypotheses rule-derived vs model-assigned)]`
- `[GAP: own-library probe, 6 photos × 2 searches (research/testing/probe-log.csv)]`
- **Carry:** self-selection, self-report vs observed behaviour; scrub names from query strings
- **Visual:** a table with one row per participant, with the exact query in quotes

## Slide 6: Target segment and root cause

**Title:** The segment is people holding only a rough time or event; the index can't turn that into a window

- **Segment:** long-time users chasing a personal moment they can place only roughly: "around
  Diwali", "my sister's graduation", "the week we moved out". Defined by the state of the memory, not by demographics.
  - 42 of 144 (29%) kept only rough time or an event, the largest group; 67% of targets are personal
    photos or videos. §B2
  - **Out, on purpose:** the 14 who remember the exact date (that is general search), the 12 whose
    learned path moved (H6), and loss/backup complaints
- **Root cause:** memory stores *episodes*; Photos stores *items with calendar timestamps*.
  1. The clue is misread: "Halloween 2024" returns nothing (real Play Store quote)
  2. The photo never surfaces: a flat grid across years with nothing narrowing it to the episode
- **Market choice (India, festivals, Hinglish time phrases) is a design choice, not a finding.** H4 is untested.
  `[GAP: interviews confirm segment fit and H1]`
- **Visual:** two-column "what memory keeps / what the index keys on"

## Slide 7: Problem definition and solution rationale

**Title:** Users already scroll to "roughly when" by hand and mostly fail, so the product should do that step

- **Problem statement** (locked, verbatim, the only framing used)
- **Workaround = the design cue:** 21 of 144 mention a workaround; 15 of those are scrolling to a
  time region, and 7 of 10 with a known outcome didn't find it. §B2
- **User value:** 46 of 62 known outcomes (74%) ended not found; utility photos (receipts,
  medicine) have deadlines. **Business sense:** 1.5B monthly users, 9T+ items; retrieval is what
  makes paid storage worth keeping (reasoning, not measured churn). §B2 external
- **Where intelligence is needed (brief Part 5), and only there:** (1) clue → date window, (2)
  library → episodes. Both run on metadata Photos already holds.
- **Why not Ask Photos:** it fixed routing and speed; it has no editable clues, no episode-grouped
  results and no match explanations. Name it and say what it does well.
- **Scoped, with the number:** the clarifying question is cut (`cannot_express` 1.4%); near-miss
  recovery is one question after "Not this moment", a safety net rather than the product (`cannot_refine` 0.7%)
- **Thinking evolved** (one line per step): search-level metric → user-level URR · recovery agent →
  recovery reduced to a safety net · H3 lead → overturned · "search is bad" → the locked statement
- **Visual:** the evolution as a 5-step strip across the top

## Slide 8: The MVP

**Title:** Memory Trails turns "roughly when and where" into moments you can recognise

- **Where it lives:** a feature inside Photos search. When a plain search fails, "Can't describe it?" opens it
  with the query carried over. It needs the user's own library and timeline.
- **Flow:** describe → clue chips (editable, with resolved dates) → up to 5 likely moments → open a
  moment → confirm ("You found the moment"). Match ledger on each card: `sister's graduation ✓ · cake ✓`,
  and "Why this moment?" says whether each clue is in the photo, in nearby photos, or approximate
- **Demo task (same as the prototype's first example):** "the photo of the handmade cake from my
  sister's graduation". Three more: college performance, handwritten note, dog in the suitcase
- **Limitation, in these words:** "This MVP validates the memory-reentry interaction and recovery model
  using representative media. It does not validate production-scale Google Photos retrieval accuracy."
- **Built for the failure it targets:** soft scoring, so a wrong date demotes a photo and never
  hides it; an outside-window strip; "Not in any of these?"
- **Measured, shown as a ladder** (120 tasks, 1,282-photo library, recall@20, plain → Memory Trails). §E1

  | Still remembers | Plain | Memory Trails |
  |---|---:|---:|
  | Rough time + place + what | 0.172 | **0.962** |
  | Two vague clues | 0.209 | 0.276 |
  | One vague time clue | 0.242 | 0.309 |
  | Content only | 0.312 | 0.312 |

- **Say plainly:** the gain is decisive when place survives and modest with one vague clue (right
  photo never ranked first below L3); the tasks were written by us; the library's metadata is synthetic
  over real CC photos.
- Link: https://memory-trails-demo.vercel.app
- **Visual:** 3–4 screenshots in sequence from `design/mvp-screenshots/` (retaken from the live site 28 Sep):
  `2-describe`, `3-clues`, `4-moments`, `7-found`; `6-recover` if slide 9 needs the recovery step

## Slide 9: User testing: **[GAP, whole slide]**

**Title (draft, rewrite from the results):** [what the 3 participants' sessions showed, stated as the message]

- **Method:** ≥3 people from the Part 3 interviews, on their **own** remembered incident rewritten as
  a task against the demo library; `?study=P0N` session log; protocol in
  `research/testing/mvp_test_protocol.md`
- `[GAP: success n/3 within 5 min · time to confirm · episodes viewed · clue corrections]`
- `[GAP: false confirmations, the guardrail that matters most]`
- `[GAP: top 2 issues found → what changed → light re-test]`
- `[GAP: what we'd change in the next iteration, as the brief asks]`
- **Visual:** a table with one row per participant and a quote per row

## Slide 10: Success metrics, risks and limitations

**Title:** Success is more users reaching the photo, and the biggest risk is that the win sits where memory is richest

- **Outcome:** URR with no Recovery term. Recovery ships only as a safety net for 0.7% of failures, so
  it is tracked as a diagnostic (near-miss recovery rate) instead
- **Leading** (each tied to a URR term and a live event): entry rate · clue-correction rate ·
  episode-open rate · confirm-after-open · time to first episode
- **Guardrails:** **false confirmation** (the worst failure) · sensitive-query exposure · p95 latency ·
  abandonment before the first moment appears
- **Risks → mitigation:**
  - R1: the gain is +0.79 at L3 but +0.07 at L1, where most users sit, and our tasks were written by us → lean on
    recognition, measure L1 in testing
  - R2: our own filter could hide the photo → soft scoring (**built**)
  - R3: the index can't read text in images (0.000) → OCR/captions
  - R4: false confirmation → nothing auto-confirms; measure it
  - R5: recovery was kept light on a number from 86% Play Store data → survey measures it; the safety
    net already logs which answer led to a find
  - R6: Ask Photos may already be enough → survey's Ask Photos block
- **Limitations:** Play Store 86.2% · H4 untested · URR baselines modelled · ranking weights are judgement
- **Visual:** metrics tree on the left, risk table on the right

---

## Open before building slides

1. **Slides 5 and 9 need the interviews and tests.** Everything else can be laid out now.
2. **Density:** slides 7 and 10 carry the most. At 14 pt they may overflow; cut prose before cutting a
   required item.
3. **Format:** Google Slides / PPT (14 pt min) or Figma/Canva at 1920×1080 (26/22 pt min), decided before layout.
