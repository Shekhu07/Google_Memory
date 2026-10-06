# Memory Trails UX & Retrieval Engine Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix Memory Trails clue extraction, ranking priority, Time Ribbon synchronization, and UI transparency issues identified in the product UX review.

**Architecture:** 
- In the Python retrieval backend, update `infer_clues` in `clues.py` to extract all detected category words (e.g. "cafe", "dosa"), emit the primary category in active filters and others in `suggested_categories`, deduplicate nested categories, and prioritize `clue_hits` before episode usefulness in `search.py`.
- In the Next.js frontend, display staged category suggestion chips in Recap, center the Time Ribbon on the active memory date window (or retitle to "Browse months" if undated), highlight full-match candidate cards, and resolve UI polish items (formatted dates, simplified evidence labels, breadcrumb kind tags, ruled-out undo, and relocated disclaimer).

**Tech Stack:** Next.js 16 (React 19, TypeScript), Vanilla CSS, FastAPI (Python 3.12), NumPy, Pytest.

## Global Constraints

- Do not break existing API contracts: `/api/py/extract`, `/api/py/search`, `/api/py/facets`, `/api/py/episode`.
- Retain all 120 existing tests passing in `webapp/apps/retrieval`.
- Build must compile cleanly with `npm run build` in `webapp/apps/web` (no TypeScript or Turbopack errors).
- All dates displayed to users must be formatted in natural language (e.g., "31 Mar – 29 Jun 2026"), never raw ISO dates.
- Pin prototype today at `2026-09-23`.

---

### Task 1: Multi-Category Extraction & Clue Deduplication

**Files:**
- Modify: `webapp/apps/retrieval/clues.py:635-676`
- Modify: `webapp/apps/retrieval/llm_clues.py:60-86`
- Test: `webapp/apps/retrieval/tests/test_clues.py`

**Interfaces:**
- Consumes: `facets.categories`, text query string.
- Produces: `extract_clues` returns `{"filters": filters, "chips": chips, "suggested_categories": [...], "source": "rules"}` where `suggested_categories` is `list[dict]` containing `{"category": str, "word": str, "label": str}`.

- [ ] **Step 1: Write failing tests for multi-category extraction & deduplication**

Add tests to `webapp/apps/retrieval/tests/test_clues.py`:

```python
def test_extract_multi_category_suggestions():
    from clues import extract_clues
    from facets import load_facets
    from tests.test_clues import DUMMY_FACETS, TODAY
    
    # "cafe in Bengaluru with friends... dosa on the table" has friends, cafe, dosa
    text = "I was at a cafe in Bengaluru with friends around late May, there was a dosa on the table"
    res = extract_clues(text, DUMMY_FACETS, TODAY)
    
    # Primary category filter should be present
    assert "category" in res["filters"]
    # Suggestions should capture the other scene words
    suggested = [s["category"] for s in res.get("suggested_categories", [])]
    all_cats = [res["filters"]["category"]] + suggested
    assert "cafe" in all_cats
    assert "dosa" in all_cats
    assert "friends" in all_cats

def test_dedupe_overlapping_categories():
    from clues import extract_clues
    from facets import load_facets
    from tests.test_clues import DUMMY_FACETS, TODAY
    
    # If text has both "college performance" and "performance", avoid duplicate chips
    text = "the group photo after our college performance"
    res = extract_clues(text, DUMMY_FACETS, TODAY)
    cat_chips = [c for c in res["chips"] if c["filter_key"] == "category"]
    assert len(cat_chips) <= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
/Users/abhishekspillai/Google\ CaseStudy/.venv/bin/pytest webapp/apps/retrieval/tests/test_clues.py -k "test_extract_multi_category_suggestions or test_dedupe_overlapping_categories" -v
```
Expected: FAIL because `suggested_categories` is not produced.

- [ ] **Step 3: Implement multi-category collection & deduplication in `clues.py`**

