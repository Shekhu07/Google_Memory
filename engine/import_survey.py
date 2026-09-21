"""Turn Google Forms survey responses into episode records that merge with the engine.

The survey (research/survey_form.gs) structures the narration the engine could not
find in public text: 8.6% of 720 collected posts were scoreable, versus ~100% of
qualifying survey responses. This module is what makes those responses usable
alongside `episodes.jsonl` instead of sitting in a separate silo.

Three mismatches are handled here rather than papered over:

  1. **Checkbox cells contain commas.** Google Forms joins multiple selections with
     ", " and several option texts have commas inside them ("a trip, a festival,
     being ill"). Splitting on comma shreds them, so options are matched
     longest-first as substrings and removed as they are found.
  2. **Q4 and Q13 both describe workarounds but mean different things.** Q4 is the
     *first move* (the Expression term in URR); Q13 is what they tried *after*
     failing. Merging them would destroy Q4's meaning, so Q4 lands in `first_move`.
  3. **The engine stores one `workaround`; Q13 allows several.** The full list goes
     to `workarounds`, and `workaround` takes the first in form order so the field
     stays comparable with engine rows.

Survey hypotheses are **rule-derived**, not model-assigned like the engine's, so
they carry `hypotheses_source: "rule"`. Report the two separately; do not pool them
into one ranking without saying so.

Usage:
  .venv/bin/python -m engine.import_survey responses.csv
"""
import argparse
import csv
import json
import sys
from datetime import datetime

from engine.common import ROOT, era_for, save_json

OUT = ROOT / "data" / "interim" / "survey_episodes.jsonl"
STATS = ROOT / "data" / "processed" / "survey_stats.json"
SCHEMA = "survey-v1"

# A distinctive fragment of each question title, so light rewording does not break import.
COLUMNS = {
    "app":            "mainly use to look back",
    "library_size":   "how many photos and videos do you have",
    "frequency":      "how often do you go looking",
    "first_move":     "what do you usually do first",
    "evidence":       "what were you trying to find",
    "asset_type":     "what kind of photo was it",
    "cues_retained":  "what did you still remember",
    "cues_lost":      "what had you forgotten",
    "query_verbatim": "what exactly did you type",
    "query_language": "what language do you use",
    "search_mode":    "ai answer or the normal search",
    "failure_stage":  "what actually went wrong",
    "workarounds":    "what did you do next",
    "outcome":        "did you find it in the end",
    "time_spent":     "how long did you spend",
    "consequence":    "cause you any actual trouble",
    "willing":        "up for a 40-minute video call",
    # Added 21 Sep with the Ask Photos and concept sections.
    "recognition_needs": "would have helped you check it",
    "ask_awareness":     "heard of ask photos",
    "ask_not_used_why":  "kept you from trying ask photos",
    "ask_outcome":       "how did ask photos work",
    "ask_problem":       "biggest problem with ask photos",
    "ask_needs":         "do better for memories that are hard to describe",
}

