# Part 4 — Define the problem

Drafted 24 Sep against the brief (p.5), not the derived plans. Every internal number is recomputed
from `data/interim/episodes.jsonl` (720 episodes, 144 specific attempts) or taken from `plans/PROGRESS.md`;
external numbers carry a link. **Survey evidence added 1 Oct** (n = 15, `data/interim/survey_episodes.jsonl`,
facts table §G1): shown beside the engine, never pooled, and where the possible duplicate pair moves a
number the dedup figure (n = 14) is given. **Interview evidence is not in yet** — every place it
belongs is marked `[INTERVIEWS]` rather than filled with an assumption.

The brief asks for seven things plus one chain. This document answers them in the brief's order, then
maps each claim to the MVP so the problem slide and the solution slide argue the same thing (the CS2
Clarity failure, −14.35).

| Brief asks for | Section |
|---|---|
| Target user segment | §1 |
| Retrieval scenario | §2 |
| Product outcome to influence | §3 |
| Root cause of retrieval failure | §4 |
| Existing workarounds | §5 |
| Why it creates user value | §6 |
| Why it makes business sense | §7 |
| Metric → Outcomes → Discovery → Behaviour → Problem | §8 |

---

## The problem statement (locked 21 Sep, unchanged)

> People remember **when-ish** and **what happened**; Google Photos indexes **items** and **calendar
> dates**. So the photo is in the library, the person can describe the moment but not the photo, and
> it never comes back. **111 of 144 observed attempts (77%) fail before the user ever needs to
> recover** — the clue is misread (51, 35.4%) or the photo never surfaces (60, 41.7%).

Not *"users find it difficult to search for old photos."* That line appears nowhere in the deck.

---

## 1. Target user segment

**Long-time Photos users chasing a personal photo from a moment they can place only roughly in
time — "around Diwali", "the Goa trip", "last winter", "when I was sick".**

The segment is defined by **the state of the memory**, not by demographics, because that is what the
evidence separates on.

| Criterion | Why | Evidence |
|---|---|---|
| Multi-year library | The problem only exists once the library is too big to scroll | Verbatims cite "pictures dating from 2017", "5 years ago", "older than 4 years", "after 10 years" |
| Target is a personal moment (photo or video) | This is where the brief's goal metric lives | 96 of 144 attempts (67%) are a photo or video; 7 screenshots and 3 documents |
| **The surviving cue is approximate time or a life event** | This is the memory the index cannot use | **42 of 144 (29%)** kept `temporal_approx` or `event_anchor` — the largest group. `temporal_approx` is the single most-retained cue (40) |
| The exact date is gone | Separates this segment from "search in general" | `date` is the **most-lost** cue (37 of 144) |
| **Survey, same shape** | A second, independent source | Roughly when is the most-kept cue (8 of 15), when it was taken the most-lost (9 of 15); 10 of 15 have 5,000+ items; 9 of 15 look for old photos monthly |

**Who is deliberately out:**

| Excluded | n of 144 | Why |
|---|---:|---|
| Users who remember the exact date | 14 | They can precisely describe the photo — the brief says the challenge is *not* general search |
| Users whose learned path moved after an app update (`browse_path_changed`) | 12 | A navigation regression, not a memory problem (H6: real, minor) |
| Loss / backup / sync complaints | (in the 576 general complaints) | The photo may not exist; retrieval cannot fix it |

**Market for the MVP: India.** The MVP resolves Indian festivals and Hinglish time phrases
("pichle saal", "Diwali ke time"). **This is a design choice, not a finding.** H4 (code-mixed
queries) has **only a weak signal**: the engine's `query_language` returned "en" for every audited
post, which is silence, not evidence. The survey found **2 of 15** who search in Hinglish, one typing
*"wedding, pichle saal diwali"* ("last year's Diwali"), a festival-anchored time clue of exactly the
kind the parser resolves. Two people is a quote, not a verdict. `[INTERVIEWS: ≥3 of 6
Hindi–English speakers; record whether any time clue was code-mixed]`

