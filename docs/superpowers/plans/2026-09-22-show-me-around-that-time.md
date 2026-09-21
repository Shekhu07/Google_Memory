# "Show me around that time" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the "Show me around that time" feature (Idea 002) in Google Photos Memory Trails on top of Memory Anchors, introducing a visual chronological ribbon of memory chapters and time-shift controls to rescue near-miss date boundaries while preserving 100% offline evaluation parity.

**Architecture:** The retrieval service exposes aggregated `monthly_chapters` with representative photo thumbnails via `/facets`. The frontend renders a horizontal `TimeRibbon` above moments whenever a date filter or episode span is active, allowing users to shift adjacent time windows with 1 tap. Deployed to the existing `memory-anchors-demo` Vercel application.

**Tech Stack:** Python 3.12 (FastAPI, pytest), Next.js 16 (React 19, TypeScript, Vanilla CSS), Vercel CLI.

## Global Constraints

- **Zero-drift parity:** `tests/test_service_parity.py` must pass with 0 regressions on all 30 offline benchmark tasks.
- **Strict metadata alignment:** Uses only the existing `date` field in `library.jsonl` and existing `date_from` / `date_to` filter contract.
- **Telemetry preservation:** Track all temporal ribbon shifts via `lib/track.ts`.
- **Target project:** Deploys to `memory-anchors-demo` on Vercel.

---

### Task 1: Retrieval API — Aggregate Monthly Chapters in `/facets`

**Files:**
- Modify: `webapp/apps/retrieval/main.py`
- Test: `webapp/apps/retrieval/tests/test_api.py`

**Interfaces:**
- Consumes: `RECORDS`
- Produces: `monthly_chapters` array in `GET /facets`:
  ```json
  [
    {
      "month": "2023-12",
      "label": "Dec 2023",
      "date_from": "2023-12-01",
      "date_to": "2023-12-31",
      "count": 45,
      "thumbnail": "library/0231.jpg"
    }
  ]
  ```

- [ ] **Step 1: Write the failing test for `monthly_chapters` in `webapp/apps/retrieval/tests/test_api.py`**

```python
def test_facets_returns_monthly_chapters():
    res = client.get("/facets")
    assert res.status_code == 200
    data = res.json()
    assert "monthly_chapters" in data
    chapters = data["monthly_chapters"]
    assert len(chapters) >= 5
    first = chapters[0]
    for key in ("month", "label", "date_from", "date_to", "count", "thumbnail"):
        assert key in first
    assert first["count"] > 0
    assert first["thumbnail"].startswith("library/")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=webapp/apps/retrieval:. .venv/bin/pytest webapp/apps/retrieval/tests/test_api.py -k test_facets_returns_monthly_chapters`  
Expected: FAIL (KeyError or AssertionError on `"monthly_chapters" in data`)

- [ ] **Step 3: Implement `_compute_monthly_chapters()` in `webapp/apps/retrieval/main.py`**

```python
def _compute_monthly_chapters(records: list) -> list[dict]:
    import calendar
    by_month: dict[str, list] = {}
    for r in records:
        dt = r.get("date")
        if dt and len(dt) >= 7:
            ym = dt[:7]
            by_month.setdefault(ym, []).append(r)

    chapters = []
    for ym in sorted(by_month):
        photos = by_month[ym]
        y, m = ym.split("-")
        month_int = int(m)
        last_day = calendar.monthrange(int(y), month_int)[1]
        label = f"{calendar.month_abbr[month_int]} {y}"
        # Pick a representative thumbnail
        thumb = photos[0].get("file") or f"library/{photos[0]['id'].split(':')[-1]}.jpg"
        chapters.append({
            "month": ym,
            "label": label,
            "date_from": f"{ym}-01",
            "date_to": f"{ym}-{last_day:02d}",
            "count": len(photos),
            "thumbnail": thumb,
        })
    return chapters

MONTHLY_CHAPTERS = _compute_monthly_chapters(RECORDS)
```

