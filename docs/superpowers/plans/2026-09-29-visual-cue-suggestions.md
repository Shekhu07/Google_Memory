# Visual-Cue Suggestions After a Miss Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement visual-cue suggestions after a miss in Memory Trails (`webapp/apps/retrieval` and `webapp/apps/web`) to offer 3–4 visible details from the closest photos that steer the query vector upon selection.

**Architecture:** 
- In the backend, a fixed vocabulary of 36 visible details is scored against precomputed photo vectors into z-scores (`CueBank`), cached on the first search.
- When results miss or are empty, candidates (top 24 or baseline fallback) are divided by visual cues that split the set (evidence 15–80%, no query overlap, max 2 per group).
- Tapping a suggestion steers the query vector $q' = \text{normalise}(\hat{q} + \alpha \sum \text{cue\_vec})$ without adding metadata filters.
- In the frontend, `SeenCues` renders chips inside `NotHere` and `NoMatch`, feeds into `seen` state, creates a removable "Something you saw" chip, and logs telemetry.

**Tech Stack:** Python 3.12, FastAPI, NumPy, Pytest, Next.js 15, TypeScript, React 19, CSS.

## Global Constraints

- Vocabulary: 36 visible details across 5 groups (colour, wearing, people, thing, setting).
- Constraints: Evidence $\ge$ 15% (`MIN_SHARE = 0.15`), narrowing $\le$ 80% (`MAX_SHARE = 0.80`), query margin 0.12 above median cosine, max 2 per group, max 3 selected.
- Steering parameter: $\alpha = 1.0$, normalising vector after addition.
- Backward compatibility: baseline mode disables cue suggestions and vector steering; offline eval and tests remain stable.
- Copy requirements: "Try something you'd have seen", "Seen in N of the X closest photos", "Something you saw".

---

### Task 1: Backend Unit Tests for Visual Cues (`tests/test_cues.py`)

**Files:**
- Create: `webapp/apps/retrieval/tests/test_cues.py`
- Reference: `webapp/apps/retrieval/cues.py`

**Interfaces:**
- Consumes: `cues.build_bank`, `cues.suggest`, `cues.steer`, `cues.known`, `encoder.TextEncoder`
- Produces: Test suite validating all 6 core cue behaviors.

- [ ] **Step 1: Write `tests/test_cues.py`**

```python
import numpy as np
import pytest
from cues import build_bank, suggest, steer, known, CueBank, VOCAB
from encoder import TextEncoder
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

@pytest.fixture(scope="module")
def encoder():
    return TextEncoder(DATA)

@pytest.fixture(scope="module")
def bank(encoder):
    _index = np.load(DATA / "index.npz", allow_pickle=False)
    return build_bank(encoder, _index["matrix"])

def test_fewer_than_4_candidates_returns_empty(bank):
    qv = np.zeros((1, 512), dtype=np.float32)
    qv[0, 0] = 1.0
    assert suggest(bank, "test query", qv, [0, 1, 2]) == []
    assert suggest(bank, "test query", qv, []) == []

def test_cake_query_does_not_offer_cake_when_share_over_80(bank, encoder):
    # Find photos that have high cake z-score
    cake_idx = bank.labels.index("a cake")
    # Pick candidate rows where cake is heavily present (> 80%)
    high_cake_rows = np.where(bank.z[:, cake_idx] > 1.0)[0]
    if len(high_cake_rows) >= 10:
        candidates = list(high_cake_rows[:10])
        qv = encoder.encode(["delicious celebration"]).astype(np.float32)
        suggestions = suggest(bank, "delicious celebration", qv, candidates)
        offered_labels = [s["label"] for s in suggestions]
        assert "a cake" not in offered_labels

def test_group_photo_query_does_not_offer_a_group_because_query_says_it(bank, encoder):
    qv = encoder.encode(["group photo"]).astype(np.float32)
    # Pick any 10 candidate rows
    candidates = list(range(10))
    suggestions = suggest(bank, "group photo", qv, candidates)
    offered_labels = [s["label"] for s in suggestions]
    assert "a group" not in offered_labels

def test_exclude_is_respected(bank, encoder):
    qv = encoder.encode(["celebration"]).astype(np.float32)
    candidates = list(range(20))
    base = suggest(bank, "celebration", qv, candidates, limit=4)
    if base:
        first_label = base[0]["label"]
        filtered = suggest(bank, "celebration", qv, candidates, limit=4, exclude=[first_label])
        assert first_label not in [s["label"] for s in filtered]

def test_at_most_two_per_group(bank, encoder):
    qv = encoder.encode(["outdoor nature walk"]).astype(np.float32)
    candidates = list(range(24))
    suggestions = suggest(bank, "outdoor nature walk", qv, candidates, limit=4)
    from collections import Counter
    groups = Counter(s["group"] for s in suggestions)
    for g, count in groups.items():
        assert count <= 2, f"Group {g} exceeded 2 items"

def test_steer_ignores_unknown_labels(bank):
    qv = np.zeros((1, 512), dtype=np.float32)
    qv[0, 0] = 1.0
    steered = steer(bank, qv, ["unknown_label_xyz"])
    np.testing.assert_allclose(steered, qv, rtol=1e-5)

def test_known_predicate():
    assert known("orange") is True
    assert known("candles or diyas") is True
    assert known("unknown_fake_label") is False
```

