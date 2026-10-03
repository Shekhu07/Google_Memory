# ⚠️ SYNTHETIC — persona walkthrough of the MVP test form (3 Oct)

**These are not users.** Five personas answer `mvp_test_form.gs` on paper so the form, the tasks and the
scoring sheet can be checked **before** real people see them. **None of this counts toward Part 6**
("return to at least 3 users"), none of it goes in `mvp-test-log.csv`, and no answer here may be quoted on a
slide as a person's words. On Slide 9 it may appear only as a labelled *cognitive walkthrough*.

**How each kind of answer was produced**

| Answer | Source | Trust |
|---|---|---|
| Segment question, own-Google-Photos page | The persona's **real survey record** (`survey:00NN`), re-expressed as form answers | Grounded, but it re-uses an old incident rather than a new search |
| What the prototype did | **Run against the live MVP** on 3 Oct (`/api/py/extract`, `/search`, `/episode`); each query is shown with the moment rank of the correct photo | Measured |
| Which features they'd use, sureness, comparisons | **Predicted** from the persona's survey behaviour and what the MVP returned | A guess, labelled as one. Themes only, no invented quotes |

---

## The five personas

| | Based on | Why this persona | In segment? |
|---|---|---|---|
| **A · Festival searcher, mixes Hindi and English** | `survey:0004`, typed *"wedding, pichle saal diwali"* | The H4 case; search misread their festival-plus-time query | ✅ event |
| **B · One-word typer who can't tell which** | `survey:0002`, typed *"gym"* | Recognition: reached results, couldn't tell which was theirs | ✅ event |
| **C · Scroller on another app** | `survey:0003`, Apple Photos, never knew what to type | Tests the skip for non-Google-Photos users | ✅ event |
| **D · Album opener who never types** | `survey:0011`, opened an album, no query | The Browse path from Slide 2 | ✅ event |
| **E · Document hunter, no sense of when** | `survey:0006`, typed *"medicine, bill"*, never found it | Outside the segment (no time memory); the real-trouble case | ❌ "didn't remember when" (O8) |

---

## What the live MVP actually returned (3 Oct)

| Query | Clues it read | Correct photo | Plain search (top 20) |
|---|---|---|---|
| *"cat pichle saal diwali"* | pet · Diwali 2025 | **moment 1, on the cover** | not found |
| *"cat"* | pet | **moment 1, on the cover** | not found |
| *"cat diwali"* | pet · Diwali 2025 (alt: or Diwali 2024) | **moment 1, on the cover** | not found |
| *"photo of my cat around diwali last year"* | pet · Diwali 2025 | **moment 1, on the cover** | not found |
| *"diwali"* | Diwali 2025 (alt: or Diwali 2024) | **moment 1, on the cover** | not found |
| *"cat october 2025"* | pet · October 2025 | **moment 1, on the cover** | not found |
| Task 2: *"the dog by a tree from the Diwali before that"* | pet · **Diwali 2025** (alt: or Diwali 2024) | **not shown** until the alternative is tapped | not found |
| Task 2: *"dog tree diwali 2024"* | pet · Diwali 2024 | **moment 1, on the cover** | not found |
| Task 2: *"dog pichle se pichle saal diwali"* | pet · **Diwali 2025, no alternative** | **not shown**, and no one-tap way to fix it | not found |

---

## Persona answers, question by question

### A · Festival searcher, mixes Hindi and English (`survey:0004`)

| Form question | Answer | Source |
|---|---|---|
| How did you remember WHEN? | By an event or festival | survey |
| Use Google Photos? | Yes, main app | survey |
| When, in your own words | "pichle saal Diwali, at the wedding" | survey query |
| Typed into Google Photos | `wedding, pichle saal diwali` | survey |
| What happened | Photos like it, but from other years or events | survey: misread |
| Could you see how it read your words? | No | predicted |
| Same words in Ask Photos | My app doesn't have it, or I didn't try (never heard of it) | survey |
| What found the last one you did find | Scrolling back through the timeline | survey workaround |
| Task 1 | Found it, sure (*"cat pichle saal diwali"*, moment 1) | **live MVP** |
| Task 2 | **Didn't find it** if typed *"dog pichle se pichle saal diwali"*: read as Diwali 2025 with no alternative | **live MVP** |
| Features used | Removed or changed a clue (trying to fix the year) | predicted |
| Sureness, comparison, would use | High sureness on Task 1; prototype easier; "every time" for festival photos | predicted theme |
| Likely change request | "It didn't understand *pichle se pichle saal*" | predicted from the live miss |

### B · One-word typer who can't tell which (`survey:0002`)

