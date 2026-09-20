"""Score a retrieval strategy against the 30 evaluation tasks.

Reports recall@k and hit@1 overall and **broken down by cue type**, because the
headline number hides the finding that matters. The engine showed the most
commonly retained cue is an approximate time (40 of 144 specific attempts) and
the most commonly lost is the exact date (37). CLIP has no concept of time, so a
pure-similarity baseline should fail precisely where real memory is strongest.

That gap is the MVP's opportunity, and this is where it gets quantified.

Usage:
  .venv/bin/python -m engine.demo_eval                 # baseline
"""
import argparse
import json
import sys
from collections import defaultdict

from engine.common import ROOT, save_json
from engine.demo_index import (INDEX, baseline_search, filtered_search, load_index,
                               load_library, load_model, recall_at_k)

TASKS = ROOT / "data" / "eval" / "tasks.jsonl"
REPORT = ROOT / "data" / "eval" / "baseline_report.json"
ORACLE_REPORT = ROOT / "data" / "eval" / "oracle_report.json"

# How wide a window a vague time cue justifies. "around winter 2024" is not a date,
# so the MVP must guess a range; 45 days either side is the plan's date-window idea.
VAGUE_WINDOW_DAYS = 45


def filters_for(task: dict, target: dict) -> dict:
    """The metadata filter a *perfect* clue-reader would derive from the query.

    This is an upper bound, not the MVP: it assumes the system infers the window
    flawlessly. The gap between baseline and oracle is the size of the prize.
    """
    from datetime import datetime, timedelta
    f, cues, date = {}, task["cues_used"], (target.get("date") or "")
    if "event_anchor" in cues and target.get("episode"):
        f["episode"] = target["episode"]
    if "place_named" in cues and target.get("location"):
        f["location"] = target["location"]
    if "object" in cues:
        f["category"] = target.get("category", "")
    if "exact_date" in cues and date:
        f["date_from"] = f["date_to"] = date[:10]
    elif "temporal_approx" in cues and date:
        when = datetime.fromisoformat(date)
        f["date_from"] = (when - timedelta(days=VAGUE_WINDOW_DAYS)).date().isoformat()
        f["date_to"] = (when + timedelta(days=VAGUE_WINDOW_DAYS)).date().isoformat()
    return f


def score_task(task: dict, results: list, k: int = 20) -> dict:
    answers = set(task["answer_ids"])
    ranked = [rid for rid, _ in results]
    hit_rank = next((i + 1 for i, rid in enumerate(ranked) if rid in answers), 0)
    return {
        "id": task["id"], "query": task["query"], "cues": task["cues_used"],
        "n_answers": len(answers),
        "recall_at_k": round(recall_at_k(results, answers, k), 3),
        "hit_at_1": bool(ranked[:1] and ranked[0] in answers),
        "rank_of_first_hit": hit_rank,          # 0 = not found in the returned list
    }


def summarise(scored: list, k: int = 20) -> dict:
    if not scored:
        return {}
    by_cue = defaultdict(list)
    for s in scored:
        for cue in s["cues"]:
            by_cue[cue].append(s)
    def agg(rows):
        return {"n": len(rows),
                f"recall_at_{k}": round(sum(r["recall_at_k"] for r in rows) / len(rows), 3),
                "hit_at_1": round(sum(r["hit_at_1"] for r in rows) / len(rows), 3),
                "found_at_all": round(sum(bool(r["rank_of_first_hit"]) for r in rows) / len(rows), 3)}
    return {"overall": agg(scored),
            "by_cue": {c: agg(rows) for c, rows in sorted(by_cue.items())},
            "by_cue_count": {str(n): agg([s for s in scored if len(s["cues"]) == n])
                             for n in sorted({len(s["cues"]) for s in scored})}}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--k", type=int, default=20)
    args = p.parse_args(argv)

    if not (TASKS.exists() and INDEX.exists()):
        print("Need both data/eval/tasks.jsonl and the CLIP index. Run demo_tasks and demo_index --build.")
        return 1
    tasks = [json.loads(l) for l in TASKS.open(encoding="utf-8")]
    ids, matrix = load_index()
    model = load_model()

    library = {r["id"]: r for r in load_library()}
    records = list(library.values())
    scored, oracle = [], []
    for t in tasks:
        qv = model.encode([t["query"]])
        scored.append(score_task(t, baseline_search(qv, ids, matrix, top_k=args.k), args.k))
        f = filters_for(t, library.get(t["target_id"], {}))
        oracle.append(score_task(t, filtered_search(qv, ids, matrix, records, top_k=args.k, **f), args.k))

    report = {"strategy": "baseline (plain CLIP similarity, no metadata)",
              "k": args.k, "library": len(ids), "tasks": len(tasks),
              "summary": summarise(scored, args.k), "tasks_detail": scored}
    save_json(REPORT, report)
    save_json(ORACLE_REPORT,
              {"strategy": "oracle (perfect clue->metadata window, then CLIP inside it)",
               "k": args.k, "library": len(ids), "tasks": len(tasks),
               "summary": summarise(oracle, args.k), "tasks_detail": oracle})

    s = report["summary"]
    print(f"BASELINE over {len(tasks)} tasks, {len(ids)} images\n")
    o = s["overall"]
    print(f"  overall   recall@{args.k}={o[f'recall_at_{args.k}']}  hit@1={o['hit_at_1']}  found_at_all={o['found_at_all']}")
    print("\n  by cue:")
    for cue, a in s["by_cue"].items():
        print(f"    {cue:<18} n={a['n']:<3} recall@{args.k}={a[f'recall_at_{args.k}']:<6} hit@1={a['hit_at_1']:<6} found={a['found_at_all']}")
    print("\n  by number of cues:")
    for n, a in s["by_cue_count"].items():
        print(f"    {n} cue(s)          n={a['n']:<3} recall@{args.k}={a[f'recall_at_{args.k}']:<6} hit@1={a['hit_at_1']}")
    osum = summarise(oracle, args.k)["overall"]
    print("\n  ORACLE (perfect clue->window, then the same CLIP):")
    print(f"    recall@{args.k}={osum[f'recall_at_{args.k}']}  hit@1={osum['hit_at_1']}  found_at_all={osum['found_at_all']}")
    lift = osum[f"recall_at_{args.k}"] - o[f"recall_at_{args.k}"]
    print(f"    lift over baseline: +{lift:.3f} recall@{args.k}  <- this is the size of the prize")
    print(f"\nreports: {REPORT}\n         {ORACLE_REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