- [ ] **Step 2: Run test suite to verify it passes**

Run: `pytest tests/test_cues.py -v`
Expected: 7 passed.

- [ ] **Step 3: Commit**

```bash
git add webapp/apps/retrieval/tests/test_cues.py
git commit -m "test(retrieval): add unit tests for cues.py"
```

---

### Task 2: Retrieval API Latency & Fallback (`main.py`, `search.py`, `tests/test_api.py`)

**Files:**
- Modify: `webapp/apps/retrieval/search.py:285-300`
- Modify: `webapp/apps/retrieval/main.py:108-120, 163-172`
- Modify: `webapp/apps/retrieval/tests/test_api.py`

**Interfaces:**
- Consumes: `cues.CueBank`, `search.search`
- Produces: `/health` reports bank build latency; `/search` falls back to baseline candidates when search results are empty; API tests validate contract.

- [ ] **Step 1: Update `search.py` for empty search fallback**

In `webapp/apps/retrieval/search.py`, when `groups` is empty (e.g. strict filters yielded no candidates), fall back to `baseline_search` top 24 so `cue_suggestions` are still generated:
```python
    suggestions = []
    if ctx.cues is not None and mode != "baseline":
        from cues import suggest
        id_row = {pid: i for i, pid in enumerate(ctx.ids)}
        flat = [p["id"] for g in groups for p in g["photos"]]
        rows = [id_row[p] for p in flat[:24] if p in id_row]
        if not rows:
            base_hits = baseline_search(base_qv, ctx.ids, ctx.matrix, top_k=24)
            rows = [id_row[pid] for pid, _ in base_hits if pid in id_row]
        suggestions = suggest(ctx.cues, text, base_qv, rows, exclude=seen or [])
```

- [ ] **Step 2: Update `main.py` for latency logging in `/health`**

In `webapp/apps/retrieval/main.py`, record bank build duration in milliseconds:
```python
_cue_bank_latency_ms: float | None = None

def cue_bank():
    """Visual-cue vocabulary scored against every photo once (~0.6 s), on first search."""
    global _cue_bank_latency_ms
    if not hasattr(cue_bank, "_instance"):
        import time
        t0 = time.perf_counter()
        cue_bank._instance = build_bank(encoder(), MATRIX)
        _cue_bank_latency_ms = round((time.perf_counter() - t0) * 1000, 1)
    return cue_bank._instance
```
And in `/health`:
```python
@app.get("/health")
def health():
    return {
        "images": len(IDS),
        "episodes": len(FACETS.episodes),
        "encoder": "loaded" if encoder.cache_info().currsize else "lazy",
        "cue_bank": f"{_cue_bank_latency_ms}ms" if _cue_bank_latency_ms is not None else "lazy",
        "groq": bool(groq_client()),
        "manifest": json.loads((DATA / "manifest.json").read_text()),
    }
```

- [ ] **Step 3: Add API tests to `tests/test_api.py`**

