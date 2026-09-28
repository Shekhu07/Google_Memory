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
  .venv/bin/python -m engine.demo_library --grow-to 1000 # append only; never rebuild
  .venv/bin/python -m engine.demo_library --curated      # append the demo-scenario episodes
"""
import argparse
import json
import random
import re
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

# Openverse's mature filter misses some nudity. These were found by eye on 22 Sep
# (the demo is shown to graders) and removed; listed so a rebuild cannot re-fetch them.
EXCLUDED_OPENVERSE_IDS = {
    "5ec19747-3ce1-4d7e-b1fd-77ab148a2dce",   # demo:0221 "Sand and See" - nude beach
    "8748aa7f-9700-4a41-aa04-56d200869abd",   # demo:0458 - naked bike ride
    "1b872703-f831-46d4-b7f4-42beb3025473",   # demo:0924 - screenshot collage, shirtless men
    "68c06809-8c5f-4407-b92b-aca8f904bd2e",   # demo:0985 - political caricature
    "94ce74a8-5289-411c-9681-81b736feafd7",   # demo:0988 - feet-on-a-bed set
    "3e1944c3-f2df-4ceb-af13-dfeb3b14c351",   # demo:0992 - feet-on-a-bed set
    "92853806-bed1-40e2-8099-5786f03d0a6c",   # demo:0993 - feet-on-a-bed set
    "0ffcac82-8653-4b4f-bf55-512857e2e8ad",   # demo:0994 - feet-on-a-bed set
    "9643b5b6-05ab-4001-b538-d2a89e6acaaa",   # demo:0995 - feet-on-a-bed set
    "06a2d32e-643b-4332-b02f-289203fb9002",   # demo:0996 - feet-on-a-bed set
    # Curated-episode screening, 28 Sep: off-topic for the scene, or a named public figure.
    "48f06ea8-d1f3-4877-9497-267a1d113b3b",   # demo:1266 - a named governor at a commencement
    "cba29d31-e1b6-49a7-8214-54919ea966e5",   # demo:1272 - wrapped cupcakes, not a handmade cake
    "edd090cf-3dd2-4592-b228-50956aa7f0c7",   # demo:1273 - wrapped cupcakes, not a handmade cake
    "a9226e56-de0c-48cc-a781-7e38d0af36df",   # demo:1275 - a classroom, not a performance
    "2e7b34e2-1f43-44d9-b98c-9f01a6c61784",   # demo:1277 - toy figurines
    "2b712217-0b10-4502-9ea5-9a64fbc3268a",   # demo:1279 - NASA-branded event
    "67491ea6-06d6-4cf1-8f72-35dbe8d4654f",   # demo:1283 - a bicycle wheel, not a note
    "e72eca6c-5afd-4a88-9059-f7fc5fd75b34",   # demo:1286 - a doctor's waiting room
    "e285006e-c44a-43ec-8ffb-87490a3464b6",   # demo:1288 - a cropped banner
}

# Growth to 1,000 (22 Sep): the photos an ordinary person takes between the moments
# above - the sky, dinner, the commute, a screenshot. Category -> (query, count).
# They are dated as strays, never placed in episodes, and never change existing
# records: the 30 eval tasks are pinned to those records' dates.
EVERYDAY = {
    "sky":         ("sky clouds sunset", 35),
    "flower":      ("flower garden bloom", 35),
    "plant":       ("potted plant", 20),
    "home food":   ("homemade food home cooking", 40),
    "tea":         ("tea cup chai coffee mug", 25),
    "family":      ("family dinner gathering", 25),
    "friends":     ("friends group selfie", 20),
    "pet":         ("dog sleeping at home cat sofa", 25),
    "rain":        ("rain window monsoon", 25),
    "commute":     ("traffic commute bus train", 25),
    "desk":        ("office desk laptop", 25),
    "gym":         ("gym workout", 15),
    "groceries":   ("grocery vegetables market", 25),
    "shopping":    ("shopping mall clothes store", 15),
    "holi":        ("holi colours festival", 15),
    "temple":      ("temple india", 20),
    "cricket":     ("cricket match", 15),
    "notes":       ("handwritten notes notebook", 20),
    "parking":     ("car parking lot", 10),
    "product":     ("sneakers", 15),
    "screenshot":  ("screenshot", 28),
    "book":        ("book reading", 15),
    "park":        ("park playground", 15),
}

# Growth to 1,250 (22 Sep): an Indian household's library. Key -> (query, count);
# the key is also the photo's category.
INDIAN = {
    "dal":            ("dal lentil curry", 10),
    "roti":           ("roti chapati", 10),
    "biryani":        ("biryani", 10),
    "dosa":           ("dosa", 10),
    "idli":           ("idli sambar", 8),
    "thali":          ("indian thali", 10),
    "paneer":         ("paneer", 10),
    "samosa":         ("samosa", 8),
    "chaat":          ("chaat", 10),
    "paratha":        ("paratha", 8),
    "pav bhaji":      ("pav bhaji", 6),
    "poha":           ("poha", 6),
    "sweets":         ("gulab jamun", 8),
    "pressure cooker": ("pressure cooker", 6),
    "utensils":       ("steel utensils kitchen", 6),
    "rangoli":        ("rangoli", 8),
    "puja":           ("puja diya", 8),
    "matka":          ("earthen pot", 4),
    "auto rickshaw":  ("auto rickshaw", 8),
    "chai stall":     ("tea stall india", 6),
    "railway":        ("indian railway station", 6),
    "ganesh":         ("ganesh chaturthi", 6),
    "kite":           ("kite flying festival", 6),
    "mehndi":         ("mehndi henna", 6),
}

# Tourist places: key -> (query, count, city). Category "landmark", located in the
# real city, and dated as one short trip rather than scattered across the years.
LANDMARKS = {
    "taj mahal":      ("taj mahal", 6, "Agra"),
    "india gate":     ("india gate delhi", 6, "Delhi"),
    "gateway of india": ("gateway of india", 6, "Mumbai"),
    "hawa mahal":     ("hawa mahal jaipur", 6, "Jaipur"),
    "qutub minar":    ("qutub minar", 6, "Delhi"),
    "mysore palace":  ("mysore palace", 6, "Mysuru"),
    "hampi":          ("hampi", 6, "Hampi"),
    "backwaters":     ("kerala backwaters houseboat", 6, "Alleppey"),
    "varanasi":       ("varanasi ghats", 6, "Varanasi"),
    "munnar":         ("munnar tea plantation", 6, "Munnar"),
    "charminar":      ("charminar", 6, "Hyderabad"),
}


# Demo scenarios (28 Sep, fixes checklist 1.1 / 5): four moments whose photos the
# growth sets never fetched. Each is appended as its own dated episode so the demo
# tasks - "the handmade cake from my sister's graduation" and three others - have a
# real answer in the library. Name -> (start, days, place, [(category, query, n)]).
# Appended with new ids; no existing record changes, so the eval tasks stay pinned.
CURATED = {
    "sister's graduation": ("2025-06-14", 2, "Pune", [
        ("graduation", "graduation ceremony", 4),
        ("family", "graduation family", 3),
        ("cake", "graduation cake", 2),
        ("cake", "homemade cake", 2),
    ]),
    "college performance": ("2024-02-24", 1, "Chennai", [
        ("performance", "students dance performance", 4),
        ("friends", "group photo stage students", 3),
    ]),
    "old apartment": ("2024-04-27", 3, "Bengaluru", [
        ("notes", "handwritten note", 3),
        ("apartment", "empty apartment room", 3),
        ("boxes", "moving boxes apartment", 2),
    ]),
    "packing for the trip": ("2025-11-08", 1, "Bengaluru", [
        ("pet", "dog suitcase", 3),
        ("suitcase", "blue suitcase", 3),
        ("pet", "dog luggage", 2),
    ]),
}


# Chosen by eye from Openverse previews where the queries above returned weak
# matches. Episode -> [(category, openverse_id)]. The graduation cake and the dog
# in the suitcase are the answers to two demo tasks.
CURATED_PICKS = {
    "sister's graduation": [("cake", "40b98cb6-3570-43ec-a1bd-fab3b0649bff"),   # homemade cake
                            ("cake", "7507a75e-7ca1-46a6-b496-5e6526727491")],  # layer cake
    "college performance": [("performance", "48087b51-782d-499a-87c5-ddc47e37c82a"),
                            ("performance", "fd121284-4b1e-4e33-8995-a6c7ae6e5cc4")],
    "old apartment": [("notes", "2e797b86-da58-4e81-b2ca-4b0936618748"),
                      ("boxes", "d75c151d-c5ce-400f-8e56-d82266698f49")],
    "packing for the trip": [("pet", "6f2998d5-4dc0-456b-a0ac-cfc1e2612e62")],   # dog in the suitcase
}


def add_curated(session) -> int:
    """Append the CURATED episodes that are not in the library yet. Idempotent."""
    existing = [json.loads(l) for l in LIBRARY.open(encoding="utf-8")]
    have = {r.get("episode") for r in existing}
    seen = {r["openverse_id"] for r in existing} | EXCLUDED_OPENVERSE_IDS
    index = max(int(r["id"].split(":")[1]) for r in existing) + 1
    next_ep = max(int(r["episode_id"][2:]) for r in existing if r.get("episode_id")) + 1
    rng = random.Random(29)
    added = []
    ep_ids = {r["episode"]: r["episode_id"] for r in existing if r.get("episode_id")}
    for name, (start, days, place, parts) in CURATED.items():
        if name in ep_ids:
            ep_id, parts = ep_ids[name], []   # already fetched: only top up the picks
        else:
            ep_id = f"ep{next_ep:02d}"
            next_ep += 1
        begin = datetime.fromisoformat(start)
        device = DEVICES[int(ep_id[2:]) % len(DEVICES)]

        def place_it(rec, key):
            when = begin + timedelta(days=rng.randrange(max(days, 1)),
                                     hours=rng.randrange(9, 21), minutes=rng.randrange(60))
            rec.update({"episode_id": ep_id, "episode": name, "location": place,
                        "date": when.isoformat(timespec="seconds"), "device": device,
                        "batch": "curated", "batch_key": key})
            added.append(rec)

        for category, oid in CURATED_PICKS.get(name, []):
            if oid in seen:
                continue
            resp = session.get(f"{API}{oid}/", headers=UA, timeout=60)
            rec = to_record(resp.json(), category, index) if resp.status_code == 200 else None
            if rec and download(rec["download_url"], IMAGES / f"{index:04d}.jpg", session, rec["fallback_url"]):
                seen.add(oid)
                place_it(rec, "pick")
                index += 1
                print(f"  {name:<22} {category:<11} pick {oid[:8]}")
        for category, query, want in parts:
            kept = 0
            for item in search(query, want * 4, session):
                if kept >= want:
                    break
                rec = to_record(item, category, index)
                if (not rec or rec["openverse_id"] in seen or not acceptable_title(rec["title"])
                        or rec["creator"] in EXCLUDED_CREATORS):
                    continue
                if download(rec["download_url"], IMAGES / f"{index:04d}.jpg", session, rec["fallback_url"]):
                    seen.add(rec["openverse_id"])
                    place_it(rec, query)
                    index += 1
                    kept += 1
            print(f"  {name:<22} {category:<11} {kept}/{want}")
    with LIBRARY.open("a", encoding="utf-8") as fh:
        for r in added:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nappended {len(added)} -> {len(existing) + len(added)} images. "
          "Screen them by eye before indexing.")
    return 0


def growth_plan() -> dict:
    """Every growth key -> (query, target count, category, pinned city or '')."""
    plan = {k: (q, n, k, "") for k, (q, n) in {**EVERYDAY, **INDIAN}.items()}
    plan.update({k: (q, n, "landmark", city) for k, (q, n, city) in LANDMARKS.items()})
    return plan


# Titles are shown on /attribution and read aloud as alt text. Openverse's mature
# filter let "Sex to Street" and "#fuckfinance" through, so filter here as well.
BLOCKED_TITLE_WORDS = re.compile(
    r"\b(sex\w*|nude|nudity|naked|nsfw|porn\w*|fuck\w*|shit\w*|pussy|dick|cock|boobs?|"
    r"tits?|topless|erotic|bikini|lingerie|retard\w*|slave\w*|enslaved|drugs?|cocaine|weed)\b",
    re.I)

# Whole photostreams to skip: one uploader's "my girl wearing sneakers" set kept
# returning under new titles after its first six shots were blocklisted.
EXCLUDED_CREATORS = {"Tnisamante"}

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
    if not url or not item.get("id") or item["id"] in EXCLUDED_OPENVERSE_IDS:
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


def everyday_quota(total: int) -> dict:
    """Scale EVERYDAY's counts to `total`, keeping every category."""
    base = sum(n for _, n in EVERYDAY.values())
    counts = {c: max(1, round(total * n / base)) for c, (_, n) in EVERYDAY.items()}
    drift = total - sum(counts.values())
    if drift:
        biggest = max(counts, key=lambda c: counts[c])
        counts[biggest] = max(1, counts[biggest] + drift)
    return counts


