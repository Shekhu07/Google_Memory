# Memory Trails on Vercel — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy one Vercel project carrying both public links — a functional Memory Trails MVP over the real 494-image CLIP index, and the engine evidence demo — and produce the MVP's first *measured* recall@20.

**Architecture:** Vercel Services: a Next.js front end (`apps/web`) and a FastAPI Python service (`apps/retrieval`) in one atomically-deployed project. The Python service reuses the already-tested `engine/` retrieval code so the live demo and the deck cannot diverge. All heavy computation (image embedding, evidence tables, ONNX export) happens locally via an export script; Vercel's build installs only `fastapi`, `numpy`, `onnxruntime`.

**Tech Stack:** Next.js (App Router, TypeScript), FastAPI, numpy, onnxruntime, Vercel Services, pytest, Playwright.

**Spec:** `docs/superpowers/specs/2026-09-20-vercel-deployment-design.md`

## Global Constraints

- **Anonymity:** the user's name appears nowhere — not in the project name, page text, repo, or metadata. Project name is `memory-trails-demo`. The deck cites the **production alias only**; preview URLs embed the account slug.
- **Filter contract:** exactly five optional keys — `date_from`, `date_to`, `location`, `category`, `episode`. `category` is **exact equality**; `location` and `episode` are **case-insensitive substring**; dates are an inclusive window. Source of truth: `engine/demo_index.apply_filters`.
- **`VAGUE_WINDOW_DAYS = 45`** (from `engine/demo_eval.py`) — the ± window for `temporal_approx`.
- **Chips carry `label` AND `value` separately.** `label` is display text; `value` reaches `apply_filters`. Never collapse them.
- **Filters are client-authoritative after chip edits.** The server must not re-derive filters from `text`.
- **Why-strings are evidence labels only** — which filter fired, on what value. Never a generated rationale.
- **Never log or persist visitor-typed text.**
- **Groq:** free tier, 190K tokens/day per model, resets 05:30 IST. Demo model stays off the pipeline's models. Every LLM path must degrade to rules.
- **The existing 150 tests in `tests/` stay green after every task.**
- **Library facts (verified 21 Sep):** 494 images · 12 categories (`cafe, beach, food, street, receipt, medicine, mountain, wedding, pet, whiteboard, document, festival`) · 12 locations (`Bengaluru, Chennai, Kochi, Mumbai, Goa, Manali, Mysuru, Pondicherry, Alleppey, Coorg, Jaipur, Hyderabad`) · 25 named episodes + 262 stray · dates 2023-11-02 → 2026-05-15.
- **Index:** `data/demo/index.npz` holds `ids` and a **pre-normalised** `matrix`. `demo_index.rank()` normalises again internally, so raw encoder output is acceptable.

---

## File Structure

| Path | Responsibility |
|---|---|
| `webapp/vercel.json` | Services definition + ordered public rewrites |
| `webapp/apps/retrieval/facets.py` | Load library; derive location/episode/category vocab + episode date windows |
| `webapp/apps/retrieval/clues.py` | **Rule-based** text → filters + chips. Pure, `today` injectable |
| `webapp/apps/retrieval/encoder.py` | ONNX CLIP text-tower wrapper |
| `webapp/apps/retrieval/search.py` | Filtered/baseline search, episode grouping, why-strings |
| `webapp/apps/retrieval/llm_clues.py` | Groq extraction + fallback to `clues.py` |
| `webapp/apps/retrieval/main.py` | FastAPI: `/extract`, `/search`, `/health` |
| `webapp/apps/retrieval/tests/` | pytest for the above |
| `webapp/apps/web/app/page.tsx` | MVP surface |
| `webapp/apps/web/app/evidence/page.tsx` | Evidence surface (3 tabs) |
| `webapp/apps/web/app/attribution/page.tsx` | CC credits |
| `engine/export_web.py` | Build-time artifact export (runs locally) |
| `engine/demo_eval.py` (modify) | Add the `inferred` strategy |

---

### Task 0: Repository and project scaffold

**Files:**
- Create: `webapp/vercel.json`, `webapp/apps/retrieval/requirements.txt`, `webapp/.gitignore`

**Interfaces:**
- Produces: the `webapp/` root every later task writes into.

> **Flag for the user:** this project is **not currently a git repository**. This plan's TDD cycle commits after every task. Step 1 runs `git init`. If the user prefers no version control, skip step 1 and drop every commit step.

- [ ] **Step 1: Initialise git**

```bash
cd "/Users/abhishekspillai/Google CaseStudy"
git init
git add .gitignore
git commit -m "chore: initialise repository"
```

- [ ] **Step 2: Create the service layout**

```bash
mkdir -p webapp/apps/retrieval/tests webapp/apps/retrieval/data webapp/apps/web
```

- [ ] **Step 3: Write `webapp/vercel.json`**

```json
{
  "services": {
    "web":       { "root": "apps/web" },
    "retrieval": {
      "root": "apps/retrieval",
      "entrypoint": "main:app",
      "rewrites": [{ "source": "/api/py/:path(.*)?", "destination": "/:path" }]
    }
  },
  "rewrites": [
    { "source": "/api/py/(.*)", "destination": { "service": "retrieval" } },
    { "source": "/(.*)",        "destination": { "service": "web" } }
  ]
}
```

- [ ] **Step 4: Write `webapp/apps/retrieval/requirements.txt`**

```
fastapi==0.120.4
numpy==2.5.3
onnxruntime==1.24.0
tokenizers==0.23.1
requests==2.34.2
```

- [ ] **Step 5: Write `webapp/.gitignore`**

```
node_modules/
.next/
.vercel/
__pycache__/
*.pyc
```

- [ ] **Step 6: Commit**

```bash
git add webapp/
git commit -m "feat: scaffold vercel services project"
```

---

### Task 1: Facet vocabulary

**Files:**
- Create: `webapp/apps/retrieval/facets.py`
- Test: `webapp/apps/retrieval/tests/test_facets.py`

**Interfaces:**
- Produces: `load_facets(library: list[dict]) -> Facets` where `Facets` is a dataclass with `locations: list[str]`, `episodes: list[str]`, `categories: list[str]`, `episode_windows: dict[str, tuple[str, str]]` (episode name → inclusive ISO date range).

- [ ] **Step 1: Write the failing test**

```python
# webapp/apps/retrieval/tests/test_facets.py
from facets import load_facets

LIB = [
    {"id": "a", "category": "cafe",   "location": "Goa",       "episode": "goa trip", "date": "2023-12-14T10:00:00"},
    {"id": "b", "category": "food",   "location": "Goa",       "episode": "goa trip", "date": "2023-12-18T10:00:00"},
    {"id": "c", "category": "receipt","location": "Bengaluru", "episode": "",         "date": "2024-02-21T10:00:00"},
]

def test_collects_distinct_values_sorted():
    f = load_facets(LIB)
    assert f.locations == ["Bengaluru", "Goa"]
    assert f.categories == ["cafe", "food", "receipt"]
    assert f.episodes == ["goa trip"]

def test_blank_episode_is_not_a_facet():
    assert "" not in load_facets(LIB).episodes

def test_episode_window_spans_first_to_last_photo():
    assert load_facets(LIB).episode_windows["goa trip"] == ("2023-12-14", "2023-12-18")
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_facets.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'facets'`