Append tests for `/search` visual cues:
```python
def test_search_returns_cue_suggestions():
    res = client.post("/search", json={"text": "haldi ceremony", "filters": {}, "mode": "soft"})
    assert res.status_code == 200
    body = res.json()
    assert "cue_suggestions" in body
    assert isinstance(body["cue_suggestions"], list)
    assert len(body["cue_suggestions"]) <= 4
    if body["cue_suggestions"]:
        s = body["cue_suggestions"][0]
        for key in ("label", "phrase", "group", "seen_in", "of"):
            assert key in s

def test_seen_steers_results_without_changing_filters_applied():
    unseen = client.post("/search", json={"text": "family gathering", "filters": {}, "mode": "soft"}).json()
    seen = client.post("/search", json={"text": "family gathering", "filters": {}, "mode": "soft", "seen": ["orange"]}).json()
    assert seen["filters_applied"] == unseen["filters_applied"]
    assert seen["seen_applied"] == ["orange"]
    # Check that rank or episodes changed
    unseen_ids = [p["id"] for g in unseen["episodes"] for p in g["photos"]]
    seen_ids = [p["id"] for g in seen["episodes"] for p in g["photos"]]
    assert unseen_ids != seen_ids

def test_unknown_seen_label_returns_422():
    res = client.post("/search", json={"text": "family", "filters": {}, "mode": "soft", "seen": ["fake_not_real"]})
    assert res.status_code == 422
    assert "unknown visual cues" in res.json()["detail"]

def test_too_many_seen_labels_returns_422():
    res = client.post("/search", json={"text": "family", "filters": {}, "mode": "soft", "seen": ["orange", "red", "white", "pink"]})
    assert res.status_code == 422

def test_baseline_mode_returns_empty_cue_suggestions():
    res = client.post("/search", json={"text": "family", "filters": {}, "mode": "baseline", "seen": ["orange"]}).json()
    assert res["cue_suggestions"] == []
    assert res["seen_applied"] == []
```

- [ ] **Step 4: Run all pytest tests**

Run: `pytest tests/test_api.py -v`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add webapp/apps/retrieval/search.py webapp/apps/retrieval/main.py webapp/apps/retrieval/tests/test_api.py
git commit -m "feat(retrieval): integrate cue suggestions and vector steering into search API"
```

---

### Task 3: Simulation Evaluation in `engine/demo_eval.py`

**Files:**
- Modify: `engine/demo_eval.py`

**Interfaces:**
- Consumes: `cues.build_bank`, `cues.suggest`, `cues.steer`, `tasks.jsonl`, `tasks_dropout.jsonl`, `tasks_real.jsonl`
- Produces: `soft+seen_oracle` evaluation strategy and summary statistics matching Section 3.

- [ ] **Step 1: Add `soft+seen_oracle` evaluation strategy in `engine/demo_eval.py`**

Implement logic to:
1. Load all 191 unique queries across `synthetic`, `dropout`, and `real_all` when requested.
2. Build `cue_bank = build_bank(model, matrix)`.
3. For each task:
   - Run `soft_search` with inferred filters.
   - If target photo is in top 20: mark as initial hit.
   - If target photo is not in top 20 (miss):
     - Extract top 24 photo row indices.
     - Call `suggest(cue_bank, task["query"], qv, rows, limit=4)`.
     - Target photo index in matrix: `target_row = ids.index(target["id"])`.
     - Check if any suggested cue has `cue_bank.z[target_row, cue_idx] > 1.0` (true of target).
     - Check if first suggestion is true of target.
     - If true cue found: steer query vector `qv' = steer(cue_bank, qv, [true_cue["label"]])`.
     - Re-run soft search with `qv'` and check if target photo is now in top 20 (recovered).
4. Print summary table of misses, suggestions shown, true of target %, and recovered %.

- [ ] **Step 2: Run eval verification command**

Run: `.venv/bin/python -m engine.demo_eval --strategy soft+seen_oracle --tasks synthetic` (or a dry run).
Expected: Clean execution and output.

- [ ] **Step 3: Commit**

```bash
git add engine/demo_eval.py
git commit -m "feat(eval): add soft+seen_oracle evaluation strategy"
```

---

### Task 4: Frontend Types and Analytics (`lib/api.ts` & `lib/track.ts`)

**Files:**
- Modify: `webapp/apps/web/lib/api.ts`
- Modify: `webapp/apps/web/lib/track.ts`

**Interfaces:**
- Consumes: Backend `/search` response shape
- Produces: `CueSuggestion` type, updated `SearchResult`, updated `search()` caller, new `TrailEvent` variants.

- [ ] **Step 1: Update `lib/api.ts`**

