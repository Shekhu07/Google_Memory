"""YouTube collector: search retrieval-related videos, pull their comments.

Quota (YouTube Data API v3, 10,000 units/day per Cloud project):
  search.list        = 100 units per call
  commentThreads.list =   1 unit per page (up to 100 comments + 5 replies each)

The run is resumable: finished queries and videos are recorded in a state
file, and comments already on disk are skipped.

Usage:
  .venv/bin/python -m engine.collect_youtube                 # full run
  .venv/bin/python -m engine.collect_youtube --max-queries 2 --max-videos 3 --max-pages 1
  .venv/bin/python -m engine.collect_youtube --prune          # re-filter saved data, no quota
"""
import argparse
import json
import os
import re
import sys

import requests
from dotenv import load_dotenv

from engine.common import RAW_DIR, ROOT, append_jsonl, load_ids, load_json, make_record, save_json

API = "https://www.googleapis.com/youtube/v3"
SEARCH_COST = 100
COMMENTS_COST = 1

OUT_COMMENTS = RAW_DIR / "youtube_comments.jsonl"
OUT_VIDEOS = RAW_DIR / "youtube_videos.jsonl"
STATE = RAW_DIR / "youtube_state.json"

# Grouped by what they are meant to surface. Hinglish queries test H4.
QUERIES = [
    # how-to: comments are people describing what they can't find
    "how to find old photos in google photos",
    "google photos search not working",
    "find a specific photo in google photos",
    "google photos search tips",
    "google photos can't find photo",
    "search google photos by date",
    "find screenshots in google photos",
    "find documents receipts in google photos",
    "google photos search text in photos",
    "google photos lost photo recover find",
    # Ask Photos coverage: dated reactions across eras
    "ask photos google photos",
    "google photos ask photos review",
    "google photos gemini search",
    "google photos classic search toggle",
    "google photos new search update",
    "google photos AI search problems",
    "ask photos vs classic search",
    # memory-style search demos
    "google photos natural language search",
    "google photos search by memory",
    "google photos search face people places",
    "google photos memories feature",
    "iphone photos search vs google photos search",
    # Hinglish / India
    "google photos me purani photo kaise dhundhe",
    "google photos me photo search kaise kare",
    "google photos search trick hindi",
    "google photos ask photos hindi",
    "gallery me photo kaise dhundhe",
    "google photos tips and tricks hindi",
]


# Video-title relevance check, applied before spending quota on comments.
# The photo must be about finding/searching (it still exists), not recovering
# deleted files, backup or storage. It must also name a personal photo library:
# a generic "photo"/"image" match let in web image search and Gemini image
# generation videos on the first full run (Sep 17).
_PHOTO_APP = re.compile(r"google photos|ask photos|photos app|gallery|iphone photos|apple photos", re.I)
_FINDING = re.compile(r"search|find|finding|ask photos|gemini|dhund|khoj|look(ing)? for|locate|memor|organi[sz]e", re.I)
_OFF_TOPIC = re.compile(r"recover|delet|restore|backup|back up|storage|cookie|transfer|free up|hide|lock|password|edit", re.I)


def is_relevant_title(title: str) -> bool:
    return bool(_PHOTO_APP.search(title) and _FINDING.search(title) and not _OFF_TOPIC.search(title))


def prune_off_topic(state: dict) -> int:
    """Re-apply the title filter to videos already collected; drop their comments. No quota used."""
    bad = {f"youtube_video:{vid}" for vid, meta in state["videos"].items() if not is_relevant_title(meta["title"])}
    for vid, meta in state["videos"].items():
        if f"youtube_video:{vid}" in bad:
            meta["skipped"] = ["off_topic_title"]
    if not OUT_COMMENTS.exists():
        return 0
    rows = [json.loads(line) for line in OUT_COMMENTS.open() if line.strip()]
    top_ids = {r["id"] for r in rows if r["parent_id"] in bad}
    keep = [r for r in rows if r["parent_id"] not in bad and r["parent_id"] not in top_ids]
    OUT_COMMENTS.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep))
    return len(rows) - len(keep)


class QuotaExhausted(Exception):
    pass


class YouTubeClient:
    def __init__(self, api_key: str, budget: int, spent: int = 0, session=None):
        self.api_key = api_key
        self.budget = budget
        self.spent = spent
        self.session = session or requests.Session()

    def _get(self, endpoint: str, cost: int, params: dict) -> dict:
        if self.spent + cost > self.budget:
            raise QuotaExhausted(f"budget {self.budget} would be exceeded (spent {self.spent})")
        resp = self.session.get(f"{API}/{endpoint}", params={**params, "key": self.api_key}, timeout=30)
        self.spent += cost
        data = resp.json()
        if "error" in data:
            reasons = {e.get("reason") for e in data["error"].get("errors", [])}
            if reasons & {"quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"}:
                raise QuotaExhausted(data["error"].get("message", "quota exceeded"))
            raise ApiError(reasons, data["error"].get("message", ""))
        return data

    def search_videos(self, query: str, max_results: int) -> list:
        data = self._get("search", SEARCH_COST, {
            "part": "snippet", "type": "video", "q": query,
            "maxResults": min(max_results, 50),
        })
        return data.get("items", [])

    def comment_pages(self, video_id: str, max_pages: int):
        token = None
        for _ in range(max_pages):
            params = {"part": "snippet,replies", "videoId": video_id,
                      "maxResults": 100, "textFormat": "plainText", "order": "relevance"}
            if token:
                params["pageToken"] = token
            data = self._get("commentThreads", COMMENTS_COST, params)
            yield data.get("items", [])
            token = data.get("nextPageToken")
            if not token:
                return


