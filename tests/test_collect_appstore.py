from engine import collect_appstore as ca


def _entry(rid="111", title="Search got worse", body="I can't find my old receipts anymore", rating="2"):
    return {"id": {"label": rid}, "title": {"label": title}, "content": {"label": body},
            "updated": {"label": "2026-08-20T10:00:00-07:00"}, "im:rating": {"label": rating},
            "im:version": {"label": "7.1"}, "author": {"name": {"label": "Someone"}}}


def test_entry_combines_title_and_body_and_drops_author():
    rec = ca.entry_to_record(_entry(), "in")
    assert rec["id"] == "appstore:111"
    assert rec["text"] == "Search got worse. I can't find my old receipts anymore"
    assert (rec["score"], rec["country"], rec["era"]) == (2, "in", "toggle")
    assert "Someone" not in str(rec)


class _Resp:
    def __init__(self, data=None, bad=False):
        self.data, self.bad = data, bad

    def json(self):
        if self.bad:
            raise ValueError("not json")
        return self.data


class _Session:
    def __init__(self, resp):
        self.resp = resp

    def get(self, *a, **k):
        return self.resp


def test_fetch_page_handles_single_entry_metadata_and_end_of_feed():
    single = _Session(_Resp({"feed": {"entry": _entry()}}))
    assert len(ca.fetch_page("us", 1, single)) == 1

    with_meta = _Session(_Resp({"feed": {"entry": [{"id": {"label": "app"}}, _entry()]}}))
    assert len(ca.fetch_page("us", 1, with_meta)) == 1

    assert ca.fetch_page("us", 11, _Session(_Resp(bad=True))) == []
