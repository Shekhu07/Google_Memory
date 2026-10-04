# Deck skeleton: NL_GooglePhotos

**Started 28 Sep 2026, completed 4 Oct 2026.** Ten slides, no separate title slide, because a title slide would count
against the ten. Every number comes from `research/analysis/facts_table.md`, and the reference in brackets (§B, §E, §G…) is the facts-table row.
**All research is complete:** Part 3 was run as the survey (n = 15, closed 1 Oct, §G1); Part 6 user testing was run with 6 participants from the target segment (closed 4 Oct, §G2). Survey and test numbers always sit beside engine numbers, never pooled.
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

**Redrafted 3 Oct** against brief Part 2: "break down *successful retrieval of vaguely remembered
photos* into user behaviours **and** product outcomes". Engine numbers recomputed from
`episodes.jsonl` (144 attempts); survey from `survey_episodes.jsonl` (15; dedup 14 in brackets).

**The tree (the main visual, top to bottom: metric → path → outcome → behaviour)**

**Level 0, the metric (the brief's words, then ours):** *Successful retrieval of vaguely remembered
photos*, measured as **URR**: of users with at least one vague-memory retrieval task in 28 days, the share who
reached the photo on at least one. One task = one target photo, not one query. The A/B splits by user.

**Level 1, the user's path (a behaviour: what they do first)**

| Path | Survey: first move | Engine |
|---|---|---|
| **Search** (types into the search bar) | 5 (4) | the 144 attempts are mostly here; 41 name a search mode |
| **Browse** (scrolls the timeline, opens albums) | **10** (9 scroll, 1 album) | 15 mention scrolling as a workaround (7 of 10 known outcomes not found); 12 broke because the path they knew moved (8.3%) |

**Level 2, product outcomes on the search path, each labelled with the brief's question**

| Outcome | The brief's question | Engine: where it broke (of 144) | Survey (15) | **Level 3: the behaviour you see** |
|---|---|---:|---:|---|
| Expression | *Is the user unable to express what they remember?* | 2 (1.4%) | **3** | Doesn't know what to type; 2 of the 3 never typed at all |
| **Interpretation** | *Does Google Photos fail to understand the clues they provide?* | **51 (35.4%)** | 3 | Adds a year, rewords: *"You must now specify the year"* |
| **Surfacing** (ours: not in the brief's list) | *Is the photo in the results at all?* | **60 (41.7%)** | **5 (4)** | Scrolls a grid of results that "look reasonable"; theirs isn't there |
| Recognition | *Are potentially relevant results difficult to evaluate?* | 2 (1.4%) | 2, but **7 (6) ended unsure** | Opens near-matches, can't confirm; wants place/trip (7), photos before/after (5) |
| Recovery | *Does the user struggle to refine an unsuccessful search?* | 1 (0.7%) | 1 | Tries again: **2–3 searches for 9 of 13** → n̄ in the formula |

`URR = Expression × [1 − (1 − Interpretation × Surfacing × Recognition)^n̄]`, the same formula as
Slide 10 and Part 4.
- **Recovery has no term:** it's 0.7% of failures. It ships only as a safety net and is tracked as a side measure.
- **Browse sits outside the formula, on purpose, and the slide says so.** The formula models the search
  path, which is where clues can be read. The browse path is measured beside it (first move; scroll-then-unsure).
  The rest of the 144: no stage stated 14, slow app 2.

**Where the opportunity is (one line under the tree):** Interpretation + Surfacing are 111 of 144 (77%) in the
engine and 8 of 15 in the survey. Both sources point to the same two outcomes, and the fix there serves the browse
path too, because a date window narrows a scroll as well as a search.

**Behaviour finding (side box):** everyone in the survey who found the photo for certain (6) had
**scrolled first**. Of the 5 who searched first, none was certain: 4 ended unsure, 1 failed (dedup: 3 and 1).
**Confirmed in MVP testing (§G2):** when asked what *actually* got them there the last time they found an old photo,
3 of 5 said scrolling back through the timeline, 2 said an album/folder, and **0 said search**. Scrolling is
the proven manual workaround.

**Also on the slide:**
- **Expression is the one disagreement** (engine 1.4% vs survey 3 of 15). Show both numbers; 2 of the 3 never
  reached a search box.
- **Where Google has already invested:** Ask Photos, the hybrid, and the classic/AI toggle all work on routing and speed.
  Episodes and event-relative time are still open.

**Footnote:** every URR baseline is modelled, not measured, because there is no Google telemetry · three inputs are
survey-measured and self-reported: n̄ ≈ 2–3, the first move, and the outcome mix (found 6 · unsure 7 (6) · not
found 2) · engine stages are model-extracted (κ 0.509 against a second model family) · survey n = 15, convenience sample

- **Visual:** a top-down tree. The metric at the top; it splits into Search and Browse; Search fans into the five
  outcomes as a horizontal chain, each box headed by the brief's question in italics, with two bars (engine %,
  survey count) and the behaviour in small type beneath. Interpretation and Surfacing are highlighted;
  Recovery is greyed and labelled "side measure, 0.7%"; Browse is a dashed box labelled "outside the formula,
  measured beside it".
- **If it's crowded, cut in this order:** "Where Google has already invested" → the behaviour side box → the
  Level 3 column (keep the brief's questions)

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

## Slide 5: User research and observed retrieval tasks

**Decided 3 Oct (user): Part 3 was run as a structured self-serve questionnaire, n = 15, not as live
interviews.** The slide states this and argues for the method; it never calls the survey "interviews".
Survey numbers recomputed from `data/interim/survey_episodes.jsonl`; engine numbers from §B.

**Title:** Most people scroll before they search, and nearly half end close but unsure

**Band 1: the method, and why this one (left column, 4 lines)** · the brief: *"think carefully about the
user research methodology"*

- **What:** a structured questionnaire, 15 people who had failed to find an old photo, 23–30 Sep. It walks
  each person through **one real failed search, in the order an interview would**: what they wanted → what
  they remembered and forgot → what they typed → where it broke → how it ended → what would have helped.
- **Why this instead of live interviews:** (1) **every answer is scoreable.** Only 8.6% of public posts
  narrate a complete attempt; structuring the story fixes that. (2) **The answers use the engine's
  vocabulary**, so 15 real searches sit beside the 144 public ones. (3) **Reach in the time available**: 15
  people against a target of 30, where live interviews had 2 contacts.
- **What it costs, stated:** no follow-up questions, self-report rather than observation, a convenience
  sample from the author's network. 8 of the 15 fit the segment (remembered a rough time or an event).
- **What adds behaviour:** the MVP test form (Slide 9) has each person run one search in their **own**
  Google Photos before trying the prototype.

**Band 2: real retrieval tasks, as people reported them (right column, the main visual)** · one row per person

| | Looking for | Remembered | Typed | Where it broke | How it ended |
|---|---|---|---|---|---|
| R04 | a wedding photo | roughly when, the event, who was there | *"wedding, pichle saal diwali"* | misread | unsure |
| R02 | a photo | roughly when, the event, an object | *"gym"* | couldn't tell which | unsure |
| R03 | a photo | roughly when, the event | *(didn't know what to type; scrolled)* | couldn't express | found |
| R11 | a photo | roughly when, the event | *(never typed; opened an album)* | couldn't express | unsure |
| R06 | a medicine bill | the object, text in it | *"medicine, bill"* | never surfaced | **never found; got it again** |

The first four are in the segment; R06 is outside it, and is one of the 3 who had real trouble (all document
or medicine photos). IDs are `survey:00NN`. No names: queries are checked for names before quoting.

**Band 3: the survey beside the engine (small table, never added together)**

| | Engine (144 attempts) | Survey (15; 14 after dedup) |
|---|---|---|
| Most remembered | roughly when (40) | roughly when (8) |
| Most forgotten | the date (37) | when it was taken (9) |
| Most common failure | never surfaced, 41.7% | never surfaced, 5 (4) |
| Didn't know what to type | 1.4% (2) | 3, of whom 2 never typed a search |
| Ended unsure: close, not certain | not measurable | **7 (6)** |

**Band 4: what they did (3 lines)** §G1

- **They scroll first.** It was the first move for 9 of 15 (5 typed a search, 1 opened an album). 9 scrolled
  back through the timeline as their next step, and 5 of those 9 still ended unsure.
- **Ask Photos rarely reached them.** 7 of 15 had never heard of it. All 4 who described a result (3 after dedup)
  said it showed "related photos, but not the one I wanted", and that they "could not tell why".
- **Their words:** *"wedding, pichle saal diwali"* (Hinglish: a festival, not a date) ·
  *"medicine, bill"* (never found; they had to get the document again)

**Footnote:** questionnaire, not interviews: self-reported, n = 15 against a target of 30, convenience sample;
one possible duplicate pair (14 after dedup); 2 respondents mainly use another app; 6 answers contradict each
other (§G1) · own-app baseline probe in MVP tests (n = 5, §G2): 0 found, 4 compressed to single nouns, 0 saw query interpretation

- **Visual:** left, the method in four lines; right, the five-row task table (Band 2); below, Band 3 and Band 4
  as two compact strips
- **Don't say:** "interviews" for the survey; "scrolled after search failed" (2 of the 9 never searched);
  "5 reached the right trip" (the data merges "the right trip" and "something similar" into unsure)
- **If it's crowded, cut in this order:** Band 4's Ask Photos line (Slide 7 carries it) → Band 3 to three rows →
  Band 2 to four rows. Never cut the method band: the brief grades the choice of method.

## Slide 6: Target segment and root cause

**Title:** The segment is people who can place the moment only roughly, and search can't turn "roughly" into a date window

**Drafted 3 Oct.** Engine numbers recomputed from `data/interim/episodes.jsonl` (144 specific
attempts); survey from `survey_episodes.jsonl`. Source: Part 4 §1 and §4.

**Band 1: who (left column)**

**Long-time Google Photos users looking for a personal moment they can place only roughly**: "around
Diwali", "my sister's graduation", "last winter". Defined by **what they still remember**, not by demographics.

| | Engine (144 attempts) | Survey (15) |
|---|---|---|
| Kept a rough time or an event | 42 (= O1) | 8 |
| **Minus the exclusions below** | **37 (26%)**, still the largest group that has a clue to search with | 8 (none overlap) |
| Looking for a personal photo or video | 30 of 37 | — |
| Big library | not measured | 5 of the 8 have 5,000+ items |

**Band 2: who is out, on purpose (one line)**

The **14** who remember the exact date (that's ordinary search) · the **12** whose usual path moved in an
app update (navigation, not memory: H6) · loss and backup complaints (the photo may not exist).
2 and 3 of these fell inside the 42, which is why the segment is 37.

**Band 3: root cause (right column, the main visual: two columns joined by a broken link)**

| What memory keeps | What search matches on |
|---|---|
| An **episode**: a rough time, an event, a few scenes | **Single photos** with a **calendar timestamp** |
| "Halloween 2024", "last winter", "when I was sick" | a date, a place name, an object word |

It breaks at the join in two ways (segment of 37):
1. **The clue is misread (12).** *"I'll type in something super simple, like 'Halloween 2024' and it
   seriously can't find anything?"* (Play Store; an event *and* a year, and still no date window)
2. **The photo never surfaces (18).** Results come back as a flat grid across years; nothing narrows
   them to the episode.

The same break shows up in classic search (7) and in Ask Photos (4), so it's not just an old-search problem.

**Band 4: the survey's 8 (one line, stated, not hidden)**

Their failures spread out: 3 didn't know what to type, 3 had the search misread or the photo never
surfaced, 2 couldn't evaluate the results. But **5 of the 8 ended unsure** they had the right photo,
against 2 of the other 7. Whatever stage it broke at, they got close, not there: the root cause, seen from the other end.

**Market choice (one line):** India, festivals and Hinglish time phrases are **a design choice, not a
finding**. H4 has a weak signal only: 2 of 15 survey search in Hinglish (*"wedding, pichle saal diwali"*);
1 of 6 MVP testers explicitly asked for *"pichle ke pichle saal"*.
**Real-app baseline evidence on the root cause (§G2):** 4 of 5 Google Photos users compressed rich episodic memories
("vacation last year", "when I started Gym") into bare nouns ("vacation", "gym") when typing into Google Photos,
and all 5 failed (2 other years/events, 3 couldn't tell which was theirs).

**Footnote:** 35 of the 37 are Play Store posts · only 15 of the 37 state an outcome (7 not found, 3 found slowly,
5 found fast) · "long-time" and "big library" are screener criteria; the engine can't measure tenure ·
survey n = 8, self-reported

- **Visual:** left, the segment table; right, the memory-vs-index columns with the Halloween quote under the
  broken link; Bands 2 and 4 as one-line strips
- **Don't say:** "42 is the segment" alongside the exclusions (5 of them overlap); "29% of attempts are the segment"
  (29% is O1; the segment is 26%)

## Slide 7: Problem definition and solution rationale

**Title:** People already scroll to "roughly when" by hand and still end unsure, so the product should take that step for them

**Redrafted 3 Oct** against brief Part 4. Engine numbers recomputed from `episodes.jsonl`; survey
from `survey_episodes.jsonl` (dedup in brackets); quotes checked against the source posts.

**Band 1: the problem (top, full width, largest type)**

> People remember **when-ish** and **what happened**; Google Photos indexes **items** and **calendar
> dates**. So the photo is in the library, the person can describe the moment but not the photo, and
> it never comes back.

- **Scenario:** the user knows the moment, not the photo: *"that small café we went to during our Goa
  trip"*. They have an episode and a scene; they don't have the date, the café's name or the album.
- **Outcome we intend to influence:** **Interpretation and Surfacing**, which are 111 of 144 failures (77%) in
  the engine and 8 of 15 in the survey. They roll up into URR (Slide 2).

**Band 2: the workaround is the design cue (left)**

- **Engine:** only 21 of 144 mention a workaround, but **15 of those are scrolling**, and 7 of the 10 with a
  known outcome didn't find it: *"Every time I scrolled to the right time frame, it kept loading more
  pictures and moving up a couple of years ahead."*
- **Survey:** scrolling is the first move for 9 of 15. 9 scrolled back through the timeline as their next step,
  and **5 of those 9 still ended unsure** they had the right photo.
- **So:** scrolling is episode retrieval done by hand. The user turns "roughly when" into a place on the
  timeline, then looks for the scene. The product should do the first step and help with the second.

**Band 3: why it's worth solving (right)**

- **User value:** of 62 posts that state an outcome, 46 describe not finding it (posts by people who failed;
  `outcome` κ 0.161). In the survey, **all 3 people who had real trouble** (had to ask someone or get the document
  again) were looking for a document or medicine photo (*"medicine, bill"*: never found).
- **Business sense:** 1.5B monthly users and 9T+ photos and videos; the older a library gets, the more of it is
  reachable only by vague memory. Retrieval is what makes paid storage worth keeping (Google One, 150M subscribers).
  *This is reasoning, not measured churn.*

**Band 4: solution rationale (right, under Band 3)**

- **Intelligence where it's needed, and only there:** (1) turning a clue into a date window; (2) grouping the
  library into episodes. Both run on data Photos already holds.
- **Why not Ask Photos:** it fixed routing and speed, but it has no editable clues, no results grouped by
  episode, and no explanation of why a photo matched. **Across survey (4 of 4) and MVP tests (3 of 3), all 7
  users who reported an Ask Photos result said "related photos, but not the one I wanted" and 0 found it (§G1, §G2).**
  The AI assistant repeats the same surfacing failure as classic search.
- **Scoped out, with numbers:** the clarifying question (engine 1.4%; survey 3 of 15, but 2 of the 3 never typed a
  search, and all 3 asked for the photos just before and after, which the moment view gives) · full recovery
  (0.7%; survey 1 of 15), which ships only as a one-question safety net

**Band 5: how the thinking evolved (strip across the bottom, the brief's five steps as labels)**

| Business Metric | Product Outcomes | AI-Powered Discovery | Observed User Behavior | Problem Definition |
|---|---|---|---|---|
| Per-*search* success → **per-user URR** (the brief counts users) | A recovery agent → **five stages**, plus a Browse path beside search | The audit first ranked H3 (recovery) top → **overturned**: it rested on the weakest field; failures cluster before recovery | Users search and retry → **they scroll to a time by hand, and end unsure**. *Reported in posts and the survey, not observed* | "Search is bad at old photos" → **the statement above** |

The fourth box stays labelled "reported": the posts and the survey are both self-report.

**Footnote:** engine 86.2% Play Store, complaint-heavy · survey n = 15, self-reported, convenience sample ·
external figures: PetaPixel (May 2025), 9to5Google (May 2025), linked

- **Visual:** the problem statement as a banner; two columns (workaround | value + rationale); the
  five-step evolution strip along the bottom, with the fourth box labelled "reported"
- **If it's crowded, cut in this order:** the engine quote in Band 2 → the scoped-out line → business sense down to
  one clause. Never cut the outcome line or the strip's step labels: the brief asks for both.
- **Don't say:** "scrolled after search failed" (2 of the 9 never searched); "land on the trip but not the photo"
  (the survey merges "right trip" and "something similar"); "observed" for the fourth box.

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
- Link: https://memory-trails-v2.vercel.app
- **Visual:** 3–4 screenshots in sequence from `design/mvp-screenshots/` (retaken from the live site 28 Sep):
  `2-describe`, `3-clues`, `4-moments`, `7-found`; `6-recover` if slide 9 needs the recovery step

## Slide 9: User testing

**Title:** Testers found the moment in 5 of 6 cases and rated it easier than search, but compound dates need explicit control

**Band 1: Method & Target Segment (left column)** §G2
- **Method:** unmoderated self-serve test form (`mvp_test_form.gs`), 3–4 Oct 2026. 6 participants,
  all from the target segment (3 remembered by event/festival, 3 roughly; none remembered exact date).
  5 use Google Photos as their primary photo app; 1 uses Apple Photos.
- **Representative tasks from research:** Task 1: "a photo of your cat from last year's Diwali" (`demo:0372`/`0373`);
  Task 2 (clue correction): "the dog by a tree, from the Diwali before that" (`demo:0365`).
- **Real-app baseline (own Google Photos):** 0 of 5 found their photo · 4 of 5 compressed memory into single nouns
  ("vacation", "gym") · 2 other years/events, 3 couldn't tell which was theirs · 0 saw how words were read (3 no, 2 not sure) ·
  3 of 3 in Ask Photos got "related, not mine" · 3 found via scroll, 2 album, **0 search**.

**Band 2: Prototype Task Results (table/cards, right)** §G2

| Participant | Own GP Query → Result | Task 1 (Cat, Diwali 2025) | Task 2 (Dog, Diwali 2024) | Task 1 Sureness | vs GP (1–5) | Adoption |
|---|---|---|---|---:|---:|---|
| R01 | *"A wedding before COVID"* → other years | Found, sure | Not found (year stuck) | 5 / 5 | 5 / 5 | Every time |
| R02 | *"gym"* → couldn't tell | Found, sure | Found, sure (1-tap alt) | 4 / 5 | 4 / 5 | When search fails |
| R03 | *(Apple Photos user)* | Found, sure | Found, sure (nearby months) | 5 / 5 | — | Every time |
| R04 | *"vacation"* → other years | Found, sure | Found, sure (1-tap alt) | 4 / 5 | 4 / 5 | When search fails |
| R05 | *"Wedding event"* → couldn't tell | Found, sure | Found, sure (clue edit) | 4 / 5 | 4 / 5 | Every time |
| R06 | *"Kerala photos"* → couldn't tell | Right Diwali, unsure photo | Found, sure (1-tap alt) | 4 / 5 | 3 / 5 | Every time |

- **Task 1: 5 found and sure, 1 right Diwali but unsure which photo** (0 failed; 6 of 6 reached the right event).
  Mean sureness: **4.33 / 5**. Reasons: *"moment matched the event"*, *"photos before and after"*, *"right month, right event"*.
- **Task 2 (clue correction): 5 found and sure, 1 not found** (stuck on "year before last").
- **Features used:** 4 picked suggested alternative ("or Diwali 2024") · 2 "Around that time" (nearby months) ·
  2 removed/changed clue · 1 "Why this moment?" (evidence details).
- **Head-to-head ease vs Google Photos:** Mean **4.0 / 5** (4 easier/much easier, 1 same, 0 harder).

**Band 3: In their own words (quotes)** §G2
- *"Shows the moment, not a grid / Google Photos is faster for simple searches"* (R02)
- *"Moving to nearby months, like scrolling but faster"* (R03)
- *"Works without knowing what to type / Google Photos has albums"* (R04)
- *"Understands festivals plus 'last year' / Google Photos has real photos and faces"* (R01)
- *"Find the exact month and the year that I was searching. And it could understand the mix of hindi and english language"* (R06)

**Band 4: What broke → Next iteration roadmap (the brief's requirement)** §G2
1. **Compound relative time failed:** R01 failed Task 2 (*"Got 'last year' right, 'the year before last' wrong"*,
   *"Understand 'pichle ke pichle saal'"*). Extractor lacked multi-year relative compounds and manual year override.
   → **Next:** Add compound offsets and direct year dropdown edit on date chips.
2. **Clue chip saliency:** R04 (*"Didn't notice the clue labels at first"*), R02 (*"Show date range more clearly"*).
   → **Next:** High-contrast accent badges and micro-prompt: *"Showing Diwali 2025 · Tap to change"*.
3. **Retrieval latency:** R05, R06 requested faster image retrieval speed.
   → **Next:** Pre-cache candidate moments and skeleton progressive image load.

**Footnote:** self-serve form, unmoderated: reported counts, not percentages · session logs were omitted by all 6 participants;
confirmed `photo_id`s and completion seconds are unobserved, so `wrong_confirm` is coded as unknown rather than asserted as zero ·
convenience sample n = 6.

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
  - R4: false confirmation → nothing auto-confirms; in testing, 1 of 6 faced recognition ambiguity; measure it
  - R5: recovery was kept light on a number from 86% Play Store data → **survey (1 of 15) and testing (4 of 6 used 1-tap alternatives) agree**;
    light alternatives suffice over heavy recovery dialogues
  - R6: Ask Photos may already be enough → **survey (4 of 4) and MVP tests (3 of 3) both show 100% of reported results were "related, not mine"** (7 of 7 total);
    Ask Photos repeats the surfacing failure
  - R7: the survey disagrees on Expression (3 of 15 vs 1.4%) → the moment view serves the scrollers
    who make up 2 of the 3; MVP testers confirmed "works without knowing what to type"
- **Limitations:** Play Store 86.2% · H4 a weak signal only (2 of 15 survey, 1 of 6 testing) · URR baselines modelled ·
  ranking weights are judgement · survey n = 15, testing n = 6, unmoderated self-serve without pasted logs (wrong_confirm unknown)
- **Visual:** metrics tree on the left, risk table on the right

---

## Open before building slides

1. **Slide 9 needs the MVP tests.** Slide 5 is complete (Part 3 = the survey, decided 3 Oct). Everything else can be laid out now.
2. **Density:** slides 7 and 10 carry the most. At 14 pt they may overflow; cut prose before cutting a
   required item.
3. **Format:** Google Slides / PPT (14 pt min) or Figma/Canva at 1920×1080 (26/22 pt min), decided before layout.
