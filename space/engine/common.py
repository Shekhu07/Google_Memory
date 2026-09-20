"""Shared record format and file helpers for all source collectors.

Every collector writes the same normalised record so later stages
(filters, extraction, audit) never need to know where a post came from.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"

# Ask Photos timeline, used to tag every record with the era it was written in.
ASK_PHOTOS_LAUNCH = "2024-10-01"   # US rollout begins
HYBRID_RELAUNCH = "2025-06-01"     # paused, relaunched as classic + Gemini hybrid
TOGGLE_ANNOUNCED = "2026-03-01"    # classic / Ask Photos toggle announced


def era_for(date_iso: str) -> str:
    """Map an ISO date (YYYY-MM-DD...) to the Ask Photos era it falls in."""
    day = date_iso[:10]
    if day < ASK_PHOTOS_LAUNCH:
        return "pre_ask"
    if day < HYBRID_RELAUNCH:
        return "ask_launch"
    if day < TOGGLE_ANNOUNCED:
        return "hybrid"
    return "toggle"


def make_record(*, source: str, source_id: str, url: str, date: str, text: str,
                context_title: str = "", parent_id: str = "", kind: str = "post") -> dict:
    """Build a normalised record. Author identity is deliberately never stored."""
    return {
        "id": f"{source}:{source_id}",
        "source": source,
        "kind": kind,
        "url": url,
        "date": date,
        "era": era_for(date),
        "context_title": context_title,
        "parent_id": parent_id,
        "text": text.strip(),
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def load_ids(path: Path) -> set:
    """Ids already written to a JSONL file, so reruns skip them."""
    if not path.exists():
        return set()
    with path.open() as f:
        return {json.loads(line)["id"] for line in f if line.strip()}


def append_jsonl(path: Path, records: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_json(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(path)
