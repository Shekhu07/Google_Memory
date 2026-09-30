import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_reports_readiness():
    body = client.get("/health").json()
    assert body["images"] == 1282
    assert "encoder" in body


def test_facets_endpoint_returns_library_anchors():
    res = client.get("/facets")
    assert res.status_code == 200
    data = res.json()
    assert "locations" in data and len(data["locations"]) > 0
    assert "categories" in data and len(data["categories"]) > 0
    assert "top_anchors" in data
    assert len(data["top_anchors"]) >= 3
    for a in data["top_anchors"]:
        assert a["filter_key"] in {"location", "category", "episode", "date_from"}
        assert "label" in a and "value" in a and "cue" in a


def test_facets_returns_monthly_chapters():
    res = client.get("/facets")
    assert res.status_code == 200
    data = res.json()
    assert "monthly_chapters" in data
    chapters = data["monthly_chapters"]
    assert len(chapters) >= 5
    first = chapters[0]
    for key in ("month", "label", "date_from", "date_to", "count", "thumbnail"):
        assert key in first
    assert first["count"] > 0
    assert first["thumbnail"].startswith("library/")


def test_extract_returns_the_contract_shape():
    body = client.post("/extract", json={"text": "our Goa trip"}).json()
    assert set(body) >= {"filters", "chips", "source", "notice"}
    assert set(body["filters"]) <= {"date_from", "date_to", "location", "category", "episode"}


def test_extract_without_a_key_uses_rules():
    body = client.post("/extract", json={"text": "cafe in Goa"}).json()
    assert body["source"] == "rules"
    assert body["filters"]["location"] == "Goa"


def test_search_returns_grouped_episodes():
    body = client.post("/search", json={"text": "cafe in Goa",
                                        "filters": {"location": "Goa"},
                                        "mode": "trails"}).json()
    assert body["mode"] == "trails"
    assert isinstance(body["episodes"], list)
    assert body["filters_applied"] == {"location": "Goa"}


def test_baseline_mode_drops_the_filters():
    body = client.post("/search", json={"text": "cafe", "filters": {"location": "Goa"},
                                        "mode": "baseline"}).json()
    assert body["filters_applied"] == {}


def test_search_rejects_a_filter_key_outside_the_contract():
    r = client.post("/search", json={"text": "x", "filters": {"camera": "Pixel"}, "mode": "trails"})
    assert r.status_code == 422


def test_search_rejects_an_unparseable_date():
    r = client.post("/search", json={"text": "x", "filters": {"date_from": "yesterday"},
                                     "mode": "trails"})
    assert r.status_code == 422


def test_blank_text_is_rejected():
    assert client.post("/extract", json={"text": "   "}).status_code == 422


def test_overlong_text_is_rejected():
    assert client.post("/extract", json={"text": "x" * 501}).status_code == 422


def test_an_unknown_mode_is_rejected():
    r = client.post("/search", json={"text": "x", "filters": {}, "mode": "sideways"})
    assert r.status_code == 422


# --- Screen 4 needs the whole surrounding sequence ---------------------------

def test_episode_endpoint_returns_the_full_sequence():
    body = client.post("/episode", json={"episode_id": "ep07"}).json()
    assert "photos" in body and isinstance(body["photos"], list)


def test_episode_photos_are_in_date_order():
    photos = client.post("/episode", json={"episode_id": "ep07"}).json()["photos"]
    dates = [p["date"] for p in photos if p["date"]]
    assert dates == sorted(dates)


def test_unknown_episode_returns_an_empty_sequence_not_an_error():
    r = client.post("/episode", json={"episode_id": "does-not-exist"})
    assert r.status_code == 200
    assert r.json()["photos"] == []


def test_episode_requires_an_id():
    assert client.post("/episode", json={}).status_code == 422


# --- roadmap: rejection memory, density cues, evidence detail ---------------

def test_search_accepts_rejected_episode_ids():
    body = client.post("/search", json={"text": "cafe in Goa", "filters": {"location": "Goa"},
                                        "mode": "trails", "rejected": ["ep07"]}).json()
    assert all(e["episode_id"] != "ep07" for e in body["episodes"])


def test_search_rejects_too_many_rejected_ids():
    r = client.post("/search", json={"text": "x", "filters": {}, "mode": "trails",
                                     "rejected": [f"ep{i}" for i in range(60)]})
    assert r.status_code == 422


def test_cards_include_density_cues_and_usefulness():
    ep = client.post("/search", json={"text": "cafe in Goa", "filters": {"location": "Goa"},
                                      "mode": "trails"}).json()["episodes"][0]
    for key in ("places", "scenes", "span_days", "usefulness", "episode_total"):
        assert key in ep


def test_evidence_detail_names_the_dimension_and_its_certainty():
    ep = client.post("/search", json={"text": "cafe in Goa",
                                      "filters": {"location": "Goa", "date_from": "2023-12-01",
                                                  "date_to": "2023-12-31"},
                                      "mode": "trails"}).json()["episodes"][0]
    detail = {d["dimension"]: d for d in ep["evidence"]}
    assert detail["Place"]["certainty"] == "strong"
    assert detail["Date"]["certainty"] == "approximate"


# --- fixes checklist, 28 Sep: demo anchors and scoped evidence ----------------

