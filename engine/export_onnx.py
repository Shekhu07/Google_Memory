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
    _shard_external_data(path)
    return path


def _shard_external_data(path: Path) -> None:
    """Re-save with one external file per tensor.

    torch.onnx.export writes a single .onnx.data blob (~254 MB). Vercel rejects any
    individual file over 100 MB, so the weights are split per tensor instead. This is
    a re-serialisation only - tests/test_export_onnx.py re-proves numerical parity.
    """
    import onnx

    model = onnx.load(str(path))
    for stale in path.parent.glob(f"{path.name}.data"):
        stale.unlink()
    onnx.save_model(
        model, str(path),
        save_as_external_data=True,
        all_tensors_to_one_file=False,
        size_threshold=1024,
        convert_attribute=True,
    )


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "webapp/apps/retrieval/data"
    print(export(out))
