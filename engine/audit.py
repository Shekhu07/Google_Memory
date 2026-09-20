"""Audit: a second model, blind to the first model's output, re-extracts a
stratified sample; we measure agreement and whether the hypothesis ranking holds.

- Model: qwen/qwen3.8-27b (different family from gpt-oss). If Groq has removed
  it, falls back to openai/gpt-oss-20b and marks the audit "same_family".
- Prompt: written independently of engine.extract (question-by-question
  wording, no shared examples) but with the same closed vocabularies, so
  answers are comparable. Output goes through the same validator.
- Sample: round-robin across (source, era, specificity) strata.

Outputs:
  data/interim/audit_labels.jsonl      second-model extractions (resumable)
  data/processed/audit_report.json     agreement + both rankings + verdict

Usage:
  .venv/bin/python -m engine.audit                 # sample 150, label, report
  .venv/bin/python -m engine.audit --report-only
"""
import argparse
import json
import math
import sys
from collections import defaultdict

from engine.analysis import HYPOTHESES, cohen_kappa, jaccard, rank_hypotheses
from engine.common import ROOT, append_jsonl, load_ids, save_json
from engine.extract import OUT as EPISODES, VOCAB, format_batch, validate
from engine.gate_a import OUT as CANDIDATES
from engine.groq import DailyBudgetReached, GroqClient, split_on_json_failure

# Qwen enforces an output-tokens-per-minute (OTPM) ceiling of 1,000 that is not
# exposed in any response header. A request whose *expected* output exceeds it is
# rejected outright, so the audit asks for one post at a time with a small output
# budget. That caps throughput at roughly 2-3 posts a minute; a 150-post audit
# therefore takes about an hour. Measured Sep 19 (see tests/test_gates.py).
MAX_TOKENS = 800
DEFAULT_BATCH = 1

PRIMARY_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODEL = "openai/gpt-oss-20b"
OUT = ROOT / "data" / "interim" / "audit_labels.jsonl"
REPORT = ROOT / "data" / "processed" / "audit_report.json"

SINGLE_FIELDS = ["specificity", "asset_type", "failure_stage", "workaround", "outcome", "query_language", "search_mode"]
LIST_FIELDS = ["cues_retained", "cues_lost", "hypotheses"]

SYSTEM = f"""Research assistant task. Each input is a public comment or app review in which someone talks about locating pictures in a photo library app. Answer a fixed set of questions about each one, strictly from what the writer says.

Answer with the exact option strings given. If the writer doesn't say, pick the "unknown" / "none" / "none_mentioned" / "not_mentioned" / "no_query" option or an empty list.

Q1 specificity - Is the writer telling us about one particular thing they tried to locate ("specific_attempt"), or commenting on searching/finding in general ("general_complaint")?
Q2 asset_type - What were they after? {VOCAB["asset_type"]}
Q3 cues_retained - What did they know or search by? Any of {VOCAB["cues_retained"]}.
   (event_anchor = linked to something that happened in their life; temporal_approx = only a rough time; text_in_image = words visible in the picture; sequence = before/after another moment; own_label_or_caption = names or captions they had added.)
Q4 cues_lost - What do they say they didn't know? Any of {VOCAB["cues_lost"]}.
Q5 query_verbatim - Words they typed into search, only if stated. Otherwise "". Also fill Q3 for general comments when they say what they search by (a word they type, a person's name).
Q6 failure_stage - The first point where things went wrong: {VOCAB["failure_stage"]}.
   (cannot_express: unsure how to ask; system_misunderstood: search ran but returned the wrong things or nothing; not_surfaced: the item never shows up anywhere; cannot_evaluate_results: too many or too similar results to spot it; cannot_refine: no way to narrow down after a miss; browse_path_changed: an update moved or removed the route they used to get there; slow_or_broken_ui: lag, crash, results won't scroll; abandoned: gave up, stage unclear.)
Q7 workaround - What did they do instead? {VOCAB["workaround"]}
Q8 outcome - Did they get it? {VOCAB["outcome"]}. Only if the text says so; a general comment about search almost always gets "unknown".
Q9 query_language - Language of the typed search: {VOCAB["query_language"]}. If no typed words are given, "no_query".
Q10 search_mode - Which search do they refer to? {VOCAB["search_mode"]}. "ask_photos_or_ai" needs a mention of AI/Ask Photos/Gemini; "classic" needs an explicit reference to the old or classic search.
Q11 hypotheses - Which statements does this text directly support? Zero or more:
   H1: the key thing they remember is when it happened relative to their life, and search couldn't use that.
   H2: they had results in front of them but couldn't tell which one was the target.
   H3: they actually hit zero or useless results and had nowhere to go next. "Search has got worse" on its own is not H3.
   H4: their search was in a non-English or mixed language and was misread. Never for an English search.
   H5: it was a receipt/document/medicine/screenshot with nothing searchable about it.
   H6: a route they relied on to reach photos was moved or removed by an update.
Q12 evidence - One continuous quote from the text (no ellipsis, max 25 words) that best supports your answers.
Q13 confidence - 0 to 1.

Output JSON only: {{"results": [{{"id": ..., "specificity": ..., "asset_type": ..., "cues_retained": [...], "cues_lost": [...], "query_verbatim": ..., "failure_stage": ..., "workaround": ..., "outcome": ..., "query_language": ..., "search_mode": ..., "hypotheses": [...], "evidence": ..., "confidence": ...}}]}}"""


