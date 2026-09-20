import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_reports_readiness():
    body = client.get("/health").json()
    assert body["images"] == 494
    assert "encoder" in body


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
