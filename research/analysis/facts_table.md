# Facts table: every number the deck may quote

**Started 28 Sep 2026.** Rule C: every figure goes on a slide only from this table, and only with the value
shown here. CS2 lost points to one statistic appearing with two values.

**How each row was verified:** recomputed on 28 Sep from the file in *Source*, not copied from
`plans/PROGRESS.md` or the plan. Rows marked **⚠** conflict with a draft or need checking before the
deck uses them. Slide numbers follow Plan 2 §10.

---

## A. Discovery engine: funnel (slide 3)

| Claim | Number | Source | Slide |
|---|---|---|---|
| Posts collected | **85,140**: Play Store 81,256 · App Store 2,732 · YouTube 696 · Reddit 456 | `data/interim/funnel.json` | 3 |
| Passed Gate A (keyword/heuristic) | **5,305** | `gate_a_candidates.jsonl` (line count) | 3 |
| Gate B labelled | **1,333**, of which **819 relevant** | `gate_b.jsonl` | 3 |
| Episodes extracted | **720** (closed deliberately at 720 of 819) | `episodes.jsonl` | 3 |
| Specific retrieval attempts | **144** (the other 576 are general complaints) | `episodes.jsonl` `specificity` | 3, 5 |
| Scoreable (specific + known outcome) | **62** = **8.6%** of 720 | `episodes.jsonl` `outcome ≠ unknown` | 3 |
| Outcomes of the 144 | not_found 46 · found_fast 11 · found_slow 5 · unknown 82 | `episodes.jsonl` | 3 |

## B. What fails and what people remember (slides 5, 7). Denominator: 144 specific attempts

| Claim | Number | Source | Slide |
|---|---|---|---|
| Photo was there, never surfaced | **41.7%** (60) | `failure_stage` | 5, 7 |
| Query misread | **35.4%** (51) | `failure_stage` | 5, 7 |
| **Fail before recovery is needed** | **77.1%** (41.7 + 35.4) | derived | 1, 7 |
| Learned browse path changed (H6) | **8.3%** (12) | `failure_stage` | 4 |
| No failure stage stated | 9.7% (14) | `failure_stage` | — |
| cannot_express | **1.4%** (2), **the reason Stage 2 is cut**. Survey says 3 of 15 (§G1): show both | `failure_stage` | 8 |
| cannot_refine | **0.7%** (1), **the reason Stage 4 is cut** | `failure_stage` | 4, 8 |
| cannot_evaluate_results | 1.4% (2) | `failure_stage` | 8 |
| Most-retained cue | **temporal_approx, 40** · object 17 · exact_date 14 · text_in_image 12 · who_with 10 | `cues_retained` (count of mentions) | 5 |
| Most-lost cue | **date, 37** · album 29 · exact_words 10 · place 10 · people 9 | `cues_lost` | 5 |
| Cues retained per attempt | 1 cue: 79 · 0: 47 · 2: 12 · 3: 6 | `cues_retained` length | 5 |
| Search mode mentioned | not mentioned 103 · classic 27 · Ask Photos/AI 10 · both 4 | `search_mode` | 8 |

## B2. Segment, asset types, workarounds, outcomes (slides 4, 6, 7). Denominator: 144, recomputed 28 Sep

| Claim | Number | Source | Slide |
|---|---|---|---|
| Asset type | photo 80 · multiple 26 · video 16 · unknown 12 · screenshot 7 · document/receipt 3 | `asset_type` | 4 |
| Personal photo or video | **96 of 144 (67%)** | `asset_type` photo + video | 6 |
| Kept a rough time or a life event (segment; = engine O1) | **42 of 144 (29%)**, of which **33 kept nothing else**. Not the same as §B "temporal_approx 40", which counts rough time alone; of these 20 not_surfaced, 12 misread; 15 known outcomes (7 not found, 3 slow, 5 fast) | `cues_retained` ∋ temporal_approx/event_anchor | 6 |
| Remembered the exact date (excluded) | 14 | `cues_retained` | 6 |
| Any workaround mentioned | **21 of 144 (15%)** | `workaround` | 7 |
| Workaround = scrolling | **15 of 21** (manual 10, to a date region 5); **7 of 10 known outcomes not found** | `workaround`, `outcome` | 7 |
| Other workarounds | other app 2 · gave up 2 · old app version 1 · classic toggle 1 | `workaround` | — |
| Known-outcome attempts ending not found | **46 of 62 (74%)**; 5 found slowly, 11 fast. **Say it as:** "of 62 posts that state an outcome, 46 describe not finding it". Complaint-biased sample, and `outcome` has the weakest audit agreement (κ 0.161, §C) | `outcome` | 7 |

