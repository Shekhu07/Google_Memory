from engine import demo_eval as de


def _task(cues=("object",), answers=("demo:0001",)):
    return {"id": "task:000", "query": "q", "cues_used": list(cues), "answer_ids": list(answers)}


def test_scoring_finds_the_answer_and_records_its_rank():
    results = [("demo:0009", .9), ("demo:0001", .8), ("demo:0003", .7)]
    s = de.score_task(_task(), results, k=20)
    assert s["recall_at_k"] == 1.0
    assert s["hit_at_1"] is False
    assert s["rank_of_first_hit"] == 2


def test_hit_at_1_when_the_answer_ranks_first():
    s = de.score_task(_task(), [("demo:0001", .9), ("demo:0002", .8)], k=20)
    assert s["hit_at_1"] is True and s["rank_of_first_hit"] == 1


def test_miss_is_recorded_as_rank_zero_not_as_a_hit():
    s = de.score_task(_task(), [("demo:0007", .9)], k=20)
    assert s["recall_at_k"] == 0.0 and s["hit_at_1"] is False and s["rank_of_first_hit"] == 0


def test_partial_recall_when_only_some_answers_surface():
    s = de.score_task(_task(answers=("a", "b")), [("a", .9), ("z", .8)], k=20)
    assert s["recall_at_k"] == 0.5


def test_empty_results_do_not_crash():
    s = de.score_task(_task(), [], k=20)
    assert s["recall_at_k"] == 0.0 and s["rank_of_first_hit"] == 0


def test_summary_breaks_down_by_cue_and_by_cue_count():
    scored = [
        {"id": "1", "query": "", "cues": ["temporal_approx"], "n_answers": 1, "recall_at_k": 0.0, "hit_at_1": False, "rank_of_first_hit": 0},
        {"id": "2", "query": "", "cues": ["object"],          "n_answers": 1, "recall_at_k": 1.0, "hit_at_1": True,  "rank_of_first_hit": 1},
        {"id": "3", "query": "", "cues": ["object", "place_named"], "n_answers": 1, "recall_at_k": 1.0, "hit_at_1": False, "rank_of_first_hit": 4},
    ]
    s = de.summarise(scored, k=20)
    assert s["overall"]["n"] == 3
    assert s["by_cue"]["temporal_approx"]["recall_at_20"] == 0.0
    assert s["by_cue"]["object"]["n"] == 2          # appears in two tasks
    assert s["by_cue_count"]["1"]["n"] == 2 and s["by_cue_count"]["2"]["n"] == 1
    assert s["by_cue"]["object"]["found_at_all"] == 1.0


def test_summary_of_nothing_is_empty_not_a_crash():
    assert de.summarise([]) == {}


def _target():
    return {"id": "demo:0001", "category": "beach", "episode": "goa trip",
            "location": "Goa", "date": "2024-03-10T10:00:00"}


def test_exact_date_pins_the_window_to_one_day():
    f = de.filters_for(_task(cues=["exact_date"]), _target())
    assert f["date_from"] == f["date_to"] == "2024-03-10"


def test_vague_time_opens_a_window_rather_than_a_day():
    f = de.filters_for(_task(cues=["temporal_approx"]), _target())
    assert f["date_from"] < "2024-03-10" < f["date_to"]
    assert "category" not in f and "location" not in f


def test_cues_map_to_their_own_filters_only():
    assert de.filters_for(_task(cues=["place_named"]), _target()) == {"location": "Goa"}
    assert de.filters_for(_task(cues=["object"]), _target()) == {"category": "beach"}
    assert de.filters_for(_task(cues=["event_anchor"]), _target()) == {"episode": "goa trip"}


def test_cues_combine_into_one_window():
    f = de.filters_for(_task(cues=["object", "place_named", "exact_date"]), _target())
    assert f == {"category": "beach", "location": "Goa",
                 "date_from": "2024-03-10", "date_to": "2024-03-10"}


def test_missing_metadata_yields_no_filter_rather_than_a_wrong_one():
    assert de.filters_for(_task(cues=["exact_date"]), {"id": "x", "date": ""}) == {}
    assert de.filters_for(_task(cues=["event_anchor"]), {"id": "x"}) == {}
