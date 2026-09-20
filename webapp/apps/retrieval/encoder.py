"""ONNX CLIP text tower. No torch at runtime.

Image vectors are precomputed, so the service only ever encodes the query string.
"""
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

MAX_LEN = 77


class TextEncoder:
    def __init__(self, model_dir):
        model_dir = Path(model_dir)
        self.tok = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        self.tok.enable_padding(length=MAX_LEN, pad_id=0, pad_token="<|endoftext|>")
        self.tok.enable_truncation(max_length=MAX_LEN)
        self.session = ort.InferenceSession(
            str(model_dir / "clip_text.onnx"), providers=["CPUExecutionProvider"])

    def encode(self, texts) -> np.ndarray:
        enc = self.tok.encode_batch(list(texts))
        ids = np.array([e.ids for e in enc], dtype=np.int64)
        mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
        out = self.session.run(["text_embeds"],
                               {"input_ids": ids, "attention_mask": mask})
        return out[0].astype(np.float32)
