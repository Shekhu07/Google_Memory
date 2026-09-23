"""Discovery engine API — real evidence diagnostic & cohort matching.

Deliberately separate from the MVP's retrieval service. This service runs the
pipeline's extraction schema on a visitor's memory and matches a cohort against
the 144 verified retrieval attempts, reporting real evidence instead of fabricated
risk figures.

Visitor-typed text is never logged or persisted.
"""
import json
import os
import re
from collections import Counter
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure Vercel's read-only filesystem does not fail when writing token usage
os.environ.setdefault("GROQ_LEDGER", "/tmp/groq_usage.json")

DATA = Path(__file__).resolve().parent / "data"

app = FastAPI(title="Retrieval discovery engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EPISODES = [json.loads(line) for line in (DATA / "episodes_specific.jsonl").open()] if (DATA / "episodes_specific.jsonl").exists() else []
_client = None


def groq_client():
    global _client
    if _client is None and os.environ.get("GROQ_API_KEY"):
        try:
            from engine.groq import GroqClient
            _client = GroqClient(os.environ.get("DEMO_MODEL", "openai/gpt-oss-20b"),
                                 daily_cap=int(os.environ.get("DEMO_TOKEN_CAP", "60000")))
        except Exception:
            _client = None
    return _client


def extract_memory(client, memory: str) -> dict:
    """Run the pipeline's own extraction prompt on a user's description."""
    from engine.common import era_for
    from engine.extract import SYSTEM, format_batch, parse_results
    today = date.today().isoformat()
    src = {"id": "query", "source": "demo", "date": today, "era": era_for(today), "text": memory}
    results = parse_results(client.chat_json(SYSTEM, format_batch([src]), max_tokens=2000), [src])
    if not results:
        raise ValueError("The model returned no usable extraction.")
    return results[0]


def rules_profile(memory: str) -> dict:
    """Deterministic keyword fallback when Groq is unavailable or unconfigured."""
    text_lower = memory.lower()
    if "screenshot" in text_lower:
        asset_type = "screenshot"
    elif any(w in text_lower for w in ("receipt", "bill", "invoice", "prescription", "document", "id", "passport", "card", "notes", "whiteboard")):
        asset_type = "document_receipt"
    elif any(w in text_lower for w in ("video", "recording", "clip")):
        asset_type = "video"
    else:
        asset_type = "photo"

    cues_retained = []
    if any(w in text_lower for w in ("ago", "last year", "last month", "few years", "summer", "winter", "spring", "fall", "autumn", "sometime", "recently", "around", "ish")):
        cues_retained.append("temporal_approx")
    elif any(w in text_lower for w in ("2020", "2021", "2022", "2023", "2024", "2025", "2026", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")):
        cues_retained.append("temporal_approx")

    if re.search(r"\b\d{1,2}(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", text_lower) or re.search(r"\b(20\d\d-\d\d-\d\d)\b", text_lower):
        cues_retained.append("exact_date")

    if any(w in text_lower for w in ("birthday", "wedding", "reception", "party", "anniversary", "trip", "vacation", "holiday", "diwali", "christmas", "sick", "hospital", "checkup", "meeting", "conference", "graduation", "funeral", "ceremony")):
        cues_retained.append("event_anchor")

    known_places = ("pune", "goa", "bengaluru", "bangalore", "delhi", "mumbai", "udaipur", "paris", "london", "beach", "hotel", "restaurant", "cafe", "airport", "station", "park", "lake", "mountain", "home", "office", "vet", "clinic", "hospital", "mall", "market")
    if any(p in text_lower for p in known_places):
        cues_retained.append("place_named")

    if any(w in text_lower for w in ("grandmother", "grandma", "grandfather", "grandpa", "mother", "mom", "father", "dad", "sister", "brother", "cousin", "friend", "friends", "kid", "kids", "daughter", "son", "baby", "wife", "husband", "dog", "puppy", "cat", "pet", "colleague")):
        cues_retained.append("who_with")

    if any(w in text_lower for w in ("car", "cake", "medicine", "parking", "spot", "whiteboard", "laptop", "phone", "bike", "shoes", "dress", "flower", "tulip", "chair", "table", "armoire", "cabinet")):
        cues_retained.append("object")

    if any(w in text_lower for w in ("text", "word", "words", "sign", "label", "notes", "quote", "receipt", "screenshot")):
        cues_retained.append("text_in_image")

    cues_lost = []
    if "exact_date" not in cues_retained:
        cues_lost.append("date")
    if not any(w in text_lower for w in ("album", "folder")):
        cues_lost.append("album")

    return {
        "asset_type": asset_type,
        "cues_retained": cues_retained,
        "cues_lost": cues_lost,
        "query_verbatim": "",
    }


def cohort_for(q: dict, episodes: list) -> list:
    """Match a cohort from the 144 by structure. Rank by Jaccard on cues_retained + 0.2 if specific asset_type matches."""
    target_cues = set(q.get("cues_retained") or [])
    target_asset = q.get("asset_type")
    scored = []
    for ep in episodes:
        ep_cues = set(ep.get("cues_retained") or [])
        shared = target_cues & ep_cues
        union = target_cues | ep_cues
        jaccard = len(shared) / len(union) if union else 0.0
        score = jaccard
        if target_asset and target_asset not in ("unknown", "multiple") and target_asset == ep.get("asset_type"):
            score += 0.2
        if shared or (not target_cues and score > 0):
            scored.append((score, ep))
    scored.sort(key=lambda t: -t[0])
    return [ep for s, ep in scored]


def summarise(cohort: list) -> dict:
    n = len(cohort)
    stages = Counter(e.get("failure_stage") for e in cohort if e.get("failure_stage"))
    outcomes = Counter(e.get("outcome") for e in cohort if e.get("outcome"))
    return {
        "n": n,
        "stages": dict(stages.most_common()),
        "outcomes": dict(outcomes.most_common()),
    }


def pick(e: dict) -> dict:
    return {
        "evidence": e.get("evidence", ""),
        "source": e.get("source", "play_store"),
        "date": e.get("date", ""),
        "era": e.get("era", ""),
        "failure_stage": e.get("failure_stage", ""),
        "outcome": e.get("outcome", "unknown"),
    }


class ExtractIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


@app.get("/health")
def health():
    manifest_path = DATA / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    return {
        "service": "discovery-engine",
        "episodes_loaded": len(EPISODES),
        "groq": bool(os.environ.get("GROQ_API_KEY")),
        "manifest": manifest,
    }


@app.post("/diagnose")
def diagnose(body: ExtractIn):
    memory = body.text.strip()
    if not memory:
        raise HTTPException(422, "text is required")

    client = groq_client()
    try:
        if client:
            q = extract_memory(client, memory)
            source = "pipeline_prompt"
        else:
            q = rules_profile(memory)
            source = "rules"
    except Exception:
        q = rules_profile(memory)
        source = "rules"

    cohort = cohort_for(q, EPISODES)
    profile = {k: q.get(k) for k in ("asset_type", "cues_retained", "cues_lost", "query_verbatim")}

    chips = []
    for c in profile.get("cues_retained", []):
        chips.append({"id": f"retained_{c}", "cue": c, "label": c.replace("_", " "), "type": "retained"})
    for c in profile.get("cues_lost", []):
        chips.append({"id": f"lost_{c}", "cue": c, "label": c.replace("_", " "), "type": "lost"})

    return {
        "profile": profile,
        "chips": chips,
        "source": source,
        "cohort": summarise(cohort),
        "quotes": [pick(e) for e in cohort[:3]],
    }


@app.post("/extract")
def extract_endpoint(body: ExtractIn):
    return diagnose(body)