External (cite with link on the slide): Photos **1.5B monthly users, 9T+ photos and videos**
([PetaPixel, May 2025](https://petapixel.com/2025/05/28/google-photos-turns-10-now-hosts-over-9-trillion-photos-and-videos/));
Google One **150M subscribers** ([9to5Google, May 2025](https://9to5google.com/2025/05/15/google-one-150-million/)).

## C. Audit: blind cross-family re-extraction (slides 3, 4). n = 203 pairs

| Claim | Number | Source | Slide |
|---|---|---|---|
| Audit model | `qwen/qwen3.8-27b`, cross-family | `audit_report.json` | 3 |
| `failure_stage` agreement | **κ 0.509** (61.6% raw) | `audit_report.json` | 4 |
| `search_mode` | κ 0.522 | `audit_report.json` | — |
| `specificity` | κ 0.464 | `audit_report.json` | — |
| `outcome` | κ **0.161** (weak) | `audit_report.json` | 4 |
| `hypotheses` | **Jaccard 0.347**, the weakest field, which is why H3 is not the lead | `audit_report.json` | 4 |
| Cues retained / lost | Jaccard 0.557 / 0.673 | `audit_report.json` | — |
| `evidence_verified` on the audit sample | primary **85.2%** · audit **97.0%** | `audit_report.json` | 3 |
| ⚠ `evidence_verified` on all 720 | **90.4%** | `episodes.jsonl` | 3 |
| Top hypothesis (specific attempts) | primary: H3 0.086, H1 0.049 · audit: H3 0.50, H6 0.25 | `ranking_on_sample` | 4 |

⚠ **Two evidence-verified figures exist.** They measure different things: 85.2% is the audit sample of 203,
and 90.4% is the full corpus of 720. Quote one, labelled with its n. The plan's disclosure list uses 85.2%.

## D. Disclosures (slide 3 footnote, slide 10)

| Claim | Number | Source |
|---|---|---|
| Play Store share of extracted episodes | **86.2%** (621/720), against the plan's 60% cap | `episodes.jsonl` |
| Reddit / App Store / YouTube | 8.6% / 5.0% / 0.1% | `episodes.jsonl` |
| Play Store share of the 144 specific attempts | 85.4% (123) | `episodes.jsonl` |
| H4 not tested | `query_language`: en 709, no_query 11, **zero code-mixed** | `episodes.jsonl` |
| `query_language` audit agreement | κ **0.002**: the field carries no signal | `audit_report.json` |
| ⚠ Outcome κ by source (Reddit 0.27 / Play Store 0.13) | not re-verified on 28 Sep | plan §10 → recheck before use |

## E. MVP retrieval evaluation (slides 8, 9). Library 1,282 photos, k = 20

**Re-run 28 Sep** after four demo-scenario episodes (32 photos) were added. Two kinds of change,
kept apart: *stale* means the committed result file did not match the committed code even before
that change (verified by re-running the previous commit on the 1,250-photo library); *this change*
means the 32 new photos moved it.

**What ships is `soft` scoring** (default since 23 Sep). Plan §3's "inferred = what ships" line
describes `inferred_rules`, which is no longer the default.

### E1. Cue-dropout ladder: 30 base tasks × 4 levels = 120 tasks (`data/eval/*_dropout.json`)

| Level | What the query keeps | Baseline recall@20 | **Soft recall@20** | Soft moment@5 | Soft found | Rules recall@20 |
|---|---|---:|---:|---:|---:|---:|
| L3 | vague time + exact place + library word | 0.172 | **0.962** | 0.933 | 1.000 | 0.851 |
| L2 | paraphrased content + two vague cues | 0.209 | **0.276** | 0.333 | 0.333 | 0.276 |
| L1 | paraphrased content + one vague time cue | 0.242 | **0.309** | 0.333 | 0.367 | 0.342 |
| L0 | content only | 0.312 | **0.312** | 0.267 | 0.367 | 0.312 |
| All 120 | | 0.234 | **0.465** | 0.467 | 0.517 | 0.445 |

### E1b. The ladder weighted by real memory: the line that goes beside it (added 1 Oct)

Each ladder level weighted by how many cues the 144 specific attempts actually kept
(0 cues: 47 → L0 · 1: 79 → L1 · 2: 12 → L2 · 3: 6 → L3; §B). Recomputed 1 Oct from
`episodes.jsonl` and `data/eval/{baseline,soft}_dropout.json`.

| Weighting | Plain recall@20 | **Memory Trails recall@20** | Gain | Plain moment@5 | Memory Trails moment@5 |
|---|---:|---:|---:|---:|---:|
| All 144 attempts | 0.259 | **0.334** | **+0.075** | 0.225 | 0.336 |
| Excluding the 47 with no cue | 0.234 | 0.345 | +0.111 | 0.204 | 0.370 |

**Why it must travel with the ladder:** L3's 0.962 needs three cues, and only **6 of 144 (4%)** real
attempts kept three. Weighted by what people actually remember, the recall gain is **+0.075**, and
the moment@5 gain (+0.111) is larger than the recall gain. That supports the H2 argument (browse moments)
over a ranking claim. **Approximate mapping:** a real attempt's cues are not always the ladder's cue
types (L3 is time + place + library word), so this is an illustration of weighting, not a
measurement of real queries.

*This change:* soft L1 was 0.342 (found 0.400) on 1,250 photos; one new photo now outranks one L1
target. Every other cell is unchanged.

### E2. Real-phrasing held-out set: 30 tasks (`data/eval/*_real_test.json`), equivalent to cue level L3

| Strategy | recall@20 | hit@1 | found |
|---|---:|---:|---:|
| Baseline (plain CLIP) | 0.172 | 0.000 | 0.200 |
| Oracle (±45 days) | 0.742 | 0.267 | 0.767 |
| Inferred, LLM | 0.718 | 0.433 | 0.767 |
| Inferred, rules | 0.718 | 0.433 | 0.767 |
| **Soft (ships)** | **0.866** | 0.467 | 0.900 |

*Stale, corrected 28 Sep:* rules was published as 0.818 / 0.500 / 0.867 and soft hit@1 as 0.500. The
committed code already gave these values before any change today. Soft still leads rules (0.866 vs
0.718), and rules now **ties** the LLM extractor (0.718) rather than beating it.

### E3. Original synthetic set: 30 tasks (`data/eval/*_synthetic.json`)

| Strategy | recall@20 | hit@1 | found |
|---|---:|---:|---:|
| Baseline | 0.012 | 0.000 | 0.067 |
| Oracle | 0.417 | 0.167 | 0.433 |
| Inferred, rules (= LLM here) | 0.479 | 0.133 | 0.533 |
| Soft (ships) | **0.517** | 0.133 | 0.533 |

*New 28 Sep:* soft had never been run on this set.

Task mix: **25 of 30 (83%) single-cue**, cue weights sampled from the 144 attempts (temporal_approx 40 of 98).

### ✅ Decided 28 Sep: the headline is the E1 ladder, shown as a ladder and not as one number

**Drafts brought in line on 28 Sep.** `research/analysis/part_4_problem_definition.md` and `research/analysis/parts_7_8_workflow.md` now
quote the ladder. Retired everywhere: 0.012 → 0.479 (synthetic set, rules extractor) and
0.053 → 0.612 (494-image library). Neither was the strategy that ships.

Also true of the ladder, and now stated in both drafts: **hit@1 is 0.000 at L0–L2**, and the tasks are
constructed by us, not collected.

**What the ladder actually shows, stated plainly:** the gain is large only when place survives alongside
time (L3: +0.79). With **one vague time cue** it is **+0.07** (0.242 → 0.309). With two vague cues it is
+0.07, and with content only it is zero. The last result is honest: the parser adds no false filters.
That is a narrower claim than the H1 verdict on "clue → window took recall from 0.053 to 0.612".

**Decision (28 Sep, user):** E1 is the headline. The reasoning:, since it is the shipped strategy on 120 tasks and it tests
the brief's own user who cannot describe the photo precisely. Present it as a ladder rather than as
one number, and add moment@5 at L2 (0.333 > 0.276 recall@20) as the episode-grouping argument. Keep E3 only as the
"same photos, same queries" baseline story if at all, and retire 0.612 entirely.

## F. Library and MVP (slide 8)

| Claim | Number | Source |
|---|---|---|
| Library size | **1,282** CC photos, 65 categories | `data/demo/library.jsonl` |
| In synthetic life episodes | 263 photos across **29 episodes**; 1,019 stray | `data/demo/library.jsonl` |
| Demo-scenario episodes (28 Sep) | sister's graduation 10 · college performance 7 · old apartment 8 · packing for the trip 7 | `engine/demo_library.py` CURATED |
| Instrumented events | 12 (wireframe §8) | plan §6, not re-verified |
| Automated tests | 305 (214 in `tests/`, 91 retrieval) as of 23 Sep | `plans/PROGRESS.md`, rerun before quoting |
| CLIP on text-in-image categories | 0.000 recall on whiteboard/document, oracle too | plan §5 H5, 494-image era, **recheck at 1,282** |

## G. Survey, interviews, MVP tests (slides 6, 9). Survey filled 1 Oct; interviews and tests empty

### G1. Survey: 15 responses, closed 1 Oct (`data/interim/survey_episodes.jsonl`, `data/processed/survey_stats.json`)

Imported with `engine.import_survey` from the closed form's CSV (responses 23-30 Sep). Every
respondent passed the gate (9 "yes", 6 "yes, but not when"), so n = 15 episodes. Target was ≥30.
**Possible duplicate:** `survey:0007` and `survey:0010` give identical answers to every closed
question (only the typed query differs), two days apart. Where a number moves, the "dedup" column
drops `survey:0010` (n = 14). Quote the smaller number.

| Claim | All 15 | Dedup (14) | Field |
|---|---:|---:|---|
| Outcome: **uncertain** (right trip but not the photo 4; similar but not sure 3) | **7 (47%)** | 6 (43%) | `retrieval_certainty` |
| Outcome: found (fast 3, slow 3) | 6 | 6 | `retrieval_certainty` |
| Outcome: never found / stopped looking | 2 | 2 | `retrieval_certainty` |
| Failure stage: not_surfaced ("results looked reasonable, mine was not there") | **5** | 4 | `failure_stage` |
| Failure stage: cannot_express ("did not know what to type") | **3** | 3 | `failure_stage` |
| Failure stage: system_misunderstood | 3 | 3 | `failure_stage` |
| Failure stage: cannot_evaluate_results / abandoned | 2 / 1 | 2 / 1 | `failure_stage` |
| Failure stage: cannot_refine (pilot wording "nothing came up, no idea what to change") | 1 | 1 | `failure_stage` |
| Most-remembered cue: roughly when | **8** | 8 | `cues_retained` |
| Then: object 7 · who was with me 6 · named place 5 · event 4 · colour 3 · text in image 2 | | | `cues_retained` |
| Most-forgotten: when it was taken / the exact words to search | **9 / 9** | 9 / 8 | `cues_lost` |
| What would have helped check a close result: place or trip | **7** | 7 | `recognition_needs` |
| Then: photos just before/after 5 · rough date range 5 · people nearby 3 · why it came up 2 | | | `recognition_needs` |
| First move: scroll the timeline / type a search / open an album | **9** / 5 / 1 | 9 / 4 / 1 | `first_move` |
| Never type, only scroll | 3 | 3 | `query_language` = no_query |
| Search in Hinglish (English letters) | **2** | 2 | `query_language` |
| Real trouble caused (had to ask someone or get the document again) | **3, all document or medicine photos**; 0 of 11 ordinary photos | 3 | `consequence` × `asset_type` |
| Ask Photos: never heard of it / heard, not used / used | **7** / 5 / 3 | 7 / 5 / 2 | `ask_awareness` |
| Ask Photos result: "related photos, but not the one I wanted" + "could not tell why" | **4 of 4** who reported a result | 3 of 3 | `ask_outcome`, `ask_problem` |
| Time: 5-15 min / >15 min / across days / 1-5 min | 7 / 3 / 2 / 3 | | `time_spent` |
| Willing to talk / left a contact | 11 / **2** | | `willing_interview` |
| App: Google Photos / Apple / other / both | 12 / 1 / 1 / 1 | | `app` |
| Library 5,000+ items / looks for old photos a few times a month | 10 / 9 | 9 / 8 | `library_size`, `frequency` |
| Searches per incident: 2-3 times (of 13 who answered) | **9** (once 1, 4+ 1, did not search 2) | 8 of 12 | `search_count` |
| Scrolled back through the timeline as a next step (not "after search failed": 2 of the 9 never searched) → outcome | **9**: 5 uncertain · 3 found · 1 failed | 9: same | `workarounds` × `retrieval_certainty` |
| The 3 cannot_express: what would have helped | **all 3: photos just before/after**; 2 never typed a search | 3 | `recognition_needs` |

**Quotes the deck may use (verbatim `query_verbatim`):** "wedding, pichle saal diwali" (Hinglish,
time-anchored: "last year's Diwali"); "medicine, bill" (never found, had to get it again).

**What this changes:**
- **The Stage 2 (Expression) cut must show both numbers.** Engine 1.4% (2 of 144) vs survey 3 of 15.
  Two of the three never typed a search (`first_move` scroll/album, `query_language` no_query), so
  part of the survey figure is people who never reach a search box. Do not keep "1.4%" alone.
- **Recovery cut holds:** 1 of 15 (cannot_refine), on the old pilot wording.
- **H2 strengthens:** uncertain is the largest outcome (tied with found after dedup), and the top
  checking aids are place/trip, sequence and date range: the episode view.
- **H4 stays weak:** 2 of 15. One real code-mixed time query, which is a quote, not a verdict.
- **H5 gains a consequence:** every case of real trouble was a document or medicine photo.

**Caveats that travel with every G1 number:** n = 15 (14), convenience sample from the author's
network, self-reported; 2 respondents do not mainly use Google Photos. Internal contradictions:
`survey:0008` and `survey:0013` say they never heard of Ask Photos yet answered its result
questions ("works well"; excluded from the Ask Photos row above); `survey:0009` says it did not
search but gave a query; `survey:0012` "gave up before getting that far" but found it;
`survey:0013` found it "fairly quickly" but came back "across days". `survey:0005` said it had heard of Ask Photos but not used it, yet described its result (counted in the 4 above). The two unsure answers ("right trip" vs "something similar") are not kept per respondent, so no subgroup of the unsure can be split by them.

### G2. Interviews, MVP tests, probes

| Claim | Number | Source |
|---|---|---|
| Interviews (Part 3) | **0 of 5–6** | `research/interviews/` (absent) |
| MVP tests (Part 6) | **0 of 3** | study-mode logs (none) |
| Own-library probe | 0 of 6 photos logged. The 30 Sep cross-check cites 26 Sep results that are not in the CSV. **When they are logged:** wedding 2 search B is unrecorded, so say "3 confirmed not found, 1 pending", never "4 of 6 never found" | `research/testing/probe-log.csv` |

Slide 6 now has survey content (G1) but no interviews. Do not substitute proto-personas for
interviews; they are hypotheses (`research/survey/survey-proto-personas.md`).
