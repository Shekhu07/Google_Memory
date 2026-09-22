# Progress: Google Photos Retrieval Case Study

**Last saved:** Sun 20 Sep 2026, ~18:00 IST · **Deadline:** 7 Oct 2026, 3:59 PM IST · **Personal done-date:** 5 Oct
**Working document:** `implementation_plan.md` — phases, owners, dates and acceptance criteria from 20 Sep to submission. **Start here.**
**Plan of record (what must be proved):** `Google_Photos_Case_Study_Plan_2.md` (v1 kept for history)
**Read before Part 2 and again before the deck:** `SCORECARDS_AND_LESSONS.md` — CS1/CS2 scorecards and the mistakes not to repeat (final attempt; CS2 lost 14.35 Clarity points to a problem/solution mismatch)

---

## Where things stand

| Step | Status | Output |
|---|---|---|
| YouTube collection | ✅ Done: 3,624 comments pruned to 696 (24 on-topic videos), 2,913 quota units | `data/raw/youtube_*` |
| App Store collection | ✅ Done: 2,732 reviews, 8 countries | `data/raw/appstore_reviews.jsonl` |
| Play Store collection | ✅ Done: 81,256 reviews kept of 428,600 read (en + hi, back to Dec 2023) | `data/raw/playstore_*` |
| Gate A: keyword filter | ✅ Re-run with Reddit: **5,305 candidates** (was 5,171) | `data/interim/gate_a_candidates.jsonl` |
| Gate B: relevant or not (`gpt-oss-120b`) | ✅ **1,333 labelled**, 819 relevant (61.4%) incl. Reddit | `data/interim/gate_b.jsonl` |
| Extraction (`gpt-oss-120b`) | ✅ **Closed at 720 / 819 by decision**; 144 specific, **62 scoreable** | `data/interim/episodes.jsonl` |
| Audit (`qwen/qwen3.8-27b`) | ✅ **Re-run with Reddit: 203 pairs. Both models now lead H3** | `data/processed/audit_report.json` |
| Hugging Face Space demo | ✅ **Bundle rebuilt: 720 episodes** (was 10-post fixture); **not deployed** — needs your HF account | `space/` |
| Part 2: metric decomposition | ✅ **Corrected to user-level (URR)**; baselines are empty slots | `Google_Photos_Case_Study_Plan_2.md` §5 |
| Interview recruitment | 🔨 Kit drafted, **not posted** — needs Form link + compensation call | `research/recruitment.md` |
| Reddit via Apify | ✅ **456 collected → 134 Gate A candidates (29.4%)**, $2.16 spent | `data/raw/reddit_posts.jsonl` |
| MVP demo library | ✅ **1,000 images** (492 original + 508 everyday, 22 Sep), 25 episodes, all screened by eye (CC, attributed) | `data/demo/library.jsonl` |
| MVP CLIP index + baseline | ✅ **1,000 embedded** (original 492 vectors bit-identical) | `data/demo/index.npz`, `engine/demo_index.py` |
| MVP evaluation tasks | ✅ **30 tasks, 83% single-cue** (mix from real episodes) | `data/eval/tasks.jsonl` |
| MVP baseline → oracle → inferred | ✅ **0.012 → 0.417 → 0.479 recall@20** on 1,000 photos (was 0.053 / 0.583 / 0.612 on 494) | `data/eval/*_report.json` |
| MVP concept (Memory Trails) | ✅ **chosen, built, deployed** — episode-first retrieval (H1/H2) | `research/memory_trails_reconciliation.md` |
| MVP presentation | ✅ **21 Sep: wrapped in a phone-shaped photo library.** The flow is now a feature *inside* a library (brief Part 5, option 1), not a standalone page. Search tab runs the measured `baseline` mode. | `webapp/apps/web/app/components/PhotoApp.tsx` |
| Retrieval survey | ✅ **Live 22 Sep** ([form](https://docs.google.com/forms/d/e/1FAIpQLSd6InawAamMykxoj6QTHq8Cgp1sgadLT3ZTrjHWjC6eerTltw/viewform)); import built (**31 tests**); not yet shared | `research/survey_form.gs`, `engine/import_survey.py` |
| Interviews / MVP core / deck | ⬜ Not started — gated on interviews | — |

Tests: `.venv/bin/python -m pytest -q tests` (**150 pass**) · `cd space && ../.venv/bin/python -m pytest -q tests` (**5 pass**) · `cd space && ../.venv/bin/python -m pytest -q tests` (5 pass)

---

## Resume here (in order)

**The engine is finished (20 Sep).** Collection, Gate A, Gate B, extraction and the audit are all
complete or deliberately closed. No loop is armed; nothing is running. **Everything now waits on the
interviews.**

**Do these, in this order:**
1. **Post the recruitment call** — `research/recruitment.md` is ready; it needs a Google Form link
   and a compensation decision. Interviews are Sep 22–26 and the problem locks Sep 26. This is the
   critical path and it is late.
2. **Build the shared MVP base** (Plan 2 §7) — demo library, index, baseline, 30 evaluation tasks.
   Deliberately independent of which hypothesis wins, so it can be built before Sep 26.
3. **After the interviews:** pick the core module, lock the problem, then rewrite the front half of
   the deck to match (§3A — this is what cost CS2).

**Optional, not required:** deploy the Space (`engine.export_space` then push `space/`), or spend the
remaining $2.84 Apify credit on r/india for H4 evidence. Neither is on the critical path, and the
Sep 20 finding that yield is source-independent argues against more collection.

```bash
cd "/Users/abhishekspillai/Google CaseStudy"

# Engine is CLOSED. Collection, Gate A, Gate B, extraction and audit are all done or
# deliberately closed. Nothing below needs rerunning unless a decision changes.
#
# Optional, not required: re-run the audit so its sample includes Reddit episodes
# (~1 hour: Qwen's 1,000 OTPM ceiling caps it at ~3 posts/min). The verdict is very
# unlikely to change - interviews already break the tie.
# .venv/bin/python -m engine.audit

# 3. Audit: blind second-model check on a 150-post stratified sample (separate Qwen budget).
.venv/bin/python -m engine.audit

# 4. Rebuild the Space bundle from real data (removes the fixture banner), then run locally.
.venv/bin/python -m engine.export_space
cd space && set -a && . ../.env && set +a && ../.venv/bin/python app.py
```

Groq free tier: **200K tokens and 1K requests a day per model**. The local ledger (`data/interim/groq_usage.json`) caps each model at 190K per UTC day. Groq's own window is rolling, so the full allowance may take a few hours longer to return.

---

## Decisions made (and why)

- **THE 26 SEP PROBLEM LOCK IS REMOVED, AND THE VERDICTS ARE WRITTEN (Sep 21).** The lock existed to gate the MVP core-module choice on interviews. The MVP is built and deployed, recruitment never happened, and a gate whose input does not exist only stalls the deck. **What the lock was for still happened**, in `implementation_plan.md` §5: a stated verdict for every hypothesis — **H1 supported and the thesis · H2 supported, secondary · H3 refined, not the lead · H4 not tested · H5 weakly supported · H6 present but minor** — plus a locked problem statement the whole deck must argue. Dropping the gate without writing the verdicts would have reproduced the CS2 Clarity failure exactly: problem slides arguing one thing, solution slides building another, 14.35 points.
- **Stages 2 and 4 are cut, not held.** They serve `cannot_express` (1.4%) and `cannot_refine` (0.7%). **Put the cut and the numbers on the slide** — a scoped-out feature with a measured reason reads as judgement, an unexplained gap reads as omission.
- **Interviews come off the never-cut list.** Plan 2 §9 listed 5 interviews as never-cut; recruitment never happened. The deck now stands on 720 extracted episodes, a two-model audit on 203 pairs, and the survey. **Say that plainly in the limitations** rather than leaving a hole where primary research should be. What would reopen the verdicts: the survey returning heavy `cannot_refine`, or a real Hinglish signal on Q10.

- **THE MVP NOW FOLLOWS THREE USER-AUTHORED SPECS (Sep 21):** the flow wireframe, the design specification and the enhancement roadmap. State machine `compose → recap → moments → episode → confirmed` plus `empty`, all 12 instrumentation events, and the quiet-gallery visual system. **Two things are cut, with the number stated**, and the reason is the same each time: the clarifying question serves `cannot_express` at **1.4%**, and near-miss recovery plus the mismatch-reason prompt serve `cannot_refine` at **0.7%**. Everything else in all three specs is built.
- **Episode ranking changed from "best photo" to "usefulness" (roadmap §1.2, P0).** Episodes are ranked by coverage × coherence × recognizability × evidence quality, never shown as a score. **The weights inside it are judgement, not measurement** — 0.55 for an unnamed episode, the span thresholds, `0.4 + 0.15n` for recognizability. The 30-task eval scores *photo recall*, not *episode ordering*, so it cannot validate them. **Do not call episode ranking evidence-led on a slide.** Phase 5 is where it gets tested.
- **A no-op bug worth stating: rejections did nothing.** `episode_rejected` was instrumented and then ignored, so "Not this moment" returned the user to the identical list. Rejections are now session evidence and the UI says how many were ruled out. The wireframe listed "episodes already rejected" in its state model; the instrumentation existed before the behaviour did.
- **Three defects found by measuring the page, not looking at it (Sep 21).** At a 320px viewport the page had **470px of horizontal overflow** — grid items default to `min-width: auto`, so the horizontally scrolling clue and thumbnail rails widened the page instead of scrolling inside it. Clue-remove buttons were **28×28px** against the spec's 44px minimum. The privacy pill overflowed the top bar. All three are acceptance criteria in the design spec §11, and none was visible by eye at desktop width. **Check responsive acceptance criteria by measuring them.**
- **The search bottleneck is now representation, not filtering.** Per-cue on the 30 tasks: `temporal_approx` 0.062 → 0.688 and `exact_date` 0.000 → 1.000, but **`object` 0.250 → 0.250, `text_in_image` 0.000 → 0.000 and `place_named` 0.000 → 0.000 — where the *oracle* scores the same as the baseline.** Perfect knowledge of the answer's date, place and category retrieves nothing there, so no better clue extraction can help: the index cannot represent those cues. CLIP cannot read text inside an image, and `text_in_image` is the fourth most-retained real cue (12 of 144). **OCR or captions is the highest-value retrieval work left.** The second is making filters score rather than gate — a hard date filter on an approximate memory can exclude the right photo permanently, which recreates `not_surfaced` with our own mechanism.

- **LIBRARY GROWN TO 1,000, AND EVERY HEADLINE NUMBER RE-MEASURED (Sep 22).** Plan 2 specified 1,000 photos; 494 was the documented time cut. Removed two nude photos first (0221, 0458 — found by eye, missed by Openverse's mature filter), then appended **508 everyday photos** in 23 categories (sky, flowers, home food, tea, family, friends, pets at home, rain, commute, desk, gym, groceries, shopping, Holi, temples, cricket, notes, parking, sneakers, screenshots, books, parks) via `demo_library --grow-to 1000`, which appends only and dates the new photos as strays. Every new photo was screened by eye; 12 more were dropped (a shirtless-men collage, a political caricature, one uploader's feet-on-a-bed set — blocked by creator after it returned under new titles) and are blocklisted. The 30 tasks and the original 492 records **and vectors** are untouched (`demo_index --build --append`; verified bit-identical). **Shipped-encoder results: baseline 0.012, oracle 0.417, inferred 0.479 recall@20; hit@1 0 / 0.167 / 0.133.** Inferred still beats the oracle, and the narrow-window caveat weakens: ≤20-candidate windows are now 2 of 21 temporal tasks for *both* strategies (was 7 vs 3), median window 54 vs 95. The widest vague-year window is now 431 candidates. **Quote 0.479, not 0.612**; the 0.612 entries below are the 494-image record.
- **MEASURED THE MVP, AND IT OVERTURNED THE "ORACLE IS AN UPPER BOUND" CLAIM (Sep 21).** Scored a third strategy, `inferred` — the same rule-based extractor the deployed service runs, deriving filters from the query text alone, never from the answer. On the 30 evaluation tasks, measured with the encoder that actually ships: **baseline recall@20 0.053 · oracle 0.583 · inferred 0.612**. The inferred strategy **beats the oracle**, so **0.583 was never an upper bound** — `filters_for` is a **±45-day heuristic** handed the target's date, not an optimal clue-to-window policy. A month-precise reading of "July 2025ish" is both more faithful to the query and narrower (14 candidates vs the oracle's 46), and at k=20 narrower wins. **Stop calling 0.583 a ceiling on any slide.**
- **Three caveats that must travel with the 0.612.** (1) The tasks are **synthetic**, and the generator phrases vague time exactly three ways — `"July 2025ish"`, `"sometime in 2024"`, `"around summer 2024"`. The extractor was written knowing those forms and reusing `demo_tasks.SEASONS`' own month mapping, so 0.612 measures *that phrasing*, not real user language. (2) **recall@20 mechanically rewards narrow windows**: when a window holds ≤20 photos every answer is returned by construction, true for 7 of 21 temporal tasks for inferred vs 3 of 21 for the oracle. (3) The win is uneven — month precision wins big, but `"sometime in 2024"` and `"around winter 2024"` widen to a 222-photo window and lose. Real-language performance is what the interviews and Phase 5 testing measure; this number does not forecast it.
- **The first extractor scored 0.246.** It parsed none of the three vague-time forms: `\b` fails between "5" and "i" in `2025ish`, bare years had no pattern, and seasons were unhandled. Fixing those three gaps moved recall@20 from 0.246 to 0.612. Worth a line on the slide: the *most-retained real cue* (`temporal_approx`, 40 of 144 episodes) was the one the first implementation handled worst.
- **THE SHIPPED ENCODER IS fp16, AND EVERY NUMBER ABOVE IS MEASURED WITH IT (Sep 21).** Vercel caps a function bundle at **225 MB** — not the 5 GB the platform docs advertise for package size — and any single file at 100 MB. fp32 ONNX came to 302 MB in one 254 MB blob. So the encoder ships **fp16, sharded one file per tensor** (126 MB). fp16 was held to the same bar int8 failed: cosine vs fp32 **0.999999**, 28/30 identical top-20 sets, and **oracle recall@20 0.583 and hit@1 0.233 unchanged**. It does move the inferred score **0.646 (fp32) → 0.612 (fp16)**, which is why every figure is re-measured with the encoder that actually ships. Quoting the fp32 number would be quoting a build nobody can reach.
- **int8 quantization was tried and rejected (Sep 21).** 254 MB → 64 MB and cosine stays ≥0.979, but it **reorders results**: 0 of 30 tasks kept an identical top-20 set and hit@1 fell 0.233 → 0.200. **High cosine does not imply stable ranking** — CLIP scores cluster too tightly. This is why fp16 was verified against rankings and not just cosine.

- **Plan v2 thesis:** "Photos indexes items; people remember episodes." Five explanations (H1–H5) written down before any data; the engine compares them instead of confirming one.
- **Ask Photos facts corrected:** US rollout Oct 2024; paused Jun 2025 (latency, quality, UX); relaunched late Jun 2025 as a hybrid; toggle announced Mar 2026, fully rolled out Jul 2026. "Users rejected it" is too strong for the deck.
- **Groq only, open models, free tier, reduced volume.** Gate B labels a 1,200-post sample drawn in turn across (source, era) groups. The ≥400-episode checkpoint moves to about **Sep 22–23**. Fallback: Developer tier (about $1–3 total).
- **Gate B is binary on `gpt-oss-120b`.** In a 60-post trial, `gpt-oss-20b` called half its "episodes" wrongly; the two models agreed 88% on relevant/irrelevant. "Specific attempt vs. general complaint" moved into extraction (`specificity` field).
- **Audit model `qwen/qwen3.8-27b`.** `llama-3.3-70b-versatile` isn't available on this key. Qwen is a *preview* model; the fallback is `gpt-oss-20b`, flagged `same_family`.
- **H6 "learned path broken"** (an update moved folders, People & Pets or the layout people relied on) came out of the extraction trial. It's **post-hoc**; report it separately from H1–H5.
- **Era labels:** `pre_ask` (<Oct 2024) · `ask_launch` (Oct 2024–Jun 2025) · `hybrid` (Jun 2025–Mar 2026) · `toggle` (≥Mar 2026).
- **YouTube is a minor source** (about 20–30 real search attempts). Reddit and Play Store carry the volume.
- **Reddit through Apify** (Reddit no longer allows direct extraction); deferred until after the app stores.
- **≥400-episode gate is unreachable from app-store data (Sep 18) — Reddit added in response.** In the first 224 extracted posts (fed in Gate A *priority* order, so the most promising quarter) only 46 were `specific_attempt` (20.5%) and only **11 had a stated outcome** (4.9%). The rate falls monotonically across that slice — 28.6% / 23.2% / 19.6% / 10.7% by quartile — so the remaining 533 lower-priority posts will yield less, not the same. Full extraction projects to ~95–110 specific attempts and ~25–35 scoreable ones, against a gate of 400. **Reviews say "search is terrible", not "I looked for X, typed Y, got Z" — more tokens cannot fix that.** Decision: add Reddit (narrative source; it also pulls Play Store under the 60% cap). The pre-registered ranking rule in `analysis.py` is **not** changing.
- **Do not read the current hypothesis ranking as a finding.** H2 "leads" on a single episode (n_tagged=1, n_known=1); H4 and H5 are at zero. It is noise until the pool grows.
- **`evidence_verified` is 85.3%** (191/224) — about 1 in 7 extracted quotes is not verbatim in its source. The audit reports this; check it before any quote goes on a slide.
- **Extraction closed at 720 of 819 (Sep 20, deliberate).** The remaining 99 are the *lowest*-priority app-store posts by Gate A rank. Skipping them because: the specific-attempt rate has been flat at ~20% across all 720 with no decline, so they project to ~20 specific / ~8 scoreable; they would cost ~100K tokens and, at Sep 20's free-tier congestion (5–25 posts/hour), most of another day; and they would push Play Store's share of the extracted set *up* from 86.2%, worsening the source-cap breach. Per §3G the engine is one slide plus a link. **This is a stated scope decision, not an incomplete run** — say so in the deck funnel.
- **Play Store is 86.2% of extracted episodes** (621 of 720; appstore 36, reddit 62, youtube 1) against the plan's 60% cap. Reddit moved it from ~97% to 86%. Reaching 60% would need ~400 more relevant Reddit posts, beyond the $2.84 credit left. **Disclose the skew and its direction on the engine slide.**
- **Reddit did NOT fix the yield problem (Sep 20) — the source was never the cause.** Extracted all 62 relevant Reddit posts: **19.4% specific attempts, 9.7% scoreable (6 episodes)** — statistically identical to the app stores' 20.1% / 8.5%. Gate B relevance was actually *lower* on Reddit (46.6% vs Play Store 65.8%), because Gate A's keyword filter is less precise on long discursive comments. Across 720 extracted posts from four platforms the scoreable rate sits at **8.6%** and does not move. **People rarely narrate a complete retrieval attempt in public text anywhere.** Further collection cannot fix this; only interviews can.
- **What Reddit did buy** ($2.16): even era spread (hybrid 16 / ask_launch 20 / pre_ask 14 / toggle 12 vs Play Store's recency skew), deck-grade quotes, and source diversity against the 60% cap. Worth it, but for evidence quality and balance — not for yield.
- **Reddit collected and it is a far denser source (Sep 19).** 456 records from r/googlephotos → **134 Gate A candidates, a 29.4% pass rate vs Play Store's 6.1%** — five times denser per record collected. Era spread is also far better than the app stores: pre_ask 77 / ask_launch 119 / hybrid 122 / toggle 138, spanning 2016–2026. Cost **$2.16 of the $5 free credit**; $2.84 left.
- **Apify config: `searchCommunityName` is the field that matters.** Two trials were wasted ($0.24) before finding it. `startUrls` + `sort=new` crawls subreddit front pages (returned that morning's r/GooglePixel fingerprint posts); `ignoreStartUrls` searches ALL of Reddit (returned r/China, r/Entomology and automod boilerplate). Only `searchCommunityName` scopes a search to one community — and it takes **one community per run**, so a multi-subreddit sweep needs one run each. Actor: `trudax~reddit-scraper-lite`, ~$4/1K marginal with a ~$0.12 per-run floor.
- **Same connection bug, second place.** `collect_reddit.py` made bare `session.get/post` calls and died on a `RemoteDisconnected` mid-poll — stranding an Apify run that had already been paid for. Now wrapped in `_retrying` (the groq.py fix, Sep 18), plus a `--dataset <id>` flag to ingest an already-paid-for run's dataset without starting a new one. That flag is what recovered the 436 records. Suite is 74 tests.
- **Watch the Gate B sample cap.** `gate_a_candidates.jsonl` was regenerated (old one kept at `gate_a_candidates.pre_reddit.jsonl`). `select_sample` round-robins (source, era) strata, so re-running Gate B will now pull Reddit into the 1,200 sample — but 1,200 are already labelled, so the new Reddit items are *additional*, taking the labelled total above the pre-registered cap. Decide deliberately whether to raise the cap or keep 1,200, and say which in the deck.
- **Space bundle rebuilt from real data and its spend cap audited (Sep 20).** Bundle went from the 10-post fixture to **720 episodes** (playstore 621 / reddit 62 / appstore 36 / youtube 1) with 720×384 embeddings and the audit report; only the short evidence quote and a public URL ship — no full text, no author. Space tests pass.
- **The demo's token cap is per-container-life, not per day — and that is acceptable.** It is enforced through `data/interim/groq_usage.json`, and a Hugging Face Space filesystem is ephemeral: any rebuild or wake-from-sleep re-clones the repo and resets the counter. **The real protection is that `DEMO_MODEL` is `gpt-oss-20b`, which the pipeline does not use** — so the worst case is the demo losing live extraction for a while, never the pipeline losing budget. Documented in `space/app.py` rather than left as a surprise. Verified `gpt-oss-20b` at `max_tokens=4000` returns HTTP 200, so the Space does not hit the OTPM wall that broke the Qwen audit.
- **Fixed: the bundle was shipping a stale ledger** (Sep 17, 6,807 tokens). `export_space.py` now writes a clean one every rebuild.
- **MVP concept 'Memory Trails' reconciled with the evidence (Sep 20).** Three new files describe a concrete MVP. The concept is sound and its root cause is close to the data, but **the three failure modes it names are the three rarest observed**: `cannot_express` 1.4%, `cannot_refine` 0.7%, `cannot_evaluate_results` 1.4%. What dominates is `not_surfaced` **41.7%** and `system_misunderstood` **35.4%** — **77% of failures happen before the user needs to recover**. Consequence: build its stages 1 (clue chips) and 3 (visual trail); stages 2 and 4 address under 3%. Full analysis in `research/memory_trails_reconciliation.md`.
- **Where `failure_stage` and `hypotheses` disagree, trust `failure_stage`.** The audit measured `failure_stage` at κ 0.509 and `hypotheses` at Jaccard **0.347** (n=203) — the lowest of the three Jaccard-scored list fields (`cues_retained` 0.557, `cues_lost` 0.673). **The H3 lead comes from the least reliable field**; the 'recovery is rare' finding comes from one of the most reliable. This decided the verdict on 21 Sep: `failure_stage` wins, H3 is refined rather than supported as the lead. **State which field decided it and why (rule B)** — an audit overturning its own ranking scored well in CS1.
- **The MVP metric regressed and was caught.** The concept doc reverts to *session-level* success, which the Sep 18 correction already replaced with user-level **URR**. Left unfixed it would put a slide in direct contradiction with slide 2 — the CS2 Clarity failure in miniature.
- **The HTML prototype is scripted, and Part 5 requires functional.** A regex picks one of two hardcoded scenarios; thumbnails are CSS gradients. Good as an interaction mock, insufficient alone. Phase 1 built the missing half — point that interface at the real 494-image index and it qualifies.
- **Survey added (Sep 20, yours) and its import built.** A second form that *structures* the narration the engine could not find: ~100% of qualifying responses are scoreable vs the engine's 8.6%. Converts three **modelled** URR slots to **measured** (n̄, Expression, outcome distribution) — rule D, and Data & Metrics is the weakest competency at 27.08/40. `engine/import_survey.py` maps responses 1:1 onto the engine vocabulary so they pool with `episodes.jsonl`.
- **Three import decisions that must be repeated on the deck.** (1) **Q4 ≠ Q13** — first move (Expression) vs post-failure fallback; merging them destroys Q4. (2) Survey hypotheses are **rule-derived**, engine ones are model-assigned — `hypotheses_source` distinguishes them; **do not pool into one ranking**. (3) `era` is the *response* date, not the incident date — the survey never asks when it happened.
- **Two parser bugs caught by tests, both silent-data-loss class.** Google Forms joins checkbox selections with ", " and four option texts contain commas — a naive split shatters them. And `"English"` is a substring of `"A mix of Hindi and English, typed in English letters"`, so plain matching returned **both** values and the wrong one won — which would have silently destroyed the H4 signal. Fixed with longest-first matching plus a selection-boundary check.
- **PHASE 1 DONE (Sep 20): the MVP's case is now measured, not asserted.** Built the shared MVP base per `implementation_plan.md` §3. Same CLIP embeddings, same images, same queries — the *only* difference is turning a vague clue into a metadata window: **baseline recall@20 0.053 → oracle 0.583 (+0.530)**, hit@1 0.000 → 0.233. The baseline scores **0.052 on `temporal_approx`**, which the engine showed is the most-retained cue (40 of 144) — so the failure lands exactly where real memory is strongest. **This is the evidence chain for slide 8.**
- *(Sep 20 — SUPERSEDED 21 Sep: the inferred extractor scores 0.646, above the oracle, so (1) below is wrong. `filters_for` is a ±45-day heuristic, not a ceiling. Point (2) still stands.)* **Two caveats that must go on the slide with it.** (1) The oracle is an **upper bound, not the MVP** — it assumes flawless clue→window inference; the real module lands somewhere between 0.053 and 0.583, and quoting 0.583 as the MVP's score would be an overclaim. (2) The oracle stops at 0.583 because **some tasks are unanswerable in principle** — "the beach" aimed at one stray photo among 45 cannot be resolved by any system. That ceiling is honest, not a defect.
- **Evaluation design: cue mix is taken from the engine, not invented.** 83% single-cue tasks, dominated by vague time, because 79 of 97 cued episodes retained exactly one cue and 47 of 144 retained none. `who_with` and `own_label` are **excluded** — the synthetic library has no people or captions and scoring against them would be dishonest. A generator bug that silently drifted the mix toward easier multi-cue tasks was caught and fixed.
- **MVP decisions (Sep 20):** CLIP-only index (no Gemini dependency) and **494 images** (Plan 2 §9's documented cut from 1,000). CLIP is weak on text *inside* images — `whiteboard`/`document` scored 0.0 — so **captions are the first fix if Phase 5 testing shows those failing**.
- **AUDIT RE-RUN (Sep 20, n=203 incl. Reddit): the lead hypothesis now AGREES.** Primary top-2 moved from [H1, H2] to **[H3, H1]**; audit top-2 stays [H3, H6]. `lead_agrees` flipped **False → True** — both models independently put **H3 (dead end: zero/poor results, no idea what to try next)** first. Top-2 sets still differ (H1 vs H6 second), so the pre-registered rule still sends the tie-break to interviews — but "both models lead with H3" is a far stronger claim than the earlier "no overlap at all". Supersedes the Sep 19 entry below.
- **Agreement tracks how much the source actually says.** On `outcome`, the two models agree **0.659 (κ 0.272) on Reddit vs 0.384 (κ 0.132) on Play Store**; `hypotheses` Jaccard 0.386 vs 0.308. App-store reviews are too terse for *anyone* to judge what happened — the schema is not the problem. Play Store is 86% of the corpus, so it dominates the headline κ of 0.161. **This reframes the audit slide**: not "our models disagreed" but "agreement tracks source richness, which is why the engine cannot carry the ranking." Caveats: Reddit n=44; `specificity` κ runs the other way (0.316 vs 0.481) on near-identical raw agreement, so don't lean on that field.
- **AUDIT RESULT (Sep 19): the engine cannot rank the hypotheses.** 142 posts re-extracted blind by `qwen/qwen3.8-27b` (genuine `cross_family` independence). The top-2 sets do not overlap: primary says **H1, H2**, audit says **H3, H6**. The pre-registered rule therefore fires as written — *interviews break the tie*. Agreement on the fields the ranking depends on is too low to trust either result: `hypotheses` Jaccard **0.32**, `outcome` κ **0.132**. *(These are the n=142 values; superseded by the n=203 re-run — Jaccard 0.347, outcome κ 0.161. Do not quote this line as current.)* Per §3B of the lessons doc this is a **strength to state plainly**, not a failure to hide — CS1 scored well on an audit that overturned its own ranking.
- **The disagreement is systematic, not random.** The audit model infers liberally (reads "search is terrible" as `not_found`: 88 of 142, vs the primary's 119 `unknown`); the primary abstains. Every audit severity is exactly 1.0 for that reason. Same pattern on `hypotheses`: primary leaves 106/142 untagged, audit tags H3 66 and H6 45.
- **`query_language` is broken — do not put it on a slide.** The primary returned `en` for **all 142** posts; the audit returned `no_query` for 118. A constant is not a finding. **Consequence: H4 (Hinglish/code-mixed) is untestable from the current extraction** — it shows zero tags because a model that labels everything `en` cannot surface it. H4 was never tested, not overturned. Say that, or re-extract that field before claiming anything about H4.
- **What the engine can defensibly claim:** prevalence of **failure stages and cue types** — the moderate-agreement fields (`failure_stage` κ 0.503, `search_mode` κ 0.514, `specificity` κ 0.478, cues Jaccard 0.57–0.63). That maps to deck slide 5. Hypothesis ranking does not come from the engine.
- **Qwen has a 1,000 output-tokens-per-minute ceiling with no header** (measured Sep 19). Requests whose *expected* output exceeds it are rejected as "Request too large" and can never succeed — waiting does not help. `groq.py` now raises `RequestTooLarge` immediately instead of burning six retries; `audit.py` uses `MAX_TOKENS=800`, `DEFAULT_BATCH=1`, which caps the audit at ~3 posts/min (~1 hour for 150). Suite is 69 tests.
- **Groq client crash fixed (Sep 18).** `chat_json` retried 429 and 5xx but not *transport-level* failures, so a dropped keep-alive connection (`RemoteDisconnected`) killed a whole run mid-way — it escaped both `split_on_json_failure` and `main`. Now caught alongside `Timeout` with the same backoff (`engine/groq.py:85-97`), covered by 2 tests in `tests/test_gates.py`. Suite is 51 tests. This mattered most for extraction and audit, which run far longer than Gate B.
- **Never pipe a run through `tee`.** The shell reports the *last* pipeline command's status, so `tee`'s 0 masked a crashed Python run and it looked like a clean exit. Redirect with `>>` instead.
- **Metric fixed to user-level (Sep 18).** The brief (p.2) counts the *percentage of users*; SRR-V counted *searches*. Replaced by **URR** in Plan 2 §5: `URR = Expression × [1 − (1 − Interpretation × Surfacing × Recognition × Recovery)^n̄]`, where the unit underneath is a **retrieval task** (one target photo), not a query string. Consequences: the A/B randomises **by user**, not by session; baselines are explicitly *modelled*, not measured, with slots to fill after extraction + interviews. Closes §3D of `SCORECARDS_AND_LESSONS.md`.
- **Recruitment kit drafted (Sep 18)** in `research/recruitment.md` — post, screener, funnel maths. Not yet posted; needs a Form link and a call on compensation.
- **Space demo:** live extraction uses `gpt-oss-20b` with its own 60K daily cap, so visitors can't use up the pipeline's budget. Clues are matched on extracted structure plus embeddings, because text similarity alone links Hinglish to English only weakly (0.35). Only short quotes and links are shipped, never full text or author names.

## Risks to watch

1. **Interviews now carry the hypothesis decision outright** (audit overturned the ranking, Sep 19), and recruitment is **two days late and still unposted**. This is now the single biggest risk to the whole case study. Original risk text: too few specific attempts. The pre-registered rule scores explanations only on specific attempts with a stated outcome, which most reviews lack. Don't change the rule after seeing data. If counts are thin, add Reddit or let the interviews break the tie (the plan allows this).
2. **Play Store is 80.6% of the labelled sample** (967 of 1,200; App Store 202, YouTube 30) — now measured, not estimated. Over the plan's 60% per-source cap, and §4's Sep 21 gate requires no source above 60%. Either add Reddit or state the skew plainly in the deck. Era spread is healthier: pre_ask 357, toggle 300, ask_launch 274, hybrid 268.
3. **Qwen preview model** could be removed; the audit falls back and labels itself.
4. **Schedule:** recruitment is now a day late — the kit is drafted (`research/recruitment.md`) but **unposted**. It gates the Sep 26 problem lock, which gates the MVP core-module choice. Post it first thing.

## Waiting on you

- [x] **Groq key rotated (Sep 20).** New key verified: authenticates, all three pipeline models available, a real call through `engine.groq` succeeded and the ledger recorded it. Fingerprint changed `158d64c9c067` → `578aa42acd15`. **Unverified from here: that the old key was deleted** — the old value was not retained, so confirm console.groq.com/keys lists only the new one.
- [ ] **Replace the YouTube key** later: restrict it to YouTube Data API v3 and delete the old one.
- [ ] **Post the interview recruitment call** — draft ready in `research/recruitment.md`; needs a Google Form link, a compensation decision, and subreddit mod approval before posting.
- [ ] **Hugging Face:** create an account and a Gradio Space; add `GROQ_API_KEY` as a secret; then ask me to deploy `space/`.
- [ ] **Apify (now on the critical path):** create an account, put `APIFY_TOKEN` in `.env` yourself, and pick an actor id from apify.com/store (cheap ~$0.60/1K vs. best-rated ~$3.40/1K). Then run `.venv/bin/python -m engine.collect_reddit --actor <id> --limit 20` and read the output before any bulk run. The collector is built and tested; only the token and the actor id are missing.

---

## File map

| Path | What |
|---|---|
| `engine/common.py` | Shared record format, era tagging, JSONL helpers |
| `engine/collect_youtube.py` / `collect_appstore.py` / `collect_playstore.py` | Collectors (resumable, no author data) |
| `engine/gate_a.py` | Keyword filter + priority + funnel counts |
| `engine/groq.py` | Groq client: daily token ledger, 429 handling, invalid-JSON split-and-retry |
| `engine/gate_b.py` | Relevant/irrelevant screen, stratified 1,200 sample |
| `engine/extract.py` | Structured extraction, fixed vocabularies, exact-quote check (schema `v3-sep17`) |
| `engine/analysis.py` | Pre-registered ranking rule, kappa, overlap scores |
| `engine/audit.py` | Blind second-model audit + report + verdict |
| `engine/demo_library.py` | Fetches CC images from Openverse, assigns 25 life episodes |
| `engine/demo_index.py` | CLIP index; `baseline_search` vs `filtered_search` |
| `engine/demo_tasks.py` | 30 eval tasks, cue mix sampled from real engine episodes |
| `research/memory_trails_reconciliation.md` | MVP concept vs evidence; build order, metric fix, what's already built |
| `research/screener_form.gs` / `survey_form.gs` | Apps Scripts that create the two Google Forms |
| `engine/import_survey.py` | Survey CSV → episode records; vocabulary-locked to the engine |
| `engine/demo_eval.py` | Scores a strategy: recall@k and hit@1, broken down by cue |
| `engine/collect_reddit.py` | Reddit via an Apify actor; tolerant field mapping, resumable |
| `engine/export_space.py` | Builds `space/data` + copies engine modules into the Space |
| `space/app.py`, `space/demo_core.py` | Gradio demo (3 tabs) and its tested logic |
| `research/recruitment.md` | Interview recruitment post, screener, funnel maths |
| `data/raw/` | Collected posts (git-ignored) |
| `data/interim/` | Candidates, Gate B labels, trial files, token ledger, run logs |
| `.env` | `GROQ_API_KEY`, `YOUTUBE_API_KEY` (git-ignored; never commit) |

Trial files kept for the record (not pipeline inputs): `gate_b_trial_20b_3label.jsonl`, `episodes_trial_v1.jsonl`, `episodes_trial_v2.jsonl`, `data/raw/youtube_comments.unpruned.jsonl`.
