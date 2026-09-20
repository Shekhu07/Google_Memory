"""Search over the pre-embedded library, grouped into visual episodes.

Filtering and ranking delegate to engine.demo_index, so the deployed service cannot
diverge from the numbers measured offline. Grouping and explanation live here.
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
    """Evidence labels only: which filter fired, on what value. Never a generated rationale."""
    out = [f'{FILTER_LABELS[k]} "{v}"' for k, v in filters.items() if k in FILTER_LABELS and v]
    if filters.get("date_from") and filters.get("date_to"):
        out.append(f'taken between {filters["date_from"]} and {filters["date_to"]}')
    return out


def group_by_episode(scored: list, records: list) -> list:
    """Flat ranked hits -> visual episodes, ordered by their best-matching photo."""
    by_id = {r["id"]: r for r in records}
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
            }
        day = (r.get("date") or "")[:10]
        if day:
            g["date_from"] = day if g["date_from"] is None else min(g["date_from"], day)
            g["date_to"] = day if g["date_to"] is None else max(g["date_to"], day)
        g["count"] += 1
        g["top_score"] = max(g["top_score"], float(score))
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
