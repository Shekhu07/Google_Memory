import json
import re
from pathlib import Path

import pytest

from engine import import_survey as imp
from engine.extract import VOCAB

GS = Path(__file__).resolve().parent.parent / "research" / "survey_form.gs"


def _titles(gs: str) -> list:
    """Question titles, lowercased. Handles titles built by joining literals with +,
    which a naive .setTitle('...') regex silently skips."""
    out = []
    for call in re.findall(r"\.setTitle\((.*?)\)\s*\n", gs, re.S):
        parts = re.findall(r"'([^']*)'", call)
        if parts:
            out.append("".join(parts).lower())
    return out


# ---------------------------------------------------------------- vocabulary lock

def test_every_mapped_value_exists_in_the_engine_vocabulary():
    """Responses must merge into episodes.jsonl, not form a separate silo."""
    allowed = {v for vals in VOCAB.values() for v in vals}
    allowed |= {"re_acquired", "typed_search", "none_mentioned"}   # documented additions
    for field, mapping in imp.OPTIONS.items():
        if field in imp.SURVEY_ONLY_FIELDS:
            continue     # research signal, not episode data - see SURVEY_ONLY_FIELDS
        for label, value in mapping.items():
            assert value in allowed, f"{field}: {label!r} -> {value!r} is not an engine value"


def test_the_one_new_value_is_the_documented_one():
    """survey_design.md flags exactly one value outside VOCAB. Catch any others."""
    allowed = {v for vals in VOCAB.values() for v in vals} | {"typed_search", "none_mentioned"}
    extra = {v for f, m in imp.OPTIONS.items() if f not in imp.SURVEY_ONLY_FIELDS
             for v in m.values() if v not in allowed}
    assert extra == {"re_acquired"}, extra


def test_survey_only_fields_are_all_real_fields():
    """A typo in SURVEY_ONLY_FIELDS would silently exempt nothing, or exempt a
    field that does need to merge. Both are worse than a loud failure."""
    assert imp.SURVEY_ONLY_FIELDS <= set(imp.OPTIONS), \
        imp.SURVEY_ONLY_FIELDS - set(imp.OPTIONS)
    assert imp.SURVEY_ONLY_FIELDS <= set(imp.COLUMNS), \
        imp.SURVEY_ONLY_FIELDS - set(imp.COLUMNS)


@pytest.mark.skipif(not GS.exists(), reason="survey_form.gs not present")
def test_import_knows_every_option_the_form_offers():
    """If the form's wording drifts, import silently drops answers. Fail loudly instead."""
    text = GS.read_text(encoding="utf-8")
    offered = set(re.findall(r"'([^'\n]{12,})',?[ \t]*//[ \t]*[a-z_]", text))
    known = {label for m in imp.OPTIONS.values() for label in m}
    for option in offered:
        assert any(k.lower() in option.lower() for k in known), \
            f"form offers {option!r} but no import mapping matches it"


# ---------------------------------------------------------------- comma hazard

def test_checkbox_options_containing_commas_survive_parsing():
    """Google Forms joins selections with ', ' and these options contain commas."""
    cell = ('Roughly when it was — "last summer", "about two years ago", '
            'What was going on — a trip, a festival, being ill, a wedding, '
            'What is in the picture — an object, food, a pet')
    got = imp.parse_multi(cell, imp.OPTIONS["cues_retained"])
    assert got == ["temporal_approx", "event_anchor", "object"]


def test_naive_comma_split_would_have_failed():
    """Guards the reason this parser exists."""
    cell = 'What was going on — a trip, a festival, being ill, a wedding'
    assert len(cell.split(",")) == 4          # naive split shatters one answer into four
    assert imp.parse_multi(cell, imp.OPTIONS["cues_retained"]) == ["event_anchor"]


def test_partial_and_empty_cells():
    assert imp.parse_multi("", imp.OPTIONS["cues_lost"]) == []
    assert imp.parse_multi("Who was in it", imp.OPTIONS["cues_lost"]) == ["people"]
    assert imp.parse_single("", imp.OPTIONS["outcome"]) == ""