def acceptable_title(title: str) -> bool:
    return not BLOCKED_TITLE_WORDS.search(title or "")


def date_everyday(records: list, seed: int = 23) -> list:
    """Date new everyday photos as strays across the library's span.

    Mostly at home in Bengaluru, as a phone library would be. Only the records
    passed in are touched.
    """
    rng = random.Random(seed)
    trips = {}
    for r in records:
        key = r.get("batch_key", "")
        if key in LANDMARKS:
            if key not in trips:
                trips[key] = datetime(2023, 11, 1) + timedelta(days=rng.randrange(0, 938))
            when = trips[key] + timedelta(days=rng.randrange(3), hours=rng.randrange(7, 20),
                                          minutes=rng.randrange(60))
            r.update({"episode_id": "", "episode": "", "location": LANDMARKS[key][2],
                      "date": when.isoformat(timespec="seconds"), "device": rng.choice(DEVICES)})
            continue
        when = datetime(2023, 11, 1) + timedelta(days=rng.randrange(0, 942),
                                                 hours=rng.randrange(7, 23), minutes=rng.randrange(60))
        r.update({"episode_id": "", "episode": "",
                  "location": rng.choice(["Bengaluru"] * 6 + ["Chennai", "Kochi", "Mumbai", "Hyderabad"]),
                  "date": when.isoformat(timespec="seconds"),
                  "device": rng.choice(DEVICES)})
    return records


