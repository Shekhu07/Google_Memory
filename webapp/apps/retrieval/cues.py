"""Visual-cue suggestions after a miss ("Try what you might have seen").

The 26 Sep own-library probe: the only natural search that found its photo described
what was visible ("me wearing orange t-shirt"); every search anchored on a festival,
a life phase or a ritual failed. People keep anchors, but the index reads pixels. So
when the first moments don't hold the photo, offer a few visible details to add.

Where the suggestions come from: the CLIP image vectors of the closest candidates,
scored against a fixed, reviewed vocabulary of visible details. Nothing is generated
and nothing is read from the visitor's words beyond the query vector already built.

A good suggestion *splits* the candidates. A detail present in every close photo
("cake" for a cake query) cannot narrow anything, and one present in none has no
evidence behind it, so each cue is scored by how evenly it divides the set, and cues
the query already says are skipped.
"""
import re
from dataclasses import dataclass

import numpy as np

# (label shown on the chip, text appended to the description, CLIP prompt, group).
# Deliberately plain and non-sensitive: no bodies, ages, skin or documents' contents.
VOCAB = [
    # Colours - the cue the probe showed working.
    ("red", "red", "a photo where red is the main colour", "colour"),
    ("orange", "orange", "a photo where orange is the main colour", "colour"),
    ("yellow", "yellow", "a photo where yellow is the main colour", "colour"),
    ("green", "green", "a photo where green is the main colour", "colour"),
    ("blue", "blue", "a photo where blue is the main colour", "colour"),
    ("pink", "pink", "a photo where pink is the main colour", "colour"),
    ("white", "white", "a photo where white is the main colour", "colour"),
    ("dark / black", "dark", "a dark photo, mostly black", "colour"),
    # What someone was wearing.
    ("traditional outfit", "traditional clothes", "a photo of people in traditional festive clothes", "wearing"),
    ("t-shirt", "t-shirt", "a photo of a person wearing a t-shirt", "wearing"),
    ("formal wear", "formal clothes", "a photo of people in suits and formal wear", "wearing"),
    ("gown or dress", "dress", "a photo of a woman in a dress", "wearing"),
    # Who was in frame.
    ("one person", "one person", "a photo of a single person", "people"),
    ("a group", "group of people", "a group photo of many people", "people"),
    ("a child", "a child", "a photo of a child", "people"),
    # Things in the photo.
    ("flowers", "flowers", "a photo of flowers", "thing"),
    ("candles or diyas", "candles", "a photo of candles or oil lamps", "thing"),
    ("string lights", "lights", "a photo of decorative string lights", "thing"),
    ("food on a table", "food on a table", "a photo of food served on a table", "thing"),
    ("a cup or drink", "a drink", "a photo of a cup of coffee or a drink", "thing"),
    ("a cake", "cake", "a photo of a cake", "thing"),
    ("a dog or cat", "a pet", "a photo of a dog or a cat", "thing"),
    ("gym equipment", "gym equipment", "a photo of gym equipment and weights", "thing"),
    ("a screen", "a screen", "a photo of a computer or phone screen", "thing"),
    ("paper with writing", "paper with writing", "a photo of a paper with writing on it", "thing"),
    ("a car or bike", "a vehicle", "a photo of a car or a motorbike", "thing"),
    ("a stage", "a stage", "a photo of a stage with performers", "thing"),
    # Where and when it looked like.
    ("indoors", "indoors", "a photo taken indoors", "setting"),
    ("outdoors", "outdoors", "a photo taken outdoors", "setting"),
    ("at night", "at night", "a photo taken at night", "setting"),
    ("sunny daylight", "in sunlight", "a photo in bright sunny daylight", "setting"),
    ("the sea or a beach", "the sea", "a photo of the sea or a beach", "setting"),
    ("hills or mountains", "mountains", "a photo of hills or mountains", "setting"),
    ("trees and greenery", "trees", "a photo of trees and greenery", "setting"),
    ("a street", "a street", "a photo of a city street", "setting"),
    ("a building", "a building", "a photo of a building", "setting"),
]

