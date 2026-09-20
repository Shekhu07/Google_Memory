"""Reddit collector via an Apify actor (Reddit no longer allows direct extraction).

Added Sep 18 after extraction showed why this source is needed: of the first 224
extracted app-store posts only 20.5% were specific retrieval attempts and just
4.9% carried a stated outcome, because reviews say "search is terrible" rather
than "I looked for X, typed Y, got Z". Reddit posts and comments are narrative,
so they are far likelier to contain an attempt *with* an outcome. Adding Reddit
also pulls Play Store back under the plan's 60% per-source cap (it is currently
84% of the relevant pool).

Actor choice is deliberately NOT hardcoded: Apify's Reddit actors come and go and
their ids and output fields differ. Pass --actor with an id from apify.com/store.
The plan's two candidates are the cheapest (about $0.60 per 1,000 items) and the
best-rated (about $3.40 per 1,000). Run --limit 20 first and read the output
before any bulk run; that check is in the plan and it is cheap insurance against
paying for a scraper whose fields don't map.

Field mapping is tolerant by design: actors disagree on key names, so each field
is looked up under several plausible aliases and an item that lacks an id, a date
or usable text is skipped rather than guessed at.

Usage:
  .venv/bin/python -m engine.collect_reddit --actor <id> --limit 20   # always do this first
  .venv/bin/python -m engine.collect_reddit --actor <id>
"""
import argparse
import html
import os
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from engine.common import RAW_DIR, ROOT, append_jsonl, load_ids, make_record

OUT = RAW_DIR / "reddit_posts.jsonl"
API = "https://api.apify.com/v2"
SUBREDDITS = ["googlephotos", "GooglePixel", "android", "iphone", "india"]
SEARCHES = [
    "google photos can't find photo",
    "google photos search not working",
    "find old photo google photos",
    "google photos search useless",
    "ask photos search",
]
POLL_SECONDS = 10
MAX_WAIT_SECONDS = 1800

# Actors disagree on field names; try each alias in order.
ID_KEYS = ("id", "postId", "commentId", "shortId")
TEXT_KEYS = ("body", "text", "content", "selftext", "postText", "comment")
TITLE_KEYS = ("title", "postTitle", "parsedTitle")
DATE_KEYS = ("createdAt", "created_at", "created", "date", "postedAt", "timestamp")
URL_KEYS = ("url", "link", "postUrl", "permalink")
SUB_KEYS = ("communityName", "parsedCommunityName", "subreddit", "community")
KIND_KEYS = ("dataType", "type", "kind")


class ApifyRunFailed(RuntimeError):
    pass


def _retrying(call, *a, **kw):
    """Run an HTTP call, retrying dropped connections.

    Same failure the Groq client hit on Sep 18: a pooled keep-alive connection is
    closed mid-run and requests raises before any status code exists. A long Apify
    poll is exactly the shape that provokes it, and losing the connection here
    strands a run that has already been paid for.
    """
    last = None
    for attempt in range(6):
        try:
            return call(*a, **kw)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last = e
            time.sleep(2 ** attempt)
    raise ApifyRunFailed(f"connection kept dropping: {last}")


def _first(item: dict, keys: tuple, default=""):
    for k in keys:
        v = item.get(k)
        if v not in (None, "", []):
            return v
    return default


def to_iso_date(value) -> str:
    """Actors return ISO strings or epoch seconds/millis; normalise to ISO, '' if unusable."""
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
        seconds = float(value)
        if seconds > 1e11:  # milliseconds
            seconds /= 1000
        if seconds <= 0:
            return ""
        return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="seconds")
    if isinstance(value, str) and len(value) >= 10 and value[:4].isdigit():
        return value
    return ""


def item_to_record(item: dict):
    """Map one actor item to the shared record shape, or None if it can't be trusted."""
    rid, date = _first(item, ID_KEYS), to_iso_date(_first(item, DATE_KEYS))
    title, body = str(_first(item, TITLE_KEYS)), str(_first(item, TEXT_KEYS))
    title, body = html.unescape(title), html.unescape(body)
    text = f"{title}. {body}".strip(". ").strip() if title and body else (body or title)
    if not rid or not date or not text:
        return None
    kind = "comment" if "comment" in str(_first(item, KIND_KEYS)).lower() else "post"
    rec = make_record(
        source="reddit", source_id=str(rid), kind=kind, url=str(_first(item, URL_KEYS)),
        date=date, text=text, context_title=title if kind == "comment" else "",
    )
    # Author identity is deliberately never stored, matching the other collectors.
    rec["subreddit"] = str(_first(item, SUB_KEYS)).removeprefix("r/")
    return rec