- [ ] **Step 3: Implement**

```python
# webapp/apps/retrieval/facets.py
"""Vocabulary the rule-based extractor matches against, derived from the library itself."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Facets:
    locations: list
    episodes: list
    categories: list
    episode_windows: dict


def load_facets(library: list) -> Facets:
    locations, episodes, categories, windows = set(), set(), set(), {}
    for r in library:
        if r.get("location"):
            locations.add(r["location"])
        if r.get("category"):
            categories.add(r["category"])
        ep = r.get("episode") or ""
        if ep:
            episodes.add(ep)
            day = (r.get("date") or "")[:10]
            if day:
                lo, hi = windows.get(ep, (day, day))
                windows[ep] = (min(lo, day), max(hi, day))
    return Facets(sorted(locations), sorted(episodes), sorted(categories), windows)
```

- [ ] **Step 4: Run and confirm green**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_facets.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add webapp/apps/retrieval/facets.py webapp/apps/retrieval/tests/test_facets.py
git commit -m "feat(retrieval): derive facet vocabulary from the library"
```

---

### Task 2: Rule-based clue extractor

This is the heart of the build — the only genuinely new retrieval logic. It must emit the five-key filter dict from text alone.

**Files:**
- Create: `webapp/apps/retrieval/clues.py`
- Test: `webapp/apps/retrieval/tests/test_clues.py`

**Interfaces:**
- Consumes: `facets.Facets` (Task 1).
- Produces: `extract_clues(text: str, facets: Facets, today: date) -> dict` returning `{"filters": dict, "chips": list[dict], "source": "rules"}`. Each chip is `{"id", "cue", "label", "filter_key", "value", "editable": True}`.

- [ ] **Step 1: Write the failing test**

```python
# webapp/apps/retrieval/tests/test_clues.py
from datetime import date
from clues import extract_clues
from facets import load_facets

LIB = [
    {"id": "a", "category": "cafe",     "location": "Goa",       "episode": "goa trip",  "date": "2023-12-14T10:00:00"},
    {"id": "b", "category": "food",     "location": "Goa",       "episode": "goa trip",  "date": "2023-12-18T10:00:00"},
    {"id": "c", "category": "medicine", "location": "Bengaluru", "episode": "fever week","date": "2024-02-21T10:00:00"},
]
F = load_facets(LIB)
TODAY = date(2026, 9, 21)


def chips_by_key(res):
    return {c["filter_key"]: c for c in res["chips"]}


def test_exact_date_pins_both_ends():
    r = extract_clues("on 2024-07-15", F, TODAY)
    assert r["filters"]["date_from"] == "2024-07-15"
    assert r["filters"]["date_to"] == "2024-07-15"
    assert chips_by_key(r)["date_from"]["cue"] == "exact_date"


def test_month_and_year_becomes_that_month():
    r = extract_clues("in July 2025", F, TODAY)
    assert r["filters"]["date_from"] == "2025-07-01"
    assert r["filters"]["date_to"] == "2025-07-31"


def test_last_year_is_the_previous_calendar_year():
    r = extract_clues("the photo from last year", F, TODAY)
    assert r["filters"]["date_from"] == "2025-01-01"
    assert r["filters"]["date_to"] == "2025-12-31"


def test_location_matches_library_vocabulary_case_insensitively():
    r = extract_clues("our goa trip", F, TODAY)
    assert r["filters"]["location"] == "Goa"
    assert chips_by_key(r)["location"]["cue"] == "place_named"


def test_category_uses_exact_value_not_the_display_label():
    r = extract_clues("that little cafe we found", F, TODAY)
    chip = chips_by_key(r)["category"]
    assert r["filters"]["category"] == "cafe"
    assert chip["value"] == "cafe"
    assert chip["label"] != chip["value"]


def test_episode_name_is_recognised():
    r = extract_clues("during fever week", F, TODAY)
    assert r["filters"]["episode"] == "fever week"


def test_synonym_maps_to_category():
    assert extract_clues("the prescription photo", F, TODAY)["filters"]["category"] == "medicine"


def test_no_recognisable_clue_yields_no_filters():
    r = extract_clues("something I cannot describe", F, TODAY)
    assert r["filters"] == {}
    assert r["chips"] == []


def test_source_is_always_rules():
    assert extract_clues("anything", F, TODAY)["source"] == "rules"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_clues.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'clues'`

- [ ] **Step 3: Implement**

```python
# webapp/apps/retrieval/clues.py
"""Deterministic text -> filter inference. Always available; never rate-limited.

This is the fallback when Groq is unavailable AND the strategy scored offline by
engine/demo_eval.py, so the number on the deck comes from code that really runs.
"""
import calendar
import re
from datetime import date, timedelta

VAGUE_WINDOW_DAYS = 45  # must match engine/demo_eval.VAGUE_WINDOW_DAYS

MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})

# Display label -> exact category value in the library.
CATEGORY_SYNONYMS = {
    "cafe": "cafe", "café": "cafe", "coffee": "cafe", "restaurant": "cafe",
    "beach": "beach", "sea": "beach", "shore": "beach",
    "food": "food", "meal": "food", "lunch": "food", "dinner": "food",
    "street": "street", "road": "street",
    "receipt": "receipt", "bill": "receipt", "invoice": "receipt",
    "medicine": "medicine", "prescription": "medicine", "tablet": "medicine",
    "medicines": "medicine", "pills": "medicine", "dawai": "medicine",
    "mountain": "mountain", "hill": "mountain", "trek": "mountain",
    "wedding": "wedding", "shaadi": "wedding", "marriage": "wedding",
    "pet": "pet", "dog": "pet", "puppy": "pet", "cat": "pet",
    "whiteboard": "whiteboard", "board": "whiteboard",
    "document": "document", "paper": "document", "scan": "document",
    "festival": "festival", "diwali": "festival", "onam": "festival",
}

CATEGORY_LABELS = {
    "cafe": "café", "beach": "beach", "food": "food", "street": "street",
    "receipt": "receipt", "medicine": "medicine / prescription", "mountain": "mountain",
    "wedding": "wedding", "pet": "pet", "whiteboard": "whiteboard",
    "document": "document", "festival": "festival",
}


def _chip(n, cue, label, key, value):
    return {"id": f"c{n}", "cue": cue, "label": label,
            "filter_key": key, "value": value, "editable": True}


def _month_span(year, month):
    last = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last:02d}"


