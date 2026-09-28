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
| cannot_express | **1.4%** (2), **the reason Stage 2 is cut** | `failure_stage` | 8 |
| cannot_refine | **0.7%** (1), **the reason Stage 4 is cut** | `failure_stage` | 4, 8 |
| cannot_evaluate_results | 1.4% (2) | `failure_stage` | 8 |
| Most-retained cue | **temporal_approx, 40** · object 17 · exact_date 14 · text_in_image 12 · who_with 10 | `cues_retained` (count of mentions) | 5 |
| Most-lost cue | **date, 37** · album 29 · exact_words 10 · place 10 · people 9 | `cues_lost` | 5 |
| Cues retained per attempt | 1 cue: 79 · 0: 47 · 2: 12 · 3: 6 | `cues_retained` length | 5 |
| Search mode mentioned | not mentioned 103 · classic 27 · Ask Photos/AI 10 · both 4 | `search_mode` | 8 |

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

## E. MVP retrieval evaluation (slides 8, 9). Library 1,250 photos, k = 20

**What ships is `soft` scoring** (default since 23 Sep). Plan §3's "inferred = what ships" line
describes `inferred_rules`, which is no longer the default.

### E1. Cue-dropout ladder: 30 base tasks × 4 levels = 120 tasks (`data/eval/*_dropout.json`)

| Level | What the query keeps | Baseline recall@20 | **Soft recall@20** | Soft moment@5 | Soft found | Rules recall@20 |
|---|---|---:|---:|---:|---:|---:|
| L3 | vague time + exact place + library word | 0.172 | **0.962** | 0.933 | 1.000 | 0.851 |
| L2 | paraphrased content + two vague cues | 0.209 | **0.276** | 0.333 | 0.333 | 0.276 |
| L1 | paraphrased content + one vague time cue | 0.242 | **0.342** | 0.333 | 0.400 | 0.342 |
| L0 | content only | 0.312 | **0.312** | 0.267 | 0.367 | 0.312 |
| All 120 | | 0.234 | **0.473** | 0.467 | 0.525 | 0.445 |

### E2. Real-phrasing held-out set: 30 tasks (`data/eval/*_real_test.json`), equivalent to cue level L3

| Strategy | recall@20 | hit@1 | found |
|---|---:|---:|---:|
| Baseline (plain CLIP) | 0.172 | 0.000 | 0.200 |
| Oracle (±45 days) | 0.742 | 0.267 | 0.767 |
| Inferred, LLM | 0.718 | 0.433 | 0.767 |
| Inferred, rules | 0.818 | 0.500 | 0.867 |
| **Soft (ships)** | **0.866** | 0.500 | 0.900 |

### E3. Original synthetic set: 30 tasks (`data/eval/*_synthetic.json`)

| Strategy | recall@20 | hit@1 | found |
|---|---:|---:|---:|
| Baseline | 0.012 | 0.000 | 0.067 |
| Oracle | 0.417 | 0.167 | 0.433 |
| Inferred, rules (= LLM here) | 0.479 | 0.133 | 0.533 |
| Soft | **not run** | | |

Task mix: **25 of 30 (83%) single-cue**, cue weights sampled from the 144 attempts (temporal_approx 40 of 98).

### ✅ Decided 28 Sep: the headline is the E1 ladder, shown as a ladder and not as one number

**Drafts brought in line on 28 Sep.** `research/analysis/part_4_problem_definition.md` and `research/analysis/parts_7_8_workflow.md` now
quote the ladder. Retired everywhere: 0.012 → 0.479 (synthetic set, rules extractor) and
0.053 → 0.612 (494-image library). Neither was the strategy that ships.

Also true of the ladder, and now stated in both drafts: **hit@1 is 0.000 at L0–L2**, and the tasks are
constructed by us, not collected.

**What the ladder actually shows, stated plainly:** the gain is large only when place survives alongside
time (L3: +0.79). With **one vague time cue** it is **+0.10** (0.242 → 0.342). With two vague cues it is
+0.07, and with content only it is zero. The last result is honest: the parser adds no false filters.
That is a narrower claim than the H1 verdict on "clue → window took recall from 0.053 to 0.612".

**Decision (28 Sep, user):** E1 is the headline. The reasoning:, since it is the shipped strategy on 120 tasks and it tests
the brief's own user who cannot describe the photo precisely. Present it as a ladder rather than as
one number, and add moment@5 at L2 (0.333 > 0.276 recall@20) as the episode-grouping argument. Keep E3 only as the
"same photos, same queries" baseline story if at all, and retire 0.612 entirely.

## F. Library and MVP (slide 8)

| Claim | Number | Source |
|---|---|---|
| Library size | **1,250** CC photos, 59+ categories | `library_stats.json` |
| In synthetic life episodes | 231 photos across **25 episodes**; 1,019 stray | `library_stats.json` |
| Instrumented events | 12 (wireframe §8) | plan §6, not re-verified |
| Automated tests | 305 (214 in `tests/`, 91 retrieval) as of 23 Sep | `plans/PROGRESS.md`, rerun before quoting |
| CLIP on text-in-image categories | 0.000 recall on whiteboard/document, oracle too | plan §5 H5, 494-image era, **recheck at 1,250** |

## G. Survey, interviews, MVP tests (slides 6, 9): **empty**

| Claim | Number | Source |
|---|---|---|
| Survey responses | **not imported**. Target ≥30 | `survey_episodes.jsonl` (absent) |
| Interviews (Part 3) | **0 of 5–6** | `research/interviews/` (absent) |
| MVP tests (Part 6) | **0 of 3** | study-mode logs (none) |
| Own-library probe | 0 of 6 photos logged | `research/testing/probe-log.csv` |

Slide 6 has no content until this section fills. Do not substitute proto-personas for it; they are
hypotheses (`research/survey/survey-proto-personas.md`).