**Segment within the evidence:** the excluded groups overlap the 42 (2 knew the exact date, 3 had a changed path), so **the segment is 37 of 144 (26%)**: 18 `not_surfaced`, 12 `system_misunderstood`, 15 known outcomes (7 not found, 3 slowly, 5 fast). Before removing them, of the 42 time/event attempts, 32 failed at the two stages this
problem targets (20 `not_surfaced`, 12 `system_misunderstood`). Only 15 have a known outcome: 7 not
found, 3 found slowly, 5 found fast. **n is small; say so on the slide.**

---

## 2. The retrieval scenario

**The user knows the moment, not the photo.** They remember roughly when it was and what was
happening, sometimes where. They do not remember the date, the album, or the words the index would
match.

Two scenes from the brief, restated in the segment's terms:

| Brief's example | What survives | What is gone | What Photos needs |
|---|---|---|---|
| "That small café we went to during our Goa trip" | an episode (Goa trip), a scene (café) | date, café name, album | "Goa trip" → a date window; "café" inside it |
| "The medicine I took when I was sick last year" | a life event (sick), rough time (last year) | date, drug name, where it was saved | "when I was sick last year" → a window; "medicine" inside it |

What real users typed, from the engine (verified quotes):

- *"I'll type in something super simple, like **'Halloween 2024'** and it seriously can't find anything?"* — Play Store, `system_misunderstood`, not found
- *"Searching for **'Thanksgiving'** only yields this year's results. You must now specify the year"* — Play Store
- *"Whenever I search for things like **'Wedding'** and press enter, it shows no result"* — Play Store, not found
- *"If I'm looking for a photo, I'm looking for one **I know when I took it**. I've yet to get the photo I'm looking for quickly this way."* — Play Store

Each one names **an event or a rough time**, and the engine tagged all four as failing at
interpretation (`system_misunderstood`).
`[INTERVIEWS: critical-incident step — collect 5–6 of these in the participant's own words, with
the exact query typed]`

---

## 3. The product outcome to influence

**Task success on vague-intent retrieval: the share of retrieval tasks where the user reaches the
target photo** — which rolls up into the goal metric, **URR** (share of users with a vague-intent
task in 28 days who reached the photo on at least one).

```
URR = Expression × [ 1 − (1 − Interpretation × Surfacing × Recognition)^n̄ ]
```

This problem moves **two terms, and says so:**

| Term | Moved by this problem? | Engine (144) | Survey (15) |
|---|---|---|---|
| Expression | No, **but the sources disagree** | `cannot_express` 2 (1.4%) | **3**; 2 of them never typed a search |
| **Interpretation** | **Yes — primary** | `system_misunderstood` 51 (35.4%) | 3 |
| **Surfacing** | **Yes — primary** | `not_surfaced` 60 (41.7%) | **5** (4 dedup) |
| Recognition | Partly | `cannot_evaluate_results` 2 (1.4%) | 2 as the failure, but **6 of 14 ended unsure** they had the right photo |
| Recovery | Not targeted: a light safety net only | `cannot_refine` 1 (0.7%) | 1 (old pilot wording). No term in the shipped URR; measured as a diagnostic (Part 7) |

**Interpretation + Surfacing lead in both sources** (111 of 144; 8 of 15). **Expression is the one
disagreement, and it is argued rather than hidden:** of the survey's 3, two never typed a search
(they scroll), and **all 3 said photos taken just before and after would have helped**. That is what
the moment view gives. A clarifying question would not reach people who never open search, so it
stays cut, and the A/B's entry rate is what would decide otherwise (Part 8, R7 in `parts_7_8_workflow.md`).

**Recognition is larger as an outcome than as a failure stage.** Only 2 of 15 named it as what went
wrong, yet 6 of 14 ended "found the right trip, not the photo" or "similar, not sure". The MVP's
grouping and match ledger are aimed at that group.

**Three URR inputs are now survey-measured** (self-reported, not telemetry): n̄ ≈ 2–3 (9 of 13
searched 2–3 times); first move 9 of 15 scroll the timeline, 5 (4 dedup) type a search; outcome
found 6 · unsure 6–7 · not found 2.

**Every URR baseline is modelled, not measured** — there is no Google telemetry. The slide says so,
and labels the three survey inputs as self-reported.

---

## 4. Root cause

**The index and the memory use different units.** Memory stores *episodes* — a stretch of life with
a rough time and a few scenes. Photos stores *items* with *calendar timestamps*. Retrieval fails at
the join between them, in two ways:

