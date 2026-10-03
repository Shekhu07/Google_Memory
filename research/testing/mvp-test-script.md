# Memory Trails: user test (self-serve Google Form, about 12 minutes)

**Brief, Part 6:** return to at least 3 users **from the target segment**, have them use the MVP on **real
or representative retrieval tasks from the research**, and **document what you learned and what you would
change next**.

**The form:** `research/testing/mvp_test_form.gs`. Run it at script.google.com; it prints the live link.
No call: participants open the prototype themselves, do the task, and answer in the form.

*Redrafted 3 Oct: a form instead of a call, at the user's request. Supersedes the tasks in
`mvp_test_protocol.md` §4. **Task fixed the same day:** the old task asked for "your dog from last
year's Diwali", but both Diwali 2025 pet photos are cats, so it had no right answer.*

---

## Who to send it to · *"from the target segment"*

Ideally the Part 3 interviewees ("return to"); next best, survey respondents who said yes to a call.
Send it to more than 3: a self-serve form loses people, and some won't fit the segment.

**Counts toward the 3 if** they answer the first question with **"By an event or festival"** or
**"Roughly"**. Report everyone else separately: "exact date" is out of the segment, "didn't remember
when" is the no-clue group (O8), and "haven't struggled recently" is not a recent case.

The form asks only this one question about them. The retrieval survey already covered cues, library size and
frequency, and it was anonymous, so its answers can't be linked to this form anyway.

## Page 2: one search in their own Google Photos · *"real retrieval tasks"*

Before the prototype, each Google Photos user searches their **own** library for a festival or event photo,
the way they'd naturally say it, then reports what happened. People who don't use Google Photos skip it.
This is the participant's version of `google-photos-probe-protocol.md`, run before the prototype so its
wording can't prime them.

## The tasks · *"representative retrieval tasks from the research"*

| Task | Wording in the form | Correct photo | Why this task |
|---|---|---|---|
| 1 | "a photo of your cat from last year's Diwali" | `demo:0372` or `demo:0373` (Diwali 2025) | A real survey query: *"wedding, pichle saal diwali"*. The segment's memory: an event, no date |
| 2 (optional) | "the photo of the dog by a tree, from the Diwali before that" | `demo:0365` (Diwali 2024) | Checks whether they correct a clue: the MVP first reads Diwali 2025 and offers "or Diwali 2024" |

Both checked against the live MVP on 3 Oct.

## Scoring each response

Fill one row per person in `mvp-test-log.csv`.

| Column | Where it comes from |
|---|---|
| `participant` | R01, R02… in the order responses arrive |
| `segment_fit` | the first question: yes (event or roughly) / no, with the option they chose |
| `task1_result` / `task2_result` | task 1: sure / right Diwali, unsure which photo / something similar / not found / stopped. Task 2: sure / unsure / not found / not tried |
| `task1_correct` / `task2_correct` | **from the log:** the first `retrieval_confirmed` event's `photo_id` is task 1, the second is task 2. Correct if it matches the table above |
| `wrong_confirm` | **yes** if any confirmed `photo_id` is not the right one. This is the guardrail; count every one |
| `seconds` | log `secondsToConfirm` (task 1) |
| `clue_edits` | log `summary.clueEdits` |
| `opened_why` | log `summary.evidenceViewed` > 0 |
| `sure_1to5` | the 1–5 sureness question |
| `vs_gp_1to5` | prototype vs Google Photos, 1 (much harder) to 5 (much easier) |
| `would_use` | every time / only when search fails / rarely / never |
| `gp_user` | "Do you use Google Photos?" |
| `gp_when_words` | how they'd say when it was, word for word |
| `gp_query` | what they typed into Google Photos, word for word |
| `gp_result` | first screen / after scrolling / other years or events / couldn't tell / nothing |
| `gp_showed_reading` | could they see how it understood their words: yes / no / not sure |
| `ask_result` | the same words in Ask Photos: found / related, not the one / nothing / no Ask or didn't try |
| `what_found_it` | the last time they did find an old photo, what got them there |
| `first_typed` | what they typed first in the prototype |
| `features_used` | the tick-box "Did you use any of these?", as a list. Compare with the log: ticked but not in the log means they noticed it without using it |
| `feature_note` | "Which of those helped most, or confused you?", word for word |
| `best_quote` | one line from Section 4, word for word |

**No log pasted?** Score from what they said only, and mark `task1_correct` as "unknown". Don't guess.

## Where each answer goes in the deck

| Answer | Feeds | What it can settle |
|---|---|---|
| Segment question | Slide 9 | Whether the testers are from the segment (the brief requires it) |
| `gp_result` | Slides 6 and 7 | Real-app evidence for the root cause: is an event-and-time search **misread** (other years or events), **never surfaced** (nothing), or **hard to evaluate** (couldn't tell)? Today this rests on public posts |
| `gp_showed_reading` | Slide 7 | Whether Google Photos shows how it read the query, the gap the prototype's clue chips and "Why this moment?" fill |
| `ask_result` | Slide 7, plan §8b | The Ask Photos comparison, still open. "Related, not the one" repeats the survey's finding |
| `what_found_it` | Slide 2 | The open question: does scrolling or searching actually find the photo? |
| `gp_when_words` vs `gp_query` | Slides 4 and 6 | Do people *say* when as an event, but *type* only a word? That's the gap between the memory and the query, in the participant's own words. Hinglish shows up here too (H4) |
| Task 1 result, split | Slides 5 and 7 | "Right Diwali, unsure which photo" vs "something similar": the split the survey couldn't make |
| `vs_gp_1to5`, the can/can't question | Slide 9 | A head-to-head from the same person, minutes apart, plus what Google Photos does better (an honest limit) |
| `would_use` | Slide 10 | Adoption intent: as an extra to search ("only when it fails") or a replacement |
| Wrong confirmations (log) | Slides 9 and 10 | The guardrail metric |

**Report counts, not percentages:** with 3–8 responses, "2 of 5" is honest and "40%" isn't.

## What you learned, and what you'd change · *"document"*

For each person, three lines:
1. **Learned:** the one thing this response tells us that we didn't know.
2. **Broke:** where they got stuck, or a wrong confirmation.
3. **Change:** one concrete change, and which answer it comes from.

**After all of them:** rank the changes by how many people hit each problem. The top 2–3 are Slide 9's
"next iteration".

**Say on Slide 9:** this was self-serve, so there was no think-aloud. What people did comes from the
prototype's log, and why they did it comes from what they wrote. Both are smaller than an observed
session, so report counts, not percentages.
