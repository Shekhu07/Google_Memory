# Implementation Plan — Google Photos Case Study

**Working document from 20 Sep to submission.** Created 20 Sep 2026 · last updated **1 Oct 2026**.

**Deadline:** 7 Oct 2026, 3:59 PM IST · **Personal done-date:** 5 Oct
**Research plan (what must be proved):** `plans/Google_Photos_Case_Study_Plan_2.md`
**Rules (what not to repeat):** `brief/SCORECARDS_AND_LESSONS.md`
**Running log (what happened):** `plans/PROGRESS.md`

**Facts table:** `research/analysis/facts_table.md`. **Every deck number comes from it** (rule C).

## Status on 1 Oct (6 days to deadline, 4 to done-date)

| Area | State |
|---|---|
| Discovery engine + link | ✅ Done, live |
| MVP + link | ✅ Done. **Redeployed 1 Oct to both projects** (visual-cue suggestions after a miss, misdated-memory flag rework, API pinned to Mumbai). Verified live: pages 200, `/api/py/health` shows 1,282 images, search returns cue suggestions |
| Problem statement, Part 4 draft | ✅ Locked (§5); draft in `research/analysis/part_4_problem_definition.md` |
| Parts 7, 8, workflow slide | 🟡 Drafted, but the 30 Sep cross-check found **slides 2 and 10 use different URR formulas** (§8b) |
| Facts table | 🟡 Sections A–F verified; **G (primary research) still empty** |
| Survey | ❌ Live since 22 Sep. **Still not shared, 0 responses.** Proto-personas (30 Sep, `Claude outputs/survey-proto-personas.md`) are hypotheses, not data |
| **Interviews (Part 3)** | ❌ **0 of 5–6. Screener still unposted.** Re-dated 1 Oct: slots Fri 2 – Sun 4 Oct |
| **MVP tests (Part 6)** | ❌ **0 of 3**. Kit ready (`?study=P01`, `research/testing/mvp_test_protocol.md`). Re-dated: 3–5 Oct |
| Own-library probe | ⚠️ `research/testing/probe-log.csv` holds only the six search terms, yet the 30 Sep cross-check quotes probe results from 26 Sep. **Copy those results into the CSV** so the facts table can cite them |
| Deck | 🟡 Skeleton only (`deck/deck_skeleton.md`); layout 3–5 Oct |
| MVP screenshots | ✅ 7 shots from 28 Sep in `design/mvp-screenshots/`. They predate the 30 Sep visual-cue suggestions; retake only if a slide shows that screen |

**The critical path is still people, not code.** The 28 Sep version of this table said "post the
screener before anything else"; three days later it is still unposted and the original interview
slots have passed. **Order for 1 Oct: post the screener and share the survey today, before any other
work.** Then 2–4 Oct interviews, 3–5 Oct MVP tests with 3 of the same people, 3–5 Oct facts table G,
the §8b fixes and deck layout.

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
| `pytest -q tests` green before stopping | **219 tests** as of 28 Sep (was 150 on 20 Sep), plus 95 in `webapp/apps/retrieval/tests` |
| **Deploy from an export while the repo is private** | 28 Sep: a plain `vercel deploy` is BLOCKED (`TEAM_ACCESS_REQUIRED`). The commit author "Memory Trails" is not a Vercel member, and the CLI shows "Building…" forever. Hit again 30 Sep–1 Oct: three blocked deployments, removed. Instead: `git archive HEAD webapp` into a scratch folder, copy in the gitignored encoder weights from `webapp/apps/retrieval/data/` (never `.env.local`), then `npx vercel deploy --prod --project <name> -y` from there. Deploy memory-trails-demo, then memory-trails-v2, one at a time. Check real state with `vercel api /v13/deployments/dpl_<id>` |

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
- [ ] **Post the recruitment call.** `research/recruitment/recruitment.md` is ready and re-dated (28 Sep).
      **Compensation: none** (decided 28 Sep). Needs only the screener's live link.
- [x] ~~Rotate the Groq key~~ **done 20 Sep**, verified working. Confirm in the console that the old key is deleted.
- [x] ~~Create a Hugging Face account + Gradio Space~~ **obsolete**: both links deployed on Vercel instead (§6).
- [x] **Survey form live 22 Sep** → https://docs.google.com/forms/d/e/1FAIpQLSd6InawAamMykxoj6QTHq8Cgp1sgadLT3ZTrjHWjC6eerTltw/viewform
      Still to do (**open on 1 Oct**): post it to LinkedIn and the subreddits.
- [ ] **Run `research/recruitment/screener_form.gs`** at script.google.com and post it to your network. **Still open on 1 Oct, and
      the single blocker for Parts 3 and 6.** Re-dated 1 Oct (the 28 Sep slots have passed): interview slots
      Fri 2 – Sun 4 Oct, plus a required question on the 15-minute MVP follow-up (3–5 Oct) so Part 6 returners
      come from the same pool.