# Option text -> engine vocabulary value. Must stay in step with survey_form.gs;
# tests/test_import_survey.py cross-checks this against the script itself.
OPTIONS = {
    "asset_type": {
        "An ordinary photo": "photo",
        "A screenshot": "screenshot",
        "A photo of a document, receipt or bill": "document_receipt",
        "A photo of medicine, a prescription or a label": "medicine_label",
        "A video": "video",
        "Something else": "unknown",
    },
    "cues_retained": {
        "Roughly when it was": "temporal_approx",
        "The exact date": "exact_date",
        "What was going on": "event_anchor",
        "Where it was, and the name of the place": "place_named",
        "Where it was, but not what the place is called": "place_unnamed",
        "Who was with me": "who_with",
        "What is in the picture": "object",
        "Words written inside the photo": "text_in_image",
        "A colour, or roughly what it looked like": "appearance_colour",
        "Which phone or app it came from": "device_or_app_source",
        "What happened just before or just after it": "sequence",
        "A name or caption I had added to it myself": "own_label_or_caption",
    },
    "cues_lost": {
        "When it was taken": "date",
        "Where it was taken": "place",
        "Which album or folder it is in": "album",
        "Who was in it": "people",
        "The exact words to search for": "exact_words",
        "What the file was called": "filename",
    },
    "query_language": {
        "English": "en",
        "A mix of Hindi and English": "hinglish_code_mixed",
        "Hindi, in Devanagari": "hi",
        "Another language": "other",
        "I do not type": "no_query",
    },
    "search_mode": {
        "The AI one": "ask_photos_or_ai",
        "The normal keyword search": "classic",
        "I tried both": "both_compared",
        "I do not know which one": "not_mentioned",
    },
    "failure_stage": {
        "I did not know what to type": "cannot_express",
        "I typed something, but got nothing back": "system_misunderstood",
        "The results looked reasonable": "not_surfaced",
        "Too many similar results": "cannot_evaluate_results",
        "Nothing came up, and I had no idea what to change": "cannot_refine",
        "The album, folder or view I normally use": "browse_path_changed",
        "The app was too slow": "slow_or_broken_ui",
        "I gave up before getting that far": "abandoned",
    },
    "workarounds": {
        "Scrolled back through the timeline": "date_scroll",
        "Scrolled through everything": "manual_scroll",
        "Dug through albums or folders": "albums_or_folders",
        "Looked in WhatsApp, Drive, email": "other_app",
        "Asked someone else": "ask_someone",
        "Switched to the normal search": "classic_search_toggle",
        "Took the photo or got the document again": "re_acquired",   # not in engine VOCAB
        "Gave up": "gave_up",
    },
    "first_move": {
        "Type something into the search bar": "typed_search",
        "Scroll back through the timeline": "date_scroll",
        "Open an album or a folder": "albums_or_folders",
        "Look in WhatsApp, Drive": "other_app",
        "Ask someone": "ask_someone",
    },
    "outcome": {
        "Yes, fairly quickly": "found_fast",
        "Yes, but it took a long time": "found_slow",
        # Both "uncertain" answers are outcome-unknown in the engine vocabulary.
        # retrieval_certainty below keeps them separable without breaking the merge.
        "I found something similar": "unknown",
        "I found the right trip or event": "unknown",
        "No, I never found it": "not_found",
        "I stopped looking": "not_found",
    },
    # --- survey-only fields, not in engine VOCAB -----------------------------
    "recognition_needs": {
        "Photos taken just before or after it": "sequence",
        "The date, or a rough date range": "date_range",
        "Where it was taken, or which trip": "place_or_trip",
        "Who else was in the nearby photos": "people_nearby",
        "Any words or text in the image": "text_in_image",
        "A short reason why it came up": "why_shown",
        "Nothing else would have helped": "nothing",
    },
    "ask_awareness": {
        "Yes, and I have used it": "used",
        "Yes, but I have not used it": "heard_only",
        "No, I had not heard of it": "unaware",
        "I am not sure": "unsure",
    },
    "ask_not_used_why": {
        "I did not know about it": "unaware",
        "I cannot get it where I am": "unavailable",
        "I do not know what to ask it": "unsure_what_to_ask",
        "The normal search is enough for me": "classic_enough",
        "I would rather browse myself": "prefer_browse",
        "I worry about privacy or accuracy": "trust_concern",
    },
    "ask_outcome": {
        "It found what I wanted quickly": "found_fast",
        "It helped after I asked again": "found_after_retry",
        "It showed related photos, but not the one I wanted": "related_only",
        "It was wrong, or not useful": "wrong",
        "I do not remember": "unknown",
    },
    "ask_problem": {
        "It did not understand my description": "not_understood",
        "Too many results, or unrelated ones": "too_many",
        "I could not tell why it showed those results": "unexplained",
        "I could not correct it or narrow it down": "cannot_refine",
        "It was slow": "slow",
        "I did not have a problem": "none",
    },
    "ask_needs": {
        "Help me describe what I remember": "help_describe",
        "Show photos from the same trip or event": "show_episode",
        "Show photos taken just before and after": "show_sequence",
        "Explain why a photo came up": "explain_why",
        "Help me carry on after a wrong result": "recover",
        "Work better with screenshots and documents": "documents",
        "It already works well for me": "works_well",
    },
}

# Fields that exist only in the survey. They are research signal, not engine
# episode data, so they are deliberately outside the VOCAB lock - but they must be
# declared here, so a new field cannot slip past the lock by accident.
SURVEY_ONLY_FIELDS = {
    "recognition_needs", "ask_awareness", "ask_not_used_why", "ask_outcome",
    "ask_problem", "ask_needs",
}

