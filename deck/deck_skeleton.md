# Deck skeleton: NL_GooglePhotos

**Started 28 Sep 2026.** Ten slides, no separate title slide, because a title slide would count
against the ten. Every number comes from `research/analysis/facts_table.md`, and the reference in brackets (§B, §E…) is the facts-table row.
**`[GAP]` marks content that waits on interviews or MVP tests. Do not fill a gap with an
assumption.** **Survey (n = 15, closed 1 Oct) is filled in (§G1).** Survey numbers always sit
*beside* engine numbers, never pooled: survey hypotheses are rule-derived, engine ones model-assigned.
Where the possible duplicate (`survey:0010`) moves a number, quote the dedup figure (n = 14).

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
- **A second source agrees:** in a 15-person survey, people kept roughly *when* (8) and lost the
  date (9), and 6 of 14 ended unsure they had the right photo (4 reached the right trip, not the
  photo). §G1
- What was built: an evidence engine over 85,140 public posts, and an MVP that turns "roughly when
  and where" into moments to browse. §A
- Two links, hyperlinked: Discovery engine · Memory Trails MVP
- **Visual:** one MVP screenshot (`design/mvp-screenshots/4-moments.jpg`) beside the 77% number

## Slide 2: Business metric decomposition

**Title:** Retrieval breaks most at interpretation and surfacing, and almost never at recovery

- **URR** = share of users with a vague-intent retrieval task in 28 days who reached the photo on at
  least one. The unit underneath is one **target photo**, not one query. A/B randomises by user.
- `URR = Expression × [1 − (1 − Interpretation × Surfacing × Recognition)^n̄]`: the same formula
  as slide 10 and Part 4. **No Recovery term:** it serves 0.7% of failures and ships only as a safety
  net, tracked as a diagnostic (near-miss recovery rate)
- Where the 144 real attempts broke: Expression 1.4% · **Interpretation 35.4%** · **Surfacing
  41.7%** · Recognition 1.4% · Recovery 0.7% (outside the formula). §B
- **Survey, shown beside it (n = 15):** Expression 3 · **Interpretation 3** · **Surfacing 5** (4 dedup) ·
  Recognition 2 · Recovery 1 · gave up 1. §G1 Interpretation + Surfacing still lead (8 of 15).
  **Expression is the one disagreement** (1.4% vs 3 of 15); 2 of those 3 never typed a search, they
  scroll. State both numbers; do not hide either.
- **Recognition is bigger as an outcome than as a failure stage:** only 2 of 15 named it as what
  went wrong, but 6 of 14 *ended* unsure (right trip, not the photo; or similar but not sure). §G1
- Where Google has already invested: Ask Photos, the hybrid, and the classic/AI toggle all work on routing and speed. Episodes and event-relative time are still open.
- **Label on slide:** every baseline is modelled, not measured, because there is no Google telemetry.
  Three inputs are now **survey-measured** (n = 15, self-reported, not telemetry): **n̄ ≈ 2–3**
  (9 of 13 searched 2–3 times) · **first move:** 9 of 15 scroll the timeline, 5 (4 dedup) type a search ·
  **outcome mix:** found 6 · unsure 6–7 · not found 2. §G1
- **Visual:** the four terms as a horizontal chain, two bars under each (engine %, survey count);
  Recovery drawn apart and greyed, labelled "diagnostic, 0.7% · survey 1 of 15"

## Slide 3: How the discovery engine works (required 1-slide explanation)

**Title:** The engine turns 85,140 public posts into 144 retrieval attempts, each recording what was remembered, what was forgotten, and where search broke

**Drafted 2 Oct.** Every number checked against facts table §A, §C, §D.

**Band 1: the pipeline (five boxes, left to right, count under each)**

| 1 · Collect | 2 · Screen | 3 · Extract | 4 · Audit | 5 · Compare |
|---|---|---|---|---|
| **85,140** public posts: Play Store 81,256 · App Store 2,732 · YouTube 696 · Reddit 456 | Keyword gate → **5,305**; model screen labels 1,333 → **819 relevant** | Fixed schema → **720 episodes** → **144 specific attempts** | A second model family re-reads **203** episodes blind | **9 opportunity areas**, ranked only on fields both models agree on |
| scrapers | rules, then `gpt-oss-120b` | `gpt-oss-120b`, the same schema every time | `qwen3.8-27b` | where it broke × what was remembered |

**Band 2: what each attempt records → the brief's questions (left: field; right: question it answers)**

