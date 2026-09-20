"""Export the CLIP text tower to ONNX. Runs locally; the output is committed.

The 494 image vectors were produced by sentence-transformers/clip-ViT-B-32, which
wraps openai/clip-vit-base-patch32. The text side must land in the same space or
every search result is quietly wrong. tests/test_export_onnx.py proves it does.
"""
from pathlib import Path

MODEL = "openai/clip-vit-base-patch32"


def export(out_dir: Path) -> Path:
    import torch
    from transformers import CLIPTextModelWithProjection, CLIPTokenizerFast

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tok = CLIPTokenizerFast.from_pretrained(MODEL)
    tok.save_pretrained(out_dir)

    model = CLIPTextModelWithProjection.from_pretrained(MODEL).eval()
    dummy = tok(["a photo"], return_tensors="pt", padding="max_length", max_length=77)
    path = out_dir / "clip_text.onnx"
    torch.onnx.export(
        model,
        (dummy["input_ids"], dummy["attention_mask"]),
        str(path),
        input_names=["input_ids", "attention_mask"],
        output_names=["text_embeds"],
        dynamic_axes={"input_ids": {0: "batch"},
                      "attention_mask": {0: "batch"},
                      "text_embeds": {0: "batch"}},
        opset_version=17,
    )
    _to_fp16_sharded(path)
    return path


# Ops left in fp32: converting them produces a graph onnxruntime rejects with a
# type error on GatherND, and they carry no meaningful weight anyway.
FP16_BLOCK = ["GatherND", "Gather", "Range", "Shape", "Slice", "Expand",
              "ConstantOfShape", "Where"]


def _to_fp16_sharded(path: Path) -> None:
    """Convert to fp16 and save one external file per tensor.

    Two Vercel limits force this. torch.onnx.export writes a single 254 MB
    .onnx.data blob and no individual file may exceed 100 MB, so weights are split
    per tensor. The whole function bundle may not exceed 225 MB and fp32 came to
    302 MB, so the weights are fp16 (125 MB).

    fp16 was verified before adoption, to the same bar int8 failed: cosine against
    fp32 is 0.999999, and oracle recall@20 (0.583) and hit@1 (0.233) are unchanged.
    It does move the inferred-filter score, 0.646 -> 0.612, which is why every
    number quoted anywhere is measured with THIS encoder, not with fp32.
    """
    import onnx
    from onnxconverter_common import float16

    model = onnx.load(str(path))
    converted = float16.convert_float_to_float16(
        model, keep_io_types=True, op_block_list=FP16_BLOCK)
    for stale in path.parent.glob(f"{path.name}.data"):
        stale.unlink()
    onnx.save_model(
        converted, str(path),
        save_as_external_data=True,
        all_tensors_to_one_file=False,
        size_threshold=1024,
        convert_attribute=True,
    )


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "webapp/apps/retrieval/data"
    print(export(out))
