"""Evaluation tasks for the MVP, with the cue mix taken from real engine episodes.

The tasks must look like what people actually remember, not what would be
convenient to search for. From the 144 specific attempts the engine extracted:

  cues retained   temporal_approx 40 · object 17 · exact_date 14 · text_in_image 12
                  who_with 10 · event_anchor 9 · own_label 7 · place_named 6
  cues lost       date 37 · album 29 · exact_words 10 · place 10 · people 9
  how many cues   1 cue: 79 · 0 cues: 47 · 2 cues: 12 · 3 cues: 6

Two things follow, and both make the evaluation harder on purpose:

  1. **Most people remember exactly one thing.** 79 of the 97 episodes with any
     cue at all had a single cue. A task set full of "the beach photo from Goa in
     December with my sister" would flatter the MVP and measure nothing.
  2. **The most common surviving cue is a vague time, and the most commonly lost
     one is the exact date.** So time-approximate single-cue tasks dominate.

Answers come from the demo library, so every task has a known correct set.

Usage:
  .venv/bin/python -m engine.demo_tasks            # writes data/eval/tasks.jsonl
  .venv/bin/python -m engine.demo_tasks --n 15     # the plan's cut-down option
"""
import argparse
import json
import random
import sys
from collections import Counter

from engine.common import ROOT, save_json
from engine.demo_library import LIBRARY

EPISODES_FILE = ROOT / "data" / "interim" / "episodes.jsonl"
OUT = ROOT / "data" / "eval" / "tasks.jsonl"

# Cues the synthetic library can actually support. who_with, own_label and
# device_or_app_source are excluded: the library has no people or user captions,
# and pretending otherwise would make the score meaningless.
SUPPORTED = ["temporal_approx", "object", "exact_date", "event_anchor", "place_named", "text_in_image"]

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
SEASONS = {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "summer",
           6: "summer", 7: "monsoon", 8: "monsoon", 9: "monsoon", 10: "autumn", 11: "autumn"}
NOUNS = {"receipt": "receipt", "medicine": "medicine strip", "whiteboard": "whiteboard",
         "document": "document", "cafe": "cafe", "beach": "beach", "mountain": "mountain",
         "wedding": "wedding", "festival": "festival lights", "pet": "dog", "food": "plate of food",
         "street": "street"}


def cue_profile(episodes: list) -> dict:
    """Observed cue weights and cue-count weights from real extracted episodes."""
    spec = [r for r in episodes if r.get("specificity") == "specific_attempt"]
    cues = Counter(c for r in spec for c in r.get("cues_retained", []) if c in SUPPORTED)
    counts = Counter(min(len([c for c in r.get("cues_retained", []) if c in SUPPORTED]), 3)
                     for r in spec)
    counts.pop(0, None)                      # a task needs at least one cue to be answerable
    return {"cue_weights": dict(cues), "count_weights": dict(counts) or {1: 1}}


def phrase(cue: str, record: dict, rng: random.Random) -> str:
    """Turn one cue into the words a person would actually type."""
    date = record.get("date") or ""
    if cue == "temporal_approx":
        if not date:
            return "a while back"
        month, year = int(date[5:7]), date[:4]
        return rng.choice([f"around {SEASONS[month]} {year}", f"sometime in {year}",
                           f"{MONTHS[month - 1]} {year}ish"])
    if cue == "exact_date":
        return f"on {date[:10]}" if date else ""
    if cue == "event_anchor":
        return f"from the {record['episode']}" if record.get("episode") else ""
    if cue == "place_named":
        return f"in {record['location']}" if record.get("location") else ""
    if cue == "object":
        return NOUNS.get(record.get("category", ""), record.get("category", ""))
    if cue == "text_in_image":
        return "with writing on it"
    return ""


