"""Generate cue-dropout evaluation tasks (Evaluation E1).

Directly measures retrieval success as cues drop out across 4 levels:
  - L3: vague time + exact place + library word (fully described)
  - L2: two of vague time / place / content, content paraphrased
  - L1: one vague cue + content paraphrased
  - L0: paraphrased content only, no time, no place, no library word

Rules:
  - Volume: 30 base tasks x 4 levels = 120 queries
  - No numeric dates at any level
  - Avoid category words and synonyms in L2, L1, L0
  - Labeled source: "constructed"
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_SYNTHETIC = ROOT / "data" / "eval" / "tasks.jsonl"
LIBRARY_FILE = ROOT / "webapp" / "apps" / "retrieval" / "data" / "library.jsonl"
PARAPHRASE_BANK_FILE = ROOT / "data" / "eval" / "paraphrase_bank.json"
OUT_FILE = ROOT / "data" / "eval" / "tasks_dropout.jsonl"

VAGUE_PLACES = {
    "Bengaluru": "down south in Karnataka",
    "Chennai": "along the Coromandel coast",
    "Mumbai": "over in Maharashtra",
    "Mysuru": "in southern Karnataka",
    "Goa": "that beach state",
    "Kochi": "down in Kerala",
    "Pondicherry": "on the French colonial coast",
    "Manali": "somewhere up in the hills",
    "Jaipur": "in Rajasthan",
}


def get_vague_time_l3(d_str: str) -> str:
    yr = int(d_str[:4])
    mo = int(d_str[5:7])
    if yr == 2023:
        return "winter 2023" if mo in (11, 12) else "sometime in 2023"
    elif yr == 2024:
        if mo in (5, 6):
            return "around summer 2024"
        if mo in (7, 8, 9):
            return "around monsoon 2024"
        if mo in (11, 12):
            return "winter 2024"
        return "sometime in 2024"
    elif yr == 2025:
        if mo in (5, 6):
            return "summer 2025"
        if mo in (7, 8, 9):
            return "monsoon 2025"
        return "sometime in 2025"
    else:
        return "earlier this year"


def get_vague_time_rel(d_str: str, idx: int) -> str:
    yr = int(d_str[:4])
    if yr == 2023:
        options = ["a couple of years ago", "sometime a couple of years ago", "back in 2023"]
    elif yr == 2024:
        options = ["a while back", "sometime a while back", "around 2 years ago"]
    elif yr == 2025:
        options = ["sometime last year", "around last year", "last year"]
    else:
        options = ["earlier this year", "a few months ago", "this year"]
    return options[idx % len(options)]


def render_l3_query(cat: str, loc: str, ep: str, t3: str) -> str:
    if cat in ("cafe", "beach", "mountain", "park"):
        return f"the {cat} we visited in {loc} {t3}"
    elif cat in ("food", "biryani", "dosa", "idli", "thali", "sweets"):
        return f"the {cat} we had in {loc} {t3}"
    elif cat in ("wedding", "festival"):
        return f"the {cat} celebration in {loc} {t3}"
    elif cat == "pet":
        return f"our {cat} in {loc} {t3}"
    elif cat in ("whiteboard", "document", "receipt"):
        return f"the {cat} from {loc}, {t3}"
    else:
        return f"{cat} in {loc}, {t3}"


def generate_dropout_tasks() -> list[dict]:
    synthetic = [json.loads(line) for line in TASKS_SYNTHETIC.open(encoding="utf-8") if line.strip()]
    library = {r["id"]: r for r in (json.loads(line) for line in LIBRARY_FILE.open(encoding="utf-8") if line.strip())}
    paraphrase_bank = json.loads(PARAPHRASE_BANK_FILE.read_text(encoding="utf-8"))

    tasks_dropout = []
    for i, base in enumerate(synthetic):
        target = library.get(base["target_id"], {})
        cat = target.get("category", base.get("category", "food"))
        loc = target.get("location", "Bengaluru")
        ep = target.get("episode", "")
        d_str = target.get("date", "2024-06-01")

        phrases = paraphrase_bank.get(cat, ["a memorable photo"])
        p = phrases[i % len(phrases)]

        t3 = get_vague_time_l3(d_str)
        t_rel = get_vague_time_rel(d_str, i)
        p_vague = VAGUE_PLACES.get(loc, "over in that city")

        # L3: vague time + exact place + library word
        q_l3 = render_l3_query(cat, loc, ep, t3)
        tasks_dropout.append({
            "id": f"{base['id']}_L3",
            "base_task_id": base["id"],
            "level": "L3",
            "query": q_l3,
            "target_id": base["target_id"],
            "answer_ids": base["answer_ids"],
            "n_answers": len(base["answer_ids"]),
            "cues_used": ["temporal_approx", "place_named", "object"],
            "phrasing_family": "dropout_l3",
            "source": "constructed",
            "split": "dropout",
        })

        # L2: two of vague time / place / content, content paraphrased
        q_l2 = f"{p}, {p_vague} {t_rel}"
        tasks_dropout.append({
            "id": f"{base['id']}_L2",
            "base_task_id": base["id"],
            "level": "L2",
            "query": q_l2,
            "target_id": base["target_id"],
            "answer_ids": base["answer_ids"],
            "n_answers": len(base["answer_ids"]),
            "cues_used": ["temporal_approx", "place_named"],
            "phrasing_family": "dropout_l2",
            "source": "constructed",
            "split": "dropout",
        })

        # L1: one vague cue + content paraphrased
        q_l1 = f"{p}, {t_rel}"
        tasks_dropout.append({
            "id": f"{base['id']}_L1",
            "base_task_id": base["id"],
            "level": "L1",
            "query": q_l1,
            "target_id": base["target_id"],
            "answer_ids": base["answer_ids"],
            "n_answers": len(base["answer_ids"]),
            "cues_used": ["temporal_approx"],
            "phrasing_family": "dropout_l1",
            "source": "constructed",
            "split": "dropout",
        })

        # L0: paraphrased content only, no time, no place, no library word
        q_l0 = p
        tasks_dropout.append({
            "id": f"{base['id']}_L0",
            "base_task_id": base["id"],
            "level": "L0",
            "query": q_l0,
            "target_id": base["target_id"],
            "answer_ids": base["answer_ids"],
            "n_answers": len(base["answer_ids"]),
            "cues_used": [],
            "phrasing_family": "dropout_l0",
            "source": "constructed",
            "split": "dropout",
        })

    return tasks_dropout


def main():
    tasks = generate_dropout_tasks()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    print(f"Generated {len(tasks)} cue-dropout evaluation tasks -> {OUT_FILE}")
    for lvl in ("L3", "L2", "L1", "L0"):
        cnt = sum(1 for t in tasks if t["level"] == lvl)
        print(f"  Level {lvl}: {cnt} tasks")
    for t in tasks[:8]:
        print(f"  [{t['level']}] {t['id']}: {t['query']!r}")


if __name__ == "__main__":
    main()