- `asset_type` → *What kinds of old photos do users struggle to retrieve?*
- `cues_retained` (14 cue types) → *What do people actually remember?*
- `cues_lost` (date · place · album · people · words · filename) → *What have they forgotten?*
- `query_verbatim` · `search_mode` → *How do they search when memory is incomplete?*
- `failure_stage` (cannot express · misunderstood · not surfaced · can't evaluate · can't refine) →
  *Where does retrieval break?* (the Part 3 decomposition)

**Band 3: why this is more than summarising reviews (three short lines)**

1. **Structure, not sentiment.** Each post becomes a record you can count and compare, not a mood score.
2. **The rules came first.** Schema and hypotheses (H1–H5) were written before reading any results, so the engine
   had to choose between explanations instead of confirming one.
3. **It can overrule itself.** The blind audit agreed on *where search broke* (κ 0.509) but not on
   *which hypothesis* (Jaccard 0.347), so the ranking uses the first and drops the second. §C

**Link (hyperlinked, large):** retrieval-discovery-engine.vercel.app. *Try it:* describe a photo
you can't find, and the engine extracts your cues and compares them with real attempts.

**Footnote (≥14 pt, one line):** 86.2% of episodes come from Play Store · quotes verified in the
source for 85.2% (audit sample, n = 203) · extraction stopped at 720 of 819 on purpose · only
62 attempts state an outcome. §C §D

- **Visual:** a horizontal five-box pipeline with counts that narrow left to right; under it, a two-column
  "field → brief question" table; a small audit loop arrow from box 4 back to box 5
- **Not on this slide** (they belong on Slide 4): the findings themselves, hypothesis verdicts, and survey numbers

## Slide 4: Discovery-engine findings

**Title:** People remember roughly when, but search needs the exact date, and the exact date is what they forget

**Drafted 3 Oct.** Engine numbers recomputed from `data/interim/episodes.jsonl` (144 specific
attempts) and `evidence.json`; survey numbers from facts table §G1. Survey always sits *beside*
the engine, never added to it.

**Band 1: the brief's four questions, answered (four tiles, one bar row each)** §B §B2

| Brief question | Engine (144 attempts) | Survey (n = 15) |
|---|---|---|
| *What kinds of old photos do users struggle to retrieve?* | Personal photos 80 · several at once 26 · videos 16 · screenshots 7 · documents 3 | All 3 cases of **real trouble** were a document or medicine photo |
| *What do people actually remember?* | **Roughly when 40** · an object 17 · the exact date 14 · text in the photo 12 · who was there 10 · an event 9 | **Roughly when 8** · object 7 · who was there 6 |
| *What have they forgotten?* | **The date 37** · the album 29 · the words to search 10 · the place 10 | **When it was taken 9** · the words to search 9 |
| *How do they search with an incomplete memory?* | Of 32 quoted queries, **20 are one word** ("dog", "Wedding"); **10 name a time** ("Halloween 2024", "December 2017") | First move is scrolling for **9 of 15**; 2 search in Hinglish ("wedding, pichle saal diwali") |

**Band 2: comparing the opportunity areas (compact table, 6 rows)** from the engine's O1–O9 table

| Area | Attempts | Where it mostly breaks | Not found (of known outcomes) | In the brief's scope? |
|---|---:|---|---:|---|
| **O1 Rough time or an event** | **42** | never surfaced (20) | 7 of 15 | **Yes, the core** |
| O8 No clue at all | 47 | never surfaced (26) | 14 of 15 | Partly: nothing to search with |
| O3 An object | 17 | misread (11) | 6 of 11 | Yes |
| O7 The exact date | 14 | misread (7) | 7 of 8 | No: a precise description |
| O2 Text in the photo | 12 | misread (8) | 5 of 8 | Yes, but needs OCR |
| O9 Path moved by an app update | 12 | path changed (12) | — | No: app design |

One line under it: **O8 is bigger, but those 47 people kept no clue to search with. O1 is the largest
group whose memory search could use and doesn't.** Areas overlap, because one attempt can keep several clues.

**Band 3: what this rules in and out (one strip)** Part 4, rule B

- **H1 episodic time: supported, the root cause.** Roughly when is the clue people keep most, and the date is the clue they lose most, in both the engine and the survey.
- **H2 recognising the right result: supported, secondary.** 41.7% never surfaced, and in the survey, 6 of 14 ended unsure.
- **H3 dead end: refined, not the lead.** Both models first ranked it top, but from the weakest field
  (Jaccard 0.347). The reliable field (κ 0.509) puts "can't refine" at **0.7%**. We went with the reliable field. §C