def build_task(index: int, target: dict, library: list, cues: list, rng: random.Random) -> dict:
    """One task: a query built from `cues`, and every library image that satisfies it."""
    parts = [p for p in (phrase(c, target, rng) for c in cues) if p]
    if not parts:
        return None
    query = "the " + " ".join(parts) if "object" in cues else " ".join(parts)

    # The person has ONE photo in mind. Answers widen only inside a named episode,
    # where any photo from that moment plausibly satisfies the memory. For a stray
    # photo the answer is the target alone - otherwise "the beach" scores against
    # every beach in the library, which measures nothing and caps recall@20 at 0.65.
    answers = [target]
    if target.get("episode_id"):
        if "event_anchor" in cues:
            answers = [r for r in library if r.get("episode_id") == target["episode_id"]]
            if "object" in cues:
                answers = [r for r in answers if r["category"] == target["category"]]
        elif "object" in cues:
            answers = [r for r in library if r["category"] == target["category"]
                       and r.get("episode_id") == target["episode_id"]] or [target]

    return {
        "id": f"task:{index:03d}",
        "query": query.strip(),
        "answer_ids": sorted(r["id"] for r in answers),
        "cues_used": cues,
        "target_id": target["id"],
        "episode": target.get("episode", ""),
        "category": target["category"],
        "n_answers": len(answers),
    }


def allocate(n: int, count_weights: dict) -> dict:
    """How many tasks should use 1, 2 or 3 cues, matching the observed mix."""
    total = sum(count_weights.values()) or 1
    alloc = {k: int(n * w / total) for k, w in count_weights.items()}
    drift = n - sum(alloc.values())
    if drift and alloc:
        commonest = max(count_weights, key=lambda k: count_weights[k])
        alloc[commonest] += drift
    return {k: v for k, v in alloc.items() if v > 0}


def generate(library: list, profile: dict, n: int = 30, seed: int = 11) -> list:
    """Tasks whose cue-count mix matches real episodes.

    Buckets are filled to a pre-allocated quota rather than generated freely and
    de-duplicated. Free generation plus de-duplication silently drifts towards
    multi-cue tasks - they produce more distinct query strings - which would make
    the evaluation easier than the evidence says it should be.
    """
    rng = random.Random(seed)
    cue_names = list(profile["cue_weights"]) or ["object"]
    cue_w = [profile["cue_weights"][c] for c in cue_names]

    tasks, seen = [], set()
    for k, want in sorted(allocate(n, profile["count_weights"]).items()):
        made, guard = 0, 0
        while made < want and guard < want * 200:
            guard += 1
            target = rng.choice(library)
            cues = list(dict.fromkeys(rng.choices(cue_names, weights=cue_w, k=k)))
            if len(cues) != k:
                continue
            task = build_task(len(tasks), target, library, cues, rng)
            if not task or not task["query"] or task["query"] in seen:
                continue
            seen.add(task["query"])
            tasks.append(task)
            made += 1
        if made < want:
            print(f"  only {made}/{want} tasks with {k} cue(s) - library too small for more")
    return tasks


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=30)
    args = p.parse_args(argv)

    if not LIBRARY.exists():
        print("No demo library yet - run engine.demo_library first.")
        return 1
    library = [json.loads(l) for l in LIBRARY.open(encoding="utf-8")]
    episodes = [json.loads(l) for l in EPISODES_FILE.open(encoding="utf-8")] if EPISODES_FILE.exists() else []
    profile = cue_profile(episodes)
    tasks = generate(library, profile, args.n)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in tasks))
    save_json(OUT.parent / "task_profile.json",
              {**profile, "n_tasks": len(tasks), "library_size": len(library),
               "source": "cue mix sampled from engine specific_attempt episodes"})
    spread = Counter(len(t["cues_used"]) for t in tasks)
    print(f"{len(tasks)} tasks -> {OUT}")
    print(f"  cues per task: {dict(sorted(spread.items()))}")
    print(f"  answers per task: median {sorted(t['n_answers'] for t in tasks)[len(tasks)//2]}")
    for t in tasks[:5]:
        print(f"  {t['id']}  {t['query']!r}  -> {t['n_answers']} answer(s)")
    return 0 if tasks else 1


if __name__ == "__main__":
    sys.exit(main())