Include `MONTHLY_CHAPTERS` in `facets()` return dict.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=webapp/apps/retrieval:. .venv/bin/pytest webapp/apps/retrieval/tests/test_api.py -k test_facets_returns_monthly_chapters`  
Expected: PASS

- [ ] **Step 5: Commit Task 1**

```bash
git add webapp/apps/retrieval/main.py webapp/apps/retrieval/tests/test_api.py
git commit -m "feat(retrieval): expose monthly_chapters with thumbnails in /facets"
```

---

### Task 2: Frontend API Client & Types for Monthly Chapters

**Files:**
- Modify: `webapp/apps/web/lib/api.ts`
- Modify: `webapp/apps/web/lib/track.ts`

**Interfaces:**
- Consumes: `/api/py/facets`
- Produces:
  ```typescript
  export type MonthlyChapter = {
    month: string;
    label: string;
    date_from: string;
    date_to: string;
    count: number;
    thumbnail: string;
  };
  export type FacetsResult = {
    locations: string[];
    categories: string[];
    episodes: string[];
    top_anchors: Anchor[];
    monthly_chapters: MonthlyChapter[];
  };
  ```

- [ ] **Step 1: Update `api.ts` with `MonthlyChapter` and updated `FacetsResult`**
- [ ] **Step 2: Add `"time_ribbon_shifted"` event to `TrailEvent` in `track.ts`**
- [ ] **Step 3: Run `npm run build` in `webapp/apps/web` to verify types**
- [ ] **Step 4: Commit Task 2**

```bash
git add webapp/apps/web/lib/api.ts webapp/apps/web/lib/track.ts
git commit -m "feat(web): add MonthlyChapter types and time_ribbon_shifted tracking"
```

---

### Task 3: Create `TimeRibbon` UI Component & Styling

**Files:**
- Create: `webapp/apps/web/app/components/TimeRibbon.tsx`
- Modify: `webapp/apps/web/app/globals.css`

**Interfaces:**
- Consumes: `MonthlyChapter`, `date_from`, `date_to`
- Produces: `<TimeRibbon chapters={chapters} activeDateFrom={filters.date_from} activeDateTo={filters.date_to} onShift={handleShift} />`

- [ ] **Step 1: Write `TimeRibbon.tsx`**

Renders horizontal ribbon of adjacent monthly chapters around active date window with thumbnails, photo counts, and "← Earlier" / "Later →" step controls.

- [ ] **Step 2: Add styles for `.time-ribbon`, `.ribbon-scroll`, `.chapter-card`, `.chapter-thumb` in `globals.css`**
- [ ] **Step 3: Run `npm run build` to verify compilation**
- [ ] **Step 4: Commit Task 3**

```bash
git add webapp/apps/web/app/components/TimeRibbon.tsx webapp/apps/web/app/globals.css
git commit -m "feat(web): create TimeRibbon component with visual chapters and shift controls"
```

---

### Task 4: Integrate `TimeRibbon` into `MemoryTrails.tsx`

**Files:**
- Modify: `webapp/apps/web/app/components/MemoryTrails.tsx`

**Interfaces:**
- Consumes: `TimeRibbon`, `monthly_chapters`
- Produces: Interactive time shifts in `stage === "moments"` and `stage === "empty"`.

- [ ] **Step 1: Store `monthlyChapters` in `MemoryTrails.tsx` state from `fetchFacets()`**
- [ ] **Step 2: Implement `onShiftTime(chapter: MonthlyChapter, direction: "earlier" | "later" | "chapter")`**
  - Updates `filters.date_from` and `filters.date_to`.
  - Replaces or adds `Chip` with label matching the chapter (e.g. "Dec 2023").
  - Tracks `time_ribbon_shifted`.
  - Calls `runSearch(nextFilters, mode)`.
- [ ] **Step 3: Mount `TimeRibbon` above moments in `stage === "moments"` and in `stage === "empty"`**
- [ ] **Step 4: Verify Next.js build passes cleanly**
- [ ] **Step 5: Commit Task 4**

```bash
git add webapp/apps/web/app/components/MemoryTrails.tsx
git commit -m "feat(web): integrate TimeRibbon into MemoryTrails moments and recovery flows"
```

---

### Task 5: Parity Verification, Vercel Deployment & Docs Update

**Files:**
- Test: `tests/test_service_parity.py`
- Test: `webapp/apps/retrieval/tests/`
- Modify: `/Users/abhishekspillai/MVP_Ideas/README.md`
- Modify: `/Users/abhishekspillai/MVP_Ideas/002-show-me-around-that-time.md`

- [ ] **Step 1: Run offline parity tests (`tests/test_service_parity.py`)**  
  Expected: 3 passed (0 drift on all 30 benchmark tasks).
- [ ] **Step 2: Run all retrieval service tests (`webapp/apps/retrieval/tests`)**  
  Expected: All passed.
- [ ] **Step 3: Deploy to production on Vercel**
  ```bash
  npx vercel deploy --prod --project memory-anchors-demo -y
  ```
- [ ] **Step 4: Smoke test live deployment**
  ```bash
  curl -s https://memory-anchors-demo.vercel.app/api/py/facets | grep "monthly_chapters"
  ```
- [ ] **Step 5: Update `MVP_Ideas/README.md` and `002-show-me-around-that-time.md`**  
  Set `Built: [Yes (Live Demo)](https://memory-anchors-demo.vercel.app)`
- [ ] **Step 6: Commit documentation and check off plan**
