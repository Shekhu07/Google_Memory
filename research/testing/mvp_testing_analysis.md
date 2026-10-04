# Memory Trails MVP: User Testing Analysis & Findings (Part 6)

**Test Window:** 3–4 Oct 2026 · **Method:** Self-serve structured testing form (`research/testing/mvp_test_form.gs`)  
**Participants:** n = 6 completed responses · **Segment fit:** 6 of 6 (100%)  
**Data Sources:** Raw responses in `research/testing/mvp-test-responses-raw.csv`; scored log in `research/testing/mvp-test-log.csv`

---

## 1. Executive Summary & Segment Fit

The MVP user testing evaluated the Memory Trails prototype (`https://memory-trails-v2.vercel.app`) with 6 participants against the core brief requirement (Part 6): returning to users from the target segment, testing representative retrieval tasks from research, and documenting learnings and next-iteration changes.

| Participant | Segment Fit (Q1) | Primary App | Own GP When (Memory) | Own GP Query (Typed) | Task 1 Result | Task 2 Result | Task 1 Sureness | vs GP (1–5) | Adoption Intent |
|---|---|---|---|---|---|---|---:|---:|---|
| **R01** | Yes (event) | Google Photos | "Before COVID" | "A wedding that I attended before COVID 19 pandemic" | Found, sure | Not found | 5 / 5 | 5 / 5 | Every time |
| **R02** | Yes (event) | Google Photos | "when I started Gym" | "gym" | Found, sure | Found, sure | 4 / 5 | 4 / 5 | When search fails |
| **R03** | Yes (roughly) | Apple Photos | *(N/A)* | *(N/A)* | Found, sure | Found, sure | 5 / 5 | *(N/A)* | Every time |
| **R04** | Yes (roughly) | Google Photos | "vacation last year" | "vacation" | Found, sure | Found, sure | 4 / 5 | 4 / 5 | When search fails |
| **R05** | Yes (event) | Google Photos | "A wedding ceremony sometime in the last year" | "Wedding event" | Found, sure | Found, sure | 4 / 5 | 4 / 5 | Every time |
| **R06** | Yes (roughly) | Google Photos | "2-3 years back when I visited Kerala" | "Kerala photos" | Right Diwali, unsure photo | Found, sure | 4 / 5 | 3 / 5 | Every time |

- **Segment validation:** All 6 participants qualified for the target segment: 3 remembered by an event or festival ("a wedding, Diwali, a trip"), 3 remembered roughly ("last winter, a couple of years ago"). None remembered the exact date.
- **App distribution:** 5 of 6 use Google Photos as their primary photo app; 1 uses Apple Photos.

---

## 2. Own Google Photos Baseline Probe (Before Using Prototype)

Before touching the prototype, the 5 Google Photos users searched their own library for a real event photo they struggled to find.

### Key Findings on Real Google Photos:
1. **The Memory vs. Query Gap in Real Life:**
   - When asked how they remembered when the photo was taken, participants articulated temporal anchors: *"Before COVID"*, *"when I started Gym"*, *"vacation last year"*, *"A wedding ceremony sometime in the last year"*, *"2-3 years back when I visited Kerala"*.
   - When typing into Google Photos, **4 of 5 stripped the temporal context entirely**: typing bare nouns (*"gym"*, *"vacation"*, *"Wedding event"*, *"Kerala photos"*). Only R01 typed a complete phrase (*"A wedding that I attended before COVID 19 pandemic"*).
   - This proves the Part 4 problem definition: users have learned that search engines drop or fail on episodic phrases, so they compress their memory into bare object/category keywords.

2. **Zero Success Rate on Real Google Photos:**
   - **0 of 5 users found the photo they searched for.**
   - **2 of 5 experienced query misinterpretation:** *"It showed photos like it, but from other years or other events"* (R01, R04).
   - **3 of 5 experienced recognition/evaluation failure:** *"It showed lots of similar photos and I couldn't tell which was mine"* (R02, R05, R06).

3. **Complete Black Box (Lack of Interpretability):**
   - **0 of 5 users could see how Google Photos read their words.** 3 answered *"No"* and 2 answered *"Not sure"*. Neither classic search nor Ask Photos showed which date range or event was searched.

4. **Ask Photos Does Not Solve the Problem:**
   - 3 of the 5 users had tried Ask Photos with the same query. **All 3 reported:** *"It showed related photos, but not the one."* (0 found).
   - This directly replicates the earlier survey finding (§G1: 4 of 4 who reported an Ask Photos result said "related photos, but not the one").
   - The remaining 2 users did not have Ask Photos enabled or had not tried it.

5. **Workarounds: Scrolling and Albums, Not Search:**
   - When asked what *actually* got them to an old photo the last time they succeeded:
     - **3 relied on scrolling back through the timeline.**
     - **2 relied on manual albums or folders.**
     - **0 relied on search.**
   - This confirms Slide 2 and Slide 7: timeline scrolling is the user's manual workaround for missing episodic re-entry.

---

## 3. Prototype Performance (Tasks 1 & 2)

### Task 1: "A photo of your cat from last year's Diwali"
- **Task completion:** 
  - **5 of 6 found the photo and were sure it was the right one.**
  - **1 of 6 found the right Diwali, but was unsure which photo was theirs** (R06: *"Cat pics from diwali"* -> landed on Diwali 2025 moment, but faced recognition ambiguity among cat photos).
  - **0 of 6 failed.** All 6 reached the correct event!
