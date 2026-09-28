# Discovery Engine: Review Against the Brief + Fix Plan

**Reviewed on 23 Sep 2026:**
- The live site: https://retrieval-discovery-engine.vercel.app
- The web app: `engineapp/apps/web` (page, 5 components, `public/data/*.json`)
- The API: `engineapp/apps/extract`
- The pipeline: `engine/` (collectors, gates, `extract.py`, `analysis.py`, `audit.py`, `export_web.py`)
- The old Gradio Space logic: `space/demo_core.py`
- The data: `data/interim/episodes.jsonl` (720 episodes, 144 specific attempts) and `data/processed/audit_report.json`

**Brief requirement being tested:**
> Your discovery engine should help uncover questions like: What kinds of old photos do users struggle to retrieve? What information do people actually remember about a photo? What information have they forgotten? How do users formulate searches when their memory is incomplete?
> Your workflow should go beyond summarizing reviews or performing sentiment analysis. It should enable you to identify and compare different retrieval problems and opportunity areas using evidence from real users.

---

## 1. Verdict

**The pipeline meets the brief. The live site doesn't show it.**

The pipeline is strong:
- The unit of analysis is the retrieval episode, not the review.
- A fixed extraction schema, with the evidence quote checked against the source.
- Pre-registered hypotheses.
- A blind audit by a second model family.
- An era cut around the Ask Photos launch.

Against that, three things weaken the site:
1. The default tab shows invented numbers.
2. One sample question isn't answered anywhere on the site.
3. There is no view that compares opportunity areas.

