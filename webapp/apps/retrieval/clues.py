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
    "new year's eve": (12, 31),
    "new years eve": (12, 31),
    "nye": (12, 31),
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
    "street": "street", "sadak": "street",
    "receipt": "receipt", "bill": "receipt", "invoice": "receipt",
    "medicine": "medicine", "medicines": "medicine", "prescription": "medicine",
    "tablet": "medicine", "tablets": "medicine", "pills": "medicine", "dawai": "medicine",
    "mountain": "mountain", "mountains": "mountain", "hill": "mountain", "trek": "mountain",
    "wedding": "wedding", "shaadi": "wedding", "marriage": "wedding", "sangeet": "wedding",
    "pet": "pet", "dog": "pet", "puppy": "pet", "cat": "pet",
    "whiteboard": "whiteboard", "board": "whiteboard",
    "document": "document", "paper": "document", "scan": "document", "passport": "document",
    "festival": "festival", "diwali": "festival", "onam": "festival", "pongal": "festival",
    "parking": "parking", "parking lot": "parking", "car park": "parking", "parked": "parking",
    "screenshot": "screenshot", "screenshots": "screenshot",
    "auto rickshaw": "auto rickshaw", "rickshaw": "auto rickshaw",
    "chai stall": "chai stall", "chai": "chai stall",
}

CATEGORY_LABELS = {
    "cafe": "café", "beach": "beach", "food": "food", "street": "street",
    "receipt": "receipt", "medicine": "medicine / prescription", "mountain": "mountain",
    "wedding": "wedding", "pet": "pet", "whiteboard": "whiteboard",
    "document": "document", "festival": "festival",
}

EPISODE_ALIASES = {
    "office offsite": ["offsite", "off-site"],
    "fever week": ["fever", "when i was sick", "when i was ill", "bimaar tha", "bimaar thi"],
    "new year goa": [
        "new year's eve party goa", "new year party goa", "nye party goa",
        "new year's eve in goa", "new year in goa", "nye goa", "new year's eve goa",
    ],
    "passport renewal": ["passport renewal", "renewing my passport"],
    "dental work": ["dentist", "dental"],
    "house move": ["moving house", "house shifting", "shifting house"],
    "flat hunting": ["flat hunt", "house hunting"],
    "puppy vet visits": ["vet visit", "the vet"],
    "product workshop": ["workshop"],
    "team strategy day": ["strategy day"],
    "year-end party": ["year end party", "office party"],
    "cousin wedding": ["wedding", "shaadi"],
    "friend's sangeet": ["sangeet"],
    "onam lunch": ["onam sadhya", "sadhya", "sadya"],
    "summer in kerala": ["summer in kerala"],
    "goa trip": ["goa trip"],
}