**Me:** nothing blocked — start Phase 1.

---

## 3. Phase 1 — MVP shared base (21–26 Sep)

Deliberately **hypothesis-independent**, so it could be built before the problem was settled and
Phase 4 wasn't standing still. That bet paid: the MVP was finished before the verdicts were written,
and §5 confirms it was built on the right hypothesis. Decisions taken 20 Sep: **CLIP-only index** (no Gemini dependency),
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

**Superseded 21 Sep — do not call the oracle an upper bound.** A third strategy, `inferred` (the
extractor the deployed service runs, deriving filters from the query text alone), scores
**recall@20 0.612** and *beats* the oracle's 0.583. `filters_for` turns out to be a **±45-day
heuristic** handed the answer's date, not an optimal policy: a month-precise reading of
"July 2025ish" is both more faithful and narrower, and at k=20 narrower wins.

| Strategy | recall@20 | hit@1 |
|---|---|---|
| Baseline (plain CLIP) | 0.053 | 0.000 |
| Oracle (±45d around the answer's date) | 0.583 | 0.233 |
| **Inferred (text alone — what ships)** | **0.612** | 0.200 |

**CURRENT NUMBERS (22 Sep) — the library is now 1,250 photos.** 508 everyday photos (sky, home food,
commute, screenshots…) were appended as distractors; the 30 tasks and the original 492 records and
vectors are unchanged. Measured with the shipped encoder:

| Strategy | recall@20 | hit@1 |
|---|---|---|
| Baseline (plain CLIP) | **0.012** | 0.000 |
| Oracle (±45d around the answer's date) | **0.417** | 0.167 |
| **Inferred (text alone — what ships)** | **0.479** | 0.133 |

A further 250 Indian photos (dal, biryani, dosa, thali, rangoli, puja, auto-rickshaws, and
11 tourist places dated as short trips in their real cities) brought it to **1,250 with every
number unchanged** — none reaches a task's top 20. Inferred still beats the oracle, and now **not** because of tiny windows: only 2 of 21 temporal
tasks have ≤20 candidates, for both strategies (was 7 vs 3). The tables above are the 494-image
record. **Quote these numbers, not those.**

**SUPERSEDED 23–24 Sep — the three tables above are history, not headline.** Two things changed:

1. **`soft` scoring now ships** (default since 23 Sep): exponential decay around the inferred window
   instead of a hard filter, so a slightly-wrong date never excludes the right photo. The "Inferred
   — what ships" row above is `inferred_rules`, which no longer ships. **Soft has not been run on
   the synthetic-30 set**, so 0.479 is not a number for the shipped product.
2. **Two new evaluations**: a 30-task held-out **real-phrasing** set (soft **0.866** vs baseline
   0.172), and the **cue-dropout ladder**, 120 tasks at four levels of degraded memory:

| Level | Query keeps | Baseline | **Soft (ships)** | Soft moment@5 |
|---|---|---:|---:|---:|
| L3 | vague time + exact place + library word | 0.172 | **0.962** | 0.933 |
| L2 | paraphrased content + two vague cues | 0.209 | **0.276** | 0.333 |
| L1 | paraphrased content + one vague time cue | 0.242 | **0.309** | 0.333 |
| L0 | content only | 0.312 | **0.312** | 0.267 |

**Read it honestly:** the large gain needs place *and* time (L3). With one vague time cue, which is
the most common real memory, the gain is **+0.07**; with content only it is zero, and the parser
adds no false filters. The real-phrasing set is also L3. **Decided 28 Sep: the ladder is the headline**, shown as a ladder and not as one number (`research/analysis/facts_table.md` §E).
The Part 4 and Parts 7/8 drafts were updated to match on 28 Sep.

**Three caveats that must travel with 0.612** *(494-image figures; the same caveats hold for 0.479)*: the tasks are synthetic and the extractor was written
knowing their three vague-time phrasings; recall@20 mechanically rewards narrow windows (≤20
candidates means automatic recall, true for 7 of 21 temporal tasks); and the win is uneven — month
precision wins big while "sometime in 2024" widens to 222 candidates and loses. See `plans/PROGRESS.md`.

**Known weakness:** CLIP scores 0.0 on `whiteboard`/`document` — text inside images. Captions are
the first fix if Phase 5 testing confirms it.

---

## 3b. Phase 1b — Survey (post today, analyse continuously)

Added 20 Sep. **Two forms, two audiences, do not merge them:**

| Form | Script | Goes to | Purpose |
|---|---|---|---|
| **Screener** (10 Q) | `research/recruitment/screener_form.gs` | Personal network, WhatsApp | Fast interview bookings + Part 6 follow-up opt-in — the critical path |
| **Survey** (26 items) — [live](https://docs.google.com/forms/d/e/1FAIpQLSd6InawAamMykxoj6QTHq8Cgp1sgadLT3ZTrjHWjC6eerTltw/viewform) | `research/survey/survey_form.gs` | LinkedIn, r/googlephotos, r/india | Wide reach + measures what the engine cannot |

**Why it earns its place despite being late scope.** The engine's hard finding is that only **8.6%**
of collected posts are scoreable and the rate does not move with the source — people don't narrate
complete retrieval attempts in public text. The survey *structures* the narration instead of hoping
to find it, so ~100% of qualifying responses are scoreable. At n=30 that roughly doubles the pool
(62 → ~90) and is not 86% Play Store.

It also converts **three modelled URR slots into measured ones** (Plan 2 §5.4) — Q3 → n̄,
Q4 → Expression, Q14 → outcome distribution — and per rule D that is the cheapest available gain in
Data & Metrics, the weakest competency at 27.08/40. Q10 is the only engine-side test of **H4** left.

**Import:** `engine/import_survey.py` (37 tests as of 28 Sep). Responses CSV → `data/interim/survey_episodes.jsonl`,
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

**Merged in `research/survey/Google Photos Survey.md` (21 Sep).** That document proposed a 32-question replacement.
Three parts of it were better than what we had and were taken; four would have broken the research
and were not.

**Taken:** an **Ask Photos block** (5 questions) — Ask Photos is the incumbent answer to this
problem, and the deck cannot say what it already solves without asking · an **"uncertain" outcome**
("found something similar but was not sure", "found the right trip but not the photo"), which is the
group the MVP exists for and which was previously collapsed into `unknown` · a **recognition-needs
question** whose options are the Memory Trails feature set, asked of people who have just described a
real failure.

**The concept-reaction block was built and then cut (21 Sep).** Every question costs completions, the
gate is ≥30 responses in five days, and Phase 5 testing answers the same question with observed
behaviour instead of self-reported interest.

**Not taken, and why:** it had **no language question**, which would leave H4 untestable from both
sides · its failure list had **6 options against the engine's 9**, dropping `browse_path_changed`
(**H6, in the audit's top-2**) · it forced a **single** most-remembered cue and capped the forgotten
cues at two, which would manufacture the one-cue distribution the engine measured rather than test it
· its library buckets stopped at "more than 2,000", below the brief's 5,000+ long-tenure user · it
dropped `query_verbatim`, losing real query strings · and it moved contact capture to a separate
form, adding a step to the funnel that is currently the critical path.

**No Apps Script branching.** The source document specifies it; Apps Script navigation cannot be
tested from here, and an untested branch on the form that gates recruitment is not worth the saved
taps. The Ask Photos section is a page break with a skip instruction and every question optional.

**The hypothesis-bearing questions are now required (21 Sep).** Previously only section 1 was
mandatory, so a respondent could answer four questions and submit, leaving a row with no failure
data at all. **16 of 26 questions are required now**, chosen on one rule: a hypothesis, a URR term or
a required brief deliverable depends on it, *and* the option list has a safe escape. Free text stays
optional throughout — required open text is the fastest way to lose a respondent.

This needed the branching I had previously declined. A **gate question sits alone on its own page** —
*"Has this happened to you in the last year?"* — and routes *"No, this has not happened to me"*
straight to submit via `FormApp.PageNavigationType.SUBMIT`. Without it, required section-2 questions
would trap the very people the form tells to skip. Their answer is still captured as `had_failure`,
which is the denominator for how common the problem is. This is the simple form of Apps Script
navigation — a choice routing to submit, on a page with no other question — rather than the
multi-page routing I still will not ship untested.

Now **26 questions, stated as 6 minutes**. `retrieval_certainty` (exact / uncertain / failed) is
derived on import, and the six survey-only fields are declared in `SURVEY_ONLY_FIELDS` so the
vocabulary lock still applies to everything that merges with `episodes.jsonl`.

**Acceptance:** ≥30 responses · import runs clean · willing-to-be-interviewed responses routed into
the screener funnel.

**The survey is now the main open research item.** With the lock gone it no longer races a date, but
it still carries the only remaining test of **H4** (Q10) and the only measured read on the
**uncertain** group (Q15). Post it.

---

## 4. Phase 2 — Interviews — supporting evidence, not a blocker (21 Sep)

Protocol in Plan 2 §6: critical incident (12 min) → self-run tasks, camera off (10) → timeline
probe (8) → recognition probe (5) → toggle question (5).

After each, I write notes into `research/interviews/NN.md` **using the same field vocabulary as
`episodes.jsonl`** (`specificity`, `cues_retained`, `failure_stage`, `outcome`, …) so interview
episodes merge with engine episodes rather than sitting in a separate silo.

**CORRECTION (21 Sep, after auditing the actual brief).** I previously wrote that interviews were
optional once the MVP was built. **That was wrong.** The brief makes them a scored requirement, in
two separate Parts:

> **Part 3:** *"AI-generated insights are only a starting point. Conduct **5–6 user interviews** with
> respondents from the target segment you choose."*
>
> **Part 6:** *"Return to at least **3 users** from your target segment and ask them to interact with
> your MVP… Document what you learned and what you would change in the next iteration."*

These are not limitations to disclose — they are **two missing components of the graded work**. The
brief explicitly anticipates the exact shortcut I proposed and forbids it: AI insight alone is a
starting point, not the research.

The problem statement is still locked from the engine evidence (§5), and the MVP is still built, so
neither blocks the other work. But interviews go **back on the never-cut list**, and the deck cannot
honestly claim Parts 3 and 6 without them. If any happen, two things are worth more than the rest: a **Hinglish speaker**, because
H4 is otherwise "not tested", and anyone who **found something and could not tell if it was right** —
the uncertain group the MVP exists for.

**If none happen**, Parts 3 and 6 are simply unmet, and the deck should say so rather than imply
otherwise. But the correct move is to get them: **5–6 for Part 3, then at least 3 of those same
people back for Part 6** against the live MVP. The screener exists for exactly this.

---

## 5. Phase 3 — Hypothesis verdicts and the problem statement (no longer a dated gate)

**The 26 Sep lock is removed (21 Sep).** It existed to gate the MVP core-module choice on
interviews. The MVP is built and deployed, interviews were never recruited for, and holding a gate
whose input does not exist just stalls the deck. Interviews are now **supporting evidence, welcome if
they happen**, not a blocker.

**What the lock was actually for still has to happen, and it is not optional.** CS2 lost **14.35
points of Clarity** — more than the whole miss — because its problem slides argued one thing while
its solution slides built another. The verdicts below are what stop that repeating.

### The verdicts, written from the evidence that exists

Rule B: every hypothesis gets a stated verdict, including the ones that lose.

| | Verdict | On what evidence |
|---|---|---|
| **H1** episodic time | **Supported, and it is the thesis** | `temporal_approx` is the most-retained cue (40 of 144) and the most-lost is the exact date (37). The index cannot use "roughly when". **Retrieval evidence, the narrower claim (28 Sep):** on the cue-dropout ladder the window is decisive when place survives too (L3 0.172 → 0.962) and modest on one vague time cue alone (L1 0.242 → 0.309, hit@1 0.000). The retired "0.053 → 0.612" is not quoted |
| **H2** recognition | **Supported, secondary** | `not_surfaced` **41.7%** — the photo was there and never came up. Answered by episode grouping, not by better ranking |
| **H3** dead end | **Refined, not supported as the lead** | Both audit models led with H3, but that comes from `hypotheses`, the **weakest** field (Jaccard 0.347). The reliable `failure_stage` (κ 0.509) puts `cannot_refine` at **0.7%** — 1 episode in 144. **Say which field decided it and why**; this is the audit overturning its own ranking, which scored well in CS1 |
| **H4** code-mixed | **Not tested** | `query_language` returned "en" for all 203 audited posts. A zero here is silence, not evidence. Survey Q10 is the only remaining test and needs responses |
| **H5** nothing to index | **Weakly supported** | CLIP scores **0.000** on `whiteboard`/`document`, and the *oracle* scores 0.000 too — the index cannot represent text inside an image at all |
| **H6** learned path broken | **Present but minor** | `browse_path_changed` **8.3%**, third behind the two leaders. Real, not the story |

### The locked problem statement

> People remember *when-ish* and *what happened*, and Google Photos indexes *items*. So the photo is
> there, the person can describe the moment but not the photo, and it never surfaces. **77% of
> observed failures happen before the user ever needs to recover** — the query is misread (35.4%) or
> the photo never appears (41.7%).

**Every slide argues that or gets cut.** The front half of the deck follows from this line, per rule A.

### Consequences now settled

- **MVP core module: episode-first retrieval (H1/H2).** Built, deployed, measured. No branch pending.
- **Stage 2 is cut; stage 4 is a light safety net (revised 28 Sep, fixes checklist 1.4).** The
  clarifying question serves `cannot_express` (1.4%) and stays cut. Near-miss recovery serves
  `cannot_refine` (0.7%), so it ships only as one question after "Not this moment", with each answer
  changing one clue. It has no URR term and is measured as a diagnostic. **State the scope and the
  number on the slide.**
- **What would reopen this:** the survey returning heavy `cannot_refine` or a real Hinglish signal.
  If that happens before the deck is written, say so and revise. Otherwise these verdicts stand.

---

## 6. Phase 4 — Core module + deploy (27 Sep – 1 Oct)

Branch per Plan 2 §7, all three pre-specified:
- **H1/H2 →** episode-first retrieval: clues → date window → episode cards → browse from an anchor
- **H3 →** refine-by-pointing, with a recovery question as fallback
- **H4 →** code-mixed query rewriter before the shared index

### Candidate design: Memory Trails (added 20 Sep, **not yet chosen**)

Three files now describe a concrete MVP — `design/Google_Photos_—_Memory_Trails.pdf`,
`…Additional_MVP_Ideas…pdf`, `design/google-photos-memory-trails.html`. Full reconciliation with the
evidence is in **`research/analysis/memory_trails_reconciliation.md`**. Four points carry into this phase:

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

**Metric correction carried from `research/analysis/memory_trails_reconciliation.md` §2.1:** the concept doc
reverts to **session-level** success. Use **user-level URR** (Plan 2 §5). Session-level is the exact
defect §3D says to fix before Part 2.

**The Hugging Face Space paragraph below is obsolete (28 Sep):** both links went to Vercel.

**Space: bundle is READY, push is not.** `engine.export_space` has been run — the bundle now holds
**720 real episodes** (was a 10-post fixture), 720×384 embeddings and the audit report, and ships
only the evidence quote plus a public URL. It is **not deployed**: that needs your Hugging Face
account. Do it before the crunch, not during — Plan 2 §9 lists both public links as *never cut*.

Its spend cap was audited (20 Sep): enforced per **container life**, not per day, because a Space
filesystem is ephemeral. Acceptable, because `DEMO_MODEL` is `gpt-oss-20b` which the pipeline does
not use — the worst case is the demo degrading, never the pipeline stalling. Add the **new** Groq key
as the `GROQ_API_KEY` secret.

**DEPLOYED 21 Sep.** Both public links are live on one Vercel project:

**The brief lists two separate link deliverables**, so these are two separate Vercel projects:

| Deliverable | Link |
|---|---|
| **[Link] AI-Powered Discovery Engine** — *"link where the workflow can be tested"* | **https://retrieval-discovery-engine.vercel.app** |
| **[Link] Deployed AI-Native MVP** — *"a publicly accessible prototype… that can be interacted with and tested"* | **https://memory-trails-demo.vercel.app** |
| *(supporting)* CC credits for all 1,282 photographs | https://memory-trails-demo.vercel.app/attribution |

**Corrected 21 Sep.** These were originally one project with the engine at `/evidence`, designed
against Plan 2 §9's phrase "both public links" rather than against the brief's deliverables list.
The brief names them as two distinct links, so they are now two deployments that link to each other.

They share one codebase: `engine/export_web.py` generates both, so **the extractor cannot drift
between the two links**, and a test asserts the two copies of `clues.py` are identical. The engine
needs no images, no CLIP encoder and no image vectors — **120 KB against the MVP's 150 MB**.

Verified live: clue extraction runs through Groq (`source: "llm"`) and degrades to rules when the cap
is hit; trails returns 3 photos in 1 episode where plain search returns 20 across 16; all three pages
return 200; and **no personal name appears in the URL or any page source**.

**Cite the production alias only.** Preview URLs embed the Vercel account slug, which is not neutral.

**Wireframe conformance (21 Sep).** `google-photos-memory-trails-flow-wireframe.pdf` specifies six
screens and a state model. The deployed MVP now implements the state machine
`compose → recap → moments → episode → confirmed`, plus `moments → empty`, and all 12 §8
instrumentation events. **Acceptance criteria: 7 of 9 met**, up from 3½.

| Screen | State |
|---|---|
| 1 Find a memory · 3 Likely moments · 4 Episode view · 6 No useful moment | ✅ Conform |
| 2 Memory recap | ⚠️ Clues removable, not yet *editable*; **no clarifying question** |
| 5 Near-miss recovery sheet | ✅ Light version, 28 Sep: "What feels wrong about this moment?", 5 answers, one clue each, with Undo |

*Revised 28 Sep:* screen 5 now ships as a safety net (§5); the paragraph below records the original cut.

**The two held screens are stages 2 and 4, deliberately.** They address `cannot_express` (1.4%) and
`cannot_refine` (0.7%) — the rarest failures in the corpus. Per §6.1 and the reconciliation doc they
are **cut, not held** (§5). Acceptance #3 ("choose Not sure and continue") and #6 ("reject a near
miss and continue") stay unmet by design; #6 is partly served by **Not this moment**, which returns
to the candidate list without restarting. **State the cut and its 1.4% / 0.7% reason on the slide.**

**Screen 4 was built regardless of the lock** because without it there is no `retrieval_confirmed`,
and Phase 5 could not measure success at all. A facilitator reads the session log from
`window.memoryTrails` — it carries the event trail, seconds-to-confirm and a `withinFiveMinutes`
flag, and **never the text a participant typed**.

**Still to fix in the source document:** the wireframe's primary metric is *session-level* again
(§1). That is the third document carrying the defect §2.1 corrected on 18 Sep. Use user-level URR.

**Design specification implemented (21 Sep).** `design/Memory Trails MVP — Design Specification.md` replaced
the visual direction entirely: the "quiet gallery" — off-white page, white surfaces, graphite ink,
soft blue action colour, Google Sans stack with Inter as the web fallback. All 12 colour tokens, the
seven-role type scale, 12/20px radii and the single shadow level are taken from it. Layout is 1120px
max, two-column above 900px with a sticky 340px memory rail, single column and 16px gutters below.

Three defects were caught by *measuring* rather than looking, all of them acceptance criteria in §11
of that spec: **470px of horizontal overflow at a 320px viewport** (grid items default to
`min-width: auto`, so scrolling rails widened the page instead of scrolling), **28×28px clue-remove
buttons** against a 44px minimum, and a privacy pill that overflowed the top bar on small screens.
Verified at 320px: no overflow, 132px thumbnails, zero targets under 44px.

**Enhancement roadmap implemented (21 Sep).** `design/Memory Trails MVP — Experience Enhancement Roadmap.md`
§11 names five elements; **four are built**:

| Element | Serves | State |
|---|---|---|
| Episode-level ranking (§1.2, P0) | how people remember moments | ✅ coverage × coherence × recognizability × evidence |
| Memory breadcrumb (§11.2) | `system_misunderstood` 35.4% | ✅ persists through episode browsing |
| Density cues (§11.3) | `not_surfaced` 41.7% | ✅ "14 photos · 5 street scenes · 3 match your clues" |
| Evidence expansion (§11.5) | trust guardrail | ✅ per-dimension certainty and provenance |
| Optional mismatch reason (§11.4) | `cannot_refine` **0.7%** | ✅ **light, 28 Sep**: the recovery question, with no URR term |

Also built: **§2.1 memory strength selector** (stops a throwaway "small café" outweighing a confident
"Goa"), **§1.4 per-dimension certainty** instead of one global number, **§4.2 rejections that stick**
— `episode_rejected` fired and did nothing, so the same candidate returned immediately — **§4.3 undo**
on clue removal, and **§5.4** one optional question after confirmation for Phase 5.

**Carry this caveat to the deck.** The `usefulness` formula is defensible but its weights — 0.55 for
an unnamed episode, the span thresholds, `0.4 + 0.15n` for recognizability — are **judgement, not
measured**. The 30-task eval scores photo recall, not episode ordering, so it cannot validate them.
If a slide claims the ranking is evidence-led, that is the one part that is not. Phase 5 tests it.

**Added 23–25 Sep, after this section was written:** parser fixes P1–P7 (seasons, New Year's Eve,
trip-relative dates, the "may" guard, all 59 categories reachable), festivals, numeric dates and
Hinglish time phrases · soft scoring · a per-card **match ledger** (`Goa ✓ · café ✓ · date +21 days`)
· resolved date chips with one-tap alternatives · an outside-window strip · episode aliases ·
**"Not in any of these?"** under the moments (25 Sep). The over-interpretation guard means a
content-only description yields zero filters. The Hinglish time phrases are parser support; they are
**not** evidence for H4.

**Acceptance (1 Oct):** another person can open the link and complete a retrieval task. **Met.**

---

### 6d. Fixes checklist applied (28 Sep)

`plans/Memory Trails Prototype — Fixes Checklist.md`, reviewed against memory-trails-v2. Four decisions
taken first: recovery gets a **light** version; the four new scenarios get **real photos**; Goa and
medicine are removed from **examples and copy only**, while the library keeps its Goa trips; the build goes to
**both** Vercel projects, and **memory-trails-demo stays the cited link**. That link had been stale
since 23 Sep and lacked the ledger and "Not in any of these?".

- **Library 1,250 → 1,282.** Four curated episodes: sister's graduation (Pune, Jun 2025), college
  performance, old apartment, packing for the trip. 34 fetched, 9 rejected by eye, 7 hand-picked
  replacements, all 32 screened. Appended with new ids; existing records and the 30 tasks are untouched.
- **Examples:** the handmade cake from my sister's graduation · the group photo after our college
  performance · the handwritten note from my old apartment · my dog curled up in the suitcase. The
  checklist's "dog near the blue suitcase" was reworded, because no CC photo shows both.
- **Built:** "Describe the moment, not the photo" · "Add one thing you remember" with cue-type chips ·
  "What feels wrong about this moment?" (5 answers, each changes one clue, Undo, rejections stick) ·
  "You found the moment." with Open photo / View the surrounding moment / Done · "Why this moment?" as
  a sentence, with each clue marked in the first photo, in nearby photos, or approximate · a
  "+ Add a clue" option that never overwrites an existing clue · an About page covering Ask Photos and the
  data limits · month covers that are never medical or paperwork photos · 8 new tracking events.
- **Not done:** the compose button stays "Continue", because it leads to the clue check, not to moments.
  None of the four demo tasks separates Memory Trails from plain search: the new photos are
  distinctive, so plain CLIP finds them too. The ladder remains the evidence for the gap.
- **Numbers re-run** (see `research/analysis/facts_table.md` §E): soft L1 0.342 → **0.309** from the new
  photos. Separately, three result files were **stale before today** (rules real_test 0.818 → 0.718,
  soft hit@1 0.500 → 0.467), and soft on the synthetic set was measured for the first time (0.517).

## 7. Phase 5 — User testing (3–5 Oct; was 1–3 Oct)

3–5 target users on **representative tasks** (revised 28 Sep): the main task is the handmade cake from
a sister's graduation, and the optional ones are college performance, handwritten note, and dog in the suitcase. The
library cannot hold a participant's own photos, so their own incident is collected before the session
and coded for cue level, to check the representative task sits at the same level. Test → fix the top 2
issues → re-test lightly.

**Kit ready (24 Sep):** `?study=P01` turns on facilitator mode. Query text stays in memory only, and
"End session: copy log" copies the JSON. Protocol and consent line are in `research/testing/mvp_test_protocol.md`.
**Participants: none booked (1 Oct).** Recruit from the Part 3 interviewees so the brief's "return
to at least 3 users" is literally true.

**Evaluation report:** confirmed retrieval rate (`retrieval_confirmed` within 5 minutes) · time to first
useful moment · steps and clue edits · near-miss recovery rate · evidence-view rate ·
false-confirmation rate · abandonment (`prototype_exited`). Test URL:
`https://memory-trails-demo.vercel.app/?study=P01`.

---

## 7b. Parts 7, 8 and the required workflow slide — DRAFTED 21 Sep

`research/analysis/parts_7_8_workflow.md` carries all three, every figure verified against
`episodes.jsonl` and `audit_report.json`:

- **Part 7 — Success.** URR with **no Recovery term**. The MVP ships recovery only as a light safety
  net, measured as a diagnostic (near-miss recovery rate). Five
  leading metrics each tied to a URR term *and* an event the app already emits; six diagnostics;
  four guardrails led by **false confirmation**, the worst failure this product can produce.
- **Part 8 — Risks.** Six risks specific to this build, not generic AI risk. The two that matter
  most (rewritten 28 Sep): **R1, the win is concentrated where memory is richest**. The gain is
  +0.79 at L3 but +0.07 at L1, where most real users sit, and the ladder's queries were written by us.
  **R2, our own filter could hide the photo.** Its mitigation, soft scoring, is now **built**, and it lifts L3 recall@20
  from 0.851 (hard rules) to 0.962.
- **The workflow slide** — a *required* deliverable, previously missing. The funnel with its real
  numbers, the two design choices that make it more than summarisation, and the brief's own four
  questions answered from the 144 specific attempts.

## 7c. MVP presentation — the flow now sits inside a library (21 Sep)

The brief's Part 5 offers five forms and the first is **"a feature within Google Photos"**; the
design spec (§3.1) already committed to sitting "naturally within Google Photos". The deployed
link did not show that — it opened on a text composer with no library anywhere, which reads as
option 5, *a standalone prototype*.

This is a **Clarity** fix, not a presentation one, and that is the competency 21 points short of
the top-fellow median. The problem this deck argues is that *the library has no memory-based
re-entry point*. A library the grader cannot see is a library whose missing re-entry point cannot
be shown. The grid of 1,282 photos with a search bar above it **is** the problem statement.

What shipped: a phone frame (full-bleed on a phone, framed on desktop) holding a month-grouped
grid of all 1,282 photos; a Search tab that runs the **real `baseline` mode** — plain CLIP, measured
at 0.012 recall@20 — so the failure a visitor watches is the one the report measured; and a
"Can't describe it?" card that opens the existing flow full-screen with the typed query carried
over. Retrieval itself is unchanged, and the parity gates still pass.

**For the MVP slide:** say where in Photos this lives and why it belongs there rather than beside
it — it needs the user's own library and their own timeline, which no standalone tool has. The
shell makes the claim legible; the slide still has to make the argument.

**Not built, deliberately:** albums, photo detail, sharing, any Google branding. The shell states
it is a concept prototype over a simulated Creative Commons library, per design spec §12.

## 8b. Open fixes from the 30 Sep cross-check

From `Claude outputs/skills-cross-check-2026-09-30.md`. Each is a Clarity risk of the kind that cost CS2
14 points. **All five open on 1 Oct.**

- [ ] **Show the re-weighted number next to the ladder.** L3's 0.962 needs three cues, which only 6 of
      144 real attempts (4%) kept. Weighted by real cue counts: plain search 0.259, Memory Trails 0.334 (+7.5 pp).
- [ ] **Test "why not Ask Photos".** Re-run the 4 failed probe searches in Ask Photos mode (~15 min).
      If it finds 2 or more, slide 7 changes from "can't interpret" to "can't explain or correct".
- [ ] **Cutting Expression and Recovery rests on absence of evidence.** Survey Q4 and Q12 decide it;
      needs responses.
- [ ] **One URR formula.** Slide 2 keeps Recovery; slide 10 and Part 4 drop it. Make them match.
- [ ] **Two overstated numbers.** "4 of 6 never found" is 3 confirmed plus 1 unrecorded. "74% ended
      not found" comes from `outcome`, the weakest-agreement field (κ 0.161). Restate both.

---

## 8. Phase 6 — Deck (3–5 Oct)

1. **Build the facts table first** — claim → number → source → slide — and check every figure
   against it (rule C). CS2 lost points to the same statistic appearing with two values.
   **Started 28 Sep: `research/analysis/facts_table.md`.** A–F are verified from data files; G fills as
   research lands. It already found two conflicts: the headline retrieval number (§3), and
   evidence-verified at 85.2% (audit n=203) versus 90.4% (all 720).
2. Then the 10 slides. **Skeleton written 28 Sep: `deck/deck_skeleton.md`**, mapped to the brief's deliverables list (p.7–8) rather than Plan 2 §10, with no separate title slide.
3. **Final pass:** read the deck in order and ask *does every slide argue the same problem?*
   Any slide that doesn't gets cut or rewritten. This single pass is worth more than any other
   hour spent on the deck.

Budget the deck, not the styling — Presentation scored above median in both prior attempts (rule F).

---

## 9. Phase 7 — Submit (by 7 Oct, 15:59 IST; personal done-date 5 Oct)

Checklist from `brief/SCORECARDS_AND_LESSONS.md` §4: 10 slides max · **name nowhere, including PDF
metadata** · each slide title states its message · ≥14pt · colour-blind-safe · <40 MB · filename
`NL_GooglePhotos` · every link opened in an incognito window · the phrase "users find it difficult
to search for old photos" appears nowhere.

---

## 10. Disclosures the deck must make

Carried forward so they cannot be forgotten. Each is a strength if stated plainly and a liability
if discovered by a grader.

- **Play Store is 86.2%** of extracted episodes against the plan's own 60% per-source cap
- **H4 was not tested**, not overturned — the `query_language` field returned "en" for every post
- `evidence_verified`: primary **85.2%**, audit 97% (audit sample, n=203). The full 720 is **90.4%**; label whichever is quoted
- Extraction was **deliberately closed** at 720/819, with the reason
- URR baselines are **modelled, not measured** — no Google telemetry
- The audit **overturned** the primary model's original ranking (rule B: this scores well)
- Model agreement tracks source richness: `outcome` κ 0.27 on Reddit vs 0.13 on Play Store

---

## 11. Cut order if behind (Plan 2 §9)

H4/H5 sources → evaluation tasks 30→15 → library 500→250 → re-test round.

**Never cut:** the audit · both public links · the evidence-chain slide · a stated verdict for every
hypothesis · **5–6 interviews (brief Part 3)** · **3 MVP tests (brief Part 6)**. *(I briefly took
interviews off this list on 21 Sep. That was wrong — the brief requires them explicitly, and they
are back on.)*

---

## 12. Open decisions

- [ ] Spend the remaining **$2.84** Apify credit on r/india for H4 evidence? *Recommendation: no.*
      The 20 Sep finding that scoreable yield is source-independent (~8.6% across four platforms)
      argues against more collection. The interviews' Hinglish quota is the better test.
- [ ] Re-extract `query_language` to rescue H4 from the engine side? *Recommendation: no* — a day
      of tokens to infer code-mixing from English-language app-store reviews.
- [x] **Headline retrieval number: decided 28 Sep, the E1 ladder**, since it is the shipped strategy on 120 tasks and tests the brief's
      user who cannot describe the photo precisely. See `research/analysis/facts_table.md` §E. Blocks finalising
      the Part 4 and Parts 7/8 drafts (both updated 28 Sep).
