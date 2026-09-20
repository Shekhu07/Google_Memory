# Google Photos Case Study: Re-plan (v2)

## Context
The v1 plan (`Google_Photos_Case_Study_Plan_1.md`) picked its answer, a question-asking "recovery agent" that runs after a failed search, before any research. It also rested on an unchecked claim that users rejected Ask Photos. You asked for a fresh plan and a new set of ideas. v2 does three things:
1. corrects the Ask Photos facts;
2. widens the set of ideas;
3. makes the discovery engine choose between competing explanations instead of confirming one.

Deadline: 7 Oct 2026, 3:59 PM IST. Personal done-date: 5 Oct.

---

## 1. Checked facts: correct the story before it goes on a slide
| v1 said | Checked |
|---|---|
| Rollout began Sep 2024 | US rollout began **Oct 2024** |
| Paused in summer 2025 over latency | **Jun 2025** pause over **latency, quality and UX**. The Photos PM said "at very small numbers". It resumed **late Jun 2025** as a hybrid: fast classic results appear first, with Gemini working in the background. |
| Mar 2026: Google "gave in", users "rejected it" | Toggle **announced Mar 2026, fully rolled out Jul 2026**. It **switches back to Ask Photos automatically** when a query looks complex. |

**What changes:** "users rejected conversational search" is too strong. Graders who check it will mark it down. The accurate reading:

> Google spent two years fixing **how queries get routed and how fast results come back** (a classic/AI hybrid, then a toggle). Neither mode gives the index what it lacks: **when something happened in the user's life, who was there, and which episode a photo belongs to.** Neither mode helps the user **recognise** the target among hundreds of similar results.

This still separates your MVP from Ask Photos, and it no longer depends on overstating a backlash.

