/**
 * Creates the MVP USER TEST as a self-serve Google Form (brief Part 6). No call needed.
 *
 * WHAT PART 6 ASKS, AND WHERE THIS FORM ANSWERS IT
 *   "at least 3 users from your target segment"  -> Page 1, one segment question
 *   "real or representative retrieval tasks"     -> Page 2: a REAL task in their own Google Photos
 *                                                  Page 3: a representative task in the prototype,
 *                                                  built from a real survey query ("pichle saal diwali")
 *   "document what you learned / would change"   -> Pages 3-4, then the scoring guide in
 *                                                  research/testing/mvp-test-script.md
 *
 * WHY PAGE 2 EXISTS (added 3 Oct): EVIDENCE ON WHAT GOOGLE PHOTOS GETS WRONG TODAY
 *   The deck's claims about the current app rest on public posts and a self-reported survey.
 *   Page 2 has each participant try one event-and-time search in their OWN library first, so
 *   the same person reports what Google Photos did and then what the prototype did. Each
 *   question closes a named gap:
 *     what happened               -> root cause, Slide 6: misread vs never surfaced vs can't tell
 *     could you see how it read   -> "no match explanation", Slide 7's case against Ask Photos
 *     the same words in Ask       -> plan §8b, the Ask Photos re-run, still open
 *     what actually got you there -> Slide 2's open question: does scrolling or search find it?
 *   It runs BEFORE the prototype so the prototype's wording cannot prime it.
 *
 * ALSO FIXED HERE: THE SURVEY'S MERGED ANSWER
 *   The retrieval survey merged "found the right trip" and "found something similar" into one
 *   "unsure" answer, which blocked a claim on Slides 5 and 7. Task 1's options keep them apart.
 *
 * WHAT A FORM LOSES, AND HOW IT IS RECOVERED
 *   Nobody watches, so the MVP's own study log stands in for the observer (?study=form). The
 *   participant taps "End session: copy log" and pastes it on Page 5. The log never contains
 *   typed text; it records clue edits, moments opened, "Why this moment?" views, time to
 *   confirm, and the photo_id of every confirmed photo. That is how wrong confirmations are
 *   counted without a facilitator:
 *     Task 1 (cat, last year's Diwali)        correct = demo:0372 or demo:0373 (Diwali 2025)
 *     Task 2 (dog by a tree, Diwali before)   correct = demo:0365 (Diwali 2024)
 *   Both checked by eye on 3 Oct. Think-aloud is lost. Say so on Slide 9.
 *
 *   ENTRY POINT (fixed 3 Oct): the MVP opens on a Photos library, not the describe screen.
 *   Memory Trails is the sparkle button ("Find a memory"); the Search tab is plain search, so the
 *   instructions name the sparkle button. A log with no memory_reentry_started event means the
 *   tester used plain search: score it as "wrong entry", not as a Memory Trails failure.
 *
 * TIME
 *   About 12 minutes: 3 in their own Google Photos, 5 at most in the prototype, 4 for the
 *   questions. People who don't use Google Photos skip Page 2 (about 9 minutes).
 *
 * HOW TO USE (about 2 minutes)
 *   1. script.google.com -> New project
 *   2. Delete the editor contents, paste this whole file
 *   3. Run createMvpTestForm. Approve the prompt (it only creates a form on your Drive)
 *   4. View -> Logs prints the LIVE and EDIT links
 *   Do not re-run to apply edits: it creates a NEW form and link. Edit the live form instead.
 */

var MVP_LINK = "https://memory-trails-v2.vercel.app/?study=form";