- H4 Hinglish: not tested by the engine, weak signal (2 of 15) · H5 nothing to index: weak, but it is where
  the real-world harm is · H6 path changed: present, minor (8.3%)

**Footnote:** quoted queries exist for only 32 of 144 attempts, and only 62 of 144 state an outcome ·
86.2% of episodes come from Play Store, a complaint-heavy source · survey: convenience sample, 14 after dedup

- **Visual:** Band 1 as paired bars per question (engine above, survey below, never stacked);
  Band 2 as a compact table with the O1 row highlighted; Band 3 as a single verdict strip
- **If it's crowded, cut in this order:** H4–H6 line → survey column of Band 1 → Band 2 rows O2 and O9.
  Never cut the O8 line: without it, the claim that O1 is "the largest" is false.

## Slide 5: User research and observed retrieval tasks: **survey filled; [GAP] interviews, probe**

**Title (draft, rewrite from what the interviews show):** In their own words, participants placed the photo by event or season, never by date

- **Method:** 5–6 interviews, 40 min: critical incident → self-run searches with camera off →
  timeline probe → recognition probe. Screener: 2+ years, 5,000+ items, a failed search in the last 3 months.
  ≥3 Hindi–English speakers (H4).
- `[GAP: interviews n=__; one row per participant: what they wanted · what they remembered · exact query typed · where it broke · outcome]`
- `[GAP: timeline probe: how many placed it by event / season / relative time / calendar → confirms or overturns H1]`
- **Survey (filled, §G1): n = 15, responses 23–30 Sep**, 12 mainly on Google Photos, 10 with 5,000+
  items, 9 looking for old photos monthly. Shown next to the engine, never pooled.

  | | Engine (144 attempts) | Survey (15) |
  |---|---|---|
  | Most remembered | approximate time (40) | roughly when (8) |
  | Most forgotten | exact date (37) | when it was taken (9) |
  | Top failure stage | not surfaced 41.7% | not surfaced 5 (4 dedup) |
  | Didn't know what to type | 1.4% | 3 (2 never typed) |
  | Ended unsure | not measurable | **6–7** |

- **What they did:** 9 of 15 scroll the timeline *first*, and 9 scrolled it after search failed; of
  those 9, **5 reached the right trip but not the photo**, 3 found it, 1 did not. §G1
- **Ask Photos:** 7 of 15 had never heard of it. Every respondent who reported a result (4; 3 dedup)
  said it showed "related photos, but not the one I wanted" and that they "could not tell why". §G1
- **Quotes (typed queries, verbatim):** *"wedding, pichle saal diwali"* (Hinglish, anchored to a
  festival, not a date) · *"medicine, bill"* (never found; had to get the document again)
- `[GAP: own-library probe, 6 photos × 2 searches (research/testing/probe-log.csv)]`
- **Carry:** self-selection, self-report vs observed behaviour; scrub names from query strings.
  Survey: n = 15 against a target of 30, from the author's network; one possible duplicate pair;
  5 internally inconsistent answers, listed in §G1
- **Visual:** left, the engine-vs-survey table; right, one row per interview participant with the
  exact query in quotes. If interviews do not land, the survey table takes the slide and the gap is
  stated, not filled

## Slide 6: Target segment and root cause

**Title:** The segment is people who can place the moment only roughly; the index can't turn that into a window

- **Segment:** long-time users chasing a personal moment they can place only roughly: "around
  Diwali", "my sister's graduation", "the week we moved out". Defined by the state of the memory, not by demographics.
  - 42 of 144 (29%) kept a rough time or an event (33 kept nothing else), the largest group; 67% of targets are personal
    photos or videos. §B2
  - Survey: 8 of 15 kept rough time or an event; 10 of 15 have 5,000+ items; 9 of 15 look for
    old photos monthly. §G1
  - **Out, on purpose:** the 14 who remember the exact date (that is general search), the 12 whose
    learned path moved (H6), and loss/backup complaints
- **Root cause:** memory stores *episodes*; Photos stores *items with calendar timestamps*.
  1. The clue is misread: "Halloween 2024" returns nothing (real Play Store quote)
  2. The photo never surfaces: a flat grid across years with nothing narrowing it to the episode
