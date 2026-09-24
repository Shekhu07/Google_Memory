"""Build every artifact the Vercel app serves. Runs locally; output is committed.

Vercel never runs this. Its build installs only fastapi, numpy, onnxruntime -
no torch, no Groq calls, no model downloads. Every heavy step happens here.
"""
import json
import re
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


SOURCE_NAMES = {"playstore": "Play Store", "appstore": "App Store", "reddit": "Reddit", "youtube": "YouTube"}
OLD_PHOTO = r"\bold\b|years? ago|\b20(?:0|1)\d\b|years back"


def _is_brief(e: dict) -> bool:
    """The brief's population: remembers something (a retained cue) and has lost something."""
    return bool(e.get("cues_retained")) and bool(e.get("cues_lost"))


def _quote_pool(pool: list, allow_path_changed: bool = False) -> list:
    """Quote selection rule, applied everywhere a quote is shown.

    Only verified quotes (the span exists in the source text), only failures (not a
    success, not stage 'none'), and no app-update path complaints unless that is the
    area being illustrated. Brief-population attempts first, then not-found outcomes,
    then extraction confidence.
    """
    def ok(e):
        if not e.get("evidence") or e.get("evidence_verified") is False:
            return False
        if e.get("outcome") == "found_fast" or e.get("failure_stage") == "none":
            return False
        if e.get("failure_stage") == "browse_path_changed" and not allow_path_changed:
            return False
        return True
    keep = [e for e in pool if ok(e)]
    keep.sort(key=lambda e: (not _is_brief(e), e.get("outcome") != "not_found", -(e.get("confidence") or 0)))
    return keep


def _pick_quotes(pool: list, k: int = 3, allow_path_changed: bool = False) -> list:
    return [e["evidence"] for e in _quote_pool(pool, allow_path_changed)[:k]]