function createMvpTestForm() {
  var form = FormApp.create("Try a new way to find an old photo — 12 minutes");

  form.setDescription(
    "About twelve minutes. First you try one search in your own photo app, then a prototype " +
      "on a demo library of made-up photos, then a few questions.\n\n" +
      "You never share any of your photos, and nothing here identifies you. " +
      "The prototype never records the words you type.\n\n" +
      "An independent student project, not connected to Google. " +
      "It is the apps being tested, not you, so there are no wrong answers.",
  );
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setConfirmationMessage("Thank you, this really helps.");

  // ---------------------------------------------------------------- PAGE 1
  // Segment check in ONE question. The retrieval survey already asked about cues, library
  // size and frequency; it was anonymous, so its answers cannot be linked to this form.
  form
    .addMultipleChoiceItem()
    .setTitle(
      "Think of the last old photo you struggled to find. How did you remember WHEN it was?",
    )
    .setChoiceValues([
      "By an event or festival (a wedding, Diwali, a trip)",
      "Roughly (last winter, a couple of years ago)",
      "I knew the exact date",
      "I didn't remember when at all",
      "I haven't struggled to find a photo recently",
    ])
    .setRequired(true);

  var usesGooglePhotos = form
    .addMultipleChoiceItem()
    .setTitle("Do you use Google Photos?")
    .setRequired(true);

  // ---------------------------------------------------------------- PAGE 2
  // A real retrieval task in their own library: evidence on the current app.
  var ownAppPage = form
    .addPageBreakItem()
    .setTitle("One search in your own Google Photos (about 3 minutes)")
    .setHelpText(
      "1. Think of a photo, at least a year old, from a festival or event you can picture " +
        "(Diwali, a wedding, a birthday, a trip).\n" +
        "2. Open Google Photos and search for it the way you'd naturally say it, " +
        'for example "last Diwali", "pichle saal Holi", "my cousin\'s wedding".\n' +
        "3. Spend 2 minutes at most, then come back here.\n\n" +
        'You never share the photo. Use "cousin" or "friend" rather than names.',
    );

  form
    .addTextItem()
    .setTitle(
      "Before you searched: in your own words, WHEN was that photo taken?",
    )
    .setHelpText(
      'For example "the Diwali before Covid", "the summer we moved", "2022".',
    )
    .setRequired(false);

  form
    .addTextItem()
    .setTitle("What did you type into Google Photos?")
    .setHelpText("Exactly as you typed it.")
    .setRequired(true);

  // Options map onto the failure stages on Slide 2: found, surfaced late, misread
  // (other years / events), can't tell (recognition), nothing (misread or not surfaced).
  form
    .addMultipleChoiceItem()
    .setTitle("What happened?")
    .setChoiceValues([
      "The photo was on the first screen",
      "I found it after scrolling",
      "It showed photos like it, but from other years or other events",
      "It showed lots of similar photos and I couldn't tell which was mine",
      "It showed nothing, or nothing related",
    ])
    .setRequired(true);

  form
    .addMultipleChoiceItem()
    .setTitle(
      "Could you see how Google Photos understood your words, for example which dates it searched?",
    )
    .setChoiceValues(["Yes", "No", "Not sure"])
    .setRequired(true);

  form
    .addMultipleChoiceItem()
    .setTitle(
      'If your app has "Ask Photos" (an Ask button or a question box), try the same words there. What happened?',
    )
    .setChoiceValues([
      "It found the photo",
      "It showed related photos, but not the one",
      "Nothing useful",
      "My app doesn't have it, or I didn't try",
    ])
    .setRequired(true);

  form
    .addMultipleChoiceItem()
    .setTitle(
      "Think of the last time you DID find an old photo. What actually got you there?",
    )
    .setChoiceValues([
      "Searching",
      "Scrolling back through the timeline",
      "An album or folder",
      "Someone sent it to me",
      "I don't remember",
    ])
    .setRequired(true);

  // ---------------------------------------------------------------- PAGE 3
  var prototypePage = form
    .addPageBreakItem()
    .setTitle("Now try the prototype")
    .setHelpText(
      "1. Open this link (a phone or a laptop both work):\n" +
        MVP_LINK +
        "\n\n" +
        "It opens on a photo library of made-up photos, like a photo app.\n\n" +
        '2. Tap the ✦ sparkle button at the top ("Find a memory"). ' +
        "Please use that, not the Search tab at the bottom: the sparkle button is the new idea being tested.\n\n" +
        "3. Do this task:\n" +
        "Imagine you're looking for A PHOTO OF YOUR CAT FROM LAST YEAR'S DIWALI. " +
        "You don't remember the date, just that it was Diwali, last year. Find it.\n\n" +
        '4. Describe it however you like, tap "Continue", check the clues it picked up, then tap "Show moments". ' +
        "Open the moment you think it's in, tap the photo you mean, then tap \"That's the one\".\n" +
        "Spend 5 minutes at most. Not finding it is a useful answer too.\n\n" +
        "5. If you have time, try a second one: tap the ✦ sparkle button again and " +
        "find THE PHOTO OF THE DOG BY A TREE, FROM THE DIWALI BEFORE THAT.\n\n" +
        '6. Before you close the prototype, tap "End session: copy log" in the dark bar at the very top. ' +
        "You will paste it at the end of this form.\n\n" +
        "Then come back here.",
    );

  // People who don't use Google Photos skip Page 2.
  usesGooglePhotos.setChoices([
    usesGooglePhotos.createChoice("Yes, it's my main photo app", ownAppPage),
    usesGooglePhotos.createChoice("Yes, alongside another app", ownAppPage),
    usesGooglePhotos.createChoice("No", prototypePage),
  ]);

  // "Right Diwali, unsure which photo" and "something similar" are kept apart on purpose:
  // the survey merged them, which blocked a claim on Slides 5 and 7.
  form
    .addMultipleChoiceItem()
    .setTitle("Task 1, the cat from last year's Diwali: how did it go?")
    .setChoiceValues([
      "I found it and I'm sure it's the right one",
      "I found the right Diwali, but I wasn't sure which photo",
      "I picked something similar, but I'm not sure it's the right one",
      "I didn't find it",
      "I stopped before the end",
    ])
    .setRequired(true);

  form
    .addTextItem()
    .setTitle("What did you type first in the prototype?")
    .setHelpText(
      "Exactly as you typed it, if you remember. The prototype doesn't record this, so it only comes from you.",
    )
    .setRequired(false);

  form
    .addMultipleChoiceItem()
    .setTitle(
      "Task 2, the dog by a tree from the Diwali before that: how did it go?",
    )
    .setChoiceValues([
      "I found it and I'm sure it's the right one",
      "I picked one, but I'm not sure it's the right one",
      "I didn't find it",
      "I didn't try it",
    ])
    .setRequired(true);

  // Which features they found on their own. Labels are the MVP's on-screen wording (checked
  // 3 Oct), so people recognise them. The study log records use; this records noticing, and
  // the follow-up says which helped or confused. Untouched features are a finding too.
  form
    .addCheckboxItem()
    .setTitle("Did you use any of these in the prototype?")
    .setHelpText("Tick all that apply. It's fine if you used none of them.")
    .setChoiceValues([
      'Removed or changed a clue (the small labels showing what it understood, like "Diwali 2025")',
      'Picked a suggested alternative (like "or Diwali 2024")',
      '"Why this moment?"',
      '"Add one thing you remember"',
      '"Around that time" (moving to nearby months)',
      '"Not this moment"',
      '"Just outside your dates"',
      "None of these",
    ])
    .setRequired(false);

  form
    .addParagraphTextItem()
    .setTitle("Which of those helped most, or confused you?")
    .setRequired(false);

  // ---------------------------------------------------------------- PAGE 4
  form
    .addPageBreakItem()
    .setTitle("A few questions")
    .setHelpText("Short answers are fine.");

  form
    .addScaleItem()
    .setTitle("For Task 1, how sure are you that you picked the right photo?")
    .setBounds(1, 5)
    .setLabels("Not sure at all", "Completely sure")
    .setRequired(true);

  form
    .addParagraphTextItem()
    .setTitle("What made you sure, or not sure?")
    .setRequired(false);

  form
    .addParagraphTextItem()
    .setTitle(
      "In your own words, what did the prototype do with what you typed? Did it get anything wrong?",
    )
    .setRequired(true);

  // The head-to-head the deck needs, from the same person, minutes apart. Optional because
  // people who skipped Page 2 have nothing to compare against.
  form
    .addScaleItem()
    .setTitle(
      "Compared with searching Google Photos, finding a photo with the prototype was…",
    )
    .setHelpText("Skip this if you don't use Google Photos.")
    .setBounds(1, 5)
    .setLabels("Much harder", "Much easier")
    .setRequired(false);

  form
    .addParagraphTextItem()
    .setTitle(
      "What could the prototype do that Google Photos can't? And what does Google Photos do better?",
    )
    .setRequired(true);

  form
    .addParagraphTextItem()
    .setTitle(
      "If you could change one thing about the prototype, what would it be?",
    )
    .setRequired(true);

  form
    .addMultipleChoiceItem()
    .setTitle("If Google Photos worked like this, when would you use it?")
    .setChoiceValues([
      "Every time I look for an old photo",
      "Only when normal search doesn't work",
      "Rarely",
      "Never",
    ])
    .setRequired(true);

  // ---------------------------------------------------------------- PAGE 5
  form
    .addPageBreakItem()
    .setTitle("Last step")
    .setHelpText("Optional, but it helps a lot.");

  form
    .addParagraphTextItem()
    .setTitle("Paste the session log here")
    .setHelpText(
      'In the prototype, tap "End session: copy log", then paste here. ' +
        "It lists what you tapped and when, never the words you typed.",
    )
    .setRequired(false);

  Logger.log("LIVE FORM  -> " + form.getPublishedUrl());
  Logger.log("EDIT FORM  -> " + form.getEditUrl());
}