1. **The clue is misread (Interpretation, 35.4%).** Search cannot turn "around Diwali", "last
   winter", "the Goa trip" or "when I was sick" into a date range. Event-relative time — the cue
   people actually keep — has no representation in the query language. *"Halloween 2024"* returning
   nothing is the purest case: a festival plus a year, and still no window.
2. **The photo never surfaces (Surfacing, 41.7%).** Even when the query runs, results are a flat,
   reverse-chronological grid of items. The target is one of hundreds of similar thumbnails across
   years, and nothing narrows it to the episode the user remembers.

**Why this and not the other explanations.** Each pre-registered hypothesis got a verdict (rule B):

| Hypothesis | Verdict | Deciding number (engine) | What the survey added (n = 15) |
|---|---|---|---|
| H1 episodic time | **Supported — the root cause** | `temporal_approx` most kept (40); exact `date` most lost (37) | Same shape: roughly when kept by 8, when it was taken lost by 9 |
| H2 recognition | Supported, secondary → **stronger** | `not_surfaced` 41.7% — answered by grouping into episodes | 6 of 14 ended unsure; top checking aids: place or trip 7, before/after 5, date range 5 |
| H3 dead end | **Refined, not the lead** | Both audit models ranked it first, but from the weakest field (`hypotheses`, Jaccard 0.347). The reliable field (`failure_stage`, κ 0.509) puts `cannot_refine` at 0.7% | 1 of 15 |
| H4 code-mixed | Not tested by the engine → **weak signal** | `query_language` = "en" for all 203 audited posts | 2 of 15 search in Hinglish |
| H5 nothing to index | Weakly supported → **gains a consequence** | CLIP *and* the oracle both score 0.000 on text-in-image tasks | All 3 who had real trouble (had to ask someone or get the document again) were after a document or medicine photo; 0 of 11 ordinary photos |
| H6 learned path | Present, minor | `browse_path_changed` 8.3% | 0 of 15 |

**The mechanism is testable, and was tested — and it works in proportion to what is remembered.**
The same 30 target photos in the 1,282-photo demo library were each searched four times, dropping
one clue per level (120 tasks, `data/eval/*_dropout.json`). Recall@20, plain image search vs the
shipped soft-scoring flow:

| What the person still remembers | Plain search | Memory Trails |
|---|---:|---:|
| Rough time + the place + what it was (L3) | 0.172 | **0.962** |
| Two vague clues, content paraphrased (L2) | 0.209 | 0.276 |
| One vague time clue, content paraphrased (L1) | 0.242 | 0.309 |
| Content only (L0) | 0.312 | 0.312 |
| **Weighted by the cues real attempts kept** | 0.259 | **0.334** |

**Read it as a ladder, not one number.** Turning "roughly when and where" into a window is decisive
when both survive. With a single vague time clue — the most common real memory — the gain is
**+0.07**, and the right photo is never ranked first (hit@1 0.000 at L0–L2). At L0 the flow matches
plain search exactly: it adds no false filters when there is nothing to filter on. At L2, grouping
into moments recovers more than flat ranking does (moment@5 0.333 vs recall@20 0.276), which is
the H2 argument in one number.

**The weighted row is the honest summary.** Only 6 of 144 real attempts (4%) kept three cues; 79
kept one and 47 kept none. Weighting each rung by those counts gives **0.259 → 0.334** recall@20
(+0.075) and 0.225 → 0.336 moment@5 (+0.111). The mapping from a real attempt's cues to a ladder
rung is approximate (`research/analysis/facts_table.md` §E1b).

**Caveat that travels with it:** the tasks are constructed, not collected — the vague phrasings
("a while back", "around last year", "that beach state") were written by us. Real-phrasing numbers
come from Part 6 testing, with their own denominators.

**The audit changing its own answer is on the slide, not hidden.** The ranking that the audit
first produced (H3) was overturned by checking which field it came from. That is the thinking the
brief asks to see.

---

## 5. Existing user workarounds

**Only 21 of 144 attempts (15%) mention a workaround at all. 15 of those 21 are scrolling.**

| Workaround | n | Known outcomes |
|---|---:|---|
| Manual scroll through the library | 10 | 5 not found, 2 slow, 1 fast, 2 unknown |
| Scroll to a date region, then browse | 5 | 2 not found, 3 unknown |
| Another app | 2 | — |
| Old app version / classic search toggle | 2 | — |
| Gave up | 2 | 2 not found |

