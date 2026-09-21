"""Discovery engine API — clue extraction only.

Deliberately separate from the MVP's retrieval service. This one runs the
pipeline's own extractor on a visitor's sentence, which is the workflow the
case study's Discovery Engine deliverable asks to be testable. It needs no CLIP
encoder, no image vectors and no photo library beyond the facet vocabulary, so
the whole service is a couple of megabytes.

Visitor-typed text is never logged or persisted.
"""
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import llm_clues
from facets import load_facets

DATA = Path(__file__).resolve().parent / "data"

app = FastAPI(title="Retrieval discovery engine")

RECORDS = [json.loads(line) for line in (DATA / "library.jsonl").open()]
FACETS = load_facets(RECORDS)
_client = None


def groq_client():
    global _client
    if _client is None and os.environ.get("GROQ_API_KEY"):
        from engine.groq import GroqClient
        _client = GroqClient(os.environ.get("DEMO_MODEL", "openai/gpt-oss-20b"),
                             daily_cap=int(os.environ.get("DEMO_TOKEN_CAP", "60000")))
    return _client


class ExtractIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


@app.get("/health")
def health():
    return {
        "service": "discovery-engine",
        "vocabulary": {
            "locations": len(FACETS.locations),
            "episodes": len(FACETS.episodes),
            "categories": len(FACETS.categories),
        },
        "groq": bool(os.environ.get("GROQ_API_KEY")),
        "manifest": json.loads((DATA / "manifest.json").read_text()),
    }


@app.post("/extract")
def extract(body: ExtractIn):
    text = body.text.strip()
    if not text:
        raise HTTPException(422, "text is required")
    return llm_clues.extract(text, FACETS, groq_client())
