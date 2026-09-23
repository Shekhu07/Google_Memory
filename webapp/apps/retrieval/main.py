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
from encoder import TextEncoder
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


DEMO_TODAY = date.fromisoformat(os.environ.get("DEMO_TODAY", "2026-09-23"))


@lru_cache(maxsize=1)
def encoder() -> TextEncoder:
    """Lazy: a cold start should not pay for the encoder until a query arrives."""
    return TextEncoder(DATA)


@lru_cache(maxsize=1)
def groq_client():
    # Rules won on the held-out split (0.818 vs 0.718); the LLM path is opt-in for experiments only.
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
    ctx = SearchContext(ids=IDS, matrix=MATRIX, records=RECORDS, encoder=encoder())
    return search(text, body.filters or {}, body.mode, ctx, rejected=body.rejected, boost_key=body.boost_key)
