import json
from pathlib import Path
import pytest

from engine.demo_tasks_real import (
    DEV_FAMILIES,
    TEST_FAMILIES,
    OUT_FILE,
    generate_real_tasks,
)

ROOT = Path(__file__).resolve().parent.parent


def test_real_tasks_file_exists_and_has_60_tasks():
    assert OUT_FILE.exists(), "tasks_real.jsonl does not exist"
    tasks = [json.loads(line) for line in OUT_FILE.open(encoding="utf-8")]
    assert len(tasks) == 60, f"Expected 60 tasks, got {len(tasks)}"


def test_real_tasks_schema_and_integrity():
    tasks = [json.loads(line) for line in OUT_FILE.open(encoding="utf-8")]
    base_counts = {}
    for t in tasks:
        assert "id" in t
        assert "base_task_id" in t
        assert "query" in t and len(t["query"].strip()) > 0
        assert "phrasing_family" in t
        assert "source" in t and t["source"] in ("real_pattern", "constructed", "survey")
        assert "split" in t and t["split"] in ("dev", "test")
        assert "answer_ids" in t and len(t["answer_ids"]) > 0
        assert "target_id" in t

        base_id = t["base_task_id"]
        base_counts[base_id] = base_counts.get(base_id, 0) + 1

    assert len(base_counts) == 30, f"Expected 30 unique base tasks, got {len(base_counts)}"
    for base_id, count in base_counts.items():
        assert count == 2, f"Base task {base_id} should have exactly 2 variants, got {count}"


def test_phrasing_family_splits_are_disjoint():
    tasks = [json.loads(line) for line in OUT_FILE.open(encoding="utf-8")]
    dev_fams = {t["phrasing_family"] for t in tasks if t["split"] == "dev"}
    test_fams = {t["phrasing_family"] for t in tasks if t["split"] == "test"}

    assert dev_fams.issubset(DEV_FAMILIES)
    assert test_fams.issubset(TEST_FAMILIES)
    assert dev_fams.isdisjoint(test_fams), "Dev and test phrasing families must be completely disjoint"


def test_generator_is_deterministic():
    tasks1 = generate_real_tasks()
    tasks2 = generate_real_tasks()
    assert tasks1 == tasks2, "generate_real_tasks must be strictly deterministic"
