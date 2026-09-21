import json

from engine.export_web import build_evidence, rewrite_file_paths

EPISODES = [{"id": "x", "era": "toggle", "specificity": "specific_attempt",
             "failure_stage": "not_surfaced", "outcome": "not_found",
             "cues_retained": ["temporal_approx"], "cues_lost": [], "hypotheses": ["H1"],
             "asset_type": "photo", "search_mode": "search", "workaround": "none"}]


def test_file_paths_are_rewritten_to_the_published_location():
    assert rewrite_file_paths([{"id": "demo:0001", "file": "images/0001.jpg"}])[0]["file"] == "library/0001.jpg"


def test_rewrite_leaves_other_fields_untouched():
    out = rewrite_file_paths([{"id": "demo:0001", "file": "images/0001.jpg", "location": "Goa"}])
    assert out[0]["location"] == "Goa"


def test_rewrite_does_not_mutate_the_input():
    recs = [{"id": "demo:0001", "file": "images/0001.jpg"}]
    rewrite_file_paths(recs)
    assert recs[0]["file"] == "images/0001.jpg"


def test_evidence_bundle_has_every_tab_key():
    ev = build_evidence(EPISODES, {}, None)
    assert set(ev) >= {"ranking", "failure_stages", "cues", "funnel", "audit", "counts"}


def test_failure_stages_carry_counts_and_denominator():
    ev = build_evidence(EPISODES, {}, None)
    assert ev["failure_stages"][0]["count"] == 1
    assert ev["counts"]["specific"] == 1


def test_evidence_json_is_serialisable():
    json.dumps(build_evidence(EPISODES, {}, None))


def test_empty_corpus_does_not_explode():
    ev = build_evidence([], {}, None)
    assert ev["counts"]["specific"] == 0


# --- the Discovery Engine is a separate deliverable ---------------------------

def test_engine_app_shares_the_extractor_rather_than_copying_it_by_hand():
    """Both deliverables run the same clue extractor. If the Discovery Engine kept
    its own copy, the two links could disagree about what the pipeline does."""
    from engine import export_web
    mvp = (export_web.RETRIEVAL / "clues.py")
    engine = (export_web.ENGINE_API / "clues.py")
    if mvp.exists() and engine.exists():
        assert mvp.read_text() == engine.read_text()


def test_engine_app_carries_no_image_or_encoder_weight():
    """It needs the facet vocabulary and the evidence tables, nothing else."""
    from engine import export_web
    data = export_web.ENGINE_API / "data"
    if data.exists():
        assert not list(data.glob("*.onnx"))
        assert not list(data.glob("index.npz"))
        assert not (export_web.ENGINE_WEB / "public" / "library").exists()