def _dates(text, today):
    """Return (date_from, date_to, cue, label) or None. Most specific pattern wins."""
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m:
        return m.group(0), m.group(0), "exact_date", f"on {m.group(0)}"

    m = re.search(r"\b([a-z]+)\s+(\d{4})\b", text)
    if m and m.group(1) in MONTHS:
        lo, hi = _month_span(int(m.group(2)), MONTHS[m.group(1)])
        return lo, hi, "temporal_approx", f"{m.group(1).title()} {m.group(2)}"

    m = re.search(r"\blast year\b", text)
    if m:
        y = today.year - 1
        return f"{y}-01-01", f"{y}-12-31", "temporal_approx", "last year"

    m = re.search(r"\bthis year\b", text)
    if m:
        y = today.year
        return f"{y}-01-01", f"{y}-12-31", "temporal_approx", "this year"

    m = re.search(r"\b(\d+)\s+years?\s+ago\b", text)
    if m:
        y = today.year - int(m.group(1))
        return f"{y}-01-01", f"{y}-12-31", "temporal_approx", m.group(0)

    m = re.search(r"\b([a-z]+)\b(?=\s|$)", text)
    if m and m.group(1) in MONTHS and re.search(rf"\b{m.group(1)}\b", text):
        month = MONTHS[m.group(1)]
        anchor = date(today.year, month, 15)
        if anchor > today:
            anchor = date(today.year - 1, month, 15)
        lo = (anchor - timedelta(days=VAGUE_WINDOW_DAYS)).isoformat()
        hi = (anchor + timedelta(days=VAGUE_WINDOW_DAYS)).isoformat()
        return lo, hi, "temporal_approx", m.group(1).title()
    return None


def extract_clues(text: str, facets, today: date = None) -> dict:
    today = today or date.today()
    low = text.lower()
    filters, chips, n = {}, [], 0

    for ep in sorted(facets.episodes, key=len, reverse=True):
        if ep.lower() in low:
            n += 1
            filters["episode"] = ep
            chips.append(_chip(n, "event_anchor", ep, "episode", ep))
            break

    for loc in sorted(facets.locations, key=len, reverse=True):
        if re.search(rf"\b{re.escape(loc.lower())}\b", low):
            n += 1
            filters["location"] = loc
            chips.append(_chip(n, "place_named", loc, "location", loc))
            break

    for word, cat in CATEGORY_SYNONYMS.items():
        if cat in facets.categories and re.search(rf"\b{re.escape(word)}\b", low):
            n += 1
            filters["category"] = cat
            chips.append(_chip(n, "object", CATEGORY_LABELS.get(cat, cat), "category", cat))
            break

    found = _dates(low, today)
    if found:
        lo, hi, cue, label = found
        n += 1
        filters["date_from"], filters["date_to"] = lo, hi
        chips.append(_chip(n, cue, label, "date_from", lo))
        chips[-1]["value_to"] = hi

    return {"filters": filters, "chips": chips, "source": "rules"}
```

- [ ] **Step 4: Run and confirm green**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_clues.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add webapp/apps/retrieval/clues.py webapp/apps/retrieval/tests/test_clues.py
git commit -m "feat(retrieval): rule-based clue extraction"
```

---

### Task 3: ONNX CLIP text encoder, with a parity gate

**The risk this task exists to kill:** the 494 image vectors were produced by `sentence-transformers/clip-ViT-B-32`. If the ONNX text tower does not land in the same space, every search result is quietly wrong while looking plausible. Step 1 exports; step 3 **proves** parity before anything depends on it.

**Files:**
- Create: `engine/export_onnx.py`, `webapp/apps/retrieval/encoder.py`
- Test: `webapp/apps/retrieval/tests/test_encoder.py`, `tests/test_export_onnx.py`

**Interfaces:**
- Produces: `encoder.TextEncoder(model_dir: Path)` with `.encode(texts: list[str]) -> np.ndarray` of shape `(len(texts), 512)`.

- [ ] **Step 1: Write the export script**

```python
# engine/export_onnx.py
"""Export the CLIP text tower to ONNX. Runs locally; output is committed."""
from pathlib import Path

import torch
from transformers import CLIPTextModelWithProjection, CLIPTokenizerFast

MODEL = "openai/clip-vit-base-patch32"  # what sentence-transformers/clip-ViT-B-32 wraps


def export(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    tok = CLIPTokenizerFast.from_pretrained(MODEL)
    tok.save_pretrained(out_dir)
    model = CLIPTextModelWithProjection.from_pretrained(MODEL).eval()
    dummy = tok(["a photo"], return_tensors="pt", padding="max_length", max_length=77)
    path = out_dir / "clip_text.onnx"
    torch.onnx.export(
        model, (dummy["input_ids"], dummy["attention_mask"]), str(path),
        input_names=["input_ids", "attention_mask"], output_names=["text_embeds"],
        dynamic_axes={"input_ids": {0: "batch"}, "attention_mask": {0: "batch"},
                      "text_embeds": {0: "batch"}},
        opset_version=17,
    )
    return path


if __name__ == "__main__":
    print(export(Path(__file__).resolve().parent.parent / "webapp/apps/retrieval/data"))
```

- [ ] **Step 2: Run the export**

Run: `.venv/bin/python -m engine.export_onnx`
Expected: prints the path; `clip_text.onnx` plus tokenizer files exist under `webapp/apps/retrieval/data/`.

- [ ] **Step 3: Write the parity test — this is the gate**

```python
# tests/test_export_onnx.py
"""ONNX text output must match sentence-transformers, or every search result is wrong."""
import numpy as np
import pytest

pytest.importorskip("onnxruntime")
pytest.importorskip("sentence_transformers")

QUERIES = ["a small cafe in Goa", "the medicine I took last year", "wedding photos"]


def test_onnx_text_embeddings_match_sentence_transformers():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "webapp/apps/retrieval"))
    from encoder import TextEncoder
    from sentence_transformers import SentenceTransformer

    data = Path(__file__).resolve().parent.parent / "webapp/apps/retrieval/data"
    mine = TextEncoder(data).encode(QUERIES)
    theirs = SentenceTransformer("clip-ViT-B-32").encode(QUERIES)

    def unit(m):
        return m / np.linalg.norm(m, axis=1, keepdims=True)

    cos = (unit(mine) * unit(theirs)).sum(axis=1)
    assert cos.min() > 0.999, f"ONNX diverged from sentence-transformers: {cos}"
```

- [ ] **Step 4: Implement the encoder**

```python
# webapp/apps/retrieval/encoder.py
"""ONNX CLIP text tower. No torch at runtime."""
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

MAX_LEN = 77


class TextEncoder:
    def __init__(self, model_dir: Path):
        model_dir = Path(model_dir)
        self.tok = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        self.tok.enable_padding(length=MAX_LEN, pad_id=0, pad_token="<|endoftext|>")
        self.tok.enable_truncation(max_length=MAX_LEN)
        self.session = ort.InferenceSession(
            str(model_dir / "clip_text.onnx"), providers=["CPUExecutionProvider"])

    def encode(self, texts: list) -> np.ndarray:
        enc = self.tok.encode_batch(list(texts))
        ids = np.array([e.ids for e in enc], dtype=np.int64)
        mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
        out = self.session.run(["text_embeds"], {"input_ids": ids, "attention_mask": mask})
        return out[0].astype(np.float32)
```

- [ ] **Step 5: Run the parity gate**

Run: `.venv/bin/python -m pytest tests/test_export_onnx.py -v`
Expected: PASS with min cosine > 0.999. **If it fails, stop** — do not build search on a mismatched encoder. The likely cause is the pooling/projection head; compare against `CLIPModel.get_text_features` before changing anything downstream.

