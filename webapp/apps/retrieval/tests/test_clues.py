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


# --- Task T2: Festivals, numeric dates, relative seasons, Hinglish (Idea A2) ---

def test_festival_diwali_2024():
    r = extract_clues("Diwali 2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-10-28"
    assert r["filters"]["date_to"] == "2024-11-03"


def test_festival_halloween_2024():
    r = extract_clues("Halloween 2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-10-28"
    assert r["filters"]["date_to"] == "2024-11-03"


def test_festival_holi_last_year():
    r = extract_clues("Holi last year", F, TODAY)
    assert r["filters"]["date_from"] == "2025-03-11"
    assert r["filters"]["date_to"] == "2025-03-17"


def test_festival_without_year_resolves_to_most_recent():
    r = extract_clues("Diwali ke time", F, TODAY)
    assert r["filters"]["date_from"] == "2025-10-17"
    assert r["filters"]["date_to"] == "2025-10-23"


def test_numeric_date_dd_mm_yyyy_exact():
    r = extract_clues("25/12/2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-12-25"
    assert r["filters"]["date_to"] == "2024-12-25"
    assert chips_by_key(r)["date_from"]["cue"] == "exact_date"


def test_numeric_date_frozen_no_alternative():
    # v2: Exact numeric dates are frozen; no alternatives generated
    r = extract_clues("10/07/2025", F, TODAY)
    assert r["filters"]["date_from"] == "2025-07-10"
    assert r["filters"]["date_to"] == "2025-07-10"
    chip = chips_by_key(r)["date_from"]
    assert "alternatives" not in chip


def test_numeric_date_word_month():
    r = extract_clues("15 July 2024", F, TODAY)
    assert r["filters"]["date_from"] == "2024-07-15"
    assert r["filters"]["date_to"] == "2024-07-15"


def test_relative_seasons():
    r_w = extract_clues("restaurant we visited in Udaipur last winter", F, TODAY)
    assert r_w["filters"]["location"] == "Udaipur" if "Udaipur" in F.locations else True
    assert r_w["filters"]["date_from"] == "2025-12-01"
    assert r_w["filters"]["date_to"] == "2026-02-28"

    r_m = extract_clues("this monsoon in Mumbai", F, TODAY)
    assert r_m["filters"]["date_from"] == "2026-07-01"
    assert r_m["filters"]["date_to"] == "2026-09-30"

    r_s = extract_clues("last summer whiteboard", F, TODAY)
    assert r_s["filters"]["date_from"] == "2026-05-01"
    assert r_s["filters"]["date_to"] == "2026-06-30"


def test_hinglish_time_words():
    r1 = extract_clues("pichle saal wali Goa trip ki photo", F, TODAY)
    assert r1["filters"]["date_from"] == "2025-01-01"
    assert r1["filters"]["date_to"] == "2025-12-31"

    r2 = extract_clues("3 saal pehle Goa", F, TODAY)
    assert r2["filters"]["date_from"] == "2023-01-01"
    assert r2["filters"]["date_to"] == "2023-12-31"
    assert r2["filters"]["location"] == "Goa"


# --- Task T3: Trip-relative time (Idea A3) ---

def test_trip_relative_after_goa():
    r = extract_clues("cafe photo a few weeks after the Goa trip", F, TODAY)
    assert r["filters"]["category"] == "cafe"
    assert "episode" not in r["filters"]
    assert "location" not in r["filters"]
    assert r["filters"]["date_from"] >= "2023-12-14"
    assert r["filters"]["date_to"] <= "2024-01-30"


def test_trip_relative_just_before_fever_week():
    r = extract_clues("medicine just before fever week", F, TODAY)
    assert r["filters"]["category"] == "medicine"
    assert "episode" not in r["filters"]
    assert "location" not in r["filters"]
    assert r["filters"]["date_from"] <= "2024-02-21"
    assert r["filters"]["date_to"] == "2024-02-21"


# --- Section 7: Acceptance probe table (today = 2026-09-23) ---

def test_acceptance_probes():
    from main import FACETS as demo_facets
    t = date(2026, 9, 23)

    # 1. restaurant we went to in Goa last winter
    p1 = extract_clues("restaurant we went to in Goa last winter", demo_facets, t)
    assert p1["filters"]["location"] == "Goa"
    assert p1["filters"]["category"] == "cafe"
    assert p1["filters"]["date_from"] == "2025-12-01"
    assert p1["filters"]["date_to"] == "2026-02-28"

    # 2. last summer in kerala
    p2 = extract_clues("last summer in kerala", demo_facets, t)
    assert p2["filters"]["episode"] == "summer in kerala"
    assert p2["filters"]["date_from"] == "2026-05-01"
    assert p2["filters"]["date_to"] == "2026-06-30"

    # 3. new year's eve party goa 2025
    p3 = extract_clues("new year's eve party goa 2025", demo_facets, t)
    assert p3["filters"]["episode"] == "new year goa"
    assert p3["filters"]["location"] == "Goa"
    assert p3["filters"]["date_from"] == "2025-12-28"
    assert p3["filters"]["date_to"] == "2026-01-03"

    # 4. Goa trip photos after sunset
    p4 = extract_clues("Goa trip photos after sunset", demo_facets, t)
    assert p4["filters"]["episode"] == "goa trip"
    assert p4["filters"]["location"] == "Goa"
    assert "date_from" not in p4["filters"]

    # 5. beach photo a few weeks after the Goa trip
    p5 = extract_clues("beach photo a few weeks after the Goa trip", demo_facets, t)
    assert p5["filters"]["category"] == "beach"
    assert "episode" not in p5["filters"]
    assert "location" not in p5["filters"]
    assert p5["filters"]["date_from"] == "2023-12-11"
    assert p5["filters"]["date_to"] == "2024-01-22"

    # 6. photos just before the cousin wedding
    p6 = extract_clues("photos just before the cousin wedding", demo_facets, t)
    assert p6["filters"]["date_from"] == "2024-06-08"
    assert p6["filters"]["date_to"] == "2024-06-22"

    # 7. I may have taken a photo of a medicine strip
    p7 = extract_clues("I may have taken a photo of a medicine strip", demo_facets, t)
    assert p7["filters"] == {"category": "medicine"}

    # 8. road trip to Manali
    p8 = extract_clues("road trip to Manali", demo_facets, t)
    assert p8["filters"] == {"location": "Manali"}

    # 9. parking spot at the mall
    p9 = extract_clues("parking spot at the mall", demo_facets, t)
    assert p9["filters"]["category"] == "parking"

    # 10. whiteboard from the offsite
    p10 = extract_clues("whiteboard from the offsite", demo_facets, t)
    assert p10["filters"]["category"] == "whiteboard"
    assert p10["filters"]["episode"] == "office offsite"

    # 11. prescription from when I had fever
    p11 = extract_clues("prescription from when I had fever", demo_facets, t)
    assert p11["filters"]["category"] == "medicine"
    assert p11["filters"]["episode"] == "fever week"

    # 12. a cosy spot with dark wood and a coffee cup (Must not over-interpret: no filters)
    p12 = extract_clues("a cosy spot with dark wood and a coffee cup", demo_facets, t)
    assert p12["filters"] == {}

    # 13. something from a while back, I think it was a bill (receipt, no date)
    p13 = extract_clues("something from a while back, I think it was a bill", demo_facets, t)
    assert p13["filters"] == {"category": "receipt"}

    # 14. that photo from sometime after a trip (no date, which trip is unknown)
    p14 = extract_clues("that photo from sometime after a trip", demo_facets, t)
    assert "date_from" not in p14["filters"]

    # 15. sometime in 2024 / July 2025ish (unchanged synthetic forms)
    p15 = extract_clues("sometime in 2024", demo_facets, t)
    assert p15["filters"]["date_from"] == "2024-01-01"
    assert p15["filters"]["date_to"] == "2024-12-31"

    p15b = extract_clues("July 2025ish", demo_facets, t)
    assert p15b["filters"]["date_from"] == "2025-07-01"
    assert p15b["filters"]["date_to"] == "2025-07-31"

    # Festival without year offers previous year alternative (F2)
    p_diwali = extract_clues("around Diwali", demo_facets, t)
    assert p_diwali["filters"]["date_from"] == "2025-10-17"
    chip_diwali = chips_by_key(p_diwali)["date_from"]
    assert "alternatives" in chip_diwali
    assert chip_diwali["alternatives"][0]["label"] == "or Diwali 2024"





def test_probe_3_literal_new_years_eve_party_in_goa():
    """The fix plan's own wording (section 8, row 3), not the easier '... goa 2025'."""
    from main import FACETS as demo_facets
    r = extract_clues("new year's eve party in goa", demo_facets, date(2026, 9, 23))
    assert r["filters"]["episode"] == "new year goa"
    assert r["filters"]["date_from"] <= "2025-12-31" <= r["filters"]["date_to"]


def test_misdated_memory_is_flagged_not_hidden():
    """F4: the Goa trip was Dec 2023; 'pichle saal' (2025) cannot contain it."""
    from main import FACETS as demo_facets
    from clues import find_conflicts
    r = extract_clues("pichle saal wali Goa trip", demo_facets, date(2026, 9, 23))
    assert r["filters"]["episode"] == "goa trip"
    conflicts = find_conflicts(r["filters"], demo_facets)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c["episode"] == "goa trip" and c["episode_dates"][0].startswith("2023-12")
    assert c["window"] == [r["filters"]["date_from"], r["filters"]["date_to"]]


def test_no_conflict_when_the_memory_fits():
    from main import FACETS as demo_facets
    from clues import find_conflicts
    r = extract_clues("last summer in kerala", demo_facets, date(2026, 9, 23))
    assert find_conflicts({"episode": "goa trip"}, demo_facets) == []
    assert find_conflicts({"episode": "summer in kerala", "date_from": "2025-05-01",
                           "date_to": "2025-06-30"}, demo_facets) == []
