# Memory Trails: user test script (10 minutes per person)

**Brief, Part 6:** return to at least 3 users **from the target segment**, have them use the MVP on **real
or representative retrieval tasks from the research**, and **document what you learned and what you would
change next**. Each section is tagged with the part of that sentence it serves.

**Goal:** can people who remember roughly *when* a photo was, but not the date, get back to it with
Memory Trails, and are they sure it's the right one?

**People:** at least 3, ideally from the Part 3 interviews. Survey respondents who said yes to a call are next best.
**You need:** a call with screen share (phone or laptop), this script, and `mvp-test-log.csv`.
**Not in this test:** plain search vs Memory Trails. The offline benchmark already measures that (soft
recall@20 0.866 vs 0.172 on held-out real phrasing), so the live test spends its 10 minutes on whether people can use the flow.

*Redrafted 3 Oct for a 10-minute session. Supersedes the tasks in `mvp_test_protocol.md` §4; its rubric (§5) still applies.*

---

## Before the call

Send the link with their ID: `https://memory-trails-demo.vercel.app/?study=P01`. Check the top bar shows
**"Study: P01"** and **"End session: copy log"**.

## 1 · Open and segment check (2 min) · *"from the target segment"*

> "Thanks. I'm testing an idea, not you, so there are no wrong answers. Please think out loud.
> What you type is recorded as text for this study; it's a demo library, not your photos."

1. "Have you looked for an old photo in the last few months and struggled to find it?"
2. "What did you remember about it? And how would you say *when* it was?" *(Don't offer options. Note
   whether they say an event or rough time, e.g. "last Diwali", or an exact date.)*
3. "About how many photos are in your library?"

**Fits the segment if:** a recent struggle **and** they remembered a rough time or event, not the date
(5,000+ photos is a plus). Record `segment_fit` = yes / partly / no. Test "partly" anyway; report them separately.

## 2 · The task (5 min max) · *"representative retrieval tasks from the research"*

Read it out; don't show the wording. It's built from a real survey query, *"wedding, pichle saal diwali"*.

> "You're looking for **a photo of your dog from last year's Diwali**. You don't remember the date, just
> that it was Diwali, last year. Find it."

*If they find it within 2 minutes, add:* "Now find one from **the Diwali before that**." *(The library has
two Diwalis a year apart. Watch whether they correct a clue or start over.)*

*If their own memory from Q2 matches the library (a festival, a trip, a wedding, a pet), you may use it
instead, in their own words.*

**While they work:** don't help. After 30 seconds of silence, ask "What are you looking for right now?"
Stop at 5 minutes. **Note:** the first words they type, clue edits, whether they open "Why this moment?",
and **whether they confirm a photo that isn't the target**.

## 3 · Four questions (2 min) · *"what you learned"*

1. "How sure are you that's the right photo, from 1 to 5? What made you sure, or not sure?"
2. "In your own words, what did the app do with what you typed? Did it get anything wrong?"
3. "How is this different from how you normally look for old photos?"
4. "If you could change one thing, what would it be?"

## 4 · Close (under 1 min)

Tap **"End session: copy log"**, paste it into `research/testing/sessions/P01_session.json`, and thank them.

---

## After each person: fill one row in `mvp-test-log.csv`

| Column | What to write |
|---|---|
| `participant` | P01 |
| `segment_fit` | yes / partly / no |
| `task` | diwali, diwali_before (the follow-up), or own |
| `found_in_5min` | yes / no |
| `seconds` | time to tap "That's the one", or 300 if stopped |
| `wrong_confirm` | yes if they confirmed a photo that **wasn't** the target |
| `clue_edits` | how many clues they changed, added or removed |
| `opened_why` | yes / no |
| `sure_1to5` | their answer to question 1 |
| `best_quote` | one line they said, word for word |

**Debrief, 3 lines, written right after** · *"what you would change next"*
1. **Learned:** the one thing this person showed us.
2. **Broke:** where they got stuck or confirmed the wrong photo.
3. **Change:** one concrete change, and which observation it comes from.

**After all 3:** rank the changes by how many people hit each problem. The top 2–3 are Slide 9's "next iteration".

**The one rule:** if they confirm the wrong photo, write it down. Wrong confirmations are the guardrail
metric, and an honest count of 1 beats a hidden one.
