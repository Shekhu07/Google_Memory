"""Minimal Groq chat client with a persisted per-model daily token ledger.

Free tier (checked Sep 17, 2026): 30 RPM, 1K RPD, 8K TPM, 200K TPD per model.
The ledger stops a run before the daily cap instead of hitting hard 429s, and
429s that still happen (per-minute limits) are waited out using retry-after.
"""
import json
import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from engine.common import ROOT, load_json, save_json

URL = "https://api.groq.com/openai/v1/chat/completions"
LEDGER = ROOT / "data" / "interim" / "groq_usage.json"
DAILY_TOKEN_CAP = 190_000  # stay under the 200K free-tier TPD
# Measured Sep 20: a slow free-tier request can exceed two minutes. At timeout=120
# the client discarded the server's work and retried from scratch, which turned a
# slow run into a stalled one (12-25 posts/hour instead of ~800).
REQUEST_TIMEOUT = 300


class DailyBudgetReached(Exception):
    pass


class RequestTooLarge(Exception):
    """The request's expected output exceeds the model's per-minute output limit (OTPM).

    Unlike an ordinary rate limit this cannot be waited out: Groq rejects on the
    request's *expected* output size, so the same request will keep failing until
    max_tokens (or the batch) is reduced. Groq publishes no OTPM header, so the
    message is the only diagnostic.
    """


class JsonGenerationFailed(Exception):
    """The model produced invalid JSON; Groq rejects the response (code json_validate_failed)."""


def _today() -> str:
    # Groq's daily windows are rolling; UTC date is a conservative approximation.
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _parse_wait(value: str) -> float:
    """Groq reset headers look like '2.94s', '1m26.4s' or '577ms'."""
    if not value:
        return 5.0
    total, num = 0.0, ""
    i = 0
    while i < len(value):
        ch = value[i]
        if ch.isdigit() or ch == ".":
            num += ch
        elif value.startswith("ms", i):
            total += float(num) / 1000
            num = ""
            i += 1
        elif ch in "hms":
            total += float(num) * {"h": 3600, "m": 60, "s": 1}[ch]
            num = ""
        i += 1
    return total or float(num or 5)


class GroqClient:
    def __init__(self, model: str, daily_cap: int = DAILY_TOKEN_CAP, session=None):
        load_dotenv(ROOT / ".env")
        self.key = os.environ["GROQ_API_KEY"]
        self.model = model
        self.daily_cap = daily_cap
        self.session = session or requests.Session()

    def used_today(self) -> int:
        return load_json(LEDGER, {}).get(_today(), {}).get(self.model, 0)

    def _record(self, tokens: int) -> None:
        ledger = load_json(LEDGER, {})
        day = ledger.setdefault(_today(), {})
        day[self.model] = day.get(self.model, 0) + tokens
        save_json(LEDGER, ledger)

    def chat_json(self, system: str, user: str, max_tokens: int = 4000, reasoning_effort: str = "low") -> dict:
        if self.used_today() >= self.daily_cap:
            raise DailyBudgetReached(f"{self.model}: {self.used_today()} tokens used today")
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
            "max_completion_tokens": max_tokens,
            "temperature": 0,
        }
        if self.model.startswith("openai/gpt-oss"):
            body["reasoning_effort"] = reasoning_effort
        last_error = None
        for attempt in range(6):
            try:
                resp = self.session.post(URL, headers={"Authorization": f"Bearer {self.key}"}, json=body, timeout=REQUEST_TIMEOUT)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Transport-level failure: raised before any status code exists, so the
                # 429/5xx branches below never see it. Groq drops pooled keep-alive
                # connections on long runs, so back off and retry as for a 5xx.
                last_error = e
                time.sleep(2 ** attempt)
                continue
            if resp.status_code == 429:
                data = resp.json() if resp.content else {}
                msg = json.dumps(data)
                if "per day" in msg or "TPD" in msg or "RPD" in msg:
                    raise DailyBudgetReached(msg[:300])
                if "Request too large" in msg:
                    raise RequestTooLarge(msg[:300])
                retry_after = resp.headers.get("retry-after")
                wait = float(retry_after) if retry_after else _parse_wait(resp.headers.get("x-ratelimit-reset-tokens", ""))
                time.sleep(min(wait, 60) + 1)
                continue
            if resp.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            data = resp.json()
            if "error" in data:
                if data["error"].get("code") == "json_validate_failed":
                    raise JsonGenerationFailed(data["error"].get("message", ""))
                raise RuntimeError(data["error"])
            self._record(data["usage"]["total_tokens"])
            return json.loads(data["choices"][0]["message"]["content"])
        raise RuntimeError(f"{self.model}: gave up after repeated 429/5xx/connection failures ({last_error})")


def split_on_json_failure(call, batch: list, label: str = "") -> list:
    """Run call(batch); on invalid JSON retry once, then split the batch in half.
    A single item that keeps failing is skipped (left for the next run)."""
    for _ in range(2):
        try:
            return call(batch)
        except JsonGenerationFailed:
            continue
    if len(batch) == 1:
        print(f"  skipped {batch[0]['id']}{label}: invalid JSON twice")
        return []
    mid = len(batch) // 2
    return split_on_json_failure(call, batch[:mid], label) + split_on_json_failure(call, batch[mid:], label)