def test_anchors_are_memory_cues_not_city_filters():
    anchors = client.get("/facets").json()["top_anchors"]
    labels = [a["label"] for a in anchors]
    assert "graduation" in labels and "cake" in labels
    assert not any(a["filter_key"] == "location" for a in anchors), labels
    assert all(a.get("kind_label") for a in anchors)


def test_evidence_says_whether_it_is_in_this_photo_nearby_or_approximate():
    ep = client.post("/search", json={
        "text": "the handmade cake from my sister's graduation",
        "filters": {"episode": "sister's graduation", "category": "cake"},
        "mode": "soft"}).json()["episodes"][0]
    scopes = {d["dimension"]: d["scope"] for d in ep["evidence"]}
    assert scopes["Event"] == "nearby"
    assert scopes["Scene"] in {"direct", "nearby"}
    date_ep = client.post("/search", json={"text": "cafe in Goa", "filters": {
        "location": "Goa", "date_from": "2023-12-01", "date_to": "2023-12-31"},
        "mode": "trails"}).json()["episodes"][0]
    assert {d["dimension"]: d["scope"] for d in date_ep["evidence"]}["Date"] == "approximate"


def test_demo_tasks_surface_their_moment_first():
    tasks = {
        "The photo of the handmade cake from my sister's graduation": "sister's graduation",
        "The group photo after our college performance": "college performance",
        "The picture of the handwritten note from my old apartment": "old apartment",
        "The photo of my dog curled up in the suitcase": "packing for the trip",
    }
    for text, episode in tasks.items():
        read = client.post("/extract", json={"text": text}).json()
        eps = client.post("/search", json={"text": text, "filters": read["filters"],
                                           "mode": "soft"}).json()["episodes"]
        assert eps[0]["episode"] == episode, (text, [e["episode"] for e in eps[:3]])


def test_month_covers_are_never_sensitive_photos():
    import main
    by_file = {r.get("file"): r.get("category") for r in main.RECORDS}
    for ch in client.get("/facets").json()["monthly_chapters"]:
        assert by_file.get(ch["thumbnail"]) not in main.SENSITIVE_COVER, ch


def test_conflicts_come_from_the_search_that_ran():
    """F4 lives on /search: it reflects the filters actually applied and what was shown."""
    body = {"text": "pichle saal wali Goa trip", "mode": "soft",
            "filters": {"episode": "goa trip", "date_from": "2025-01-01", "date_to": "2025-12-31"}}
    c = client.post("/search", json=body).json()["conflicts"]
    assert len(c) == 1 and c[0]["episode"] == "goa trip"
    assert isinstance(c[0]["shown_episode"], bool) and isinstance(c[0]["shown_window"], bool)
    # Remove the date clue and the conflict goes with it.
    body["filters"] = {"episode": "goa trip"}
    assert client.post("/search", json=body).json()["conflicts"] == []
    # A festival-derived window is never flagged.
    body["filters"] = {"episode": "goa trip", "date_from": "2025-01-01", "date_to": "2025-12-31"}
    body["date_meta"] = {"kind": "festival"}
    assert client.post("/search", json=body).json()["conflicts"] == []
    assert "conflicts" not in client.post("/extract", json={"text": "pichle saal wali Goa trip"}).json()


# --- visual cue suggestions and vector steering -------------------------------

def test_search_returns_cue_suggestions():
    res = client.post("/search", json={"text": "haldi ceremony", "filters": {}, "mode": "soft"})
    assert res.status_code == 200
    body = res.json()
    assert "cue_suggestions" in body
    assert isinstance(body["cue_suggestions"], list)
    assert len(body["cue_suggestions"]) <= 4
    if body["cue_suggestions"]:
        s = body["cue_suggestions"][0]
        for key in ("label", "phrase", "group", "seen_in", "of"):
            assert key in s


def test_seen_steers_results_without_changing_filters_applied():
    unseen = client.post("/search", json={"text": "family gathering", "filters": {}, "mode": "soft"}).json()
    seen = client.post("/search", json={"text": "family gathering", "filters": {}, "mode": "soft", "seen": ["orange"]}).json()
    assert seen["filters_applied"] == unseen["filters_applied"]
    assert seen["seen_applied"] == ["orange"]
    unseen_ids = [p["id"] for g in unseen["episodes"] for p in g["photos"]]
    seen_ids = [p["id"] for g in seen["episodes"] for p in g["photos"]]
    assert unseen_ids != seen_ids


def test_unknown_seen_label_returns_422():
    res = client.post("/search", json={"text": "family", "filters": {}, "mode": "soft", "seen": ["fake_not_real"]})
    assert res.status_code == 422
    assert "unknown visual cues" in res.json()["detail"]


def test_too_many_seen_labels_returns_422():
    res = client.post("/search", json={"text": "family", "filters": {}, "mode": "soft", "seen": ["orange", "red", "white", "pink"]})
    assert res.status_code == 422


def test_baseline_mode_returns_empty_cue_suggestions():
    res = client.post("/search", json={"text": "family", "filters": {}, "mode": "baseline", "seen": ["orange"]}).json()
    assert res["cue_suggestions"] == []
    assert res["seen_applied"] == []


def test_health_reports_cue_bank_status():
    body = client.get("/health").json()
    assert "cue_bank" in body