- [ ] **Step 6: Commit**

```bash
git add engine/export_onnx.py webapp/apps/retrieval/encoder.py tests/test_export_onnx.py
git commit -m "feat(retrieval): ONNX CLIP text encoder with parity gate"
```

---

### Task 4: Search, episode grouping and why-strings

**Files:**
- Create: `webapp/apps/retrieval/search.py`
- Test: `webapp/apps/retrieval/tests/test_search.py`

**Interfaces:**
- Consumes: `encoder.TextEncoder`, `engine.demo_index.{apply_filters, rank}`.
- Produces: `search(text, filters, mode, ctx, top_k=20) -> dict` with keys `episodes`, `total`, `mode`, `filters_applied`. `ctx` is a `SearchContext(ids, matrix, records, encoder)`.

- [ ] **Step 1: Write the failing test**

```python
# webapp/apps/retrieval/tests/test_search.py
import numpy as np
from search import SearchContext, group_by_episode, why_strings, search


class FakeEncoder:
    def encode(self, texts):
        return np.array([[1.0, 0.0]], dtype=np.float32)


RECORDS = [
    {"id": "demo:1", "episode_id": "ep1", "episode": "goa trip", "location": "Goa",
     "category": "cafe", "date": "2023-12-14T10:00:00", "file": "library/0001.jpg"},
    {"id": "demo:2", "episode_id": "ep1", "episode": "goa trip", "location": "Goa",
     "category": "food", "date": "2023-12-18T10:00:00", "file": "library/0002.jpg"},
    {"id": "demo:3", "episode_id": "",    "episode": "",         "location": "Mumbai",
     "category": "street", "date": "2025-01-05T10:00:00", "file": "library/0003.jpg"},
]
IDS = ["demo:1", "demo:2", "demo:3"]
MATRIX = np.array([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]], dtype=np.float32)
CTX = SearchContext(ids=IDS, matrix=MATRIX, records=RECORDS, encoder=FakeEncoder())


def test_filters_restrict_the_result_set():
    out = search("cafe", {"location": "Goa"}, "trails", CTX)
    assert {p["id"] for e in out["episodes"] for p in e["photos"]} == {"demo:1", "demo:2"}


def test_baseline_mode_ignores_filters():
    out = search("cafe", {"location": "Goa"}, "baseline", CTX)
    assert out["total"] == 3
    assert out["filters_applied"] == {}


def test_results_group_by_episode_not_flat():
    groups = group_by_episode([("demo:1", 0.9), ("demo:2", 0.8)], RECORDS)
    assert len(groups) == 1
    assert groups[0]["episode"] == "goa trip"
    assert groups[0]["count"] == 2


def test_stray_photos_group_separately_from_named_episodes():
    groups = group_by_episode([("demo:1", 0.9), ("demo:3", 0.7)], RECORDS)
    assert len(groups) == 2


def test_episode_window_spans_its_photos():
    g = group_by_episode([("demo:1", 0.9), ("demo:2", 0.8)], RECORDS)[0]
    assert g["date_from"] == "2023-12-14"
    assert g["date_to"] == "2023-12-18"


def test_why_strings_name_the_filter_and_its_value():
    w = why_strings({"location": "Goa", "category": "cafe"})
    assert any("Goa" in s for s in w)
    assert any("cafe" in s for s in w)


def test_why_strings_are_empty_without_filters():
    assert why_strings({}) == []
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_search.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'search'`

- [ ] **Step 3: Implement**

```python
# webapp/apps/retrieval/search.py
"""Search over the pre-embedded library, grouped into visual episodes.

Filtering and ranking delegate to engine.demo_index so the deployed demo cannot
diverge from the numbers measured offline.
"""
from dataclasses import dataclass

from engine.demo_index import apply_filters, rank

FILTER_LABELS = {
    "location": "location matched",
    "category": "photo type matched",
    "episode": "event matched",
}


@dataclass
class SearchContext:
    ids: list
    matrix: object
    records: list
    encoder: object


def why_strings(filters: dict) -> list:
    out = [f'{FILTER_LABELS[k]} "{v}"' for k, v in filters.items() if k in FILTER_LABELS]
    if filters.get("date_from") and filters.get("date_to"):
        out.append(f'taken between {filters["date_from"]} and {filters["date_to"]}')
    return out


def group_by_episode(scored: list, records: list) -> list:
    by_id = {r["id"]: r for r in records}
    groups = {}
    for pid, score in scored:
        r = by_id.get(pid)
        if r is None:
            continue
        key = r.get("episode_id") or f"stray:{pid}"
        g = groups.setdefault(key, {
            "episode_id": r.get("episode_id", ""), "episode": r.get("episode") or "Other photos",
            "location": r.get("location", ""), "date_from": None, "date_to": None,
            "count": 0, "photos": [], "top_score": score,
        })
        day = (r.get("date") or "")[:10]
        if day:
            g["date_from"] = day if g["date_from"] is None else min(g["date_from"], day)
            g["date_to"] = day if g["date_to"] is None else max(g["date_to"], day)
        g["count"] += 1
        g["photos"].append({"id": pid, "file": r.get("file", ""), "score": round(float(score), 3)})
    return sorted(groups.values(), key=lambda g: -g["top_score"])


def search(text: str, filters: dict, mode: str, ctx: SearchContext, top_k: int = 20) -> dict:
    applied = {} if mode == "baseline" else {k: v for k, v in (filters or {}).items() if v}
    qv = ctx.encoder.encode([text])
    allowed = None
    if applied:
        allowed = {r["id"] for r in apply_filters(ctx.records, **applied)}
    scored = rank(qv, ctx.ids, ctx.matrix, allowed=allowed, top_k=top_k)
    groups = group_by_episode(scored, ctx.records)
    reasons = why_strings(applied)
    for g in groups:
        g["why"] = list(reasons)
    return {"episodes": groups, "total": len(scored), "mode": mode, "filters_applied": applied}
```

- [ ] **Step 4: Run and confirm green**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_search.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add webapp/apps/retrieval/search.py webapp/apps/retrieval/tests/test_search.py
git commit -m "feat(retrieval): episode-grouped search with evidence labels"
```

---

### Task 5: LLM extraction with guaranteed fallback

**Files:**
- Create: `webapp/apps/retrieval/llm_clues.py`
- Test: `webapp/apps/retrieval/tests/test_llm_clues.py`

**Interfaces:**
- Consumes: `clues.extract_clues`, `engine.groq.GroqClient`.
- Produces: `extract(text, facets, client, today=None) -> dict` — same shape as `extract_clues` plus `"notice": str | None`. `source` is `"llm"` or `"rules"`.

- [ ] **Step 1: Write the failing test**

```python
# webapp/apps/retrieval/tests/test_llm_clues.py
import json
from datetime import date

from facets import load_facets
from llm_clues import extract

LIB = [{"id": "a", "category": "cafe", "location": "Goa", "episode": "goa trip",
        "date": "2023-12-14T10:00:00"}]
F = load_facets(LIB)
TODAY = date(2026, 9, 21)


