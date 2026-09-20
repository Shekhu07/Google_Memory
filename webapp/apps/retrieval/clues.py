"""Deterministic text -> filter inference. Always available; never rate-limited.

Two jobs:
  1. The fallback when Groq is unavailable, so the public demo never hard-fails.
  2. The strategy scored offline by engine/demo_eval.py, so the number that reaches
     the deck comes from code that really runs in the product.

Output is the five-key filter contract of engine.demo_index.apply_filters and nothing else.
"""
import calendar
import re
from datetime import date, timedelta

VAGUE_WINDOW_DAYS = 45  # must match engine/demo_eval.VAGUE_WINDOW_DAYS

MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
MONTH_RE = "|".join(sorted(MONTHS, key=len, reverse=True))

WORD_NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}

# Spoken word -> the exact category value stored in the library.
CATEGORY_SYNONYMS = {
    "cafe": "cafe", "café": "cafe", "coffee": "cafe", "restaurant": "cafe",
    "beach": "beach", "sea": "beach", "shore": "beach", "seaside": "beach",
    "food": "food", "meal": "food", "lunch": "food", "dinner": "food", "khana": "food",
    "street": "street", "road": "street", "sadak": "street",
    "receipt": "receipt", "bill": "receipt", "invoice": "receipt",
    "medicine": "medicine", "medicines": "medicine", "prescription": "medicine",
    "tablet": "medicine", "tablets": "medicine", "pills": "medicine", "dawai": "medicine",
    "mountain": "mountain", "mountains": "mountain", "hill": "mountain", "trek": "mountain",
    "wedding": "wedding", "shaadi": "wedding", "marriage": "wedding", "sangeet": "wedding",
    "pet": "pet", "dog": "pet", "puppy": "pet", "cat": "pet",
    "whiteboard": "whiteboard", "board": "whiteboard",
    "document": "document", "paper": "document", "scan": "document", "passport": "document",
    "festival": "festival", "diwali": "festival", "onam": "festival", "pongal": "festival",
}

CATEGORY_LABELS = {
    "cafe": "café", "beach": "beach", "food": "food", "street": "street",
    "receipt": "receipt", "medicine": "medicine / prescription", "mountain": "mountain",
    "wedding": "wedding", "pet": "pet", "whiteboard": "whiteboard",
    "document": "document", "festival": "festival",
}


def _chip(n, cue, label, key, value):
    return {"id": f"c{n}", "cue": cue, "label": label,
            "filter_key": key, "value": value, "editable": True}


def _month_span(year, month):
    last = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last:02d}"


def _year_span(year):
    return f"{year}-01-01", f"{year}-12-31"


def _dates(text, today):
    """(date_from, date_to, cue, label) or None. Most specific pattern wins."""
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m:
        return m.group(0), m.group(0), "exact_date", f"on {m.group(0)}"

    m = re.search(rf"\b({MONTH_RE})\s+(\d{{4}})\b", text)
    if m:
        lo, hi = _month_span(int(m.group(2)), MONTHS[m.group(1)])
        return lo, hi, "temporal_approx", f"{m.group(1).title()} {m.group(2)}"

    if re.search(r"\blast year\b", text):
        lo, hi = _year_span(today.year - 1)
        return lo, hi, "temporal_approx", "last year"

    if re.search(r"\bthis year\b", text):
        lo, hi = _year_span(today.year)
        return lo, hi, "temporal_approx", "this year"

    m = re.search(r"\b(\d+|" + "|".join(WORD_NUMBERS) + r")\s+years?\s+ago\b", text)
    if m:
        token = m.group(1)
        n = int(token) if token.isdigit() else WORD_NUMBERS[token]
        lo, hi = _year_span(today.year - n)
        return lo, hi, "temporal_approx", m.group(0)

    m = re.search(rf"\b({MONTH_RE})\b", text)
    if m:
        month = MONTHS[m.group(1)]
        anchor = date(today.year, month, 15)
        if anchor > today:
            anchor = date(today.year - 1, month, 15)
        lo = (anchor - timedelta(days=VAGUE_WINDOW_DAYS)).isoformat()
        hi = (anchor + timedelta(days=VAGUE_WINDOW_DAYS)).isoformat()
        return lo, hi, "temporal_approx", m.group(1).title()
    return None


def extract_clues(text: str, facets, today: date = None) -> dict:
    """Text -> {"filters", "chips", "source"}. Never raises on unrecognisable input."""
    today = today or date.today()
    low = text.lower()
    filters, chips, n = {}, [], 0

    # Longest match first so "new year goa" beats "goa trip" when both appear.
    for ep in sorted(facets.episodes, key=len, reverse=True):
        if ep.lower() in low:
            n += 1
            filters["episode"] = ep
            chips.append(_chip(n, "event_anchor", ep, "episode", ep))
            break

    for loc in sorted(facets.locations, key=len, reverse=True):
        if re.search(rf"\b{re.escape(loc.lower())}\b", low):
            n += 1
            filters["location"] = loc
            chips.append(_chip(n, "place_named", loc, "location", loc))
            break

    for word in sorted(CATEGORY_SYNONYMS, key=len, reverse=True):
        cat = CATEGORY_SYNONYMS[word]
        if cat in facets.categories and re.search(rf"\b{re.escape(word)}\b", low):
            n += 1
            filters["category"] = cat
            chips.append(_chip(n, "object", CATEGORY_LABELS.get(cat, cat), "category", cat))
            break

    found = _dates(low, today)
    if found:
        lo, hi, cue, label = found
        n += 1
        filters["date_from"], filters["date_to"] = lo, hi
        chip = _chip(n, cue, label, "date_from", lo)
        chip["value_to"] = hi  # removing this chip drops date_from AND date_to
        chips.append(chip)

    return {"filters": filters, "chips": chips, "source": "rules"}
