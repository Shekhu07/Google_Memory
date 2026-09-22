"""Search over the pre-embedded library, grouped into visual episodes.

Filtering and ranking delegate to engine.demo_index, so the deployed service cannot
diverge from the numbers measured offline. Grouping and explanation live here.
"""
from collections import Counter
from dataclasses import dataclass
from datetime import date

from engine.demo_index import apply_filters, baseline_search, outside_window_photos, rank, soft_search

REASON_KINDS = ("episode", "location", "category")


@dataclass
class SearchContext:
    ids: list
    matrix: object
    records: list
    encoder: object


def why_strings(filters: dict) -> list:
    """Structured evidence: which filter fired, on what value.

    Deliberately not prose. The client renders these as noun phrases ("Goa location",
    "Photos grouped around 8-11 Dec 2023") so dates can be written the way a person
    reads them. Never a generated rationale, never a confidence score.
    """
    out = [{"kind": k, "value": v} for k in REASON_KINDS for _k, v in [(k, filters.get(k))] if v]
    if filters.get("date_from") and filters.get("date_to"):
        out.append({"kind": "date_window", "value": filters["date_from"], "to": filters["date_to"]})
    return out


def episode_facts(episode_id: str, records: list) -> dict:
    """Density cues for the card: places, scene mix, how long the moment ran.

    These let someone judge an episode without opening it, which is the
    not_surfaced failure (41.7%) addressed at the card level.
    """
    rows = [r for r in records if r.get("episode_id") == episode_id] if episode_id else []
    days = sorted((r.get("date") or "")[:10] for r in rows if r.get("date"))
    span = 0
    if len(days) > 1:
        try:
            span = (date.fromisoformat(days[-1]) - date.fromisoformat(days[0])).days
        except ValueError:
            span = 0
    return {
        "places": len({r.get("location") for r in rows if r.get("location")}),
        "scenes": Counter(r["category"] for r in rows if r.get("category")).most_common(3),
        "span_days": span,
    }


def usefulness(coverage: float, coherence: float, recognizability: float, evidence: float) -> float:
    """Episode usefulness = coverage x coherence x recognizability x evidence quality.

    An internal ranking principle, never shown as a score. The UI explains the
    contributing evidence in words instead.
    """
    return coverage * coherence * recognizability * evidence


def episode_sequence(episode_id: str, records: list) -> list:
    """Every photo in an episode, oldest first - the sequence Screen 4 scrubs.

    Screen 4 exists so the user re-enters the surrounding moment rather than
    landing on one isolated result, so this is deliberately not limited to hits.
    """
    if not episode_id:
        return []
    rows = [r for r in records if r.get("episode_id") == episode_id]
    rows.sort(key=lambda r: r.get("date") or "")
    return [{"id": r["id"], "file": r.get("file", ""), "date": (r.get("date") or "")[:10],
             "location": r.get("location", "")} for r in rows]


def _coherence(named: bool, span_days: int) -> float:
    """A named moment with a tight span hangs together; a loose photo does not."""
    base = 1.0 if named else 0.55
    if span_days <= 7:
        return base
    return base * (0.85 if span_days <= 30 else 0.7)


def _recognizability(total: int) -> float:
    """One photo is hard to recognize a moment from; four or more is enough."""
    return min(1.0, 0.4 + 0.15 * total)


DIMENSION_NAMES = {"location": "Place", "category": "Scene", "episode": "Event",
                   "date_window": "Date"}

# Certainty is per dimension, never one global number. A candidate can have strong
# place evidence, possible scene evidence and an approximate date at the same time.
DIMENSION_CERTAINTY = {"location": "strong", "episode": "strong",
                       "category": "possible", "date_window": "approximate"}

DIMENSION_SOURCE = {
    "location": "From the place recorded on these photos.",
    "episode": "From photos taken close together in time.",
    "category": "From what the images look like, not from any label you gave.",
    "date_window": "Your wording gave a range, not an exact day.",
}


def evidence_detail(reasons: list) -> list:
    """The expandable "See evidence" view: what fired, how certain, where it came from."""
    out = []
    for r in reasons:
        kind = r["kind"]
        out.append({
            "dimension": DIMENSION_NAMES.get(kind, kind),
            "value": r["value"] if kind != "date_window" else f'{r["value"]} to {r["to"]}',
            "certainty": DIMENSION_CERTAINTY.get(kind, "possible"),
            "source": DIMENSION_SOURCE.get(kind, ""),
        })
    return out