- **Sureness rating (1 to 5):**
  - Ratings: 5, 4, 5, 4, 4, 4. **Mean = 4.33 / 5.**
- **Why they were sure:**
  - *"Moment matched the event"* (R01)
  - *"The photos before and after"* (R02 — validates the surrounding context feature)
  - *"Right month, right event"* (R03)
  - *"Recognised the setting"* (R04)

### Task 2 (Optional Clue-Correction): "The dog by a tree, from the Diwali before that"
- **Task completion:**
  - **5 of 6 found the photo and were sure it was the right one.**
  - **1 of 6 did not find it (R01).** R01 got stuck because the prototype extracted "last year" as Diwali 2025 and R01 struggled to edit the year label to 2024 (*"The year label was wrong and couldn't be fixed"*, *"Got 'last year' right, 'the year before last' wrong"*).
  - R02, R04, and R06 successfully clicked the 1-tap chip alternative *"or Diwali 2024"*, which took them straight to the target moment.

### Interaction & Feature Usage:
- **Picked a suggested alternative (e.g. "or Diwali 2024"):** Used by 4 of 6 participants (R02, R04, R06). This was the single most effective clue-correction mechanism.
- **"Around that time" (moving to nearby months):** Used by 2 of 6 (R03, R06). R03 noted: *"Moving to nearby months, like scrolling but faster."*
- **Removed or changed a clue:** Used by 2 of 6 (R01, R05).
- **"Why this moment?" (Evidence details):** Used by R02: *"Seeing the photos around it helped."*

---

## 4. Head-to-Head: Prototype vs. Google Photos

Among the 5 Google Photos users:
- **Ease comparison rating (1 = Much harder, 3 = Same, 5 = Much easier):**
  - Ratings: 5, 4, 4, 4, 3. **Mean = 4.0 / 5.**
  - 4 of 5 (80%) rated the prototype easier or much easier than Google Photos.
  - 1 of 5 (20%) rated it the same (R06, who wanted higher photo retrieval speed).
  - 0 of 5 rated it harder.

### What the Prototype Did Better (User Quotes):
- *"Shows the moment, not a grid"* (R02)
- *"Moving to nearby months, like scrolling but faster"* (R03)
- *"Works without knowing what to type"* (R04)
- *"Understands festivals plus 'last year'"* (R01)
- *"Find the exact month and the year that I was searching. And it could understand the mix of hindi and english language"* (R06)
- *"Understood a full sentence"* (R03)

### What Google Photos Does Better (User Quotes):
- *"Google Photos has real photos and faces"* (R01)
- *"Google Photos is faster for simple searches"* (R02)
- *"Google Photos has albums"* (R04)
- Retrieval latency for instant results.

### Adoption Intent:
- **4 of 6:** *"Every time I look for an old photo."*
- **2 of 6:** *"Only when normal search doesn't work."*
- **0 of 6:** *"Rarely"* or *"Never"*.

---

## 5. Top Usability Issues & Next-Iteration Roadmap

| Issue | Severity | User Evidence | Root Cause | Next-Iteration Fix |
|---|---|---|---|---|
| **1. Compound relative year phrasing** | High | R01 failed Task 2: *"Understand 'pichle ke pichle saal'"*, *"The year label was wrong and couldn't be fixed"* | Parser handled "last year" (2025) and "N years ago" (2024), but missed compound colloquial "year before last" / "pichle ke pichle saal" | Extend temporal resolver with compound relative offsets; allow manual year dropdown edit directly on the date chip |
| **2. Clue chip saliency** | Medium | R04: *"Didn't notice the clue labels at first"* · R02: *"Show the date range more clearly"* | Clue chips styled in subtle muted pills above the moments | Add explicit accent badge and micro-prompt: *"Showing Diwali 2025 · Tap to change"* |
| **3. Retrieval latency & UI transition speed** | Medium | R05, R06: *"The Design and the speed at which the photos are retrieved"* | ONNX CLIP vector inference runs client-side / serverless cold-start | Pre-cache top candidate moments; show instant skeleton loader with progressive image decoding |
| **4. Recognition ambiguity within large moments** | Low | R06 found right Diwali, but was unsure which cat photo was target | Moments contain multiple photos of the same event; small thumbnails on mobile | Add 1-tap "Enlarge photo" swipe sheet before confirming |

---

## 6. Methodological Disclosures & Guardrails

1. **Study Log Omission:** All 6 participants submitted the Google Form without pasting the raw JSON session log from the prototype footer. Consequently:
   - Specific confirmed `photo_id`s could not be cross-checked against the database.
   - Exact task completion times (`secondsToConfirm`) and quantitative clue-edit event counts are unobserved.
   - Guardrail metric (`wrong_confirm`) is coded as **unknown** rather than asserted as zero.
2. **Self-Report Nature:** Results are based on self-reported questionnaire responses following an unmoderated session, rather than an audio/video recorded think-aloud session.
3. **Sample Size:** n = 6 participants from the author's network (convenience sample). All statistics are reported as integer counts (e.g. "5 of 6") rather than generalized percentages.