def grow(target: int, session) -> int:
    """Append everyday photos until the library holds `target` images."""
    existing = [json.loads(l) for l in LIBRARY.open(encoding="utf-8")]
    need = target - len(existing)
    if need <= 0:
        print(f"library already has {len(existing)} images")
        return 0
    seen = {r["openverse_id"] for r in existing} | EXCLUDED_OPENVERSE_IDS
    index = max(int(r["id"].split(":")[1]) for r in existing) + 1
    plan = growth_plan()
    grown = {}
    for r in existing:
        if r.get("batch") == "everyday":
            key = r.get("batch_key", r["category"])
            grown[key] = grown.get(key, 0) + 1
    deficit = {k: n - grown.get(k, 0) for k, (_, n, _, _) in plan.items() if n > grown.get(k, 0)}
    if sum(deficit.values()) != need:
        print(f"note: the plan's shortfall is {sum(deficit.values())}, not {need}; fetching the shortfall")
    counts = deficit
    print(f"adding {sum(counts.values())} images across {len(counts)} categories")
    added = []
    for cat, want in counts.items():
        query, _, category, _ = plan[cat]
        items = search(query, want * 3 + 2 * grown.get(cat, 0), session)
        kept = 0
        for item in items:
            if kept >= want:
                break
            rec = to_record(item, category, index)
            if (not rec or rec["openverse_id"] in seen or not acceptable_title(rec["title"])
                    or rec["creator"] in EXCLUDED_CREATORS):
                continue
            if download(rec["download_url"], IMAGES / f"{index:04d}.jpg", session, rec["fallback_url"]):
                seen.add(rec["openverse_id"])
                rec["batch_key"] = cat
                added.append(rec)
                index += 1
                kept += 1
        print(f"  {cat:<11} {len(items):>3} found -> {kept:>3}/{want} downloaded")
    date_everyday(added, seed=23 + len(existing))
    for r in added:
        r["batch"] = "everyday"
    with LIBRARY.open("a", encoding="utf-8") as fh:
        for r in added:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nappended {len(added)} -> {len(existing) + len(added)} images. "
          "Screen them by eye before indexing.")
    return 0


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


