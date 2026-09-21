from datetime import date

from facets import load_facets
from llm_clues import extract

LIB = [{"id": "a", "category": "cafe", "location": "Goa", "episode": "goa trip",
        "date": "2023-12-14T10:00:00"}]
F = load_facets(LIB)
TODAY = date(2026, 9, 21)


class OkClient:
    """engine.groq.GroqClient.chat_json returns an already-parsed dict."""

    def chat_json(self, *a, **k):
        return {"filters": {"location": "Goa"},
                "chips": [{"id": "c1", "cue": "place_named", "label": "Goa",
                           "filter_key": "location", "value": "Goa", "editable": True}]}


class BoomClient:
    def __init__(self, exc):
        self.exc = exc

    def chat_json(self, *a, **k):
        raise self.exc


def test_uses_the_llm_when_it_answers():
    r = extract("our Goa trip", F, OkClient(), TODAY)
    assert r["source"] == "llm"
    assert r["filters"]["location"] == "Goa"
    assert r["notice"] is None


def test_falls_back_to_rules_when_the_budget_is_gone():
    from engine.groq import DailyBudgetReached
    r = extract("our Goa trip", F, BoomClient(DailyBudgetReached("cap")), TODAY)
    assert r["source"] == "rules"
    assert r["filters"]["location"] == "Goa"
    assert r["notice"]


def test_falls_back_on_any_transport_error():
    assert extract("our Goa trip", F, BoomClient(TimeoutError("slow")), TODAY)["source"] == "rules"


def test_falls_back_when_the_model_returns_junk():
    class Junk:
        def chat_json(self, *a, **k):
            return "not a dict at all"
    assert extract("our Goa trip", F, Junk(), TODAY)["source"] == "rules"


def test_falls_back_when_no_client_is_configured():
    assert extract("our Goa trip", F, None, TODAY)["source"] == "rules"


def test_filter_keys_outside_the_contract_are_dropped():
    class Extra:
        def chat_json(self, *a, **k):
            return {"filters": {"location": "Goa", "camera": "Pixel"}, "chips": []}
    assert extract("x", F, Extra(), TODAY)["filters"] == {"location": "Goa"}


def test_filter_values_outside_the_library_vocabulary_are_dropped():
    class Hallucinating:
        def chat_json(self, *a, **k):
            return {"filters": {"location": "Atlantis", "category": "cafe"}, "chips": []}
    out = extract("x", F, Hallucinating(), TODAY)["filters"]
    assert "location" not in out
    assert out["category"] == "cafe"


def test_malformed_dates_from_the_model_are_dropped():
    class BadDate:
        def chat_json(self, *a, **k):
            return {"filters": {"date_from": "sometime", "date_to": "2025-01-01"}, "chips": []}
    assert "date_from" not in extract("x", F, BadDate(), TODAY)["filters"]


def test_chips_are_dropped_when_their_filter_did_not_survive():
    class Mismatch:
        def chat_json(self, *a, **k):
            return {"filters": {"location": "Atlantis"},
                    "chips": [{"id": "c1", "cue": "place_named", "label": "Atlantis",
                               "filter_key": "location", "value": "Atlantis", "editable": True}]}
    assert extract("x", F, Mismatch(), TODAY)["chips"] == []


def test_one_chip_per_filter_key_even_if_the_model_emits_two():
    """A date window is two filter keys but one clue. The model often returns a
    chip for each, which rendered the same label twice in the UI."""
    class TwoDateChips:
        def chat_json(self, *a, **k):
            return {"filters": {"date_from": "2025-07-01", "date_to": "2025-07-31"},
                    "chips": [
                        {"id": "c1", "cue": "temporal_approx", "label": "July 2025",
                         "filter_key": "date_from", "value": "2025-07-01", "editable": True},
                        {"id": "c2", "cue": "temporal_approx", "label": "July 2025",
                         "filter_key": "date_to", "value": "2025-07-31", "editable": True},
                    ]}
    chips = extract("July 2025ish", F, TwoDateChips(), TODAY)["chips"]
    assert len(chips) == 1
    assert chips[0]["filter_key"] == "date_from"


def test_duplicate_chips_for_the_same_key_collapse_to_one():
    class Dupes:
        def chat_json(self, *a, **k):
            return {"filters": {"location": "Goa"},
                    "chips": [{"id": "a", "cue": "place_named", "label": "Goa",
                               "filter_key": "location", "value": "Goa", "editable": True},
                              {"id": "b", "cue": "place_named", "label": "Goa",
                               "filter_key": "location", "value": "Goa", "editable": True}]}
    assert len(extract("Goa", F, Dupes(), TODAY)["chips"]) == 1
