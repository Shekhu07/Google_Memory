from facets import load_facets

LIB = [
    {"id": "a", "category": "cafe",   "location": "Goa",       "episode": "goa trip", "date": "2023-12-14T10:00:00"},
    {"id": "b", "category": "food",   "location": "Goa",       "episode": "goa trip", "date": "2023-12-18T10:00:00"},
    {"id": "c", "category": "receipt","location": "Bengaluru", "episode": "",         "date": "2024-02-21T10:00:00"},
]


def test_collects_distinct_values_sorted():
    f = load_facets(LIB)
    assert f.locations == ["Bengaluru", "Goa"]
    assert f.categories == ["cafe", "food", "receipt"]
    assert f.episodes == ["goa trip"]


def test_blank_episode_is_not_a_facet():
    assert "" not in load_facets(LIB).episodes


def test_episode_window_spans_first_to_last_photo():
    assert load_facets(LIB).episode_windows["goa trip"] == ("2023-12-14", "2023-12-18")
