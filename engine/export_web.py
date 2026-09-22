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
# The Discovery Engine is a separate deliverable and a separate deployment, but it
# is generated from this same source so its extractor cannot drift from the MVP's.
ENGINE_WEB = ROOT / "engineapp" / "apps" / "web"
ENGINE_API = ROOT / "engineapp" / "apps" / "extract"


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


MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")


def month_label(month: str) -> str:
    """'2025-12' -> 'December 2025'. Spelled out rather than strftime because the
    output is committed and must not vary with the exporting machine's locale.

    A record with no usable date groups under 'Undated' rather than raising: one
    such record would otherwise kill export() with an unpacking error, after it
    had already copied 494 images and written half the artifacts.
    """
    if not month or "-" not in month:
        return "Undated"
    y, m = month.split("-")
    return f"{MONTHS[int(m) - 1]} {y}"


def build_gallery(records: list) -> dict:
    """The shell's photo grid, newest first, grouped by month.

    Static because no endpoint lists the library without a query - /search requires
    non-empty text and caps at top_k=20 - and adding one would put a second copy of
    all 494 records inside the retrieval bundle, which is already ~126 MB of the
    225 MB Vercel limit. Sections are months; the client splits them into days, the
    way the Photos timeline reads. Each photo carries its id, date, place, device,
    category and credit for the viewer's info panel and the Places/Things page.

    Call this AFTER rewrite_file_paths, so `f` is the servable 'library/0000.jpg'.
    """
    rows = sorted(records, key=lambda r: r.get("date") or "", reverse=True)
    sections: list = []
    for r in rows:
        month = (r.get("date") or "")[:7]
        if not sections or sections[-1]["month"] != month:
            sections.append({"month": month, "label": month_label(month), "photos": []})
        sections[-1]["photos"].append({
            "f": r["file"], "t": r.get("title", ""), "i": r.get("id", ""), "d": r.get("date") or "",
            "p": r.get("location", ""), "v": r.get("device", ""), "c": r.get("category", ""),
            "a": r.get("creator", ""), "l": r.get("license", "")})
    return {"count": len(rows), "built": date.today().isoformat(), "sections": sections}


def build_evidence(episodes: list, funnel: dict, audit) -> dict:
    """Precompute every table the /evidence tabs render, so they need no function call."""
    if str(ROOT / "space") not in sys.path:
        sys.path.insert(0, str(ROOT / "space"))
    import demo_core as core

    specific = [e for e in episodes if e.get("specificity") == "specific_attempt"]
    stages = Counter(e["failure_stage"] for e in specific)

    def share(counter, total):
        return [{"value": k, "count": v, "share": f"{v / total:.1%}"}
                for k, v in counter.most_common()] if total else []

    n = len(specific)
    return {
        # The brief names four questions the discovery engine should answer. These
        # three were measured but never surfaced on the public page.
        "asset_types": share(Counter(e["asset_type"] for e in specific), n),
        "cues_lost": share(Counter(c for e in specific for c in e["cues_lost"]), n),
        "search_modes": share(Counter(e["search_mode"] for e in specific), n),
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


def export_engine_app(records: list, episodes: list, funnel: dict, audit) -> None:
    """Populate the Discovery Engine project from the same source as the MVP.

    It shares the extractor, the facet vocabulary and the evidence tables, and
    needs none of the MVP's weight: no images, no CLIP encoder, no image vectors.
    """
    (ENGINE_WEB / "public" / "data").mkdir(parents=True, exist_ok=True)
    (ENGINE_API / "data").mkdir(parents=True, exist_ok=True)

    (ENGINE_WEB / "public" / "data" / "evidence.json").write_text(
        json.dumps(build_evidence(episodes, funnel, audit)))

    # Facet vocabulary only - the extractor matches against the library's own
    # place, episode and category values, and needs nothing else from it.
    facets_only = [{k: r.get(k, "") for k in ("id", "location", "episode", "category", "date")}
                   for r in records]
    with (ENGINE_API / "data" / "library.jsonl").open("w") as fh:
        for r in facets_only:
            fh.write(json.dumps(r) + "\n")

    for mod in ("clues.py", "facets.py", "llm_clues.py"):
        shutil.copy2(RETRIEVAL / mod, ENGINE_API / mod)

    # globals.css is NOT copied: since the 22 Sep upgrade the Discovery Engine owns
    # its own stylesheet, and copying the MVP's over it deleted 744 lines of it.
    if (WEB / "app" / "components").exists():
        (ENGINE_WEB / "app" / "components").mkdir(parents=True, exist_ok=True)
        for comp in ("DataTable.tsx",):
            src = WEB / "app" / "components" / comp
            if src.exists():
                shutil.copy2(src, ENGINE_WEB / "app" / "components" / comp)

    engine_out = ENGINE_API / "engine"
    engine_out.mkdir(exist_ok=True)
    for mod in ("__init__.py", "common.py", "groq.py"):
        src = ROOT / "engine" / mod
        if src.exists():
            shutil.copy2(src, engine_out / mod)

    (ENGINE_API / "data" / "manifest.json").write_text(json.dumps({
        "episodes": len(episodes),
        "vocabulary_from": f"{len(records)} library records",
        "built": date.today().isoformat(),
        "service": "discovery-engine",
    }, indent=2))


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

    # The gallery shell's grid. WEB only - the Discovery Engine ships no image weight.
    gallery = build_gallery(records)
    (WEB / "public" / "data" / "gallery.json").write_text(json.dumps(gallery))

    engine_out = RETRIEVAL / "engine"
    engine_out.mkdir(exist_ok=True)
    for mod in ["__init__.py", "common.py", "demo_index.py", "groq.py", "analysis.py", "extract.py"]:
        src = ROOT / "engine" / mod
        if src.exists():
            shutil.copy2(src, engine_out / mod)

    export_engine_app(records, episodes, funnel, audit)

    manifest = {"images": len(records), "images_copied": copied, "episodes": len(episodes),
                "gallery_sections": len(gallery["sections"]),
                "built": date.today().isoformat(), "clip_model": "clip-ViT-B-32",
                "encoder": "clip_text.onnx (fp16, sharded)"}
    (RETRIEVAL / "data" / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    print(json.dumps(export(), indent=2))