In `webapp/apps/retrieval/clues.py` (around lines 636-658):
```python
    # Step 4: Category matching
    fest_anchor = _festival_dates(low, today, matched_ep=filters.get("episode"))
    synonyms = {c.lower(): c for c in facets.categories}
    synonyms.update(CATEGORY_SYNONYMS)
    hits = []
    for word in sorted(synonyms, key=len, reverse=True):
        cat = synonyms[word]
        if cat in facets.categories and re.search(rf"\b{re.escape(word)}\b", low):
            if fest_anchor and cat == "festival":
                continue
            hits.append((word, cat))

    suggested_categories = []
    if hits:
        ep = filters.get("episode", "")
        ep_words = " ".join([ep] + EPISODE_ALIASES.get(ep, [])) if ep else ""
        fresh = [h for h in hits if not (ep_words and re.search(rf"\b{re.escape(h[0])}\b", ep_words))]
        target_hits = fresh or hits
        
        # Deduplicate hits by category and filter out sub-word overlaps
        seen_cats = []
        for word, cat in target_hits:
            if cat not in [c for _, c in seen_cats]:
                # Check for redundant substrings
                if not any(word in prev_word and word != prev_word for prev_word, _ in seen_cats):
                    seen_cats.append((word, cat))

        if seen_cats:
            primary_word, primary_cat = seen_cats[0]
            n += 1
            filters["category"] = primary_cat
            chips.append(_chip(n, "object", CATEGORY_LABELS.get(primary_cat, primary_cat), "category", primary_cat))
            
            # Secondary matches become suggested categories
            for extra_word, extra_cat in seen_cats[1:]:
                suggested_categories.append({
                    "category": extra_cat,
                    "word": extra_word,
                    "label": CATEGORY_LABELS.get(extra_cat, extra_cat),
                })
```
Return `suggested_categories` in `extract_clues`:
```python
    return {"filters": filters, "chips": chips, "suggested_categories": suggested_categories, "source": "rules"}
```

Also update `llm_clues.py` so that any fallback or rules dictionary preserves `suggested_categories`:
```python
        return {"filters": filters, "chips": chips, "suggested_categories": fallback.get("suggested_categories", []), "source": "llm", "notice": None}
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
/Users/abhishekspillai/Google\ CaseStudy/.venv/bin/pytest webapp/apps/retrieval/tests/test_clues.py -v
```
Expected: PASS for all tests in `test_clues.py`.

- [ ] **Step 5: Commit Task 1**

```bash
git add webapp/apps/retrieval/clues.py webapp/apps/retrieval/llm_clues.py webapp/apps/retrieval/tests/test_clues.py
git commit -m "feat(retrieval): extract multiple scene keywords and deduplicate category clues"
```

---

### Task 2: Ranking Priority by `clue_hits`

**Files:**
- Modify: `webapp/apps/retrieval/search.py:223-246`
- Test: `webapp/apps/retrieval/tests/test_search.py`

**Interfaces:**
- Consumes: `groups` dictionary, `filters`.
- Produces: `group_by_episode()` sets `g["clue_hits"]` and `g["full_match"]`, sorting by `(-g["clue_hits"], -g["usefulness"], -g["top_score"])`.

- [ ] **Step 1: Write failing test in `test_search.py`**

Add test in `webapp/apps/retrieval/tests/test_search.py`:

```python
def test_group_by_episode_prioritizes_clue_hits_over_richness():
    from search import group_by_episode
    
    records = [
        # Big episode with 5 photos, but only matches location and date, NOT category
        {"id": "p1", "episode_id": "ep1", "episode": "Big Event", "location": "Bengaluru", "date": "2026-05-10", "category": "office"},
        {"id": "p2", "episode_id": "ep1", "episode": "Big Event", "location": "Bengaluru", "date": "2026-05-11", "category": "office"},
        {"id": "p3", "episode_id": "ep1", "episode": "Big Event", "location": "Bengaluru", "date": "2026-05-12", "category": "office"},
        # Singleton photo matching ALL 3 clues: Bengaluru, cafe, May 2026
        {"id": "s1", "episode_id": "", "episode": "", "location": "Bengaluru", "date": "2026-05-15", "category": "cafe"},
    ]
    scored = [("p1", 0.8), ("p2", 0.79), ("p3", 0.78), ("s1", 0.75)]
    filters = {
        "location": "Bengaluru",
        "category": "cafe",
        "date_from": "2026-05-01",
        "date_to": "2026-05-31",
    }
    
    groups = group_by_episode(scored, records, filters=filters)
    # The singleton photo matches all clues (clue_hits = 1), so it must rank FIRST
    assert groups[0]["clue_hits"] == 1
    assert groups[0]["full_match"] is True
    assert groups[0]["photos"][0]["id"] == "s1"
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
/Users/abhishekspillai/Google\ CaseStudy/.venv/bin/pytest webapp/apps/retrieval/tests/test_search.py -k "test_group_by_episode_prioritizes_clue_hits_over_richness" -v
```
Expected: FAIL because sorting prioritizes `usefulness` over `clue_hits`.