Sources: [TechCrunch, Jun 2025](https://techcrunch.com/2025/06/04/google-delays-rollout-of-its-ask-photos-ai-search-feature/) · [PetaPixel, resume](https://petapixel.com/2025/06/27/google-resumes-rollout-of-ai-based-ask-photos-image-search/) · [9to5Google, Mar 2026](https://9to5google.com/2026/03/10/google-photos-ask-search-toggle/) · [9to5Google, Jul 2026](https://9to5google.com/2026/07/20/google-photos-classic-search-toggle/)

---

## 2. The idea set
Each idea stands for a **different theory of why retrieval fails even though the user remembers something**. The deck has to name one root cause, and each idea implies a different one.

| # | Idea | Root cause it assumes | Decomposition term |
|---|---|---|---|
| 1 | **Life-event timeline resolver.** "When I was sick", "around Diwali", "before we moved" become a date window. It uses signals already in the library: photo bursts, location gaps, receipts/medicine clusters, festival calendar. | Memory holds time *relative to life events*; the index only understands calendar dates | Interpretation |
| 2 | **Anchor-hop.** Find a photo you *can* find (the Goa beach), then browse outward from it with duplicates collapsed | Memory is a chain of associations; search treats each photo in isolation | Expression → Surfacing |
| 3 | **Episode cards.** Results are grouped into labelled moments ("Goa · Dec 2023 · 3 cafés") instead of a grid of 400 thumbnails | The target *is* in the results but can't be recognised | Recognition |
| 4 | **Context at capture for utility photos.** When a receipt, medicine strip or document is photographed, attach the episode around it | These photos are born with no faces, landmark or name, so there's nothing to search for later | Surfacing (upstream) |
| 5 | **"Where did I save it" across apps.** One vague query covers Photos, WhatsApp media, Drive and a partner's library | The photo was never in this library | out of scope for Photos? |
| 6 | **Refine by pointing.** Tap a result and say "earlier", "same place, different day" or "this person, indoors" | Refining is a blind retry of typing | Recovery |
| 7 | **Recovery agent (v1).** Up to 3 questions after a failed search | Dead end with no explanation | Recovery |
| 8 | **Hinglish / code-mixed queries** *(new)*. "dawai wali photo", "parchi", transliterated names and places | Indian users remember and type in mixed language; the query is misunderstood | Interpretation |
| 9 | **Negative and contrast clues** *(new)*. "Not the one with mom", "the other café", "before the rain" | Search can't take exclusions or comparisons | Interpretation |

**Screened out:** 5 (the business case says keep things in Photos, but the scope is huge and it's mostly an integration problem, not intelligence) and 7 as the *lead* idea (it looks most like Ask Photos, and a reviewer's first question will be "isn't this Ask Photos?").

**Front-runner going into research:** one thesis, **"Photos indexes items; people remember episodes."** It combines 1 + 3, with 2 as the way to browse. Intelligence sits in exactly two places:
- (a) turning an episodic clue into a date window;
- (b) splitting the library into episodes and labelling them.

Everything else (ranking inside the window, grouping, browsing from an anchor) is rules and metadata. That answers "where is intelligence actually needed" precisely.

**Challengers kept alive:** 6 (Recovery), 8 (Hinglish), 4 (capture). The engine decides.

---

## 3. Pre-registration: competing hypotheses (write these down Sep 17–18)
- **H1 Episodic time:** failures cluster where the only surviving clue is a relative time or event.
- **H2 Recognition:** the user reached a plausible result set but couldn't pick the target out ("scrolled through hundreds").
- **H3 Dead end:** zero or poor results, and the user had no idea what to try next.
- **H4 Language:** the query was code-mixed or transliterated and was misread.
- **H5 Nothing to index:** utility photos with no searchable attributes.

**Added after the pre-registration (Sep 17, from the 10-post extraction trial). Report it as post-hoc, not as a pre-registered hypothesis:**
- **H6 Learned path broken:** people reached photos through a route they had learned (folders, People & Pets, albums, timeline layout, a search that used to work), and an app update moved or removed it. Example: "can't find my people & pets folders… today was his birthday & I wanted to make a post with his pictures". It has its own failure stage, `browse_path_changed`.

Decision rule, set before seeing data: the lead hypothesis is the one with the highest **(share of episodes) × (share that ended not_found or found_slow)**, provided the audit model agrees on the top 2. If the audit disagrees, the interviews break the tie. Record the outcome on Sep 22, whatever it is. That record becomes a slide.

---

## 4. Part 1: Discovery engine (redesigned to compare hypotheses)
**Unit of analysis:** a *retrieval episode*: one attempt to find one specific photo.

**Sources, most to least load-bearing:**
1. Reddit **via an Apify scraper** (Reddit no longer allows direct extraction): r/googlephotos, r/GooglePixel, r/android, r/iphone, r/india. **Deferred (decided Sep 17): build after Play Store / App Store.** Open decision: which scraper to use, cheapest (about $0.60 per 1,000 items; about $4–8 for 1,500 posts + 5,000 comments) or the best-rated (about $3.40 per 1,000). Test 20 items before any bulk run; token stored as `APIFY_TOKEN` in `.env`.
2. YouTube comments on Ask Photos coverage and "find old photos" how-to videos (API)
3. Play Store / App Store reviews after Oct 2024, for how common each problem is
4. Quora, and Google Photos Community read lightly (its terms of service may restrict scraping; don't depend on it)

**Models (decided Sep 17: Groq only, open models).** Checked against console.groq.com/docs/models on Sep 17; production models only, since preview models can disappear at short notice.

| Stage | Model | Why |
|---|---|---|
| Gate A: keyword filter | none (regex) | Free; broad; ~7% of collected posts pass |
| Gate B: relevant / irrelevant | `openai/gpt-oss-120b` | **Changed Sep 17 after a 60-post trial.** `gpt-oss-20b` over-labelled "episode" (about half wrong, e.g. "can't find the magic eraser"). The two models agreed 88% on relevant/irrelevant but only 67% on the three-way split, so Gate B is binary. |
| Extraction (+ `specificity`: specific_attempt / general_complaint) | `openai/gpt-oss-120b` | Strongest production model on Groq; decides the episode-vs-complaint question with full context |
| Second-model audit | `qwen/qwen3.8-27b` | A different model family, so the audit really is independent. Preview model; fallback is `openai/gpt-oss-20b` with a different prompt, noted on the slide. (`llama-3.3-70b-versatile` isn't available on this key.) |

**Free tier (decided Sep 17: stay free, cut volume).** Limits are 200K tokens and 1K requests a day *per model*, and Gate B and extraction share `gpt-oss-120b`'s budget. So Gate B labels only a **1,200-candidate sample**, drawn round-robin across (source, era) groups so older eras and small sources are represented. Expect the ≥400-episode checkpoint around **Sep 22–23** instead of Sep 21. The Developer tier (about $1–3 for the whole pipeline) is the fallback if the schedule slips further.

Key: `GROQ_API_KEY` in a git-ignored `.env`. Watch the free-tier rate limits; keep the stages resumable so the run can pause and continue.

**YouTube result (Sep 17 run):** 28 searches, 2,913 quota units, 3,624 comments. A title filter requiring a photo-library mention cut this to 696 comments from 24 videos; a keyword check suggests only about 20–30 describe a real search attempt. **YouTube is a minor source.** The ≥400-episode gate depends on Reddit and Play Store reviews. Record this yield in the deck funnel.

**Pipeline:** collect → cheap keyword/embedding filter → model filter ("a specific attempt to find a specific past photo?") → extraction → hypothesis tagging → second-model audit on a stratified sample → comparison view.

**Extraction schema (v1 fields, plus):**
- `asset_type`, `cues_retained[]`, `cues_lost[]`, `query_verbatim`, `failure_stage`, `workaround`, `outcome`, `confidence` + evidence span
- `era`: pre_ask (<Oct 2024) · ask_launch (Oct 2024–Jun 2025) · hybrid (Jun 2025–Mar 2026) · toggle (≥Mar 2026)
- `query_language`: en · hinglish/code-mixed · other
- `reached_candidates`: bool (separates H2 from H3)
- `hypotheses_supported[]`: H1–H5 with a reason

**Public demo (Hugging Face Space):**
- Tab 1: paste a vague memory → see the extraction plus the most similar real episodes.
- Tab 2: **comparison matrix** of hypotheses × prevalence × failure severity × era. This is the "compare retrieval problems" view the brief asks for.

**Gate, Sep 21:** at least 400 gated episodes, and no single source above 60% of the total. Record the yield at each stage as a deck funnel.

---

## 5. Part 2: Metric decomposition

**The brief's goal, in its own words (p.2):** *"Increase the **percentage of users** who successfully
retrieve a photo they remember but cannot precisely describe when they start searching."*

v1 and the first draft of v2 decomposed **SRR-V**, a share of *searches*. The brief counts *users*.
Corrected here (v2.1). The goal metric is now user-level; the search-level chain sits underneath it
as the mechanism, and the bridge between the two levels is written down rather than assumed.

**Unit correction:** the working unit is a **retrieval task** — one target photo the user is trying
to get back to — not one query string. A task contains however many queries the user types at that
target; that is what reformulation *is*. Counting queries as if each were an independent trial was
the level error, and it double-counts exactly the users who struggle most.

### 5.1 The goal metric

**URR (Unblocked Retrieval Rate)** = of users who had at least one vague-intent retrieval task in a
28-day window, the share who reached the photo they were after on at least one of them.

The denominator is users with the **need**, not users who searched. That is deliberate: a user who
gives up before typing is a failure of this metric, and restricting to searchers would hide them.
The need is only partly observable, so the measurable proxy is: started a vague-intent search **or**
showed the scroll-hunt signature (sustained undirected scrolling in library regions more than ~6
months old, no search issued). **The proxy's own coverage is a number to report, not to bury.**

### 5.2 The decomposition

**URR = Expression × [ 1 − (1 − Interpretation × Surfacing × Recognition × Recovery)^n̄ ]**

where **n̄** = average vague-intent retrieval tasks per user in the window.

| Level | Term | The question it answers | Fails when | Hypothesis |
|---|---|---|---|---|
| User | **Expression** | Of users with a vague memory to chase, how many start a search at all? | Blank box; doesn't believe search can take what they remember; defaults to scrolling | H6 |
| Task | **Interpretation** | Does Photos map the clues onto something it indexes? | Event-relative, relational, negative or code-mixed clues unsupported | H1, H4 |
| Task | **Surfacing** | Is the target anywhere in the returned set? | Ranking buries it; the asset has no indexed attribute | H5 |
| Task | **Recognition** | Can the user pick it out of what came back? | Dense grids, near-duplicate bursts | H2 |
| Task | **Recovery** | After a miss, does the next attempt beat a blind retry? | No signal on *why* nothing matched | H3 |

**Reading the bracket.** A user succeeds if **any** of their tasks succeeds, so the user-level rate
runs ahead of the task-level rate, and the gap widens with n̄. Two consequences worth a sentence on
the slide each:

1. **Heavy users mask the problem.** At task-success 0.50, a user with one task sits at 0.50 and a
   user with five sits at 0.97. A user-level metric reported without n̄ will look healthy while
   single-task users — the ones with the weakest memory cues — fail most of the time.
2. **Task-level lift compounds.** Moving task success 0.50 → 0.60 moves a 2-task user from 0.75 to
   0.84. This is why the search-level chain is still the right place to intervene even though the
   goal is user-level.

**Independence caveat:** the bracket assumes a user's tasks succeed or fail independently. They do
not — a user whose clue vocabulary is unsupported fails correlated. So the bracket is an **upper
bound** on URR given a task-success rate; state it as such and report the task-level rate beside it.

### 5.3 Where the opportunity sits

Expression and the Interpretation of plain queries are where Google has already spent — Ask Photos,
then the hybrid, then the toggle. **Episodic Interpretation and Recognition remain open.** That is
the claim the engine either supports or overturns; it is not yet a finding.

### 5.4 Metric specification (per §3D of the lessons doc)

| | |
|---|---|
| **Primary** | URR, 28-day window, vague-intent tasks |
| **Baseline** | **MODELLED, not measured** — no access to Google telemetry. Derived from engine task outcomes + the 6 interviews. Slot: `URR₀ = __`, `task-success₀ = __`, `n̄ = __`. Fill after extraction and interviews; label every one of them "modelled" on the slide. |
| **Target** | Slot: `+__ pp URR`, stated as an absolute lift with its task-level equivalent beside it |
| **Experiment** | **Randomise by user, not by search** — this follows directly from the metric being user-level, and it is the change the old plan's session-level A/B got wrong. Exposure-qualified population = users meeting the 5.1 proxy. |
| **Sizing** | **1,531 qualified users per arm** for a 5pp absolute lift on a 55% base (80% power, α=0.05 two-sided); round to **1,600** for dropout. Recompute once the baseline slot is filled. |
| **Leading** | Episode-card click-through · tasks-to-find · abandon-after-one-query rate |
| **Diagnostic** | Resolution by clue type · date-window accuracy · recognition time · **n̄ distribution** (guards against consequence 1 above) |
| **Guardrails** | No regression in success or latency on normal searches (the Ask Photos lesson) · no rise in wrong-photo confirmations · no drop in the scroll-hunt proxy's coverage |

**If a search-level number must be quoted** (it is the more familiar unit), quote it as
**task-success**, name the denominator, and show the bracket that maps it to URR. Never quote a
per-query rate — that is the unit the brief does not count.

---

## 6. Part 3: Research (6 interviews, target 5 usable, Sep 22–26)
**Screener:**
- Google Photos 2+ years
- 5,000+ items
- a search for an old photo that failed or took too long in the last 3 months
- at least 3 of 6 who use Hindi/English mixing day to day (tests H4)

**Protocol (40 min):**
1. **Critical incident** (12 min): what you were looking for, what you remembered, the exact query typed, what came back, what you did next.
2. **Tasks run alone in their own library** (10 min, camera off): (a) a utility photo from over a year ago; (b) a photo dated only by a life event. They report queries, time, whether they got to candidates, and the outcome. Nobody sees their photos.
3. **Timeline probe** (8 min): "When roughly was that?" Record *how* they place it in time (event, season, relative, calendar). This tests H1 directly.
4. **Recognition probe** (5 min): did they scroll past it? How many results before giving up? Tests H2.
5. **Toggle** (5 min): Ask Photos or classic, and why?

Recruitment is the slowest step. Post the call on Sep 17.

---

## 7. Part 5: MVP (modular so the research can pick the core)
**Shared base, built during the research week whatever the result:**
- A demo library of 1,000 CC-licensed images, deliberately including hard cases (receipts, medicine, whiteboards, cafés, trips, bursts of near-duplicates), with synthetic metadata (date, location, device) forming about 25 believable life episodes (a trip, an illness week, a move, a festival, a wedding).
- An index built from SigLIP/CLIP embeddings + Gemini 2.5 Flash captions + metadata filters.
- A plain semantic-search baseline.
- An evaluation set of 30 tasks, written from engine episodes, each with the correct answer known.

**Core module, chosen Sep 26:**
- **H1/H2 wins → episode-first retrieval:** turn clues into a date window + episode cards + browse from an anchor.
- **H3 wins → refine-by-pointing** (idea 6), with a recovery question as fallback.
- **H4 wins → a code-mixed query rewriter** placed before the shared index.

**Latency:** zero added cost on searches that already work. The intelligence runs only on vague-intent searches or failures, and the MVP measures that.

**Evaluation report:** success rate, steps to find, recall@20 against the baseline, false-confirmation rate, added latency.

**Guardrails:** never claim "this is your photo"; always show alternatives; if something breaks, fall back to a plain grid.

**Honesty:** label it as a representative demo library, not a Google Photos integration. Never use participants' photos.

---

## 8. Parts 6–8: Testing, metrics, risks
- **Testing:** 3–5 target users on tasks taken from their own critical incidents. Test → fix the top 2 issues → re-test lightly.
- **Metrics:**
  - Primary: **URR** (user-level, §5.1) on vague-intent retrieval tasks. Task-success is reported
    beside it as the mechanism, never on its own.
  - Leading: episode-card click-through, steps to find, abandon-after-one-query rate.
  - Diagnostic: resolution by clue type, accuracy of the date window, recognition time.
  - Guardrails: no regression in success or latency on normal searches; no rise in wrong-photo confirmations.
- **Risks:**
  - "Isn't this Ask Photos?" Answer on the slide: this fixes a different broken step.
  - The date window is wrong: show confidence, let the user widen it.
  - Episodes split wrongly: let the user merge or split them.
  - Privacy of life-event inference (illness): process on-device, allow opt-out of sensitive categories.
  - Users never discover the feature: trigger it on vague-intent queries.

---

## 9. Schedule
| Dates | Work | Gate |
|---|---|---|
| Sep 17–18 | Pre-register H1–H5; freeze the schema; set up source APIs; post the recruitment call; start curating the library | Schema + hypotheses written |
| Sep 19–21 | Run the engine; hand-check 100 extractions | **Sep 21:** ≥400 episodes |
| Sep 22 | Audit + comparison matrix; deploy the engine | **Engine link live**; hypothesis ranking recorded |
| Sep 22–26 | Interviews; evenings: shared MVP base + baseline + evaluation tasks | **Sep 26:** problem locked + core module chosen |
| Sep 27–Oct 1 | Build core module + UI; run evaluation; deploy | **Oct 1:** MVP live |
| Oct 1–3 | User testing, fix, re-test | Findings written |
| Oct 3–5 | 10-slide deck + QA | **Oct 5:** ready to submit |
| Oct 6 | Buffer; check the brief line by line; submit | Submitted |

**Cut in this order if behind:** H4/H5 sources → evaluation tasks 30→15 → library 1,000→500 → re-test round.
**Never cut:** audit, 5 interviews, both public links, the evidence-chain slide.

## 10. Deck (10 slides)
1. Metric + thesis ("Photos indexes items; people remember episodes")
2. URR decomposition: which steps Google already invested in, which are open (user-level metric; task-level chain underneath)
3. How the discovery engine works + link
4. Comparison of hypotheses: what the evidence supported and what it overturned
5. What people remember vs. what they lose, with failure rate by clue type
6. Interviews: exact queries, workarounds, where searches die
7. Evidence chain → segment + root cause + problem statement
8. MVP: where the intelligence sits, and why it isn't Ask Photos
9. Evaluation + user testing: what broke, what's next
10. Metrics + risks

**QA:** no name anywhere, including PDF metadata · titles state the message · colour-blind-safe palette · ≥14pt · <40 MB · `NL_GooglePhotos` · every link opened in incognito.

## Verification of this plan
- The facts in §1 are backed by the linked sources.
- Every Part 1–8 requirement and deck item from the brief maps to a section above.
- Implementation starts only after you approve this plan.
