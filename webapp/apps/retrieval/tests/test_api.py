import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_reports_readiness():
    body = client.get("/health").json()
    assert body["images"] == 494
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