def _mention_re(ep: str) -> str:
    names = [ep] + EPISODE_ALIASES.get(ep, [])
    return r"(?:" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")"


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

    WORD_MAP = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
        "a few": 6, "few": 6,
        "ek": 1, "do": 2, "teen": 3, "chaar": 4, "char": 4,
        "paanch": 5, "panch": 5, "chhe": 6, "che": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
    }

    QTY = r"(?:(?P<n>\d+|a few|few|one|two|three|four|five|six)\s+(?P<unit>days?|weeks?|months?)\s+|(?P<adv>just|right|shortly)\s+)?"
    DET = r"(?:the\s+|our\s+|my\s+|that\s+)?"
    QTY_HI = r"(?:(?P<n_hi>\d+|ek|do|teen|chaar|char|paanch|panch|chhe|che|saat|aath|nau|das)\s+(?P<unit_hi>din|hafte|mahine)\s+)?"

    # Check known episodes sorted by name length descending
    for ep in sorted(windows.keys(), key=len, reverse=True):
        m = _mention_re(ep)

        after_en = re.search(QTY + r"after\s+" + DET + r"\b" + m + r"\b", low)
        before_en = re.search(QTY + r"before\s+" + DET + r"\b" + m + r"\b", low)
        after_hi = re.search(r"\b" + m + r"(?:\s+trip)?\s+(?:ke\s+)?" + QTY_HI + r"baad\b", low)
        before_hi = re.search(r"\b" + m + r"(?:\s+trip)?\s+(?:se\s+|ke\s+)?" + QTY_HI + r"pehle\b", low)

        match = after_en or before_en or after_hi or before_hi
        if not match:
            continue

        ep_lo_str, ep_hi_str = windows[ep]
        ep_start = date.fromisoformat(ep_lo_str)
        ep_end = date.fromisoformat(ep_hi_str)

        is_after = bool(after_en or after_hi)
        direction = "after" if is_after else "before"

        gd = match.groupdict()
        n_val = gd.get("n") or gd.get("n_hi")
        unit = gd.get("unit") or gd.get("unit_hi")
        adv = gd.get("adv")

        if adv:
            delta_days = 14
            label = f"{adv} {direction} {ep}"
        elif unit:
            w = int(n_val) if n_val.isdigit() else WORD_MAP.get(n_val, 6)
            if unit in ("day", "days", "din"):
                delta_days = w
                label = f"{w} days {direction} {ep}"
            elif unit in ("week", "weeks", "hafte"):
                delta_days = w * 7
                label = f"{w} weeks {direction} {ep}"
            elif unit in ("month", "months", "mahine"):
                delta_days = w * 30
                label = f"{w} months {direction} {ep}"
            else:
                delta_days = 42
                label = f"{direction} {ep}"
        else:
            delta_days = 42
            label = f"{direction} {ep}"

        if is_after:
            lo = ep_end.isoformat()
            hi = (ep_end + timedelta(days=delta_days)).isoformat()
        else:
            lo = (ep_start - timedelta(days=delta_days)).isoformat()
            hi = ep_start.isoformat()

        return lo, hi, "temporal_approx", label, ep

    return None