def select_sample(episodes: list, size: int) -> list:
    strata = defaultdict(list)
    for e in episodes:
        strata[(e["source"], e["era"], e["specificity"])].append(e)
    queues = [strata[k] for k in sorted(strata)]
    picked, i = [], 0
    while len(picked) < size and any(queues):
        q = queues[i % len(queues)]
        if q:
            picked.append(q.pop(0))
        i += 1
    return picked


def pick_client() -> tuple:
    """Qwen if Groq still serves it; otherwise the same-family fallback."""
    client = GroqClient(PRIMARY_MODEL)
    try:
        resp = client.session.get("https://api.groq.com/openai/v1/models",
                                  headers={"Authorization": f"Bearer {client.key}"}, timeout=30)
        ids = {m["id"] for m in resp.json().get("data", [])}
    except Exception:
        ids = {PRIMARY_MODEL}
    if PRIMARY_MODEL in ids:
        return client, "cross_family"
    print(f"{PRIMARY_MODEL} unavailable; falling back to {FALLBACK_MODEL} (same family as extraction)")
    return GroqClient(FALLBACK_MODEL), "same_family"


def agreement(pairs: list) -> dict:
    """pairs: list of (primary, audit) records for the same post."""
    out = {"n": len(pairs), "fields": {}, "hypotheses": {}}
    for f in SINGLE_FIELDS:
        a, b = [p[f] for p, _ in pairs], [q[f] for _, q in pairs]
        k = cohen_kappa(a, b)
        out["fields"][f] = {"agreement": round(sum(x == y for x, y in zip(a, b)) / len(pairs), 3),
                            "kappa": None if math.isnan(k) else round(k, 3)}
    for f in LIST_FIELDS:
        out["fields"][f] = {"mean_jaccard": round(sum(jaccard(p[f], q[f]) for p, q in pairs) / len(pairs), 3)}
    for h in HYPOTHESES:
        a, b = [h in p["hypotheses"] for p, _ in pairs], [h in q["hypotheses"] for _, q in pairs]
        k = cohen_kappa(a, b)
        out["hypotheses"][h] = {"primary_tagged": sum(a), "audit_tagged": sum(b),
                                "kappa": None if math.isnan(k) else round(k, 3)}
    out["evidence_verified"] = {"primary": round(sum(p["evidence_verified"] for p, _ in pairs) / len(pairs), 3),
                                "audit": round(sum(q["evidence_verified"] for _, q in pairs) / len(pairs), 3)}
    return out


def verdict(primary_rank: list, audit_rank: list) -> dict:
    """Compare top-2 by the pre-registered score. Zero scores are not a ranking."""
    top_p = [r["hypothesis"] for r in primary_rank if r["score"] > 0][:2]
    top_a = [r["hypothesis"] for r in audit_rank if r["score"] > 0][:2]
    if len(top_p) < 2 or len(top_a) < 2:
        return {"primary_top2": top_p, "audit_top2": top_a, "top2_agree": None, "lead_agrees": None,
                "status": "insufficient_data",
                "rule": "Fewer than two hypotheses have a non-zero score in at least one model."}
    return {"primary_top2": top_p, "audit_top2": top_a, "top2_agree": set(top_p) == set(top_a),
            "lead_agrees": top_p[0] == top_a[0], "status": "ok",
            "rule": "If top-2 sets differ, interviews break the tie (Plan 2, section 3)."}


