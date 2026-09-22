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

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

HINGLISH_NUMBERS = {
    "ek": 1, "do": 2, "teen": 3, "chaar": 4, "char": 4,
    "paanch": 5, "panch": 5, "chhe": 6, "che": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10
}

# Season -> contiguous month window. Mirrors engine/demo_tasks.SEASONS, which labels a
# photo by ITS OWN year, so "winter 2024" means Jan, Feb or Dec of 2024 - a disjoint
# set. apply_filters supports one contiguous window, so winter widens to the full year.
SEASON_MONTHS = {
    "spring": (3, 4),
    "summer": (5, 6),
    "monsoon": (7, 9),
    "autumn": (10, 11),
    "winter": (1, 12),   # deliberately the whole year; see above
}
SEASON_RE = "|".join(SEASON_MONTHS)
YEAR = r"(\d{4})(?:ish)?"

# Published festival dates 2016-2026 (verified from published panchang / official calendars)
FESTIVAL_DATES = {
    "diwali": {
        2016: date(2016, 10, 30), 2017: date(2017, 10, 19), 2018: date(2018, 11, 7),
        2019: date(2019, 10, 27), 2020: date(2020, 11, 14), 2021: date(2021, 11, 4),
        2022: date(2022, 10, 24), 2023: date(2023, 11, 12), 2024: date(2024, 10, 31),
        2025: date(2025, 10, 20), 2026: date(2026, 11, 8),
    },
    "holi": {
        2016: date(2016, 3, 24), 2017: date(2017, 3, 13), 2018: date(2018, 3, 2),
        2019: date(2019, 3, 21), 2020: date(2020, 3, 10), 2021: date(2021, 3, 29),
        2022: date(2022, 3, 18), 2023: date(2023, 3, 8), 2024: date(2024, 3, 25),
        2025: date(2025, 3, 14), 2026: date(2026, 3, 4),
    },
    "onam": {
        2016: date(2016, 9, 14), 2017: date(2017, 9, 4), 2018: date(2018, 8, 25),
        2019: date(2019, 9, 11), 2020: date(2020, 8, 31), 2021: date(2021, 8, 21),
        2022: date(2022, 9, 8), 2023: date(2023, 8, 29), 2024: date(2024, 9, 15),
        2025: date(2025, 9, 5), 2026: date(2026, 8, 26),
    },
    "ganesh chaturthi": {
        2016: date(2016, 9, 5), 2017: date(2017, 8, 25), 2018: date(2018, 9, 13),
        2019: date(2019, 9, 2), 2020: date(2020, 8, 22), 2021: date(2021, 9, 10),
        2022: date(2022, 8, 31), 2023: date(2023, 9, 19), 2024: date(2024, 9, 7),
        2025: date(2025, 8, 27), 2026: date(2026, 9, 14),
    },
    "eid": {
        2016: date(2016, 7, 7), 2017: date(2017, 6, 26), 2018: date(2018, 6, 16),
        2019: date(2019, 6, 5), 2020: date(2020, 5, 25), 2021: date(2021, 5, 14),
        2022: date(2022, 5, 3), 2023: date(2023, 4, 22), 2024: date(2024, 4, 11),
        2025: date(2025, 3, 31), 2026: date(2026, 3, 21),
    },
    "dussehra": {
        2016: date(2016, 10, 11), 2017: date(2017, 9, 30), 2018: date(2018, 10, 19),
        2019: date(2019, 10, 8), 2020: date(2020, 10, 25), 2021: date(2021, 10, 15),
        2022: date(2022, 10, 5), 2023: date(2023, 10, 24), 2024: date(2024, 10, 12),
        2025: date(2025, 10, 2), 2026: date(2026, 10, 20),
    },
}

FESTIVAL_NAME_MAP = {
    "diwali": "diwali",
    "deepavali": "diwali",
    "holi": "holi",
    "onam": "onam",
    "ganesh chaturthi": "ganesh chaturthi",
    "ganpati": "ganesh chaturthi",
    "vinayaka chaturthi": "ganesh chaturthi",
    "eid-ul-fitr": "eid",
    "eid ul fitr": "eid",
    "eid": "eid",
    "dussehra": "dussehra",
    "dasara": "dussehra",
    "navratri": "dussehra",
    "vijayadashami": "dussehra",
}

