import json

import numpy as np

import demo_core as core


def _ep(rid, cues=(), outcome="unknown", era="hybrid", asset="photo", stage="none", hyps=(), spec="specific_attempt"):
    return {"id": rid, "source": "playstore", "era": era, "specificity": spec, "asset_type": asset,
            "cues_retained": list(cues), "cues_lost": [], "failure_stage": stage, "outcome": outcome,
            "hypotheses": list(hyps), "evidence": "quote", "url": "", "date": "2025-01-01"}


def test_structure_can_outrank_raw_text_similarity():
    bundle = {"episodes": [_ep("text_twin", asset="video"), _ep("same_clues", cues=["event_anchor"], asset="medicine_label")],
              "vectors": np.array([[1.0, 0.0], [0.6, 0.8]], dtype=np.float32)}
    query = {"cues_retained": ["event_anchor"], "asset_type": "medicine_label"}
    ids = [m["id"] for m in core.similar_episodes(bundle, np.array([1.0, 0.0]), query)]
    assert ids[0] == "same_clues"
    assert [m["id"] for m in core.similar_episodes(bundle, np.array([1.0, 0.0]), None)][0] == "text_twin"


def test_small_groups_are_not_shown_as_percentages():
    eps = [_ep(str(i), cues=["event_anchor"], outcome="not_found") for i in range(3)]
    row = core.cue_outcomes(eps, ["event_anchor"])[0]
    assert row["posts"] == 3 and row["ended badly (of known outcomes)"].startswith("too few")


def test_cue_outcomes_percent_and_most_common_failure():
    eps = ([_ep(f"b{i}", cues=["text_in_image"], outcome="not_found", stage="system_misunderstood", hyps=["H3"]) for i in range(4)]
           + [_ep("g", cues=["text_in_image"], outcome="found_fast")])
    row = core.cue_outcomes(eps, ["text_in_image"])[0]
    assert row["ended badly (of known outcomes)"] == "80%"
    assert row["most common failure"] == "system_misunderstood" and row["most supported hypothesis"] == "H3"


def test_funnel_rows_add_a_total():
    rows = core.funnel_rows({"playstore": {"collected": 10, "gate_a": 2}, "appstore": {"collected": 5, "gate_a": 1}})
    assert rows[-1]["source"] == "total" and rows[-1]["collected"] == 15 and rows[-1]["keyword filter"] == 3


def test_load_bundle_reads_fixture_dir(tmp_path):
    (tmp_path / "episodes.jsonl").write_text(json.dumps(_ep("a")) + "\n")
    np.save(tmp_path / "embeddings.npy", np.zeros((1, 4), dtype=np.float32))
    b = core.load_bundle(tmp_path)
    assert len(b["episodes"]) == 1 and b["audit"] is None and b["funnel"] == {}
