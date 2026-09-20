"""Data and scoring for the Space demo, kept separate from the Gradio UI so it can be tested."""
import json
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np

from engine.analysis import HYPOTHESES, rank_hypotheses
from engine.common import era_for
from engine.extract import SYSTEM, format_batch, parse_results

DATA = Path(__file__).resolve().parent / "data"
MIN_N = 5  # below this, a percentage is shown as "too few"

HYPOTHESIS_NAMES = {
    "H1": "Episodic time: remembered by life event, search can't use it",
    "H2": "Recognition: results shown, target can't be picked out",
    "H3": "Dead end: nothing useful, no way forward",
    "H4": "Language: mixed-language query misread",
    "H5": "Nothing to index: utility photo with no searchable features",
    "H6": "Learned path broken: an update moved the route to photos (post-hoc)",
}
ERAS = ["pre_ask", "ask_launch", "hybrid", "toggle"]
ERA_NAMES = {"pre_ask": "Before Ask Photos (<Oct 2024)", "ask_launch": "Ask Photos launch (Oct 2024–Jun 2025)",
             "hybrid": "Hybrid relaunch (Jun 2025–Mar 2026)", "toggle": "Toggle (Mar 2026–)"}
BAD = {"not_found", "found_slow"}


def load_bundle(data_dir: Path = DATA) -> dict:
    episodes = [json.loads(l) for l in (data_dir / "episodes.jsonl").open()]
    vectors = np.load(data_dir / "embeddings.npy")

    def read(name, default):
        path = data_dir / name
        return json.loads(path.read_text()) if path.exists() else default

    return {"episodes": episodes, "vectors": vectors, "funnel": read("funnel.json", {}),
            "audit": read("audit_report.json", None), "manifest": read("manifest.json", {})}


def extract_memory(client, memory: str) -> dict:
    """Run the pipeline's own extraction prompt on a user's description."""
    today = date.today().isoformat()
    src = {"id": "query", "source": "demo", "date": today, "era": era_for(today), "text": memory}
    results = parse_results(client.chat_json(SYSTEM, format_batch([src]), max_tokens=4000), [src])
    if not results:
        raise ValueError("The model returned no usable extraction.")
    return results[0]


def _jaccard(a, b) -> float:
    sa, sb = set(a), set(b)
    return 0.0 if not sa and not sb else len(sa & sb) / len(sa | sb)


def similar_episodes(bundle: dict, query_vec: np.ndarray, query: dict | None, k: int = 8) -> list:
    """Blend text similarity with structured overlap; structure matters more across languages."""
    cos = bundle["vectors"] @ query_vec
    scored = []
    for i, ep in enumerate(bundle["episodes"]):
        score = float(cos[i])
        if query:
            score = 0.5 * score + 0.3 * _jaccard(query["cues_retained"], ep["cues_retained"])
            if query["asset_type"] not in ("unknown", "multiple") and query["asset_type"] == ep["asset_type"]:
                score += 0.2
        scored.append((score, ep))
    scored.sort(key=lambda t: -t[0])
    return [dict(ep, match=round(s, 3)) for s, ep in scored[:k]]


def pct(part: int, whole: int) -> str:
    return f"{part / whole:.0%}" if whole >= MIN_N else f"too few (n={whole})"


def cue_outcomes(episodes: list, cues: list) -> list:
    """For each cue the user still has: how real posts with that cue fared."""
    rows = []
    for cue in cues:
        with_cue = [e for e in episodes if cue in e["cues_retained"]]
        known = [e for e in with_cue if e["outcome"] != "unknown"]
        stages = Counter(e["failure_stage"] for e in with_cue if e["failure_stage"] != "none")
        hyps = Counter(h for e in with_cue for h in e["hypotheses"])
        rows.append({
            "cue": cue, "posts": len(with_cue),
            "ended badly (of known outcomes)": pct(sum(e["outcome"] in BAD for e in known), len(known)),
            "most common failure": stages.most_common(1)[0][0] if stages else "—",
            "most supported hypothesis": hyps.most_common(1)[0][0] if hyps else "—",
        })
    return rows


def ranking_table(episodes: list) -> list:
    specific = {r["hypothesis"]: r for r in rank_hypotheses(episodes, specific_only=True)}
    everything = {r["hypothesis"]: r for r in rank_hypotheses(episodes, specific_only=False)}
    order = [r["hypothesis"] for r in rank_hypotheses(episodes, specific_only=True)]
    return [{
        "hypothesis": f"{h}: {HYPOTHESIS_NAMES[h]}",
        "score (specific attempts, pre-registered)": specific[h]["score"],
        "share of attempts": specific[h]["share"], "of those, ended badly": specific[h]["severity"],
        "tagged / pool": f"{specific[h]['n_tagged']} / {specific[h]['n_pool']}",
        "score (all relevant posts, secondary)": everything[h]["score"],
    } for h in order]


def by_era(episodes: list, field: str, values: list, list_field: bool = False) -> list:
    """Share of posts in each era that have each value of a field."""
    rows = []
    for v in values:
        row = {field: v}
        for era in ERAS:
            pool = [e for e in episodes if e["era"] == era]
            hits = sum((v in e[field]) if list_field else (e[field] == v) for e in pool)
            row[ERA_NAMES[era]] = pct(hits, len(pool))
        rows.append(row)
    return rows


def failure_values(episodes: list) -> list:
    counts = Counter(e["failure_stage"] for e in episodes if e["failure_stage"] != "none")
    return [v for v, _ in counts.most_common()]


def cue_table(episodes: list) -> list:
    counts = Counter(c for e in episodes for c in e["cues_retained"])
    return cue_outcomes(episodes, [c for c, _ in counts.most_common()])


def funnel_rows(funnel: dict) -> list:
    rows = []
    for src, c in funnel.items():
        rows.append({"source": src, "collected": c.get("collected", 0), "keyword filter": c.get("gate_a", 0),
                     "model-screened": c.get("gate_b_labelled", 0), "relevant": c.get("gate_b_relevant", 0),
                     "extracted": c.get("extracted", 0), "specific attempts": c.get("specific_attempts", 0)})
    if rows:
        rows.append({"source": "total", **{k: sum(r[k] for r in rows) for k in rows[0] if k != "source"}})
    return rows


__all__ = ["HYPOTHESES", "HYPOTHESIS_NAMES", "load_bundle", "extract_memory", "similar_episodes", "cue_outcomes",
           "ranking_table", "by_era", "failure_values", "cue_table", "funnel_rows"]
