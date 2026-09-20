"""Build the Hugging Face Space bundle in space/ from pipeline outputs.

Ships only what the demo needs: structured episode fields, the short evidence
quote and a link to the public source (never full review text), the funnel, the
audit report and precomputed text embeddings. Vendors the engine modules the
Space imports so the Space repo is self-contained.

Usage:
  .venv/bin/python -m engine.export_space
  .venv/bin/python -m engine.export_space --episodes data/interim/episodes_trial_v2.jsonl   # UI dev fixture
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

from engine.common import RAW_DIR, ROOT, save_json
from engine.extract import OUT as EPISODES
from engine.gate_a import FUNNEL, OUT as CANDIDATES, SOURCES
from engine.gate_b import OUT as GATE_B

SPACE = ROOT / "space"
DATA = SPACE / "data"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
VENDORED = ["__init__.py", "common.py", "analysis.py", "extract.py", "gate_a.py", "gate_b.py", "groq.py"]
PUBLIC_FIELDS = ["id", "source", "era", "specificity", "asset_type", "cues_retained", "cues_lost", "query_verbatim",
                 "failure_stage", "workaround", "outcome", "query_language", "search_mode", "hypotheses",
                 "evidence", "evidence_verified", "confidence"]


def build_funnel(episodes: list) -> dict:
    funnel = json.loads(FUNNEL.read_text()) if FUNNEL.exists() else {}
    gate_b = [json.loads(l) for l in GATE_B.open()] if GATE_B.exists() else []
    by_source = {}
    for src, counts in funnel.get("gate_a", {}).items():
        by_source[src] = {
            **counts,
            "gate_b_labelled": sum(r["source"] == src for r in gate_b),
            "gate_b_relevant": sum(r["source"] == src and r["label"] == "relevant" for r in gate_b),
            "extracted": sum(e["source"] == src for e in episodes),
            "specific_attempts": sum(e["source"] == src and e["specificity"] == "specific_attempt" for e in episodes),
        }
    return by_source


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--episodes", type=Path, default=EPISODES)
    args = p.parse_args(argv)

    args.episodes = args.episodes.resolve()
    if not args.episodes.exists():
        print(f"{args.episodes} not found")
        return 1
    episodes = [json.loads(l) for l in args.episodes.open()]
    texts = {c["id"]: c for c in (json.loads(l) for l in CANDIDATES.open())}
    wanted = {e["id"] for e in episodes}
    urls = {}
    for name in SOURCES:
        path = RAW_DIR / name
        for line in (path.open() if path.exists() else []):
            rec = json.loads(line)
            if rec["id"] in wanted:
                urls[rec["id"]] = rec["url"]

    DATA.mkdir(parents=True, exist_ok=True)
    public = []
    for e in episodes:
        public.append({**{k: e.get(k) for k in PUBLIC_FIELDS},
                       "date": e["date"][:10], "url": urls.get(e["id"], "")})
    (DATA / "episodes.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in public))

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL)
    vectors = model.encode([texts.get(e["id"], {}).get("text", e["evidence"])[:1500] for e in episodes],
                           normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    np.save(DATA / "embeddings.npy", vectors.astype(np.float32))

    save_json(DATA / "funnel.json", build_funnel(episodes))
    report = ROOT / "data" / "processed" / "audit_report.json"
    if report.exists():
        shutil.copy(report, DATA / "audit_report.json")
    save_json(DATA / "manifest.json", {"episodes_file": str(args.episodes.relative_to(ROOT)),
                                        "n_episodes": len(episodes), "embed_model": EMBED_MODEL,
                                        "fixture": args.episodes != EPISODES})

    (SPACE / "engine").mkdir(exist_ok=True)
    for name in VENDORED:
        shutil.copy(ROOT / "engine" / name, SPACE / "engine" / name)
    # Ship an empty ledger: a stale one is confusing, and the Space resets it on
    # every container restart anyway (ephemeral filesystem).
    (DATA / "interim").mkdir(parents=True, exist_ok=True)
    (DATA / "interim" / "groq_usage.json").write_text("{}\n")

    print(f"space bundle: {len(public)} episodes, embeddings {vectors.shape}, "
          f"audit report {'included' if report.exists() else 'missing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
