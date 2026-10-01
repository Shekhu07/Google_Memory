/**
 * Creates the RETRIEVAL SURVEY as a real Google Form.
 *
 * This is NOT the interview screener. That is research/recruitment/screener_form.gs and it stays
 * a tight 9 questions because every extra question costs bookings.
 *
 * WHY THIS FORM EXISTS
 *   The engine's hard finding (20 Sep) is that people almost never narrate a complete
 *   retrieval attempt in public text: 8.6% scoreable across 720 posts from four
 *   platforms, and the rate does not move with the source. This form fixes that by
 *   STRUCTURING the narration instead of hoping to find it - every respondent who had
 *   a failure walks through cue -> query -> failure stage -> outcome. Yield goes from
 *   8.6% to ~100% of qualifying responses.
 *
 * WHAT IT BUYS, BEYOND MORE EPISODES
 *   Three URR terms are currently MODELLED, not measured (Plan 2 section 5.4). This
 *   form measures them:
 *     Q3  -> n-bar, retrieval tasks per user per period
 *     Q4  -> Expression, the share who start a search at all vs scroll or give up
 *     Q14 -> the outcome distribution, a measured proxy for the URR numerator
 *   Per rule D of brief/SCORECARDS_AND_LESSONS.md, measured beats modelled for the Data
 *   and Metrics competency, which is the weakest of the four.
 *
 *   It is also the only remaining test of H4 besides the interview Hinglish quota:
 *   query_language came back "en" for all 142 audited posts, so the engine cannot
 *   test it. Q11 asks the respondent directly.
 *
 * VOCABULARY LOCK
 *   Every closed-choice answer below maps 1:1 onto engine/extract.py VOCAB, so survey
 *   responses merge into episodes.jsonl rather than sitting in a separate silo. The
 *   engine value is written in a comment beside each option block.
 *
 *   Two things in engine/import_survey.py are tied to the exact wording here:
 *     OPTIONS - matched against the START of each option's text
 *     COLUMNS - matched against a fragment of each QUESTION TITLE
 *   Both are cross-checked against this file by tests/test_import_survey.py, so
 *   reword freely and let the tests tell you what to update. Silently orphaning a
 *   column drops that answer for every respondent.
 *
 * LANGUAGE PASS (21 Sep)
 *   Simplified throughout: shorter options, no product jargon, the double negative
 *   in the consequence question removed, and the stated length raised from four
 *   minutes to five because sixteen questions was never four minutes.
 *   Wording only - no question was added, removed, or changed in what it measures.
 *
 * PILOT CUT (23 Sep) - edited by hand on the LIVE form after 5 responses
 *   The form under-measured "struggles to refine an unsuccessful search", one of
 *   the brief's four sample questions. Three edits, all mirrored below:
 *     1. NEW  "How many times did you search?" (optional), after the query question
 *     2. Q12  "Nothing came up, and I had no idea what to change" became
 *             "I didn't know what to try next" - the old wording overlapped with
 *             "got nothing back". Import still maps the old wording.
 *     3. Q13  two new options: searched again with other words; narrowed by a
 *             date, place or person
 *   The first 5 responses are the PILOT. Report them apart from the stage ranking.
 *   Do not re-run this script to apply edits: it creates a NEW form and link.
 *
 * HOW TO USE (about 2 minutes)
 *   1. script.google.com -> New project
 *   2. Delete the editor contents, paste this whole file
 *   3. Run. Approve the prompt (it only creates a form on your Drive)
 *   4. View -> Logs prints the LIVE and EDIT links
 */