def _headline_numbers(pool: list, verbatims: list) -> dict:
    n = len(pool)
    kept = Counter(c for e in pool for c in e.get("cues_retained", []))
    lost = Counter(c for e in pool for c in e.get("cues_lost", []))
    assets = Counter(e.get("asset_type") for e in pool)
    no_cue = sum(1 for e in pool if not e.get("cues_retained"))
    top_cue, top_cue_n = kept.most_common(1)[0] if kept else ("-", 0)
    lost_sorted = lost.most_common()
    utility = assets.get("screenshot", 0) + assets.get("document_receipt", 0) + assets.get("medicine_label", 0)
    old = sum(1 for e in pool if re.search(OLD_PHOTO, e.get("evidence") or "", re.I))
    cue_names = {"temporal_approx": "Approximate time", "object": "An object", "exact_date": "An exact date",
                 "text_in_image": "Text inside the photo", "who_with": "Who was there",
                 "event_anchor": "An event", "own_label_or_caption": "Their own label", "place_named": "A named place"}
    q2_tail = (f"{no_cue}/{n} keep no searchable cue at all." if no_cue
               else "every attempt in this group keeps at least one cue.")
    second = f", then {lost_sorted[1][0].replace('_', ' ')} ({lost_sorted[1][1]}/{n})" if len(lost_sorted) > 1 else ""
    return {
        "q1": (f"Most complaints are about ordinary photos ({assets.get('photo', 0)}/{n}); screenshots and documents "
               f"are rare in public posts ({utility}/{n}). Only {old}/{n} texts mention the photo being old "
               f"(keyword match), so public posts can't yet say which old photos fail."),
        "q2": f"{cue_names.get(top_cue, top_cue)} is the most-kept cue ({top_cue_n}/{n}); {q2_tail}",
        "q3_lead": (f"The date is the most-lost detail ({lost.get('date', 0)}/{n}){second}."
                    if lost_sorted else "No lost cues recorded in this group."),
    }


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
        no_cue_bad = sum(1 for e in no_cue_known if e.get("outcome") in core.BAD)
        no_cue_stages = Counter(e["failure_stage"] for e in no_cue_episodes if e["failure_stage"] != "none")
        no_cue_hyps = Counter(h for e in no_cue_episodes for h in e.get("hypotheses", []))
        cues_table.append({
            "cue": "no cue retained",
            "posts": len(no_cue_episodes),
            "ended badly (of known outcomes)": core.pct(no_cue_bad, len(no_cue_known)),
            "most common failure": no_cue_stages.most_common(1)[0][0] if no_cue_stages else "—",
            "most supported hypothesis": no_cue_hyps.most_common(1)[0][0] if no_cue_hyps else "—",
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
            "quotes": _pick_quotes(matched, allow_path_changed=(oid == "O9")),
        })

    # Q3 note: highest not-found rate among the on-brief cue areas (O1-O6), known outcomes >= 5
    on_brief = []
    for o, (oid, name, _d, pred, _bf, _mvp) in zip(opportunities, definitions):
        if oid in ("O1", "O2", "O3", "O4", "O5", "O6"):
            m = [e for e in specific if pred(e)]
            known = [e for e in m if e.get("outcome") != "unknown"]
            if len(known) >= 5:
                nf = sum(1 for e in known if e.get("outcome") == "not_found")
                on_brief.append((nf / len(known), nf, len(known), name))
    if on_brief:
        _r, nf, nk, nm = max(on_brief)
        q3_note = (f"Among the cues the brief covers, {nm.lower()} has the highest not-found rate when it is "
                   f"remembered ({nf} of {nk} known outcomes; small n).")
    else:
        q3_note = ""

    # Q4: describe long queries by what the data actually says
    long_q = [v for v in verbatims if v["words"] >= 11]
    one_w = sum(1 for v in verbatims if v["words"] == 1)
    two_w = sum(1 for v in verbatims if v["words"] == 2)
    found_long = sum(1 for v in long_q if v["outcome"] in ("found_fast", "found_slow"))
    failed_long = sum(1 for v in long_q if v["stage"] not in ("none",) and v["outcome"] not in ("found_fast", "found_slow"))
    ask_long = sum(1 for v in long_q if v["search_mode"] == "ask_photos_or_ai")
    q4_headline = (f"{one_w} of {len(verbatims)} quoted queries are a single word and {two_w} are two words: people "
                   f"reduce a rich memory to one noun ('dog', 'cake', 'restaurant'). Only {len(long_q)} are full "
                   f"sentences: {found_long} found the photo, {failed_long} did not, and only {ask_long} "
                   f"{'is' if ask_long == 1 else 'are'} explicitly an Ask Photos query.")

    # Sample quotes chosen by the same rule as the opportunity table, with their real source
    def _q(e, **extra):
        return {"quote": e["evidence"], "source": SOURCE_NAMES.get(e.get("source"), e.get("source")), **extra}

    q1_pool = _quote_pool([e for e in specific if e.get("asset_type") in
                           ("screenshot", "document_receipt", "medicine_label", "video")])
    q1_pick, seen_types = [], set()
    for e in q1_pool:
        if e["asset_type"] not in seen_types:
            q1_pick.append(e)
            seen_types.add(e["asset_type"])
        if len(q1_pick) == 2:
            break
    used = {e["id"] for e in q1_pick}

    def _fresh(pool, k):
        out = [e for e in pool if e["id"] not in used][:k]
        used.update(e["id"] for e in out)
        return out

    q2_pick = _fresh(_quote_pool([e for e in specific if "temporal_approx" in e.get("cues_retained", [])
                                  or "event_anchor" in e.get("cues_retained", [])]), 2)
    q3_pick = _fresh(_quote_pool([e for e in brief_pop if e.get("cues_lost")]), 2)
    one_word_fail = [e for e in specific if e.get("query_verbatim") and len(e["query_verbatim"].split()) == 1]
    # Every full-sentence query is shown, successes and failures alike, so the panel can't cherry-pick.
    q4_pick = _fresh(_quote_pool(one_word_fail), 1) + [e for e in specific if e.get("query_verbatim")
                                                      and len(e["query_verbatim"].split()) >= 11]
    sample_quotes = {
        "q1_photos": [_q(e, type=e["asset_type"].replace("_", " ")) for e in q1_pick],
        "q2_remembered": [_q(e, cue=", ".join(e["cues_retained"])) for e in q2_pick],
        "q3_lost": [_q(e, cue="lost: " + ", ".join(e["cues_lost"])) for e in q3_pick],
        "q4_search": [_q(e, mode=f"query: \"{e['query_verbatim']}\" · {e.get('search_mode', 'not_mentioned')} · "
                                 f"{e.get('outcome', 'unknown')}") for e in q4_pick],
    }

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
        "sample_quotes": sample_quotes,
        "headlines": {
            "all_144": _headline_numbers(specific, verbatims),
            "brief_population": _headline_numbers(brief_pop, verbatims),
            "q3_note": q3_note,
            "q4": q4_headline,
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
                     "query_verbatim", "failure_stage", "workaround", "outcome", "hypotheses", "evidence",
                     "evidence_verified", "confidence")
    with (ENGINE_API / "data" / "episodes_specific.jsonl").open("w") as fh:
        for ep in specific:
            fh.write(json.dumps({k: ep.get(k) for k in public_fields}) + "\n")

    # Stop copying clues.py, facets.py, llm_clues.py, and library.jsonl to ENGINE_API.
    # Instead, copy the actual pipeline modules needed for extraction and analysis:
    engine_out = ENGINE_API / "engine"
    engine_out.mkdir(exist_ok=True)
    for mod in ("__init__.py", "common.py", "groq.py", "extract.py", "analysis.py", "gate_a.py", "gate_b.py"):
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
