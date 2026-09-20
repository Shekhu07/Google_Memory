# Design — Public deployment on Vercel

**Date:** 20 Sep 2026 · **Status:** approved in chat, pending spec review
**Supersedes:** the Hugging Face Space deployment path (`space/`, `engine/export_space.py`)
**Feeds:** `implementation_plan.md` §6 (Phase 4) and §7 (Phase 5)

---

## 1. Why this exists

Plan 2 §9 lists two public links as *never cut*. The engine demo was built for a Gradio Space; the
MVP prototype is a static HTML mock. Neither is deployed. The user has a Vercel account and no
Hugging Face account, so both surfaces move to one Vercel project.

**The binding constraint, and the reason the backend is Python.** The deck will carry
`recall@20 0.053 → 0.583`. Those numbers come from `engine/demo_index.py` and `engine/demo_eval.py`.
Reimplementing filtering or ranking in TypeScript risks the live demo disagreeing with the deck —
the CS2 Clarity failure, reproduced in code. Reusing the tested Python makes them identical by
construction.

---

## 2. Scope

**In scope now (hypothesis-independent, safe to build before the 26 Sep lock):**
- Vercel project with two services, routing, and deploy
- The Python retrieval service and its three endpoints
- Clue extraction (LLM + deterministic fallback) and the offline eval that scores it
- The evidence surface (3 tabs), served from precomputed JSON
- The MVP surface: stages 1 (editable clue chips) and 3 (visual episodes)
- Attribution page, baseline toggle, build-time export pipeline

**Out of scope until the 26 Sep problem lock:**
- Stage 2 (one high-value follow-up) — addresses `cannot_express`, 1.4%
- Stage 4 (steer / "not this, but nearby") — addresses `cannot_refine`, 0.7%

Both are built **only if** interviews overturn `failure_stage` and vindicate H3. See §12.

**Never in scope:** user accounts, uploads, any real Google Photos data, persistence of
visitor-typed text.

---

## 3. Architecture

One Vercel project, two services, deployed atomically (skew protection between front end and API).

```
webapp/
  vercel.json
  apps/
    web/                     Next.js · App Router · TypeScript
      app/
        page.tsx             MVP — Memory Trails
        evidence/page.tsx    Evidence — 3 tabs
        attribution/page.tsx CC credits
      components/  lib/
      public/
        library/             494 images (27 MB, CDN)
        data/evidence/       precomputed JSON
    retrieval/               Python · FastAPI
      main.py
      engine/                copied in by the export script
      data/                  vectors, library, episodes, ONNX encoders
      requirements.txt
```

**Public routing** — ordered, specific first; routing into a service is final:

| Source | Destination |
|---|---|
| `/api/py/(.*)` | `retrieval` |
| `/(.*)` | `web` |

Next.js keeps the rest of `/api`. The retrieval service receives the full path, so it carries a
service-scoped rewrite `/api/py/:path(.*)?` → `/:path`.

---

## 4. The filter contract — the interface everything turns on

`engine/demo_index.apply_filters` accepts exactly five optional keys. **All supplied filters must
match.**

```python
apply_filters(records, date_from="", date_to="", location="", category="", episode="")
```

| Key | Match rule | Cue that produces it |
|---|---|---|
| `date_from` / `date_to` | inclusive window on `record.date` | `exact_date` → both = that day · `temporal_approx` → ±`VAGUE_WINDOW_DAYS` (**45**) |
| `location` | case-insensitive substring | `place_named` |
| `category` | exact equality | `object` |
| `episode` | case-insensitive substring | `event_anchor` |

**The oracle vs the MVP — state this plainly on the slide.** `demo_eval.filters_for(task, target)`
reads the *answer record* to build this dict. That is why 0.583 is an upper bound, not a product.
The MVP must produce the same five keys **from the user's text alone**. That inference is the only
genuinely new retrieval logic in this build.

---

## 5. Python service API

All responses are JSON. All errors are typed, never a stack trace.

### `POST /api/py/extract`
```jsonc
// request
{ "text": "that small café we went to during our Goa trip" }
// response
{
  "filters":   { "location": "Goa", "category": "food" },
  "chips":     [ { "id": "c1", "cue": "place_named", "label": "Goa",         "filter_key": "location", "value": "Goa",  "editable": true },
                 { "id": "c2", "cue": "object",      "label": "café / food", "filter_key": "category", "value": "food", "editable": true } ],
  "source":    "llm",          // or "rules"
  "notice":    null            // set when the fallback fired
}
```

Chips are the UI projection of `filters`; **every chip maps to exactly one filter key**, so removing
a chip deletes that key and re-running search is trivially correct.