def group_by_episode(scored: list, records: list, filters: dict = None,
                     reasons: list = None) -> list:
    """Flat ranked hits -> visual episodes, ranked by usefulness rather than by
    the single best-matching photo."""
    by_id = {r["id"]: r for r in records}
    sizes = {}
    for r in records:
        key = r.get("episode_id")
        if key:
            sizes[key] = sizes.get(key, 0) + 1
    groups = {}
    for pid, score in scored:
        r = by_id.get(pid)
        if r is None:
            continue
        key = r.get("episode_id") or f"stray:{pid}"
        g = groups.get(key)
        if g is None:
            g = groups[key] = {
                "episode_id": r.get("episode_id", ""),
                "episode": r.get("episode") or "Other photos",
                "location": r.get("location", ""),
                "date_from": None, "date_to": None,
                "count": 0, "photos": [], "top_score": float(score), "why": [],
                # The card shows how big the episode really is; "count" is how many matched.
                "episode_total": sizes.get(r.get("episode_id"), 1),
                **{k: v for k, v in episode_facts(r.get("episode_id", ""), records).items()},
            }
        day = (r.get("date") or "")[:10]
        if day:
            g["date_from"] = day if g["date_from"] is None else min(g["date_from"], day)
            g["date_to"] = day if g["date_to"] is None else max(g["date_to"], day)
        g["count"] += 1
        g["top_score"] = max(g["top_score"], float(score))
        g["photos"].append({"id": pid, "file": r.get("file", "")})

    filters = filters or {}
    reasons = reasons or []
    dims = [k for k in ("episode", "location", "category") if filters.get(k)]
    if filters.get("date_from"):
        dims.append("date")
    best = max((g["top_score"] for g in groups.values()), default=1.0) or 1.0

    for g in groups.values():
        # Cue coverage blends the metadata clues that fired with how well the
        # episode matches the words the user actually used.
        filter_cover = 1.0 if not dims else len(dims) / len(dims)
        semantic = max(0.0, g["top_score"]) / best if best else 0.0
        coverage = 0.5 * filter_cover + 0.5 * semantic
        g["usefulness"] = round(usefulness(
            coverage,
            _coherence(bool(g["episode_id"]), g.get("span_days", 0)),
            _recognizability(g["episode_total"]),
            min(1.0, 0.6 + 0.1 * len(reasons)),
        ), 4)

    return sorted(groups.values(), key=lambda g: (-g["usefulness"], -g["top_score"]))


def search(text: str, filters: dict, mode: str, ctx: SearchContext, top_k: int = 20,
           rejected: list = None) -> dict:
    applied = {} if mode == "baseline" else {k: v for k, v in (filters or {}).items() if v}
    qv = ctx.encoder.encode([text])

    if mode == "soft":
        scored = soft_search(qv, ctx.ids, ctx.matrix, ctx.records, top_k=top_k, **applied)
    elif mode == "baseline":
        scored = baseline_search(qv, ctx.ids, ctx.matrix, top_k=top_k)
    else:
        allowed = None
        if applied:
            allowed = {r["id"] for r in apply_filters(ctx.records, **applied)}
        scored = rank(qv, ctx.ids, ctx.matrix, allowed=allowed, top_k=top_k)

    reasons = why_strings(applied)
    groups = group_by_episode(scored, ctx.records, applied, reasons)

    # A rejection is session evidence, not a preference: drop it from this pass only.
    skip = set(rejected or [])
    if skip:
        groups = [g for g in groups if g["episode_id"] not in skip]

    detail = evidence_detail(reasons)
    for g in groups:
        g["why"] = list(reasons)
        g["evidence"] = list(detail)

    outside = []
    if applied.get("date_from") or applied.get("date_to"):
        outside = outside_window_photos(qv, ctx.ids, ctx.matrix, ctx.records, limit=5, **applied)

    return {"episodes": groups, "total": sum(g["count"] for g in groups),
            "mode": mode, "filters_applied": applied, "outside_window": outside}