class OkClient:
    def chat_json(self, *a, **k):
        return json.dumps({"filters": {"location": "Goa"},
                           "chips": [{"id": "c1", "cue": "place_named", "label": "Goa",
                                      "filter_key": "location", "value": "Goa", "editable": True}]})


class BoomClient:
    def __init__(self, exc):
        self.exc = exc

    def chat_json(self, *a, **k):
        raise self.exc


def test_uses_the_llm_when_it_answers():
    r = extract("our Goa trip", F, OkClient(), TODAY)
    assert r["source"] == "llm"
    assert r["filters"]["location"] == "Goa"
    assert r["notice"] is None


def test_falls_back_to_rules_when_the_budget_is_gone():
    from engine.groq import DailyBudgetReached
    r = extract("our Goa trip", F, BoomClient(DailyBudgetReached("cap")), TODAY)
    assert r["source"] == "rules"
    assert r["filters"]["location"] == "Goa"
    assert r["notice"]


def test_falls_back_on_any_transport_error():
    r = extract("our Goa trip", F, BoomClient(TimeoutError("slow")), TODAY)
    assert r["source"] == "rules"


def test_falls_back_when_the_model_returns_junk():
    class Junk:
        def chat_json(self, *a, **k):
            return "not json at all"
    assert extract("our Goa trip", F, Junk(), TODAY)["source"] == "rules"


def test_falls_back_when_no_client_is_configured():
    assert extract("our Goa trip", F, None, TODAY)["source"] == "rules"


def test_llm_filter_keys_outside_the_contract_are_dropped():
    class Extra:
        def chat_json(self, *a, **k):
            return json.dumps({"filters": {"location": "Goa", "camera": "Pixel"}, "chips": []})
    assert extract("x", F, Extra(), TODAY)["filters"] == {"location": "Goa"}
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_llm_clues.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'llm_clues'`

- [ ] **Step 3: Implement**

```python
# webapp/apps/retrieval/llm_clues.py
"""LLM clue extraction that can always degrade to rules."""
import json
from datetime import date

from clues import extract_clues

ALLOWED = {"date_from", "date_to", "location", "category", "episode"}

SYSTEM = (
    "You turn a person's vague memory of a photo into retrieval filters.\n"
    "Return ONLY JSON: {\"filters\": {...}, \"chips\": [...]}.\n"
    "filters keys, all optional: date_from, date_to (YYYY-MM-DD), location, category, episode.\n"
    "Use ONLY these values.\n"
    "  location: {locations}\n  category: {categories}\n  episode: {episodes}\n"
    "Each chip is {{\"id\",\"cue\",\"label\",\"filter_key\",\"value\",\"editable\":true}} where cue is one of "
    "exact_date, temporal_approx, place_named, object, event_anchor. "
    "'label' is what a person reads; 'value' must be exactly one of the allowed values above. "
    "Omit anything you are not confident about. Today is {today}."
)


def _prompt(facets, today):
    return SYSTEM.format(locations=", ".join(facets.locations),
                         categories=", ".join(facets.categories),
                         episodes=", ".join(facets.episodes), today=today.isoformat())


def extract(text: str, facets, client, today: date = None) -> dict:
    today = today or date.today()
    fallback = dict(extract_clues(text, facets, today),
                    notice="Live extraction unavailable - used rule-based clue matching.")
    if client is None:
        return fallback
    try:
        raw = client.chat_json(_prompt(facets, today), text)
        data = json.loads(raw)
        filters = {k: v for k, v in (data.get("filters") or {}).items() if k in ALLOWED and v}
        return {"filters": filters, "chips": data.get("chips") or [],
                "source": "llm", "notice": None}
    except Exception:
        return fallback
```

- [ ] **Step 4: Run and confirm green**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_llm_clues.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add webapp/apps/retrieval/llm_clues.py webapp/apps/retrieval/tests/test_llm_clues.py
git commit -m "feat(retrieval): LLM clue extraction with rule fallback"
```

---

### Task 6: FastAPI service

**Files:**
- Create: `webapp/apps/retrieval/main.py`
- Test: `webapp/apps/retrieval/tests/test_api.py`

**Interfaces:**
- Produces: ASGI `app` with `POST /extract`, `POST /search`, `GET /health`.

- [ ] **Step 1: Write the failing test**

```python
# webapp/apps/retrieval/tests/test_api.py
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_reports_readiness():
    body = client.get("/health").json()
    assert body["images"] > 0
    assert "encoder" in body


def test_extract_returns_the_contract_shape():
    body = client.post("/extract", json={"text": "our Goa trip"}).json()
    assert set(body) >= {"filters", "chips", "source", "notice"}
    assert set(body["filters"]) <= {"date_from", "date_to", "location", "category", "episode"}


def test_search_returns_grouped_episodes():
    body = client.post("/search", json={"text": "cafe in Goa",
                                        "filters": {"location": "Goa"},
                                        "mode": "trails"}).json()
    assert body["mode"] == "trails"
    assert isinstance(body["episodes"], list)


def test_search_rejects_a_filter_key_outside_the_contract():
    r = client.post("/search", json={"text": "x", "filters": {"camera": "Pixel"},
                                     "mode": "trails"})
    assert r.status_code == 422


def test_search_rejects_an_unparseable_date():
    r = client.post("/search", json={"text": "x", "filters": {"date_from": "yesterday"},
                                     "mode": "trails"})
    assert r.status_code == 422


def test_empty_text_is_rejected():
    assert client.post("/extract", json={"text": "   "}).status_code == 422
```

- [ ] **Step 2: Run it and watch it fail**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_api.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 3: Implement**

```python
# webapp/apps/retrieval/main.py
"""Public retrieval API. Visitor text is never logged or persisted."""
import json
import os
from datetime import date
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import llm_clues
from encoder import TextEncoder
from facets import load_facets
from search import SearchContext, search

DATA = Path(__file__).resolve().parent / "data"
ALLOWED = {"date_from", "date_to", "location", "category", "episode"}

app = FastAPI(title="Memory Trails retrieval")

_records = [json.loads(l) for l in (DATA / "library.jsonl").open()]
_index = np.load(DATA / "index.npz", allow_pickle=False)
_ids = list(_index["ids"])
_matrix = _index["matrix"]
_facets = load_facets(_records)
_encoder = None
_client = None


def encoder():
    global _encoder
    if _encoder is None:
        _encoder = TextEncoder(DATA)
    return _encoder


def client():
    global _client
    if _client is None and os.environ.get("GROQ_API_KEY"):
        from engine.groq import GroqClient
        _client = GroqClient(os.environ.get("DEMO_MODEL", "openai/gpt-oss-20b"),
                             daily_cap=int(os.environ.get("DEMO_TOKEN_CAP", "60000")))
    return _client


class ExtractIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class SearchIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    filters: dict = Field(default_factory=dict)
    mode: str = "trails"


def _validate(filters: dict):
    bad = set(filters) - ALLOWED
    if bad:
        raise HTTPException(422, f"unsupported filter keys: {sorted(bad)}")
    for key in ("date_from", "date_to"):
        if filters.get(key):
            try:
                date.fromisoformat(filters[key])
            except ValueError:
                raise HTTPException(422, f"{key} must be YYYY-MM-DD")


@app.get("/health")
def health():
    return {"images": len(_ids), "episodes": len(_facets.episodes),
            "encoder": "loaded" if _encoder else "lazy",
            "groq": bool(os.environ.get("GROQ_API_KEY"))}


@app.post("/extract")
def extract(body: ExtractIn):
    if not body.text.strip():
        raise HTTPException(422, "text is required")
    return llm_clues.extract(body.text.strip(), _facets, client())


@app.post("/search")
def do_search(body: SearchIn):
    if not body.text.strip():
        raise HTTPException(422, "text is required")
    _validate(body.filters or {})
    ctx = SearchContext(ids=_ids, matrix=_matrix, records=_records, encoder=encoder())
    return search(body.text.strip(), body.filters or {}, body.mode, ctx)
```

