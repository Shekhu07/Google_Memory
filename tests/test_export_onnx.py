"""ONNX text output must match sentence-transformers, or every search result is wrong.

The 494 image vectors came from sentence-transformers/clip-ViT-B-32. If the text tower
lands in a different space, results look plausible and are meaningless. This is the gate.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "webapp/apps/retrieval/data"

pytest.importorskip("onnxruntime")

QUERIES = ["a small cafe in Goa", "the medicine I took last year",
           "wedding photos", "whiteboard from the product workshop"]


@pytest.mark.skipif(not (DATA / "clip_text.onnx").exists(), reason="run engine.export_onnx first")
def test_onnx_text_embeddings_match_sentence_transformers():
    sys.path.insert(0, str(ROOT / "webapp/apps/retrieval"))
    from encoder import TextEncoder
    sentence_transformers = pytest.importorskip("sentence_transformers")

    mine = TextEncoder(DATA).encode(QUERIES)
    theirs = sentence_transformers.SentenceTransformer("clip-ViT-B-32").encode(QUERIES)

    def unit(m):
        return m / np.linalg.norm(m, axis=1, keepdims=True)

    cos = (unit(mine) * unit(np.asarray(theirs))).sum(axis=1)
    assert cos.min() > 0.999, f"ONNX diverged from sentence-transformers: {cos}"