FIXED_HOLIDAYS = {
    "christmas": (12, 25),
    "xmas": (12, 25),
    "new year's": (1, 1),
    "new years": (1, 1),
    "new year": (1, 1),
    "halloween": (10, 31),
    "independence day": (8, 15),
    "15 august": (8, 15),
    "15th august": (8, 15),
    "republic day": (1, 26),
    "26 january": (1, 26),
    "26th january": (1, 26),
}

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


def _thanksgiving_date(year: int) -> date:
    c = calendar.Calendar()
    thursdays = [d for d in c.itermonthdates(year, 11) if d.month == 11 and d.weekday() == 3]
    return thursdays[3]


def _month_span(year, month):
    last = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last:02d}"


def _year_span(year):
    return f"{year}-01-01", f"{year}-12-31"


def _festival_dates(text: str, today: date, matched_ep: str = None):
    low = text.lower()
    all_fest_names = sorted(list(FESTIVAL_NAME_MAP.keys()) + list(FIXED_HOLIDAYS.keys()) + ["thanksgiving"], key=len, reverse=True)
    fest_pattern = r"\b(" + "|".join(re.escape(n) for n in all_fest_names) + r")\b"
    m_fest = re.search(fest_pattern, low)
    if not m_fest:
        return None
    matched_name = m_fest.group(1)

    # Check for explicit year or relative year keywords
    m_yr = re.search(r"\b(20\d{2})\b", low)
    target_year = None
    if m_yr:
        target_year = int(m_yr.group(1))
    elif re.search(r"\b(last year|pichle saal|pichhle saal)\b", low):
        target_year = today.year - 1
    elif re.search(r"\b(this year|is saal|iss saal)\b", low):
        target_year = today.year

    # If the festival word is part of the episode name already matched and no explicit year was asked,
    # the user is referring to the episode directly, not asking to date-gate to the latest festival year.
    if matched_ep and matched_name in matched_ep.lower() and target_year is None:
        return None

    d_center = None
    if matched_name in FIXED_HOLIDAYS:
        mo, da = FIXED_HOLIDAYS[matched_name]
        if target_year is not None:
            d_center = date(target_year, mo, da)
        else:
            cand = date(today.year, mo, da)
            d_center = cand if cand < today else date(today.year - 1, mo, da)
    elif matched_name == "thanksgiving":
        if target_year is not None:
            d_center = _thanksgiving_date(target_year)
        else:
            cand = _thanksgiving_date(today.year)
            d_center = cand if cand < today else _thanksgiving_date(today.year - 1)
    else:
        canon = FESTIVAL_NAME_MAP[matched_name]
        table = FESTIVAL_DATES[canon]
        if target_year is not None:
            d_center = table.get(target_year)
        else:
            past = [d for y, d in sorted(table.items()) if d < today]
            d_center = past[-1] if past else table[min(table.keys())]

    if d_center:
        lo = (d_center - timedelta(days=3)).isoformat()
        hi = (d_center + timedelta(days=3)).isoformat()
        return lo, hi, "temporal_approx", f"{matched_name.title()} {d_center.year}"
    return None


