# Memory Anchors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the "Memory Anchors" idea (Idea 001) in Google Photos Memory Trails, providing library-grounded anchor chips for immediate recognition-based memory retrieval while strictly preserving offline evaluation parity.

**Architecture:** A lightweight `/facets` endpoint in FastAPI exposes library-grounded values (`location`, `category`, `episode`). The Next.js client renders interactive anchor chips in the compose and recap stages of `MemoryTrails.tsx`. Selected anchors map 1-to-1 to existing `filtered_search` filter keys without altering ranking logic or index structures.

**Tech Stack:** Python 3.12 (FastAPI, pytest), Next.js 16 (React 19, TypeScript, Vanilla CSS).

## Global Constraints

- **Zero-drift parity:** `tests/test_service_parity.py` must pass with 0 regressions on all 30 offline benchmark tasks.
- **Strict metadata alignment:** Only offer anchors corresponding to existing metadata fields (`location`, `category`, `date_from`/`date_to`, `episode`). People and OCR text anchors are strictly deferred.
- **No form fatigue:** Keep suggested anchors limited to 4–6 prominent, verified anchors.
- **Telemetry preservation:** Track all anchor interactions via `lib/track.ts`.

---

### Task 1: Retrieval API — Expose Facets & Anchor Suggestions

**Files:**
- Modify: `webapp/apps/retrieval/main.py`
- Test: `webapp/apps/retrieval/tests/test_api.py`

**Interfaces:**
- Consumes: `facets.load_facets(RECORDS)`, `RECORDS`
- Produces: `GET /facets` endpoint returning:
  ```json
  {
    "locations": ["Goa", "Bengaluru", ...],
    "categories": ["cafe", "beach", ...],
    "episodes": ["diwali 2025", ...],
    "top_anchors": [
      { "id": "a1", "cue": "place_named", "label": "Goa", "filter_key": "location", "value": "Goa" },
      { "id": "a2", "cue": "object", "label": "café", "filter_key": "category", "value": "cafe" },
      { "id": "a3", "cue": "object", "label": "beach", "filter_key": "category", "value": "beach" },
      { "id": "a4", "cue": "place_named", "label": "Bengaluru", "filter_key": "location", "value": "Bengaluru" },
      { "id": "a5", "cue": "object", "label": "food", "filter_key": "category", "value": "food" }
    ]
  }
  ```

- [ ] **Step 1: Write the failing test for `/facets` in `webapp/apps/retrieval/tests/test_api.py`**

```python
def test_facets_endpoint_returns_library_anchors(client):
    res = client.get("/facets")
    assert res.status_code == 200
    data = res.json()
    assert "locations" in data and len(data["locations"]) > 0
    assert "categories" in data and len(data["categories"]) > 0
    assert "top_anchors" in data
    assert len(data["top_anchors"]) >= 3
    for a in data["top_anchors"]:
        assert a["filter_key"] in {"location", "category", "episode", "date_from"}
        assert "label" in a and "value" in a and "cue" in a
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=webapp/apps/retrieval:. .venv/bin/pytest webapp/apps/retrieval/tests/test_api.py -k test_facets_endpoint_returns_library_anchors`  
Expected: FAIL (404 Not Found or AttributeError)

- [ ] **Step 3: Implement `/facets` in `webapp/apps/retrieval/main.py`**

Derive top anchors by counting occurrences in `RECORDS` for locations and categories, and return the structured response.