Add `CueSuggestion` and update `SearchResult`:
```typescript
export type CueSuggestion = {
  label: string;
  phrase: string;
  group: string;
  seen_in: number;
  of: number;
};

export type SearchResult = {
  episodes: Episode[];
  total: number;
  mode: "trails" | "soft" | "baseline";
  filters_applied: Filters;
  outside_window?: OutsidePhoto[];
  conflicts?: Conflict[];
  cue_suggestions?: CueSuggestion[];
  seen_applied?: string[];
};
```
Update `search()`:
```typescript
export function search(
  text: string,
  filters: Filters,
  mode: "trails" | "soft" | "baseline",
  rejected: string[] = [],
  boostKey?: string | null,
  dateMeta?: DateMeta | null,
  seen: string[] = [],
) {
  return post<SearchResult>("/api/py/search", {
    text,
    filters,
    mode,
    rejected,
    boost_key: boostKey || undefined,
    date_meta: dateMeta || undefined,
    seen,
  });
}
```

- [ ] **Step 2: Update `lib/track.ts`**

Add trail events:
```typescript
export type TrailEvent =
  | ...
  | "seen_cues_shown"
  | "seen_cue_picked"
  | "seen_cue_removed";
```

- [ ] **Step 3: Commit**

```bash
git add webapp/apps/web/lib/api.ts webapp/apps/web/lib/track.ts
git commit -m "feat(web): add CueSuggestion types and visual cue tracking events"
```

---

### Task 5: Component Implementations (`SeenCues.tsx`, `ClueChip.tsx`, `NotHere.tsx`, `NoMatch.tsx`, `SearchView.tsx`, `globals.css`)

**Files:**
- Create: `webapp/apps/web/app/components/SeenCues.tsx`
- Modify: `webapp/apps/web/app/components/ClueChip.tsx`
- Modify: `webapp/apps/web/app/components/NotHere.tsx`
- Modify: `webapp/apps/web/app/components/NoMatch.tsx`
- Modify: `webapp/apps/web/app/components/SearchView.tsx`
- Modify: `webapp/apps/web/app/globals.css`

**Interfaces:**
- Consumes: `CueSuggestion`, `track`
- Produces: Reusable `SeenCues` component, updated copy in `SearchView`, updated `clueKind("seen")`.

- [ ] **Step 1: Create `webapp/apps/web/app/components/SeenCues.tsx`**

```tsx
"use client";

import { useEffect, useRef } from "react";
import type { CueSuggestion } from "@/lib/api";
import { track } from "@/lib/track";

export function SeenCues({
  cues,
  surface,
  onPick,
}: {
  cues: CueSuggestion[];
  surface: "not_here" | "no_match";
  onPick: (label: string, rank: number) => void;
}) {
  const trackedRef = useRef(false);

  useEffect(() => {
    if (cues.length > 0 && !trackedRef.current) {
      trackedRef.current = true;
      track("seen_cues_shown", {
        labels: cues.map((c) => c.label),
        surface,
      });
    }
  }, [cues, surface]);

  if (!cues || cues.length === 0) return null;

  const topCue = cues[0];

  return (
    <div className="seen-cues" aria-label="Visual detail suggestions">
      <div className="seen-cues-title">Try something you'd have seen</div>
      <div className="seen-cues-support">
        Seen in {topCue.seen_in} of the {topCue.of} closest photos
      </div>
      <div className="seen-cues-chips">
        {cues.map((cue, idx) => (
          <button
            key={cue.label}
            className="seen-cue-chip"
            onClick={() => onPick(cue.label, idx)}
            title={`Seen in ${cue.seen_in} of ${cue.of} photos`}
          >
            <span>{cue.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Update `ClueChip.tsx`**

Add `if (cue === "seen") return "Something you saw";` inside `clueKind`.

- [ ] **Step 3: Update `NotHere.tsx`**

Accept `cues?: CueSuggestion[]` and `onPickSeen?: (label: string, rank: number) => void`.
Render `SeenCues` inside the open panel, above "Show the next N moments".

- [ ] **Step 4: Update `NoMatch.tsx`**

Accept `cues?: CueSuggestion[]` and `onPickSeen?: (label: string, rank: number) => void`.
Render `SeenCues` above "Keep the memory and try one small change".

- [ ] **Step 5: Update `SearchView.tsx` handoff copy**

In lines 198-206:
Replace `"who was there"` with `"what you'd have seen — a colour, what someone wore"`.

- [ ] **Step 6: Add styles in `globals.css`**

Add `.seen-cues`, `.seen-cues-title`, `.seen-cues-support`, `.seen-cues-chips`, `.seen-cue-chip`.

- [ ] **Step 7: Commit**

```bash
git add webapp/apps/web/app/components/SeenCues.tsx \
        webapp/apps/web/app/components/ClueChip.tsx \
        webapp/apps/web/app/components/NotHere.tsx \
        webapp/apps/web/app/components/NoMatch.tsx \
        webapp/apps/web/app/components/SearchView.tsx \
        webapp/apps/web/app/globals.css
