import pytest

from engine.collect_youtube import ApiError, QuotaExhausted, YouTubeClient, thread_to_records
from engine.common import era_for


@pytest.mark.parametrize("date,era", [
    ("2023-05-01T10:00:00Z", "pre_ask"),
    ("2024-09-30T23:59:59Z", "pre_ask"),
    ("2024-10-01T00:00:00Z", "ask_launch"),
    ("2025-06-01T00:00:00Z", "hybrid"),
    ("2026-02-28T00:00:00Z", "hybrid"),
    ("2026-03-01T00:00:00Z", "toggle"),
])
def test_era_boundaries(date, era):
    assert era_for(date) == era


def _comment(cid, text, date="2025-07-01T00:00:00Z"):
    return {"id": cid, "snippet": {"publishedAt": date, "textOriginal": text}}


def test_thread_flattens_comment_and_replies_without_author():
    thread = {
        "snippet": {"videoId": "vid1", "topLevelComment": _comment("c1", "can't find my receipt photo")},
        "replies": {"comments": [_comment("r1", "try searching 'receipt'"), _comment("r2", "   ")]},
    }
    records = thread_to_records(thread, "Find old photos")

    assert [r["id"] for r in records] == ["youtube:c1", "youtube:r1"]  # blank reply dropped
    assert records[0]["parent_id"] == "youtube_video:vid1"
    assert records[1]["parent_id"] == "youtube:c1"
    assert records[0]["era"] == "hybrid"
    assert records[0]["url"].endswith("v=vid1&lc=c1")
    assert not any("author" in k for r in records for k in r)


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class FakeSession:
    def __init__(self, data):
        self.data = data
        self.calls = 0

    def get(self, *a, **k):
        self.calls += 1
        return FakeResponse(self.data)


def test_budget_stops_before_overspending():
    session = FakeSession({"items": []})
    client = YouTubeClient("key", budget=150, session=session)
    client.search_videos("q", 25)          # 100 units
    with pytest.raises(QuotaExhausted):
        client.search_videos("q2", 25)     # would reach 200
    assert session.calls == 1 and client.spent == 100


def test_quota_error_from_api_raises_quota_exhausted():
    session = FakeSession({"error": {"message": "over", "errors": [{"reason": "quotaExceeded"}]}})
    with pytest.raises(QuotaExhausted):
        YouTubeClient("key", budget=1000, session=session).search_videos("q", 5)


def test_comments_disabled_is_an_api_error_with_reason():
    session = FakeSession({"error": {"message": "disabled", "errors": [{"reason": "commentsDisabled"}]}})
    client = YouTubeClient("key", budget=1000, session=session)
    with pytest.raises(ApiError) as exc:
        list(client.comment_pages("vid", 3))
    assert "commentsDisabled" in exc.value.reasons


@pytest.mark.parametrize("title,expected", [
    ("How to find old photos in Google Photos", True),
    ("Ask Photos: NEW Google Photos AI Search is Here!", True),
    ("Google Photos me purani photo kaise dhundhe", True),
    ("How To Recover Deleted Google Photos #ytshorts", False),
    ("Set This Settings For Cookies In GoogleChrome Browser", False),
    ("Google Lens Not Working | Fix Google Image Search", False),
    ("ChatGPT vs Gemini – AI Image Generation Test", False),
    ("Find Other Pictures of You on the Internet!", False),
    ("Gallery me photo kaise dhundhe", True),
    ("Google photos not showing all the photos - Fix", False),
])
def test_title_relevance(title, expected):
    from engine.collect_youtube import is_relevant_title
    assert is_relevant_title(title) is expected


def test_prune_drops_comments_and_replies_of_off_topic_videos(tmp_path, monkeypatch):
    import json
    from engine import collect_youtube as cy
    out = tmp_path / "c.jsonl"
    monkeypatch.setattr(cy, "OUT_COMMENTS", out)
    rows = [
        {"id": "youtube:a", "parent_id": "youtube_video:good"},
        {"id": "youtube:b", "parent_id": "youtube_video:bad"},
        {"id": "youtube:b1", "parent_id": "youtube:b"},
    ]
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    state = {"videos": {"good": {"title": "Ask Photos in Google Photos"},
                        "bad": {"title": "ChatGPT vs Gemini image generation"}}}

    assert cy.prune_off_topic(state) == 2
    assert [json.loads(l)["id"] for l in out.read_text().splitlines()] == ["youtube:a"]
    assert state["videos"]["bad"]["skipped"] == ["off_topic_title"]