**`label` and `value` are different fields and must not be collapsed.** `label` is display text
("café / food"); `value` is what reaches `apply_filters`. This matters because `category` is matched
by **exact equality** against the library's 12 category values, while `location` and `episode` are
substring matches. A chip whose label reached the filter would silently return nothing.

### `POST /api/py/search`
```jsonc
// request
{ "text": "...", "filters": { "location": "Goa" }, "mode": "trails" }  // or "baseline"
// response
{
  "episodes": [ { "episode_id": "ep07", "episode": "goa trip", "location": "Goa",
                  "date_from": "2023-12-14", "date_to": "2023-12-18", "count": 18,
                  "why": ["location matched \"Goa\"", "12 of 18 photos fall in the date window"],
                  "photos": [ { "id": "demo:0231", "file": "library/0231.jpg", "score": 0.31 } ] } ],
  "total": 24, "mode": "trails", "filters_applied": { "location": "Goa" }
}
```

**Filters are client-authoritative after chip edits** — the server does not re-derive them from
`text`, because the user may have corrected what the extractor got wrong, which is the entire point
of stage 1. The server validates that keys are within the five allowed names and that dates parse;
anything else is rejected with a typed error. `text` is still sent because it is what gets
CLIP-encoded for ranking.

`mode: "baseline"` ignores `filters` and calls `baseline_search` — this powers the toggle that lets a
grader *watch* 0.053 become 0.583 rather than read it.

**Why-strings are evidence labels only** — which filter fired, on what value. Never a generated
rationale. v2's risk table is explicit that overclaiming here costs more trust than a miss.

### `GET /api/py/health`
Returns encoder load state, vector counts, manifest build date, and whether a Groq key is present.
Used to warm cold starts before demos.

---

## 6. Clue extraction

**Primary — LLM.** A dedicated query-extraction prompt (not `extract.SYSTEM`, which analyses
*posts*, not queries) returning the five filter keys plus the cue that produced each. Model and cap
per the existing `GroqClient` ledger; `DEMO_MODEL` stays off the pipeline's models.

**Fallback — deterministic rules.** Same output shape, `source: "rules"`. Month/year/relative-time
patterns → date window; the library's known `location` and `episode` values matched as substrings;
`category` via a keyword map over the 12 categories. Always available, never rate-limited, and it is
what makes the offline eval reproducible.

**Fallback fires on:** budget reached, 429, timeout, transport failure, unparseable JSON after
`split_on_json_failure`. The UI shows one honest line; results still appear.

---

## 7. Front-end surfaces

**`/` — Memory Trails (MVP).** Prompt → chips (stage 1, `system_misunderstood` 35.4%) → visual
episodes (stage 3, `not_surfaced` 41.7%). Chips are editable and removable; editing re-runs search.
Results group by `episode_id`, never a flat grid. Each card carries **"why this episode is here"**.
Baseline ⇄ Trails toggle on the results header.

**`/evidence` — the engine.** Three tabs, ported from `space/app.py`: *Try a memory* (live, calls
`/extract`), *Compare retrieval problems* (static JSON), *How it works* (funnel, audit,
limitations). Tabs 2 and 3 make **no** function calls.

**`/attribution`** — every image with creator, licence and source URL. Non-negotiable: the library is
CC and several licences require credit.

**v2 vocabulary throughout:** "why this episode is here" (not "why this matches"), "visual episodes"
(not "result clusters"), "memory re-entry" (not "search mode").

---

## 8. Build-time vs request-time

`engine/export_web.py` (new, modelled on `export_space.py`) runs **locally** and its output is
committed:

- 494 images: `data/demo/images/NNNN.jpg` → `apps/web/public/library/NNNN.jpg`. The export rewrites
  each record's `file` field to the published path, so the API returns `library/NNNN.jpg` and the
  front end needs no path logic.
- evidence tables → `apps/web/public/data/evidence/*.json`
- `library.jsonl`, `image_vectors.npy` (494×512 CLIP) → `apps/retrieval/data/`
- `episodes.jsonl`, `episode_vectors.npy` (720×384 MiniLM) → `apps/retrieval/data/`
- both ONNX text encoders + tokenizers → `apps/retrieval/data/`
- `manifest.json` — model ids, dims, counts, build date

**Vercel's build installs only `fastapi`, `numpy`, `onnxruntime`.** No torch, no model downloads, no
Groq calls at build time. Every heavy step stays on the machine where it already works.

