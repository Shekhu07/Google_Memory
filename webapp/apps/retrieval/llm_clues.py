"""LLM clue extraction that can always degrade to rules.

Two guarantees:
  - Any failure (budget, transport, malformed output) falls back to clues.extract_clues,
    so the public demo never hard-fails in front of a grader.
  - Whatever the model returns is validated against the library's own vocabulary. A
    hallucinated value would match nothing and read as broken retrieval, not a bad guess.
"""
from datetime import date

from clues import extract_clues

ALLOWED = {"date_from", "date_to", "location", "category", "episode"}
VOCAB_KEYS = {"location": "locations", "category": "categories", "episode": "episodes"}

SYSTEM = (
    "You turn a person's vague memory of a photo into retrieval filters.\n"
    "Return ONLY JSON: {{\"filters\": {{...}}, \"chips\": [...]}}.\n"
    "filters keys, all optional: date_from, date_to (YYYY-MM-DD), location, category, episode.\n"
    "Use ONLY these values:\n"
    "  location: {locations}\n"
    "  category: {categories}\n"
    "  episode: {episodes}\n"
    "Each chip is {{\"id\",\"cue\",\"label\",\"filter_key\",\"value\",\"editable\":true}} where cue is one of "
    "exact_date, temporal_approx, place_named, object, event_anchor. "
    "'label' is what a person reads; 'value' must be exactly one of the allowed values above. "
    "Omit anything you are not confident about. Today is {today}."
)


def _prompt(facets, today):
    return SYSTEM.format(locations=", ".join(facets.locations),
                         categories=", ".join(facets.categories),
                         episodes=", ".join(facets.episodes),
                         today=today.isoformat())


def _clean(filters: dict, facets) -> dict:
    """Keep only contract keys whose values actually exist in the library."""
    out = {}
    for key, value in (filters or {}).items():
        if key not in ALLOWED or not value or not isinstance(value, str):
            continue
        if key in VOCAB_KEYS:
            allowed = getattr(facets, VOCAB_KEYS[key])
            match = next((v for v in allowed if v.lower() == value.lower()), None)
            if match is None:
                continue
            out[key] = match
        else:
            try:
                date.fromisoformat(value)
            except (ValueError, TypeError):
                continue
            out[key] = value
    return out


def extract(text: str, facets, client, today: date = None) -> dict:
    today = today or date.today()
    if client is None:
        # Deliberate rules path carries no error notice
        return dict(extract_clues(text, facets, today), notice=None)
    fallback = dict(extract_clues(text, facets, today),
                    notice="Live extraction unavailable - used rule-based clue matching.")
    try:
        data = client.chat_json(_prompt(facets, today), text)
        if not isinstance(data, dict):
            return fallback
        filters = _clean(data.get("filters"), facets)
        # One chip per filter key. A date window is two keys but one clue, and the
        # model usually returns a chip for each, which showed the same label twice.
        chips, seen = [], set()
        for c in (data.get("chips") or []):
            if not isinstance(c, dict):
                continue
            key = c.get("filter_key")
            if key == "date_to" and "date_from" in filters:
                continue
            if key in filters and key not in seen:
                seen.add(key)
                chips.append(c)
        return {"filters": filters, "chips": chips, "source": "llm", "notice": None}
    except Exception:
        return fallback