- [ ] **Step 3: Update `group_by_episode` in `search.py`**

In `webapp/apps/retrieval/search.py` (lines 230-246):
```python
    for g in groups.values():
        rows = [by_id[p["id"]] for p in g["photos"] if p["id"] in by_id]
        ledger = match_ledger(rows, filters)
        matched_dims = sum(1 for item in ledger if item.get("matched"))
        filter_cover = (matched_dims / len(dims)) if dims else 1.0
        semantic = max(0.0, g["top_score"]) / best if best else 0.0
        coverage = 0.5 * filter_cover + 0.5 * semantic
        c_hits = clue_hits(rows, filters)
        g["clue_hits"] = c_hits
        g["full_match"] = bool(c_hits > 0 and len(dims) > 0 and matched_dims == len(dims))
        g["usefulness"] = round(usefulness(
            coverage,
            _coherence(bool(g["episode_id"]), g.get("span_days", 0)),
            min(1.0, 0.4 + 0.15 * c_hits) if c_hits > 0 else _recognizability(g["episode_total"]),
            min(1.0, 0.6 + 0.1 * matched_dims),
        ), 4)

    return sorted(groups.values(), key=lambda g: (-g["clue_hits"], -g["usefulness"], -g["top_score"]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
/Users/abhishekspillai/Google\ CaseStudy/.venv/bin/pytest webapp/apps/retrieval/tests/test_search.py -v
```
Expected: PASS for all tests.

- [ ] **Step 5: Commit Task 2**

```bash
git add webapp/apps/retrieval/search.py webapp/apps/retrieval/tests/test_search.py
git commit -m "fix(retrieval): rank candidates by clue_hits before episode usefulness"
```

---

### Task 3: Time Ribbon Temporal Centering & Contextual Retitle

**Files:**
- Modify: `webapp/apps/web/app/components/TimeRibbon.tsx:1-89`
- Modify: `webapp/apps/web/lib/api.ts` (type updates)

**Interfaces:**
- Consumes: `chapters: MonthlyChapter[]`, `activeDateFrom?: string | null`, `activeDateTo?: string | null`, `onShift`.
- Produces: Centered scroll container on mount/change, fallback label `"Browse months"` when undated.

- [ ] **Step 1: Update API type definitions in `lib/api.ts`**

In `webapp/apps/web/lib/api.ts`:
Add `full_match?: boolean` to `Episode`.
Add `suggested_categories?: { category: string; word: string; label?: string }[]` to `ExtractResult`.

- [ ] **Step 2: Implement auto-centering & title logic in `TimeRibbon.tsx`**

In `webapp/apps/web/app/components/TimeRibbon.tsx`:
Add a `scrollRef = useRef<HTMLDivElement>(null)` and `useEffect`:
```tsx
  const scrollRef = useRef<HTMLDivElement>(null);

  // Determine active index based on activeDateFrom or activeDateTo
  let activeIndex = -1;
  const targetDate = activeDateFrom || activeDateTo;
  if (targetDate) {
    const activeMonth = targetDate.slice(0, 7);
    activeIndex = chapters.findIndex((c) => c.month === activeMonth);
  }

  const hasDateClue = Boolean(targetDate);
  const title = hasDateClue ? "Around that time" : "Browse months";
  const subtitle = hasDateClue
    ? "Shift to nearby months to explore surrounding moments"
    : "Explore moments across the library timeline";

  useEffect(() => {
    if (activeIndex >= 0 && scrollRef.current) {
      const activeEl = scrollRef.current.children[activeIndex] as HTMLElement | undefined;
      if (activeEl) {
        const container = scrollRef.current;
        const scrollLeft = activeEl.offsetLeft - container.clientWidth / 2 + activeEl.clientWidth / 2;
        container.scrollTo({ left: Math.max(0, scrollLeft), behavior: "smooth" });
      }
    }
  }, [activeIndex]);
```
Attach `ref={scrollRef}` to `<div className="ribbon-scroll" role="list">`.
Use `{title}` and `{subtitle}` in `.ribbon-title-wrap`.

- [ ] **Step 3: Verify build**

Run:
```bash
npm run build --prefix webapp/apps/web
```
Expected: Build passes with no TypeScript or Turbopack errors.

- [ ] **Step 4: Commit Task 3**

```bash
git add webapp/apps/web/lib/api.ts webapp/apps/web/app/components/TimeRibbon.tsx
git commit -m "feat(ui): center TimeRibbon on active date window and retitle when undated"
```

---

### Task 4: Moments Full-Match Prominence & Singleton Card Parity