def build_report(episodes_path=None, audit_path=None) -> dict:
    episodes_path, audit_path = episodes_path or EPISODES, audit_path or OUT
    primary = {json.loads(l)["id"]: json.loads(l) for l in episodes_path.open()}
    audited = [json.loads(l) for l in audit_path.open()] if audit_path.exists() else []
    pairs = [(primary[a["id"]], a) for a in audited if a["id"] in primary]
    sample_primary = [p for p, _ in pairs]
    report = {
        "audit_model": audited[0]["model"] if audited else None,
        "independence": audited[0].get("independence", "unknown") if audited else None,
        "agreement": agreement(pairs) if pairs else None,
        "ranking_on_sample": {
            "specific_attempts": {"primary": rank_hypotheses(sample_primary),
                                  "audit": rank_hypotheses([a for _, a in pairs])},
            "all_relevant_secondary": {"primary": rank_hypotheses(sample_primary, specific_only=False),
                                       "audit": rank_hypotheses([a for _, a in pairs], specific_only=False)},
        },
        "ranking_full_corpus_primary": rank_hypotheses(list(primary.values())),
    }
    spec = report["ranking_on_sample"]["specific_attempts"]
    report["verdict"] = verdict(spec["primary"], spec["audit"]) if pairs else None
    return report


def print_summary(report: dict) -> None:
    ag = report["agreement"]
    if not ag:
        print("No audited pairs yet.")
        return
    print(f"\nAudit model: {report['audit_model']} ({report['independence']}) | pairs: {ag['n']}")
    for f, v in ag["fields"].items():
        print(f"  {f:<16} " + " ".join(f"{k}={v[k]}" for k in v))
    print("  hypotheses: " + ", ".join(f"{h} k={v['kappa']} ({v['primary_tagged']}/{v['audit_tagged']})"
                                       for h, v in ag["hypotheses"].items()))
    print(f"  evidence verified: primary {ag['evidence_verified']['primary']}, audit {ag['evidence_verified']['audit']}")
    for view, ranks in report["ranking_on_sample"].items():
        for who, rows in ranks.items():
            print(f"  {view:<24} {who:<8} " + " > ".join(f"{r['hypothesis']}({r['score']})" for r in rows[:3]))
    print(f"  verdict: {report['verdict']}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--size", type=int, default=150)
    p.add_argument("--batch", type=int, default=DEFAULT_BATCH)
    p.add_argument("--report-only", action="store_true")
    args = p.parse_args(argv)

    if not EPISODES.exists():
        print("No episodes yet; run engine.extract first.")
        return 1
    client, independence = (None, "unknown") if args.report_only else pick_client()
    if client:
        episodes = [json.loads(l) for l in EPISODES.open()]
        texts = {c["id"]: c for c in (json.loads(l) for l in CANDIDATES.open())}
        sample = [texts[e["id"]] for e in select_sample(episodes, args.size) if e["id"] in texts]
        done = load_ids(OUT)
        todo = [s for s in sample if s["id"] not in done]
        print(f"audit sample {len(sample)}, {len(todo)} to label with {client.model}")

        def run(batch):
            resp = client.chat_json(SYSTEM, format_batch(batch), max_tokens=MAX_TOKENS)
            by_id = {b["id"]: b for b in batch}
            return [{**validate(item, by_id[item["id"]]), "model": client.model, "independence": independence}
                    for item in resp.get("results", []) if item.get("id") in by_id]
        try:
            for i in range(0, len(todo), args.batch):
                append_jsonl(OUT, split_on_json_failure(run, todo[i: i + args.batch], " (audit)"))
        except DailyBudgetReached as e:
            print(f"Stopped at daily token cap: {e}. Report covers what's labelled so far.")

    report = build_report()
    save_json(REPORT, report)
    print_summary(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
