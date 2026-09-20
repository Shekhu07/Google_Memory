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
from search import SearchContext, search

DATA = Path(__file__).resolve().parent / "data"
ALLOWED = {"date_from", "date_to", "location", "category", "episode"}

app = FastAPI(title="Memory Trails retrieval")

RECORDS = [json.loads(line) for line in (DATA / "library.jsonl").open()]
_index = np.load(DATA / "index.npz", allow_pickle=False)
IDS = list(_index["ids"])
MATRIX = _index["matrix"]
FACETS = load_facets(RECORDS)


@lru_cache(maxsize=1)
def encoder() -> TextEncoder:
    """Lazy: a cold start should not pay for the encoder until a query arrives."""
    return TextEncoder(DATA)


@lru_cache(maxsize=1)
def groq_client():
    if not os.environ.get("GROQ_API_KEY"):
        return None
    from engine.groq import GroqClient
    return GroqClient(os.environ.get("DEMO_MODEL", "openai/gpt-oss-20b"),
                      daily_cap=int(os.environ.get("DEMO_TOKEN_CAP", "60000")))


class ExtractIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class SearchIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    filters: dict = Field(default_factory=dict)
    mode: Literal["trails", "baseline"] = "trails"


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
        "groq": bool(os.environ.get("GROQ_API_KEY")),
        "manifest": json.loads((DATA / "manifest.json").read_text()),
    }


@app.post("/extract")
def extract(body: ExtractIn):
    text = body.text.strip()
    if not text:
        raise HTTPException(422, "text is required")
    return llm_clues.extract(text, FACETS, groq_client())


@app.post("/search")
def do_search(body: SearchIn):
    text = body.text.strip()
    if not text:
        raise HTTPException(422, "text is required")
    _validate(body.filters or {})
    ctx = SearchContext(ids=IDS, matrix=MATRIX, records=RECORDS, encoder=encoder())
    return search(text, body.filters or {}, body.mode, ctx)
