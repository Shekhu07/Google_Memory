"""Extraction: turn each relevant post into a structured retrieval record.

The unit is a *retrieval episode* (one attempt to find one photo). Many app
reviews are general complaints instead; `specificity` records which, so both
can be compared without pretending a complaint is an episode.

Every field is validated against a closed vocabulary; unknown values are
dropped rather than trusted. The evidence quote must appear verbatim in the
post, otherwise `evidence_verified` is false (a cheap hallucination check the
audit step reports on).

Shares gpt-oss-120b's free-tier daily budget with Gate B. Resumable.

Usage:
  .venv/bin/python -m engine.extract
  .venv/bin/python -m engine.extract --limit 10
"""
import argparse
import json
import re
import sys
from collections import Counter

from engine.common import ROOT, append_jsonl, load_ids
from engine.gate_a import OUT as CANDIDATES
from engine.gate_b import OUT as GATE_B
from engine.groq import DailyBudgetReached, GroqClient, split_on_json_failure

MODEL = "openai/gpt-oss-120b"
OUT = ROOT / "data" / "interim" / "episodes.jsonl"
MAX_CHARS = 1500
SCHEMA_VERSION = "v3-sep17"
# Groq schedules on a request's *expected* output size, so over-reserving puts the
# call in a slow lane. Measured Sep 20: a real batch of 5 emits about 780 completion
# tokens, and asking for 6000 stalled extraction to ~20 posts/hour. 2000 leaves ~2.5x
# headroom for unusually long posts without the queueing penalty.
MAX_TOKENS = 2000

VOCAB = {
    "specificity": ["specific_attempt", "general_complaint"],
    "asset_type": ["photo", "screenshot", "document_receipt", "medicine_label", "video", "multiple", "unknown"],
    "cues_retained": ["temporal_approx", "exact_date", "event_anchor", "place_named", "place_unnamed",
                      "who_with", "activity", "object", "text_in_image", "appearance_colour",
                      "device_or_app_source", "emotional", "sequence", "own_label_or_caption"],
    "cues_lost": ["date", "place", "album", "people", "exact_words", "filename"],
    "failure_stage": ["cannot_express", "system_misunderstood", "not_surfaced", "cannot_evaluate_results",
                      "cannot_refine", "browse_path_changed", "slow_or_broken_ui", "abandoned", "none"],
    "workaround": ["date_scroll", "manual_scroll", "albums_or_folders", "other_app", "ask_someone",
                   "old_app_version", "classic_search_toggle", "gave_up", "none_mentioned"],
    "outcome": ["found_fast", "found_slow", "not_found", "unknown"],
    "query_language": ["en", "hinglish_code_mixed", "hi", "other", "no_query"],
    "search_mode": ["ask_photos_or_ai", "classic", "both_compared", "not_mentioned"],
    # H1-H5 pre-registered Sep 17. H6 emerged from the 10-post extraction trial the same day
    # and is reported separately as a post-hoc hypothesis.
    "hypotheses": ["H1", "H2", "H3", "H4", "H5", "H6"],
}

SYSTEM = f"""You extract structured data from user comments and app reviews about finding photos in Google Photos (or a similar photo app). Each item has already been judged relevant to finding/searching photos.

For each item return one object. Use ONLY the listed values. When the text doesn't say, use "unknown", "none", "none_mentioned", "not_mentioned" or an empty list. Never guess beyond the text.

- specificity: "specific_attempt" if the writer describes trying to find a particular photo/video/screenshot or set (e.g. "the receipt from last year", "pics from Nov 2023"); "general_complaint" if it's about search/finding in general.
- asset_type: {VOCAB["asset_type"]}
- cues_retained (what the person still remembered or used to search; list): {VOCAB["cues_retained"]}
  text_in_image = words that appear inside the photo (signs, documents, screenshots), including searching for a word to find it; temporal_approx = rough time ("last year", "summer"); event_anchor = tied to a life event ("when I was sick", "Diwali", "my wedding"); sequence = "right before/after X"; own_label_or_caption = names/descriptions they added themselves.
  Fill cues_retained and query_verbatim for general complaints too when they say what they search by (e.g. "I used to search the word 'green' and find it on signs" -> text_in_image, query "green"; "searching people's names" -> own_label_or_caption or who_with).
- cues_lost (what they explicitly didn't know; list): {VOCAB["cues_lost"]}
- query_verbatim: the exact search words they typed if quoted or clearly stated, else "".
- failure_stage (where it broke): {VOCAB["failure_stage"]}
  cannot_express = didn't know how to phrase it or what's searchable; system_misunderstood = query run but wrong/irrelevant/zero results; not_surfaced = photo exists but never appears; cannot_evaluate_results = results shown but too many/similar to spot it; cannot_refine = no way to narrow or correct after a miss; browse_path_changed = an update moved/removed the folders, albums, People view or layout they used to reach photos; slow_or_broken_ui = lag, crashes, can't scroll results; abandoned = gave up without a clear stage.
- workaround: {VOCAB["workaround"]}
- outcome: {VOCAB["outcome"]}. Use "unknown" unless the text says whether and how they found it; general complaints are almost always "unknown".
- query_language: {VOCAB["query_language"]}. "no_query" if no search words are given.
- search_mode: {VOCAB["search_mode"]}. Only "ask_photos_or_ai" if they mention AI, Ask Photos, Gemini or a conversational answer; only "classic" if they explicitly mean the old/classic/keyword search. Otherwise "not_mentioned".
- hypotheses (which research explanations this item is CLEARLY evidence for; list; empty is normal and fine):
  H1 episodic time: the main surviving cue is a relative time or life event, and search couldn't use it.
  H2 recognition: they got a plausible result set but couldn't pick the target out (too many, near-duplicates, small thumbnails).
  H3 dead end: zero/poor results and no idea what to try next.
  H4 language: a code-mixed/transliterated/non-English query was misread. Never for English queries.
  H5 nothing to index: a utility photo (receipt, document, medicine, screenshot) with no faces/place/text search could latch onto.
  H6 learned path broken: they used to reach photos through a specific route (folders, People & Pets, albums, timeline layout, a search that worked) and an app change removed or moved it.
  H3 needs an actual miss with no way forward; a general "search is worse" complaint is not H3 by itself.
- evidence: the single most informative quote, copied EXACTLY from the text as one continuous span, max 25 words. No "...", no paraphrasing, no joining separate sentences.
- confidence: 0.0-1.0, how clearly the text supports the extraction.

Return JSON: {{"results": [{{"id": "<id>", "specificity": ..., "asset_type": ..., "cues_retained": [...], "cues_lost": [...], "query_verbatim": ..., "failure_stage": ..., "workaround": ..., "outcome": ..., "query_language": ..., "search_mode": ..., "hypotheses": [...], "evidence": ..., "confidence": ...}}]}}"""

