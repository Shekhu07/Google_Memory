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


# --- vague-time forms the eval actually uses (21 Sep) -------------------------
# temporal_approx is the most-retained real cue (40 of 144 episodes), and the
# generator phrases it three ways: "July 2025ish", "sometime in 2024",
# "around summer 2024". The first version of the extractor parsed none of them.

def test_ish_suffix_does_not_break_month_and_year():
    r = extract_clues("July 2025ish", F, TODAY)
    assert r["filters"]["date_from"] == "2025-07-01"
    assert r["filters"]["date_to"] == "2025-07-31"


def test_bare_year_becomes_the_whole_year():
    r = extract_clues("sometime in 2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-01-01"
    assert r["filters"]["date_to"] == "2024-12-31"


def test_bare_year_with_ish():
    assert extract_clues("2024ish", F, TODAY)["filters"]["date_from"] == "2024-01-01"


def test_monsoon_maps_to_july_september():
    r = extract_clues("around monsoon 2025", F, TODAY)
    assert r["filters"]["date_from"] == "2025-07-01"
    assert r["filters"]["date_to"] == "2025-09-30"


def test_summer_maps_to_may_june():
    r = extract_clues("around summer 2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-05-01"
    assert r["filters"]["date_to"] == "2024-06-30"


def test_spring_maps_to_march_april():
    r = extract_clues("around spring 2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-03-01"
    assert r["filters"]["date_to"] == "2024-04-30"


def test_autumn_maps_to_october_november():
    r = extract_clues("around autumn 2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-10-01"
    assert r["filters"]["date_to"] == "2024-11-30"


def test_winter_spans_the_whole_year_because_it_is_disjoint():
    """Winter is Dec, Jan and Feb OF THE SAME YEAR in this corpus, so the only
    contiguous window that contains it is the year itself."""
    r = extract_clues("around winter 2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-01-01"
    assert r["filters"]["date_to"] == "2024-12-31"


def test_an_exact_date_still_wins_over_a_vague_one():
    r = extract_clues("on 2025-07-10 July 2025ish", F, TODAY)
    assert r["filters"]["date_from"] == r["filters"]["date_to"] == "2025-07-10"
