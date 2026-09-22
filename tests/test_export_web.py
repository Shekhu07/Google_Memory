import json

from engine.export_web import build_evidence, build_gallery, month_label, rewrite_file_paths

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


# --- the gallery shell's grid --------------------------------------------------

GALLERY = [
    {"file": "library/0001.jpg", "title": "old", "date": "2024-02-21T14:37:00"},
    {"file": "library/0002.jpg", "title": "newest", "date": "2026-05-15T14:29:00"},
    {"file": "library/0003.jpg", "title": "same month as newest", "date": "2026-05-02T09:00:00"},
]


def test_month_label_does_not_depend_on_locale():
    assert month_label("2025-12") == "December 2025"
    assert month_label("2026-01") == "January 2026"


def test_gallery_is_newest_first():
    sections = build_gallery(GALLERY)["sections"]
    assert [s["month"] for s in sections] == ["2026-05", "2024-02"]


def test_photos_in_the_same_month_share_one_section():
    sections = build_gallery(GALLERY)["sections"]
    assert [p["t"] for p in sections[0]["photos"]] == ["newest", "same month as newest"]


def test_every_record_lands_in_exactly_one_section():
    """A photo dropped by the grouping is a photo missing from the library the
    shell claims to show."""
    out = build_gallery(GALLERY)
    assert sum(len(s["photos"]) for s in out["sections"]) == len(GALLERY) == out["count"]


def test_gallery_carries_the_servable_path_not_the_source_path():
    assert build_gallery(GALLERY)["sections"][0]["photos"][0]["f"] == "library/0002.jpg"


def test_gallery_is_serialisable():
    json.dumps(build_gallery(GALLERY))


def test_a_record_with_no_date_does_not_kill_the_whole_export():
    """export() copies 494 images before it reaches build_gallery. A single
    dateless record must not take the run down after that work is done."""
    out = build_gallery([{"file": "library/1.jpg", "title": "x", "date": None}])
    assert out["sections"][0]["label"] == "Undated"
    assert out["count"] == 1


def test_undated_records_sort_last():
    rows = [{"file": "a.jpg", "title": "a", "date": None},
            {"file": "b.jpg", "title": "b", "date": "2025-03-01T00:00:00"}]
    labels = [s["label"] for s in build_gallery(rows)["sections"]]
    assert labels == ["March 2025", "Undated"]


def test_empty_library_does_not_explode():
    assert build_gallery([]) == {"count": 0, "built": build_gallery([])["built"], "sections": []}


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


def test_gallery_photos_carry_what_the_viewer_and_search_page_show():
    """The viewer's info panel and the Places/Things page read these; a missing
    field shows as a blank line to a grader."""
    rec = {"id": "demo:0007", "file": "library/0007.jpg", "title": "Chai", "date": "2025-06-14T19:42:00",
           "location": "Bengaluru", "device": "Pixel 7", "category": "tea",
           "creator": "someone", "license": "by 2.0", "w": 640, "h": 480, "episode": "goa trip"}
    p = build_gallery([rec])["sections"][0]["photos"][0]
    assert p == {"f": "library/0007.jpg", "t": "Chai", "i": "demo:0007", "d": "2025-06-14T19:42:00",
                 "p": "Bengaluru", "v": "Pixel 7", "c": "tea", "a": "someone", "l": "by 2.0",
                 "w": 640, "h": 480, "e": "goa trip"}


def test_gallery_falls_back_to_square_when_size_is_unknown():
    """The justified grid divides by height; a missing size must not become 0."""
    p = build_gallery([{"file": "library/1.jpg", "title": "x", "date": "2025-01-01T10:00:00"}])["sections"][0]["photos"][0]
    assert (p["w"], p["h"]) == (1, 1)


def test_image_sizes_are_read_from_the_files(tmp_path):
    from PIL import Image
    from engine.export_web import image_sizes
    Image.new("RGB", (300, 200)).save(tmp_path / "0001.jpg")
    assert image_sizes([{"file": "images/0001.jpg"}], tmp_path) == [{"file": "images/0001.jpg", "w": 300, "h": 200}]
