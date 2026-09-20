"""Gate B: gpt-oss-120b decides whether each Gate A candidate is relevant.

Binary by design (decided Sep 17): on a 60-item trial the two gpt-oss models agreed
on relevant/irrelevant 88% of the time but only 67% on the three-way
episode/complaint/irrelevant split, and 20b over-labelled "episode". Whether a
relevant post is a specific attempt or a general complaint is decided later,
during extraction.

Free tier (decided Sep 17): only --cap candidates are labelled, chosen by
round-robin across (source, era) strata in Gate A priority order, so small
sources and older eras aren't crowded out by recent Play Store reviews. Resumable.

Usage:
  .venv/bin/python -m engine.gate_b                  # cap 1,200, until done or daily cap
  .venv/bin/python -m engine.gate_b --cap 60
"""
import argparse
import json
import sys
from collections import Counter, defaultdict

from engine.common import ROOT, append_jsonl, load_ids
from engine.gate_a import OUT as CANDIDATES
from engine.groq import DailyBudgetReached, GroqClient, split_on_json_failure

MODEL = "openai/gpt-oss-120b"
OUT = ROOT / "data" / "interim" / "gate_b.jsonl"
LABELS = {"relevant", "irrelevant"}
MAX_CHARS = 1200  # long reviews are truncated; the retrieval story is almost always early

SYSTEM = """You screen user comments and app reviews about Google Photos (and similar photo apps) for a research study on how people try to find photos, videos and screenshots already in their own library.

Label every item with exactly one label:

"relevant" - the text is about finding, searching for, locating or browsing to photos/videos/screenshots in the person's own library. Either a specific attempt or general feedback on search/finding counts. Examples:
- "I searched for my passport photo and nothing came up"
- "Took me 20 minutes of scrolling to find the receipt from last year"
- "Search used to find text inside photos, now it returns random results"
- "The new AI search is awful, bring back the old one"
- "Can't scroll search results past the first rows"

"irrelevant" - anything else. In particular:
- finding a FEATURE, tool, button or setting (magic eraser, crop tool, backup toggle)
- data loss: photos deleted, not synced, gone after an update or account problem
- backup, storage, pricing, editing, crashes, sharing, ads, permissions, album creation mechanics
- general praise with no real content about finding ("easy to find memories, love it")
- searching the web or finding a tutorial

Hindi, Hinglish and other languages count the same as English.

Return JSON: {"results": [{"id": "<id>", "label": "relevant" or "irrelevant", "reason": "<max 10 words>"}]} with one entry per input item, same ids."""


def format_batch(batch: list) -> str:
    return json.dumps([{"id": r["id"], "text": r["text"][:MAX_CHARS]} for r in batch], ensure_ascii=False)


def parse_results(response: dict, batch: list) -> list:
    """Keep only well-formed results for ids in this batch; missing ids are retried next run."""
    by_id = {r["id"]: r for r in batch}
    out = []
    for item in response.get("results", []):
        rid, label = item.get("id"), item.get("label")
        if rid in by_id and label in LABELS:
            src = by_id.pop(rid)
            out.append({"id": rid, "source": src["source"], "era": src["era"], "label": label,
                        "reason": str(item.get("reason", ""))[:200], "model": MODEL})
    return out


def label_batch(client, batch: list) -> list:
    return split_on_json_failure(
        lambda b: parse_results(client.chat_json(SYSTEM, format_batch(b), max_tokens=4000), b), batch)


def select_sample(candidates: list, cap: int) -> list:
    """Round-robin across (source, era) strata, each stratum in its existing priority order."""
    strata = defaultdict(list)
    for c in candidates:
        strata[(c["source"], c["era"])].append(c)
    queues = [strata[k] for k in sorted(strata)]
    picked, i = [], 0
    while len(picked) < cap and any(queues):
        q = queues[i % len(queues)]
        if q:
            picked.append(q.pop(0))
        i += 1
    return picked


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--batch", type=int, default=20)
    p.add_argument("--cap", type=int, default=1200, help="max candidates to label (free-tier volume cut)")
    args = p.parse_args(argv)

    candidates = select_sample([json.loads(l) for l in CANDIDATES.open()], args.cap)
    done = load_ids(OUT)
    todo = [c for c in candidates if c["id"] not in done]
    client = GroqClient(MODEL)
    print(f"{len(done)} already labelled, {len(todo)} to go; {client.used_today()} tokens used today")

    labelled = 0
    try:
        for i in range(0, len(todo), args.batch):
            batch = todo[i: i + args.batch]
            results = label_batch(client, batch)
            append_jsonl(OUT, results)
            labelled += len(results)
            if (i // args.batch) % 10 == 0:
                print(f"  {labelled:>5} labelled this run | {client.used_today():>7} tokens today")
    except DailyBudgetReached as e:
        print(f"\nStopped at daily token cap: {e}. Rerun tomorrow to continue.")

    rows = [json.loads(l) for l in OUT.open()] if OUT.exists() else []
    print(f"\nlabelled this run: {labelled} | total: {len(rows)} | {dict(Counter(r['label'] for r in rows))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