**Of the 10 scrolling attempts with a known outcome, 7 ended not found.**

**The survey sharpens what scrolling achieves.** 9 of 15 scroll the timeline *first*, before any
search, and 9 scrolled it after search failed. Of those 9, **5 reached the right trip but not the
photo**, 3 found it and 1 did not. Scrolling gets people to the episode; it is picking the photo out
of it that fails. (The engine's "mostly not found" comes from complaint posts; the survey's
respondents were not selected for failing.)

**What the workaround reveals — the design cue.** Scrolling *is* episodic retrieval done by hand:
the user converts "roughly when" into a place on the timeline, then looks for the scene. Photos
makes them do the conversion themselves, and the timeline fights them:

- *"Every time I scrolled to the right time frame, it kept loading more pictures and moving up a
  couple of years ahead."*
- *"Cant remember the pic's date! … Searched thru 2 yrs of pix - nothing"*
- *"Just spent over 1 hr trying to find a photo I had taken of an order that the seller asked for me to upload a pic."*

The MVP automates exactly this step (clue → window → moments) instead of inventing a new
behaviour. `[INTERVIEWS: timeline probe — "when roughly was that?" Record whether they place it by
event, season, relative time or calendar. This is the direct test of H1.]`

---

## 6. Why solving it creates user value

- **The photo is wanted for the moment, not the file.** Personal photos and videos are 67% of
  attempts; the time/event group is where people keep the memory but lose the handle.
- **Failure is the common outcome today.** Of the 62 posts that state an outcome, **46 (74%)
  describe not finding it**, and 5 more were found only slowly. Read it as a floor on frustration,
  not a failure rate: these are posts by people who failed, and `outcome` is the field the audit
  agreed on least (κ 0.161). One user spent "over 1 hr" and still did not find it.
- **The cost is not only time.** A wrong photo taken as the right one is worse than none — one
  user sent a screenshot of a report instead of a birthday cake. Hence false confirmation is the
  MVP's first guardrail (Part 7).
- **Utility photos have deadlines.** Receipts, medicine, orders and documents are retrieved *for* a
  task — a return, a doctor, a claim. Missing them has a cost beyond sentiment. **In the survey, all 3
  people who had real trouble were looking for a document or medicine photo** ("medicine, bill":
  never found, had to get it again); the 11 looking for ordinary photos called it "just annoying".

`[INTERVIEWS: one line per participant on what the photo was for and what not finding it cost them]`

---

## 7. Why it makes business sense for Google Photos

