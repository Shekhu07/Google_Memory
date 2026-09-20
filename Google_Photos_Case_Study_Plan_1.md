# Google Photos Retrieval — Graduation Project Execution Plan
**NextLeap PM Fellowship, Sep 2026 cohort · Submission: Tue 7 Oct 2026, 3:59 PM IST · Personal done-date: Sun 5 Oct**

*(The brief shows both "Oct 7, 4:00:00 PM" and "3:59:00 PM IST". Treat 3:59 PM as the wall — same discrepancy as Case Study 2. Don't relitigate it, just finish early.)*

---

## 1. What is actually being graded

The brief is unusually explicit about how you lose marks:

- **"The challenge is not to improve search in general."** Any slide that reads as "better search" fails the framing test.
- **"DO NOT frame the problem simply as: Users find it difficult to search for old photos."** The graded question is *why retrieval fails **despite** the user retaining some memory of the photo.*
- **"Your workflow should go beyond summarizing reviews or performing sentiment analysis."** A theme-counter on Play Store reviews scores low. The engine must let you **compare distinct retrieval problems against each other**.
- **"Your research should determine where intelligence is actually needed in the retrieval journey."** Locate the AI; don't sprinkle it.
- The evidence chain is named for you: **Business Metric → Product Outcomes → AI-Powered Discovery → Observed User Behavior → Problem Definition.** Build one slide that *is* that chain.

**Three hard deliverables:** (1) a testable link to the discovery engine, (2) a 10-slide PDF, (3) a publicly accessible deployed MVP another person can use.

---

## 2. The fact that reshapes this whole case study

**Google already shipped conversational retrieval, and users rejected it.**

- Sep 2024 — Ask Photos (Gemini-powered conversational search) begins US rollout.
- Summer 2025 — rollout **paused over latency**.
- Jun 2025 — Google merges classic search with AI results to speed things up.
- Through 2025–26 — sustained complaints: slower, *less* accurate, and regressions on things classic search did well. One widely-quoted example: text-in-photo search, which worked by typing a word, now routed through Gemini and failing.
- **Mar 2026 — Google gave in and put a toggle on the search screen** to switch back to classic search, saying users wanted "more control over the type of results."

This kills the obvious answer. Any deck that proposes "make Google Photos search conversational" is proposing the thing that was just rolled back. **Handled well, this is the strongest argument in your deck**, because it converts a competitive threat into evidence:

> Conversation as a *replacement* for search has already been tried and rejected — it taxed the 95% of searches that were working. The unsolved moment is not query entry. It is the **dead end**: the user who searched, got nothing usable, and has no idea what to try next.

That reframes your opportunity from **Expression** (Google's bet, and it backfired) to **Recovery** — intelligence that fires *only on failure*, costing nothing in latency on healthy searches. It also answers "where is intelligence actually needed" with evidence rather than taste.

It also solves your biggest corpus risk: the Ask Photos backlash is recent, loud, dated and public. There is a natural before/after cut in the corpus, and a toggle event in Mar 2026 you can anchor on.

**Treat §2 as a hypothesis with a pre-registration, not a conclusion.** Write it down on Day 1, and on Sep 26 record explicitly whether the evidence supported it, refined it, or overturned it. That record is a slide. (On Myntra, the audit overturning your own ranking became a strength — same move.)

---

## 3. The spine (lock Day 1, revise only with evidence, freeze Sep 26)

> Human memory of a photo is **episodic and associative** — who was there, what else happened that day, which trip, roughly when. Google Photos' index is **object-, face-, place- and text-centric**, and the interface takes **one shot** at a single string. When that shot misses, the user gets no signal about *why*, no way to hand over the partial cues they still hold, and no path forward except scrolling.

**Working segment hypothesis:** long-tenure, high-volume users who use the camera as a **filing cabinet** — documents, receipts, medicine strips, whiteboards, parking spots, screenshots. The only surviving cue is episodic ("when I was sick last year"), and the asset has no face, no landmark, no trip name to grab. The brief's own second example is exactly this. Sharper than "people with lots of photos", and structurally under-served by a face/place-centric index.

---

## 4. Part 1 — The discovery engine (rebuilt fresh)

**Design principle: the unit of analysis is a *retrieval episode*, not a review.** One comment may yield zero or two episodes. That is what makes it more than sentiment analysis.

**Source priority — invert the obvious order.** Star ratings are dominated by storage, pricing and backup noise. The highest-signal public sources are **help-seeking posts**, because the person describes the cues they still hold:

1. Google Photos Community / support threads ("I'm trying to find a photo of…")
2. r/googlephotos, r/GooglePixel, r/android, r/iphone help and complaint posts
3. Quora questions about finding old photos
4. YouTube comments under "how to find old photos in Google Photos" and Ask Photos coverage
5. **Ask Photos backlash threads and post-Sep-2024 app reviews** — dense, dated, and directly about retrieval failure
6. Play Store + App Store reviews at volume — use for prevalence, not insight

**Pipeline:**

| Stage | What it does |
|---|---|
| Ingest | Multi-source collector, normalised schema (source, date, text, url, lang) |
| Gate A (cheap) | Keyword/embedding prefilter for retrieval-relevance |
| Gate B (model) | "Does this describe a specific attempt to find a specific past photo?" — yes/no + reason |
| Episode extraction | Structured JSON per episode (schema below) |
| Taxonomy build | Cluster retained-cue types and failure stages |
| Audit | **Second model, different prompt, re-scores a stratified sample and re-ranks the opportunity areas.** Non-negotiable |
| Probe | Replay real vague queries against a real library and record outcomes |

**Episode extraction schema** — this is the asset. Get it right before scraping anything.

```
asset_type        photo | screenshot | document/receipt | video | medicine/label | other
cues_retained     [temporal_approx, season/event_anchor, place_named, place_unnamed,
                   who_with, activity, object, appearance/colour, device/app_source,
                   emotional, sequence ("right before X")]
cues_lost         [date, place, album, people, exact_words]
query_attempted   verbatim if available
failure_stage     cannot_express | system_misunderstood | not_surfaced |
                  cannot_evaluate_results | cannot_refine | abandoned
workaround        date-scroll | ask_a_friend | other_app (WhatsApp/Drive) | gave_up | found_slowly
era               pre_ask_photos | post_ask_photos   ← enables the before/after cut
outcome           found_fast | found_slow | not_found
confidence        model's own 0-1 + evidence span
```

**The Retrieval Probe** — your "beyond summarisation" proof and the bridge into Part 3. Take the vague memory descriptions users actually wrote, re-express them as queries, run them against a real Google Photos library (yours, plus participants running their own probes privately in Part 3), and record: found / not found, rank position, reformulations needed. You end up with a **measured failure rate by cue type** instead of an anecdote pile. That table will carry the deck.

**Deployment:** public Hugging Face Space (Streamlit/Gradio) with a demo box where a grader pastes a vague memory and sees the extraction plus comparable evidence. One deck slide explains how it works — required.

**Corpus-sufficiency gate, Sep 21:** if gated episodes < ~400, or one failure stage holds >70% purely from source skew, add sources before continuing. Record the yield numbers — 15,820 → 4,740 → 1,094 was deck material on Blinkit; the same funnel works here.

---

## 5. Part 2 — Metric decomposition

**Business metric (SRR-V):** share of search sessions that begin with an incomplete memory and end with the user reaching the intended photo.

**SRR-V = Expression × Interpretation × Surfacing × Recognition × Recovery**

| Term | User behaviour | Fails when | Measurable proxy |
|---|---|---|---|
| **Expression** | Turns a fuzzy memory into a query at all | Blank box; doesn't know what's searchable; defaults to scrolling | Search-entry rate on vague-intent sessions; scroll-first rate |
| **Interpretation** | System maps the cues onto index dimensions | Relational ("with mum"), event-relative ("around Diwali"), negative and sequence cues unsupported | Zero/near-zero result rate by cue type |
| **Surfacing** | Target is in the returned set | Ranking buries it; asset has no indexed attributes | recall@k on probe tasks |
| **Recognition** | User identifies it among results | Dense grids, near-duplicate bursts, thumbnails too small to judge | Time-to-first-open; open-then-back rate |
| **Recovery** | Refines productively after a miss | No signal on *why* nothing matched; reformulation is a blind retry | Reformulations per session; abandon-after-one rate |

Name the weakest terms and say why the others are already owned. Current read: **Surfacing gets all the engineering attention and is probably not your opportunity. Expression is where Google just spent two years and retreated. Recovery is unowned.** Saying that out loud reads as judgement, which is what a graduation deck is scored on.

---

## 6. Part 3 — Primary research (privacy-safe, as chosen)

**n = 6 interviews** (target 6 to land 5 usable), 40–45 min, plus an optional 20–30 response survey for cue-frequency ranking.

**Screener:** Google Photos 2+ years · 5,000+ items · abandoned a search for an old photo in the last 3 months.

**Protocol:**
1. **Critical-incident recall** (15 min) — one *specific* recent failure. What were you looking for, what did you still remember, what did you type, what came back, what did you do next. Capture **verbatim query strings**; they go on a slide.
2. **Self-run retrieval tasks** (offline, 10 min, camera off) — two assigned tasks: (a) a document/receipt/label photographed over a year ago, (b) an event datable only approximately. They run it alone in their own library and report queries tried, time, outcome. No private photos are ever seen. Doubles as probe data for Part 1.
3. **Cue elicitation** (10 min) — for a photo they never found, what do they still know? Score against the cue taxonomy.
4. **One question earning its keep:** have they seen the Ask Photos / classic search toggle, and which do they use? Their answer is worth a slide either way.

**Recruit from Day 1.** Recruitment is the long pole on every one of these projects; a slipped slate is what compresses the MVP window.

---

## 7. Parts 4–5 — Problem definition and the MVP

**Problem statement shape** (fill from evidence, lock Sep 26):
> For [long-tenure camera-as-filing-cabinet users], re-finding [a utility photo whose only surviving cues are episodic] fails because [the index is object/face/place-centric while memory is episodic, and a failed search is a dead end with no diagnosis and no way to hand over partial cues], so they [date-scroll for minutes, ask a friend, or re-acquire the document].

The brief demands seven explicit items in Part 4. Two are easy to drop — don't:

- **Why it creates user value:** the assets in this segment are consequential — a prescription, an insurance document, a warranty, a receipt. Failure has a real-world cost, not a nostalgia cost.
- **Why it makes business sense for Google Photos:** retrieval success is the load-bearing reason to keep a decade of photos in one place rather than spread across device, WhatsApp and Drive. It underwrites storage-subscription retention, it is the differentiator against Apple Photos, and after the Ask Photos retreat, Google needs an AI win in this surface that users keep switched on. Put a number shape on it even if the number is illustrative, and label it as illustrative.

**MVP — a recovery agent, not a chat replacement for search.** It does not intercept the query box. It fires when a search dead-ends (zero/weak results, a reformulation, or a scroll-away), and then: tells the user *what it did and didn't understand*, asks up to three questions chosen to best split the candidate set, and returns an evaluable contact sheet grouped by day/place that accepts cue-level feedback ("not this, but that trip is right") instead of blind re-typing.

Build spec:

- **Library:** 800–1,500 CC-licensed images (Unsplash/Openverse/Flickr CC), deliberately seeded with the hard cases — screenshots, receipts, medicine strips, whiteboards, cafés, trips, pets, near-duplicate bursts — plus synthetic EXIF (date, geo, device). **Never use a participant's real photos.** Start curating this in the research week; it does not depend on the problem lock.
- **Index:** image embeddings (CLIP/SigLIP) + VLM attribute captions (Gemini 2.5 Flash) + metadata filters.
- **Intelligence, located deliberately:** rules choose *which* question to ask (information gain over the candidate set); the model only does language understanding and phrasing. Same integrity split as BlinkIQ — put it on the slide, it directly answers "where is intelligence actually needed".
- **Latency is a first-class requirement, not a footnote.** Ask Photos was paused over latency and users called it laggy. Budget it, measure it, and show that the recovery path costs zero milliseconds on searches that succeed.
- **Guardrails:** max 3 questions, all skippable, best candidates visible throughout, confidence gate, never assert "this is your photo", fail-open to a plain grid.
- **Eval harness (your differentiator):** 30–40 ground-truthed vague-memory tasks over the seeded library. Report **success rate, turns-to-find, recall@20 agent vs. plain semantic search, false-confirmation rate.** This is the evaluation-first framing your portfolio already runs on.
- **Deploy:** public HF Space. Label the corpus clearly as a representative demo library, not a Google Photos integration — the same honesty move as the SYNTHETIC labels in BlinkIQ.

**Part 6 — testing:** 3–5 users (at least 3 from the target segment) on tasks lifted from real failures in Part 3. Two rounds if time: test → fix the top two issues → light re-test. Document what you'd change next.

---

## 8. Parts 7–8 — Success metrics and risks

**Primary:** SRR-V on vague-intent sessions.
**Leading:** recovery-path trigger rate · first-question answer rate · median turns-to-find · abandon-after-one-query rate.
**Diagnostic:** resolution rate by cue type · candidate-set reduction per turn · false-confirmation rate · per-question skip rate · added latency on the failure path.
**Guardrails:** zero regression in standard search success **and** in standard search latency (the Ask Photos lesson), no rise in wrong-photo confirmations, no dialogue retention.
**Experiment:** session-level A/B on vague-intent-classified sessions, power-sized, with a kill date set in advance — the Myntra pattern reviewers responded to.

**Risk register:**

| Risk | Mitigation |
|---|---|
| "This is just Ask Photos again" — the first question a reviewer asks | Answer it on the slide: fires only on failure, zero latency cost on healthy search, diagnoses rather than replaces |
| Photo genuinely lacks indexable attributes — no dialogue can find it | Degrade to time/place scaffolding; state the ceiling honestly |
| Agent confirms the wrong photo → trust collapse | Confidence gate, always show alternatives, never assert |
| Dialogue fatigue — users won't answer three questions | Cap at 3, skippable, candidates visible throughout |
| Creepiness — an agent questioning you about your life, over medical and document photos | On-device framing, no logging, sensitive-category handling |
| Cost/latency of VLM captioning at Google scale | Precomputed embeddings; dialogue runs only over candidate sets |
| Can't identify vague-intent sessions for measurement | Explicit trigger + session classifier, reported with its own accuracy |
| Nobody discovers the mode | Trigger on dead ends, not a menu entry |

---

## 9. Twenty-one day schedule

| Days | Dates | Work | Gate |
|---|---|---|---|
| 1–2 | Sep 16–17 | Lock spine + pre-register the §2 hypothesis. Extraction schema, cue/failure taxonomies. Repo + Space skeleton. **Post recruitment call.** | Schema frozen |
| 3–6 | Sep 18–21 | Build and run the engine: ingest → gates → extraction. Hand-QA 100 extractions. | **Sep 21: ≥400 gated episodes or add sources** |
| 6–7 | Sep 21–22 | Second-model audit + opportunity ranking. Deploy engine Space. | Public link live — deliverable #1 done early |
| 7–11 | Sep 22–26 | 6 interviews + self-run tasks + survey. Synthesise. Finalise decomposition. **In parallel (evenings): curate the seeded library.** | **Sep 26: problem statement locked — no changes after** |
| 11–16 | Sep 26–Oct 1 | Build MVP: index, dialogue agent, UI, eval harness. Deploy public. | **Oct 1: MVP live and eval run** |
| 16–18 | Oct 1–3 | User testing (3–5), fix top two issues, light re-test. | Findings documented |
| 18–20 | Oct 3–5 | Deck, metric framework, risks. Full QA pass. | **Oct 5: submission-ready** |
| 21 | Oct 6 | Buffer only. Re-read the brief against the deck, line by line. Submit. | Submitted |

Oct 7 is the wall, not the plan.

**Descope ladder** — if you slip, cut in this order and nothing else: survey → eval harness 40 tasks to 20 → information-gain question selection replaced by a fixed 3-question script → seeded library 1,500 to 600 images → second round of user testing. **Never cut:** the second-model audit, the 5 interviews, the public MVP link, the evidence-chain slide.

---

## 10. Deck plan (10 slides, no separate title slide)

1. The metric, the thesis, and why this is not "better search"
2. SRR-V decomposed into five terms — where the loss sits and which terms are already owned
3. How the discovery engine works *(required)* + link
4. What people remember vs. what they lose — cue taxonomy with measured failure rate by cue type
5. Observed retrieval tasks: verbatim queries, workarounds, where sessions die
6. Target segment + root cause
7. The evidence chain: Metric → Outcomes → Discovery → Behaviour → Problem
8. Solution rationale + MVP, including where intelligence sits and why this is not Ask Photos
9. User testing: what happened, what broke, what changes next
10. Success metrics + risks and mitigations

Slides 9 and 10 are the squeeze. If risks need room, fold testing evidence into slide 8.

**Submission QA checklist:** name absent everywhere **including PDF metadata and file properties** · ≤10 slides · every slide title states a message, not a label · colour-blind-safe palette · ≥14pt throughout · <40 MB · filename `NL_GooglePhotos` · **every link opened in an incognito window to prove access** · engine and MVP both live at 3 PM on submission day · the phrase "users find it difficult to search for old photos" appears nowhere.

---

## 11. Review log — what changed after checking this plan against reality

1. **Found the Ask Photos history and rebuilt the plan around it.** The first draft proposed a conversational retrieval agent without knowing Google shipped one, paused it over latency, and added an opt-out toggle in Mar 2026. That draft would have been shredded in review. The MVP is now a *recovery* agent that fires only on failure, and the backlash became the argument rather than the threat.
2. **Filled a hard gap: "why it makes business sense for Google Photos."** Part 4 requires it explicitly and the first draft omitted it.
3. **Moved seeded-library curation into the research week.** It is half a day of grunt work that doesn't depend on the problem lock, and it was sitting inside the tightest phase.
4. **Added a pre-registration step.** The plan commits to an MVP direction before the research runs, which risks anchoring. Writing the hypothesis down on Day 1 and recording on Sep 26 whether evidence supported it turns that risk into a credibility asset.
5. **Promoted latency to a first-class MVP requirement** — the specific thing that killed the incumbent feature.
6. **Added an `era` field to the extraction schema** so the corpus supports a pre/post-Ask-Photos cut.

**Still risky, by my read, and worth your judgement:**

- **The MVP window is the binding constraint.** Sep 26 → Oct 1 for index + dialogue agent + UI + eval harness is roughly 28 working hours. It fits only if the library is already curated and the eval tasks are written during the research week. If the interview slate slips by two days, this is what breaks — go to the descope ladder immediately rather than compressing testing.
- **Scraping the Google Photos community forum may be ToS-restricted.** Have Reddit and YouTube (both proper APIs) as the load-bearing sources so the engine doesn't depend on the risky one.
- **The probe is n=1 on your own library unless participants run their own.** Decide this in week one, not week three — it changes the interview script.
