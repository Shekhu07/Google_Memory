import pytest

from engine import demo_library as dl


def _item(i=1, thumb=True):
    return {"id": f"ov-{i}", "title": "a receipt", "creator": "someone",
            "license": "by-sa", "license_version": "2.0",
            "foreign_landing_url": "https://flickr.com/x",
            "url": "https://example.test/full.jpg",
            "thumbnail": "https://example.test/thumb.jpg" if thumb else None}


def test_quota_sums_to_the_requested_total():
    for total in (20, 100, 500, 501):
        q = dl.quota(total)
        assert sum(q.values()) == total, (total, q)
        assert set(q) == set(dl.CATEGORIES)
        assert all(v >= 1 for v in q.values())


def test_quota_overweights_utility_photos():
    """Receipts/medicine/whiteboards/documents are where retrieval actually breaks."""
    q = dl.quota(500)
    utility = q["receipt"] + q["medicine"] + q["whiteboard"] + q["document"]
    assert utility / 500 >= 0.30


def test_record_prefers_thumbnail_and_keeps_attribution():
    rec = dl.to_record(_item(), "receipt", 3)
    assert rec["id"] == "demo:0003" and rec["file"] == "images/0003.jpg"
    assert rec["download_url"].endswith("thumb.jpg")      # not the full image
    assert rec["license"] == "by-sa 2.0" and rec["creator"] == "someone"
    assert rec["source_url"].startswith("https://")


def test_record_falls_back_to_full_image_and_rejects_unusable():
    assert dl.to_record(_item(thumb=False), "receipt", 1)["download_url"].endswith("full.jpg")
    assert dl.to_record({"title": "no id"}, "receipt", 1) is None


def _records(n_per_cat=6):
    out, i = [], 0
    for cat in dl.CATEGORIES:
        for _ in range(n_per_cat):
            out.append({"id": f"demo:{i:04d}", "category": cat})
            i += 1
    return out


def test_every_record_gets_a_date_even_when_it_belongs_to_no_episode():
    recs = dl.assign_episodes(_records())
    assert all(r.get("date") for r in recs)
    assert all(r.get("location") and r.get("device") for r in recs)


def test_episodes_are_internally_consistent():
    """One episode = one place, one device, one contiguous date window."""
    recs = dl.assign_episodes(_records())
    grouped = {}
    for r in recs:
        if r["episode_id"]:
            grouped.setdefault(r["episode_id"], []).append(r)
    assert len(grouped) >= 10, f"only {len(grouped)} episodes populated"
    for eid, rs in grouped.items():
        assert len({r["location"] for r in rs}) == 1, eid
        assert len({r["device"] for r in rs}) == 1, eid
        assert len({r["episode"] for r in rs}) == 1, eid
        span = max(r["date"] for r in rs)[:10], min(r["date"] for r in rs)[:10]
        assert span[0] >= span[1]


def test_library_keeps_some_stray_photos():
    """A library where every photo sits in a tidy episode would flatter the MVP."""
    recs = dl.assign_episodes(_records(n_per_cat=12))
    assert any(not r["episode_id"] for r in recs)


def test_assignment_is_deterministic():
    a = dl.assign_episodes(_records(), seed=7)
    b = dl.assign_episodes(_records(), seed=7)
    assert [(r["episode_id"], r["date"]) for r in a] == [(r["episode_id"], r["date"]) for r in b]


class _Resp:
    def __init__(self, data, status=200):
        self.data, self.status_code, self.text = data, status, ""
        self.content = b"x" * 5000

    def json(self):
        return self.data


class _Session:
    def __init__(self, pages):
        self.pages, self.calls = list(pages), 0

    def get(self, url, **kw):
        self.calls += 1
        return self.pages.pop(0) if self.pages else _Resp({"results": []})


def test_search_pages_until_it_has_enough():
    s = _Session([_Resp({"results": [_item(i) for i in range(50)]}),
                  _Resp({"results": [_item(i) for i in range(50, 70)]})])
    assert len(dl.search("q", 60, s)) == 60


def test_search_stops_on_empty_page_rather_than_looping():
    s = _Session([_Resp({"results": []})])
    assert dl.search("q", 100, s) == []
    assert s.calls == 1


class _RecordingSession:
    """Captures the params of every request so limits can be asserted."""
    def __init__(self, per_page=20):
        self.seen, self.per_page = [], per_page

    def get(self, url, **kw):
        self.seen.append(kw.get("params", {}))
        page = kw["params"]["page"]
        return _Resp({"results": [_item(f"{page}-{i}") for i in range(self.per_page)]})


def test_search_never_exceeds_the_anonymous_page_size_limit():
    """Openverse 401s on page_size > 20 for anonymous requests (hit on the 500-image run)."""
    s = _RecordingSession()
    dl.search("q", 200, s)
    assert s.seen, "no requests made"
    assert all(p["page_size"] <= dl.MAX_PAGE_SIZE for p in s.seen), s.seen


def test_search_pages_enough_to_fill_a_large_request():
    s = _RecordingSession()
    assert len(dl.search("q", 60, s)) == 60


class _StatusSession:
    """Serves a scripted sequence of HTTP statuses, recording which urls were tried."""
    def __init__(self, statuses):
        self.statuses, self.tried = list(statuses), []

    def get(self, url, **kw):
        self.tried.append(url)
        status = self.statuses.pop(0) if self.statuses else 200
        r = _Resp({}, status=status)
        r.content = b"x" * (5000 if status == 200 else 200)
        return r


def test_download_falls_back_when_the_thumbnail_is_dead(tmp_path):
    """Openverse 424s on gone upstreams; this wiped 34/35 festival images once."""
    s = _StatusSession([424, 200])
    assert dl.download("https://thumb", tmp_path / "a.jpg", s, "https://full") is True
    assert s.tried == ["https://thumb", "https://full"]
    assert (tmp_path / "a.jpg").exists()


def test_download_gives_up_when_both_urls_fail(tmp_path):
    s = _StatusSession([424, 404])
    assert dl.download("https://thumb", tmp_path / "a.jpg", s, "https://full") is False
    assert not (tmp_path / "a.jpg").exists()


def test_download_rejects_truncated_images(tmp_path):
    s = _StatusSession([200])
    s.statuses = []
    r = _Resp({}, status=200); r.content = b"tiny"
    s.get = lambda url, **kw: r
    assert dl.download("https://thumb", tmp_path / "a.jpg", s) is False


def test_record_keeps_a_fallback_url_when_a_thumbnail_exists():
    rec = dl.to_record(_item(), "receipt", 1)
    assert rec["download_url"].endswith("thumb.jpg")
    assert rec["fallback_url"].endswith("full.jpg")
    # no thumbnail -> nothing to fall back to
    assert dl.to_record(_item(thumb=False), "receipt", 1)["fallback_url"] == ""
