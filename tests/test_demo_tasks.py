import random

import pytest

from engine import demo_tasks as dt


def _library():
    lib = []
    for n, (ep, place, cats) in enumerate([
        ("goa trip", "Goa", ["beach", "cafe"]),
        ("fever week", "Bengaluru", ["medicine", "receipt"]),
    ]):
        for cat in cats:
            for i in range(3):
                lib.append({"id": f"demo:{len(lib):04d}", "category": cat, "episode": ep,
                            "episode_id": f"ep{n:02d}", "location": place,
                            "date": f"202{4+n}-0{3+n}-1{i}T10:00:00"})
    lib.append({"id": "demo:9999", "category": "street", "episode": "", "episode_id": "",
                "location": "Mumbai", "date": "2025-07-04T10:00:00"})
    return lib


def _episodes():
    return ([{"specificity": "specific_attempt", "cues_retained": ["temporal_approx"]}] * 8
            + [{"specificity": "specific_attempt", "cues_retained": ["object"]}] * 3
            + [{"specificity": "specific_attempt", "cues_retained": ["object", "place_named"]}] * 2
            + [{"specificity": "general_complaint", "cues_retained": ["exact_date"]}] * 5)


def test_profile_uses_specific_attempts_only():
    p = dt.cue_profile(_episodes())
    assert "exact_date" not in p["cue_weights"], "general complaints must not shape the task mix"
    assert p["cue_weights"]["temporal_approx"] == 8
    assert p["count_weights"][1] == 11 and p["count_weights"][2] == 2


def test_profile_drops_zero_cue_episodes():
    """47 real episodes had no cue at all; a task with no cue is unanswerable."""
    p = dt.cue_profile([{"specificity": "specific_attempt", "cues_retained": []}] * 5
                       + [{"specificity": "specific_attempt", "cues_retained": ["object"]}])
    assert 0 not in p["count_weights"]


def test_profile_never_returns_empty_weights():
    assert dt.cue_profile([])["count_weights"]


def test_unsupported_cues_are_excluded():
    """The library has no people or captions; scoring against them would be dishonest."""
    p = dt.cue_profile([{"specificity": "specific_attempt",
                         "cues_retained": ["who_with", "own_label_or_caption", "object"]}])
    assert set(p["cue_weights"]) == {"object"}


@pytest.mark.parametrize("cue,expect", [
    ("place_named", "in Goa"),
    ("event_anchor", "from the goa trip"),
    ("exact_date", "on 2024-03-10"),
    ("object", "beach"),
])
def test_phrases_read_like_something_a_person_would_type(cue, expect):
    rec = {"category": "beach", "episode": "goa trip", "location": "Goa", "date": "2024-03-10T10:00:00"}
    assert dt.phrase(cue, rec, random.Random(1)) == expect


def test_temporal_phrase_is_vague_and_never_leaks_the_exact_date():
    rec = {"category": "beach", "date": "2024-03-10T10:00:00"}
    for seed in range(12):
        said = dt.phrase("temporal_approx", rec, random.Random(seed))
        assert "2024-03-10" not in said and said
        assert "2024" in said


def test_phrases_degrade_gracefully_when_the_field_is_missing():
    assert dt.phrase("event_anchor", {"category": "x"}, random.Random(1)) == ""
    assert dt.phrase("exact_date", {"category": "x", "date": ""}, random.Random(1)) == ""
    assert dt.phrase("temporal_approx", {"category": "x", "date": ""}, random.Random(1))


def test_every_task_has_answers_that_exist_in_the_library():
    lib = _library()
    ids = {r["id"] for r in lib}
    tasks = dt.generate(lib, dt.cue_profile(_episodes()), n=20)
    # a 13-image library cannot yield 20 unique queries; the generator says so
    # rather than padding the mix with easier multi-cue tasks
    assert 10 <= len(tasks) <= 20
    for t in tasks:
        assert t["answer_ids"], t
        assert set(t["answer_ids"]) <= ids, t
        assert t["target_id"] in t["answer_ids"] or t["n_answers"] > 0
        assert t["query"].strip()


def test_event_anchor_answers_span_the_whole_episode():
    lib = _library()
    rng = random.Random(3)
    target = next(r for r in lib if r["episode_id"] == "ep00")
    task = dt.build_task(0, target, lib, ["event_anchor"], rng)
    assert len(task["answer_ids"]) == 6      # all of ep00, both categories
    assert task["query"] == "from the goa trip"


def test_event_anchor_plus_object_narrows_within_the_episode():
    lib = _library()
    target = next(r for r in lib if r["episode_id"] == "ep00" and r["category"] == "beach")
    task = dt.build_task(0, target, lib, ["event_anchor", "object"], random.Random(3))
    assert len(task["answer_ids"]) == 3
    assert all(i.startswith("demo:") for i in task["answer_ids"])


def test_queries_are_unique_and_generation_is_deterministic():
    lib, prof = _library(), dt.cue_profile(_episodes())
    a = dt.generate(lib, prof, n=15, seed=11)
    b = dt.generate(lib, prof, n=15, seed=11)
    assert [t["query"] for t in a] == [t["query"] for t in b]
    assert len({t["query"] for t in a}) == len(a)


def test_task_mix_is_dominated_by_single_cue_tasks():
    """Matches the engine finding: 79 of 97 cued episodes had exactly one cue."""
    tasks = dt.generate(_library(), dt.cue_profile(_episodes()), n=30)
    single = sum(1 for t in tasks if len(t["cues_used"]) == 1)
    assert single / len(tasks) >= 0.6, f"only {single}/{len(tasks)} single-cue"


def test_allocate_matches_the_observed_cue_count_mix():
    alloc = dt.allocate(30, {1: 79, 2: 12, 3: 6})
    assert sum(alloc.values()) == 30
    assert alloc[1] >= 22            # ~81% single-cue, as observed
    assert alloc.get(3, 0) <= 3


def test_allocate_handles_drift_and_degenerate_input():
    assert sum(dt.allocate(30, {1: 1}).values()) == 30
    assert sum(dt.allocate(7, {1: 5, 2: 3, 3: 1}).values()) == 7


def test_a_stray_photo_scores_against_itself_only():
    """'the beach' must not score against every beach in the library."""
    lib = _library()
    stray = next(r for r in lib if not r["episode_id"])
    task = dt.build_task(0, stray, lib, ["object"], random.Random(1))
    assert task["answer_ids"] == [stray["id"]]


def test_answer_sets_stay_small_enough_to_measure():
    lib = _library()
    tasks = dt.generate(lib, dt.cue_profile(_episodes()), n=15)
    assert all(t["n_answers"] <= 8 for t in tasks), \
        [(t["query"], t["n_answers"]) for t in tasks if t["n_answers"] > 8]