def _is_raster(data: bytes) -> bool:
    """True for a decodable bitmap. Some Openverse 'images' are SVG documents."""
    import io
    from PIL import Image
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.verify()
        return True
    except Exception:
        return False


MAX_SIDE = 800   # a dead thumbnail falls back to the original, once 15.8 MB


def shrink(path, max_side: int = MAX_SIDE) -> bool:
    """Downscale an oversized image in place. CLIP sees 224px; the grid far less."""
    from PIL import Image
    with Image.open(path) as im:
        if max(im.size) <= max_side:
            return False
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side))
        im.save(path, "JPEG", quality=85)
    return True


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
        if resp.status_code == 200 and len(resp.content) >= 1000 and _is_raster(resp.content):
            path.write_bytes(resp.content)
            shrink(path)
            return True
    return False


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--limit", type=int, default=500, help="total images; use 20 for a trial")
    p.add_argument("--grow-to", type=int, default=0,
                   help="append everyday photos up to this total, leaving existing records untouched")
    p.add_argument("--curated", action="store_true",
                   help="append the CURATED demo-scenario episodes, leaving existing records untouched")
    args = p.parse_args(argv)
    if args.curated:
        IMAGES.mkdir(parents=True, exist_ok=True)
        return add_curated(requests.Session())
    if args.grow_to:
        IMAGES.mkdir(parents=True, exist_ok=True)
        return grow(args.grow_to, requests.Session())

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
