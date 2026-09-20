from engine import extract

SRC = {"id": "playstore:1", "source": "playstore", "date": "2025-08-01T10:00:00", "era": "hybrid",
       "text": "I searched 'dawai' for the medicine strip photo from when I was sick last year.\nNothing came up, so I scrolled for ages."}


def test_validate_keeps_valid_values_and_drops_unknown_ones():
    item = {
        "id": "playstore:1", "specificity": "specific_attempt", "asset_type": "medicine_label",
        "cues_retained": ["event_anchor", "temporal_approx", "made_up_cue"], "cues_lost": ["date"],
        "query_verbatim": "dawai", "failure_stage": "system_misunderstood", "workaround": "manual_scroll",
        "outcome": "not_found", "query_language": "hinglish_code_mixed", "search_mode": "banana",
        "hypotheses": ["H1", "H5", "H9"], "evidence": "Nothing came up,  so I scrolled for ages.",
        "confidence": 1.7,
    }
    rec = extract.validate(item, SRC)
    assert rec["cues_retained"] == ["event_anchor", "temporal_approx"]
    assert rec["hypotheses"] == ["H1", "H5"]
    assert rec["search_mode"] == "not_mentioned"
    assert rec["confidence"] == 1.0
    assert rec["evidence_verified"] is True  # whitespace/case-insensitive match
    assert (rec["era"], rec["schema"]) == ("hybrid", extract.SCHEMA_VERSION)


def test_validate_flags_invented_evidence_and_bad_types():
    rec = extract.validate({"evidence": "search told me the photo was deleted", "cues_retained": "object",
                            "confidence": "high"}, SRC)
    assert rec["evidence_verified"] is False
    assert rec["cues_retained"] == []
    assert rec["confidence"] == 0.0
    assert rec["specificity"] == "general_complaint"


def test_parse_results_ignores_unknown_ids():
    out = extract.parse_results({"results": [{"id": "nope"}, {"id": "playstore:1", "outcome": "found_slow"}]}, [SRC])
    assert [(r["id"], r["outcome"]) for r in out] == [("playstore:1", "found_slow")]


def test_evidence_match_ignores_whitespace_but_not_ellipsis():
    src = {**SRC, "text": "today was his birthday & I wanted his pictures& couldn't find them"}
    ok = extract.validate({"evidence": "his pictures & couldn't find them"}, src)
    elided = extract.validate({"evidence": "today was his birthday ... couldn't find them"}, src)
    assert ok["evidence_verified"] is True
    assert elided["evidence_verified"] is False


def test_h6_and_browse_path_changed_are_valid():
    rec = extract.validate({"hypotheses": ["H6"], "failure_stage": "browse_path_changed"}, SRC)
    assert rec["hypotheses"] == ["H6"] and rec["failure_stage"] == "browse_path_changed"


def _p(i, source, done=False):
    return {"id": f"{source}:{i}", "source": source, "text": "t"}


def test_select_todo_skips_done_and_can_narrow_to_one_source():
    from engine.extract import select_todo
    posts = [_p(1, "playstore"), _p(2, "reddit"), _p(3, "playstore"), _p(4, "reddit")]
    done = {"playstore:1"}

    assert [r["id"] for r in select_todo(posts, done)] == ["reddit:2", "playstore:3", "reddit:4"]
    assert [r["id"] for r in select_todo(posts, done, source="reddit")] == ["reddit:2", "reddit:4"]
    assert [r["id"] for r in select_todo(posts, done, source="reddit", limit=1)] == ["reddit:2"]
    assert select_todo(posts, done, source="nosuch") == []
