/**
 * Creates the RETRIEVAL SURVEY as a real Google Form.
 *
 * This is NOT the interview screener. That is research/screener_form.gs and it stays
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
 *   Per rule D of SCORECARDS_AND_LESSONS.md, measured beats modelled for the Data
 *   and Metrics competency, which is the weakest of the four.
 *
 *   It is also the only remaining test of H4 besides the interview Hinglish quota:
 *   query_language came back "en" for all 142 audited posts, so the engine cannot
 *   test it. Q11 asks the respondent directly.
 *
 * VOCABULARY LOCK
 *   Every closed-choice answer below maps 1:1 onto engine/extract.py VOCAB, so survey
 *   responses merge into episodes.jsonl rather than sitting in a separate silo. The
 *   engine value is written in a comment beside each option block. DO NOT reword an
 *   option without updating the mapping in research/survey_design.md.
 *
 * HOW TO USE (about 2 minutes)
 *   1. script.google.com -> New project
 *   2. Delete the editor contents, paste this whole file
 *   3. Run. Approve the prompt (it only creates a form on your Drive)
 *   4. View -> Logs prints the LIVE and EDIT links
 */

function createSurvey() {
  var form = FormApp.create('Finding an old photo — 4-minute survey');

  form.setDescription(
    'Four minutes, no photos shared, nothing that identifies you.\n\n' +
    'This is about one specific thing: the times you KNOW a photo exists in your library ' +
    'and still cannot get it to come up.\n\n' +
    'Independent product case study. Not affiliated with Google or Apple. ' +
    'Answers are used in aggregate; any quote used is anonymous.');

  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setConfirmationMessage(
    'Thank you — this is genuinely useful. If you left your contact I will be in touch about the ' +
    '40-minute call. Happy to share what I find with anyone who took part.');

  // ---------------------------------------------------------------- SECTION 1
  // Context and the two URR terms that are currently modelled.
  form.addSectionHeaderItem()
    .setTitle('First, a bit about how you use your photo app')
    .setHelpText('Four quick ones.');

  // Q1 - segment. Mirrors screener Q1 so the two datasets can be pooled.
  form.addMultipleChoiceItem()
    .setTitle('Which app do you mainly use to look back at your photos?')
    .setHelpText('Whichever one you actually open when you want to find an old photo.')
    .setChoiceValues([
      'Google Photos',
      'Apple Photos / iCloud Photos',
      'Both, about equally',
      'Something else (Samsung Gallery, OneDrive, Amazon Photos…)'])
    .setRequired(true);

  // Q2 - library size. Segment definition: 5,000+ is the brief's long-tenure user.
  form.addMultipleChoiceItem()
    .setTitle('Roughly how many photos and videos do you have saved?')
    .setHelpText('A rough guess is completely fine.')
    .setChoiceValues(['Under 1,000', '1,000–5,000', '5,000–20,000', 'More than 20,000'])
    .setRequired(true);

  // Q3 - MEASURES n-bar in URR = Expression x [1 - (1 - I x S x Rec x Rcv)^n-bar].
  // Currently a modelled slot. This is the only cheap way to measure it.
  form.addMultipleChoiceItem()
    .setTitle('How often do you go looking for a photo that is more than a year old?')
    .setChoiceValues([
      'Most weeks',
      'A few times a month',
      'A few times a year',
      'Almost never'])
    .setRequired(true);

  // Q4 - MEASURES the Expression term: of people with a vague memory to chase,
  // how many start a search at all rather than scrolling or asking someone?
  form.addMultipleChoiceItem()
    .setTitle('When you go looking for an old photo, what do you usually do first?')
    .setHelpText('Your honest first move, not the one that works best.')
    .setChoiceValues([
      'Type something into the search bar',            // Expression = yes
      'Scroll back through the timeline by date',      // workaround: date_scroll
      'Open an album or a folder',                     // workaround: albums_or_folders
      'Look in WhatsApp, Drive or wherever else it might be',  // workaround: other_app
      'Ask someone who might also have it'])           // workaround: ask_someone
    .setRequired(true);

  // ---------------------------------------------------------------- SECTION 2
  // The core. One specific attempt, narrated in structured pieces.
  form.addPageBreakItem()
    .setTitle('Now think of ONE time it went wrong')
    .setHelpText(
      'Pick one recent time you went looking for a photo you were sure existed, and it was hard ' +
      'or impossible to find. One specific time — not photo search in general.\n\n' +
      'If that has never happened to you, skip to the end and submit. That is a useful answer too.');

  // Q5 - free text. Human colour, and the quote source for the deck.
  form.addParagraphTextItem()
    .setTitle('What were you trying to find?')
    .setHelpText('One or two lines. For example: "a photo of a medicine strip from when I was ill ' +
                 'last year" or "the receipt from the shop in Goa".')
    .setRequired(false);

  // Q6 -> asset_type. Directly tests H5 (utility photos with nothing to index).
  form.addMultipleChoiceItem()
    .setTitle('What kind of photo was it?')
    .setChoiceValues([
      'An ordinary photo — people, places, food, a pet',   // photo
      'A screenshot',                                       // screenshot
      'A photo of a document, receipt or bill',             // document_receipt
      'A photo of medicine, a prescription or a label',     // medicine_label
      'A video',                                            // video
      'Something else'])                                    // unknown
    .setRequired(false);

  // Q7 - THE question. Maps to cues_retained. Tests H1 (episodic time) directly.
  // Long list, but checkboxes are fast and this is the highest-value answer on the form.
  form.addCheckboxItem()
    .setTitle('What did you still remember about it? Tick everything that applies.')
    .setHelpText('This is the most important question here — take a few extra seconds on it.')
    .setChoiceValues([
      'Roughly when it was — "last summer", "about two years ago"',   // temporal_approx
      'The exact date',                                                // exact_date
      'What was going on — a trip, a festival, being ill, a wedding',  // event_anchor
      'Where it was, and the name of the place',                       // place_named
      'Where it was, but not what the place is called',                // place_unnamed
      'Who was with me',                                               // who_with
      'What is in the picture — an object, food, a pet',               // object
      'Words written inside the photo — a sign, a label, a document',  // text_in_image
      'A colour, or roughly what it looked like',                      // appearance_colour
      'Which phone or app it came from',                               // device_or_app_source
      'What happened just before or just after it',                    // sequence
      'A name or caption I had added to it myself'])                   // own_label_or_caption
    .setRequired(false);

  // Q8 -> cues_lost. The other half of the brief's question: what has gone.
  form.addCheckboxItem()
    .setTitle('And what had you forgotten? Tick everything that applies.')
    .setChoiceValues([
      'When it was taken',            // date
      'Where it was taken',           // place
      'Which album or folder it is in',  // album
      'Who was in it',                // people
      'The exact words to search for', // exact_words
      'What the file was called'])     // filename
    .setRequired(false);

  // Q9 -> query_verbatim. Gold for the deck: real query strings, not paraphrases.
  form.addParagraphTextItem()
    .setTitle('What exactly did you type into search?')
    .setHelpText('The actual words, as close as you can remember — including anything you tried ' +
                 'second or third. Leave blank if you never typed anything.')
    .setRequired(false);

  // Q10 -> query_language. THE ONLY remaining engine-side test of H4. The extraction
  // returned "en" for all 142 audited posts, so H4 is currently "not tested".
  form.addMultipleChoiceItem()
    .setTitle('When you type into photo search, what language do you use?')
    .setChoiceValues([
      'English',                                         // en
      'A mix of Hindi and English, typed in English letters',  // hinglish_code_mixed
      'Hindi, in Devanagari',                            // hi
      'Another language',                                // other
      'I do not type — I scroll or browse'])             // no_query
    .setRequired(false);

  // Q11 -> search_mode. Separates the Ask Photos era from classic search, which the
  // engine tracks via era labels but cannot attribute per-user.
  form.addMultipleChoiceItem()
    .setTitle('Were you using the AI answer or the normal search?')
    .setHelpText('Google Photos now has both, with a toggle on the search screen.')
    .setChoiceValues([
      'The AI one (Ask Photos / Gemini)',   // ask_photos_or_ai
      'The normal keyword search',          // classic
      'I tried both',                       // both_compared
      'I do not know which one I was using'])  // not_mentioned
    .setRequired(false);

  // Q12 -> failure_stage. The single field the whole hypothesis ranking turns on.
  // Option order matches the URR decomposition: Expression, Interpretation,
  // Surfacing, Recognition, Recovery, then H6 and the catch-alls.
  form.addMultipleChoiceItem()
    .setTitle('What actually went wrong? Pick the closest one.')
    .setChoiceValues([
      'I did not know what to type — I could not put the memory into words',  // cannot_express
      'I typed something, but got nothing back or completely wrong results',  // system_misunderstood
      'The results looked reasonable, but my photo just was not among them',  // not_surfaced
      'Too many similar results — it may have been there but I could not spot it',  // cannot_evaluate_results
      'Nothing came up, and I had no idea what to change or try next',        // cannot_refine  [H3]
      'The album, folder or view I normally use had moved or disappeared',    // browse_path_changed [H6]
      'The app was too slow, or kept crashing',                               // slow_or_broken_ui
      'I gave up before getting that far'])                                   // abandoned
    .setRequired(false);

  // Q13 -> workaround. Feeds the "existing user workarounds" item the brief requires
  // in Part 4, with a measured distribution instead of anecdote.
  form.addCheckboxItem()
    .setTitle('What did you do next? Tick everything you tried.')
    .setChoiceValues([
      'Scrolled back through the timeline to roughly the right date',  // date_scroll
      'Scrolled through everything',                                    // manual_scroll
      'Dug through albums or folders',                                  // albums_or_folders
      'Looked in WhatsApp, Drive, email or another app',                // other_app
      'Asked someone else who might have it',                           // ask_someone
      'Switched to the classic / non-AI search',                        // classic_search_toggle
      'Took the photo or got the document again',                       // (new: re-acquisition)
      'Gave up'])                                                        // gave_up
    .setRequired(false);

  // Q14 -> outcome. Measured proxy for the URR numerator across all respondents.
  form.addMultipleChoiceItem()
    .setTitle('Did you find it in the end?')
    .setChoiceValues([
      'Yes, fairly quickly',              // found_fast
      'Yes, but it took a long time',     // found_slow
      'No, I never found it',             // not_found
      'I am still not sure whether it is in there'])  // unknown
    .setRequired(false);

  // Q15 - time cost. Not an engine field; this is the business-case number for the
  // "why solving it matters" item in Part 4, and it is measured rather than asserted.
  form.addMultipleChoiceItem()
    .setTitle('Roughly how long did you spend before you found it or stopped?')
    .setChoiceValues([
      'Under a minute',
      '1–5 minutes',
      '5–15 minutes',
      'More than 15 minutes',
      'I came back to it more than once, across days'])
    .setRequired(false);

  // Q16 - consequence. Separates nostalgia loss from utility loss, which is the whole
  // case for the camera-as-filing-cabinet segment.
  form.addMultipleChoiceItem()
    .setTitle('Did not finding it cause you any actual trouble?')
    .setChoiceValues([
      'No, it was just annoying',
      'Yes — I had to ask someone or get the document again',
      'Yes — it cost me money, time off work, or a deadline',
      'I found it eventually, so no real harm'])
    .setRequired(false);

  // ---------------------------------------------------------------- SECTION 3
  form.addPageBreakItem()
    .setTitle('Last thing')
    .setHelpText('Optional, and then you are done.');

  form.addParagraphTextItem()
    .setTitle('Anything else about finding old photos that this form did not ask?')
    .setRequired(false);

  // Routes willing respondents into the interview funnel - this form doubles as a
  // low-friction top of funnel for recruitment, which is the late critical path.
  form.addMultipleChoiceItem()
    .setTitle('Would you be up for a 40-minute video call about this?')
    .setHelpText('Your camera stays off for the hands-on part and you never show your photos.')
    .setChoiceValues(['Yes', 'No thanks'])
    .setRequired(true);

  form.addTextItem()
    .setTitle('If yes — email or WhatsApp number')
    .setHelpText('Used only to send the invite, and deleted after the study.')
    .setRequired(false);

  Logger.log('LIVE FORM  -> ' + form.getPublishedUrl());
  Logger.log('EDIT FORM  -> ' + form.getEditUrl());
  Logger.log('Post the LIVE link to LinkedIn and the subreddits. Keep the SCREENER for personal network.');
}