def _dates(text, today, matched_ep: str = None):
    """(date_from, date_to, cue, label, [alternatives]) or None. Most specific pattern wins."""
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
                alts = []
                if day <= 12 and month <= 12 and day != month:
                    alt_dt = date(yr, day, month)
                    alts.append({
                        "label": f"or {alt_dt.strftime('%d %b %Y')}",
                        "value": alt_dt.isoformat(),
                        "value_to": alt_dt.isoformat(),
                    })
                return dt.isoformat(), dt.isoformat(), "exact_date", f"on {day:02d}/{month:02d}/{yr}", alts
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
        end_year = today.year if today.month >= 3 else today.year - 1
        feb_last = calendar.monthrange(end_year, 2)[1]
        lo = f"{end_year - 1}-12-01"
        hi = f"{end_year}-02-{feb_last:02d}"
        alt_lo = f"{end_year - 2}-12-01"
        alt_hi = f"{end_year - 1}-02-{calendar.monthrange(end_year - 1, 2)[1]:02d}"
        alts = [{
            "label": f"or Dec {end_year - 2} – Feb {end_year - 1}",
            "value": alt_lo,
            "value_to": alt_hi,
        }]
        return lo, hi, "temporal_approx", "last winter", alts

    summer_year = today.year if today.month >= 7 else today.year - 1
    monsoon_year = today.year if today.month >= 10 else today.year - 1

    if re.search(r"\bthis monsoon\b", low):
        lo, hi = f"{today.year}-07-01", f"{today.year}-09-30"
        alts = [{"label": f"or Jul – Sep {today.year - 1}", "value": f"{today.year - 1}-07-01", "value_to": f"{today.year - 1}-09-30"}]
        return lo, hi, "temporal_approx", "this monsoon", alts

    if re.search(r"\blast monsoon\b", low):
        lo, hi = f"{monsoon_year}-07-01", f"{monsoon_year}-09-30"
        alts = [{"label": f"or Jul – Sep {monsoon_year - 1}", "value": f"{monsoon_year - 1}-07-01", "value_to": f"{monsoon_year - 1}-09-30"}]
        return lo, hi, "temporal_approx", "last monsoon", alts

    if re.search(r"\blast summer\b", low):
        lo, hi = f"{summer_year}-05-01", f"{summer_year}-06-30"
        alts = [{"label": f"or May – Jun {summer_year - 1}", "value": f"{summer_year - 1}-05-01", "value_to": f"{summer_year - 1}-06-30"}]
        return lo, hi, "temporal_approx", "last summer", alts

    if re.search(r"\bthis summer\b", low):
        lo, hi = f"{today.year}-05-01", f"{today.year}-06-30"
        alts = [{"label": f"or May – Jun {today.year - 1}", "value": f"{today.year - 1}-05-01", "value_to": f"{today.year - 1}-06-30"}]
        return lo, hi, "temporal_approx", "this summer", alts

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
        alts = [{"label": f"or {today.year - 2}", "value": f"{today.year - 2}-01-01", "value_to": f"{today.year - 2}-12-31"}]
        return lo, hi, "temporal_approx", "pichle saal", alts

    if re.search(r"\b(is|iss)\s+saal\b", low):
        lo, hi = _year_span(today.year)
        alts = [{"label": f"or {today.year - 1}", "value": f"{today.year - 1}-01-01", "value_to": f"{today.year - 1}-12-31"}]
        return lo, hi, "temporal_approx", "is saal", alts

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
        alts = [{"label": f"or {today.year - 2}", "value": f"{today.year - 2}-01-01", "value_to": f"{today.year - 2}-12-31"}]
        return lo, hi, "temporal_approx", "last year", alts

    if re.search(r"\bthis year\b", low):
        lo, hi = _year_span(today.year)
        alts = [{"label": f"or {today.year - 1}", "value": f"{today.year - 1}-01-01", "value_to": f"{today.year - 1}-12-31"}]
        return lo, hi, "temporal_approx", "this year", alts

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
    BARE_MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
    BARE_MONTHS["sept"] = 9
    m = re.search(r"\b(" + "|".join(BARE_MONTHS) + r")\b", low)
    if m and m.group(1) == "may" and not re.search(r"\b(in|during|around|early|mid|late|last|this|since)\s+may\b|\bmay\s+(?:mein|ke|me)\b", low):
        m = None
    if m:
        month = BARE_MONTHS[m.group(1)]
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
        # Full episode name first
        for ep in sorted(facets.episodes, key=len, reverse=True):
            if re.search(rf"\b{re.escape(ep.lower())}\b", low):
                n += 1
                filters["episode"] = ep
                chips.append(_chip(n, "event_anchor", ep, "episode", ep))
                break

        # Episode aliases if no full name matched
        if "episode" not in filters:
            alias_list = []
            for target_ep, aliases in EPISODE_ALIASES.items():
                if target_ep in facets.episodes:
                    for alias in aliases:
                        alias_list.append((alias, target_ep))
            alias_list.sort(key=lambda x: len(x[0]), reverse=True)

            for alias, target_ep in alias_list:
                if re.search(rf"\b{re.escape(alias)}\b", low):
                    n += 1
                    filters["episode"] = target_ep
                    chips.append(_chip(n, "event_anchor", target_ep, "episode", target_ep))
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
    synonyms = {c.lower(): c for c in facets.categories}
    synonyms.update(CATEGORY_SYNONYMS)
    for word in sorted(synonyms, key=len, reverse=True):
        cat = synonyms[word]
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
            lo, hi, cue, label = found[:4]
            alts = found[4] if len(found) > 4 else None
            n += 1
            filters["date_from"], filters["date_to"] = lo, hi
            chip = _chip(n, cue, label, "date_from", lo)
            chip["value_to"] = hi
            if alts:
                chip["alternatives"] = alts
            chips.append(chip)

    return {"filters": filters, "chips": chips, "source": "rules"}
