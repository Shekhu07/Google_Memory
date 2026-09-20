from datetime import date

from engine.demo_eval import inferred_filters_for


class F:
    locations = ["Goa", "Bengaluru"]
    episodes = ["goa trip", "fever week"]
    categories = ["cafe", "food", "medicine"]
    episode_windows = {}


TODAY = date(2026, 9, 21)


def test_infers_from_the_query_alone():
    task = {"query": "on 2024-07-15", "cues_used": ["exact_date"]}
    assert inferred_filters_for(task, F, TODAY)["date_from"] == "2024-07-15"


def test_never_reads_the_target_record():
    """filters_for() gets the answer; this must not. A vague query yields nothing."""
    task = {"query": "something vague", "cues_used": ["event_anchor"], "episode": "goa trip"}
    assert inferred_filters_for(task, F, TODAY) == {}


def test_returns_only_contract_keys():
    task = {"query": "cafe in Goa last year", "cues_used": []}
    out = inferred_filters_for(task, F, TODAY)
    assert set(out) <= {"date_from", "date_to", "location", "category", "episode"}