```python
def _compute_top_anchors(records: list, limit: int = 6) -> list[dict]:
    loc_counts: dict[str, int] = {}
    cat_counts: dict[str, int] = {}
    for r in records:
        loc = r.get("location")
        if loc:
            loc_counts[loc] = loc_counts.get(loc, 0) + 1
        cat = r.get("category")
        if cat:
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

    anchors = []
    idx = 1
    # Top locations
    for loc, _ in sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
        anchors.append({
            "id": f"a{idx}",
            "cue": "place_named",
            "label": loc,
            "filter_key": "location",
            "value": loc,
        })
        idx += 1
    # Top categories
    from clues import CATEGORY_LABELS
    for cat, _ in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
        anchors.append({
            "id": f"a{idx}",
            "cue": "object",
            "label": CATEGORY_LABELS.get(cat, cat.title()),
            "filter_key": "category",
            "value": cat,
        })
        idx += 1
    return anchors

TOP_ANCHORS = _compute_top_anchors(RECORDS)

@app.get("/facets")
def facets():
    return {
        "locations": FACETS.locations,
        "categories": FACETS.categories,
        "episodes": FACETS.episodes,
        "top_anchors": TOP_ANCHORS,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=webapp/apps/retrieval:. .venv/bin/pytest webapp/apps/retrieval/tests/test_api.py -k test_facets_endpoint_returns_library_anchors`  
Expected: PASS

- [ ] **Step 5: Commit Task 1**

```bash
git add webapp/apps/retrieval/main.py webapp/apps/retrieval/tests/test_api.py
git commit -m "feat(retrieval): add /facets endpoint returning library anchors"
```

---

### Task 2: Frontend API Client & Types for Anchors

**Files:**
- Modify: `webapp/apps/web/lib/api.ts`
- Modify: `webapp/apps/web/lib/track.ts`

**Interfaces:**
- Consumes: `/api/py/facets`
- Produces:
  ```typescript
  export type Anchor = {
    id: string;
    cue: string;
    label: string;
    filter_key: string;
    value: string;
  };
  export type FacetsResult = {
    locations: string[];
    categories: string[];
    episodes: string[];
    top_anchors: Anchor[];
  };
  export function fetchFacets(): Promise<FacetsResult>;
  export function anchorToChip(anchor: Anchor): Chip;
  ```

- [ ] **Step 1: Update `api.ts` with Anchor types and `fetchFacets` client**

Add `Anchor` and `FacetsResult` interfaces, `fetchFacets()` with fallback defaults, and `anchorToChip()`.

- [ ] **Step 2: Update `track.ts` to support anchor telemetry events**

Add `"anchor_selected"` and `"anchor_removed"` to tracked events in `lib/track.ts`.

- [ ] **Step 3: Verify TypeScript builds**

Run: `cd webapp/apps/web && npm run build`  
Expected: Clean build without errors.

- [ ] **Step 4: Commit Task 2**

```bash
git add webapp/apps/web/lib/api.ts webapp/apps/web/lib/track.ts
git commit -m "feat(web): add Anchor types, fetchFacets API client, and anchor tracking"
```

---

### Task 3: Create `AnchorPicker` Component & Styling

**Files:**
- Create: `webapp/apps/web/app/components/AnchorPicker.tsx`
- Modify: `webapp/apps/web/app/globals.css`

**Interfaces:**
- Consumes: `Anchor`, `Chip`
- Produces: `<AnchorPicker anchors={anchors} selectedAnchorIds={selectedIds} onToggleAnchor={handleToggle} />`

- [ ] **Step 1: Write `AnchorPicker.tsx`**

A clean pill-based component displaying 4–6 high-confidence anchors with grounded icons/labels. Tapping toggles selection or adds as an active cue.