SINGLE = {"specificity": "general_complaint", "asset_type": "unknown", "failure_stage": "none",
          "workaround": "none_mentioned", "outcome": "unknown", "query_language": "no_query",
          "search_mode": "not_mentioned"}
LISTS = {"cues_retained": "cues_retained", "cues_lost": "cues_lost", "hypotheses": "hypotheses"}


def _norm(text: str) -> str:
    """Compare quotes ignoring case and all whitespace ("pictures&" vs "pictures &")."""
    return re.sub(r"\s+", "", text).lower()


def validate(item: dict, src: dict) -> dict:
    """Coerce a model result into the closed schema. Invalid values fall back to defaults."""
    rec = {"id": src["id"], "source": src["source"], "date": src["date"], "era": src["era"]}
    for field, default in SINGLE.items():
        value = item.get(field)
        rec[field] = value if value in VOCAB[field] else default
    for field, vocab in LISTS.items():
        values = item.get(field) if isinstance(item.get(field), list) else []
        rec[field] = sorted({v for v in values if v in VOCAB[vocab]})
    rec["query_verbatim"] = str(item.get("query_verbatim") or "")[:200]
    evidence = str(item.get("evidence") or "")[:300]
    rec["evidence"] = evidence
    rec["evidence_verified"] = bool(evidence) and _norm(evidence) in _norm(src["text"])
    try:
        rec["confidence"] = min(max(float(item.get("confidence", 0)), 0.0), 1.0)
    except (TypeError, ValueError):
        rec["confidence"] = 0.0
    rec["model"] = MODEL
    rec["schema"] = SCHEMA_VERSION
    return rec


def parse_results(response: dict, batch: list) -> list:
    by_id = {r["id"]: r for r in batch}
    out = []
    for item in response.get("results", []):
        src = by_id.pop(item.get("id"), None)
        if src:
            out.append(validate(item, src))
    return out


def format_batch(batch: list) -> str:
    return json.dumps([{"id": r["id"], "text": r["text"][:MAX_CHARS],
                        **({"video_title": r["context_title"]} if r.get("context_title") else {})}
                       for r in batch], ensure_ascii=False)


def relevant_posts() -> list:
    """Gate B 'relevant' posts joined to their text, in Gate A priority order."""
    if not GATE_B.exists():
        return []
    relevant = {json.loads(l)["id"] for l in GATE_B.open() if json.loads(l)["label"] == "relevant"}
    return [c for c in (json.loads(l) for l in CANDIDATES.open()) if c["id"] in relevant]


def select_todo(posts: list, done: set, source: str = "", limit: int = 0) -> list:
    """Posts still to extract, optionally narrowed to one source.

    Added Sep 20: `relevant_posts()` interleaves sources by Gate A priority, but when
    the daily budget only covers part of the queue the cheap-and-dense source should
    go first. Reddit costs about the same per post as an app-store review and is far
    likelier to carry a specific attempt with a stated outcome.
    """
    todo = [r for r in posts if r["id"] not in done]
    if source:
        todo = [r for r in todo if r["source"] == source]
    return todo[:limit] if limit else todo


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--batch", type=int, default=5)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--source", default="",
                   help="extract only this source (e.g. reddit) - use when the daily budget is tight")
    args = p.parse_args(argv)

    posts = relevant_posts()
    done = load_ids(OUT)
    todo = select_todo(posts, done, args.source, args.limit)
    client = GroqClient(MODEL)
    print(f"{len(done)} extracted, {len(todo)} to go; {client.used_today()} {MODEL} tokens used today")

    extracted = 0
    try:
        for i in range(0, len(todo), args.batch):
            batch = todo[i: i + args.batch]
            results = split_on_json_failure(
                lambda b: parse_results(client.chat_json(SYSTEM, format_batch(b), max_tokens=MAX_TOKENS), b), batch)
            append_jsonl(OUT, results)
            extracted += len(results)
            if (i // args.batch) % 10 == 0:
                print(f"  {extracted:>5} extracted this run | {client.used_today():>7} tokens today")
    except DailyBudgetReached as e:
        print(f"\nStopped at daily token cap: {e}. Rerun tomorrow to continue.")

    rows = [json.loads(l) for l in OUT.open()] if OUT.exists() else []
    print(f"\nextracted this run: {extracted} | total: {len(rows)} | "
          f"{dict(Counter(r['specificity'] for r in rows))} | "
          f"evidence verified: {sum(r['evidence_verified'] for r in rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