**Files:**
- Modify: `webapp/apps/web/app/components/Moments.tsx`
- Modify: `webapp/apps/web/app/globals.css` (badge styling)

**Interfaces:**
- Consumes: `Episode.full_match`, `Episode.clue_hits`.
- Produces: "Matches all your clues" top badge on matching cards, clickable singletons with "View moment".

- [ ] **Step 1: Update `sequenceNote` and card rendering in `Moments.tsx`**

In `webapp/apps/web/app/components/Moments.tsx`:
1. Highlight cards matching all clues:
```tsx
const isFullMatch = ep.full_match || (ep.clue_hits !== undefined && ep.clue_hits > 0);
```
2. Render full match badge above title:
```tsx
{isFullMatch && (
  <span className="full-match-badge" aria-label="Matches all your clues">
    ✓ Matches all your clues
  </span>
)}
```
3. Make singletons (unnamed cards) clickable to open the moment view:
Change `onClick={() => named && onOpen(ep)}` to `onClick={() => onOpen(ep)}`
Update footer action button to show for both named and singletons:
```tsx
<div className="foot">
  <button className="btn ghost moment-open-btn" onClick={() => onOpen(ep)}>
    <span>View {named ? "moment" : "photo"}</span>
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M9 18l6-6-6-6" />
    </svg>
  </button>
</div>
```

- [ ] **Step 2: Add CSS rules for `.full-match-badge` in `globals.css`**

In `webapp/apps/web/app/globals.css`:
```css
.full-match-badge {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-green, #137333);
  background: var(--color-green-light, #e6f4ea);
  padding: 2px 8px;
  border-radius: 12px;
  margin-bottom: 4px;
}
```

- [ ] **Step 3: Run build to verify compilation**

Run:
```bash
npm run build --prefix webapp/apps/web
```
Expected: Build succeeds.

- [ ] **Step 4: Commit Task 4**

```bash
git add webapp/apps/web/app/components/Moments.tsx webapp/apps/web/app/globals.css
git commit -m "feat(ui): highlight full-match moments and enable interaction on singleton cards"
```

---

### Task 5: Staged Category Suggestions in Recap

**Files:**
- Modify: `webapp/apps/web/app/components/MemoryTrails.tsx:720-760`
- Modify: `webapp/apps/web/app/globals.css`

**Interfaces:**
- Consumes: `ExtractResult.suggested_categories`.
- Produces: Interactive suggestion chips below clue chips in Recap: `"I also heard: [ + cafe ] [ + dosa ]"`. Tapping a suggestion adds it as an active clue or switches category.

- [ ] **Step 1: Store `suggestedCategories` state and render in `MemoryTrails.tsx`**

In `webapp/apps/web/app/components/MemoryTrails.tsx`:
1. Add state: `const [suggestedCategories, setSuggestedCategories] = useState<{ category: string; word: string; label?: string }[]>([]);`
2. In `runExtract()`, set `setSuggestedCategories(extracted.suggested_categories || []);`.
3. In Recap stage (`stage === "recap"`), render the suggestion bar:
```tsx
{suggestedCategories.length > 0 && (
  <div className="suggested-clues-bar" aria-label="Suggested clues heard from your memory">
    <span className="t-support">I also heard:</span>
    <div className="suggested-chips">
      {suggestedCategories.map((s) => (
        <button
          key={s.category}
          type="button"
          className="suggested-chip-btn"
          onClick={() => {
            const newFilters = { ...filters, category: s.category };
            setFilters(newFilters);
            const newChip: Chip = {
              id: `c_cat_${Date.now()}`,
              cue: "object",
              label: s.label || s.category,
              filter_key: "category",
              value: s.category,
              editable: true,
            };
            setChips((prev) => [...prev.filter((c) => c.filter_key !== "category"), newChip]);
            setSuggestedCategories((prev) => prev.filter((item) => item.category !== s.category));
          }}
        >
          + {s.label || s.category}
        </button>
      ))}
    </div>
  </div>
)}
```

- [ ] **Step 2: Add CSS for `.suggested-clues-bar` in `globals.css`**

Add styling matching Google Photos design system with chip hover and focus states.

- [ ] **Step 3: Run build to verify compilation**

Run:
```bash
npm run build --prefix webapp/apps/web
```
Expected: Build succeeds.

- [ ] **Step 4: Commit Task 5**

```bash
git add webapp/apps/web/app/components/MemoryTrails.tsx webapp/apps/web/app/globals.css
git commit -m "feat(ui): display staged scene suggestions in Recap flow"
```

