import numpy as np
import pytest
from pathlib import Path
from cues import build_bank, suggest, steer, known, VOCAB, PRESENT_Z
from encoder import TextEncoder

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="module")
def encoder():
    return TextEncoder(DATA)


@pytest.fixture(scope="module")
def bank(encoder):
    _index = np.load(DATA / "index.npz", allow_pickle=False)
    return build_bank(encoder, _index["matrix"])


def test_fewer_than_4_candidates_returns_empty(bank, encoder):
    qv = encoder.encode(["celebration"]).astype(np.float32)
    assert suggest(bank, "celebration", qv, [0, 1, 2]) == []
    assert suggest(bank, "celebration", qv, []) == []


def test_cake_query_does_not_offer_a_cake_when_share_over_80(bank, encoder):
    cake_idx = bank.labels.index("a cake")
    # Candidates with cake present
    cake_rows = np.where(bank.z[:, cake_idx] > PRESENT_Z)[0]
    if len(cake_rows) >= 10:
        candidates = list(cake_rows[:10])
        qv = encoder.encode(["birthday celebration"]).astype(np.float32)
        suggestions = suggest(bank, "birthday celebration", qv, candidates)
        offered = [s["label"] for s in suggestions]
        assert "a cake" not in offered


def test_group_photo_query_does_not_offer_a_group_because_query_says_it(bank, encoder):
    qv = encoder.encode(["group photo"]).astype(np.float32)
    candidates = list(range(20))
    suggestions = suggest(bank, "group photo", qv, candidates)
    offered = [s["label"] for s in suggestions]
    assert "a group" not in offered


def test_exclude_is_respected(bank, encoder):
    qv = encoder.encode(["holiday celebration"]).astype(np.float32)
    candidates = list(range(24))
    base = suggest(bank, "holiday celebration", qv, candidates, limit=4)
    if base:
        first_label = base[0]["label"]
        filtered = suggest(bank, "holiday celebration", qv, candidates, limit=4, exclude=[first_label])
        assert first_label not in [s["label"] for s in filtered]


def test_at_most_two_per_group(bank, encoder):
    qv = encoder.encode(["walk outside"]).astype(np.float32)
    candidates = list(range(24))
    suggestions = suggest(bank, "walk outside", qv, candidates, limit=4)
    from collections import Counter
    group_counts = Counter(s["group"] for s in suggestions)
    for g, count in group_counts.items():
        assert count <= 2, f"Group {g} has {count} suggestions, expected <= 2"


def test_steer_ignores_unknown_labels(bank, encoder):
    qv = encoder.encode(["mountain hike"]).astype(np.float32)
    qv = qv / np.linalg.norm(qv)
    steered = steer(bank, qv, ["unknown_label_xyz", "another_unknown"])
    np.testing.assert_allclose(steered, qv, rtol=1e-5)


def test_known_predicate():
    assert known("orange") is True
    assert known("candles or diyas") is True
    assert known("unknown_fake_label") is False