| Form question | Answer | Source |
|---|---|---|
| How did you remember WHEN? | By an event or festival | survey |
| Use Google Photos? | Yes, main app | survey |
| When, in your own words | "around when I started at the gym, last year" | predicted from cues |
| Typed into Google Photos | `gym` | survey |
| What happened | Lots of similar photos, couldn't tell which was mine | survey: couldn't evaluate |
| Could you see how it read your words? | No | predicted |
| Same words in Ask Photos | Didn't try (heard of it, never used) | survey |
| What found the last one you did find | Scrolling back through the timeline | survey workaround |
| Task 1 | Found it, sure (*"cat"* alone, moment 1) | **live MVP** |
| Task 2 | Found it **if** they tap "or Diwali 2024" (*"dog diwali"*) | **live MVP** |
| Features used | Picked a suggested alternative · "Why this moment?" | predicted (wanted before/after and date range in the survey) |
| Sureness, comparison, would use | Sure because the moment shows the photos around it; "only when normal search fails" | predicted theme |

### C · Scroller on another app (`survey:0003`)

| Form question | Answer | Source |
|---|---|---|
| How did you remember WHEN? | By an event or festival | survey |
| Use Google Photos? | **No** → skips the own-Google-Photos page | survey: Apple Photos |
| Task 1 | Found it, sure (*"photo of my cat around diwali last year"*, moment 1) | **live MVP** |
| Task 2 | Found it **if** they tap "or Diwali 2024" (*"the dog by a tree from the Diwali before that"*) | **live MVP** |
| Features used | "Around that time" (a scroller's habit) | predicted |
| Comparison with Google Photos | Skipped (doesn't use it) | form logic |
| Sureness, would use | High; would want it in their own app | predicted theme |

### D · Album opener who never types (`survey:0011`)

| Form question | Answer | Source |
|---|---|---|
| How did you remember WHEN? | By an event or festival | survey |
| Use Google Photos? | Yes, main app | survey |
| When, in your own words | "Diwali, a while back" | predicted from cues |
| Typed into Google Photos | `diwali` (the form asks them to search, though they never do) | predicted |
| What happened | Photos like it, but from other years | predicted |
| Could you see how it read your words? | No | predicted |
| Same words in Ask Photos | Didn't try (never heard of it) | survey |
| What found the last one you did find | An album or folder | survey first move |
| Task 1 | Found it, sure (*"diwali"*, moment 1) | **live MVP** |
| Task 2 | Found it if they tap "or Diwali 2024" | **live MVP** |
| Features used | Picked a suggested alternative | predicted |
| Risk to watch | May drop out at "type into Google Photos" (never searches) | predicted |

### E · Document hunter, no sense of when (`survey:0006`, outside the segment)

| Form question | Answer | Source |
|---|---|---|
| How did you remember WHEN? | **I didn't remember when at all** → reported separately, not one of the 3 | survey: no time cue |
| Use Google Photos? | Yes, main app (20,000+ photos) | survey |
| Typed into Google Photos | `medicine, bill` | survey |
| What happened | Photos like it, but not mine | survey: never surfaced |
| Same words in Ask Photos | Didn't try (heard of it) | survey |
| What found the last one you did find | I don't remember (got the document again) | survey consequence |
| Task 1 | Found it, sure (*"cat october 2025"*, moment 1) | **live MVP** |
| Task 2 | Found it (*"dog tree diwali 2024"*, moment 1) | **live MVP** |
| Likely change request | "Read the text in my photos" (receipts, medicine) | predicted; matches H5 and the OCR roadmap |

---

## What the walkthrough tells us before anyone real takes the test

1. **Task 1 has a ceiling.** Every phrasing found the target first, even the single word *"cat"*. All 5
   personas succeed, so Task 1 will show the flow works but won't separate testers. **Option:** make Task 1
   harder (e.g. a photo inside a moment that isn't on its cover), or keep it as the easy warm-up and let
   Task 2 carry the signal.
2. **Task 2 is where the learning is.** Success depends on one tap ("or Diwali 2024"). Expect a split
   between people who notice the alternative and people who don't. That is the clue-correction finding Slide 9 needs.
3. **A real parser gap: "pichle se pichle saal"** (the year before last) is read as last year, with **no
   alternative offered**. Persona A, the Hinglish searcher, cannot finish Task 2. Worth a fix before testing,
   or worth reporting as a found issue.
4. **Plain search never found the target** in its top 20 for any of the nine queries, Memory Trails found it
   first in seven. Measured on the live site, not a persona's opinion.
5. **Form flow:** persona C checks the Google Photos skip; persona D may stall at "type into Google Photos";
   persona E checks that out-of-segment people are reported separately.

**Not claimed here:** how real people feel about it, what they'd say, or whether they'd use it. Only the form
responses can tell you that.
