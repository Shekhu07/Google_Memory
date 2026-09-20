from http.client import RemoteDisconnected

import pytest
import requests

from engine import collect_reddit as cr


def _post(rid="abc123"):
    return {"id": rid, "title": "Can't find a photo from our Goa trip",
            "body": "I know it exists, searched cafe and beach, nothing came up",
            "createdAt": "2025-08-01T10:00:00Z", "url": "https://reddit.com/r/googlephotos/abc123",
            "communityName": "r/googlephotos", "dataType": "post", "username": "someone"}


def _comment():
    return {"commentId": "c9", "postTitle": "Search is broken",
            "text": "same here, took me an hour of scrolling to find the receipt",
            "created": 1754035200, "link": "https://reddit.com/r/android/c9",
            "subreddit": "android", "type": "comment", "author": "another"}


@pytest.mark.parametrize("value,expected_prefix", [
    ("2025-08-01T10:00:00Z", "2025-08-01"),
    (1754035200, "2025-08-01"),
    (1754035200000, "2025-08-01"),   # milliseconds
    ("1754035200", "2025-08-01"),
    ("not a date", ""),
    (0, ""),
])
def test_to_iso_date_normalises_actor_formats(value, expected_prefix):
    assert cr.to_iso_date(value)[:10] == expected_prefix


def test_post_maps_to_record_and_drops_author():
    rec = cr.item_to_record(_post())
    assert rec["id"] == "reddit:abc123"
    assert rec["kind"] == "post" and rec["subreddit"] == "googlephotos"
    assert rec["era"] == "hybrid"
    assert rec["text"].startswith("Can't find a photo from our Goa trip.")
    assert "someone" not in str(rec)


def test_comment_maps_through_alternative_key_names():
    rec = cr.item_to_record(_comment())
    assert rec["id"] == "reddit:c9"
    assert rec["kind"] == "comment"
    assert rec["context_title"] == "Search is broken"
    assert rec["subreddit"] == "android"
    assert "another" not in str(rec)


@pytest.mark.parametrize("drop", ["id", "createdAt", "body"])
def test_unusable_items_are_skipped_not_guessed(drop):
    item = _post()
    item.pop(drop)
    if drop == "body":
        item.pop("title")  # no text at all
    assert cr.item_to_record(item) is None


class _Resp:
    def __init__(self, data, status=200, text=""):
        self.data, self.status_code, self.text = data, status, text

    def json(self):
        return self.data


class _Session:
    """Returns queued responses in order; records the urls it was asked for."""
    def __init__(self, responses):
        self.responses, self.urls = list(responses), []

    def _next(self, url):
        self.urls.append(url)
        return self.responses.pop(0)

    def get(self, url, **kw):
        return self._next(url)

    def post(self, url, **kw):
        return self._next(url)


def test_wait_for_run_returns_dataset_id_after_running():
    session = _Session([
        _Resp({"data": {"status": "RUNNING"}}),
        _Resp({"data": {"status": "SUCCEEDED", "defaultDatasetId": "ds1"}}),
    ])
    assert cr.wait_for_run("run1", "tok", session, poll=0) == "ds1"


def test_wait_for_run_raises_when_the_actor_fails():
    session = _Session([_Resp({"data": {"status": "FAILED"}})])
    with pytest.raises(cr.ApifyRunFailed):
        cr.wait_for_run("run1", "tok", session, poll=0)


def test_start_run_reports_a_bad_actor_id_clearly():
    session = _Session([_Resp({}, status=404, text="actor not found")])
    with pytest.raises(cr.ApifyRunFailed, match="actor not found"):
        cr.start_run("nope~nope", "tok", {}, session)


def test_fetch_items_pages_until_short_batch():
    session = _Session([_Resp([{"id": str(i)} for i in range(3)]), _Resp([{"id": "3"}])])
    assert len(cr.fetch_items("ds1", "tok", session, page=3)) == 4


def test_html_entities_are_decoded():
    """Reddit returns &#39; and friends; left raw they corrupt keyword matching and quotes."""
    item = _post()
    item["title"] = "I can&#39;t find it"
    item["body"] = "searched &quot;goa cafe&quot; &amp; got nothing"
    rec = cr.item_to_record(item)
    assert "&#39;" not in rec["text"] and "&quot;" not in rec["text"] and "&amp;" not in rec["text"]
    assert "I can't find it" in rec["text"] and '"goa cafe" & got nothing' in rec["text"]


def test_input_is_search_driven_not_crawl_driven():
    """Crawling startUrls with sort=new returns today's posts, not retrieval content."""
    payload = cr.build_input(["googlephotos"], ["can't find photo"], 20)
    assert payload["ignoreStartUrls"] is True
    assert payload["sort"] == "relevance"
    assert payload["searchComments"] is True and payload["skipComments"] is False


def test_search_is_scoped_to_a_community():
    """Unscoped search returns r/China and automod boilerplate; scoping is what makes it useful."""
    payload = cr.build_input(["googlephotos"], ["can't find photo"], 20, community="googlephotos")
    assert payload["searchCommunityName"] == "googlephotos"
    assert payload["ignoreStartUrls"] is True


class _FlakyThenOk:
    def __init__(self, drops):
        self.drops, self.calls = drops, 0

    def __call__(self, *a, **kw):
        self.calls += 1
        if self.calls <= self.drops:
            raise requests.exceptions.ConnectionError(("Connection aborted.", RemoteDisconnected("x")))
        return "ok"


def test_http_calls_retry_dropped_connections(monkeypatch):
    """A dropped poll must not strand an Apify run that has already been paid for."""
    monkeypatch.setattr(cr.time, "sleep", lambda s: None)
    call = _FlakyThenOk(drops=3)
    assert cr._retrying(call) == "ok"
    assert call.calls == 4


def test_persistent_connection_failure_is_reported_clearly(monkeypatch):
    monkeypatch.setattr(cr.time, "sleep", lambda s: None)
    with pytest.raises(cr.ApifyRunFailed, match="connection kept dropping"):
        cr._retrying(_FlakyThenOk(drops=99))