- [ ] **Step 4: Run and confirm green**

Run: `cd webapp/apps/retrieval && python -m pytest tests/test_api.py -v`
Expected: 6 passed. (Requires Task 7's export to have populated `data/`; if running out of order, run Task 7 step 2 first.)

- [ ] **Step 5: Commit**

```bash
git add webapp/apps/retrieval/main.py webapp/apps/retrieval/tests/test_api.py
git commit -m "feat(retrieval): FastAPI service with contract validation"
```

---

### Task 7: Build-time export pipeline

**Files:**
- Create: `engine/export_web.py`
- Test: `tests/test_export_web.py`

**Interfaces:**
- Produces: `export(root: Path) -> dict` writing every runtime artifact and returning a manifest.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export_web.py
import json

from engine.export_web import build_evidence, rewrite_file_paths


def test_file_paths_are_rewritten_to_the_published_location():
    recs = [{"id": "demo:0001", "file": "images/0001.jpg"}]
    assert rewrite_file_paths(recs)[0]["file"] == "library/0001.jpg"


def test_rewrite_leaves_other_fields_untouched():
    recs = [{"id": "demo:0001", "file": "images/0001.jpg", "location": "Goa"}]
    assert rewrite_file_paths(recs)[0]["location"] == "Goa"


def test_evidence_bundle_has_every_tab_key():
    ev = build_evidence([{"id": "x", "era": "toggle", "specificity": "specific_attempt",
                          "failure_stage": "not_surfaced", "outcome": "not_found",
                          "cues_retained": ["temporal_approx"], "hypotheses": ["H1"],
                          "asset_type": "photo", "search_mode": "search"}], {}, None)
    assert set(ev) >= {"ranking", "failure_stages", "cues", "funnel", "audit"}


def test_evidence_json_is_serialisable():
    ev = build_evidence([], {}, None)
    json.dumps(ev)
```

- [ ] **Step 2: Run it and watch it fail**

Run: `.venv/bin/python -m pytest tests/test_export_web.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'engine.export_web'`

- [ ] **Step 3: Implement**

```python
# engine/export_web.py
"""Build every artifact the Vercel app serves. Runs locally; output is committed.

Vercel never runs this: no torch, no Groq, no model downloads at build time.
"""
import json
import shutil
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "data" / "demo"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
WEB = ROOT / "webapp" / "apps" / "web"
RETRIEVAL = ROOT / "webapp" / "apps" / "retrieval"


def rewrite_file_paths(records: list) -> list:
    out = []
    for r in records:
        r = dict(r)
        name = Path(r.get("file", "")).name
        if name:
            r["file"] = f"library/{name}"
        out.append(r)
    return out


def build_evidence(episodes: list, funnel: dict, audit) -> dict:
    import sys
    sys.path.insert(0, str(ROOT / "space"))
    import demo_core as core
    specific = [e for e in episodes if e.get("specificity") == "specific_attempt"]
    from collections import Counter
    return {
        "ranking": core.ranking_table(episodes) if episodes else [],
        "failure_stages": [{"stage": k, "count": v, "share": round(v / len(specific), 3)}
                           for k, v in Counter(e["failure_stage"] for e in specific).most_common()]
                          if specific else [],
        "cues": core.cue_table(episodes) if episodes else [],
        "funnel": core.funnel_rows(funnel) if funnel else [],
        "audit": audit or {},
        "counts": {"episodes": len(episodes), "specific": len(specific)},
        "built": date.today().isoformat(),
    }


def export(root: Path = ROOT) -> dict:
    (WEB / "public" / "library").mkdir(parents=True, exist_ok=True)
    (WEB / "public" / "data").mkdir(parents=True, exist_ok=True)
    RETRIEVAL.joinpath("data").mkdir(parents=True, exist_ok=True)

    for src in sorted((DEMO / "images").glob("*.jpg")):
        shutil.copy2(src, WEB / "public" / "library" / src.name)

    records = rewrite_file_paths([json.loads(l) for l in (DEMO / "library.jsonl").open()])
    with (RETRIEVAL / "data" / "library.jsonl").open("w") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    shutil.copy2(DEMO / "index.npz", RETRIEVAL / "data" / "index.npz")

    episodes = [json.loads(l) for l in (INTERIM / "episodes.jsonl").open()]
    funnel_path = INTERIM / "funnel.json"
    audit_path = PROCESSED / "audit_report.json"
    funnel = json.loads(funnel_path.read_text()) if funnel_path.exists() else {}
    audit = json.loads(audit_path.read_text()) if audit_path.exists() else None
    evidence = build_evidence(episodes, funnel, audit)
    (WEB / "public" / "data" / "evidence.json").write_text(json.dumps(evidence))

    attribution = [{"file": r["file"], "title": r.get("title", ""),
                    "creator": r.get("creator", ""), "license": r.get("license", ""),
                    "source_url": r.get("source_url", "")} for r in records]
    (WEB / "public" / "data" / "attribution.json").write_text(json.dumps(attribution))

    src_engine = RETRIEVAL / "engine"
    src_engine.mkdir(exist_ok=True)
    for mod in ["__init__.py", "common.py", "demo_index.py", "groq.py", "analysis.py", "extract.py"]:
        if (ROOT / "engine" / mod).exists():
            shutil.copy2(ROOT / "engine" / mod, src_engine / mod)

    manifest = {"images": len(records), "episodes": len(episodes),
                "built": date.today().isoformat(), "clip_model": "clip-ViT-B-32"}
    (RETRIEVAL / "data" / "manifest.json").write_text(json.dumps(manifest))
    return manifest


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
```

- [ ] **Step 4: Run the tests, then the export**

Run: `.venv/bin/python -m pytest tests/test_export_web.py -v` → 4 passed
Run: `.venv/bin/python -m engine.export_web` → prints a manifest with `"images": 494`

- [ ] **Step 5: Confirm the whole suite is still green**

Run: `.venv/bin/python -m pytest -q tests`
Expected: 154+ passed (150 existing plus this task's)

- [ ] **Step 6: Commit**

```bash
git add engine/export_web.py tests/test_export_web.py webapp/apps/retrieval/data webapp/apps/web/public
git commit -m "feat: build-time export pipeline for the web app"
```

---

### Task 8: The measured MVP number

**This task produces a figure for the deck.** Phase 5 currently has only the bounds 0.053 and 0.583; this yields the value between them, from the same extractor the live app runs.

**Files:**
- Modify: `engine/demo_eval.py`
- Test: `tests/test_demo_eval_inferred.py`

**Interfaces:**
- Consumes: `clues.extract_clues` (Task 2).
- Produces: `inferred_filters_for(task, facets, today) -> dict` — same five-key shape as `filters_for`, but derived from `task["query"]` **without** reading the target.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_demo_eval_inferred.py
from datetime import date

from engine.demo_eval import inferred_filters_for


class F:
    locations = ["Goa", "Bengaluru"]
    episodes = ["goa trip", "fever week"]
    categories = ["cafe", "food", "medicine"]
    episode_windows = {}


def test_infers_from_the_query_alone():
    task = {"query": "on 2024-07-15", "cues_used": ["exact_date"]}
    assert inferred_filters_for(task, F, date(2026, 9, 21))["date_from"] == "2024-07-15"


def test_never_reads_the_target_record():
    task = {"query": "something vague", "cues_used": ["event_anchor"], "episode": "goa trip"}
    assert inferred_filters_for(task, F, date(2026, 9, 21)) == {}


def test_returns_only_contract_keys():
    task = {"query": "cafe in Goa last year", "cues_used": []}
    out = inferred_filters_for(task, F, date(2026, 9, 21))
    assert set(out) <= {"date_from", "date_to", "location", "category", "episode"}
```

- [ ] **Step 2: Run it and watch it fail**

Run: `.venv/bin/python -m pytest tests/test_demo_eval_inferred.py -v`
Expected: FAIL — `ImportError: cannot import name 'inferred_filters_for'`

- [ ] **Step 3: Implement — append to `engine/demo_eval.py`**

```python
def inferred_filters_for(task: dict, facets, today=None) -> dict:
    """What the MVP can actually derive: filters from the query text alone.

    Unlike filters_for, this never sees the answer. The gap between the two is the
    cost of imperfect inference, and it is the number the MVP slide should carry.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "webapp/apps/retrieval"))
    from clues import extract_clues
    return extract_clues(task["query"], facets, today)["filters"]
```

- [ ] **Step 4: Run and confirm green**

Run: `.venv/bin/python -m pytest tests/test_demo_eval_inferred.py -v` → 3 passed

- [ ] **Step 5: Score all three strategies and record the result**

```bash
.venv/bin/python - <<'EOF'
import json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, "webapp/apps/retrieval")
import numpy as np
from facets import load_facets
from engine import demo_eval, demo_index

lib = [json.loads(l) for l in open("data/demo/library.jsonl")]
tasks = [json.loads(l) for l in open("data/eval/tasks.jsonl")]
idx = np.load("data/demo/index.npz", allow_pickle=False)
ids, matrix = list(idx["ids"]), idx["matrix"]
facets = load_facets(lib)
by_id = {r["id"]: r for r in lib}
model = demo_index.load_model()

rows = {"baseline": [], "oracle": [], "inferred": []}
for t in tasks:
    qv = model.encode([t["query"]])
    target = by_id[t["target_id"]]
    answers = set(t["answer_ids"])
    rows["baseline"].append(demo_index.baseline_search(qv, ids, matrix, 20))
    rows["oracle"].append(demo_index.filtered_search(qv, ids, matrix, lib, 20,
                          **demo_eval.filters_for(t, target)))
    rows["inferred"].append(demo_index.filtered_search(qv, ids, matrix, lib, 20,
                            **demo_eval.inferred_filters_for(t, facets, date.today())))

for name, results in rows.items():
    rec = np.mean([demo_index.recall_at_k(r, set(t["answer_ids"]), 20)
                   for r, t in zip(results, tasks)])
    hit = np.mean([1.0 if r and r[0][0] in set(t["answer_ids"]) else 0.0
                   for r, t in zip(results, tasks)])
    print(f"{name:10s} recall@20={rec:.3f}  hit@1={hit:.3f}")
EOF
```

Expected: `baseline recall@20=0.053`, `oracle recall@20=0.583`, and an `inferred` value between them. **Record all three in `PROGRESS.md` with the date.** If `inferred` lands near 0.053, the honest deck line is "the mechanic works, the inference does not yet" — that is a finding, not a failure, but it changes the MVP slide's claim (spec §14.2).

- [ ] **Step 6: Commit**

```bash
git add engine/demo_eval.py tests/test_demo_eval_inferred.py PROGRESS.md
git commit -m "feat(eval): score inferred-filter retrieval as a third strategy"
```

---

### Task 9: Parity gate — service vs offline

**Files:**
- Test: `tests/test_service_parity.py`

**Interfaces:**
- Consumes: `search.search` (Task 4), `demo_index.filtered_search`.

- [ ] **Step 1: Write the test**

```python
# tests/test_service_parity.py
"""The deployed service must return exactly what the offline code returns.

This is what mechanically stops the live demo and the deck from disagreeing.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "webapp/apps/retrieval"))
pytest.importorskip("onnxruntime")


@pytest.fixture(scope="module")
def ctx():
    from encoder import TextEncoder
    from search import SearchContext
    data = ROOT / "webapp/apps/retrieval/data"
    records = [json.loads(l) for l in (data / "library.jsonl").open()]
    idx = np.load(data / "index.npz", allow_pickle=False)
    return SearchContext(ids=list(idx["ids"]), matrix=idx["matrix"],
                         records=records, encoder=TextEncoder(data))


def test_service_search_matches_offline_filtered_search(ctx):
    from engine import demo_eval, demo_index
    from search import search
    tasks = [json.loads(l) for l in (ROOT / "data/eval/tasks.jsonl").open()]
    by_id = {r["id"]: r for r in ctx.records}
    for t in tasks:
        filters = demo_eval.filters_for(t, by_id[t["target_id"]])
        qv = ctx.encoder.encode([t["query"]])
        expected = [i for i, _ in demo_index.filtered_search(
            qv, ctx.ids, ctx.matrix, ctx.records, 20, **filters)]
        got = [p["id"] for e in search(t["query"], filters, "trails", ctx)["episodes"]
               for p in e["photos"]]
        assert sorted(got) == sorted(expected), f"divergence on {t['id']}"
```

- [ ] **Step 2: Run it**

Run: `.venv/bin/python -m pytest tests/test_service_parity.py -v`
Expected: PASS across all 30 tasks. A failure here means the service and the deck disagree — fix before going further.

- [ ] **Step 3: Commit**

```bash
git add tests/test_service_parity.py
git commit -m "test: parity gate between service and offline retrieval"
```

---

### Task 10: Next.js scaffold and the MVP surface

**Files:**
- Create: `webapp/apps/web/package.json`, `app/layout.tsx`, `app/globals.css`, `app/page.tsx`, `components/ChipRow.tsx`, `components/EpisodeCard.tsx`, `lib/api.ts`

**Interfaces:**
- Consumes: `POST /api/py/extract`, `POST /api/py/search`.
- Produces: the `/` surface.

- [ ] **Step 1: Scaffold**

```bash
cd webapp/apps/web
npx --yes create-next-app@latest . --typescript --app --no-tailwind --no-src-dir --no-eslint --import-alias "@/*"
```

- [ ] **Step 2: Write the API client**

```ts
// webapp/apps/web/lib/api.ts
export type Chip = { id: string; cue: string; label: string; filter_key: string; value: string; editable: boolean };
export type Filters = Record<string, string>;
export type Photo = { id: string; file: string; score: number };
export type Episode = { episode_id: string; episode: string; location: string;
  date_from: string | null; date_to: string | null; count: number; why: string[]; photos: Photo[] };

export async function extract(text: string) {
  const r = await fetch("/api/py/extract", { method: "POST",
    headers: { "content-type": "application/json" }, body: JSON.stringify({ text }) });
  if (!r.ok) throw new Error("extract failed");
  return r.json() as Promise<{ filters: Filters; chips: Chip[]; source: string; notice: string | null }>;
}

export async function search(text: string, filters: Filters, mode: "trails" | "baseline") {
  const r = await fetch("/api/py/search", { method: "POST",
    headers: { "content-type": "application/json" }, body: JSON.stringify({ text, filters, mode }) });
  if (!r.ok) throw new Error("search failed");
  return r.json() as Promise<{ episodes: Episode[]; total: number; mode: string; filters_applied: Filters }>;
}
```

- [ ] **Step 3: Build the MVP page**

`app/page.tsx` holds state `{text, chips, filters, episodes, mode, notice, loading}`. Behaviour:
1. Textarea + "Find the moment" button → `extract(text)` → render chips → `search(text, filters, mode)`.
2. `ChipRow` renders each chip with a remove control. Removing chip `c` deletes `filters[c.filter_key]` (and `date_to` when `filter_key === "date_from"`), then re-runs `search`. **Never re-run `extract`** — the user's correction is authoritative.
3. Toggle switches `mode` between `"trails"` and `"baseline"` and re-runs `search`. Label the baseline side "Plain search (what Photos does today)".
4. `EpisodeCard` shows episode name, date range, location, count, the `why` list under a "why this episode is here" heading, and a thumbnail grid from `/library/...`.
5. When `episodes` is empty, render the filters that fired plus a "widen the date window" action that drops `date_from`/`date_to` and re-runs.
6. When `notice` is non-null, show it as a single muted line.

- [ ] **Step 4: Verify locally**

Run: `cd webapp && vercel dev`
Check: `/` loads, "our Goa trip" produces chips, removing the location chip changes results, the toggle visibly changes them.

- [ ] **Step 5: Commit**

```bash
git add webapp/apps/web
git commit -m "feat(web): memory trails MVP surface"
```

---

### Task 11: Evidence and attribution surfaces

**Files:**
- Create: `webapp/apps/web/app/evidence/page.tsx`, `app/attribution/page.tsx`, `components/DataTable.tsx`

- [ ] **Step 1: Build `/evidence`**

Three tabs. **Tabs 2 and 3 make no network calls** — they import `public/data/evidence.json` at build time.
- *Try a memory*: textarea → `/api/py/extract` → show the chips the pipeline's own extractor produced.
- *Compare retrieval problems*: `ranking`, `failure_stages`, `cues` tables from `evidence.json`.
- *How it works*: `funnel` and `audit` from `evidence.json`, plus the limitations list from spec §11.

Every percentage renders with its denominator (rule C).

- [ ] **Step 2: Build `/attribution`**

Read `public/data/attribution.json`; render a table of all 494 entries with creator, licence and a link to `source_url`.

- [ ] **Step 3: Verify**

Run: `cd webapp && vercel dev`
Check: `/evidence` renders all three tabs; the browser network panel shows **no** request when switching to tabs 2 and 3. `/attribution` lists 494 rows.

- [ ] **Step 4: Commit**

```bash
git add webapp/apps/web/app/evidence webapp/apps/web/app/attribution webapp/apps/web/components
git commit -m "feat(web): evidence and attribution surfaces"
```

---

### Task 12: Deploy and verify

- [ ] **Step 1: Link the project under a neutral name**

```bash
cd webapp
vercel link --project memory-trails-demo
```

Confirm the name contains no personal name.

- [ ] **Step 2: Add the Groq secret**

```bash
vercel env add GROQ_API_KEY production
vercel env add DEMO_MODEL production   # openai/gpt-oss-20b
```

- [ ] **Step 3: Deploy to production**

```bash
vercel --prod
```

- [ ] **Step 4: Smoke-test the live URL**

```bash
curl -s https://memory-trails-demo.vercel.app/api/py/health | python3 -m json.tool
```
Expected: `"images": 494`.

Then in a browser: run a query end to end, remove a chip, flip the toggle, open `/evidence` and `/attribution`.

- [ ] **Step 5: Verify the fallback path**

Temporarily remove `GROQ_API_KEY` from the production environment, redeploy, and confirm `/extract` still returns filters with `"source": "rules"` and a notice. Restore the key afterwards.

- [ ] **Step 6: Anonymity check**

Open the production URL in an incognito window. Confirm the user's name appears nowhere in the URL, page text, or `view-source`. **Cite the production alias in the deck, never a preview URL.**

- [ ] **Step 7: Record and commit**

Add the live URLs and the three measured recall figures to `PROGRESS.md` and `implementation_plan.md` §6.

```bash
git add PROGRESS.md implementation_plan.md
git commit -m "docs: record live deployment and measured retrieval results"
```

---

## Self-Review

**Spec coverage.** §3 architecture → Task 0. §4 filter contract → Tasks 2, 4, 6 (validation). §5 API → Task 6. §6 extraction → Tasks 2, 5. §7 surfaces → Tasks 10, 11. §8 export → Task 7. §9 error handling → Tasks 5 (fallback), 6 (422s), 10 steps 3.5–3.6 (empty state, notice). §10 testing → Tasks 3 (encoder parity), 8 (inferred eval), 9 (service parity), 12 (smoke). §11 constraints → Task 11 step 2 (attribution), Task 12 steps 1 and 6 (anonymity), Task 6 (no logging). §12 post-lock branch → deliberately excluded; it is post-26-Sep work. §13 acceptance → Task 12.

**Gap found and closed:** the spec's MiniLM encoder for `/evidence` episode matching (§8, §14.3) has **no task**. Resolved by deferring it — Task 11's *Try a memory* tab shows extracted chips only, which needs no second encoder. Spec §14.3 already flagged this as droppable; this plan takes that option, removing ~120 MB and a cold-start cost. **If episode similarity is wanted later, it is a new task.**

**Placeholder scan:** none — every code step carries runnable code; Task 10 step 3 and Task 11 specify behaviour precisely because the exact JSX is style, not contract.

**Type consistency:** `extract_clues` returns `{filters, chips, source}` (Task 2); `llm_clues.extract` adds `notice` (Task 5); `main.py` returns that shape directly (Task 6); `lib/api.ts` types match (Task 10). Chip fields `{id, cue, label, filter_key, value, editable}` are identical across Tasks 2, 5, 6 and 10. `SearchContext(ids, matrix, records, encoder)` is constructed identically in Tasks 4, 6 and 9.