function createSurvey() {
  var form = FormApp.create("Finding an old photo — 6 minutes");

  form.setDescription(
    "About six minutes. You do not share any photos, and nothing here identifies you.\n\n" +
      "It is about one thing: the times you know a photo is somewhere in your library, " +
      "and still cannot get it to come up.\n\n" +
      "An independent student project, not connected to Google or Apple. " +
      "Answers are only used together, and any quote stays anonymous.",
  );

  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setConfirmationMessage(
    "Thank you — this really helps.\n\n" +
      "If you said yes to a call, I will be in touch. Happy to share what I find " +
      "with anyone who took part.",
  );

  // ---------------------------------------------------------------- SECTION 1
  // Context and the two URR terms that are currently modelled.
  form
    .addSectionHeaderItem()
    .setTitle("How you use your photos")
    .setHelpText("Four quick questions.");

  // Q1 - segment. Mirrors screener Q1 so the two datasets can be pooled.
  form
    .addMultipleChoiceItem()
    .setTitle("Which app do you mainly use to look back at old photos?")
    .setHelpText("The one you actually open when you want to find something.")
    .setChoiceValues([
      "Google Photos",
      "Apple Photos / iCloud Photos",
      "Both, about equally",
      "Something else (Samsung Gallery, OneDrive, Amazon Photos…)",
    ])
    .setRequired(true);

  // Q2 - library size. Segment definition: 5,000+ is the brief's long-tenure user.
  form
    .addMultipleChoiceItem()
    .setTitle("Roughly how many photos and videos do you have?")
    .setHelpText("A guess is fine.")
    .setChoiceValues([
      "Under 1,000",
      "1,000–5,000",
      "5,000–20,000",
      "More than 20,000",
    ])
    .setRequired(true);

  // Q3 - MEASURES n-bar in URR = Expression x [1 - (1 - I x S x Rec x Rcv)^n-bar].
  // Currently a modelled slot. This is the only cheap way to measure it.
  form
    .addMultipleChoiceItem()
    .setTitle("How often do you go looking for a photo more than a year old?")
    .setChoiceValues([
      "Most weeks",
      "A few times a month",
      "A few times a year",
      "Almost never",
    ])
    .setRequired(true);

  // Q4 - MEASURES the Expression term: of people with a vague memory to chase,
  // how many start a search at all rather than scrolling or asking someone?
  form
    .addMultipleChoiceItem()
    .setTitle(
      "When you go looking for an old photo, what do you usually do first?",
    )
    .setHelpText("Whatever you actually do first, even if it rarely works.")
    .setChoiceValues([
      "Type something into the search bar", // Expression = yes
      "Scroll back through the timeline by date", // workaround: date_scroll
      "Open an album or a folder", // workaround: albums_or_folders
      "Look in WhatsApp, Drive or somewhere else", // workaround: other_app
      "Ask someone who might also have it",
    ]) // workaround: ask_someone
    .setRequired(true);

  // ---------------------------------------------------------------- GATE
  // Everything after this point is REQUIRED, which is only safe because people who
  // have never had the problem are routed straight to submit. Their answer is still
  // useful: it is the denominator for how common this is.
  //
  // The question sits alone on its page. Google Forms takes navigation from the last
  // branching question on a page, so keeping it alone removes any ambiguity.
  form.addPageBreakItem().setTitle("One quick check");

  var gate = form
    .addMultipleChoiceItem()
    .setTitle("Has this happened to you in the last year?")
    .setHelpText(
      "Looking for a photo you were sure existed, and struggling to find it.",
    )
    .setRequired(true);
  gate.setChoices([
    gate.createChoice("Yes", FormApp.PageNavigationType.CONTINUE),
    gate.createChoice(
      "Yes, but I do not remember when",
      FormApp.PageNavigationType.CONTINUE,
    ),
    gate.createChoice(
      "No, this has not happened to me",
      FormApp.PageNavigationType.SUBMIT,
    ),
  ]);

  // ---------------------------------------------------------------- SECTION 2
  // The core. One specific attempt, narrated in structured pieces.
  form
    .addPageBreakItem()
    .setTitle("Now think of ONE time it went wrong")
    .setHelpText(
      "Think of one recent time you looked for a photo you were sure existed, and could not " +
        "find it. Just that one time, not photo search in general.",
    );

  // Q5 - free text. Human colour, and the quote source for the deck.
  form
    .addParagraphTextItem()
    .setTitle("What were you trying to find?")
    .setHelpText(
      'A line or two. For example: "the photo of my medicine from when I was ill ' +
        'last year", or "the receipt from that shop in Goa".',
    )
    .setRequired(false);

  // Q6 -> asset_type. Directly tests H5 (utility photos with nothing to index).
  form
    .addMultipleChoiceItem()
    .setTitle("What kind of photo was it?")
    .setChoiceValues([
      "An ordinary photo — people, places, food, a pet", // photo
      "A screenshot", // screenshot
      "A photo of a document, receipt or bill", // document_receipt
      "A photo of medicine, a prescription or a label", // medicine_label
      "A video", // video
      "Something else",
    ]) // unknown
    .setRequired(true); // H5 - utility photos with nothing to index

  // Q7 - THE question. Maps to cues_retained. Tests H1 (episodic time) directly.
  // Long list, but checkboxes are fast and this is the highest-value answer on the form.
  form
    .addCheckboxItem()
    .setTitle("What did you still remember? Tick all that apply.")
    .setHelpText(
      "The most useful question here, so it is worth a few extra seconds.",
    )
    .setChoiceValues([
      'Roughly when it was — "last summer", "about two years ago"', // temporal_approx
      "The exact date", // exact_date
      "What was going on — a trip, a festival, being ill", // event_anchor
      "Where it was, and the name of the place", // place_named
      "Where it was, but not what the place is called", // place_unnamed
      "Who was with me", // who_with
      "What is in the picture — an object, food, a pet", // object
      "Words written inside the photo — a sign or a label", // text_in_image
      "A colour, or roughly what it looked like", // appearance_colour
      "Which phone or app it came from", // device_or_app_source
      "What happened just before or just after it", // sequence
      "A name or caption I had added to it myself",
    ]) // own_label_or_caption
    .setRequired(true); // H1 and the brief's core question

  // Q8 -> cues_lost. The other half of the brief's question: what has gone.
  form
    .addCheckboxItem()
    .setTitle("What had you forgotten? Tick all that apply.")
    .setChoiceValues([
      "When it was taken", // date
      "Where it was taken", // place
      "Which album or folder it is in", // album
      "Who was in it", // people
      "The exact words to search for", // exact_words
      "What the file was called",
    ]) // filename
    .setRequired(true); // the other half of the brief's question

  // Q9 -> query_verbatim. Gold for the deck: real query strings, not paraphrases.
  form
    .addParagraphTextItem()
    .setTitle("What exactly did you type into search?")
    .setHelpText(
      "The actual words, as best you remember, including anything you tried next. " +
        "Leave it blank if you never typed anything.",
    )
    .setRequired(false);

  // NEW (23 Sep, pilot cut) -> search_count. Survey-only. Separates giving up after
  // one try from trying repeatedly and failing, which point to different fixes (H3).
  form
    .addMultipleChoiceItem()
    .setTitle("How many times did you search?")
    .setChoiceValues([
      "Once", // once
      "2 or 3 times", // two_three
      "4 or more", // four_plus
      "Did not search", // none
    ])
    .setRequired(false); // added after 5 responses, so those rows are blank

  // Q10 -> query_language. THE ONLY remaining engine-side test of H4. The extraction
  // returned "en" for all 142 audited posts, so H4 is currently "not tested".
  form
    .addMultipleChoiceItem()
    .setTitle("When you search your photos, what language do you use?")
    .setChoiceValues([
      "English", // en
      "A mix of Hindi and English, in English letters", // hinglish_code_mixed
      "Hindi, in Devanagari", // hi
      "Another language", // other
      "I do not type — I scroll instead",
    ]) // no_query
    .setRequired(true); // the ONLY remaining test of H4

  // Q11 -> search_mode. Separates the Ask Photos era from classic search, which the
  // engine tracks via era labels but cannot attribute per-user.
  form
    .addMultipleChoiceItem()
    .setTitle("Were you using the AI answer or the normal search?")
    .setHelpText("Google Photos has both, with a switch on the search screen.")
    .setChoiceValues([
      "The AI one that answers in sentences", // ask_photos_or_ai
      "The normal keyword search", // classic
      "I tried both", // both_compared
      "I do not know which one it was",
    ]) // not_mentioned
    .setRequired(true); // separates the Ask Photos era

  // Q12 -> failure_stage. The single field the whole hypothesis ranking turns on.
  // Option order matches the URR decomposition: Expression, Interpretation,
  // Surfacing, Recognition, Recovery, then H6 and the catch-alls.
  form
    .addMultipleChoiceItem()
    .setTitle("What actually went wrong? Pick the closest one.")
    .setChoiceValues([
      "I did not know what to type", // cannot_express
      "I typed something, but got nothing back, or the wrong things", // system_misunderstood
      "The results looked reasonable, but mine was not there", // not_surfaced
      "Too many similar results to pick mine out", // cannot_evaluate_results
      "I didn't know what to try next", // cannot_refine  [H3] (reworded 23 Sep)
      "The album, folder or view I normally use had moved", // browse_path_changed [H6]
      "The app was too slow, or kept crashing", // slow_or_broken_ui
      "I gave up before getting that far",
    ]) // abandoned
    .setRequired(true); // the hypothesis ranking turns on this

  // NEW (21 Sep) - demand-side test of the MVP. The options are the Memory Trails
  // feature set, asked of people who have just described a real failure. Not an
  // engine field; survey-only.
  form
    .addCheckboxItem()
    .setTitle(
      "When a result looked close, what would have helped you check it? Tick all that apply.",
    )
    .setChoiceValues([
      "Photos taken just before or after it",
      "The date, or a rough date range",
      "Where it was taken, or which trip it was from",
      "Who else was in the nearby photos",
      "Any words or text in the image",
      "A short reason why it came up",
      "Nothing else would have helped",
    ])
    .setRequired(false);

  // Q13 -> workaround. Feeds the "existing user workarounds" item the brief requires
  // in Part 4, with a measured distribution instead of anecdote.
  form
    .addCheckboxItem()
    .setTitle("What did you do next? Tick all that apply.")
    .setChoiceValues([
      "Scrolled back through the timeline to about the right date", // date_scroll
      "Scrolled through everything", // manual_scroll
      "Dug through albums or folders", // albums_or_folders
      "Looked in WhatsApp, Drive, email or another app", // other_app
      "Asked someone else who might have it", // ask_someone
      "Switched to the normal search", // classic_search_toggle
      "Took the photo or got the document again", // (new: re-acquisition)
      "Searched again with other words", // requery (new 23 Sep)
      "Picked a date, place or person to narrow it down", // narrowed (new 23 Sep)
      "Gave up",
    ]) // gave_up
    .setRequired(true); // brief requires existing workarounds

  // Q14 -> outcome. Measured proxy for the URR numerator across all respondents.
  // The two middle options are the group the MVP is built for: the photo surfaced
  // and the person still could not tell. They land on outcome "unknown" in the
  // engine vocabulary, and import_survey derives retrieval_certainty from them.
  form
    .addMultipleChoiceItem()
    .setTitle("Did you find it in the end?")
    .setChoiceValues([
      "Yes, fairly quickly", // found_fast
      "Yes, but it took a long time", // found_slow
      "I found something similar, but was not sure it was right", // unknown + uncertain
      "I found the right trip or event, but not the exact photo", // unknown + uncertain
      "No, I never found it", // not_found
      "I stopped looking",
    ]) // not_found
    .setRequired(true); // URR numerator, and the exact/uncertain/failed split

  // Q15 - time cost. Not an engine field; this is the business-case number for the
  // "why solving it matters" item in Part 4, and it is measured rather than asserted.
  form
    .addMultipleChoiceItem()
    .setTitle("Roughly how long did you spend before you found it or gave up?")
    .setChoiceValues([
      "Under a minute",
      "1–5 minutes",
      "5–15 minutes",
      "More than 15 minutes",
      "I came back to it more than once, across days",
    ])
    .setRequired(false);

  // Q16 - consequence. Separates nostalgia loss from utility loss, which is the whole
  // case for the camera-as-filing-cabinet segment.
  form
    .addMultipleChoiceItem()
    .setTitle("Did this cause you any actual trouble?")
    .setChoiceValues([
      "No, just annoying",
      "Yes — I had to ask someone, or get the document again",
      "Yes — it cost me money, time off work, or a deadline",
      "I found it in the end, so no real harm",
    ])
    .setRequired(true); // utility loss vs nostalgia loss

  // ---------------------------------------------------------------- SECTION 3
  // NEW (21 Sep). Ask Photos is the incumbent answer to this problem, so the deck
  // has to say what it already solves and what it does not. Deliberately NOT
  // branched: Apps Script navigation cannot be tested from here, and an untested
  // branch on the form that gates recruitment is not worth the saved taps.
  form
    .addPageBreakItem()
    .setTitle("Ask Photos")
    .setHelpText(
      "Ask Photos is the newer Google Photos search that lets you ask in ordinary " +
        "sentences instead of keywords.\n\n" +
        "If you have never used it, answer the first two questions and leave the rest blank.",
    );

  form
    .addMultipleChoiceItem()
    .setTitle("Have you heard of Ask Photos?")
    .setChoiceValues([
      "Yes, and I have used it",
      "Yes, but I have not used it",
      "No, I had not heard of it",
      "I am not sure",
    ])
    .setRequired(true); // splits respondents for the Ask Photos comparison

  form
    .addCheckboxItem()
    .setTitle(
      "If you have not used it, what has kept you from trying Ask Photos?",
    )
    .setHelpText("Skip if you have used it.")
    .setChoiceValues([
      "I did not know about it",
      "I cannot get it where I am",
      "I do not know what to ask it",
      "The normal search is enough for me",
      "I would rather browse myself",
      "I worry about privacy or accuracy",
    ])
    .setRequired(false);

  form
    .addMultipleChoiceItem()
    .setTitle("If you have used it, how did Ask Photos work for you?")
    .setChoiceValues([
      "It found what I wanted quickly",
      "It helped after I asked again",
      "It showed related photos, but not the one I wanted",
      "It was wrong, or not useful",
      "I do not remember",
    ])
    .setRequired(false);

  form
    .addMultipleChoiceItem()
    .setTitle("What was the biggest problem with Ask Photos?")
    .setChoiceValues([
      "It did not understand my description",
      "Too many results, or unrelated ones",
      "I could not tell why it showed those results",
      "I could not correct it or narrow it down",
      "It was slow",
      "I did not have a problem",
    ])
    .setRequired(false);

  form
    .addCheckboxItem()
    .setTitle(
      "What would Ask Photos need to do better for memories that are hard to describe?",
    )
    .setChoiceValues([
      "Help me describe what I remember",
      "Show photos from the same trip or event",
      "Show photos taken just before and after",
      "Explain why a photo came up",
      "Help me carry on after a wrong result",
      "Work better with screenshots and documents",
      "It already works well for me",
    ])
    .setRequired(false);

  // ---------------------------------------------------------------- SECTION 4
  form
    .addPageBreakItem()
    .setTitle("Last thing")
    .setHelpText("Optional, then you are done.");

  form
    .addParagraphTextItem()
    .setTitle("Anything else about finding old photos we did not ask?")
    .setRequired(false);

  // Routes willing respondents into the interview funnel - this form doubles as a
  // low-friction top of funnel for recruitment, which is the late critical path.
  form
    .addMultipleChoiceItem()
    .setTitle("Would you be up for a call about this?")
    .setHelpText(
      "Your camera stays off for the hands-on part, and you never show your photos.",
    )
    .setChoiceValues(["Yes", "No thanks"])
    .setRequired(true);

  form
    .addTextItem()
    .setTitle("If yes — email or WhatsApp number")
    .setHelpText("Only used to send the invite, then deleted.")
    .setRequired(false);

  Logger.log("LIVE FORM  -> " + form.getPublishedUrl());
  Logger.log("EDIT FORM  -> " + form.getEditUrl());
  Logger.log(
    "Post the LIVE link to LinkedIn and the subreddits. Keep the SCREENER for personal network.",
  );
}
