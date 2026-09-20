import json

import pytest

from engine import analysis, audit


def _rec(rid, spec="specific_attempt", hyps=(), outcome="unknown", **kw):
    base = {"id": rid, "source": "playstore", "era": "hybrid", "specificity": spec, "asset_type": "photo",
            "failure_stage": "none", "workaround": "none_mentioned", "outcome": outcome, "query_language": "en",
            "search_mode": "not_mentioned", "cues_retained": [], "cues_lost": [], "hypotheses": list(hyps),
            "evidence_verified": True}
    return {**base, **kw}


def test_kappa_perfect_chance_and_disagreement():
    assert analysis.cohen_kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]) == 1.0
    assert analysis.cohen_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]) == pytest.approx(0.0)
    assert analysis.cohen_kappa(["a", "b"], ["b", "a"]) < 0


def test_jaccard_handles_empty_lists():
    assert analysis.jaccard([], []) == 1.0
    assert analysis.jaccard(["x", "y"], ["y"]) == 0.5


def test_rank_uses_preregistered_rule_on_specific_attempts_only():
    records = [
        _rec("1", hyps=["H1"], outcome="not_found"),
        _rec("2", hyps=["H1"], outcome="found_fast"),
        _rec("3", hyps=["H3"], outcome="not_found"),
        _rec("4", hyps=["H3"], outcome="unknown"),
        _rec("5", spec="general_complaint", hyps=["H2", "H2"], outcome="not_found"),
    ]
    rows = {r["hypothesis"]: r for r in analysis.rank_hypotheses(records)}
    assert rows["H1"]["share"] == 0.5 and rows["H1"]["severity"] == 0.5 and rows["H1"]["score"] == 0.25
    assert rows["H3"]["severity"] == 1.0 and rows["H3"]["score"] == 0.5   # unknown outcome excluded
    assert rows["H2"]["n_tagged"] == 0                                    # general complaint excluded
    assert analysis.rank_hypotheses(records)[0]["hypothesis"] == "H3"
    assert rows["H6"]["post_hoc"] is True


def test_sample_round_robins_strata():
    eps = [_rec(f"p{i}") for i in range(5)] + [_rec("g0", spec="general_complaint")] + [_rec("a0", source="appstore")]
    assert [e["id"] for e in audit.select_sample(eps, 4)] == ["a0", "g0", "p0", "p1"]


def test_verdict_and_report_from_files(tmp_path):
    primary = [_rec("1", hyps=["H1"], outcome="not_found"), _rec("2", hyps=["H3"], outcome="not_found")]
    audited = [{**_rec("1", hyps=["H1"], outcome="not_found"), "model": "qwen", "independence": "cross_family"},
               {**_rec("2", hyps=["H2"], outcome="not_found"), "model": "qwen", "independence": "cross_family"}]
    ep, au = tmp_path / "e.jsonl", tmp_path / "a.jsonl"
    ep.write_text("".join(json.dumps(r) + "\n" for r in primary))
    au.write_text("".join(json.dumps(r) + "\n" for r in audited))

    report = audit.build_report(ep, au)

    assert report["independence"] == "cross_family"
    assert report["agreement"]["n"] == 2
    assert report["agreement"]["hypotheses"]["H1"]["kappa"] == 1.0
    assert report["verdict"]["status"] == "ok"
    assert report["verdict"]["lead_agrees"] is True     # both lead with H1 (tie broken by share, then name)
    assert report["verdict"]["top2_agree"] is False     # {H1, H3} vs {H1, H2}


def test_kappa_undefined_when_nobody_uses_a_label():
    import math
    assert math.isnan(analysis.cohen_kappa([False, False], [False, False]))


def test_verdict_ignores_zero_scores():
    rank = lambda scores: [{"hypothesis": h, "score": s} for h, s in scores]
    v = audit.verdict(rank([("H6", 0.5), ("H3", 0.2), ("H1", 0)]), rank([("H6", 0.4), ("H1", 0.1), ("H2", 0)]))
    assert v["status"] == "ok" and v["lead_agrees"] is True and v["top2_agree"] is False
    assert audit.verdict(rank([("H6", 0.5), ("H1", 0)]), rank([("H6", 0.5), ("H3", 0.1)]))["status"] == "insufficient_data"
