from datetime import date

from clues import extract_clues
from facets import load_facets

LIB = [
    {"id": "a", "category": "cafe",     "location": "Goa",       "episode": "goa trip",   "date": "2023-12-14T10:00:00"},
    {"id": "b", "category": "food",     "location": "Goa",       "episode": "goa trip",   "date": "2023-12-18T10:00:00"},
    {"id": "c", "category": "medicine", "location": "Bengaluru", "episode": "fever week", "date": "2024-02-21T10:00:00"},
]
F = load_facets(LIB)
TODAY = date(2026, 9, 21)


def chips_by_key(res):
    return {c["filter_key"]: c for c in res["chips"]}


def test_exact_date_pins_both_ends():
    r = extract_clues("on 2024-07-15", F, TODAY)
    assert r["filters"]["date_from"] == "2024-07-15"
    assert r["filters"]["date_to"] == "2024-07-15"
    assert chips_by_key(r)["date_from"]["cue"] == "exact_date"


def test_month_and_year_becomes_that_month():
    r = extract_clues("in July 2025", F, TODAY)
    assert r["filters"]["date_from"] == "2025-07-01"
    assert r["filters"]["date_to"] == "2025-07-31"


def test_last_year_is_the_previous_calendar_year():
    r = extract_clues("the photo from last year", F, TODAY)
    assert r["filters"]["date_from"] == "2025-01-01"
    assert r["filters"]["date_to"] == "2025-12-31"


def test_location_matches_library_vocabulary_case_insensitively():
    r = extract_clues("our goa trip", F, TODAY)
    assert r["filters"]["location"] == "Goa"
    assert chips_by_key(r)["location"]["cue"] == "place_named"


def test_category_uses_exact_value_not_the_display_label():
    r = extract_clues("that little cafe we found", F, TODAY)
    chip = chips_by_key(r)["category"]
    assert r["filters"]["category"] == "cafe"
    assert chip["value"] == "cafe"
    assert chip["label"] != chip["value"]


def test_episode_name_is_recognised():
    r = extract_clues("during fever week", F, TODAY)
    assert r["filters"]["episode"] == "fever week"


def test_synonym_maps_to_category():
    assert extract_clues("the prescription photo", F, TODAY)["filters"]["category"] == "medicine"


def test_no_recognisable_clue_yields_no_filters():
    r = extract_clues("something I cannot describe", F, TODAY)
    assert r["filters"] == {}
    assert r["chips"] == []


def test_source_is_always_rules():
    assert extract_clues("anything", F, TODAY)["source"] == "rules"


def test_bare_month_anchors_a_window_in_the_past():
    r = extract_clues("the trip in March", F, TODAY)
    assert r["filters"]["date_from"] < "2026-03-15" < r["filters"]["date_to"]


def test_n_years_ago_resolves_to_that_year():
    r = extract_clues("about two years ago", F, TODAY)
    assert r["filters"]["date_from"] == "2024-01-01"


def test_every_chip_maps_to_a_filter_key_that_was_set():
    r = extract_clues("cafe in Goa in July 2025", F, TODAY)
    for chip in r["chips"]:
        assert chip["filter_key"] in r["filters"]
