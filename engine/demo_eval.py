"""Score retrieval strategies against evaluation tasks.

Supports synthetic tasks (tasks.jsonl) and real-phrasing tasks (tasks_real.jsonl),
split into dev (tune on it) and test (held-out).

Strategies:
  - baseline:       pure CLIP text-to-image similarity
  - oracle:         perfect clue->metadata window, then CLIP
  - inferred_rules: rule-based clue extractor (clues.py), then filtered CLIP
  - inferred_llm:   LLM-based clue extractor (llm_clues.py with cache), then filtered CLIP

Usage:
  .venv/bin/python -m engine.demo_eval --tasks synthetic
  .venv/bin/python -m engine.demo_eval --tasks real_dev
  .venv/bin/python -m engine.demo_eval --tasks real_test
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from engine.common import ROOT, save_json
from engine.demo_index import (
    INDEX,
    baseline_search,
    filtered_search,
    load_index,
    load_library,
    load_model,
    recall_at_k,
    soft_search,
)

TASKS_SYNTHETIC = ROOT / "data" / "eval" / "tasks.jsonl"
TASKS_REAL = ROOT / "data" / "eval" / "tasks_real.jsonl"
LLM_CACHE_FILE = ROOT / "data" / "eval" / "llm_cache.json"

REPORT_DIR = ROOT / "data" / "eval"

VAGUE_WINDOW_DAYS = 45
TODAY_STR = "2026-09-23"

# Ensure retrieval app is on sys.path
SERVICE_PATH = ROOT / "webapp" / "apps" / "retrieval"
if str(SERVICE_PATH) not in sys.path:
    sys.path.insert(0, str(SERVICE_PATH))


def filters_for(task: dict, target: dict) -> dict:
    """The metadata filter a *perfect* clue-reader would derive from the query.

    This is an upper bound, not the MVP: it assumes the system infers the window
    flawlessly. The gap between baseline and oracle is the size of the prize.
    """
    from datetime import datetime, timedelta
    f, cues, date = {}, task.get("cues_used", []), (target.get("date") or "")
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


from datetime import date

TODAY_DATE = date.fromisoformat(TODAY_STR)


def inferred_filters_for(task: dict, facets, today=TODAY_DATE) -> dict:
    """Derive filters using rule-based extractor (clues.py) from query text alone."""
    from clues import extract_clues
    if isinstance(today, str):
        today = date.fromisoformat(today)
    return extract_clues(task["query"], facets, today=today)["filters"]


def llm_filters_for(query: str, facets, cache: dict) -> dict:
    """Derive filters using LLM extractor (llm_clues.py), with local file cache."""
    if query in cache:
        return cache[query]
    from llm_clues import extract

    client = None
    if os.environ.get("GROQ_API_KEY"):
        from engine.groq import GroqClient
        client = GroqClient(
            os.environ.get("DEMO_MODEL", "openai/gpt-oss-20b"),
            daily_cap=int(os.environ.get("DEMO_TOKEN_CAP", "60000")),
        )
    res = extract(query, facets, client)
    cache[query] = res["filters"]
    return res["filters"]


def score_task(task: dict, results: list, k: int = 20) -> dict:
    answers = set(task["answer_ids"])
    ranked = [rid for rid, _ in results]
    hit_rank = next((i + 1 for i, rid in enumerate(ranked) if rid in answers), 0)
    return {
        "id": task["id"],
        "query": task["query"],
        "cues": task.get("cues_used", []),
        "phrasing_family": task.get("phrasing_family", "synthetic"),
        "n_answers": len(answers),
        "recall_at_k": round(recall_at_k(results, answers, k), 3),
        "hit_at_1": bool(ranked[:1] and ranked[0] in answers),
        "rank_of_first_hit": hit_rank,
    }


def summarise(scored: list, k: int = 20) -> dict:
    if not scored:
        return {}
    by_cue = defaultdict(list)
    by_family = defaultdict(list)
    for s in scored:
        for cue in s["cues"]:
            by_cue[cue].append(s)
        if s.get("phrasing_family"):
            by_family[s["phrasing_family"]].append(s)

    def agg(rows):
        return {
            "n": len(rows),
            f"recall_at_{k}": round(sum(r["recall_at_k"] for r in rows) / len(rows), 3),
            "hit_at_1": round(sum(r["hit_at_1"] for r in rows) / len(rows), 3),
            "found_at_all": round(sum(bool(r["rank_of_first_hit"]) for r in rows) / len(rows), 3),
        }

    return {
        "overall": agg(scored),
        "by_cue": {c: agg(rows) for c, rows in sorted(by_cue.items())},
        "by_family": {f: agg(rows) for f, rows in sorted(by_family.items())},
        "by_cue_count": {
            str(n): agg([s for s in scored if len(s["cues"]) == n])
            for n in sorted({len(s["cues"]) for s in scored})
        },
    }


def load_task_set(task_type: str) -> list[dict]:
    if task_type == "synthetic":
        if not TASKS_SYNTHETIC.exists():
            raise FileNotFoundError(f"Missing {TASKS_SYNTHETIC}")
        return [json.loads(line) for line in TASKS_SYNTHETIC.open(encoding="utf-8")]

    if not TASKS_REAL.exists():
        from engine.demo_tasks_real import main as gen_real
        gen_real()

    all_real = [json.loads(line) for line in TASKS_REAL.open(encoding="utf-8")]
    if task_type == "real_dev":
        return [t for t in all_real if t.get("split") == "dev"]
    elif task_type == "real_test":
        return [t for t in all_real if t.get("split") == "test"]
    elif task_type == "real_all":
        return all_real
    else:
        raise ValueError(f"Unknown task type: {task_type}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tasks", choices=["synthetic", "real_dev", "real_test", "real_all"], default="synthetic")
    p.add_argument("--strategy", choices=["all", "baseline", "oracle", "inferred_rules", "inferred_llm", "soft"], default="all")
    p.add_argument("--k", type=int, default=20)
    args = p.parse_args(argv)

    if not INDEX.exists():
        print("Missing index. Run engine.demo_index --build first.")
        return 1

    tasks = load_task_set(args.tasks)
    ids, matrix = load_index()
    model = load_model()

    from facets import load_facets
    library = {r["id"]: r for r in load_library()}
    records = list(library.values())
    facets = load_facets(records)

    # Load LLM cache if exists
    llm_cache = {}
    if LLM_CACHE_FILE.exists():
        try:
            llm_cache = json.loads(LLM_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            llm_cache = {}

    run_baseline = args.strategy in ("all", "baseline")
    run_oracle = args.strategy in ("all", "oracle")
    run_rules = args.strategy in ("all", "inferred_rules")
    run_llm = args.strategy in ("all", "inferred_llm")
    run_soft = args.strategy in ("all", "soft")

    scored_baseline, scored_oracle, scored_rules, scored_llm, scored_soft = [], [], [], [], []

    print(f"\n--- EVALUATION: {args.tasks.upper()} ({len(tasks)} tasks, k={args.k}) ---")

    for t in tasks:
        qv = model.encode([t["query"]])
        target = library.get(t["target_id"], {})

        if run_baseline:
            res_b = baseline_search(qv, ids, matrix, top_k=args.k)
            scored_baseline.append(score_task(t, res_b, args.k))

        if run_oracle:
            f_o = filters_for(t, target)
            res_o = filtered_search(qv, ids, matrix, records, top_k=args.k, **f_o)
            scored_oracle.append(score_task(t, res_o, args.k))

        if run_rules:
            f_r = inferred_filters_for(t, facets, today=TODAY_STR)
            res_r = filtered_search(qv, ids, matrix, records, top_k=args.k, **f_r)
            scored_rules.append(score_task(t, res_r, args.k))

        if run_llm:
            f_l = llm_filters_for(t["query"], facets, llm_cache)
            res_l = filtered_search(qv, ids, matrix, records, top_k=args.k, **f_l)
            scored_llm.append(score_task(t, res_l, args.k))

        if run_soft:
            f_s = inferred_filters_for(t, facets, today=TODAY_STR)
            res_s = soft_search(qv, ids, matrix, records, top_k=args.k, **f_s)
            scored_soft.append(score_task(t, res_s, args.k))

    # Save LLM cache if updated
    if run_llm and llm_cache:
        LLM_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        LLM_CACHE_FILE.write_text(json.dumps(llm_cache, indent=2, ensure_ascii=False), encoding="utf-8")

    def print_strategy_report(name, scored_list, filename):
        s = summarise(scored_list, args.k)
        o = s["overall"]
        print(f"\n[{name.upper()}] recall@{args.k}={o[f'recall_at_{args.k}']:.3f}  hit@1={o['hit_at_1']:.3f}  found={o['found_at_all']:.3f}")
        for cue, a in s["by_cue"].items():
            print(f"  cue: {cue:<18} n={a['n']:<2} recall@{args.k}={a[f'recall_at_{args.k}']:.3f}  hit@1={a['hit_at_1']:.3f}")
        if s.get("by_family"):
            print("  by phrasing family:")
            for fam, a in s["by_family"].items():
                print(f"    family: {fam:<18} n={a['n']:<2} recall@{args.k}={a[f'recall_at_{args.k}']:.3f}")

        save_json(REPORT_DIR / filename, {
            "strategy": name, "tasks_type": args.tasks, "k": args.k,
            "tasks_count": len(tasks), "summary": s, "tasks_detail": scored_list
        })

    if run_baseline:
        print_strategy_report("baseline", scored_baseline, f"baseline_{args.tasks}.json")
    if run_oracle:
        print_strategy_report("oracle", scored_oracle, f"oracle_{args.tasks}.json")
    if run_rules:
        print_strategy_report("inferred_rules", scored_rules, f"rules_{args.tasks}.json")
    if run_llm:
        print_strategy_report("inferred_llm", scored_llm, f"llm_{args.tasks}.json")
    if run_soft:
        print_strategy_report("soft", scored_soft, f"soft_{args.tasks}.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
