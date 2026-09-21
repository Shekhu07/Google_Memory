# Memory Anchors Design Specification

- **Date:** 2026-09-22
- **Topic:** Memory Anchors (Idea 001)
- **Status:** Approved for Implementation

---

## 1. Overview & Context

Memory Anchors allows users to initiate or refine memory retrieval using grounded, library-verified anchors (such as place, category, time span, or event) rather than relying exclusively on unconstrained free-text narratives.

### The Evidence It Serves
Analysis of 144 real memory retrieval attempts (`data/interim/episodes.jsonl`) revealed that:
- **41.7%** (60/144) fail at `not_surfaced` (relevant photos never appeared).
- **35.4%** (51/144) fail at `system_misunderstood` (the query parser extracted wrong clues or misplaced filter bounds).
- In total, **77.1%** of failures occur before recovery interactions are possible.

By providing explicit, grounded anchor chips (e.g., *Goa*, *café*, *last year*, *beach*) derived directly from the user's photo library, the system eliminates free-text parsing errors and lets users assemble their search by recognition.

---

## 2. Capabilities & Constraints

### What the Index Supports Today (Zero New Infrastructure)
The current 494-image index carries CLIP image embeddings alongside four metadata fields:
1. `location`: Places (`place_named` cue) — e.g. *Goa*, *Bengaluru*.
2. `category`: Activity / scene (`object` cue) — e.g. *café*, *beach*, *food*, *receipt*, *medicine*.
3. `date`: Contiguous time windows (`temporal_approx`, `exact_date` cues) — e.g. *December 2023*, *last summer*.
4. `episode_id`: Clustered events (`event_anchor` cue).

### Explicitly Excluded (Deferred)
- **People (`who_with`):** Requires a face clustering pipeline and identity recognition.
- **In-image text (`text_in_image`):** Requires an OCR indexing pipeline.

The initial implementation restricts suggested anchors to `location`, `category`, and `date` spans already present in `facets.py`.

---

## 3. Architecture & User Experience

### 3.1 Interaction Flow in `MemoryTrails.tsx`
1. **Compose Screen (`stage === "compose"`):**
   - The user sees the text input field as usual (*"Start with what you remember"*).
   - Below the text area, instead of only passive text examples, the interface presents a curated row of **Suggested memory anchors** (e.g. *Goa*, *café*, *beach*, *last year*).
   - Tapping an anchor immediately adds it as a selected anchor chip and can either pre-fill the query or transition to the `recap`/`moments` stage with filters pre-populated.
2. **Recap Screen (`stage === "recap"`):**
   - Anchors appear alongside any extracted text clues as standard `ClueChip` elements.
   - Users can remove anchors (`onRemoveChip`) with full undo support.
3. **Moments Screen (`stage === "moments"`):**
   - Anchors are reflected in the breadcrumb rail.
   - Users can remove an anchor to immediately widen the search.

### 3.2 Backend Service API (`webapp/apps/retrieval`)
- **Facet Provider:** Reuse `facets.py` (`load_facets`).
- **Endpoint / Payload:** Expose `/facets` or include top candidate anchors in the app initialization so the frontend has high-confidence chips ready without latency.
- **Search Execution:** Continue calling `search.search` / `engine.demo_index.filtered_search` with the exact same filter dictionary contract:
  ```python
  filters = {
      "location": "...",
      "category": "...",
      "date_from": "YYYY-MM-DD",
      "date_to": "YYYY-MM-DD",
      "episode": "..."
  }
  ```

---

## 4. Preservation of Retrieval Parity Gate

The critical system invariant is that `tests/test_service_parity.py` asserts the deployed service returns the exact same results as offline evaluation across all 30 benchmark tasks.

- **Impact on Core Ranking:** **Zero.**
- Anchor selections pass standard `filters` into `filtered_search`. The underlying CLIP cosine similarity calculations, ranking order, and offline tasks remain untouched.
- `tests/test_service_parity.py` must stay 100% green before and after the change.

---

## 5. Telemetry & Success Criteria

Instrumentation in `lib/track.ts`:
- `anchor_selected`: Fires when an anchor chip is tapped (`{ cue: string, value: string }`).
- `anchor_removed`: Fires when an anchor chip is removed.
- `time_to_first_plausible_moment`: Measured from session start to `stage === "moments"`.
- `reformulation_count`: Edits/removals needed before `retrieval_confirmed`.

---

## 6. Verification Plan

1. **Unit & Parity Tests:** Run `pytest tests/test_service_parity.py` in `~/Google CaseStudy` to verify zero regression.
2. **Backend API Test:** Verify facet loading and search execution with explicit anchor filters.
3. **Frontend Build & UI Test:** Verify Next.js build succeeds (`npm run build` in `webapp/apps/web`) and verify anchor interactions in the browser.
