"""App Store collector: Google Photos (iOS) reviews from Apple's public RSS feed.

Apple's feed returns at most 10 pages x 50 of the most recent reviews per
country, so this source only covers recent weeks (the "toggle" era). It is used
for iOS prevalence, not for the before/after era comparison.

Usage:
  .venv/bin/python -m engine.collect_appstore
  .venv/bin/python -m engine.collect_appstore --countries us --pages 1
"""
import argparse
import sys

import requests

from engine.common import RAW_DIR, append_jsonl, load_ids, make_record

APP_ID = "962194608"  # Google Photos: Backup & Edit
FEED = "https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app}/sortby=mostrecent/json"
MAX_PAGES = 10
OUT = RAW_DIR / "appstore_reviews.jsonl"
COUNTRIES = "us,in,gb,ca,au,ie,nz,sg"


def entry_to_record(entry: dict, country: str) -> dict:
    title = entry.get("title", {}).get("label", "")
    body = entry.get("content", {}).get("label", "")
    rid = entry["id"]["label"]
    rec = make_record(
        source="appstore", source_id=rid, kind="review",
        url=f"https://apps.apple.com/{country}/app/id{APP_ID}?see-all=reviews",
        date=entry["updated"]["label"], text=f"{title}. {body}" if title else body,
    )
    # Author name is deliberately not stored.
    rec.update({"country": country, "score": int(entry["im:rating"]["label"]),
                "app_version": entry.get("im:version", {}).get("label")})
    return rec


def fetch_page(country: str, page: int, session) -> list:
    """Review entries on one feed page; [] when the feed runs out or errors."""
    resp = session.get(FEED.format(country=country, page=page, app=APP_ID), timeout=30)
    try:
        entries = resp.json().get("feed", {}).get("entry", [])
    except ValueError:  # Apple returns a non-JSON body past the last page
        return []
    if isinstance(entries, dict):  # a single entry is not wrapped in a list
        entries = [entries]
    return [e for e in entries if "content" in e]  # the first entry can be app metadata


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--countries", default=COUNTRIES)
    p.add_argument("--pages", type=int, default=MAX_PAGES)
    p.add_argument("--min-words", type=int, default=8)
    args = p.parse_args(argv)

    session = requests.Session()
    seen = load_ids(OUT)
    for country in args.countries.split(","):
        fetched = kept = 0
        oldest = ""
        for page in range(1, min(args.pages, MAX_PAGES) + 1):
            entries = fetch_page(country, page, session)
            if not entries:
                break
            fetched += len(entries)
            new = [r for r in (entry_to_record(e, country) for e in entries)
                   if len(r["text"].split()) >= args.min_words and r["id"] not in seen]
            append_jsonl(OUT, new)
            seen.update(r["id"] for r in new)
            kept += len(new)
            oldest = min(e["updated"]["label"] for e in entries)[:10]
        print(f"{country}: {fetched:>4} fetched, {kept:>4} kept, back to {oldest}")
    print(f"\nreviews on disk: {len(load_ids(OUT))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
