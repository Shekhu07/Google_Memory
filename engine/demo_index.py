"""CLIP index over the demo library, plus the plain-search baseline the MVP must beat.

Decided 20 Sep: CLIP embeddings only, no captioning model. That keeps the build
free and offline, at a known cost - CLIP is weak on text *inside* an image, which
is exactly the receipt / medicine-label / whiteboard case H5 is about. If Phase 5
user testing shows those failing, captions are the first thing to add.

Two things live here and they must not be confused:

  baseline_search  - plain text->image similarity over the whole library. This is
                     what Google Photos already does well, and what the MVP is
                     measured against.
  filtered_search  - the same similarity, restricted by metadata (date window,
                     place, episode). The Phase 4 core module builds on this: the
                     intelligence is in *choosing* the filter from a vague clue,
                     not in the similarity itself.

Usage:
  .venv/bin/python -m engine.demo_index --build
  .venv/bin/python -m engine.demo_index --query "the cafe from our goa trip"
"""
import argparse
import json
import sys
from datetime import datetime

import numpy as np

from engine.common import ROOT

DEMO = ROOT / "data" / "demo"
LIBRARY = DEMO / "library.jsonl"
INDEX = DEMO / "index.npz"
MODEL_NAME = "clip-ViT-B-32"   # ~600MB on first use, then cached locally


def load_library() -> list:
    if not LIBRARY.exists():
        return []
    return [json.loads(l) for l in LIBRARY.open(encoding="utf-8")]


def normalise(m: np.ndarray) -> np.ndarray:
    """Unit-length rows so a dot product is cosine similarity."""
    m = np.asarray(m, dtype="float32")
    if m.ndim == 1:
        m = m[None, :]
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.maximum(norms, 1e-9)


def in_window(record: dict, date_from: str = "", date_to: str = "") -> bool:
    day = (record.get("date") or "")[:10]
    if not day:
        return not (date_from or date_to)
    if date_from and day < date_from[:10]:
        return False
    if date_to and day > date_to[:10]:
        return False
    return True


def apply_filters(records: list, date_from: str = "", date_to: str = "",
                  location: str = "", category: str = "", episode: str = "") -> list:
    """Metadata narrowing. Every filter is optional; all supplied ones must match."""
    out = []
    for r in records:
        if not in_window(r, date_from, date_to):
            continue
        if location and location.lower() not in (r.get("location") or "").lower():
            continue
        if category and r.get("category") != category:
            continue
        if episode and episode.lower() not in (r.get("episode") or "").lower():
            continue
        out.append(r)
    return out


def rank(query_vec: np.ndarray, ids: list, matrix: np.ndarray,
         allowed: set = None, top_k: int = 20) -> list:
    """(id, score) for the closest images, optionally restricted to `allowed` ids."""
    scores = (normalise(matrix) @ normalise(query_vec)[0])
    order = np.argsort(-scores)
    out = []
    for i in order:
        if allowed is not None and ids[i] not in allowed:
            continue
        out.append((ids[i], float(scores[i])))
        if len(out) >= top_k:
            break
    return out


def baseline_search(query_vec, ids, matrix, top_k: int = 20) -> list:
    """Plain semantic search over everything - the thing the MVP must beat."""
    return rank(query_vec, ids, matrix, allowed=None, top_k=top_k)


def filtered_search(query_vec, ids, matrix, records: list, top_k: int = 20, **filters) -> list:
    """Semantic search inside a metadata window."""
    keep = {r["id"] for r in apply_filters(records, **filters)}
    return rank(query_vec, ids, matrix, allowed=keep, top_k=top_k)


def recall_at_k(results: list, answer_ids: set, k: int = 20) -> float:
    """Share of the known answers that appear in the top k."""
    if not answer_ids:
        return 0.0
    got = {rid for rid, _ in results[:k]}
    return len(got & answer_ids) / len(answer_ids)


def load_model(name: str = MODEL_NAME):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name)


def build(limit: int = 0, append: bool = False) -> int:
    """Embed the library. With append, embed only records the index lacks and keep
    every existing vector bit-for-bit, so published scores stay reproducible."""
    from PIL import Image
    records = load_library()
    if limit:
        records = records[:limit]
    old_ids, old_matrix = (load_index() if append and INDEX.exists() else ([], None))
    if append:
        have = set(old_ids)
        records = [r for r in records if r["id"] not in have]
        print(f"appending {len(records)} new images to {len(old_ids)} indexed")
        if not records:
            return 0
    if not records:
        print("No library yet - run engine.demo_library first.")
        return 1
    model = load_model()
    ids, vecs, skipped = [], [], 0
    for i, r in enumerate(records, 1):
        path = DEMO / r["file"]
        try:
            with Image.open(path) as im:
                vecs.append(model.encode(im.convert("RGB")))
            ids.append(r["id"])
        except Exception as e:
            skipped += 1
            print(f"  skipped {r['file']}: {type(e).__name__}")
        if i % 50 == 0:
            print(f"  embedded {i}/{len(records)}")
    matrix = normalise(np.vstack(vecs))
    if old_matrix is not None:
        ids, matrix = list(old_ids) + ids, np.vstack([old_matrix, matrix.astype(old_matrix.dtype)])
    np.savez_compressed(INDEX, ids=np.array(ids), matrix=matrix)
    print(f"\nindexed {len(ids)} images ({skipped} skipped) -> {INDEX}")
    return 0


def load_index():
    data = np.load(INDEX, allow_pickle=False)
    return list(data["ids"]), data["matrix"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--build", action="store_true")
    p.add_argument("--append", action="store_true", help="with --build: embed only new records")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--query", default="")
    p.add_argument("--top-k", type=int, default=10)
    args = p.parse_args(argv)

    if args.build:
        return build(args.limit, append=args.append)
    if not args.query:
        p.print_help()
        return 1
    if not INDEX.exists():
        print("No index yet - run with --build first.")
        return 1
    ids, matrix = load_index()
    records = {r["id"]: r for r in load_library()}
    qv = load_model().encode([args.query])
    print(f"query: {args.query!r}\n")
    for rid, score in baseline_search(qv, ids, matrix, args.top_k):
        r = records.get(rid, {})
        print(f"  {score:.3f}  {rid}  {r.get('category','?'):<11} {r.get('episode') or '(stray)':<18} "
              f"{(r.get('date') or '')[:10]}  {r.get('title','')[:40]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