def build_input(subreddits: list, searches: list, limit: int, community: str = "") -> dict:
    """Actor inputs vary; these keys are the ones the common Reddit actors accept."""
    return {
        # Scoped search. Two trials on Sep 19 showed this actor does one of two things
        # and neither is what we want by default:
        #   startUrls + sort=new  -> crawls subreddit front pages: got that morning's
        #                            r/GooglePixel posts about fingerprint sensors.
        #   ignoreStartUrls       -> searches ALL of Reddit: got r/China, r/Entomology,
        #                            r/garland and a pile of automod boilerplate.
        # `searchCommunityName` is the field that scopes `searches` to one community,
        # which is what actually produces retrieval content. It takes a single community,
        # so a multi-subreddit sweep means one run per community.
        "startUrls": [{"url": f"https://www.reddit.com/r/{s}/"} for s in subreddits],
        "ignoreStartUrls": True,
        "searchCommunityName": community,
        "searches": searches,
        "sort": "relevance",
        "maxItems": limit,
        "maxPostCount": limit,
        "maxComments": limit,
        "skipComments": False,
        "searchPosts": True,
        "searchComments": True,
    }


def start_run(actor: str, token: str, payload: dict, session) -> str:
    resp = _retrying(session.post, f"{API}/acts/{actor}/runs", params={"token": token}, json=payload, timeout=60)
    if resp.status_code >= 400:
        raise ApifyRunFailed(f"starting actor {actor} failed: {resp.status_code} {resp.text[:200]}")
    return resp.json()["data"]["id"]


def wait_for_run(run_id: str, token: str, session, poll=POLL_SECONDS, max_wait=MAX_WAIT_SECONDS) -> str:
    """Block until the run leaves RUNNING/READY; return its dataset id."""
    waited = 0
    while True:
        data = _retrying(session.get, f"{API}/actor-runs/{run_id}", params={"token": token}, timeout=60).json()["data"]
        status = data["status"]
        if status == "SUCCEEDED":
            return data["defaultDatasetId"]
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise ApifyRunFailed(f"run {run_id} ended {status}")
        if waited >= max_wait:
            raise ApifyRunFailed(f"run {run_id} still {status} after {max_wait}s")
        time.sleep(poll)
        waited += poll


def fetch_items(dataset_id: str, token: str, session, page=1000) -> list:
    """Every item in the run's dataset, paged."""
    items, offset = [], 0
    while True:
        batch = _retrying(session.get, f"{API}/datasets/{dataset_id}/items",
                          params={"token": token, "offset": offset, "limit": page},
                          timeout=120).json()
        if not batch:
            return items
        items.extend(batch)
        offset += len(batch)
        if len(batch) < page:
            return items


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--actor", default="", help="Apify actor id, e.g. user~reddit-scraper")
    p.add_argument("--limit", type=int, default=1500, help="use 20 for the first trial run")
    p.add_argument("--min-words", type=int, default=8)
    p.add_argument("--subreddits", default=",".join(SUBREDDITS))
    p.add_argument("--dataset", default="",
                   help="ingest an existing run's dataset id instead of starting (and paying for) a new run")
    p.add_argument("--community", default="googlephotos",
                   help="scope the searches to one subreddit (the actor takes only one)")
    args = p.parse_args(argv)

    load_dotenv(ROOT / ".env")
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("APIFY_TOKEN is not set. Add it to .env (never paste it into a shell or a chat).")
        return 1

    session = requests.Session()
    if args.dataset:
        dataset_id = args.dataset
        print(f"ingesting existing dataset {dataset_id} (no new run, no new cost)")
    else:
        payload = build_input(args.subreddits.split(","), SEARCHES, args.limit, args.community)
        print(f"starting {args.actor} (limit {args.limit})...")
        dataset_id = wait_for_run(start_run(args.actor, token, payload, session), token, session)
    items = fetch_items(dataset_id, token, session)

    seen = load_ids(OUT)
    records = [r for r in (item_to_record(i) for i in items) if r]
    new = [r for r in records if len(r["text"].split()) >= args.min_words and r["id"] not in seen]
    append_jsonl(OUT, new)

    skipped = len(items) - len(records)
    print(f"{len(items)} items fetched | {skipped} unmappable | {len(new)} new kept "
          f"| {len(records) - len(new)} duplicates or too short")
    print(f"posts on disk: {len(load_ids(OUT))}")
    if args.limit <= 20:
        print("\nTrial run. Read data/raw/reddit_posts.jsonl before running in bulk;\n"
              "if 'unmappable' is high the actor's field names differ - extend the *_KEYS tuples.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
