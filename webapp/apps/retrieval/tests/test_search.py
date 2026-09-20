import numpy as np

from search import SearchContext, group_by_episode, search, why_strings


class FakeEncoder:
    def encode(self, texts):
        return np.array([[1.0, 0.0]], dtype=np.float32)


RECORDS = [
    {"id": "demo:1", "episode_id": "ep1", "episode": "goa trip", "location": "Goa",
     "category": "cafe", "date": "2023-12-14T10:00:00", "file": "library/0001.jpg"},
    {"id": "demo:2", "episode_id": "ep1", "episode": "goa trip", "location": "Goa",
     "category": "food", "date": "2023-12-18T10:00:00", "file": "library/0002.jpg"},
    {"id": "demo:3", "episode_id": "", "episode": "", "location": "Mumbai",
     "category": "street", "date": "2025-01-05T10:00:00", "file": "library/0003.jpg"},
]
IDS = ["demo:1", "demo:2", "demo:3"]
MATRIX = np.array([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]], dtype=np.float32)


def ctx():
    return SearchContext(ids=IDS, matrix=MATRIX, records=RECORDS, encoder=FakeEncoder())


def test_filters_restrict_the_result_set():
    out = search("cafe", {"location": "Goa"}, "trails", ctx())
    assert {p["id"] for e in out["episodes"] for p in e["photos"]} == {"demo:1", "demo:2"}


def test_baseline_mode_ignores_filters():
    out = search("cafe", {"location": "Goa"}, "baseline", ctx())
    assert out["total"] == 3
    assert out["filters_applied"] == {}


def test_results_group_by_episode_not_flat():
    groups = group_by_episode([("demo:1", 0.9), ("demo:2", 0.8)], RECORDS)
    assert len(groups) == 1
    assert groups[0]["episode"] == "goa trip"
    assert groups[0]["count"] == 2


def test_stray_photos_group_separately_from_named_episodes():
    assert len(group_by_episode([("demo:1", 0.9), ("demo:3", 0.7)], RECORDS)) == 2


def test_episode_window_spans_its_photos():
    g = group_by_episode([("demo:1", 0.9), ("demo:2", 0.8)], RECORDS)[0]
    assert g["date_from"] == "2023-12-14"
    assert g["date_to"] == "2023-12-18"


def test_groups_are_ordered_by_best_matching_photo():
    groups = group_by_episode([("demo:3", 0.95), ("demo:1", 0.4)], RECORDS)
    assert groups[0]["photos"][0]["id"] == "demo:3"


def test_why_strings_name_the_filter_and_its_value():
    w = why_strings({"location": "Goa", "category": "cafe"})
    kinds = {r["kind"]: r["value"] for r in w}
    assert kinds["location"] == "Goa"
    assert kinds["category"] == "cafe"


def test_why_strings_are_empty_without_filters():
    assert why_strings({}) == []


def test_why_strings_describe_a_date_window_as_one_reason():
    w = why_strings({"date_from": "2023-12-01", "date_to": "2023-12-31"})
    assert len(w) == 1
    assert w[0] == {"kind": "date_window", "value": "2023-12-01", "to": "2023-12-31"}


def test_why_reasons_carry_no_prose_or_score():
    for r in why_strings({"location": "Goa", "date_from": "2023-12-01", "date_to": "2023-12-31"}):
        assert set(r) <= {"kind", "value", "to"}


def test_blank_filter_values_are_ignored():
    out = search("cafe", {"location": ""}, "trails", ctx())
    assert out["filters_applied"] == {}


# --- wireframe conformance (21 Sep) ------------------------------------------
# Screen 3 cards show the episode's real size ("18 photos"), not the number of
# matched hits, and Screen 4 scrubs the whole surrounding sequence.

def test_group_reports_total_episode_size_not_just_hits():
    groups = group_by_episode([("demo:1", 0.9)], RECORDS)
    assert groups[0]["count"] == 1
    assert groups[0]["episode_total"] == 2


def test_stray_photo_has_episode_total_of_one():
    groups = group_by_episode([("demo:3", 0.9)], RECORDS)
    assert groups[0]["episode_total"] == 1


def test_episode_sequence_is_every_photo_in_date_order():
    from search import episode_sequence
    seq = episode_sequence("ep1", RECORDS)
    assert [p["id"] for p in seq] == ["demo:1", "demo:2"]


def test_episode_sequence_is_empty_for_unknown_episode():
    from search import episode_sequence
    assert episode_sequence("nope", RECORDS) == []


def test_photos_carry_no_similarity_score_to_the_ui():
    """The wireframe forbids exposing a false precision score."""
    out = search("cafe", {}, "baseline", ctx())
    for e in out["episodes"]:
        for p in e["photos"]:
            assert "score" not in p