**Encoders:** CLIP ViT-B/32 **text tower only** (~65 MB quantized) for photo search; multilingual
MiniLM text encoder (~120 MB quantized) for episode matching on `/evidence`. Image and episode
vectors are already computed — the service never encodes an image.

---

## 9. Error handling

| Failure | Behaviour |
|---|---|
| Groq cap / 429 / timeout / transport | Rule-based extraction, `source: "rules"`, one-line notice |
| Unparseable JSON | `split_on_json_failure`, then the fallback |
| Filters match nothing | Empty state **naming the filters that fired**, with a widen-the-window action — a failure the user can act on, which is the thesis |
| Cold start | Skeleton UI; `/health` warms encoders |
| Missing image file | Placeholder card, logged, never a broken layout |
| Unhandled service error | Typed JSON error + retry affordance |

---

## 10. Testing

1. **Parity test (the one that matters).** For all 30 tasks in `data/eval/tasks.jsonl`, the service's
   `/search` with oracle filters must return **the same ranked ids** as offline
   `demo_index.filtered_search`. This mechanically prevents the live demo and the deck from
   diverging.
2. **Inferred-filter eval — produces a number for the deck.** Run the *same* rule-based extractor
   offline across the 30 tasks as a third strategy alongside baseline and oracle. This yields the
   MVP's **real** recall@20, which lands between 0.053 and 0.583. Phase 5 currently has only bounds;
   this gives it a measured value, and Data & Metrics is the weakest competency at 27.08/40.
3. Unit tests: rule extractor per cue type; chip↔filter-key round trip; date-window arithmetic at
   `VAGUE_WINDOW_DAYS = 45`; empty-filter and no-match paths.
4. **The existing 150 tests stay green** throughout.
5. Playwright smoke run against the deployed URL before the link is cited anywhere.

---

## 11. Constraints and obligations

- **Anonymity.** Submission requires the user's name nowhere. Vercel preview URLs embed the account
  slug, so: neutral project name, and **the deck cites the production alias only**. Verify in an
  incognito window per the §9 checklist.
- **CC attribution.** `/attribution` ships with the first deploy, not later.
- **Privacy.** Visitor-typed text is never logged or persisted. `/evidence` ships only short evidence
  quotes and public URLs, never full post text or author names — matching the Space's existing rule.
- **Groq budget.** Free tier, 190K tokens/day per model, resets 05:30 IST. The demo model stays off
  the pipeline's models so a visitor can never consume pipeline budget.
- **Repo is not under git.** The spec cannot be committed as the skill's default flow assumes; it
  lives at this path and is tracked by hand.

---

## 12. Post-lock branch (after 26 Sep)

The shell is hypothesis-independent by design. One of three lands on top:

| Lock outcome | What gets built |
|---|---|
| `failure_stage` holds (`not_surfaced` + `system_misunderstood`) | Ship stages 1+3 as built; deepen episode grouping |
| H3 vindicated by interviews | Add stage 2 (one follow-up) and stage 4 (steer) |
| H4 (code-mixed) surfaces | Query rewriter ahead of the shared index |

v2 moved its framing *away* from H3 ("recovery loop" → "memory-reconstruction loop"). If interviews
vindicate H3, say plainly that the concept moved and the evidence moved it back. Rule B rewards the
stated verdict; a quiet switch does not.

---

## 13. Acceptance criteria

- [ ] A stranger opens the production URL and completes a retrieval task against the real 494-image
      index (Plan 2 Part 5 bar)
- [ ] Baseline ⇄ Trails toggle visibly changes results
- [ ] Parity test green: service results == offline `filtered_search` on all 30 tasks
- [ ] Inferred-filter recall@20 measured and recorded in `PROGRESS.md`
- [ ] `/evidence` renders all three tabs with **zero** function calls on tabs 2 and 3
- [ ] `/attribution` lists all 494 images
- [ ] Extraction degrades to rules with the Groq key removed, and still returns results
- [ ] 150 existing tests green
- [ ] No personal name in the URL, page text, or metadata — verified incognito

---

## 14. Open questions

1. **Project name.** Must be neutral. Proposal: `memory-trails-demo`. Needs the user's call.
2. **Does inferred-filter recall justify the toggle's framing?** If the inferred number lands near
   0.053, the honest deck line is "the mechanic works, the inference does not yet" — still a
   finding, but it changes the MVP slide's claim. Measured in §10.2 before the deck is written.
3. **`/evidence` MiniLM encoder.** ~120 MB for one tab. If cold starts hurt, fall back to
   structure-only episode matching (`demo_core.similar_episodes` already blends Jaccard and
   asset_type) and drop the encoder entirely. Decide after the first deploy measurement.
