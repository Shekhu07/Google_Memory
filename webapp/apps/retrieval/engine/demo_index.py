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


def soft_search(query_vec, ids, matrix, records: list, top_k: int = 20,
                beta_date: float = 0.15, beta_place: float = 0.15, beta_cat: float = 0.1,
                beta_ep: float = 0.2, tau: float = 7.0, hard_exact: bool = True, **filters) -> list:
    """Soft scoring search (Idea A4 / Task T4).

    Score = cos(query, photo) + beta_date * w_date + beta_place * [place match] +
            beta_cat * [cat match] + beta_ep * [ep match]
    where w_date = 1 inside the window and exp(-days_outside / tau) outside.
    """
    from datetime import date

    matrix_norm = normalise(matrix)
    qv_norm = normalise(query_vec)[0]
    cos_sim = matrix_norm @ qv_norm

    date_from_str = filters.get("date_from", "")
    date_to_str = filters.get("date_to", "")
    loc = filters.get("location", "").lower()
    cat = filters.get("category", "")
    ep = filters.get("episode", "").lower()

    is_exact = bool(date_from_str and date_to_str and date_from_str == date_to_str)
    d_from = date.fromisoformat(date_from_str[:10]) if date_from_str else None
    d_to = date.fromisoformat(date_to_str[:10]) if date_to_str else None
    has_date = bool(d_from or d_to)

    boost = np.zeros(len(records), dtype="float32")
    allowed = np.ones(len(records), dtype=bool)

    for i, r in enumerate(records):
        # Date scoring
        if has_date:
            d_str = (r.get("date") or "")[:10]
            if len(d_str) == 10:
                try:
                    rd = date.fromisoformat(d_str)
                    if d_from and rd < d_from:
                        days_out = (d_from - rd).days
                    elif d_to and rd > d_to:
                        days_out = (rd - d_to).days
                    else:
                        days_out = 0

                    if days_out == 0:
                        w_d = 1.0
                    else:
                        if is_exact and hard_exact:
                            allowed[i] = False
                            w_d = 0.0
                        else:
                            w_d = float(np.exp(-days_out / tau))
                except ValueError:
                    w_d = 0.0
                    if is_exact and hard_exact:
                        allowed[i] = False
            else:
                w_d = 0.0
                if is_exact and hard_exact:
                    allowed[i] = False
            boost[i] += beta_date * w_d

        # Place scoring
        if loc and loc in (r.get("location") or "").lower():
            boost[i] += beta_place

        # Category scoring
        if cat and r.get("category") == cat:
            boost[i] += beta_cat

        # Episode scoring
        if ep and ep in (r.get("episode") or "").lower():
            boost[i] += beta_ep

    total_scores = cos_sim + boost
    if hard_exact and is_exact:
        total_scores[~allowed] = -999.0

    order = np.argsort(-total_scores)
    out = []
    for idx in order:
        if hard_exact and is_exact and not allowed[idx]:
            continue
        out.append((ids[idx], float(total_scores[idx])))
        if len(out) >= top_k:
            break
    return out


def outside_window_photos(query_vec, ids, matrix, records: list, limit: int = 5,
                          max_days: int = 45, **filters) -> list:
    """Photos that fall just outside the query's date window, sorted by similarity."""
    from datetime import date

    date_from_str = filters.get("date_from", "")
    date_to_str = filters.get("date_to", "")
    if not (date_from_str or date_to_str):
        return []

    d_from = date.fromisoformat(date_from_str[:10]) if date_from_str else None
    d_to = date.fromisoformat(date_to_str[:10]) if date_to_str else None

    matrix_norm = normalise(matrix)
    qv_norm = normalise(query_vec)[0]
    cos_sim = matrix_norm @ qv_norm

    candidates = []
    for i, r in enumerate(records):
        d_str = (r.get("date") or "")[:10]
        if len(d_str) != 10:
            continue
        try:
            rd = date.fromisoformat(d_str)
        except ValueError:
            continue

        offset = 0
        if d_from and rd < d_from:
            offset = -(d_from - rd).days
        elif d_to and rd > d_to:
            offset = (rd - d_to).days
        else:
            continue  # inside the window

        if 0 < abs(offset) <= max_days:
            candidates.append({
                "id": r["id"],
                "file": r.get("file", ""),
                "date": d_str,
                "offset_days": offset,
                "score": float(cos_sim[i]),
                "category": r.get("category", ""),
                "location": r.get("location", ""),
                "title": r.get("title", ""),
            })

    candidates.sort(key=lambda c: -c["score"])
    return candidates[:limit]


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