def _trip_relative_dates(text: str, facets):
    """Detect time relative to user's trips/episodes (Idea A3 / Task T3)."""
    low = text.lower()
    windows = getattr(facets, "episode_windows", {})
    if not windows:
        return None

    matched_ep = None
    for ep in sorted(facets.episodes, key=len, reverse=True):
        if ep.lower() in low:
            matched_ep = ep
            break

    # Also resolve short names / colloquial mentions to specific library episodes
    if not matched_ep:
        if re.search(r"\b(wedding|shaadi|marriage)\b", low) and "cousin wedding" in windows:
            matched_ep = "cousin wedding"
        elif re.search(r"\b(goa)\b", low) and "goa trip" in windows:
            matched_ep = "goa trip"
        elif re.search(r"\b(sangeet)\b", low) and "friend's sangeet" in windows:
            matched_ep = "friend's sangeet"

    if not matched_ep or matched_ep not in windows:
        return None

    # Guard: if the only occurrence of 'pehle' is inside 'saal pehle' or 'mahine pehle',
    # it is a year/month delta (e.g. '3 saal pehle Goa'), NOT a trip-relative preposition.
    low_without_saal_pehle = re.sub(r"\b(\d+|" + "|".join(HINGLISH_NUMBERS) + r")\s+(?:saal|mahine)\s+pehle\b", "", low)

    ep_lo_str, ep_hi_str = windows[matched_ep]
    ep_start = date.fromisoformat(ep_lo_str)
    ep_end = date.fromisoformat(ep_hi_str)

    after_patterns = [
        r"(?:a few|few|\d+|one|two|three|four|five|six)\s+weeks?\s+after",
        r"(?:a few|few|\d+|one|two|three|four|five|six)\s+days?\s+after",
        r"(?:a few|few|\d+|one|two|three|four|five|six)\s+months?\s+after",
        r"\b(?:just|right|shortly)\s+after\b",
        r"\bafter\b", r"\bbaad\b", r"\bke\s+baad\b",
    ]
    before_patterns = [
        r"(?:a few|few|\d+|one|two|three|four|five|six)\s+weeks?\s+before",
        r"(?:a few|few|\d+|one|two|three|four|five|six)\s+days?\s+before",
        r"(?:a few|few|\d+|one|two|three|four|five|six)\s+months?\s+before",
        r"\b(?:just|right|shortly)\s+before\b",
        r"\bbefore\b", r"\bpehle\b", r"\bse\s+pehle\b", r"\bke\s+pehle\b",
    ]

    is_after = any(re.search(p, low_without_saal_pehle) for p in after_patterns)
    is_before = any(re.search(p, low_without_saal_pehle) for p in before_patterns)

    if not is_after and not is_before:
        return None

    WORD_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                "a few": 6, "few": 6}

    if is_after:
        m_w = re.search(r"(\d+|one|two|three|four|five|six|a few|few)\s+weeks?\s+after", low)
        m_d = re.search(r"(\d+|one|two|three|four|five|six|a few|few)\s+days?\s+after", low)
        m_m = re.search(r"(\d+|one|two|three|four|five|six|a few|few)\s+months?\s+after", low)
        if re.search(r"\b(just|right|shortly)\s+after\b", low):
            lo = ep_end.isoformat()
            hi = (ep_end + timedelta(days=14)).isoformat()
            label = f"just after {matched_ep}"
        elif m_w:
            val = m_w.group(1)
            w = int(val) if val.isdigit() else WORD_MAP.get(val, 6)
            lo = ep_end.isoformat()
            hi = (ep_end + timedelta(days=w * 7)).isoformat()
            label = f"{w} weeks after {matched_ep}"
        elif m_d:
            val = m_d.group(1)
            d = int(val) if val.isdigit() else WORD_MAP.get(val, 14)
            lo = ep_end.isoformat()
            hi = (ep_end + timedelta(days=d)).isoformat()
            label = f"{d} days after {matched_ep}"
        elif m_m:
            val = m_m.group(1)
            m = int(val) if val.isdigit() else WORD_MAP.get(val, 1)
            lo = ep_end.isoformat()
            hi = (ep_end + timedelta(days=m * 30)).isoformat()
            label = f"{m} months after {matched_ep}"
        else:
            lo = ep_end.isoformat()
            hi = (ep_end + timedelta(days=42)).isoformat()
            label = f"after {matched_ep}"
        return lo, hi, "temporal_approx", label, matched_ep

    if is_before:
        m_w = re.search(r"(\d+|one|two|three|four|five|six|a few|few)\s+weeks?\s+before", low)
        m_d = re.search(r"(\d+|one|two|three|four|five|six|a few|few)\s+days?\s+before", low)
        m_m = re.search(r"(\d+|one|two|three|four|five|six|a few|few)\s+months?\s+before", low)
        if re.search(r"\b(just|right|shortly)\s+before\b", low):
            lo = (ep_start - timedelta(days=14)).isoformat()
            hi = ep_end.isoformat()
            label = f"just before {matched_ep}"
        elif m_w:
            val = m_w.group(1)
            w = int(val) if val.isdigit() else WORD_MAP.get(val, 6)
            lo = (ep_start - timedelta(days=w * 7)).isoformat()
            hi = ep_end.isoformat()
            label = f"{w} weeks before {matched_ep}"
        elif m_d:
            val = m_d.group(1)
            d = int(val) if val.isdigit() else WORD_MAP.get(val, 14)
            lo = (ep_start - timedelta(days=d)).isoformat()
            hi = ep_end.isoformat()
            label = f"{d} days before {matched_ep}"
        elif m_m:
            val = m_m.group(1)
            m = int(val) if val.isdigit() else WORD_MAP.get(val, 1)
            lo = (ep_start - timedelta(days=m * 30)).isoformat()
            hi = ep_end.isoformat()
            label = f"{m} months before {matched_ep}"
        else:
            lo = (ep_start - timedelta(days=42)).isoformat()
            hi = ep_end.isoformat()
            label = f"before {matched_ep}"
        return lo, hi, "temporal_approx", label, matched_ep

    return None


