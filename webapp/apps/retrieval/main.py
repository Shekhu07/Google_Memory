"""Public retrieval API.

Visitor-typed text is never logged or persisted - it is read from the request,
used to build a query vector, and dropped.
"""
import json
import os
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Literal

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import llm_clues
from clues import find_conflicts
from encoder import TextEncoder
from cues import build_bank, known
from facets import load_facets
from search import SearchContext, episode_sequence, search

DATA = Path(__file__).resolve().parent / "data"
ALLOWED = {"date_from", "date_to", "location", "category", "episode"}

app = FastAPI(title="Memory Trails retrieval")

RECORDS = [json.loads(line) for line in (DATA / "library.jsonl").open()]
_index = np.load(DATA / "index.npz", allow_pickle=False)
IDS = list(_index["ids"])
MATRIX = _index["matrix"]
FACETS = load_facets(RECORDS)


# "Add one thing you remember" (fixes checklist 2.2): examples of the kinds of thing
# people keep - an event, an object, a person, a type of image - rather than a
# city-and-category filter bar. Each still maps to one filter the library can serve.
DEMO_ANCHORS = [
    {"id": "a1", "cue": "event_anchor", "kind_label": "An event", "label": "graduation",
     "filter_key": "episode", "value": "sister's graduation"},
    {"id": "a2", "cue": "object", "kind_label": "An object", "label": "cake",
     "filter_key": "category", "value": "cake"},
    {"id": "a3", "cue": "object", "kind_label": "People", "label": "family",
     "filter_key": "category", "value": "family"},
    {"id": "a4", "cue": "object", "kind_label": "A type of image", "label": "handwritten note",
     "filter_key": "category", "value": "notes"},
    {"id": "a5", "cue": "event_anchor", "kind_label": "An event", "label": "college performance",
     "filter_key": "episode", "value": "college performance"},
    {"id": "a6", "cue": "object", "kind_label": "A pet", "label": "dog",
     "filter_key": "category", "value": "pet"},
]


def _compute_top_anchors(records: list) -> list[dict]:
    """The demo anchors whose filter value the library can actually serve."""
    have = {"episode": {r.get("episode") for r in records},
            "category": {r.get("category") for r in records}}
    return [a for a in DEMO_ANCHORS if a["value"] in have.get(a["filter_key"], set())]


TOP_ANCHORS = _compute_top_anchors(RECORDS)


SENSITIVE_COVER = {"medicine", "receipt", "document", "screenshot", "notes"}


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
        # The ribbon is seen before the user has chosen anything, so a month's cover
        # is never a medical, money or paperwork photo (fixes checklist 1.2).
        calm = [p for p in photos if p.get("category") not in SENSITIVE_COVER] or photos
        thumb = calm[0].get("file") or f"library/{calm[0]['id'].split(':')[-1]}.jpg"
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


DEMO_TODAY = date.fromisoformat(os.environ.get("DEMO_TODAY", "2026-09-23"))


@lru_cache(maxsize=1)
def encoder() -> TextEncoder:
    """Lazy: a cold start should not pay for the encoder until a query arrives."""
    return TextEncoder(DATA)


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


@lru_cache(maxsize=1)
def groq_client():
    # Rules tie the LLM on the held-out split (0.718 each, re-run 28 Sep) at no latency or token
    # cost; the LLM path is opt-in for experiments only.
    if os.environ.get("EXTRACTOR", "rules") != "llm" or not os.environ.get("GROQ_API_KEY"):
        return None
    os.environ.setdefault("GROQ_LEDGER", "/tmp/groq_usage.json")
    from engine.groq import GroqClient
    return GroqClient(os.environ.get("DEMO_MODEL", "openai/gpt-oss-20b"),
                      daily_cap=int(os.environ.get("DEMO_TOKEN_CAP", "60000")))


class ExtractIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class EpisodeIn(BaseModel):
    episode_id: str = Field(min_length=1, max_length=64)


class SearchIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    filters: dict = Field(default_factory=dict)
    mode: Literal["trails", "soft", "baseline"] = "trails"
    # Session evidence only - rejections are never persisted beyond the request.
    rejected: list[str] = Field(default_factory=list, max_length=50)
    boost_key: str | None = Field(default=None, max_length=32)
    # The current date chip, so the misdated-memory check (F4) knows how the window was
    # read: {"kind": "festival" | None, "alternatives": [[from, to], ...]}.
    date_meta: dict | None = None
    # Visible details the user picked from the suggestions ("orange", "at night").
    seen: list[str] = Field(default_factory=list, max_length=3)


def _validate(filters: dict) -> None:
    bad = set(filters) - ALLOWED
    if bad:
        raise HTTPException(422, f"unsupported filter keys: {sorted(bad)}")
    for key in ("date_from", "date_to"):
        if filters.get(key):
            try:
                date.fromisoformat(filters[key])
            except (ValueError, TypeError):
                raise HTTPException(422, f"{key} must be YYYY-MM-DD")


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


@app.get("/facets")
def facets():
    return {
        "locations": FACETS.locations,
        "categories": FACETS.categories,
        "episodes": FACETS.episodes,
        "top_anchors": TOP_ANCHORS,
        "monthly_chapters": MONTHLY_CHAPTERS,
        "demo_today": DEMO_TODAY.isoformat(),
    }


@app.post("/extract")
def extract(body: ExtractIn):
    text = body.text.strip()
    if not text:
        raise HTTPException(422, "text is required")
    return llm_clues.extract(text, FACETS, groq_client(), today=DEMO_TODAY)


@app.post("/episode")
def episode(body: EpisodeIn):
    """The full surrounding sequence for Screen 4, oldest first."""
    photos = episode_sequence(body.episode_id, RECORDS)
    first = next((r for r in RECORDS if r.get("episode_id") == body.episode_id), None)
    return {
        "episode_id": body.episode_id,
        "episode": (first or {}).get("episode", ""),
        "location": (first or {}).get("location", ""),
        "photos": photos,
        "count": len(photos),
    }


@app.post("/search")
def do_search(body: SearchIn):
    text = body.text.strip()
    if not text:
        raise HTTPException(422, "text is required")
    _validate(body.filters or {})
    bad = [s for s in body.seen if not known(s)]
    if bad:
        raise HTTPException(422, f"unknown visual cues: {bad}")
    ctx = SearchContext(ids=IDS, matrix=MATRIX, records=RECORDS, encoder=encoder(), cues=cue_bank())
    res = search(text, body.filters or {}, body.mode, ctx, rejected=body.rejected,
                 boost_key=body.boost_key, seen=body.seen)
    res["conflicts"] = _conflicts(res, body.date_meta)
    return res


def _conflicts(res: dict, date_meta: dict | None) -> list:
    """F4, computed from the filters this search applied, so it can never describe a clue
    the user removed, and it reports what the first page actually shows."""
    meta = date_meta if isinstance(date_meta, dict) else {}
    out = find_conflicts(res.get("filters_applied") or {}, FACETS, meta)
    first_page = res.get("episodes", [])[:5]
    for c in out:
        lo, hi = c["window"]
        c["shown_episode"] = any(g.get("episode") == c["episode"] for g in first_page)
        c["shown_window"] = any(
            g.get("episode") != c["episode"] and g.get("date_from") and g.get("date_to")
            and (not hi or g["date_from"] <= hi) and (not lo or g["date_to"] >= lo)
            for g in first_page)
    return out
