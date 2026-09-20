"""Demo library for the MVP: CC-licensed images arranged into believable life episodes.

The MVP cannot use anyone's real photos, so it needs a stand-in library that still
contains the cases retrieval actually fails on. Engine evidence (720 extracted
episodes) says the hard cases are utility photos with nothing to search for -
receipts, medicine strips, whiteboards, documents - plus near-duplicate bursts
where the target is present but unrecognisable.

Images come from Openverse (CC-licensed, commercial-use filter). Creator, licence
and source URL are stored for every image so the deck can attribute them; the
plan requires labelling this a representative demo library, not a Photos
integration.

Thumbnails are downloaded rather than full images: CLIP sees 224px anyway, and
500 thumbnails is tens of MB instead of a gigabyte.

Size decided 20 Sep: 500 images (Plan 2 section 9's documented cut from 1,000).

Usage:
  .venv/bin/python -m engine.demo_library --limit 20     # always trial first
  .venv/bin/python -m engine.demo_library
"""
import argparse
import json
import random
import sys
import time
from datetime import datetime, timedelta

import requests

from engine.common import ROOT, append_jsonl, load_ids, save_json

OUT_DIR = ROOT / "data" / "demo"
IMAGES = OUT_DIR / "images"
LIBRARY = OUT_DIR / "library.jsonl"
API = "https://api.openverse.org/v1/images/"
# Openverse rejects page_size > 20 for anonymous requests with a 401. The 24-image
# trial passed because its computed page size happened to be under the cap.
MAX_PAGE_SIZE = 20
MAX_PAGES = 12
UA = {"User-Agent": "nextleap-case-study-research/1.0"}

# Category -> (search query, share of the library). Utility photos are
# over-weighted on purpose: they are where retrieval actually breaks.
CATEGORIES = {
    "receipt":        ("receipt bill paper", 0.10),
    "medicine":       ("medicine pills bottle prescription", 0.08),
    "whiteboard":     ("whiteboard", 0.07),
    "document":       ("document form paperwork", 0.07),
    "cafe":           ("cafe restaurant interior table", 0.10),
    "beach":          ("beach sea coast", 0.09),
    "mountain":       ("mountain hills trek", 0.08),
    "wedding":        ("wedding ceremony celebration", 0.08),
    "festival":       ("festival lights", 0.07),
    "pet":            ("dog cat pet", 0.08),
    "food":           ("food plate meal", 0.09),
    "street":         ("street city road", 0.09),
}

# ~25 episodes: a theme, when it happened, where, and which categories it draws on.
EPISODES = [
    ("goa trip",          "2023-12-08", 4, "Goa",        ["beach", "cafe", "food", "street"]),
    ("fever week",        "2024-02-19", 5, "Bengaluru",  ["medicine", "receipt", "document"]),
    ("office offsite",    "2024-03-14", 2, "Mysuru",     ["whiteboard", "cafe", "food"]),
    ("flat hunting",      "2024-04-06", 3, "Bengaluru",  ["document", "street", "receipt"]),
    ("house move",        "2024-05-11", 2, "Bengaluru",  ["document", "receipt", "street"]),
    ("cousin wedding",    "2024-06-22", 3, "Kochi",      ["wedding", "food", "festival"]),
    ("monsoon trek",      "2024-07-20", 2, "Coorg",      ["mountain", "street", "food"]),
    ("dental work",       "2024-08-09", 3, "Bengaluru",  ["medicine", "receipt", "document"]),
    ("onam lunch",        "2024-09-15", 1, "Kochi",      ["food", "festival"]),
    ("diwali at home",    "2024-10-31", 3, "Chennai",    ["festival", "food", "pet"]),
    ("new puppy",         "2024-11-16", 4, "Bengaluru",  ["pet", "receipt", "medicine"]),
    ("year-end party",    "2024-12-28", 1, "Bengaluru",  ["cafe", "food", "street"]),
    ("car service",       "2025-01-18", 2, "Bengaluru",  ["receipt", "document", "street"]),
    ("pondicherry trip",  "2025-02-14", 3, "Pondicherry",["beach", "cafe", "street", "food"]),
    ("product workshop",  "2025-03-25", 2, "Hyderabad",  ["whiteboard", "cafe"]),
    ("passport renewal",  "2025-04-12", 2, "Bengaluru",  ["document", "receipt"]),
    ("summer in kerala",  "2025-05-20", 4, "Alleppey",   ["beach", "food", "street"]),
    ("back pain",         "2025-06-30", 3, "Bengaluru",  ["medicine", "document", "receipt"]),
    ("manali trip",       "2025-08-08", 5, "Manali",     ["mountain", "street", "food", "cafe"]),
    ("friend's sangeet",  "2025-09-19", 2, "Jaipur",     ["wedding", "festival", "food"]),
    ("diwali 2025",       "2025-10-20", 3, "Chennai",    ["festival", "food", "pet"]),
    ("laptop repair",     "2025-12-03", 2, "Bengaluru",  ["receipt", "document"]),
    ("new year goa",      "2025-12-30", 4, "Goa",        ["beach", "cafe", "food"]),
    ("puppy vet visits",  "2026-03-11", 3, "Bengaluru",  ["pet", "medicine", "receipt"]),
    ("team strategy day", "2026-05-14", 2, "Bengaluru",  ["whiteboard", "cafe", "food"]),
]

DEVICES = ["Pixel 7", "Pixel 7", "Pixel 8", "iPhone 13", "OnePlus 11"]


