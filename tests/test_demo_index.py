import numpy as np
import pytest

from engine import demo_index as di


def _records():
    return [
        {"id": "demo:0000", "category": "cafe",    "location": "Goa",       "episode": "goa trip",   "date": "2023-12-09T10:00:00"},
        {"id": "demo:0001", "category": "beach",   "location": "Goa",       "episode": "goa trip",   "date": "2023-12-10T11:00:00"},
        {"id": "demo:0002", "category": "receipt", "location": "Bengaluru", "episode": "fever week", "date": "2024-02-20T09:00:00"},
        {"id": "demo:0003", "category": "cafe",    "location": "Bengaluru", "episode": "",           "date": "2025-06-01T09:00:00"},
        {"id": "demo:0004", "category": "medicine","location": "Bengaluru", "episode": "fever week", "date": ""},
    ]


def _index():
    ids = [r["id"] for r in _records()]
    # 0000 and 0003 point the same way; the query below matches them best
    matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [0.9, 0.1, 0], [0, 0.5, 0.5]], dtype="float32")
    return ids, matrix


def test_normalise_makes_dot_product_a_cosine():
    m = di.normalise(np.array([[3.0, 4.0]]))
    assert np.allclose(np.linalg.norm(m, axis=1), 1.0)
    assert di.normalise(np.array([1.0, 0.0])).shape == (1, 2)   # 1-D is promoted


def test_date_window_is_inclusive_and_tolerates_missing_dates():
    r = {"date": "2024-02-20T09:00:00"}
    assert di.in_window(r, "2024-02-20", "2024-02-20")
    assert di.in_window(r, "2024-01-01", "2024-12-31")
    assert not di.in_window(r, "2024-02-21", "")
    assert not di.in_window(r, "", "2024-02-19")
    assert di.in_window({"date": ""})                      # no filter, no date -> kept
    assert not di.in_window({"date": ""}, "2024-01-01")    # filtered, no date -> dropped


def test_filters_combine_and_all_must_match():
    recs = _records()
    assert {r["id"] for r in di.apply_filters(recs, location="goa")} == {"demo:0000", "demo:0001"}
    assert {r["id"] for r in di.apply_filters(recs, category="cafe")} == {"demo:0000", "demo:0003"}
    assert {r["id"] for r in di.apply_filters(recs, episode="fever")} == {"demo:0002", "demo:0004"}
    # location AND category together
    assert {r["id"] for r in di.apply_filters(recs, location="goa", category="cafe")} == {"demo:0000"}
    assert di.apply_filters(recs, location="goa", category="receipt") == []


def test_baseline_ranks_by_similarity():
    ids, matrix = _index()
    q = np.array([[1.0, 0.0, 0.0]])
    out = di.baseline_search(q, ids, matrix, top_k=3)
    assert [i for i, _ in out][:2] == ["demo:0000", "demo:0003"]
    assert out[0][1] > out[1][1]


def test_filtered_search_restricts_to_the_window_and_can_beat_the_baseline():
    """The point of the MVP: the right answer is buried until metadata narrows the pool."""
    ids, matrix = _index()
    recs = _records()
    q = np.array([[1.0, 0.0, 0.0]])
    baseline = di.baseline_search(q, ids, matrix, top_k=1)
    assert baseline[0][0] == "demo:0000"
    # asking only for the Bengaluru cafe surfaces 0003, which the baseline ranked second
    narrowed = di.filtered_search(q, ids, matrix, recs, top_k=5, location="Bengaluru", category="cafe")
    assert [i for i, _ in narrowed] == ["demo:0003"]


def test_filtered_search_returns_nothing_when_the_window_is_empty():
    ids, matrix = _index()
    q = np.array([[1.0, 0.0, 0.0]])
    assert di.filtered_search(q, ids, matrix, _records(), location="Paris") == []


def test_recall_at_k_counts_known_answers_only_inside_k():
    results = [("a", 0.9), ("b", 0.8), ("c", 0.7)]
    assert di.recall_at_k(results, {"a", "b"}, k=3) == 1.0
    assert di.recall_at_k(results, {"a", "z"}, k=3) == 0.5
    assert di.recall_at_k(results, {"c"}, k=2) == 0.0      # outside k
    assert di.recall_at_k(results, set()) == 0.0


def test_index_round_trips_through_npz(tmp_path, monkeypatch):
    monkeypatch.setattr(di, "INDEX", tmp_path / "index.npz")
    ids, matrix = _index()
    np.savez_compressed(di.INDEX, ids=np.array(ids), matrix=di.normalise(matrix))
    back_ids, back_matrix = di.load_index()
    assert back_ids == ids
    assert back_matrix.shape == matrix.shape
    assert np.allclose(np.linalg.norm(back_matrix, axis=1), 1.0)
