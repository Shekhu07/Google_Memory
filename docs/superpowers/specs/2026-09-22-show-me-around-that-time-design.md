# "Show me around that time" Design Specification

- **Date:** 2026-09-22
- **Topic:** "Show me around that time" (Idea 002)
- **Status:** Approved for Implementation

---

## 1. Overview & Context

"Show me around that time" addresses temporal memory fuzziness by introducing a chronological visual ribbon of memory chapters and quick time-shift controls ("← Earlier", "Later →") into the Memory Trails retrieval experience.

### The Evidence It Serves
- **#1 Remembered Cue:** `temporal_approx` accounts for **40 of 144** attempts (27.8%), with exact dates accounting for another 14 (total 37.5%).
- **Highest Retrieval Gain:** Offline evaluation on the 30 case study tasks proved that applying a temporal window drives recall from **0.052 to 0.571** (+0.519).
- **Near-Miss Boundary Recovery:** Users who recall "around December" often seek moments occurring in late November or early January. Currently, a missed date window leads to an empty or irrelevant result set. The visual ribbon transforms a dead end into a 1-tap recovery.

---

## 2. Capabilities & Constraints

- **Zero New Infrastructure:** Fully supported by the existing `date` field in `library.jsonl` and the existing `date_from` / `date_to` window contract in `engine.demo_index.filtered_search`.
- **Zero Parity Drift:** Time shifts pass standard ISO date strings into `filtered_search`, maintaining 100% agreement with `tests/test_service_parity.py`.

---

## 3. Architecture & User Experience

### 3.1 Backend: Monthly Chapter Aggregation (`webapp/apps/retrieval`)
In `main.py`, compute `MONTHLY_CHAPTERS` across the 494 photos in `RECORDS`:
- Group photos by `YYYY-MM`.
- For each active month, compute:
  - `month`: e.g. `"2023-12"`
  - `label`: e.g. `"Dec 2023"`
  - `date_from`: e.g. `"2023-12-01"`
  - `date_to`: e.g. `"2023-12-31"`
  - `count`: number of photos
  - `thumbnail`: path to a representative photo (e.g. `library/0231.jpg`)
- Expose via `GET /facets` under `monthly_chapters`.

### 3.2 Frontend: `TimeRibbon` Component (`webapp/apps/web/app/components/TimeRibbon.tsx`)
- Displayed in `stage === "moments"` (and in `stage === "empty"` for instant recovery).
- Shows:
  - "← Earlier" step button.
  - Active and neighboring month chapter cards with representative thumbnails, dates, and photo counts.
  - "Later →" step button.
- Clicking an adjacent chapter or step button invokes `onShiftWindow(newFrom, newTo, label)`.

### 3.3 Integration in `MemoryTrails.tsx`
- When `onShiftWindow` fires:
  - Updates `filters.date_from` and `filters.date_to`.
  - Updates the active temporal `ClueChip` label.
  - Fires `track("time_ribbon_shifted", { direction, month })`.
  - Re-executes `runSearch(newFilters, mode)`.

---

## 4. Verification Plan

1. **Parity Preservation:** `pytest tests/test_service_parity.py` passes 3/3 tasks.
2. **Backend Unit Tests:** `pytest webapp/apps/retrieval/tests` passes all tests including `/facets` monthly chapters.
3. **Frontend Build:** `npm run build` succeeds cleanly.
4. **Vercel Deployment:** Deployed to `https://memory-anchors-demo.vercel.app` and verified via curl and UI smoke testing.
