# Implementation Plan — Google Photos Case Study

**Working document from 20 Sep to submission.** Created 20 Sep 2026 · Phase 1 complete · survey + MVP candidate reconciled.

**Deadline:** 7 Oct 2026, 3:59 PM IST · **Personal done-date:** 5 Oct
**Research plan (what must be proved):** `Google_Photos_Case_Study_Plan_2.md`
**Rules (what not to repeat):** `SCORECARDS_AND_LESSONS.md`
**Running log (what happened):** `PROGRESS.md`

This file is the *execution* layer: what to do next, in order, by whom, and what "done" means.
Plan 2 says what must be proved; it does not sequence the work. That gap cost three days —
recruitment has been ready since 18 Sep and is still unposted because nothing made it a dated,
blocking step.

---

## 0. Operating rules

Learned this week, not theoretical. Breaking these has already cost time.

| Rule | Why |
|---|---|
| Groq free tier: **190K tokens/day per model**, resets 00:00 UTC (05:30 IST) | Both `gpt-oss-120b` and `qwen/qwen3.8-27b` have separate budgets |
| **Don't launch at the reset** | 20 Sep: 5–25 posts/hour right after rollover vs ~800 later. Likely a thundering herd |
| **Never run two jobs against the same Groq model at once** | A diagnostic halved extraction throughput on 20 Sep |
| **Redirect with `>>`, never pipe through `tee`** | The shell reports tee's exit code; a crashed run looked clean |
| Apify: **$2.84 left** of the $5 monthly credit | Trial 20 items before any bulk run; `searchCommunityName` is the field that scopes a search |
| `pytest -q tests` green before stopping | **150 tests** as of 20 Sep |

---

## 1. Status at start (20 Sep)

**The engine is finished.** 85,140 posts collected across Play Store, App Store, YouTube and Reddit
→ 5,305 Gate A candidates → 1,333 Gate B labels (819 relevant) → **720 extracted episodes, 144
specific attempts, 62 scoreable**. Blind cross-family audit on **203 pairs**: both models lead
**H3 (dead end)**, but top-2 sets differ, so the pre-registered rule sends the tie-break to
interviews.

**Everything remaining depends on six interviews that have not been recruited for.**

---

## 2. Phase 0 — Unblock (today, 20 Sep)

**You:**
- [ ] **Post the recruitment call.** `research/recruitment.md` is ready. Needs a Google Form link
      and a compensation decision. *This is the critical path and it is 3 days late.*
- [x] ~~Rotate the Groq key~~ **done 20 Sep**, verified working. Confirm in the console that the old key is deleted.
- [ ] Create a Hugging Face account + Gradio Space, add `GROQ_API_KEY` as a secret.
- [ ] **Run both form scripts** (`screener_form.gs`, `survey_form.gs`) at script.google.com and post
      them — screener to your network, survey to LinkedIn and the subreddits.

**Me:** nothing blocked — start Phase 1.

---

## 3. Phase 1 — MVP shared base (21–26 Sep)