- **Market choice (India, festivals, Hinglish time phrases) is a design choice, not a finding.** H4
  has a weak signal only: 2 of 15 search in Hinglish, one as *"pichle saal diwali"* ("last year's
  Diwali"), a festival-anchored time clue the parser is built for. Two people is a quote, not a verdict.
  `[GAP: interviews confirm segment fit and H1]`
- **Visual:** two-column "what memory keeps / what the index keys on"

## Slide 7: Problem definition and solution rationale

**Title:** Users already scroll to "roughly when" by hand and land on the trip but not the photo, so the product should do that step

- **Problem statement** (locked, verbatim, the only framing used)
- **Workaround = the design cue:** 21 of 144 mention a workaround; 15 of those are scrolling to a
  time region, and 7 of 10 with a known outcome didn't find it. §B2 **Survey:** 9 of 15 scrolled the
  timeline after search failed; 5 of them reached the right trip but not the photo. §G1
- **User value:** of 62 posts that state an outcome, 46 (74%) describe not finding it (posts by
  people who failed; `outcome` κ 0.161); utility photos (receipts,
  medicine) have deadlines: **in the survey, all 3 people who had real trouble (had to ask someone
  or get the document again) were looking for a document or medicine photo.** §G1 **Business sense:** 1.5B monthly users, 9T+ items; retrieval is what
  makes paid storage worth keeping (reasoning, not measured churn). §B2 external
- **Where intelligence is needed (brief Part 5), and only there:** (1) clue → date window, (2)
  library → episodes. Both run on metadata Photos already holds.
- **Why not Ask Photos:** it fixed routing and speed; it has no editable clues, no episode-grouped
  results and no match explanations. Name it and say what it does well. **Survey:** 7 of 15 had never
  heard of it, and every respondent who reported a result (4; 3 dedup) got "related photos, not
  mine" and "could not tell why". That is the gap the match ledger fills. §G1
  `[Ask Photos re-run of the 4 failed probe searches: pending (plan §8b)]`
- **Scoped, with the numbers from both sources:** the clarifying question stays cut, but not on
  1.4% alone. The survey puts "didn't know what to type" at 3 of 15; **2 of those 3 never typed a
  search, and all 3 asked for the photos just before and after**, which the moment view already
  gives. A question would not reach people who scroll. Near-miss recovery is one question after "Not
  this moment", a safety net rather than the product (`cannot_refine` 0.7%; survey 1 of 15)
- **Thinking evolved** (one line per step): search-level metric → user-level URR · recovery agent →
  recovery reduced to a safety net · H3 lead → overturned · Expression cut on 1.4% → re-argued when
  the survey said 3 of 15 · "search is bad" → the locked statement
- **Visual:** the evolution as a 5-step strip across the top

## Slide 8: The MVP

**Title:** Memory Trails turns "roughly when and where" into moments you can recognise

- **Where it lives:** a feature inside Photos search. When a plain search fails, "Can't describe it?" opens it
  with the query carried over. It needs the user's own library and timeline.
- **Flow:** describe → clue chips (editable, with resolved dates) → up to 5 likely moments → open a
  moment → confirm ("You found the moment"). Match ledger on each card: `sister's graduation ✓ · cake ✓`,
  and "Why this moment?" says whether each clue is in the photo, in nearby photos, or approximate.
  **These are what survey respondents asked for** to check a close result: the place or trip (7),
  photos just before or after (5), a rough date range (5). §G1
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
  | **Weighted by what real people remember** | 0.259 | **0.334** |

- **The weighted line is mandatory.** Only 6 of 144 real attempts (4%) kept the three clues that L3
  needs; weighting each rung by real cue counts gives +0.075 recall and +0.111 moment@5. §E1b

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
  - R5: recovery was kept light on a number from 86% Play Store data → **survey agrees (1 of 15)**;
    the safety net already logs which answer led to a find
  - R6: Ask Photos may already be enough → **survey: 7 of 15 had not heard of it, and all who reported
    a result got related photos they could not explain**; the probe re-run is still pending
  - R7: the survey disagrees on Expression (3 of 15 vs 1.4%) → the moment view serves the scrollers
    who make up 2 of the 3; a measured entry rate in the A/B decides if a question is needed
- **Limitations:** Play Store 86.2% · H4 a weak signal only (2 of 15) · URR baselines modelled ·
  ranking weights are judgement · survey n = 15 from the author's network, self-reported, with one
  possible duplicate
- **Visual:** metrics tree on the left, risk table on the right

---

## Open before building slides

1. **Slides 5 and 9 need the interviews and tests.** Slide 5's survey half is filled (1 Oct). Everything else can be laid out now.
2. **Density:** slides 7 and 10 carry the most. At 14 pt they may overflow; cut prose before cutting a
   required item.
3. **Format:** Google Slides / PPT (14 pt min) or Figma/Canva at 1920×1080 (26/22 pt min), decided before layout.