# Answers that mean "it surfaced something and I still could not tell". The
# analysis plan treats this group as the clearest opportunity, so it must stay
# separable from a plain success or a plain failure.
UNCERTAIN_ANSWERS = ("I found something similar", "I found the right trip or event")


def retrieval_certainty(outcome_cell: str, outcome: str) -> str:
    """exact | uncertain | failed - the three-way split the analysis plan needs."""
    if any(a.lower() in (outcome_cell or "").lower() for a in UNCERTAIN_ANSWERS):
        return "uncertain"
    if outcome in ("found_fast", "found_slow"):
        return "exact"
    if outcome in ("not_found",):
        return "failed"
    return "unknown"

# failure_stage / cue / field -> hypothesis. Explicit and auditable, unlike the
# model-assigned tags on engine rows.
STAGE_TO_H = {
    "cannot_refine": "H3",
    "browse_path_changed": "H6",
    "cannot_evaluate_results": "H2",
    "not_surfaced": "H2",
}


def parse_multi(cell: str, options: dict) -> list:
    """Vocabulary values present in a checkbox cell.

    Two hazards, both real in this form:

      * Google Forms joins selections with ", " and several option texts contain
        commas themselves, so splitting on comma shreds them.
      * Some options are substrings of others - "English" sits inside "A mix of
        Hindi and English, typed in English letters" - so a plain substring search
        returns both and the wrong one wins.

    So: match longest-first, mark the characters consumed, and only accept a match
    that begins a selection (start of cell, or just after ", ").
    """
    text = cell or ""
    low, consumed, found = text.lower(), [False] * len(text), []
    for label in sorted(options, key=len, reverse=True):
        needle, start = label.lower(), 0
        while True:
            i = low.find(needle, start)
            if i == -1:
                break
            end = i + len(needle)
            at_boundary = i == 0 or text[i - 2:i] == ", "
            if at_boundary and not any(consumed[i:end]):
                for j in range(i, end):
                    consumed[j] = True
                found.append(options[label])
                break
            start = i + 1
    order = list(options.values())
    return sorted(set(found), key=order.index)


def parse_single(cell: str, options: dict) -> str:
    values = parse_multi(cell, options)
    return values[0] if values else ""


def derive_hypotheses(record: dict) -> list:
    """Rule-derived, not model-assigned. Kept explicit so a reader can audit it."""
    out = set()
    stage = record.get("failure_stage", "")
    if stage in STAGE_TO_H:
        out.add(STAGE_TO_H[stage])
    cues = set(record.get("cues_retained", []))
    if stage == "system_misunderstood" and cues & {"temporal_approx", "event_anchor"}:
        out.add("H1")          # episodic clue the index could not use
    if record.get("query_language") == "hinglish_code_mixed":
        out.add("H4")
    if record.get("asset_type") in {"document_receipt", "medicine_label", "screenshot"}:
        out.add("H5")
    return sorted(out)


def find_columns(headers: list) -> dict:
    """Map our field names onto the actual CSV headers, by fragment."""
    found = {}
    for field, fragment in COLUMNS.items():
        for h in headers:
            if fragment.lower() in (h or "").lower():
                found[field] = h
                break
    return found


