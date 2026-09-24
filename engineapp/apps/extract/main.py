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
from pydantic import BaseModel, Field

# Vercel's filesystem is read-only; the Groq client writes a token ledger.
os.environ.setdefault("GROQ_LEDGER", "/tmp/groq_usage.json")

DATA = Path(__file__).resolve().parent / "data"
DEMO_MODEL = os.environ.get("DEMO_MODEL", "openai/gpt-oss-20b")
CLOSE = 0.5       # cohort = attempts at least this similar to the visitor's cue profile
FALLBACK_K = 10   # if fewer than MIN_N are that close, show the nearest 10 and say so
MIN_N = 5

app = FastAPI(title="Retrieval discovery engine")

EPISODES = ([json.loads(line) for line in (DATA / "episodes_specific.jsonl").open()]
            if (DATA / "episodes_specific.jsonl").exists() else [])
_client = None


def groq_client():
    global _client
    if _client is None and os.environ.get("GROQ_API_KEY"):
        try:
            from engine.groq import GroqClient
            _client = GroqClient(DEMO_MODEL, daily_cap=int(os.environ.get("DEMO_TOKEN_CAP", "60000")))
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


def _any(text: str, words) -> bool:
    """Whole-word match, so 'kid' never matches 'id' and 'person' never matches 'son'."""
    return re.search(r"\b(?:" + "|".join(re.escape(w) for w in words) + r")\b", text) is not None


DOC_WORDS = ("receipt", "receipts", "bill", "invoice", "prescription", "document", "documents", "id card",
             "aadhaar", "passport", "certificate", "ticket", "notes", "whiteboard", "form")
TIME_WORDS = ("ago", "last year", "last month", "last week", "few years", "couple of years", "summer", "winter",
              "spring", "autumn", "monsoon", "sometime", "recently", "around", "a while back", "years back",
              "birthdays ago", "when i was")
YEARS = tuple(str(y) for y in range(2005, 2027))
MONTHS = ("january", "february", "march", "april", "june", "july", "august", "september", "october",
          "november", "december")
EVENT_WORDS = ("birthday", "birthdays", "wedding", "reception", "party", "anniversary", "trip", "vacation",
               "holiday", "diwali", "holi", "christmas", "eid", "onam", "sick", "hospital", "checkup",
               "meeting", "conference", "graduation", "funeral", "ceremony", "festival")
PLACE_WORDS = ("beach", "hotel", "restaurant", "cafe", "café", "airport", "station", "park", "lake",
               "mountain", "mountains", "office", "clinic", "hospital", "mall", "market", "temple")
PEOPLE_WORDS = ("grandmother", "grandma", "grandfather", "grandpa", "mother", "mom", "mum", "father", "dad",
                "sister", "brother", "cousin", "friend", "friends", "kid", "kids", "daughter", "son", "baby",
                "wife", "husband", "colleague", "colleagues", "family", "me and")
OBJECT_WORDS = ("car", "cake", "medicine", "tablet", "tablets", "parking", "laptop", "phone", "bike", "shoes",
                "dress", "flower", "flowers", "chair", "table", "dog", "puppy", "cat", "food", "tree", "trees")
TEXT_WORDS = ("text", "word", "words", "sign", "label", "quote", "written", "serial number", "number plate")


