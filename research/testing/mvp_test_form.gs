/**
 * Creates the MVP USER TEST as a self-serve Google Form (brief Part 6). No call needed.
 *
 * WHAT PART 6 ASKS, AND WHERE THIS FORM ANSWERS IT
 *   "at least 3 users from your target segment"  -> Section 2, segment check
 *   "real or representative retrieval tasks"     -> Section 3, a task built from a real
 *                                                  survey query ("wedding, pichle saal diwali")
 *   "document what you learned / would change"   -> Section 4, then the analysis note in
 *                                                  research/testing/mvp-test-script.md
 *
 * WHAT A FORM LOSES, AND HOW IT IS RECOVERED
 *   Nobody watches, so the MVP's own study log stands in for the observer. The link opens
 *   study mode (?study=form). The participant taps "End session: copy log" and pastes it into
 *   Section 5. The log never contains typed text; it records clue edits, moments opened,
 *   "Why this moment?" views, time to confirm, and the photo_id of every confirmed photo.
 *   That photo_id is how wrong confirmations are counted without a facilitator:
 *     Task 1 (cat, last year's Diwali)        correct = demo:0372 or demo:0373 (Diwali 2025)
 *     Task 2 (dog by a tree, Diwali before)   correct = demo:0365 (Diwali 2024)
 *   Both checked by eye on 3 Oct. The old task said "dog"; both Diwali 2025 pets are cats.
 *   Think-aloud is lost. Say so on Slide 9.
 *
 * TIME
 *   About 10 minutes: under 1 for the segment question, 5 at most on the task, 3 for the questions.
 *
 * HOW TO USE (about 2 minutes)
 *   1. script.google.com -> New project
 *   2. Delete the editor contents, paste this whole file
 *   3. Run createMvpTestForm. Approve the prompt (it only creates a form on your Drive)
 *   4. View -> Logs prints the LIVE and EDIT links
 *   Do not re-run to apply edits: it creates a NEW form and link. Edit the live form instead.
 */

var MVP_LINK = "https://memory-trails-demo.vercel.app/?study=form";

function createMvpTestForm() {
  var form = FormApp.create("Try a new way to find an old photo — 10 minutes");

  form.setDescription(
    "About ten minutes. You try a prototype on a demo library of made-up photos, then answer a few questions.\n\n" +
      "You do not share any of your own photos, and nothing here identifies you. " +
      "The prototype never records the words you type.\n\n" +
      "An independent student project, not connected to Google. " +
      "It is the prototype being tested, not you, so there are no wrong answers.",
  );
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setConfirmationMessage("Thank you, this really helps.");

  // ---------------------------------------------------------------- SECTION 2
  // Segment check in ONE question. The retrieval survey already asked about cues, library
  // size and frequency; it was anonymous, so its answers cannot be linked to this form.
  // This question is the only thing the test needs: does the person remember roughly WHEN,
  // not the date? Kept distinct from the survey's tick-all cue question on purpose.
  form
    .addMultipleChoiceItem()
    .setTitle("Think of the last old photo you struggled to find. How did you remember WHEN it was?")
    .setChoiceValues([
      "By an event or festival (a wedding, Diwali, a trip)",
      "Roughly (last winter, a couple of years ago)",
      "I knew the exact date",
      "I didn't remember when at all",
      "I haven't struggled to find a photo recently",
    ])
    .setRequired(true);

  // ---------------------------------------------------------------- SECTION 3
  form
    .addPageBreakItem()
    .setTitle("Now try the prototype")
    .setHelpText(
      "1. Open this link (a phone or a laptop both work):\n" +
        MVP_LINK +
        "\n\n" +
        "2. Do this task:\n" +
        "Imagine you're looking for A PHOTO OF YOUR CAT FROM LAST YEAR'S DIWALI. " +
        "You don't remember the date, just that it was Diwali, last year. Find it.\n\n" +
        '3. Describe it however you like. When you find it, tap "That\'s the one".\n' +
        "Spend 5 minutes at most. Not finding it is a useful answer too.\n\n" +
        "4. If you have time, try a second one in the same window:\n" +
        "find THE PHOTO OF THE DOG BY A TREE, FROM THE DIWALI BEFORE THAT.\n\n" +
        '5. Before you close the prototype, tap "End session: copy log" at the top. ' +
        "You will paste it at the end of this form.\n\n" +
        "Then come back here.",
    );

  form
    .addMultipleChoiceItem()
    .setTitle("Task 1, the cat from last year's Diwali: how did it go?")
    .setChoiceValues([
      "I found it and I'm sure it's the right one",
      "I picked one, but I'm not sure it's the right one",
      "I didn't find it",
      "I stopped before the end",
    ])
    .setRequired(true);

  form
    .addTextItem()
    .setTitle("What did you type first?")
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

  // ---------------------------------------------------------------- SECTION 4
  form
    .addPageBreakItem()
    .setTitle("Four questions")
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

  form
    .addParagraphTextItem()
    .setTitle(
      "How is this different from how you normally look for old photos?",
    )
    .setRequired(true);

  form
    .addParagraphTextItem()
    .setTitle("If you could change one thing about it, what would it be?")
    .setRequired(true);

  // ---------------------------------------------------------------- SECTION 5
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