def row_to_record(row: dict, cols: dict, index: int) -> dict:
    def cell(field):
        return (row.get(cols.get(field, ""), "") or "").strip()

    stamp = (row.get("Timestamp") or row.get("Horodateur") or "").strip()
    try:
        when = datetime.strptime(stamp, "%m/%d/%Y %H:%M:%S").isoformat(timespec="seconds")
    except ValueError:
        when = datetime.now().isoformat(timespec="seconds")

    workarounds = parse_multi(cell("workarounds"), OPTIONS["workarounds"])
    rec = {
        "id": f"survey:{index:04d}",
        "source": "survey",
        "date": when,
        # The respondent describes a *recent* failure, but the survey never asks when
        # it happened, so this era is the response date, not the incident date.
        "era": era_for(when),
        "era_source": "response_time",
        "specificity": "specific_attempt",     # Section 2 forces one specific incident
        "asset_type": parse_single(cell("asset_type"), OPTIONS["asset_type"]) or "unknown",
        "cues_retained": parse_multi(cell("cues_retained"), OPTIONS["cues_retained"]),
        "cues_lost": parse_multi(cell("cues_lost"), OPTIONS["cues_lost"]),
        "query_verbatim": cell("query_verbatim"),
        "query_language": parse_single(cell("query_language"), OPTIONS["query_language"]),
        "search_mode": parse_single(cell("search_mode"), OPTIONS["search_mode"]) or "not_mentioned",
        "failure_stage": parse_single(cell("failure_stage"), OPTIONS["failure_stage"]),
        "workaround": workarounds[0] if workarounds else "none_mentioned",
        "workarounds": workarounds,
        "first_move": parse_single(cell("first_move"), OPTIONS["first_move"]),
        "outcome": parse_single(cell("outcome"), OPTIONS["outcome"]) or "unknown",
        "evidence": cell("evidence"),
        "evidence_verified": True,             # self-reported: the respondent is the source
        "confidence": "self_reported",
        "model": "survey",
        "schema": SCHEMA,
        # context, not engine fields
        "app": cell("app"),
        "library_size": cell("library_size"),
        "frequency": cell("frequency"),
        "time_spent": cell("time_spent"),
        "consequence": cell("consequence"),
        "willing_interview": cell("willing").lower().startswith("yes"),
        # Survey-only research signal. Kept beside the episode rather than merged
        # into it, so engine rows and survey rows stay comparable.
        "retrieval_certainty": retrieval_certainty(cell("outcome"),
                                                   parse_single(cell("outcome"), OPTIONS["outcome"])),
        "recognition_needs": parse_multi(cell("recognition_needs"), OPTIONS["recognition_needs"]),
        "ask_awareness": parse_single(cell("ask_awareness"), OPTIONS["ask_awareness"]),
        "ask_not_used_why": parse_multi(cell("ask_not_used_why"), OPTIONS["ask_not_used_why"]),
        "ask_outcome": parse_single(cell("ask_outcome"), OPTIONS["ask_outcome"]),
        "ask_problem": parse_single(cell("ask_problem"), OPTIONS["ask_problem"]),
        "ask_needs": parse_multi(cell("ask_needs"), OPTIONS["ask_needs"]),
    }
    rec["hypotheses"] = derive_hypotheses(rec)
    rec["hypotheses_source"] = "rule"
    return rec


def is_episode(rec: dict) -> bool:
    """Did this respondent actually narrate a retrieval failure?"""
    return bool(rec["failure_stage"] or rec["cues_retained"] or rec["evidence"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv", help="the Google Forms responses CSV")
    args = p.parse_args(argv)

    with open(args.csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("No rows in that CSV.")
        return 1
    cols = find_columns(list(rows[0]))
    missing = [f for f in COLUMNS if f not in cols]
    if missing:
        print(f"WARNING: could not find columns for {missing} - check the question wording")

    records = [row_to_record(r, cols, i) for i, r in enumerate(rows)]
    episodes = [r for r in records if is_episode(r)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in episodes))

    from collections import Counter
    stats = {
        "responses": len(records), "episodes": len(episodes),
        "willing_interview": sum(r["willing_interview"] for r in records),
        "frequency": dict(Counter(r["frequency"] for r in records if r["frequency"])),
        "first_move": dict(Counter(r["first_move"] for r in records if r["first_move"])),
        "outcome": dict(Counter(r["outcome"] for r in episodes)),
        "failure_stage": dict(Counter(r["failure_stage"] for r in episodes if r["failure_stage"])),
        "query_language": dict(Counter(r["query_language"] for r in episodes if r["query_language"])),
        "time_spent": dict(Counter(r["time_spent"] for r in episodes if r["time_spent"])),
        "consequence": dict(Counter(r["consequence"] for r in episodes if r["consequence"])),
        "hypotheses_rule_derived": dict(Counter(h for r in episodes for h in r["hypotheses"])),
    }
    save_json(STATS, stats)
    print(f"{len(records)} responses -> {len(episodes)} episodes ({OUT})")
    print(f"  willing to be interviewed: {stats['willing_interview']}")
    print(f"  outcomes: {stats['outcome']}")
    print(f"  failure stages: {stats['failure_stage']}")
    print(f"  rule-derived hypotheses: {stats['hypotheses_rule_derived']}")
    print(f"\nstats: {STATS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
