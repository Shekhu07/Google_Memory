# MVP test form: 5 personas (synthetic, for a dry run)

> **⚠️ These are not test participants.** They predict how five real survey respondents would answer the live MVP test form, *"Try a new way to find an old photo — 12 minutes"* ([form](https://docs.google.com/forms/d/e/1FAIpQLSec7si5Wff2CYzHBNoQXaU_WPACot5FhkQO57CTQHir1zUIrg/viewform)).
> - **Don't submit them to the form or add them to `mvp-test-log.csv`.** They don't count toward Part 6 ("at least 3 users").
> - On a slide, they can only appear as a labelled *cognitive walkthrough*. Never quote them as a person's words.
>
> **Two good uses:**
> 1. Dry-run the form and the tasks before sending it.
> 2. Send the real form to these same five respondents (all said yes to follow-up), then score each prediction.

**Checked against the live form (3 Oct):** all 25 items, the wording, the options and the page-2 skip match `mvp_test_form.gs`. The edit link and the public link are the same form.

**Where each answer comes from**

| Tag | Meaning |
|---|---|
| **S** | Their real survey answer (`data/interim/survey_episodes.jsonl`) |
| **M** | Measured on the live MVP, 3 Oct (see `synthetic-walkthrough.md`) |
| **P** | Predicted. A guess, written as a theme, not a quote |

---

## The five at a glance

| | Persona | Survey record | What they test in the form | Counts toward the 3? |
|---|---|---|---|---|
| **A** | **Diwali-and-wedding searcher** (mixes Hindi and English) | `0004` | Search misreading a festival plus "last year"; parsing Hinglish | ✅ event |
| **B** | **Gym regular who types one word** | `0002` | Can't tell look-alike photos apart (recognition) | ✅ event |
| **C** | **Apple Photos scroller** | `0003` | The skip past page 2 for people who don't use Google Photos | ✅ event |
| **D** | **Album browser who never types** | `0011` | The browse path; may stall at "type into Google Photos" | ✅ event |
| **E** | **Bill-and-medicine hunter** | `0006` | Out-of-segment handling (no sense of *when*); the real-cost case | ❌ "didn't remember when" |

---

## Persona cards

### A · Diwali-and-wedding searcher · `survey:0004`
- **Library:** Google Photos, 5,000–20,000 items. Looks for old photos a few times a year, more around festivals. **S**
- **Remembers:** the event, roughly when, and who was there. **Forgets:** the date and the album. **S**
- **Searches like this:** `wedding, pichle saal diwali` (Hindi–English mix), 2–3 tries, then scrolls or asks someone. **S**
- **What went wrong:** search misread the query. **S** Never heard of Ask Photos. **S**
- **Wants:** to see the place or trip and who else was nearby. **S**
- **Risk in the test:** Task 2 in Hinglish (*"pichle se pichle saal"*) is read as last year, with no other year offered. **M**

### B · Gym regular who types one word · `survey:0002`
- **Library:** Google Photos, 5,000–20,000 items. Looks for old photos a few times a month. **S**
- **Remembers:** roughly when, the event, an object. **Forgets:** the date and the exact words. **S**
- **Searches like this:** `gym`, 2–3 tries, then scrolls to about the date. **S**
- **What went wrong:** got results but couldn't tell which was theirs. **S** Has heard of Ask Photos; normal search feels enough. **S**
- **Wants:** the photos just before and after, and a date range. **S**

### C · Apple Photos scroller · `survey:0003`
- **Library:** Apple Photos / iCloud, 5,000–20,000 items. Looks a few times a month. **S**
- **Remembers:** roughly when, and the event. **S**
- **Searches like this:** doesn't type; scrolls the timeline to about the date and usually finds it in 1–5 minutes. **S**
- **What went wrong:** didn't know what to type. **S**
- **Wants:** photos before and after, a date range, the place or trip. **S**

### D · Album browser who never types · `survey:0011`
- **Library:** Google Photos, 1,000–5,000 items. Looks a few times a year. **S**
- **Remembers:** the event and roughly when (*"vacation photos from last year"*). **Forgets:** who was there. **S**
- **Searches like this:** opens an album, then scrolls. Never types a query. **S**
- **What went wrong:** didn't know what to type. **S** Never heard of Ask Photos. **S**
- **Wants:** photos before and after, the place or trip. **S**

### E · Bill-and-medicine hunter · `survey:0006` (outside the segment)
- **Library:** Google Photos, 20,000+ items. Looks a few times a month. **S**
- **Remembers:** what's in the photo and words printed on it. **No sense of when.** **S**
- **Searches like this:** `medicine, bill`, 4+ tries, 15+ minutes. Then looked in another app and got the document again. **S**
- **What went wrong:** the photo never came up. **S** Has heard of Ask Photos but doesn't know what to ask it. **S**
- **Wants:** a date range, and search by the words inside the image. **S**

---

## Predicted answers, question by question

`–` means the form skips that question for them.

### Page 1 · Who they are

| Question | A | B | C | D | E |
|---|---|---|---|---|---|
| How did you remember WHEN? | By an event or festival **S** | By an event or festival **S** | By an event or festival **S** | By an event or festival **S** | **I didn't remember when at all** **S** |
| Use Google Photos? | Yes, main app **S** | Yes, main app **S** | **No** → skips page 2 **S** | Yes, main app **S** | Yes, main app **S** |

### Page 2 · One search in their own Google Photos

| Question | A | B | C | D | E |
|---|---|---|---|---|---|
| When, in your own words | pichle saal Diwali, at the wedding **S** | around when I started at the gym, last year **P** | – | the vacation last year **S** | doesn't know **S** |
| What they typed | `wedding, pichle saal diwali` **S** | `gym` **S** | – | `vacation` (a first-ever search) **P** | `medicine, bill` **S** |
| What happened | Photos like it, but from other years or events **S** | Lots of similar photos, couldn't tell which was mine **S** | – | Photos like it, but from other years **P** | Nothing, or nothing related **S** |
| Could you see how it read your words? | No **P** | No **P** | – | No **P** | No **P** |
| Same words in Ask Photos | Doesn't have it / didn't try **S** | Didn't try **S** | – | Didn't try **S** | Didn't try **S** |
| What got you there last time | Scrolling the timeline **S** | Scrolling the timeline **S** | – | An album or folder **S** | I don't remember **S** |

### Page 3 · The prototype

| Question | A | B | C | D | E |
|---|---|---|---|---|---|
| First typed | `cat pichle saal diwali` | `cat` | `photo of my cat around diwali last year` | `diwali` | `cat october 2025` |
| Task 1 (cat, last Diwali) | Found, sure (on the cover of the first moment) **M** | Found, sure **M** | Found, sure **M** | Found, sure **M** | Found, sure **M** |
| Task 2 (dog by a tree, the Diwali before) | **Didn't find it** (Hinglish read as last year, no fix offered) **M** | Found it, **if** they tap "or Diwali 2024" **M** | Found it, **if** they tap "or Diwali 2024" **M** | Found it, **if** they tap "or Diwali 2024" **M** | Found it (typed the year: `dog tree diwali 2024`) **M** |
| Features ticked | Removed or changed a clue **P** | Picked a suggested alternative; "Why this moment?" **P** | "Around that time" **P** | Picked a suggested alternative **P** | None of these **P** |
| Helped or confused | The year clue was wrong and couldn't be fixed **P** | Seeing the photos around it helped **P** | Moving to nearby months felt like scrolling, but faster **P** | Didn't notice the clues at first **P** | Nothing stood out; typed exact words **P** |

### Page 4 · Questions

| Question | A | B | C | D | E |
|---|---|---|---|---|---|
| Sure of Task 1 (1–5) | 5 **P** | 4–5 **P** | 5 **P** | 4 **P** | 5 **P** |
| What made you sure | The moment matched the event **P** | The photos before and after **P** | Right month, right event **P** | Recognised the setting **P** | Matched the exact date typed **P** |
| What did it do with your words? Anything wrong? | Got "last year" right, got "the year before last" wrong **P** | Turned one word into an event and a date **P** | Understood a full sentence **P** | Guessed the year from "diwali" **P** | Read the date literally **P** |
| vs Google Photos (1–5) | 5 **P** | 4 **P** | – (doesn't use it) | 4 **P** | 3 **P** |
| Can / can't vs Google Photos | Understands festivals plus "last year" / GP has my real photos and faces **P** | Shows the moment, not a grid / GP is faster for simple searches **P** | – | Finds it without knowing what to type / GP albums **P** | – / GP has all my documents **P** |
| One change | Understand *pichle se pichle saal* **P** | Show the date range more clearly **P** | Work inside Apple Photos **P** | Make the clue labels more obvious **P** | Read the text in my photos (bills, medicine) **P** |
| When would you use it | Every time **P** | Only when normal search fails **P** | Every time **P** | Only when normal search fails **P** | Rarely **P** |

### Page 5 · Session log
All five paste it. Expect **0 wrong confirmations** on Task 1 **M**. On Task 2, anyone who misses the "or Diwali 2024" tap may confirm a 2025 photo. That's the guardrail to watch.

---

## What this predicts for the real responses

1. **Segment count:** 4 of 5 count toward the 3. E is reported separately, as the brief requires.
2. **Task 1 tells nobody apart:** all 5 find it, however it's typed. It only shows the flow works.
3. **Task 2 carries the signal:** success depends on noticing "or Diwali 2024". Score `clue_edits` from the log.
4. **One real failure to fix or report:** *"pichle se pichle saal"* gets no alternative, so A fails Task 2.
5. **Form flow:** C checks the page-2 skip; D may drop out at "type into Google Photos"; E checks out-of-segment reporting.
6. **Score afterwards:** for each real respondent, count how many **P** answers held (e.g. "B: 5 of 8"). Wrong predictions are findings too.