```tsx
import type { Anchor } from "@/lib/api";
import { clueKind } from "@/app/components/ClueChip";

export function AnchorPicker({
  anchors,
  selectedAnchorIds,
  onToggleAnchor,
}: {
  anchors: Anchor[];
  selectedAnchorIds: Set<string>;
  onToggleAnchor: (anchor: Anchor) => void;
}) {
  if (!anchors || anchors.length === 0) return null;
  return (
    <div className="anchors-section">
      <p className="t-eyebrow anchors-label">Or start with a memory anchor</p>
      <div className="anchors-list" role="group" aria-label="Suggested memory anchors">
        {anchors.map((anchor) => {
          const selected = selectedAnchorIds.has(anchor.id);
          return (
            <button
              key={anchor.id}
              type="button"
              className={`anchor-chip ${selected ? "selected" : ""}`}
              onClick={() => onToggleAnchor(anchor)}
              aria-pressed={selected}
            >
              <span className="anchor-label">{anchor.label}</span>
              <span className="anchor-cue">{clueKind(anchor.cue)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Add CSS styles in `webapp/apps/web/app/globals.css`**

Add styling for `.anchors-section`, `.anchors-list`, and `.anchor-chip` matching the existing design system.

- [ ] **Step 3: Run build to verify component compiles**

Run: `cd webapp/apps/web && npm run build`  
Expected: Clean build.

- [ ] **Step 4: Commit Task 3**

```bash
git add webapp/apps/web/app/components/AnchorPicker.tsx webapp/apps/web/app/globals.css
git commit -m "feat(web): create AnchorPicker component with Google Photos styling"
```

---

### Task 4: Integrate Memory Anchors into `MemoryTrails.tsx`

**Files:**
- Modify: `webapp/apps/web/app/components/MemoryTrails.tsx`

**Interfaces:**
- Consumes: `AnchorPicker`, `fetchFacets`, `anchorToChip`
- Produces: Integrated Memory Trails flow allowing direct memory re-entry from anchors.

- [ ] **Step 1: Load top anchors in `MemoryTrails.tsx`**

Fetch facets on mount or initialize with fallback anchors:
```tsx
const [anchors, setAnchors] = useState<Anchor[]>(DEFAULT_ANCHORS);
const [selectedAnchorIds, setSelectedAnchorIds] = useState<Set<string>>(new Set());
```

- [ ] **Step 2: Handle anchor selection and interaction**

When an anchor is tapped:
- If unselected: add to `selectedAnchorIds`, convert to `Chip`, add to `chips`, merge filter into `filters`, track `"anchor_selected"`.
- If user clicks "Show moments" or "Continue" with anchors selected, transition directly to `moments` (or `recap`). If no text is typed, use anchor labels as query placeholder (e.g. *"Photos from Goa"*).
- When a chip is removed via `onRemoveChip`, remove from `selectedAnchorIds` as well.

- [ ] **Step 3: Mount `AnchorPicker` in `compose` stage**

Place `AnchorPicker` right above or below the examples block so the user can easily choose an anchor before or alongside entering text.

- [ ] **Step 4: Build web app and verify no errors**

Run: `cd webapp/apps/web && npm run build`  
Expected: Clean build.

- [ ] **Step 5: Commit Task 4**

```bash
git add webapp/apps/web/app/components/MemoryTrails.tsx
git commit -m "feat(web): integrate AnchorPicker into MemoryTrails re-entry flow"
```

---

### Task 5: Parity & Regression Verification, Documentation Update

**Files:**
- Test: `tests/test_service_parity.py`
- Modify: `/Users/abhishekspillai/MVP_Ideas/README.md`
- Modify: `/Users/abhishekspillai/MVP_Ideas/001-memory-anchors.md`

- [ ] **Step 1: Run offline parity tests**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_service_parity.py`  
Expected: 3 passed, 0 failures. (Mechanical proof of 0 drift on all 30 evaluation tasks).

- [ ] **Step 2: Run all retrieval service tests**

Run: `PYTHONPATH=webapp/apps/retrieval:. .venv/bin/pytest webapp/apps/retrieval/tests`  
Expected: All tests pass.

- [ ] **Step 3: Update `MVP_Ideas/README.md` and `001-memory-anchors.md`**

Update the status table in `README.md` to reflect `Built: Yes` once all tests pass.

- [ ] **Step 4: Commit changes in both repositories**

```bash
git add tests/ webapp/
git commit -m "feat(mvp): complete Memory Anchors implementation with 100% parity preserved"
```
