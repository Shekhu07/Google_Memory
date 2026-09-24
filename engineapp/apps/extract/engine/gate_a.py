"""Gate A: free keyword prefilter over every raw source.

Deliberately recall-oriented: it keeps anything that talks about searching,
failing to find, looking for or scrolling. Gate B (a model) decides relevance.
Also writes the per-source funnel counts used on the discovery-engine slide.

Usage:
  .venv/bin/python -m engine.gate_a
"""
import json
import re
import sys
from collections import Counter

from engine.common import RAW_DIR, ROOT, save_json

INTERIM = ROOT / "data" / "interim"
OUT = INTERIM / "gate_a_candidates.jsonl"
FUNNEL = INTERIM / "funnel.json"
SOURCES = ["youtube_comments.jsonl", "appstore_reviews.jsonl", "playstore_reviews.jsonl",
           "reddit_posts.jsonl"]

KEYWORDS = re.compile(
    r"\b(search(es|ed|ing)?"
    r"|(can'?t|cannot|couldn'?t|unable to|trying to|hard to|impossible to|never) find"
    r"|find(ing)? (a|an|the|my|old|specific|that|this|photos?|pictures?|pics?)"
    r"|look(ing|ed)? for|locate|scroll(ing|ed)?|dig(ging)? through"
    r"|ask photos|classic search|keywords?"
    r"|dhund\w*|dhoondh\w*|nahi mil\w*|mil nahi)\b",
    re.I,
)
# Phrases that signal a concrete attempt rather than general praise; used to order Gate B.
STRONG = re.compile(
    r"(can'?t|cannot|couldn'?t|unable to|trying to|impossible to) find|looking for|scroll(ing|ed)? (through|for|back)"
    r"|search(ed|ing)? for|where (is|are|did)|nahi mil|dhund",
    re.I,
)


def priority(text: str) -> int:
    """Higher = more likely a concrete retrieval episode; Gate B reads these first."""
    words = len(text.split())
    return 3 * len(STRONG.findall(text)) + min(words, 120) // 20


def main() -> int:
    seen, kept, out = Counter(), Counter(), []
    for name in SOURCES:
        path = RAW_DIR / name
        if not path.exists():
            continue
        for line in path.open():
            rec = json.loads(line)
            seen[rec["source"]] += 1
            if KEYWORDS.search(rec["text"]):
                kept[rec["source"]] += 1
                out.append({"id": rec["id"], "source": rec["source"], "date": rec["date"], "era": rec["era"],
                            "text": rec["text"], "context_title": rec.get("context_title", ""),
                            "priority": priority(rec["text"])})
    out.sort(key=lambda r: -r["priority"])
    INTERIM.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    funnel = {s: {"collected": seen[s], "gate_a": kept[s]} for s in seen}
    save_json(FUNNEL, {**({} if not FUNNEL.exists() else json.loads(FUNNEL.read_text())), "gate_a": funnel})
    for s in seen:
        print(f"{s:<10} {seen[s]:>7} collected -> {kept[s]:>5} candidates ({kept[s] / seen[s]:.1%})")
    print(f"total      {sum(seen.values()):>7} collected -> {len(out):>5} candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
