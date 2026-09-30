/**
 * Creates the interview screener as a real Google Form.
 *
 * HOW TO USE (about 2 minutes)
 *   1. Go to script.google.com -> New project
 *   2. Delete whatever is in the editor, paste this whole file
 *   3. Press Run. Approve the permission prompt (it only creates a form on your Drive)
 *   4. Open View -> Logs. It prints two links:
 *        LIVE FORM  -> paste this into [FORM LINK] in research/recruitment/recruitment.md
 *        EDIT FORM  -> for tweaking wording later
 *
 * Mirrors the screener in research/recruitment/recruitment.md: 9 questions, plus the Part 6 follow-up
 * question added 28 Sep (re-dated 1 Oct). Every extra question
 * costs responses, so resist adding more: the funnel needs ~25-30 responses to
 * yield 6 interviews.
 *
 * COMPENSATION is not mentioned. If you decide to offer it, uncomment the line
 * marked COMPENSATION below before running.
 */

function createScreener() {
  var form = FormApp.create('Finding old photos — 2-minute screener');

  form.setDescription(
    'Two minutes. I am looking for people who have had trouble finding an old photo in Google ' +
    'Photos, for a 40-minute conversation between 2 and 4 October.\n\n' +
    'Some people will also be asked back for a short 15-minute follow-up between 3 and 5 October, ' +
    'to try an early prototype and tell me what is confusing. That part is optional.\n\n' +
    'You will never share or show your photos. For the hands-on part your camera stays off and ' +
    'you run the searches yourself on your own phone — I only hear what you typed and what came back.\n\n' +
    'This is an independent product case study. It is not affiliated with Google. Your contact ' +
    'details are used only to send the invite and are deleted after the study. Nothing that ' +
    'identifies you appears in the write-up.'
    // COMPENSATION: + '\n\nAs a thank-you, participants receive a ₹500 voucher.'
  );

  form.setCollectEmail(false);          // Q9 asks for contact explicitly instead
  form.setProgressBar(true);
  form.setConfirmationMessage(
    'Thank you. If you fit what I am looking for I will message you with a slot within a day or two. ' +
    'Happy to share what I find with everyone who takes part.');

  // Q1 — which app. Qualifies: Google Photos, or both. This has to come first:
  // asking "how long have you used Google Photos" presupposes that they do.
  // "Both" is a qualifier and is actually the most interesting answer - those
  // participants can compare the two directly.
  form.addMultipleChoiceItem()
    .setTitle('Which app do you mainly use to look back at your photos?')
    .setHelpText('Whichever one you actually open when you want to find an old photo.')
    .setChoiceValues([
      'Google Photos',
      'Apple Photos / iCloud Photos',
      'Both, about equally',
      'Something else (Samsung Gallery, OneDrive, Amazon Photos…)'
    ])
    .setRequired(true);

  // Q2 — tenure. Qualifies: 2+ years
  form.addMultipleChoiceItem()
    .setTitle('How long have you been using it?')
    .setChoiceValues(['Less than a year', '1–2 years', '2+ years'])
    .setRequired(true);

  // Q3 — library size. Qualifies: 5,000+
  form.addMultipleChoiceItem()
    .setTitle('Roughly how many photos and videos are in your library?')
    .setHelpText('Google Photos → Settings shows this. A rough guess is fine.')
    .setChoiceValues(['Under 1,000', '1,000–5,000', '5,000–20,000', 'More than 20,000'])
    .setRequired(true);

  // Q4 — the actual qualifying event. Qualifies: Yes
  form.addMultipleChoiceItem()
    .setTitle('In the last 3 months, have you searched for a specific older photo and either ' +
              'failed to find it, or taken far longer than you expected?')
    .setChoiceValues(['Yes', 'No', 'I cannot remember'])
    .setRequired(true);

  // Q5 — THE question. A concrete answer here is the best predictor of a usable interview.
  form.addParagraphTextItem()
    .setTitle('If yes — what were you looking for, and what did you type?')
    .setHelpText('One or two lines is plenty. For example: "a photo of a medicine strip from when ' +
                 'I was ill last year — I typed medicine, then tablet, and got nothing." ' +
                 'This is the most useful answer on the form.')
    .setRequired(false);

  // Q6 — H4 quota: at least 3 of 6 participants should mix Hindi and English
  form.addMultipleChoiceItem()
    .setTitle('Day to day, do you mix Hindi and English when you type or talk?')
    .setChoiceValues(['Mostly English', 'A mix of both', 'Mostly Hindi'])
    .setRequired(true);

  // Q7 — balance, not a filter
  form.addMultipleChoiceItem()
    .setTitle('Which phone do you mainly use?')
    .setChoiceValues(['Android', 'iPhone', 'Both'])
    .setRequired(true);

  // Q8 — slots. All times IST.
  form.addCheckboxItem()
    .setTitle('Which of these 40-minute slots could work for you? (pick every one that does)')
    .setHelpText('All times are IST. The more you pick, the easier it is to find a fit.')
    .setChoiceValues([
      'Fri 2 Oct (holiday) · 11 AM–1 PM',
      'Fri 2 Oct (holiday) · 4–6 PM',
      'Fri 2 Oct · 8–10 PM',
      'Sat 3 Oct · 10 AM–12 PM',
      'Sat 3 Oct · 4–6 PM',
      'Sat 3 Oct · 8–10 PM',
      'Sun 4 Oct · 10 AM–12 PM',
      'None of these, but I am interested'
    ])
    .setRequired(true);

  // Q9 — Part 6 follow-up. The brief asks for at least 3 of the SAME target users to
  // come back and try the MVP, so ask now rather than chase people later.
  form.addMultipleChoiceItem()
    .setTitle('Would you be open to a 15-minute follow-up between 3 and 5 October, to try an ' +
              'early prototype?')
    .setHelpText('Optional extra. You would use a demo on your own phone with sample photos, not yours.')
    .setChoiceValues(['Yes', 'Maybe', 'No, just the conversation'])
    .setRequired(true);

  // Q10 — contact
  form.addTextItem()
    .setTitle('Email or WhatsApp number, so I can send the invite')
    .setHelpText('Used only to send the invite, and deleted after the study.')
    .setRequired(true);

  Logger.log('LIVE FORM  -> ' + form.getPublishedUrl());
  Logger.log('EDIT FORM  -> ' + form.getEditUrl());
  Logger.log('Paste the LIVE FORM link into [FORM LINK] in research/recruitment/recruitment.md (3 places).');
}
