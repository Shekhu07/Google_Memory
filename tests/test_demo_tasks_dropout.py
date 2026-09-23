"""Tests for E1 cue-dropout task generator and dataset."""
import json
import re
from pathlib import Path

from engine.demo_tasks_dropout import (
    LIBRARY_FILE,
    OUT_FILE,
    generate_dropout_tasks,
)


def test_dropout_generation_volume_and_balance():
    tasks = generate_dropout_tasks()
    assert len(tasks) == 120

    levels = [t["level"] for t in tasks]
    for lvl in ("L3", "L2", "L1", "L0"):
        assert levels.count(lvl) == 30


def test_dropout_tasks_metadata_and_library_presence():
    library_ids = {json.loads(line)["id"] for line in LIBRARY_FILE.open(encoding="utf-8") if line.strip()}
    tasks = [json.loads(line) for line in OUT_FILE.open(encoding="utf-8") if line.strip()]

    assert len(tasks) == 120
    for t in tasks:
        assert t["source"] == "constructed"
        assert t["target_id"] in library_ids
        for aid in t["answer_ids"]:
            assert aid in library_ids
        assert len(t["query"].strip()) > 5


def test_dropout_no_numeric_dates():
    tasks = [json.loads(line) for line in OUT_FILE.open(encoding="utf-8") if line.strip()]
    for t in tasks:
        q = t["query"]
        # Must not contain numeric slash/hyphen dates like 25/12/2024 or 2024-12-25
        assert not re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", q), f"Numeric date in {t['id']}: {q}"
        assert not re.search(r"\b\d{4}-\d{2}-\d{2}\b", q), f"ISO date in {t['id']}: {q}"


def test_dropout_l0_no_filters_extracted():
    from webapp.apps.retrieval.clues import extract_clues
    from webapp.apps.retrieval.main import FACETS
    from datetime import date

    today = date(2026, 9, 23)
    tasks = [json.loads(line) for line in OUT_FILE.open(encoding="utf-8") if line.strip()]
    l0_tasks = [t for t in tasks if t["level"] == "L0"]

    assert len(l0_tasks) == 30
    # L0 is pure paraphrased content - should extract 0 filters
    for t in l0_tasks:
        res = extract_clues(t["query"], FACETS, today)
        assert res["filters"] == {}, f"Over-interpretation on L0 query {t['id']}: {t['query']!r} -> {res['filters']}"
