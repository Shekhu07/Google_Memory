"""The deployed service must return exactly what the offline code returns.

This is what mechanically stops the live demo and the deck from disagreeing, and
it is the reason the backend is Python rather than TypeScript.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "webapp/apps/retrieval/data"

pytest.importorskip("onnxruntime")
pytestmark = pytest.mark.skipif(not (DATA / "clip_text.onnx").exists(),
                                reason="run engine.export_onnx and engine.export_web first")

from engine import demo_eval, demo_index  # noqa: E402  (must precede the service path)

if str(ROOT / "webapp/apps/retrieval") not in sys.path:
    sys.path.append(str(ROOT / "webapp/apps/retrieval"))


@pytest.fixture(scope="module")
def ctx():
    from encoder import TextEncoder
    from search import SearchContext
    records = [json.loads(line) for line in (DATA / "library.jsonl").open()]
    idx = np.load(DATA / "index.npz", allow_pickle=False)
    return SearchContext(ids=list(idx["ids"]), matrix=idx["matrix"],
                         records=records, encoder=TextEncoder(DATA))


@pytest.fixture(scope="module")
def tasks():
    return [json.loads(line) for line in (ROOT / "data/eval/tasks.jsonl").open()]


def _flat(result):
    return [p["id"] for e in result["episodes"] for p in e["photos"]]


def test_service_search_matches_offline_filtered_search(ctx, tasks):
    from search import search
    by_id = {r["id"]: r for r in ctx.records}
    for t in tasks:
        filters = demo_eval.filters_for(t, by_id[t["target_id"]])
        qv = ctx.encoder.encode([t["query"]])
        expected = [i for i, _ in demo_index.filtered_search(
            qv, ctx.ids, ctx.matrix, ctx.records, 20, **filters)]
        got = _flat(search(t["query"], filters, "trails", ctx))
        assert sorted(got) == sorted(expected), f"divergence on {t['id']}"


def test_service_baseline_matches_offline_baseline(ctx, tasks):
    from search import search
    for t in tasks:
        qv = ctx.encoder.encode([t["query"]])
        expected = [i for i, _ in demo_index.baseline_search(qv, ctx.ids, ctx.matrix, 20)]
        got = _flat(search(t["query"], {}, "baseline", ctx))
        assert sorted(got) == sorted(expected), f"baseline divergence on {t['id']}"


def test_grouping_never_drops_or_duplicates_a_hit(ctx, tasks):
    from search import search
    for t in tasks:
        got = _flat(search(t["query"], {}, "baseline", ctx))
        assert len(got) == len(set(got)), f"duplicate hit on {t['id']}"
        assert len(got) == 20, f"lost a hit while grouping on {t['id']}"