| Requirement | Verdict | Evidence |
|---|---|---|
| Q1: kinds of old photos people struggle with | ⚠ Weak | `asset_type` is too coarse: photo 80/144 (55.6%), multiple 26, video 16, unknown 12, screenshot 7, document/receipt 3. The schema has no *subject* (people, pets, trips, documents) and no *photo age*. Only 15/144 texts mention the photo being old; 14 mention recent photos. |
| Q2: what people remember | ✅ Met | 14-value `cues_retained` vocabulary, crossed with failure stage and outcome. **Label bug:** the table is captioned "across all 144" but counts all 720 episodes. `temporal_approx` shows 79; among the 144 it is 40. It also hides that **47/144 attempts retain no cue at all**. |
| Q3: what they've forgotten | ✅ Met | `cues_lost` over the 144: date 37, album 29, exact_words 10, place 10, people 9, filename 6. These are **the brief's four unknowns, counted from real posts**, yet they aren't presented that way. |
| Q4: how people phrase searches with incomplete memory | ❌ Not surfaced | 32 `query_verbatim` values exist among the 144 but are **not exported** to the site. Finding: 20 of 32 are one word ("dog", "cake", "idea"), 9 are two words, and the only full sentences are 2 Ask Photos **successes** (tulips, Udaipur, both `found_fast`). |
| Beyond summaries or sentiment | ⚠ Undercut | The pipeline qualifies. The **default tab**, "AI Memory Diagnostic", doesn't: `MemoryDiagnostic.tsx` has 4 if/else branches that print **hardcoded "Baseline Search Failure Risk" figures** (88%, 77%, 69%, 24%). It calls the MVP's clue parser, which matches against the synthetic demo library's vocabulary. Live test: *"my grandmother's birthday in Pune a few years ago"* gives zero clues and "88% risk, cannot_express", though the memory has who, event, place and time. |
| Compare problems and opportunity areas | ⚠ Partial | Failure stages and cues are compared. The H1 to H6 ranking is **not supported by the audit**: hypothesis Jaccard 0.347, H1 κ −0.009, H5 κ −0.007, and H3 tagged 24 times by the primary model vs 93 by the audit model. README already says the ranking does not come from this engine. "Ended badly" uses `outcome`, where κ is 0.161 and 82/144 (57%) are unknown. |
| Evidence from real users | ✅ With caveats | Real public posts. **Skew:** Play Store supplies 123/144 specific attempts, Reddit 12, App Store 8, YouTube 1. **Brief fit:** only 45/144 have both a retained and a lost cue (the brief's population). 12 are `browse_path_changed` (an app update moved the path to photos), which is an app-design problem, not a memory one. Survey and interview data are not imported yet. |

**Smaller issues on the page:**
- "See the MVP it led to" links to **v1** (`memory-trails-demo`). It should point to v2.
- The stat "77.1% fails before search completes" is wrong. `not_surfaced` means the search *did* complete. The 144 also includes 14 attempts with stage `none`.
- The hero says "AI discovery platform". The diagnostic called "AI" is rule-based code.
- The extraction API uses the MVP's filter extractor (`clues.py`, `llm_clues.py`) plus the demo library's facets. That extractor isn't the discovery pipeline.

**What already exists and was dropped:** `space/demo_core.py` (the earlier Gradio Space) had the right design:
- `extract_memory()` runs **the pipeline's own extraction prompt** on a visitor's memory.
- `similar_episodes()` finds comparable real episodes.
- `cue_outcomes()` reports how posts with each cue fared.
- `by_era()` compares eras.

The fix is mostly porting this back, not inventing something new.

---

## 2. Fix plan

Priorities fit around the MVP fix plan: P0 on **Wed 24**, P1 on **Thu 25**, P2 only if the MVP work is on schedule.

| # | Fix | Priority | Effort |
|---|---|---|---|
| D1 | Replace the default tab with a real-evidence diagnostic | P0 | 3 to 4 h |
| D2 | Correct the labels and links | P0 | 30 min |
| D3 | A "Findings" tab that answers the four questions, as the default | P0 | 2 h |
| D4 | A "How people search" panel | P1 | 1 h |
| D5 | An opportunity comparison table and a partial-memory toggle | P1 | 2 h |
| D6 | Add `subject` and `photo_age` fields (pass + audit sample) | P2 | 3 h |
| D7 | Import survey responses as a second source | P2 | when data arrives |

---

### D1: Replace "AI Memory Diagnostic" with a real-evidence diagnostic (P0)

**Remove:**
- The four hardcoded risk branches and every percentage not computed from data.
- The copy about "standard Google Photos search" behaviour, which is not verified.

**New flow:** "Compare your memory with real people's attempts"
1. The visitor describes a photo they can't find.
2. **Extract with the pipeline's own schema**, not the MVP's filter parser. Use `engine.extract.SYSTEM`, `format_batch` and `parse_results`, which is exactly what `space/demo_core.extract_memory()` does. It returns `asset_type`, `cues_retained`, `cues_lost` and `query_verbatim`.
3. **Match a cohort from the 144 by structure** (no encoder needed on Vercel). Rank by Jaccard on `cues_retained`, plus 0.2 if `asset_type` matches and is specific. Keep attempts with at least one shared cue.
4. **Show the cohort's evidence with its n:**

   > **You remember:** approximate time · people · event
   > **You've lost:** exact date · album
   > **12 real attempts remembered the same kind of thing.**
   > Where they broke: not surfaced 7 · misunderstood 4 · none 1
   > Outcome: not found 5 · found slowly 1 · **unknown 6** (outcomes are often not stated; κ 0.16 between models)
   > 3 quotes, each with source, date and era

5. Show counts below 5 as "too few (n = 3)". That rule is already in `demo_core.pct` via `MIN_N`.
6. **Fallback when Groq is unavailable:** a keyword map to cue types, labelled "rule-based". Never show fabricated figures.

**API** (`engineapp/apps/extract/main.py`):
```python
EPISODES = [json.loads(l) for l in (DATA / "episodes_specific.jsonl").open()]   # 144, public fields only

@app.post("/diagnose")
def diagnose(body: ExtractIn):
    memory = body.text.strip()
    client = groq_client()
    try:
        q = extract_memory(client, memory) if client else rules_profile(memory)   # engine.extract schema
        source = "pipeline_prompt" if client else "rules"
    except Exception:
        q, source = rules_profile(memory), "rules"
    cohort = cohort_for(q, EPISODES)             # Jaccard on cues_retained (+0.2 same specific asset_type)
    return {"profile": {k: q.get(k) for k in ("asset_type", "cues_retained", "cues_lost", "query_verbatim")},
            "source": source,
            "cohort": summarise(cohort),             # n, stage counts, outcome counts incl. unknown
            "quotes": [pick(e) for e in cohort[:3]]}  # evidence, source, date, era
```
- Set `os.environ.setdefault("GROQ_LEDGER", "/tmp/groq_usage.json")` before building the client. Vercel's filesystem is read-only, which is the same failure found in the MVP.

**Export** (`engine/export_web.py → export_engine_app`):
- Copy `engine/extract.py` and `engine/analysis.py` (plus what they import) into `engineapp/apps/extract/engine/`.
- Write `episodes_specific.jsonl` with public fields only: no author data, which already holds.
- **Stop copying** `clues.py`, `facets.py` and `llm_clues.py`, and stop writing the demo-library facets into the engine API. The engine should not know the MVP's photo library.

**Presets:** replace the MVP-library examples ("A beach cafe in Goa…", "Puppy's first vet checkup in Bengaluru") with paraphrases of real episode types:
- "a receipt I photographed sometime last year"
- "the photo of my parking spot"
- "a picture of my kid with a cake a few birthdays ago"
- "that screenshot with some text I need"

---

### D2: Correct labels and links (P0)

| Where | Now | Change to |
|---|---|---|
| `export_web.build_evidence` | `"cues": core.cue_table(episodes)` (all 720) | `core.cue_table(specific)`. Optionally add a secondary "all 720 relevant posts" column |
| Cue table caption | "across all 144 verified retrieval attempts" | Correct once the table uses the specific 144. Add the row "no cue retained: 47" |
| Stat card | "77.1% Fails Before Search Completes" | "77.1% of attempts break at interpretation or surfacing" (111/144), or quote failures only: 111/130 = 85.4% |
| Hero | "An AI discovery platform…" | "A discovery pipeline: 85,140 public posts → 720 structured episodes → 144 specific attempts, audited by a second model family" |
| `page.tsx` `MVP_URL` | `https://memory-trails-demo.vercel.app` | `https://memory-trails-v2.vercel.app` |
| Tab name | "AI Memory Diagnostic" | "Compare your memory" (after D1) |

Keep the **one value per number** rule: every figure on the page must match the deck and README.

---

### D3: A "Findings" tab, as the default (P0)

Four panels, one per sample question, each with a headline, a table or bar, and two quotes. All counts come from the 144.

**1. What people remember**
- Headline: *"Approximate time is the most-kept cue (40/144); a third keep nothing searchable (47/144)."*
- Table: `cues_retained` counts, plus "none".

**2. What they've forgotten: the brief's four unknowns**
- One bar per unknown: when (date 37), album (29), where (place 10), exact words (10). Add people (9) and filename (6).
- Headline: *"Date and album are lost most. Exact words and place are lost less often, but 'text in image' fails most when kept (5 of 8 known outcomes not found)."*

**3. What kinds of photos**
- After D6: `subject` × `photo_age`.
- Before D6: show `asset_type` honestly, noting that "photo" dominates and the schema can't say more yet. Report that documents/receipts are only 3/144 *in public posts*. That argues against the "filing cabinet" segment hypothesis unless interviews say otherwise. Record it; don't hide it.

**4. How people search**
- Headline and table from D4.

Add a **"Brief population only" toggle** (the 45 attempts with a retained *and* a lost cue) that re-filters all four panels.

---

### D4: "How people search when memory is incomplete" (P1)

**Export** (`build_evidence`):
```python
verbatims = [{"query": e["query_verbatim"], "words": len(e["query_verbatim"].split()),
              "search_mode": e["search_mode"], "era": e["era"], "stage": e["failure_stage"],
              "outcome": e["outcome"], "source": e["source"]}
             for e in specific if e.get("query_verbatim")]
evidence["verbatims"] = verbatims
evidence["query_length"] = Counter(min(v["words"], 5) for v in verbatims)   # 1,2,3,4,5+
```

**Show:**
- A length histogram: **1 word: 20 · 2 words: 9 · 11+ words: 3** (n = 32).
- The list of verbatims with mode, era and stage.

**Headline:** *"In classic search, people reduce a rich memory to one noun ('dog', 'cake', 'restaurant'). Full sentences appear only with Ask Photos, and those were successes."*
- That supports the MVP thesis: the gap is between what people remember and the one word they type.

**Caveats to show:**
- n = 32. Only 22% of the 144 quote their query.
- `query_language` shows κ 0.002 in the audit, so no language claim (H4 Hinglish = 0/144).

**Knock-on for the MVP:** the "tulips" and "Udaipur" verbatims are **successes**. They're fine as phrasing patterns, but don't describe them as failed queries anywhere.

---

### D5: Opportunity comparison table (P1)

Build only from fields the two models **agreed on**: `failure_stage` (κ 0.509) and `cues_retained` (Jaccard 0.557). Areas overlap (one attempt can keep several cues), so rows don't sum to 144.

**Computed 23 Sep from `data/interim/episodes.jsonl`** (regenerate in `build_evidence`):

| Opportunity area | Attempts (of 144) | In brief population (of 45) | Not found / known outcomes | Top failure stage | Pre vs post Ask Photos | Brief fit | MVP addresses |
|---|---:|---:|---:|---|---:|---|---|
| **O1 Vague time** (approx time or event anchor) | **42** | **21** | 7/15 | not_surfaced (20) | 8 / 34 | ✅ core | ✅ vague time, ribbon, soft dates |
| O2 Text inside the photo | 12 | 3 | 5/8 | system_misunderstood (8) | 1 / 11 | ✅ (exact words) | ❌ roadmap: OCR |
| O3 Object or thing | 17 | 3 | 6/11 | system_misunderstood (11) | 6 / 11 | ✅ (words) | ◐ CLIP + synonyms |
| O4 People (who with) | 10 | 5 | 2/5 | system_misunderstood (3) | 2 / 8 | ✅ | ❌ no people data |
| O5 Own label or caption | 7 | 5 | too few (n = 2) | system_misunderstood (4) | 1 / 6 | ◐ | ❌ |
| O6 Place | 7 | 3 | 3/5 | not_surfaced (4) | 3 / 4 | ✅ | ✅ place anchors, soft place |
| O7 Exact date | 14 | 8 | 7/8 | system_misunderstood (7) | 5 / 9 | ❌ precise description | frozen |
| O8 No cue at all | 47 | 0 | 14/15 | not_surfaced (26) | 13 / 34 | ◐ can't express | ◐ anchors, ribbon (browse) |
| O9 Path changed by an app update | 12 | 1 | — | browse_path_changed (12) | 2 / 10 | ❌ app design | ❌ out of scope |

**Reading it:**
- **O1 is the largest area that fits the brief:** 42 attempts, and **21 of the 45** remember-something-forgot-something attempts. That is the evidence link to the MVP.
- **O2 is the sharpest gap:** it fails most when present, and the MVP can't address it. That's the roadmap slide (OCR and captions), consistent with the MVP's oracle-zero result on `text_in_image`.
- **O8 is large but unaddressable by query features.** Browse-first entry (anchors, ribbon) is the only lever; say so.
- **O7 and O9 are explicitly outside the brief.** Showing that you excluded them is a strength.
- **Era cut:** 106 of 144 attempts are post-Ask Photos, but only 38 pre-Ask. That's not a rate comparison without volume per era, so present the counts, not a trend.

**Columns to add in code:** `n`, `n_partial`, `not_found/known`, `top_stage`, `pre/post`, `example_ids[3]`.
- "Brief fit" and "MVP addresses" are **judgement columns**. Label them as such in the UI.
- Replace the H1 to H6 ranking on the page with this table. Keep the ranking in the Audit tab as *"pre-registered, not supported by the audit"*. That honesty scores better than a ranking you can't defend.

---

### D6: Add `subject` and `photo_age` fields (P2)

This makes Q1 answerable.

- Add to `engine/extract.py VOCAB`, and re-run on the **144 specific attempts only** (about 20 batches on the Groq budget; not the 720):
  ```python
  "subject": ["people_family", "pets", "trip_or_event", "document_or_text", "screenshot",
              "object_or_product", "food", "place_or_scenery", "unknown"],
  "photo_age": ["days_or_weeks", "months", "one_to_three_years", "over_three_years", "unknown"],
  ```
- Bump `SCHEMA_VERSION` to `v4-sep26`.
- Keep v3 fields untouched: this only adds fields.
- Audit **40 stratified** attempts with the second model. Report κ for both fields. If κ < 0.4, show the counts with that warning.
- Then Findings panel 3 becomes a `subject` × `photo_age` table, and Q1 gets a real answer about *old* photos.

---

### D7: Import survey responses as a second source (P2)

`engine/import_survey.py` already maps survey CSV rows to episode records with the same vocabulary. When responses arrive:
- Add `source: "survey"` to the funnel.
- Add a source filter on every panel.

The survey asks directly what people remember and forget, so it is the least skewed evidence for Q2 and Q3. It also offsets Play Store's 85% share.

---

## 3. Caveats to show on the engine and the deck

- **Source skew:** Play Store supplies 123/144 specific attempts. Reviews are complaints; help-seeking forums are thin (Reddit 12).
- **Outcome is weak:** 57% unknown, κ 0.161. Every "ended badly" figure shows its known-outcome n.
- **Hypotheses:** audit agreement near zero for H1 and H5, so the ranking is not a finding.
- **Extraction agreement** (the fields the comparison uses): failure stage κ 0.509; cues retained Jaccard 0.557; cues lost Jaccard 0.673.
- **Evidence quotes checked against the source:** 85.2% (primary), 97.0% (audit).

---

## 4. Acceptance checks (live, incognito)

1. The site opens on **Findings**. All four sample questions are answered with counts from the 144 and two quotes each.
2. **"Compare your memory"**:
   - *"my grandmother's birthday in Pune a few years ago"* returns cues retained `who_with, event_anchor, place_named, temporal_approx` (not "no clues"), a cohort n, and quotes. No figure appears that wasn't computed from data.
   - *"the parking spot photo"* returns a cohort with n shown, or "too few", never a made-up risk.
3. The cue table's `temporal_approx` reads **40** (of 144), matching the deck and README.
4. "How people search" shows 32 verbatims and the 20 / 9 / 3 length split.
5. The opportunity table matches §2 D5 (or the regenerated values), with judgement columns labelled.
6. The MVP link opens **memory-trails-v2**.
7. `/health` shows no demo-library vocabulary. The engine API no longer ships `library.jsonl`.

---

## 5. Deck slide 3 ("How the discovery engine works")

- **Pipeline:** 85,140 posts → 5,305 keyword filter → 1,333 model-screened → 819 relevant → 720 episodes → 144 specific → **45 partial-memory attempts** (the brief's population).
- **Why it is more than sentiment:** the unit is a retrieval episode. For each one it records what was remembered, what was lost, the typed query, where retrieval broke, and the outcome. A second model family audits it, and opportunity areas are compared only on the fields the two models agree on.
- **One visual:** the D5 table, trimmed to O1, O2, O3, O8 and O9.
- **Link:** the engine, opening on Findings.
