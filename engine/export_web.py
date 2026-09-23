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
            "a": r.get("creator", ""), "l": r.get("license", ""),
            # The justified grid lays photos out at their real aspect ratio.
            "w": r.get("w") or 1, "h": r.get("h") or 1,
            # Episodes are the library's albums ("goa trip"); strays carry "".
            "e": r.get("episode", "")})
    return {"count": len(rows), "built": date.today().isoformat(), "sections": sections}


def image_sizes(records: list, base: Path) -> list:
    """Copy of `records` with each image's pixel width and height, read from `base`."""
    from PIL import Image
    out = []
    for r in records:
        r = dict(r)
        try:
            with Image.open(base / Path(r["file"]).name) as im:
                r["w"], r["h"] = im.size
        except (OSError, KeyError):
            pass
        out.append(r)
    return out


def build_evidence(episodes: list, funnel: dict, audit) -> dict:
    """Precompute every table the /evidence tabs render, so they need no function call."""
    if str(ROOT / "space") not in sys.path:
        sys.path.insert(0, str(ROOT / "space"))
    import demo_core as core

    specific = [e for e in episodes if e.get("specificity") == "specific_attempt"]
    brief_pop = [e for e in specific if e.get("cues_retained") and e.get("cues_lost")]
    stages = Counter(e["failure_stage"] for e in specific)

    def share(counter, total):
        return [{"value": k, "count": v, "share": f"{v / total:.1%}"}
                for k, v in counter.most_common()] if total else []

    n = len(specific)

    # Cue table over the 144 specific attempts (D2: temporal_approx is 40, not 79)
    cues_table = core.cue_table(specific) if specific else []
    no_cue_episodes = [e for e in specific if not e.get("cues_retained")]
    if specific:
        no_cue_known = [e for e in no_cue_episodes if e.get("outcome") != "unknown"]
        no_cue_bad = sum(1 for e in no_cue_known if e.get("outcome") in ("not_found", "found_slow"))
        cues_table.append({
            "cue": "no cue retained",
            "posts": len(no_cue_episodes),
            "ended badly (of known outcomes)": f"{no_cue_bad / len(no_cue_known):.0%}" if no_cue_known else "—",
            "most common failure": "not_surfaced",
            "most supported hypothesis": "H3",
        })

    # Verbatims export (D4)
    verbatims = [
        {
            "query": e["query_verbatim"],
            "words": len(e["query_verbatim"].split()),
            "search_mode": e.get("search_mode", "not_mentioned"),
            "era": e.get("era", "pre_ask"),
            "stage": e.get("failure_stage", "none"),
            "outcome": e.get("outcome", "unknown"),
            "source": e.get("source", "play_store"),
            "evidence": e.get("evidence", ""),
        }
        for e in specific
        if e.get("query_verbatim")
    ]
    query_lengths = [
        {"length": "1 word", "count": sum(1 for v in verbatims if v["words"] == 1),
         "share": f"{sum(1 for v in verbatims if v['words'] == 1) / len(verbatims):.1%}" if verbatims else "0%"},
        {"length": "2 words", "count": sum(1 for v in verbatims if v["words"] == 2),
         "share": f"{sum(1 for v in verbatims if v['words'] == 2) / len(verbatims):.1%}" if verbatims else "0%"},
        {"length": "11+ words", "count": sum(1 for v in verbatims if v["words"] >= 11),
         "share": f"{sum(1 for v in verbatims if v['words'] >= 11) / len(verbatims):.1%}" if verbatims else "0%"},
    ]

    # Opportunity comparison table O1-O9 (D5)
    definitions = [
        ("O1", "Vague time", "approx time or event anchor",
         lambda e: "temporal_approx" in e.get("cues_retained", []) or "event_anchor" in e.get("cues_retained", []),
         "✅ core", "✅ vague time, ribbon, soft dates"),
        ("O2", "Text inside the photo", "text_in_image",
         lambda e: "text_in_image" in e.get("cues_retained", []),
         "✅ (exact words)", "❌ roadmap: OCR"),
        ("O3", "Object or thing", "object",
         lambda e: "object" in e.get("cues_retained", []),
         "✅ (words)", "◐ CLIP + synonyms"),
        ("O4", "People (who with)", "who_with",
         lambda e: "who_with" in e.get("cues_retained", []),
         "✅", "❌ no people data"),
        ("O5", "Own label or caption", "own_label_or_caption",
         lambda e: "own_label_or_caption" in e.get("cues_retained", []),
         "◐", "❌"),
        ("O6", "Place", "place_named or place_unnamed",
         lambda e: "place_named" in e.get("cues_retained", []) or "place_unnamed" in e.get("cues_retained", []),
         "✅", "✅ place anchors, soft place"),
        ("O7", "Exact date", "exact_date",
         lambda e: "exact_date" in e.get("cues_retained", []),
         "❌ precise description", "frozen"),
        ("O8", "No cue at all", "cannot express / no clues",
         lambda e: len(e.get("cues_retained", [])) == 0,
         "◐ can't express", "◐ anchors, ribbon (browse)"),
        ("O9", "Path changed by an app update", "browse_path_changed",
         lambda e: e.get("failure_stage") == "browse_path_changed",
         "❌ app design", "❌ out of scope"),
    ]

    opportunities = []
    for oid, name, detail, pred, brief_fit, mvp_addresses in definitions:
        matched = [e for e in specific if pred(e)]
        in_brief = [e for e in matched if e.get("cues_retained") and e.get("cues_lost")]
        known = [e for e in matched if e.get("outcome") != "unknown"]
        not_found = sum(1 for e in known if e.get("outcome") == "not_found")
        stages_m = Counter(e.get("failure_stage") for e in matched if e.get("failure_stage") != "none")
        top_stage_name, top_stage_cnt = stages_m.most_common(1)[0] if stages_m else ("—", 0)
        pre = sum(1 for e in matched if e.get("era") == "pre_ask")
        post = sum(1 for e in matched if e.get("era") != "pre_ask")
        nf_str = f"{not_found}/{len(known)}" if len(known) >= 5 else (f"too few (n = {len(known)})" if len(known) > 0 else "—")
        opportunities.append({
            "id": oid,
            "name": f"{oid} {name}",
            "description": detail,
            "attempts": len(matched),
            "in_brief_population": len(in_brief),
            "not_found_known": nf_str,
            "top_failure_stage": f"{top_stage_name} ({top_stage_cnt})",
            "pre_vs_post": f"{pre} / {post}",
            "brief_fit": brief_fit,
            "mvp_addresses": mvp_addresses,
            "quotes": [e.get("evidence", "") for e in matched if e.get("evidence")][:3],
        })

    # Findings data for the 4 core questions (D3)
    findings = {
        "all_144": {
            "n": len(specific),
            "cues_retained": share(Counter(c for e in specific for c in e.get("cues_retained", [])), n),
            "no_cue_count": len(no_cue_episodes),
            "no_cue_share": f"{len(no_cue_episodes) / n:.1%}" if n else "0%",
            "cues_lost": share(Counter(c for e in specific for c in e.get("cues_lost", [])), n),
            "asset_types": share(Counter(e.get("asset_type") for e in specific), n),
            "failure_stages": share(Counter(e.get("failure_stage") for e in specific), n),
        },
        "brief_population": {
            "n": len(brief_pop),
            "cues_retained": share(Counter(c for e in brief_pop for c in e.get("cues_retained", [])), len(brief_pop)) if brief_pop else [],
            "cues_lost": share(Counter(c for e in brief_pop for c in e.get("cues_lost", [])), len(brief_pop)) if brief_pop else [],
            "asset_types": share(Counter(e.get("asset_type") for e in brief_pop), len(brief_pop)) if brief_pop else [],
            "failure_stages": share(Counter(e.get("failure_stage") for e in brief_pop), len(brief_pop)) if brief_pop else [],
        },
        "sample_quotes": {
            "q1_photos": [
                {"quote": "they disappeared and I cannot find ONE PICURE OF ID,OUT OF AT LEAST 5", "type": "Document / ID", "source": "Play Store"},
                {"quote": "I'll take a screenshot, then look at the 'screenshot' collection and it's not there.", "type": "Screenshot", "source": "Play Store"},
            ],
            "q2_remembered": [
                {"quote": "If I'm looking for a photo, I'm looking for one I know when I took it. I've yet to get the photo I'm looking for quickly this way.", "cue": "temporal_approx", "source": "Reddit"},
                {"quote": "I was looking for a picture of a fancy armoire ... tried 'cabinet' and it brought it right up.", "cue": "object", "source": "Play Store"},
            ],
            "q3_lost": [
                {"quote": "When I search my photos for 'water rail' I get photos of trains by a river (lost place / context)", "cue": "place / context", "source": "Play Store"},
                {"quote": "I'm no longer able to access or find my people & pets folders ... where did they go & how do I get them back?", "cue": "album / folder", "source": "Play Store"},
            ],
            "q4_search": [
                {"quote": "if I search 'idea' then I need all those photos in which the word idea is present but its showing me best match and Most Recent pics", "mode": "Classic single-word query ('idea')", "source": "Play Store"},
                {"quote": "Recently I wanted to find a picture of myself and my wife sitting in front of some tulips about 5 years ago. So I just typed that description in and found it in 2 minutes.", "mode": "Ask Photos natural sentence (Success)", "source": "Play Store"},
            ],
        },
    }

    return {
        "asset_types": share(Counter(e["asset_type"] for e in specific), n),
        "cues_lost": share(Counter(c for e in specific for c in e["cues_lost"]), n),
        "search_modes": share(Counter(e["search_mode"] for e in specific), n),
        "ranking": core.ranking_table(episodes) if episodes else [],
        "failure_stages": [
            {"stage": k, "count": v, "share": round(v / len(specific), 3)}
            for k, v in stages.most_common()
        ] if specific else [],
        "cues": cues_table,
        "verbatims": verbatims,
        "query_lengths": query_lengths,
        "opportunities": opportunities,
        "findings": findings,
        "funnel": core.funnel_rows(funnel) if funnel else [],
        "audit": audit or {},
        "counts": {"episodes": len(episodes), "specific": len(specific), "brief_population": len(brief_pop)},
        "built": date.today().isoformat(),
    }