Deliberately **hypothesis-independent**, so it can be built before the problem locks on 26 Sep and
Phase 4 isn't standing still. Decisions taken 20 Sep: **CLIP-only index** (no Gemini dependency),
**500 images** (Plan 2 §9's own documented cut).

**✅ COMPLETE (20 Sep).** 131 tests green.

| # | Step | Result |
|---|---|---|
| 1.1 | CC images from Openverse with a hard-case quota | **494 images**, 12 categories at quota |
| 1.2 | Synthetic metadata forming life episodes | **25 episodes**, 232 placed, 262 stray |
| 1.3 | CLIP index (sentence-transformers, CPU) | **494 embedded, 0 skipped**, ~6 min |
| 1.4 | Plain-similarity baseline | `baseline_search` vs `filtered_search` |
| 1.5 | 30 tasks, cue mix from real episodes | **83% single-cue**, dominated by vague time |

**Headline result — the MVP's case, measured:**

| Strategy | recall@20 | hit@1 |
|---|---|---|
| Baseline (plain CLIP) | 0.053 | 0.000 |
| Oracle (perfect clue→window, same CLIP) | **0.583** | **0.233** |
| **Lift** | **+0.530** | +0.233 |

Same embeddings, same images, same queries. The only difference is turning a vague clue into a
metadata window — and the baseline scores **0.052 on `temporal_approx`**, the most-retained real cue.

**Carry these caveats to the slide:** the oracle is an **upper bound**, not the MVP (it assumes
flawless clue→window inference); and it stops at 0.583 because some tasks are **unanswerable in
principle**. Phase 4's real number will land between 0.053 and 0.583.

**Known weakness:** CLIP scores 0.0 on `whiteboard`/`document` — text inside images. Captions are
the first fix if Phase 5 testing confirms it.

---

## 3b. Phase 1b — Survey (post today, analyse continuously)

Added 20 Sep. **Two forms, two audiences, do not merge them:**

| Form | Script | Goes to | Purpose |
|---|---|---|---|
| **Screener** (9 Q) | `research/screener_form.gs` | Personal network, WhatsApp | Fast interview bookings — the critical path |
| **Survey** (22 items) | `research/survey_form.gs` | LinkedIn, r/googlephotos, r/india | Wide reach + measures what the engine cannot |

**Why it earns its place despite being late scope.** The engine's hard finding is that only **8.6%**
of collected posts are scoreable and the rate does not move with the source — people don't narrate
complete retrieval attempts in public text. The survey *structures* the narration instead of hoping
to find it, so ~100% of qualifying responses are scoreable. At n=30 that roughly doubles the pool
(62 → ~90) and is not 86% Play Store.

It also converts **three modelled URR slots into measured ones** (Plan 2 §5.4) — Q3 → n̄,
Q4 → Expression, Q14 → outcome distribution — and per rule D that is the cheapest available gain in
Data & Metrics, the weakest competency at 27.08/40. Q10 is the only engine-side test of **H4** left.

**Import:** `engine/import_survey.py` (31 tests). Responses CSV → `data/interim/survey_episodes.jsonl`,
mapped 1:1 onto the engine vocabulary so they pool with `episodes.jsonl`.

```bash
.venv/bin/python -m engine.import_survey ~/Downloads/responses.csv
```

**Three things the import handles deliberately, and the deck must repeat:**
- **Q4 ≠ Q13.** Q4 is the *first move* (the Expression measure); Q13 is the fallback after failure.
  They land in `first_move` and `workarounds` — merging them would destroy Q4.
- **Survey hypotheses are rule-derived**, not model-assigned like the engine's. They carry
  `hypotheses_source: "rule"`. **Report the two separately; do not pool into one ranking.**
- **`era` is the response date, not the incident date** — the survey never asks when the failure
  happened. Flagged as `era_source: "response_time"`.

**Also carry to the deck:** self-reported recall, not observed behaviour · self-selection (people who
answer a survey about failing to find photos have failed to find photos — carry the denominator,
rule C) · Q12 forces one failure stage where a real session may cross several · **Q9 collects real
query strings, which contain names — scrub before quoting.**

**Acceptance:** ≥30 responses before the 26 Sep problem lock · import runs clean · willing-to-be-
interviewed responses routed into the screener funnel.

---

## 4. Phase 2 — Interviews (22–26 Sep) — you lead

Protocol in Plan 2 §6: critical incident (12 min) → self-run tasks, camera off (10) → timeline
probe (8) → recognition probe (5) → toggle question (5).

After each, I write notes into `research/interviews/NN.md` **using the same field vocabulary as
`episodes.jsonl`** (`specificity`, `cues_retained`, `failure_stage`, `outcome`, …) so interview
episodes merge with engine episodes rather than sitting in a separate silo.

**Acceptance:** ≥5 usable interviews · **≥3 participants who mix Hindi/English** — this is now the
only remaining test of H4.

---

## 5. Phase 3 — Problem lock (26 Sep) — HARD GATE

1. Score H1–H6 across interviews **and** engine episodes.
2. Write an explicit verdict for each: **supported / refined / overturned / not tested** (rule B).
   H4 is currently *not tested* — say so, don't let a zero read as evidence.
3. Lock the problem statement.
4. Choose the MVP core module.

**Highest-risk moment in the schedule.** If H3 wins, **slide 1's thesis line changes** — "Photos
indexes items; people remember episodes" points at H1/H2, while H3 is the dead-end/recovery story.
Per rule A the deck's whole front half is rewritten that week. This is precisely the CS2 failure.

---

## 6. Phase 4 — Core module + deploy (27 Sep – 1 Oct)

Branch per Plan 2 §7, all three pre-specified:
- **H1/H2 →** episode-first retrieval: clues → date window → episode cards → browse from an anchor
- **H3 →** refine-by-pointing, with a recovery question as fallback
- **H4 →** code-mixed query rewriter before the shared index

### Candidate design: Memory Trails (added 20 Sep, **not yet chosen**)

Three files now describe a concrete MVP — `Google_Photos_—_Memory_Trails.pdf`,
`…Additional_MVP_Ideas…pdf`, `google-photos-memory-trails.html`. Full reconciliation with the
evidence is in **`research/memory_trails_reconciliation.md`**. Four points carry into this phase:

**1. Build stages 1 and 3 first; 2 and 4 are stretch.** The concept names three failure modes and
**all three are the rarest in the data**: `cannot_express` 1.4%, `cannot_refine` 0.7%,
`cannot_evaluate_results` 1.4%. What dominates is `not_surfaced` **41.7%** and
`system_misunderstood` **35.4%** — 77% of failures happen *before* the user needs to recover.
Stage 1 (clue chips) and stage 3 (visual trail) address those; stages 2 and 4 address under 3%.

**2. Where `failure_stage` and `hypotheses` disagree, trust `failure_stage`.** The audit measured
`failure_stage` at **κ 0.509** and `hypotheses` at **Jaccard 0.347** — the H3 lead comes from the
least reliable field on the form. Say so in one line on the slide rather than switching quietly.

**3. Only three pieces are genuinely new.** Clue-extraction from free text, the "why this matches"
explanation, and UI wiring. The library, index, `filtered_search`, episode clusters and the measured
baseline all exist from Phase 1 — and the **oracle already proves the mechanic works** (0.053 →
0.583). What is missing is *inferring* the window from text instead of being handed it.

**4. The prototype must become functional.** The HTML is scripted — a regex picks one of two
hardcoded scenarios, thumbnails are CSS gradients. Part 5 requires that *"another person can use it
to attempt a retrieval task."* Point that interface at the real 494-image index and it qualifies.

**Metric correction carried from `research/memory_trails_reconciliation.md` §2.1:** the concept doc
reverts to **session-level** success. Use **user-level URR** (Plan 2 §5). Session-level is the exact
defect §3D says to fix before Part 2.

**Space: bundle is READY, push is not.** `engine.export_space` has been run — the bundle now holds
**720 real episodes** (was a 10-post fixture), 720×384 embeddings and the audit report, and ships
only the evidence quote plus a public URL. It is **not deployed**: that needs your Hugging Face
account. Do it before the crunch, not during — Plan 2 §9 lists both public links as *never cut*.

Its spend cap was audited (20 Sep): enforced per **container life**, not per day, because a Space
filesystem is ephemeral. Acceptable, because `DEMO_MODEL` is `gpt-oss-20b` which the pipeline does
not use — the worst case is the demo degrading, never the pipeline stalling. Add the **new** Groq key
as the `GROQ_API_KEY` secret.

**Acceptance (1 Oct):** another person can open the link and complete a retrieval task.

---

## 7. Phase 5 — User testing (1–3 Oct)

3–5 target users on tasks taken from **their own** critical incidents. Test → fix the top 2 issues →
re-test lightly.

**Evaluation report:** success rate · steps to find · recall@20 vs baseline · false-confirmation
rate · added latency.

---

## 8. Phase 6 — Deck (3–5 Oct)

1. **Build the facts table first** — claim → number → source → slide — and check every figure
   against it (rule C). CS2 lost points to the same statistic appearing with two values.
2. Then the 10 slides per Plan 2 §10.
3. **Final pass:** read the deck in order and ask *does every slide argue the same problem?*
   Any slide that doesn't gets cut or rewritten. This single pass is worth more than any other
   hour spent on the deck.

Budget the deck, not the styling — Presentation scored above median in both prior attempts (rule F).

---

## 9. Phase 7 — Submit (by 7 Oct, 15:59 IST; personal done-date 5 Oct)

Checklist from `SCORECARDS_AND_LESSONS.md` §4: 10 slides max · **name nowhere, including PDF
metadata** · each slide title states its message · ≥14pt · colour-blind-safe · <40 MB · filename
`NL_GooglePhotos` · every link opened in an incognito window · the phrase "users find it difficult
to search for old photos" appears nowhere.

---

## 10. Disclosures the deck must make

Carried forward so they cannot be forgotten. Each is a strength if stated plainly and a liability
if discovered by a grader.

- **Play Store is 86.2%** of extracted episodes against the plan's own 60% per-source cap
- **H4 was not tested**, not overturned — the `query_language` field returned "en" for every post
- `evidence_verified`: primary **85.2%**, audit 97%
- Extraction was **deliberately closed** at 720/819, with the reason
- URR baselines are **modelled, not measured** — no Google telemetry
- The audit **overturned** the primary model's original ranking (rule B: this scores well)
- Model agreement tracks source richness: `outcome` κ 0.27 on Reddit vs 0.13 on Play Store

---

## 11. Cut order if behind (Plan 2 §9)

H4/H5 sources → evaluation tasks 30→15 → library 500→250 → re-test round.

**Never cut:** the audit · 5 interviews · both public links · the evidence-chain slide.

---

## 12. Open decisions

- [ ] Spend the remaining **$2.84** Apify credit on r/india for H4 evidence? *Recommendation: no.*
      The 20 Sep finding that scoreable yield is source-independent (~8.6% across four platforms)
      argues against more collection. The interviews' Hinglish quota is the better test.
- [ ] Re-extract `query_language` to rescue H4 from the engine side? *Recommendation: no* — a day
      of tokens to infer code-mixing from English-language app-store reviews.