def test_longest_match_wins_when_options_overlap():
    """'Where it was, and the name of the place' contains 'Where it was'."""
    got = imp.parse_multi("Where it was, but not what the place is called",
                          imp.OPTIONS["cues_retained"])
    assert got == ["place_unnamed"]


# ---------------------------------------------------------------- record shape

def _row():
    return {
        "Timestamp": "09/21/2026 14:03:11",
        "Has this happened to you in the last year — looking for a photo you were sure existed, and struggling to find it?": "Yes",
        "Which app do you mainly use to look back at your photos?": "Google Photos",
        "Roughly how many photos and videos do you have saved?": "More than 20,000",
        "How often do you go looking for a photo that is more than a year old?": "A few times a month",
        "When you go looking for an old photo, what do you usually do first?": "Type something into the search bar",
        "What were you trying to find?": "the medicine strip from when I was ill",
        "What kind of photo was it?": "A photo of medicine, a prescription or a label",
        "What did you still remember about it? Tick everything that applies.":
            'Roughly when it was — "last summer", "about two years ago", What was going on — a trip, a festival, being ill, a wedding',
        "And what had you forgotten? Tick everything that applies.": "When it was taken, Which album or folder it is in",
        "What exactly did you type into search?": "medicine, tablet, strip",
        "When you type into photo search, what language do you use?": "A mix of Hindi and English, typed in English letters",
        "Were you using the AI answer or the normal search?": "The normal keyword search",
        "What actually went wrong? Pick the closest one.": "Nothing came up, and I had no idea what to change or try next",
        "What did you do next? Tick everything you tried.": "Scrolled through everything, Gave up",
        "Did you find it in the end?": "No, I never found it",
        "Roughly how long did you spend before you found it or stopped?": "5–15 minutes",
        "Did not finding it cause you any actual trouble?": "Yes — I had to ask someone or get the document again",
        "Would you be up for a 40-minute video call about this?": "Yes",
        # Added 21 Sep. Titles here are deliberately the OLD wording where it
        # still exists, proving COLUMNS matches a fragment and not an exact title.
        "When a result looked close, what would have helped you check it? Tick all that apply.":
            "Photos taken just before or after it, A short reason why it came up",
        "Have you heard of Ask Photos?": "Yes, and I have used it",
        "If you have not used it, what has kept you from trying Ask Photos?": "",
        "If you have used it, how did Ask Photos work for you?":
            "It showed related photos, but not the one I wanted",
        "What was the biggest problem with Ask Photos?":
            "I could not tell why it showed those results",
        "What would Ask Photos need to do better for memories that are hard to describe?":
            "Show photos from the same trip or event, Explain why a photo came up",
    }


def _record():
    row = _row()
    return imp.row_to_record(row, imp.find_columns(list(row)), 0)


def test_columns_are_found_by_fragment_not_exact_title():
    cols = imp.find_columns(list(_row()))
    assert set(cols) == set(imp.COLUMNS), set(imp.COLUMNS) - set(cols)


def test_record_maps_onto_engine_fields():
    r = _record()
    assert r["id"] == "survey:0000" and r["source"] == "survey"
    assert r["specificity"] == "specific_attempt"
    assert r["asset_type"] == "medicine_label"
    assert r["cues_retained"] == ["temporal_approx", "event_anchor"]
    assert r["cues_lost"] == ["date", "album"]
    assert r["failure_stage"] == "cannot_refine"
    assert r["outcome"] == "not_found"
    assert r["query_language"] == "hinglish_code_mixed"
    assert r["schema"] == imp.SCHEMA


def test_first_move_does_not_collide_with_workaround():
    """Q4 measures Expression; Q13 measures fallback. Merging them destroys Q4."""
    r = _record()
    assert r["first_move"] == "typed_search"
    assert r["workaround"] == "manual_scroll"
    assert r["workarounds"] == ["manual_scroll", "gave_up"]