def export_engine_app(records: list, episodes: list, funnel: dict, audit) -> None:
    """Populate the Discovery Engine project from the same source as the MVP.

    It shares the evidence tables and pipeline models, without synthetic demo facets.
    """
    (ENGINE_WEB / "public" / "data").mkdir(parents=True, exist_ok=True)
    (ENGINE_API / "data").mkdir(parents=True, exist_ok=True)

    evidence_data = build_evidence(episodes, funnel, audit)
    (ENGINE_WEB / "public" / "data" / "evidence.json").write_text(
        json.dumps(evidence_data, indent=2))

    # Export specific retrieval attempts (144) with public fields only for the API
    specific = [e for e in episodes if e.get("specificity") == "specific_attempt"]
    public_fields = ("id", "source", "date", "era", "asset_type", "cues_retained", "cues_lost",
                     "query_verbatim", "failure_stage", "workaround", "outcome", "hypotheses", "evidence")
    with (ENGINE_API / "data" / "episodes_specific.jsonl").open("w") as fh:
        for ep in specific:
            fh.write(json.dumps({k: ep.get(k) for k in public_fields}) + "\n")

    # Stop copying clues.py, facets.py, llm_clues.py, and library.jsonl to ENGINE_API.
    # Instead, copy the actual pipeline modules needed for extraction and analysis:
    engine_out = ENGINE_API / "engine"
    engine_out.mkdir(exist_ok=True)
    for mod in ("__init__.py", "common.py", "groq.py", "extract.py", "analysis.py"):
        src = ROOT / "engine" / mod
        if src.exists():
            shutil.copy2(src, engine_out / mod)

    if (WEB / "app" / "components").exists():
        (ENGINE_WEB / "app" / "components").mkdir(parents=True, exist_ok=True)
        for comp in ("DataTable.tsx",):
            src = WEB / "app" / "components" / comp
            if src.exists():
                shutil.copy2(src, ENGINE_WEB / "app" / "components" / comp)

    (ENGINE_API / "data" / "manifest.json").write_text(json.dumps({
        "episodes_total": len(episodes),
        "episodes_specific": len(specific),
        "brief_population": len([e for e in specific if e.get("cues_retained") and e.get("cues_lost")]),
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
    gallery = build_gallery(image_sizes(records, DEMO / "images"))
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
