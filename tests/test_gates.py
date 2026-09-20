from http.client import RemoteDisconnected

import pytest
import requests

from engine import gate_a, gate_b, groq


@pytest.mark.parametrize("value,seconds", [("2.94s", 2.94), ("1m26.4s", 86.4), ("577ms", 0.577), ("", 5.0)])
def test_parse_wait(value, seconds):
    assert groq._parse_wait(value) == pytest.approx(seconds)


def test_keywords_match_retrieval_language_not_noise():
    assert gate_a.KEYWORDS.search("Can't find pics from Nov 2023")
    assert gate_a.KEYWORDS.search("google photos me purani photo nahi mil rahi")
    assert gate_a.KEYWORDS.search("the new search is awful")
    assert not gate_a.KEYWORDS.search("can't get rid of the ad for this app update")
    assert not gate_a.KEYWORDS.search("backup keeps failing on wifi")


def test_priority_prefers_concrete_attempts():
    concrete = "I was trying to find my receipt and kept scrolling through months of photos"
    praise = "great app easy to find photos"
    assert gate_a.priority(concrete) > gate_a.priority(praise)


def test_parse_results_keeps_valid_ids_and_labels_only():
    batch = [{"id": "a", "source": "playstore", "era": "hybrid"},
             {"id": "b", "source": "appstore", "era": "toggle"},
             {"id": "c", "source": "youtube", "era": "pre_ask"}]
    response = {"results": [
        {"id": "a", "label": "relevant", "reason": "searched for receipt"},
        {"id": "b", "label": "episode", "reason": "old label no longer valid"},
        {"id": "zzz", "label": "relevant", "reason": "unknown id"},
        {"id": "a", "label": "irrelevant", "reason": "duplicate id"},
    ]}
    out = gate_b.parse_results(response, batch)
    assert [(r["id"], r["label"]) for r in out] == [("a", "relevant")]  # b and c get retried next run


def test_client_refuses_calls_past_daily_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(groq, "LEDGER", tmp_path / "usage.json")
    monkeypatch.setenv("GROQ_API_KEY", "test")
    client = groq.GroqClient("openai/gpt-oss-20b", daily_cap=100, session=object())
    client._record(100)
    with pytest.raises(groq.DailyBudgetReached):
        client.chat_json("sys", "user")


class _FlakyClient:
    """Fails with invalid JSON for any batch larger than 2 items."""
    def __init__(self):
        self.calls = 0

    def chat_json(self, system, user, max_tokens=4000):
        import json
        self.calls += 1
        items = json.loads(user)
        if len(items) > 2:
            raise groq.JsonGenerationFailed("bad json")
        return {"results": [{"id": i["id"], "label": "irrelevant", "reason": "x"} for i in items]}


def test_label_batch_splits_on_invalid_json():
    batch = [{"id": str(i), "source": "playstore", "era": "hybrid", "text": "t"} for i in range(5)]
    client = _FlakyClient()
    out = gate_b.label_batch(client, batch)
    assert sorted(r["id"] for r in out) == ["0", "1", "2", "3", "4"]


def test_select_sample_round_robins_strata_in_priority_order():
    cands = ([{"id": f"p{i}", "source": "playstore", "era": "toggle"} for i in range(10)]
             + [{"id": "a0", "source": "appstore", "era": "pre_ask"}]
             + [{"id": f"y{i}", "source": "youtube", "era": "hybrid"} for i in range(2)])
    picked = [c["id"] for c in gate_b.select_sample(cands, 6)]
    assert picked == ["a0", "p0", "y0", "p1", "y1", "p2"]


class _FakeResponse:
    status_code = 200
    content = b"{}"
    headers: dict = {}

    def __init__(self, text="{\"ok\": true}", tokens=10):
        self._text, self._tokens = text, tokens

    def json(self):
        return {"choices": [{"message": {"content": self._text}}],
                "usage": {"total_tokens": self._tokens}}