def _dates(text, today, matched_ep: str = None):
    """(date_from, date_to, cue, label) or None. Most specific pattern wins."""
    low = text.lower()

    # 1. Exact ISO date: YYYY-MM-DD
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", low)
    if m:
        return m.group(0), m.group(0), "exact_date", f"on {m.group(0)}"

    # 2. DD/MM/YYYY, DD-MM-YYYY, DD.MM.YY(YY)
    m = re.search(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b", low)
    if m:
        try:
            p1, p2, p3 = int(m.group(1)), int(m.group(2)), int(m.group(3))
            yr = 2000 + p3 if p3 < 100 else p3
            day, month = p1, p2
            if 1 <= month <= 12 and 1 <= day <= 31:
                dt = date(yr, month, day)
                if day <= 12 and month <= 12:
                    lo = (dt - timedelta(days=3)).isoformat()
                    hi = (dt + timedelta(days=3)).isoformat()
                    return lo, hi, "exact_date", f"around {day:02d}/{month:02d}/{yr}"
                else:
                    return dt.isoformat(), dt.isoformat(), "exact_date", f"on {day:02d}/{month:02d}/{yr}"
        except ValueError:
            pass

    # 3. DD Month YYYY (e.g. 15 July 2024, 15th September 2024)
    m = re.search(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_RE})\s+{YEAR}\b", low)
    if m:
        try:
            day = int(m.group(1))
            month = MONTHS[m.group(2)]
            yr = int(m.group(3))
            dt = date(yr, month, day)
            return dt.isoformat(), dt.isoformat(), "exact_date", f"on {dt.isoformat()}"
        except ValueError:
            pass

    # 4. Month YYYY (e.g. July 2025, July 2025ish)
    m = re.search(rf"\b({MONTH_RE})\s+{YEAR}\b", low)
    if m:
        lo, hi = _month_span(int(m.group(2)), MONTHS[m.group(1)])
        return lo, hi, "temporal_approx", f"{m.group(1).title()} {m.group(2)}"

    # 5. Festivals & holidays (Diwali 2024, Halloween 2024, Onam 2024, Holi last year)
    fest = _festival_dates(low, today, matched_ep=matched_ep)
    if fest:
        return fest

    # 6. Relative seasons
    if re.search(r"\blast winter\b", low):
        lo = f"{today.year - 2}-12-01"
        hi = f"{today.year}-02-28"
        return lo, hi, "temporal_approx", "last winter"
    if re.search(r"\bthis monsoon\b", low):
        return f"{today.year}-07-01", f"{today.year}-09-30", "temporal_approx", "this monsoon"
    if re.search(r"\blast monsoon\b", low):
        return f"{today.year - 1}-07-01", f"{today.year - 1}-09-30", "temporal_approx", "last monsoon"
    if re.search(r"\blast summer\b", low):
        return f"{today.year - 1}-05-01", f"{today.year - 1}-06-30", "temporal_approx", "last summer"
    if re.search(r"\bthis summer\b", low):
        return f"{today.year}-05-01", f"{today.year}-06-30", "temporal_approx", "this summer"

    # 7. Season YYYY (synthetic forms: around summer 2024, winter 2024)
    m = re.search(rf"\b({SEASON_RE})\s+{YEAR}\b", low)
    if m:
        season, year = m.group(1), int(m.group(2))
        first, last = SEASON_MONTHS[season]
        lo = f"{year:04d}-{first:02d}-01"
        hi = f"{year:04d}-{last:02d}-{calendar.monthrange(year, last)[1]:02d}"
        return lo, hi, "temporal_approx", f"{season} {year}"

    # 8. Hinglish relative years & months
    if re.search(r"\b(pichle|pichhle)\s+saal\b", low):
        lo, hi = _year_span(today.year - 1)
        return lo, hi, "temporal_approx", "pichle saal"
    if re.search(r"\b(is|iss)\s+saal\b", low):
        lo, hi = _year_span(today.year)
        return lo, hi, "temporal_approx", "is saal"
    if re.search(r"\b(pichle|pichhle)\s+mahine\b", low):
        yr = today.year - 1 if today.month == 1 else today.year
        mo = 12 if today.month == 1 else today.month - 1
        lo, hi = _month_span(yr, mo)
        return lo, hi, "temporal_approx", "pichle mahine"

    m_h = re.search(r"\b(\d+|" + "|".join(HINGLISH_NUMBERS) + r")\s+saal\s+pehle\b", low)
    if m_h:
        tok = m_h.group(1)
        n = int(tok) if tok.isdigit() else HINGLISH_NUMBERS[tok]
        lo, hi = _year_span(today.year - n)
        return lo, hi, "temporal_approx", m_h.group(0)

    # 9. Bare year forms
    m = re.search(rf"\b(?:in|during|around|sometime in)\s+{YEAR}\b", low)
    if m:
        lo, hi = _year_span(int(m.group(1)))
        return lo, hi, "temporal_approx", m.group(1)

    m = re.search(rf"\b((?:19|20)\d{{2}})ish\b", low)
    if m:
        lo, hi = _year_span(int(m.group(1)))
        return lo, hi, "temporal_approx", m.group(1)

    # 10. English relative years
    if re.search(r"\blast year\b", low):
        lo, hi = _year_span(today.year - 1)
        return lo, hi, "temporal_approx", "last year"

    if re.search(r"\bthis year\b", low):
        lo, hi = _year_span(today.year)
        return lo, hi, "temporal_approx", "this year"

    # 11. N years ago / about N years ago / about a year ago
    m = re.search(r"\b(?:about\s+)?(a|an|\d+|" + "|".join(WORD_NUMBERS) + r")\s+years?\s+ago\b", low)
    if m:
        token = m.group(1)
        if token in ("a", "an"):
            n = 1
        else:
            n = int(token) if token.isdigit() else WORD_NUMBERS[token]
        lo, hi = _year_span(today.year - n)
        return lo, hi, "temporal_approx", m.group(0)

    # 12. Bare month (vague anchor in the past)
    m = re.search(rf"\b({MONTH_RE})\b", low)
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

    # Step 1: Check for trip-relative time (Idea A3 / Task T3).
    # If time is relative to an episode ("after Goa trip", "just before the wedding"),
    # we shift the window and MUST drop both episode and location locks.
    trip_rel = _trip_relative_dates(low, facets)
    relative_ep = None
    if trip_rel:
        lo, hi, cue, label, relative_ep = trip_rel
        n += 1
        filters["date_from"], filters["date_to"] = lo, hi
        chip = _chip(n, cue, label, "date_from", lo)
        chip["value_to"] = hi
        chips.append(chip)

    # Step 2: Episode matching (skip if trip-relative already consumed the episode)
    if not relative_ep:
        for ep in sorted(facets.episodes, key=len, reverse=True):
            if ep.lower() in low:
                n += 1
                filters["episode"] = ep
                chips.append(_chip(n, "event_anchor", ep, "episode", ep))
                break

    # Step 3: Location matching (skip if trip-relative dropped location lock)
    if not relative_ep:
        for loc in sorted(facets.locations, key=len, reverse=True):
            if re.search(rf"\b{re.escape(loc.lower())}\b", low):
                n += 1
                filters["location"] = loc
                chips.append(_chip(n, "place_named", loc, "location", loc))
                break

    # Step 4: Category matching
    fest_anchor = _festival_dates(low, today, matched_ep=filters.get("episode"))
    for word in sorted(CATEGORY_SYNONYMS, key=len, reverse=True):
        cat = CATEGORY_SYNONYMS[word]
        if cat in facets.categories and re.search(rf"\b{re.escape(word)}\b", low):
            if fest_anchor and cat == "festival":
                continue
            n += 1
            filters["category"] = cat
            chips.append(_chip(n, "object", CATEGORY_LABELS.get(cat, cat), "category", cat))
            break

    # Step 5: Date matching (if not already set by trip-relative)
    if "date_from" not in filters:
        found = _dates(low, today, matched_ep=filters.get("episode"))
        if found:
            lo, hi, cue, label = found
            n += 1
            filters["date_from"], filters["date_to"] = lo, hi
            chip = _chip(n, cue, label, "date_from", lo)
            chip["value_to"] = hi
            chips.append(chip)

    return {"filters": filters, "chips": chips, "source": "rules"}