def rules_profile(memory: str) -> dict:
    """Deterministic keyword fallback when the model path is unavailable. Whole words only."""
    t = memory.lower()
    if _any(t, ("screenshot", "screenshots", "screen shot")):
        asset_type = "screenshot"
    elif _any(t, DOC_WORDS):
        asset_type = "document_receipt"
    elif _any(t, ("video", "videos", "recording", "clip")):
        asset_type = "video"
    else:
        asset_type = "photo"

    cues = []
    exact = (re.search(r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b", t)
             or re.search(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b", t))
    if exact:
        cues.append("exact_date")
    elif (_any(t, TIME_WORDS) or _any(t, YEARS) or _any(t, MONTHS)
          or re.search(r"\b(?:in|during|around|early|mid|late|last|this)\s+may\b", t)):
        cues.append("temporal_approx")
    if _any(t, EVENT_WORDS):
        cues.append("event_anchor")
    if _any(t, PLACE_WORDS) or re.search(r"\b(?:in|at|near)\s+[A-Z][a-z]+", memory):
        cues.append("place_named")
    if _any(t, PEOPLE_WORDS):
        cues.append("who_with")
    if _any(t, OBJECT_WORDS):
        cues.append("object")
    if _any(t, TEXT_WORDS) or asset_type == "screenshot":
        cues.append("text_in_image")

    # Only what the wording implies was lost: no exact date given means the date is not known.
    cues_lost = [] if exact else ["date"]
    return {"asset_type": asset_type, "cues_retained": cues, "cues_lost": cues_lost, "query_verbatim": ""}


def _score(q: dict, ep: dict) -> float:
    a, b = set(q.get("cues_retained") or []), set(ep.get("cues_retained") or [])
    score = len(a & b) / len(a | b) if (a | b) else 0.0
    if q.get("asset_type") not in (None, "unknown", "multiple", "photo") and q.get("asset_type") == ep.get("asset_type"):
        score += 0.2
    return score


def cohort_for(q: dict, episodes: list) -> tuple:
    """Closest real attempts only. Returns (cohort, rule) where rule says how it was chosen."""
    if not q.get("cues_retained"):
        return [], "no remembered cue to match on: add when, where, who or what it showed"
    scored = sorted(((_score(q, ep), ep) for ep in episodes), key=lambda t: -t[0])
    close = [ep for s, ep in scored if s >= CLOSE]
    if len(close) >= MIN_N:
        return close, f"attempts with a similar memory profile (similarity ≥ {CLOSE})"
    nearest = [ep for s, ep in scored if s > 0][:FALLBACK_K]
    return nearest, f"the {len(nearest)} nearest attempts (few were closely similar)"


def summarise(cohort: list, rule: str) -> dict:
    return {
        "n": len(cohort),
        "rule": rule,
        "stages": dict(Counter(e.get("failure_stage") for e in cohort if e.get("failure_stage")).most_common()),
        "outcomes": dict(Counter(e.get("outcome") for e in cohort if e.get("outcome")).most_common()),
    }


def _quotable(e: dict) -> bool:
    """Same rule as the evidence tables: verified failures only, no app-update path complaints."""
    return (bool(e.get("evidence")) and e.get("evidence_verified") is not False
            and e.get("outcome") != "found_fast" and e.get("failure_stage") not in ("none", "browse_path_changed"))


def pick_quotes(cohort: list, k: int = 3) -> list:
    keep = [e for e in cohort if _quotable(e)]  # cohort order = similarity order
    keep.sort(key=lambda e: (not (e.get("cues_retained") and e.get("cues_lost")), e.get("outcome") != "not_found"))
    return [{
        "evidence": e.get("evidence", ""),
        "source": {"playstore": "Play Store", "appstore": "App Store", "reddit": "Reddit",
                   "youtube": "YouTube"}.get(e.get("source"), e.get("source")),
        "date": (e.get("date") or "")[:10],
        "era": e.get("era", ""),
        "failure_stage": e.get("failure_stage", ""),
        "outcome": e.get("outcome", "unknown"),
    } for e in keep[:k]]


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
        "model": DEMO_MODEL,
        "manifest": manifest,
    }


@app.post("/diagnose")
def diagnose(body: ExtractIn):
    memory = body.text.strip()
    if not memory:
        raise HTTPException(422, "text is required")

    client = groq_client()
    fallback_reason = None
    if client:
        try:
            q = extract_memory(client, memory)
            source = "pipeline_prompt"
        except Exception as exc:          # the type only - never the visitor's text
            q, source, fallback_reason = rules_profile(memory), "rules", type(exc).__name__
    else:
        q, source, fallback_reason = rules_profile(memory), "rules", "no_model_configured"

    cohort, rule = cohort_for(q, EPISODES)
    profile = {k: q.get(k) for k in ("asset_type", "cues_retained", "cues_lost", "query_verbatim")}

    chips = [{"id": f"retained_{c}", "cue": c, "label": c.replace("_", " "), "type": "retained"}
             for c in profile.get("cues_retained") or []]
    chips += [{"id": f"lost_{c}", "cue": c, "label": c.replace("_", " "), "type": "lost"}
              for c in profile.get("cues_lost") or []]

    return {
        "profile": profile,
        "chips": chips,
        "source": source,
        "model": DEMO_MODEL if source == "pipeline_prompt" else None,
        "fallback_reason": fallback_reason,
        "cohort": summarise(cohort, rule),
        "quotes": pick_quotes(cohort),
    }


@app.post("/extract")
def extract_endpoint(body: ExtractIn):
    return diagnose(body)