- **Scale.** Photos has **1.5 billion monthly users and over 9 trillion photos and videos**
  ([PetaPixel, May 2025](https://petapixel.com/2025/05/28/google-photos-turns-10-now-hosts-over-9-trillion-photos-and-videos/)).
  Every year a library grows, more of it becomes reachable only by vague memory.
- **Retrieval is what makes storage worth paying for.** Photos draws on the same storage quota as
  Google One, which passed **150 million subscribers** in May 2025
  ([9to5Google](https://9to5google.com/2025/05/15/google-one-150-million/)). An archive the user
  cannot get back into is harder to justify paying for. *This is reasoning, not measured churn —
  there is no telemetry; label it on the slide.*
- **Google already treats retrieval as strategic — and has spent on a different layer.** Ask Photos
  launched Oct 2024, paused Jun 2025 over latency, quality and UX, came back as a hybrid, and got a
  classic/AI toggle in 2026. That work fixed **how queries are routed and how fast results come
  back**. None of it gives the index **episodes or event-relative time**. This opportunity sits
  beside Ask Photos, not against it, and a reviewer's first question — "isn't this Ask Photos?" —
  has an answer. **Survey:** 7 of 15 had never heard of Ask Photos, and every respondent who reported
  a result (4; 3 dedup) said it showed "related photos, but not the one I wanted" and that they "could
  not tell why". Explaining the match is the gap. `[Ask Photos re-run of the 4 failed probe
  searches: pending (plan §8b)]`
- **Low-cost intelligence.** Intelligence is needed in two places only: turning a clue into a
  window, and grouping the library into episodes. Both run on metadata Photos already holds
  (timestamps, location, bursts). The MVP does the first with rules and falls back to an LLM.

---

## 8. How the thinking evolved

**Business metric → Product outcomes → AI-powered discovery → Observed user behaviour → Problem
definition.** Each step changed the answer the step before it gave.

| Step | What we believed going in | What changed it | What we believed after |
|---|---|---|---|
| **Business metric** | Success rate per *search* (SRR-V) | The brief counts the **percentage of users** (p.2) | **URR**, user-level; the unit underneath is a **retrieval task**, not a query. A/B randomises by user |
| **Product outcomes** | v1 plan: build a **recovery agent** that asks questions after a failed search | Decomposition into Expression · Interpretation · Surfacing · Recognition · Recovery, each with its own failure | The opportunity could sit at any of five stages; the engine had to choose |
| **AI-powered discovery** | Front-runner H1 (episodic time), challengers H3, H4, H6 | 85,140 posts → 720 episodes → 144 specific attempts. **The audit first ranked H3 first**, then that turned out to rest on the weakest field. `cannot_refine` = 0.7% | **Recovery cut.** Failures cluster *before* recovery: misread 35.4%, never surfaced 41.7% |
| **Observed user behaviour** | Users search, fail, retry | Where a workaround is mentioned, 15 of 21 are **scrolling to a time region** — doing the episode conversion by hand, and mostly failing (7 of 10 known). Survey: 9 of 15 scroll first; of 9 who scrolled after a failed search, 5 reached the trip but not the photo | Users already think in episodes and get to the episode by hand; the product should do that step and help them pick the photo out of it. `[INTERVIEWS: confirm or overturn]` |
| **Problem definition** | "Search is bad at old photos" | All of the above | **People remember when-ish and what happened; Photos indexes items; so the photo never surfaces.** |

**What would reopen this:** the interviews showing heavy `cannot_refine` (brings Recovery back), or a
real Hinglish signal (moves H4 from weak to supported). **The survey has answered part of it:**
`cannot_refine` 1 of 15, so Recovery stays out; Hinglish 2 of 15, so H4 moves from untested to weak,
not supported. It also raised one thing the engine had not: "didn't know what to type" at 3 of 15
against 1.4%, argued in §3.

---

## 9. Consistency check — problem slide vs solution slide

Rule A. Every claim above must be served by something the MVP ships, or be cut.

| Problem claim | MVP feature that serves it |
|---|---|
| Event-relative time is misread | Clue chips: festivals, seasons, "N years ago", trip-relative time, Hinglish → a visible, editable date window |
| The photo never surfaces in a flat grid | Results grouped into **moments** (episodes), not a grid of items |
| The user scrolls to a time region by hand | The window does that step; "just outside your dates" covers a near-miss |
| A hard filter could hide the photo (our own `not_surfaced`) | Soft scoring: metadata ranks, it does not exclude |
| Wrong-photo confirmation is costly | Per-card match ledger ("Goa ✓ · café ✓ · date +21 days"); false confirmation is a guardrail |
| Recovery is not the target (0.7%) | **One question after "Not this moment", each answer changing one clue. It is a safety net, kept out of URR, and the slide says why** |

---

## 10. What the interviews must add before this goes on a slide

The brief says Part 4 is based on the discovery engine **and primary research**. The survey
(n = 15) is the primary research in hand; until the interviews run, nothing here is observed
behaviour, and the deck must not imply otherwise.

| Slot | Interview step | Confirms / overturns |
|---|---|---|
| Segment fit | Screener: 2+ years, 5,000+ items, a failed old-photo search in the last 3 months | §1 |
| Scenario in their words | Critical incident: target, what they remembered, exact query | §2 |
| How they place it in time | Timeline probe | **H1 — the root cause** (§4) |
| Did they scroll past it? | Recognition probe | H2 (§4), workarounds (§5) |
| Code-mixed clues | Any Hindi–English time phrase | H4 (§1) |
| What it cost them | Close of the critical incident | User value (§6) |

**Deck slides this feeds:** *Chosen target segment*, *Root cause*, *Problem definition*. Suggested
titles (each states the message):

1. "People keep the moment and lose the date — 29% hold a rough time or event, and 37 lost the exact date"
2. "77% of attempts fail before recovery — the clue is misread or the photo never surfaces"
3. "Users already scroll to 'roughly when' by hand and land on the trip but not the photo"