class ApiError(Exception):
    def __init__(self, reasons, message):
        super().__init__(f"{sorted(r for r in reasons if r)}: {message}")
        self.reasons = reasons


def thread_to_records(thread: dict, video_title: str) -> list:
    """Flatten one comment thread (top-level comment + included replies)."""
    video_id = thread["snippet"]["videoId"]
    top = thread["snippet"]["topLevelComment"]
    top_id = top["id"]
    records = [make_record(
        source="youtube", source_id=top_id, kind="comment",
        url=f"https://www.youtube.com/watch?v={video_id}&lc={top_id}",
        date=top["snippet"]["publishedAt"], text=top["snippet"]["textOriginal"],
        context_title=video_title, parent_id=f"youtube_video:{video_id}",
    )]
    for reply in thread.get("replies", {}).get("comments", []):
        records.append(make_record(
            source="youtube", source_id=reply["id"], kind="reply",
            url=f"https://www.youtube.com/watch?v={video_id}&lc={reply['id']}",
            date=reply["snippet"]["publishedAt"], text=reply["snippet"]["textOriginal"],
            context_title=video_title, parent_id=f"youtube:{top_id}",
        ))
    return [r for r in records if r["text"]]


def run(args) -> int:
    load_dotenv(ROOT / ".env")
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY missing from .env", file=sys.stderr)
        return 1

    state = load_json(STATE, {"done_queries": [], "done_videos": [], "videos": {}})
    if args.prune:
        removed = prune_off_topic(state)
        save_json(STATE, state)
        print(f"Pruned {removed} comments from off-topic videos; {len(load_ids(OUT_COMMENTS))} remain.")
        return 0
    client = YouTubeClient(api_key, budget=args.budget)
    seen = load_ids(OUT_COMMENTS)
    queries = QUERIES[: args.max_queries] if args.max_queries else QUERIES

    try:
        # 1. Search: collect candidate videos per query.
        for q in queries:
            if q in state["done_queries"]:
                continue
            for item in client.search_videos(q, args.max_videos):
                vid = item["id"]["videoId"]
                if vid not in state["videos"]:
                    state["videos"][vid] = {
                        "title": item["snippet"]["title"],
                        "published": item["snippet"]["publishedAt"],
                        "channel": item["snippet"]["channelTitle"],
                        "query": q,
                    }
            state["done_queries"].append(q)
            save_json(STATE, state)
            print(f"search  [{client.spent:>5} units] {q!r} -> {len(state['videos'])} videos total")

        # 2. Comments: pull pages per video.
        for vid, meta in state["videos"].items():
            if vid in state["done_videos"]:
                continue
            if not is_relevant_title(meta["title"]):
                meta["skipped"] = ["off_topic_title"]
                state["done_videos"].append(vid)
                continue
            new = []
            try:
                for page in client.comment_pages(vid, args.max_pages):
                    for thread in page:
                        new.extend(r for r in thread_to_records(thread, meta["title"]) if r["id"] not in seen)
            except ApiError as e:
                if not e.reasons & {"commentsDisabled", "videoNotFound", "forbidden"}:
                    raise
                meta["skipped"] = sorted(r for r in e.reasons if r)
            seen.update(r["id"] for r in new)
            append_jsonl(OUT_COMMENTS, new)
            state["done_videos"].append(vid)
            save_json(STATE, state)
            print(f"comments[{client.spent:>5} units] {vid} +{len(new):>4}  {meta['title'][:60]}")
    except QuotaExhausted as e:
        save_json(STATE, state)
        print(f"\nStopped: {e}. Rerun later to resume.")

    save_json(STATE, state)
    videos_out = [{"id": f"youtube_video:{v}", "video_id": v, **m} for v, m in state["videos"].items()]
    OUT_VIDEOS.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in videos_out))
    total = len(load_ids(OUT_COMMENTS))
    off_topic = sum(1 for m in state["videos"].values() if m.get("skipped") == ["off_topic_title"])
    print(f"\nDone. units this run: {client.spent} | videos: {len(state['videos'])} "
          f"({off_topic} skipped as off-topic) | comments on disk: {total}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--budget", type=int, default=8000, help="max quota units this run (default 8000)")
    p.add_argument("--max-queries", type=int, default=0, help="only run the first N queries (0 = all)")
    p.add_argument("--max-videos", type=int, default=25, help="videos per search query")
    p.add_argument("--prune", action="store_true", help="re-apply the title filter to collected data (no API calls)")
    p.add_argument("--max-pages", type=int, default=5, help="comment pages (100 threads each) per video")
    return run(p.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
