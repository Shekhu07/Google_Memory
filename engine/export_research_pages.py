"""Turn the two published response CSVs into the JSON behind the engine's
/survey and /mvp-test pages.

The Google Forms are closed, so a reader who opens them sees no questions.
These pages show every question with its answers instead, read from the same
anonymised CSVs the engine already serves. Runs locally; output is committed.

    .venv/bin/python -m engine.export_research_pages
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "engineapp" / "apps" / "web" / "public" / "data"

# Column index -> kind. Anything not listed is a single choice.
# Sections follow the pages of each Google Form.
FORMS = {
    "survey": {
        "csv": "survey-responses.csv",
        "multi": {9, 10, 16, 17, 22, 25},
        "text": {7, 11, 26},
        "scale": set(),
        "sections": [
            (2, "About you and your photos"),
            (6, "Has it happened to you?"),
            (7, "The last time you could not find a photo"),
            (21, "Ask Photos"),
            (26, "Anything else"),
        ],
    },
    "mvp-test": {
        "csv": "mvp-test-responses.csv",
        "multi": {13},
        "text": {4, 5, 11, 14, 16, 17, 19, 20},
        "scale": {15, 18},
        "sections": [
            (2, "Page 1 · Are you in the segment?"),
            (3, "Page 2 · One search in your own Google Photos"),
            (10, "Page 3 · Two tasks in the prototype"),
            (15, "Page 4 · How it went"),
        ],
    },
}


def build(spec: dict) -> dict:
    rows = list(csv.reader((DATA / spec["csv"]).open(encoding="utf-8")))
    header, body = rows[0], rows[1:]
    starts = dict(spec["sections"])
    sections: list = []
    for j in range(2, len(header)):
        if j in starts:
            sections.append({"title": starts[j], "questions": []})
        answers = [(r[0], r[j].strip()) for r in body if r[j].strip()]
        kind = ("text" if j in spec["text"] else "multi" if j in spec["multi"]
                else "scale" if j in spec["scale"] else "choice")
        q = {"q": header[j], "kind": kind, "answered": len(answers)}
        if kind == "text":
            q["answers"] = [{"id": rid, "text": a} for rid, a in answers]
        else:
            who: dict = {}
            for rid, a in answers:
                for opt in (a.split(";") if kind == "multi" else [a]):
                    who.setdefault(opt.strip(), []).append(rid)
            counts = Counter({k: len(v) for k, v in who.items()})
            order = (sorted(who, key=lambda k: -int(k)) if kind == "scale"
                     else [k for k, _ in counts.most_common()])
            q["options"] = [{"option": k, "count": counts[k], "ids": who[k]} for k in order]
        sections[-1]["questions"].append(q)
    dates = sorted(r[1] for r in body)
    return {"n": len(body), "first": dates[0], "last": dates[-1], "sections": sections}


def main() -> None:
    for name, spec in FORMS.items():
        out = DATA / f"{name}.json"
        out.write_text(json.dumps(build(spec), indent=1, ensure_ascii=False) + "\n")
        print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