---

### Task 6: UI Polish & Transparency Fixes

**Files:**
- Modify: `webapp/apps/web/app/components/Moments.tsx:30-35, 110-125`
- Modify: `webapp/apps/web/app/components/Breadcrumb.tsx:20-35`
- Modify: `webapp/apps/web/app/components/MemoryTrails.tsx:810-830, 935-970, 1020`
- Modify: `webapp/apps/web/app/components/Viewer.tsx` (pinch-to-zoom)
- Modify: `webapp/apps/web/app/components/Disclaimer.tsx`

**Interfaces:**
- Evidence panel formats ISO date ranges nicely.
- Jargon tag "IN THE FIRST PHOTO" reworded to "from the place recorded on the first photo".
- Breadcrumbs show clue kinds (`clueKind(c.cue)`).
- Ruled-out moments notice includes an active `Undo` button.
- Persistent disclaimer footer removed from workflow sheets; kept in compose/info modal.
- Yes/Partly/No survey deferred until after "Done".
- Viewer touch handler tracks pinch distance for pinch-to-zoom.

- [ ] **Step 1: Fix Evidence date formatting and jargon in `Moments.tsx`**

In `webapp/apps/web/app/components/Moments.tsx`:
1. Change `direct` wording in `SCOPE_WORDS`:
```tsx
const SCOPE_WORDS: Record<string, string> = {
  direct: "from the place recorded on the first photo",
  nearby: "in nearby photos",
  approximate: "approximate",
};
```
2. In `Evidence` component, format date values:
```tsx
const val = d.dimension === "Date" && d.value.includes("-")
  ? formatWindow(d.value.split(" to ")[0], d.value.split(" to ")[1] || null)
  : (d.dimension === "Scene" ? CATEGORY_WORDS[d.value] ?? d.value : d.value);
```

- [ ] **Step 2: Update `Breadcrumb.tsx` with clue kinds**

Import `clueKind` from `ClueChip` and display `{c.label} · {clueKind(c.cue)}` inside the breadcrumb.

- [ ] **Step 3: Update `MemoryTrails.tsx` (Ruled-out undo, Survey deferral, Disclaimer removal)**

1. Make "Not showing X moments you ruled out" interactive:
```tsx
{rejected.length > 0 && (
  <p className="t-support undo-row">
    Not showing {rejected.length} moment{rejected.length === 1 ? "" : "s"} you ruled out.
    <button className="btn quiet" onClick={() => setRejected([])}>
      Restore
    </button>
  </p>
)}
```
2. Remove `<Disclaimer />` from bottom of `MemoryTrails.tsx` (line 1021). Render it only on the initial compose stage or inside an info button/modal in the header.
3. In `confirmed` stage, show "Done" and summary; move survey to after clicking "Done" or an optional feedback card.

- [ ] **Step 4: Add touch pinch-to-zoom in `Viewer.tsx`**

In `webapp/apps/web/app/components/Viewer.tsx`, handle multi-touch distance (`e.touches.length === 2`) to scale the image transform smoothly.

- [ ] **Step 5: Verify build & tests**

Run:
```bash
npm run build --prefix webapp/apps/web
/Users/abhishekspillai/Google\ CaseStudy/.venv/bin/pytest webapp/apps/retrieval
```
Expected: Both pass completely.

- [ ] **Step 6: Commit Task 6**

```bash
git add webapp/apps/web/app/components/Moments.tsx webapp/apps/web/app/components/Breadcrumb.tsx webapp/apps/web/app/components/MemoryTrails.tsx webapp/apps/web/app/components/Viewer.tsx webapp/apps/web/app/components/Disclaimer.tsx
git commit -m "fix(ui): format evidence dates, simplify jargon, restore ruled-out moments, and add pinch-zoom"
```

---

### Task 7: Full End-to-End Verification

**Files:**
- Test: Full Pytest test suite
- Test: Next.js production build

- [ ] **Step 1: Execute all Python unit & integration tests**

```bash
/Users/abhishekspillai/Google\ CaseStudy/.venv/bin/pytest webapp/apps/retrieval -v
```
Expected: All tests pass.

- [ ] **Step 2: Execute Next.js build**

```bash
npm run build --prefix webapp/apps/web
```
Expected: Turbopack production compilation succeeds with 0 errors.

- [ ] **Step 3: Commit final plan completion**

```bash
git commit --allow-empty -m "chore: verify all Memory Trails fixes pass tests and build"
```
