# Memory Trails Fixes & Native Architecture Design

**Date:** 2026-10-06  
**Status:** Approved by User  
**Target Projects:**
- **Phase 1 (Immediate):** Webapp & Retrieval Engine Fixes (`webapp/apps/retrieval`, `webapp/apps/web`)
- **Phase 2 (Sub-project 2):** Native Mobile App (`apps/native-expo` / Expo React Native)

---

## 1. Problem Statement & Scope

Based on the product and UX audit ([`memory_trails_product_ux_review.md`](file:///Users/abhishekspillai/Google%20CaseStudy/webapp/memory_trails_product_ux_review.md)), Memory Trails succeeds at trust transparency and the "What was off?" repair loop, but suffers from engine and interaction failures in its core retrieval loop:
1. **Clue extraction drops specific scene words:** When a user expresses a rich memory ("at a cafe in Bengaluru with friends... there was a dosa on the table"), only the first category ("friends") is retained; highly specific words like "cafe" and "dosa" are discarded.
2. **Ranking favors episode size over clue completeness:** The usefulness scoring formula prioritizes multi-photo episode coherence over clue completeness, placing partial-match events above singleton photos that match 100% of the user's clues.
3. **Time ribbon lacks contextual temporal centering:** "Around that time" defaults to rendering from November 2023 (the dataset's beginning), even when a query specifies May 2026.
4. **Desktop phone-frame limits gesture validation:** The concept's ideal endgame is an on-device native mobile app with gestures (pinch-zoom, swipe dismiss, haptics).

Per user decision, work is decomposed into two phases:
- **Phase 1:** Fix the core retrieval engine, ranking algorithms, Time Ribbon, and web UI in the existing Next.js and FastAPI/Python codebase.
- **Phase 2:** Build the native mobile Expo app incorporating the seeded dataset and mobile-first gesture layer.

---

## 2. Phase 1: Webapp & Engine Architecture

### 2.1 Clue Extraction & Staged Suggestions
- **Component:** `webapp/apps/retrieval/clues.py`, `webapp/apps/retrieval/main.py`
- **Logic:**
  1. In `infer_clues()`, update category extraction to capture **all** matched distinct categories from the input text rather than taking only the first match `(fresh or hits)[0][1]`.
  2. The highest-priority match becomes the primary filter: `filters["category"] = cat`.
  3. Additional detected categories are collected into a `suggested_categories` list (e.g. `[{"category": "cafe", "word": "cafe"}, {"category": "dosa", "word": "dosa"}]`).
  4. Response payload from `/api/py/extract` includes `suggested_categories`.
  5. In `webapp/apps/web/app/components/MemoryTrails.tsx`, the Recap stage renders an interactive suggestions banner right below the active clue chips:
     `"I also heard: [ + cafe ] [ + dosa ]"`.
     Tapping a suggestion adds it as a clue or switches the category filter without re-typing.

### 2.2 Ranking by Clue Completeness (`clue_hits`)
- **Component:** `webapp/apps/retrieval/search.py`, `webapp/apps/web/app/components/Moments.tsx`
- **Logic:**
  1. In `group_by_episode()`, calculate `c_hits = clue_hits(rows, filters)`.
  2. Determine if the group contains full matches: `full_match = (c_hits > 0 and matched_dims == len(dims))`.
  3. Attach `g["clue_hits"] = c_hits` and `g["full_match"] = full_match`.
  4. Update group sorting:
     ```python
     return sorted(groups.values(), key=lambda g: (-g["clue_hits"], -g["usefulness"], -g["top_score"]))
     ```
  5. In `Moments.tsx`, render a distinctive highlight badge on candidate cards where `full_match` is true:
     `"✓ Matches all your clues"`.
  6. Ensure clue-complete singletons ("Other photos") receive full card parity: clickable contact cell, clear metadata, and active "View moment" button.

### 2.3 Synchronize "Around that time" Ribbon
- **Component:** `webapp/apps/web/app/components/TimeRibbon.tsx`
- **Logic:**
  1. If `activeDateFrom` or `activeDateTo` is provided, compute `activeMonth = (activeDateFrom || activeDateTo).slice(0, 7)`.
  2. Find `activeIndex = chapters.findIndex(c => c.month === activeMonth)`.
  3. If `activeIndex >= 0`, automatically scroll the `.ribbon-scroll` container so that `activeIndex` is horizontally centered in the viewport.
  4. The ribbon navigation buttons (`← Earlier`, `Later →`) shift relative to the active month chapter.
  5. If no date clues exist in the memory (`!activeDateFrom && !activeDateTo`):
     - Change eyebrow label from `"Around that time"` to `"Browse months"`.
     - Change support copy to `"Explore moments across the library timeline"`.

### 2.4 Supporting UI Polish & Transparency Fixes
- **Component:** `webapp/apps/web/app/components/Moments.tsx`, `Viewer.tsx`, `Disclaimer.tsx`, `Breadcrumb.tsx`, `MemoryTrails.tsx`
- **Refinements:**
  - **Evidence formatting:** Format ISO date ranges in `Evidence` using `formatWindow()` instead of leaking raw strings (`2026-03-31 to 2026-06-29` -> `31 Mar – 29 Jun 2026`).
  - **Evidence label:** Change `"in the first photo"` tag from uppercase jargon to `"from the place recorded on the first photo"`.
  - **Breadcrumbs:** Include clue kinds (`Place`, `Date`, `Scene`) alongside chip labels in `Breadcrumb.tsx`.
  - **Disclaimer:** Remove the persistent `<Disclaimer />` footer from every sub-sheet in `MemoryTrails.tsx`; present a clean notice on the initial Compose screen and an info icon in the header opening an info modal.
  - **Ruled-out moments:** Add an "Undo" button next to *"Not showing X moments you ruled out"* in `MemoryTrails.tsx` to restore dismissed moments.
  - **Viewer Pinch-to-Zoom:** Add touch-scaling (`touchmove` distance ratio) in `Viewer.tsx` so photos can be zoomed on mobile viewports.
  - **Satisfaction survey:** Defer the Yes/Partly/No prompt until after the user finishes viewing and clicks "Done".

---

## 3. Phase 2: Native Mobile Blueprint (Expo React Native)

- **Framework:** Expo (React Native) with TypeScript.
- **Data & Seed:** Pre-bundled SQLite / local JSON index with the 1,282 photo metadata entries and representative public image assets.
- **Search Engine:** Local rules-based clue extractor + on-device embeddings/cosine ranking or bridge to lightweight FastAPI endpoint.
- **Mobile Gesture Layer:**
  - Multi-touch pinch-to-zoom on photos using `react-native-gesture-handler`.
  - Interactive swipe-down to dismiss photo viewer.
  - Haptic feedback on "That's the one" and clue selection.
  - One-handed ergonomics (bottom-aligned action sheets and search prompts).

---

## 4. Verification & Testing Strategy

1. **Python Engine Tests:**
   - Execute `.venv/bin/pytest webapp/apps/retrieval` to verify all 120 existing tests pass.
   - Add new tests in `test_clues.py` for multi-category extraction and `suggested_categories`.
   - Add test in `test_search.py` verifying that groups with higher `clue_hits` outrank larger episodes with fewer clue matches.
2. **Next.js Frontend Build & Typecheck:**
   - Run `npm run build` inside `webapp/apps/web` with Turbopack to verify zero TypeScript or compilation errors.
3. **Manual Interactive Verification:**
   - Test memory: *"I was at a cafe in Bengaluru with friends around late May, there was a dosa on the table"*.
   - Verify that "cafe" and "dosa" appear as suggestions, that ranking prioritizes clue-complete candidates, and that the Time Ribbon centers on May 2026.
