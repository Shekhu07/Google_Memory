"""Build every artifact the Vercel app serves. Runs locally; output is committed.

Vercel never runs this. Its build installs only fastapi, numpy, onnxruntime -
no torch, no Groq calls, no model downloads. Every heavy step happens here.
"""
import json
import shutil
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "data" / "demo"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
WEB = ROOT / "webapp" / "apps" / "web"
RETRIEVAL = ROOT / "webapp" / "apps" / "retrieval"


def rewrite_file_paths(records: list) -> list:
    """images/0001.jpg -> library/0001.jpg, so the API returns a servable path."""
    out = []
    for r in records:
        r = dict(r)
        name = Path(r.get("file", "")).name
        if name:
            r["file"] = f"library/{name}"
        out.append(r)
    return out


def build_evidence(episodes: list, funnel: dict, audit) -> dict:
    """Precompute every table the /evidence tabs render, so they need no function call."""
    if str(ROOT / "space") not in sys.path:
        sys.path.insert(0, str(ROOT / "space"))
    import demo_core as core

    specific = [e for e in episodes if e.get("specificity") == "specific_attempt"]
    stages = Counter(e["failure_stage"] for e in specific)
    return {
        "ranking": core.ranking_table(episodes) if episodes else [],
        "failure_stages": [
            {"stage": k, "count": v, "share": round(v / len(specific), 3)}
            for k, v in stages.most_common()
        ] if specific else [],
        "cues": core.cue_table(episodes) if episodes else [],
        "funnel": core.funnel_rows(funnel) if funnel else [],
        "audit": audit or {},
        "counts": {"episodes": len(episodes), "specific": len(specific)},
        "built": date.today().isoformat(),
    }


def export(root: Path = ROOT) -> dict:
    (WEB / "public" / "library").mkdir(parents=True, exist_ok=True)
    (WEB / "public" / "data").mkdir(parents=True, exist_ok=True)
    (RETRIEVAL / "data").mkdir(parents=True, exist_ok=True)

    copied = 0
    for src in sorted((DEMO / "images").glob("*.jpg")):
        shutil.copy2(src, WEB / "public" / "library" / src.name)
        copied += 1

    records = rewrite_file_paths([json.loads(l) for l in (DEMO / "library.jsonl").open()])
    with (RETRIEVAL / "data" / "library.jsonl").open("w") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    shutil.copy2(DEMO / "index.npz", RETRIEVAL / "data" / "index.npz")

    episodes = [json.loads(l) for l in (INTERIM / "episodes.jsonl").open()]
    # interim/funnel.json only holds gate_a counts, nested. export_space.build_funnel
    # joins them with gate_b labels and the extracted episodes to make the full funnel.
    from engine.export_space import build_funnel
    funnel = build_funnel(episodes)
    audit = json.loads((PROCESSED / "audit_report.json").read_text()) if (PROCESSED / "audit_report.json").exists() else None
    (WEB / "public" / "data" / "evidence.json").write_text(
        json.dumps(build_evidence(episodes, funnel, audit)))

    attribution = [{"file": r["file"], "title": r.get("title", ""),
                    "creator": r.get("creator", ""), "license": r.get("license", ""),
                    "source_url": r.get("source_url", "")} for r in records]
    (WEB / "public" / "data" / "attribution.json").write_text(json.dumps(attribution))

    engine_out = RETRIEVAL / "engine"
    engine_out.mkdir(exist_ok=True)
    for mod in ["__init__.py", "common.py", "demo_index.py", "groq.py", "analysis.py", "extract.py"]:
        src = ROOT / "engine" / mod
        if src.exists():
            shutil.copy2(src, engine_out / mod)

    manifest = {"images": len(records), "images_copied": copied, "episodes": len(episodes),
                "built": date.today().isoformat(), "clip_model": "clip-ViT-B-32",
                "encoder": "clip_text.onnx (fp16, sharded)"}
    (RETRIEVAL / "data" / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