def quota(total: int) -> dict:
    """How many images to fetch per category, summing to `total`."""
    counts = {c: max(1, round(total * share)) for c, (_, share) in CATEGORIES.items()}
    # correct rounding drift against the largest category
    drift = total - sum(counts.values())
    if drift:
        biggest = max(counts, key=lambda c: counts[c])
        counts[biggest] = max(1, counts[biggest] + drift)
    return counts


def to_record(item: dict, category: str, index: int) -> dict:
    """Map one Openverse result to a library record, or None if unusable."""
    url = item.get("thumbnail") or item.get("url")
    if not url or not item.get("id"):
        return None
    fallback = item.get("url") if item.get("thumbnail") else ""
    return {
        "id": f"demo:{index:04d}",
        "openverse_id": item["id"],
        "file": f"images/{index:04d}.jpg",
        "category": category,
        "title": (item.get("title") or "")[:160],
        "creator": item.get("creator") or "",
        "license": f"{item.get('license','')} {item.get('license_version','')}".strip(),
        "source_url": item.get("foreign_landing_url") or "",
        "download_url": url,
        "fallback_url": fallback or "",
    }


def assign_episodes(records: list, episodes: list = None, seed: int = 7) -> list:
    """Give every record a date, place, device and episode.

    Records whose category belongs to no episode still get a date - real libraries
    contain stray photos, and a retrieval demo where every photo belongs to a tidy
    episode would flatter the MVP.
    """
    episodes = episodes or EPISODES
    rng = random.Random(seed)
    by_cat = {}
    for r in records:
        by_cat.setdefault(r["category"], []).append(r)
    for r in records:
        r["episode_id"] = ""
        r["episode"] = ""

    for n, (name, start, days, place, cats) in enumerate(episodes):
        begin = datetime.fromisoformat(start)
        for cat in cats:
            pool = [r for r in by_cat.get(cat, []) if not r["episode_id"]]
            for r in pool[: rng.randint(2, 5)]:
                when = begin + timedelta(days=rng.randrange(max(days, 1)),
                                         hours=rng.randrange(7, 22), minutes=rng.randrange(60))
                r.update({"episode_id": f"ep{n + 1:02d}", "episode": name, "location": place,
                          "date": when.isoformat(timespec="seconds"),
                          "device": DEVICES[n % len(DEVICES)]})

    stray = [r for r in records if not r["episode_id"]]
    for r in stray:
        when = datetime(2023, 11, 1) + timedelta(days=rng.randrange(0, 900),
                                                 hours=rng.randrange(7, 22))
        r.update({"location": rng.choice(["Bengaluru", "Chennai", "Kochi", "Mumbai"]),
                  "date": when.isoformat(timespec="seconds"),
                  "device": rng.choice(DEVICES)})
    return records


def search(query: str, want: int, session, page_size: int = MAX_PAGE_SIZE) -> list:
    """Openverse results for one query, paging until `want` is reached."""
    out, page = [], 1
    while len(out) < want and page <= MAX_PAGES:
        resp = session.get(API, headers=UA, timeout=60, params={
            "q": query, "page_size": min(page_size, MAX_PAGE_SIZE), "page": page,
            "license_type": "commercial", "mature": "false"})
        if resp.status_code == 429:
            time.sleep(10)
            continue
        if resp.status_code != 200:
            print(f"  openverse {resp.status_code} for {query!r}: {resp.text[:120]}")
            break
        results = resp.json().get("results", [])
        if not results:
            break
        out.extend(results)
        page += 1
    return out[:want]


def download(url: str, path, session, fallback: str = "") -> bool:
    """Fetch an image, falling back to the original when the thumbnail is dead.

    Openverse returns HTTP 424 from its thumbnail endpoint when the upstream
    provider image has gone. That wiped out 34 of 35 festival images on the first
    full run, silently, because only the thumbnail was ever tried.
    """
    for candidate in (url, fallback):
        if not candidate:
            continue
        try:
            resp = session.get(candidate, headers=UA, timeout=60)
        except requests.exceptions.RequestException:
            continue
        if resp.status_code == 200 and len(resp.content) >= 1000:
            path.write_bytes(resp.content)
            return True
    return False


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--limit", type=int, default=500, help="total images; use 20 for a trial")
    args = p.parse_args(argv)

    IMAGES.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    counts = quota(args.limit)
    print(f"target {args.limit} images across {len(counts)} categories")

    records, index = [], 0
    for cat, want in counts.items():
        query = CATEGORIES[cat][0]
        items = search(query, want * 2, session)   # dead upstreams are common
        kept = 0
        for item in items:
            rec = to_record(item, cat, index)
            if not rec:
                continue
            if kept >= want:
                break
            if download(rec["download_url"], IMAGES / f"{index:04d}.jpg", session, rec["fallback_url"]):
                records.append(rec)
                index += 1
                kept += 1
        print(f"  {cat:<11} {len(items):>3} found -> {kept:>3} downloaded")

    assign_episodes(records)
    LIBRARY.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
    placed = sum(1 for r in records if r["episode_id"])
    save_json(OUT_DIR / "library_stats.json", {
        "images": len(records), "in_episodes": placed, "stray": len(records) - placed,
        "episodes": len({r["episode_id"] for r in records if r["episode_id"]}),
        "by_category": {c: sum(1 for r in records if r["category"] == c) for c in counts},
    })
    print(f"\n{len(records)} images | {placed} in {len({r['episode_id'] for r in records if r['episode_id']})} episodes "
          f"| {len(records) - placed} stray")
    print(f"library: {LIBRARY}")
    if not records:
        print("NOTHING DOWNLOADED - check the messages above before rerunning.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