def test_single_workaround_stays_comparable_with_engine_rows():
    r = _record()
    assert isinstance(r["workaround"], str)
    assert r["workaround"] in r["workarounds"]


def test_era_is_flagged_as_response_time_not_incident_time():
    """The survey never asks when the failure happened; don't pretend otherwise."""
    r = _record()
    assert r["era_source"] == "response_time"
    assert r["era"]


def test_hypotheses_are_rule_derived_and_labelled_as_such():
    r = _record()
    assert r["hypotheses_source"] == "rule"
    assert "H3" in r["hypotheses"]      # cannot_refine
    assert "H4" in r["hypotheses"]      # hinglish
    assert "H5" in r["hypotheses"]      # medicine_label


def test_h1_needs_both_a_misread_query_and_an_episodic_cue():
    base = {"failure_stage": "system_misunderstood", "cues_retained": ["object"],
            "query_language": "en", "asset_type": "photo"}
    assert "H1" not in imp.derive_hypotheses(base)
    base["cues_retained"] = ["temporal_approx"]
    assert "H1" in imp.derive_hypotheses(base)


def test_respondents_with_no_failure_are_not_counted_as_episodes():
    row = _row()
    for q in ["What actually went wrong? Pick the closest one.",
              "What did you still remember about it? Tick everything that applies.",
              "What were you trying to find?"]:
        row[q] = ""
    rec = imp.row_to_record(row, imp.find_columns(list(row)), 1)
    assert not imp.is_episode(rec)
    assert imp.is_episode(_record())


def test_missing_timestamp_does_not_crash():
    row = _row(); row["Timestamp"] = "not a date"
    rec = imp.row_to_record(row, imp.find_columns(list(row)), 0)
    assert rec["date"]


def test_an_option_that_is_a_substring_of_another_does_not_double_match():
    """'English' sits inside 'A mix of Hindi and English, typed in English letters'."""
    cell = "A mix of Hindi and English, typed in English letters"
    assert imp.parse_multi(cell, imp.OPTIONS["query_language"]) == ["hinglish_code_mixed"]
    assert imp.parse_single(cell, imp.OPTIONS["query_language"]) == "hinglish_code_mixed"


def test_plain_english_still_parses():
    assert imp.parse_single("English", imp.OPTIONS["query_language"]) == "en"


def test_a_match_must_start_a_selection_not_appear_mid_sentence():
    """Free-text-ish noise must not be read as a selection."""
    assert imp.parse_multi("I once typed English words", imp.OPTIONS["query_language"]) == []


@pytest.mark.skipif(not GS.exists(), reason="survey_form.gs not present")
def test_every_column_fragment_appears_in_a_real_question_title():
    """COLUMNS matches spreadsheet headers, and a header is the question title.

    Nothing tied the two together, so rewording a title would have silently
    orphaned a column and dropped that answer for every respondent. This closes
    that gap: edit the form's wording freely, and this test says what to fix.
    """
    gs = GS.read_text()
    titles = _titles(gs)
    orphans = [f for f in imp.COLUMNS.values() if not any(f in t for t in titles)]
    assert not orphans, f"COLUMNS fragments with no matching question title: {orphans}"


@pytest.mark.skipif(not GS.exists(), reason="survey_form.gs not present")
def test_no_column_fragment_matches_two_different_questions():
    """An ambiguous fragment would bind the field to whichever column came first."""
    gs = GS.read_text()
    titles = _titles(gs)
    for field, fragment in imp.COLUMNS.items():
        hits = [t for t in titles if fragment in t]
        assert len(hits) <= 1, f"{field!r} fragment {fragment!r} matches {hits}"


# ---------------------------------------------------------------- merged sections

def test_ask_photos_answers_are_captured():
    r = _record()
    assert r["ask_awareness"] == "used"
    assert r["ask_outcome"] == "related_only"
    assert r["ask_problem"] == "unexplained"
    assert r["ask_needs"] == ["show_episode", "explain_why"]


