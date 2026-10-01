# Memory Trails: user test script (about 20 minutes per person)

**Goal:** can people who half-remember a photo get back to it with Memory Trails, and are they sure it's the right one?
**People:** at least 3. Survey respondents who said "yes" to a call are ideal.
**You need:** the participant on a call with screen share (phone or laptop), this script, and the recording sheet (`mvp-test-log.csv`).

---

## Before the call (2 min)

1. Give each person an ID: P01, P02, P03…
2. Send them this link (change the ID each time): `https://memory-trails-demo.vercel.app/?study=P01`
3. Check the top bar shows **"Study: P01"** and **"End session: copy log"**. (Checked: it works.)

---

## 1 · Open (2 min). Read this out

> "Thanks for helping. I'm testing an idea, not you, so there are no wrong answers. If something is confusing, that's the app's fault.
> Please think out loud as you go: say what you're looking at and what you're trying to do.
> What you type will be recorded as text for this study. No photos of yours are used. It's a demo library."

## 2 · Warm-up (3 min)

Ask, and write down their answers word for word:

1. "Think of the last time you looked for an old photo and struggled. What was it?"
2. "What did you remember about it, and what had you forgotten?"
3. "What did you type, or what did you do?"

## 3 · Task A: the main task (5 min max). Read it out; don't show the wording

> "Imagine you're looking for **the photo of the handmade cake from your sister's graduation**. You remember the event and what the photo looked like, but not the date or the album. Find it."

## 4 · Task B: a vague memory (5 min max)

> "Now imagine you're looking for **a photo of your dog from a while back**. That's all you remember. Find it."

This one is meant to be harder. If they don't find it, that's a useful result too.

**During both tasks:**
- **Don't help or explain.** If they're silent for about 30 seconds, ask: "What are you looking for right now?"
- **Stop at 5 minutes.** Say: "That's great, thanks, let's stop there."
- **Note:** whether they edit a clue, tap "Why this moment?", or use "Not this moment".

## 5 · Questions after the tasks (5 min)

Ask in this order. Don't suggest answers.

1. "In your own words, what did the app do with what you typed?"
2. "Was there a moment you didn't know what to do next? What did you do?"
3. "How sure are you that the photo you picked was the right one, from 1 to 5? Why?"
4. "Did you notice the ✓ marks, or 'Why this moment?'. Did they change what you did?"
5. "How is this different from how you normally look for old photos?"
6. "Would you want Google Photos to show you how it understood your words?"
7. "If you could change one thing, what would it be?"

## 6 · Close (1 min)

1. Tap **"End session: copy log"** and paste it into a note named `P01_session.json`.
2. Thank them.

---

## What to fill in after each person

One row per task in `mvp-test-log.csv`:

| Column | What to write |
|---|---|
| `participant` | P01 |
| `task` | A (cake) or B (dog) |
| `found_in_5min` | yes / no |
| `seconds` | time to tap "That's the one", or 300 if stopped |
| `wrong_confirm` | yes if they confirmed a photo that **wasn't** the target |
| `clue_edits` | how many clues they changed, added or removed |
| `opened_why` | yes / no: tapped "Why this moment?" |
| `used_not_this_moment` | yes / no |
| `sure_1to5` | their answer to question 3 |
| `best_quote` | one line they said, word for word |

**When you're done, send me the sheet and the session logs.** I'll fill slide 8 and the takeaway.

**The one rule:** if they confirm the wrong photo, write it down, even if it feels awkward. Wrong confirmations are the guardrail metric, and an honest count of 1 beats a hidden one.