git commit -m "feat(web): add SeenCues component, update NotHere, NoMatch and SearchView"
```

---

### Task 6: Wire `seen` State & Interactions in `MemoryTrails.tsx`

**Files:**
- Modify: `webapp/apps/web/app/components/MemoryTrails.tsx`

**Interfaces:**
- Consumes: `SeenCues`, `api.search(..., seen)`
- Produces: Interactive visual-cue adding, removal, undo, and confirmation analytics.

- [ ] **Step 1: Add `seen` state and connect to `runSearch`**

In `MemoryTrails.tsx`:
```typescript
const [seen, setSeen] = useState<string[]>([]);
```
Pass `seen` to `search(text, f, m, skip, boostKey, dateMetaFor(chips, f.date_from), s)` where `s = seen`.
Ensure `runSearch(f, m, skip, st, s = seen)` accepts `s`.

- [ ] **Step 2: Implement `onPickSeen` and undo**

```typescript
function onPickSeen(label: string, rank: number) {
  if (seen.length >= 3 || seen.includes(label)) return;
  track("seen_cue_picked", { label, rank });
  const nextSeen = [...seen, label];
  setSeen(nextSeen);
  const seenChip: Chip = {
    id: `seen_${label}`,
    cue: "seen",
    label: label,
    filter_key: "seen",
    value: label,
    editable: false,
  };
  setChips((prev) => [...prev, seenChip]);
  setNotice(`Added ‘${label}’. Undo`);
  void runSearch(filters, mode, rejected, strength, nextSeen);
}
```

- [ ] **Step 3: Handle chip removal and undo for seen cues**

In `onRemoveChip`:
```typescript
if (chip.cue === "seen" || chip.filter_key === "seen") {
  track("seen_cue_removed", { label: chip.label });
  const nextSeen = seen.filter((s) => s !== chip.label);
  setSeen(nextSeen);
  setChips((prev) => prev.filter((c) => c.id !== chip.id));
  void runSearch(filters, mode, rejected, strength, nextSeen);
  return;
}
```
And handle clicking Undo on the notification:
Revert the added seen cue and rerun search.

- [ ] **Step 4: Update `restart()` and `track("retrieval_confirmed")`**

In `restart()`: add `setSeen([])`.
In `track("retrieval_confirmed", { photo_id: photoId, seen })`: pass `seen`.

- [ ] **Step 5: Pass `cues` and `onPickSeen` to `NotHere` and `NoMatch`**

In `NotHere`: pass `cues={result?.cue_suggestions ?? []}` and `onPickSeen={onPickSeen}`.
In `NoMatch`: pass `cues={result?.cue_suggestions ?? []}` and `onPickSeen={onPickSeen}`.

- [ ] **Step 6: Commit**

```bash
git add webapp/apps/web/app/components/MemoryTrails.tsx
git commit -m "feat(web): wire up visual cues state, undo, and analytics in MemoryTrails"
```

---

### Task 7: Full Test Suite and Verification

**Files:**
- Tests across backend and frontend

- [ ] **Step 1: Run all Python tests**
Run: `.venv/bin/pytest webapp/apps/retrieval/tests`
Expected: All tests pass (including `test_cues.py` and new `test_api.py` tests).

- [ ] **Step 2: Run Next.js / TypeScript build verification**
Run: `npm run build` in `webapp/apps/web`
Expected: Clean compilation with 0 TypeScript or lint errors.

- [ ] **Step 3: Verification of evaluation script**
Run: `.venv/bin/python -m engine.demo_eval --strategy soft+seen_oracle --tasks synthetic`
Expected: Successfully regenerates simulation metrics.