def test_recognition_needs_capture_what_would_have_helped():
    assert _record()["recognition_needs"] == ["sequence", "why_shown"]


def test_uncertain_outcome_stays_separable_from_success_and_failure():
    """The group the MVP exists for: something surfaced and they still could not tell."""
    assert imp.retrieval_certainty("I found something similar, but was not sure it was right",
                                   "unknown") == "uncertain"
    assert imp.retrieval_certainty("I found the right trip or event, but not the exact photo",
                                   "unknown") == "uncertain"
    assert imp.retrieval_certainty("Yes, fairly quickly", "found_fast") == "exact"
    assert imp.retrieval_certainty("No, I never found it", "not_found") == "failed"
    assert imp.retrieval_certainty("I stopped looking", "not_found") == "failed"


def test_uncertain_answers_still_map_to_an_engine_outcome():
    """They must remain mergeable with episodes.jsonl, not become a new outcome."""
    for answer in imp.UNCERTAIN_ANSWERS:
        assert imp.parse_single(answer, imp.OPTIONS["outcome"]) == "unknown"


def test_an_unanswered_ask_photos_section_is_empty_not_wrong():
    row = _row()
    for k in list(row):
        if "Ask Photos" in k:
            row[k] = ""
    rec = imp.row_to_record(row, imp.find_columns(list(row)), 0)
    assert rec["ask_awareness"] == "" and rec["ask_needs"] == []


# ---------------------------------------------------------------- required questions

def test_the_gate_answer_is_captured():
    assert _record()["had_failure"] == "yes"


def test_gate_longest_match_wins_over_the_bare_yes():
    """"Yes" is a substring of "Yes, but I do not remember when"."""
    assert imp.parse_single("Yes, but I do not remember when",
                            imp.OPTIONS["had_failure"]) == "yes_undated"
    assert imp.parse_single("No, this has not happened to me",
                            imp.OPTIONS["had_failure"]) == "no"


@pytest.mark.skipif(not GS.exists(), reason="survey_form.gs not present")
def test_every_hypothesis_bearing_question_is_required():
    """A respondent could previously answer four questions and submit, leaving a row
    with no failure data. These are the questions the case study cannot do without."""
    gs = GS.read_text()
    must = [
        "What did you still remember?",          # H1, the brief's core
        "What actually went wrong?",             # the hypothesis ranking
        "When you search your photos, what language do you use?",   # only test of H4
        "Did you find it in the end?",           # URR numerator
        "What did you do next?",                 # brief requires workarounds
        "Have you heard of Ask Photos?",         # Ask Photos comparison
    ]
    for title in must:
        start = gs.find(title)
        assert start != -1, f"question missing: {title}"
        nxt = gs.find(".setTitle(", start + len(title))
        block = gs[start:nxt if nxt != -1 else len(gs)]
        assert ".setRequired(true)" in block, f"{title!r} is not required"


@pytest.mark.skipif(not GS.exists(), reason="survey_form.gs not present")
def test_free_text_questions_stay_optional():
    """Required open text is the fastest way to lose a respondent."""
    gs = GS.read_text()
    for title in ["What were you trying to find?",
                  "What exactly did you type into search?",
                  "Anything else about finding old photos"]:
        start = gs.find(title)
        nxt = gs.find(".setTitle(", start + len(title))
        assert ".setRequired(false)" in gs[start:nxt], f"{title!r} should stay optional"


@pytest.mark.skipif(not GS.exists(), reason="survey_form.gs not present")
def test_the_gate_routes_non_sufferers_straight_to_submit():
    """Required questions in section 2 are only safe because of this branch."""
    gs = GS.read_text()
    assert "FormApp.PageNavigationType.SUBMIT" in gs
    assert "No, this has not happened to me', FormApp.PageNavigationType.SUBMIT" in gs