class _DroppingSession:
    """Drops the connection for the first `drops` posts, then answers normally.

    Mirrors Groq closing a pooled keep-alive connection mid-run, which is a
    transport-level failure: it is raised by post() before any status code exists,
    so the 429/5xx branches never see it.
    """
    def __init__(self, drops: int):
        self.drops, self.calls = drops, 0

    def post(self, *a, **kw):
        self.calls += 1
        if self.calls <= self.drops:
            raise requests.exceptions.ConnectionError(
                ("Connection aborted.", RemoteDisconnected("Remote end closed connection without response")))
        return _FakeResponse()


def test_client_retries_dropped_connections(tmp_path, monkeypatch):
    monkeypatch.setattr(groq, "LEDGER", tmp_path / "usage.json")
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(groq.time, "sleep", lambda s: None)
    session = _DroppingSession(drops=2)
    client = groq.GroqClient("openai/gpt-oss-120b", session=session)
    assert client.chat_json("sys", "user") == {"ok": True}
    assert session.calls == 3  # two drops, then the answer


def test_client_gives_up_after_persistent_connection_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(groq, "LEDGER", tmp_path / "usage.json")
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(groq.time, "sleep", lambda s: None)
    session = _DroppingSession(drops=99)
    client = groq.GroqClient("openai/gpt-oss-120b", session=session)
    with pytest.raises(RuntimeError):  # not a bare ConnectionError escaping the run
        client.chat_json("sys", "user")


class _RateLimitedSession:
    """Returns a 429 with the given body/headers forever, counting calls."""
    def __init__(self, body, headers=None):
        self.body, self.headers_, self.calls = body, headers or {}, 0

    def post(self, *a, **kw):
        self.calls += 1
        resp = _FakeResponse()
        resp.status_code, resp.content = 429, b"{}"
        resp.headers = self.headers_
        resp.json = lambda: self.body
        return resp


OTPM_BODY = {"error": {"message": (
    "Request too large for model `qwen/qwen3.8-27b` in organization `org_x` service tier "
    "`on_demand` on output tokens per minute (OTPM): Limit 1000, Requested 1005. The request's "
    "expected output tokens exceed the enforced limit; reduce max_tokens.")}}


def test_oversized_request_fails_fast_instead_of_retrying(tmp_path, monkeypatch):
    """An OTPM 'Request too large' is unsatisfiable at that size: waiting cannot fix it,
    so it must raise immediately with the real reason rather than burn six retries."""
    monkeypatch.setattr(groq, "LEDGER", tmp_path / "usage.json")
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(groq.time, "sleep", lambda s: None)
    session = _RateLimitedSession(OTPM_BODY, {"x-ratelimit-reset-tokens": "21.4s"})
    client = groq.GroqClient("qwen/qwen3.8-27b", session=session)
    with pytest.raises(groq.RequestTooLarge, match="OTPM"):
        client.chat_json("sys", "user", max_tokens=6000)
    assert session.calls == 1  # not 6


def test_ordinary_rate_limit_still_waits_and_retries(tmp_path, monkeypatch):
    monkeypatch.setattr(groq, "LEDGER", tmp_path / "usage.json")
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setattr(groq.time, "sleep", lambda s: None)
    body = {"error": {"message": "Rate limit reached for tokens per minute (TPM)"}}
    session = _RateLimitedSession(body, {"x-ratelimit-reset-tokens": "2s"})
    client = groq.GroqClient("openai/gpt-oss-120b", session=session)
    with pytest.raises(RuntimeError):
        client.chat_json("sys", "user")
    assert session.calls == 6  # exhausts the retry budget, as before


def test_audit_requests_fit_under_the_output_limit():
    """The audit's per-call output budget must stay under Qwen's 1,000 OTPM ceiling."""
    from engine import audit
    assert audit.MAX_TOKENS < 1000
    assert audit.DEFAULT_BATCH == 1


def test_request_sizes_are_tuned_for_groq_scheduling():
    """Groq queues on expected output size; over-reserving stalls the run (Sep 20)."""
    from engine import extract
    assert groq.REQUEST_TIMEOUT >= 300          # a slow call must finish, not be retried
    assert 1000 < extract.MAX_TOKENS <= 3000    # real batches emit ~780 completion tokens
