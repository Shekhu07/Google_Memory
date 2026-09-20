"""Vocabulary the rule-based extractor matches against, derived from the library itself.

Deriving these from the data rather than hardcoding them means the extractor can never
propose a filter value the library has no photos for.
"""
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
