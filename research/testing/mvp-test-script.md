# Memory Trails: user test (self-serve Google Form, about 10 minutes)

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
| `task1_result` / `task2_result` | the person's answer: sure / unsure / not found / stopped (task 2: or not tried) |
| `task1_correct` / `task2_correct` | **from the log:** the first `retrieval_confirmed` event's `photo_id` is task 1, the second is task 2. Correct if it matches the table above |
| `wrong_confirm` | **yes** if any confirmed `photo_id` is not the right one. This is the guardrail; count every one |
| `seconds` | log `secondsToConfirm` (task 1) |
| `clue_edits` | log `summary.clueEdits` |
| `opened_why` | log `summary.evidenceViewed` > 0 |
| `sure_1to5` | Section 4, the 1–5 question |
| `first_typed` | Section 3, what they typed first |
| `best_quote` | one line from Section 4, word for word |

**No log pasted?** Score from what they said only, and mark `task1_correct` as "unknown". Don't guess.

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
