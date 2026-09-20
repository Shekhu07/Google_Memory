"""Play Store collector: Google Photos reviews, newest first, back to a cutoff date.

Reviews are grouped by language, not country (en-IN and en-US return the same
reviews), so the run is per language. Short reviews ("nice app") can't describe
a retrieval attempt, so only reviews with at least --min-words are kept; the
totals seen and kept are logged for the deck funnel.

Resumable: the continuation token and oldest date reached are saved after every page.

Usage:
  .venv/bin/python -m engine.collect_playstore                       # en + hi back to 2024-01-01
  .venv/bin/python -m engine.collect_playstore --langs en --max-pages 3
"""
import argparse
import sys
import time

from google_play_scraper import Sort, reviews
from google_play_scraper.features.reviews import _ContinuationToken

from engine.common import RAW_DIR, append_jsonl, load_ids, load_json, make_record, save_json

APP_ID = "com.google.android.apps.photos"
PAGE_SIZE = 200
OUT = RAW_DIR / "playstore_reviews.jsonl"
STATE = RAW_DIR / "playstore_state.json"


def review_to_record(review: dict, lang: str) -> dict:
    rec = make_record(
        source="playstore", source_id=review["reviewId"], kind="review",
        url=f"https://play.google.com/store/apps/details?id={APP_ID}&reviewId={review['reviewId']}",
        date=review["at"].isoformat(), text=review["content"] or "",
    )
    # Rating and helpful votes are kept for prevalence weighting; user name/image are not.
    rec.update({"lang": lang, "score": review["score"], "thumbs_up": review["thumbsUpCount"],
                "app_version": review.get("reviewCreatedVersion")})
    return rec


def keep(review: dict, min_words: int) -> bool:
    return len((review["content"] or "").split()) >= min_words


def fetch_page(lang: str, token_str):
    """One page of reviews, retrying on transient failures."""
    token = None
    if token_str:
        # The library stores sort as its int value; passing the enum silently returns no reviews.
        token = _ContinuationToken(token_str, lang, "us", Sort.NEWEST.value, PAGE_SIZE, None, None)
    for attempt in range(5):
        try:
            if token:
                return reviews(APP_ID, continuation_token=token)
            return reviews(APP_ID, lang=lang, country="us", sort=Sort.NEWEST, count=PAGE_SIZE)
        except Exception as e:  # the library raises bare exceptions on network/parse errors
            wait = 2 ** attempt
            print(f"  retry {attempt + 1}/5 in {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError(f"giving up on {lang} page after 5 attempts")


def collect_lang(lang: str, state: dict, seen: set, cutoff: str, min_words: int, max_pages: int) -> None:
    s = state.setdefault(lang, {"token": None, "seen": 0, "kept": 0, "oldest": None, "done": False})
    pages = 0
    while not s["done"] and (not max_pages or pages < max_pages):
        batch, token = fetch_page(lang, s["token"])
        pages += 1
        new = [review_to_record(r, lang) for r in batch
               if keep(r, min_words) and f"playstore:{r['reviewId']}" not in seen
               and r["at"].isoformat()[:10] >= cutoff]
        append_jsonl(OUT, new)
        seen.update(r["id"] for r in new)
        s["seen"] += len(batch)
        s["kept"] += len(new)
        if batch:
            s["oldest"] = min(r["at"] for r in batch).isoformat()[:10]
        s["token"] = token.token if token else None
        s["done"] = not batch or not s["token"] or (s["oldest"] or "9999") < cutoff
        save_json(STATE, state)
        if pages % 10 == 0 or s["done"]:
            print(f"{lang}: {s['seen']:>7} seen, {s['kept']:>6} kept, reached {s['oldest']}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--langs", default="en,hi", help="comma-separated review languages")
    p.add_argument("--cutoff", default="2024-01-01", help="stop once reviews are older than this date")
    p.add_argument("--min-words", type=int, default=8)
    p.add_argument("--max-pages", type=int, default=0, help="pages per language this run (0 = until cutoff)")
    args = p.parse_args(argv)

    state = load_json(STATE, {})
    seen = load_ids(OUT)
    for lang in args.langs.split(","):
        collect_lang(lang.strip(), state, seen, args.cutoff, args.min_words, args.max_pages)
    print(f"\nreviews on disk: {len(load_ids(OUT))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
