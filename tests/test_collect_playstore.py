from datetime import datetime

from engine import collect_playstore as cp


def _review(rid, text, at="2025-08-01 10:00:00"):
    return {"reviewId": rid, "content": text, "at": datetime.fromisoformat(at), "score": 2,
            "thumbsUpCount": 5, "reviewCreatedVersion": "7.1", "userName": "Someone", "userImage": "x"}


def test_record_drops_user_identity_and_keeps_rating():
    rec = cp.review_to_record(_review("r1", "search can't find my old receipt photos anymore"), "en")
    assert rec["id"] == "playstore:r1"
    assert rec["era"] == "hybrid"
    assert (rec["score"], rec["thumbs_up"], rec["lang"]) == (2, 5, "en")
    assert "Someone" not in str(rec) and "userImage" not in rec


def test_keep_requires_min_words_and_handles_empty():
    assert cp.keep(_review("a", "one two three four five six seven eight"), 8)
    assert not cp.keep(_review("b", "nice app"), 8)
    assert not cp.keep(_review("c", None), 8)


def test_collect_stops_at_cutoff_and_skips_old_reviews(tmp_path, monkeypatch):
    monkeypatch.setattr(cp, "OUT", tmp_path / "r.jsonl")
    monkeypatch.setattr(cp, "STATE", tmp_path / "s.json")
    long = "I searched for the medicine photo but nothing came back at all"
    pages = iter([
        ([_review("new", long, "2024-03-01 00:00:00")], type("T", (), {"token": "t1"})()),
        ([_review("old", long, "2023-12-30 00:00:00")], type("T", (), {"token": "t2"})()),
    ])
    monkeypatch.setattr(cp, "fetch_page", lambda lang, tok: next(pages))
    state, seen = {}, set()

    cp.collect_lang("en", state, seen, cutoff="2024-01-01", min_words=8, max_pages=0)

    assert seen == {"playstore:new"}
    assert state["en"]["done"] and state["en"]["oldest"] == "2023-12-30"


def test_resumed_token_uses_int_sort(monkeypatch):
    captured = {}

    def fake_reviews(app_id, continuation_token=None, **kw):
        captured["token"] = continuation_token
        return [], continuation_token

    monkeypatch.setattr(cp, "reviews", fake_reviews)
    cp.fetch_page("hi", "abc")
    tok = captured["token"]
    assert (tok.token, tok.lang, tok.sort, tok.count) == ("abc", "hi", 2, 200)
    assert type(tok.sort) is int
