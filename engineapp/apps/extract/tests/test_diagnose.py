"""Discovery engine API: the regressions found in the 23 Sep review."""
import main


def test_pipeline_extractor_imports():
    # Live bug: engine.extract imports gate_a/gate_b; missing files silently forced the rules path.
    # conftest also puts the repo root on sys.path, so check the deployed copy's files directly:
    import ast
    from pathlib import Path
    here = Path(main.__file__).resolve().parent / "engine"
    tree = ast.parse((here / "extract.py").read_text())
    needed = {n.module.split(".")[1] for n in ast.walk(tree)
              if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("engine.")}
    missing = [m for m in needed if not (here / f"{m}.py").exists()]
    assert not missing, f"deployed engine/ is missing {missing}"


def test_rules_match_whole_words_only():
    assert main.rules_profile("a picture of my kid with a cake")["asset_type"] == "photo"      # not 'id'
    assert main.rules_profile("my kids at the beach")["asset_type"] == "photo"
    assert "who_with" not in main.rules_profile("the location of that restaurant")["cues_retained"]  # not 'cat'
    assert "temporal_approx" not in main.rules_profile("Chicago trip photos")["cues_retained"]      # not 'ago'
    assert "temporal_approx" not in main.rules_profile("I may have a photo somewhere")["cues_retained"]


def test_rules_still_read_real_cues():
    p = main.rules_profile("my grandmother's birthday in Pune a few years ago")
    assert {"temporal_approx", "event_anchor", "place_named", "who_with"} <= set(p["cues_retained"])
    assert main.rules_profile("a receipt I photographed sometime last year")["asset_type"] == "document_receipt"


def test_cohort_is_close_matches_not_any_shared_cue():
    p = main.rules_profile("my grandmother's birthday in Pune a few years ago")
    cohort, rule = main.cohort_for(p, main.EPISODES)
    assert 0 < len(cohort) <= 20
    assert rule


def test_no_cues_gives_empty_cohort_with_reason():
    cohort, rule = main.cohort_for({"cues_retained": [], "asset_type": "photo"}, main.EPISODES)
    assert cohort == [] and "no remembered cue" in rule


def test_quotes_are_verified_failures_only():
    for text in ("my grandmother's birthday in Pune a few years ago", "the photo of my parking spot",
                 "that screenshot with some text I need"):
        cohort, _ = main.cohort_for(main.rules_profile(text), main.EPISODES)
        for q in main.pick_quotes(cohort):
            assert q["outcome"] != "found_fast"
            assert q["failure_stage"] not in ("none", "browse_path_changed")
            assert q["source"] in ("Play Store", "App Store", "Reddit", "YouTube")