LABELS = {v[0] for v in VOCAB}

PRESENT_Z = 1.0          # a cue "shows" in a photo when it scores 1 sd above the library mean
MIN_SHARE = 0.15         # ...in at least this share of the candidates (evidence)
MAX_SHARE = 0.80         # ...and not in nearly all of them (it must narrow)
QUERY_MARGIN = 0.12      # skip a cue the query already says: its text sits this far above
                         # the median cue (raw CLIP text cosines are all high, so relative)
MAX_PER_GROUP = 2


@dataclass
class CueBank:
    labels: list
    phrases: list
    groups: list
    text: np.ndarray       # cues x d, unit rows
    z: np.ndarray          # photos x cues, z-scored against the whole library


def build_bank(encoder, matrix: np.ndarray) -> CueBank:
    t = encoder.encode([v[2] for v in VOCAB]).astype(np.float32)
    t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
    s = matrix @ t.T
    z = (s - s.mean(0)) / np.maximum(s.std(0), 1e-9)
    return CueBank([v[0] for v in VOCAB], [v[1] for v in VOCAB], [v[3] for v in VOCAB], t, z)


def _said(query: str, phrase: str, label: str) -> bool:
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    return any(w in words for w in (phrase.lower().split() + label.lower().split())
               if len(w) > 3 and w not in {"with", "photo", "people", "person"}) \
        or phrase.lower() in query.lower()


STEER = 1.0              # weight of an added visual cue against the description (tuned in sim)


def known(label: str) -> bool:
    return label in LABELS


def steer(bank: CueBank, query_vec: np.ndarray, labels: list) -> np.ndarray:
    """Move the query toward the visible details the user picked.

    The description stays the anchor; each cue adds its own text vector. Unknown
    labels are ignored rather than trusted.
    """
    q = np.asarray(query_vec, dtype=np.float32).reshape(1, -1)
    q = q / max(float(np.linalg.norm(q)), 1e-9)
    seen_set = set()
    idx = []
    for l in labels:
        if l in bank.labels and l not in seen_set:
            seen_set.add(l)
            idx.append(bank.labels.index(l))
    if not idx:
        return q
    v = q + STEER * bank.text[idx].sum(0, keepdims=True)
    return v / max(float(np.linalg.norm(v)), 1e-9)


def suggest(bank: CueBank, query: str, query_vec: np.ndarray, rows: list, limit: int = 4,
            exclude: list = ()) -> list:
    """Up to `limit` visible details that would split the candidate photos.

    rows: library row indices of the closest candidates, best first.
    """
    if len(rows) < 4:
        return []
    exclude_set = set(exclude or ())
    present = bank.z[rows] > PRESENT_Z                      # candidates x cues
    share = present.mean(0)
    lift = np.clip(bank.z[rows].mean(0), 0, None)
    q = query_vec.reshape(-1).astype(np.float32)
    q = q / max(float(np.linalg.norm(q)), 1e-9)
    overlap = bank.text @ q
    said_bar = float(np.median(overlap)) + QUERY_MARGIN

    scored = []
    for j in range(len(bank.labels)):
        if bank.labels[j] in exclude_set or not (MIN_SHARE <= share[j] <= MAX_SHARE):
            continue
        if overlap[j] >= said_bar or _said(query, bank.phrases[j], bank.labels[j]):
            continue
        split = share[j] * (1 - share[j])                  # 0.25 at an even split
        scored.append((split * (1 + lift[j]), j))
    scored.sort(reverse=True)

    out, per_group = [], {}
    for _, j in scored:
        g = bank.groups[j]
        if per_group.get(g, 0) >= MAX_PER_GROUP:
            continue
        per_group[g] = per_group.get(g, 0) + 1
        out.append({"label": bank.labels[j], "phrase": bank.phrases[j], "group": g,
                    "seen_in": int(present[:, j].sum()), "of": len(rows)})
        if len(out) == limit:
            break
    return out
