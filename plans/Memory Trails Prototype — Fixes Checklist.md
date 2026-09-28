# Memory Trails Prototype — Fixes Checklist

## Purpose

This document captures the recommended fixes for the live Memory Trails prototype at:

<https://memory-trails-v2.vercel.app>

The goal is to make the prototype more clearly aligned with the case study:

> Help users recognize and retrieve a remembered visual moment when they cannot describe it precisely.

The prototype should feel like a **memory re-entry experience**, not another keyword search form or a conventional filter interface.

---

# 1. Must-fix changes

## 1.1 Replace the fellowship-provided examples

The current prototype still uses the original case-study examples:

- “the medicine photo from last year”
- “a small café during our Goa trip”

Replace them throughout the prototype with original examples.

### Recommended examples

Use one primary example and two or three secondary examples:

**Primary example:**

> The photo of the handmade cake from my sister’s graduation

**Secondary examples:**

> The group photo after our college performance

> The picture of the handwritten note from my old apartment

> The photo of my dog near the blue suitcase

### Update these locations

- Text-field placeholder.
- `Try a memory like` examples.
- Memory-anchor examples.
- Any preset/demo scenarios.
- Results or recap copy that repeats the original examples.
- Prototype documentation and screenshots used in the presentation.

### Acceptance criteria

- [ ] No reference to Goa remains in the user-facing demo.
- [ ] No medicine example appears in the first screen.
- [ ] The graduation/cake example works as a complete demo task.
- [ ] The examples represent different memory types: event, object, document, and pet/person.

---

## 1.2 Remove the sensitive medicine example from the first screen

Do not show a health-related example in the primary entry flow. The user should not encounter a sensitive memory category before choosing it themselves.

Replace:

> the medicine photo from last year

With:

> the picture of the handwritten note from my old apartment

Health-related retrieval can remain in research scenarios, but it should not be a prominent demo example or proactive suggestion.

### Acceptance criteria

- [ ] No medical example appears in the entry screen.
- [ ] No sensitive memory is suggested proactively.
- [ ] The privacy message remains visible but calm and concise.

---

## 1.3 Make the success state explicit

The current `That’s the one` action is directionally correct, but the prototype needs a clear confirmation state so the user and evaluator understand when retrieval succeeds.

### Recommended success state

After the user taps `That’s the one`, show:

> **You found the moment.**
>
> This photo matches the memory you described.

Actions:

- `Open photo`
- `View the surrounding moment`
- `Done`

### Why this matters

The case-study metric is successful retrieval, not simply opening a result. The prototype should visibly distinguish:

```text
Candidate shown → User recognizes it → Retrieval confirmed
```

### Acceptance criteria

- [ ] Confirmation happens only after an explicit user action.
- [ ] The interface does not claim success before the user confirms.
- [ ] The user can open the target photo or inspect the surrounding sequence.
- [ ] A completion event can be tracked as `retrieval_confirmed`.

---

## 1.4 Clarify the recovery flow after “Not this moment”

The prototype already supports rejecting a moment. Make the next step easier to understand and more actionable.

### Recommended heading

> **What feels wrong about this moment?**

### Recommended options

- `Wrong day`
- `Wrong place`
- `Wrong people`
- `Wrong type of image`
- `I’m not sure`

The prototype can continue to support more specific actions such as:

- `Earlier`
- `Later`
- `Same place, different day`
- `Show more like these photos`
- `Change a memory clue`

### Feedback after selection

After the user chooses an option, explain the change:

> Keeping the event clue. Looking at nearby days.

or:

> Keeping the date range. Looking for a different place.

### Acceptance criteria

- [ ] Rejection does not send the user back to the beginning.
- [ ] Each recovery action changes one retrieval dimension.
- [ ] The next state explains what changed.
- [ ] Previously rejected moments remain excluded during the session.
- [ ] An `Undo` action is available where appropriate.

---

# 2. Improve the entry experience

## 2.1 Strengthen the distinction from normal Search

The current entry screen is good, but it can still look like another search box. Make the memory-first purpose more explicit.

### Recommended copy

**Heading:**

> Describe the moment, not the photo

**Supporting text:**

> Start with what you remember. It’s okay if you are unsure about the date, place, or exact words.

Keep the action label:

> `Show moments`

Avoid using `Search` as the main button label.

### Acceptance criteria

- [ ] The first screen communicates that exact wording is not required.
- [ ] The copy uses “moment” and “remember,” not only “query” or “search.”
- [ ] The primary action is clearly different from normal Search.

---

## 2.2 Reframe “Memory anchor” as an optional memory cue

The current anchor controls—such as Goa, Bengaluru, Kochi, Landmark, Beach, and Food—look like conventional filters. This weakens the distinction between Memory Trails and regular Search.

### Replace the label

Current:

> Or start with a memory anchor

Recommended:

> **Add one thing you remember**

### Use memory-friendly cue types

Prefer:

- `A place`
- `A person`
- `An object`
- `An event`
- `A type of image`
- `A season or time`

If the prototype uses concrete chips, make them examples rather than filters:

- `graduation`
- `cake`
- `family`
- `handwritten note`
- `college performance`
- `dog`

### Acceptance criteria

- [ ] The anchor section does not look like an advanced filter panel.
- [ ] Users can start with a cue without knowing an exact place name.
- [ ] Concrete chips reflect the new demo examples.
- [ ] Users can continue with only a vague description.

---

# 3. Improve episode results and explanations

## 3.1 Make “Why this moment?” more prominent

`Why this moment?` is one of the strongest elements of the concept. It should be visible enough to support trust and result evaluation.

### Recommended episode explanation

> Matches the graduation event, cake-like images, and nearby family photos.

Then offer:

> `See evidence`

### Evidence categories

Separate evidence into three types:

| Evidence type | Example |
|---|---|
| Direct | Cake-like scene detected in this photo |
| Nearby context | Family gathering detected in nearby photos |
| Approximate | Date appears to be around the graduation period |

### Recommended evidence detail

```text
Cake-like scene · detected in this photo
Family gathering · detected in nearby photos
Date · approximate
```

### Acceptance criteria

- [ ] Every episode has a short explanation.
- [ ] Explanations use grounded evidence, not invented narratives.
- [ ] Direct and nearby evidence are distinguishable.
- [ ] Approximate information is labelled as approximate.
- [ ] No numeric confidence score is required in the UI.

---

## 3.2 Keep the memory context visible while browsing

The user should not lose the original recollection while reviewing episodes.

Keep a compact context row visible:

```text
Your memory: graduation · cake · family
```

Allow each clue to be removed or edited.

### Acceptance criteria

- [ ] Original memory remains visible on the results screen.
- [ ] Current clues are editable.
- [ ] Removed clues can be restored with `Undo`.
- [ ] The user can add a new clue without restarting.

---

## 3.3 Make episode grouping visually recognizable

The prototype should communicate that the result is a moment or episode, not just a ranked image.

Each episode should show:

- Episode label.
- Approximate date or date range.
- Place or context if available.
- Number of photos.
- Representative thumbnails.
- Short explanation.
- `Open moment` action.

### Recommended example

```text
Sister’s graduation · around May 2022
12 photos · family event

[photo] [photo] [photo] [photo]

Why this moment?
Graduation-like event · cake scene · family photos nearby
```

---

# 4. Improve prototype trust and research clarity

## 4.1 Explain the representative data limitation clearly

The prototype uses approximately 1,250 openly licensed photographs with invented dates, places, and moments. This is appropriate for an interaction prototype, but it limits what users can evaluate.

### Recommended disclaimer

> **Concept prototype**
>
> Uses representative public images and invented metadata. Not affiliated with Google.

Keep the disclaimer visible near the prototype information link, but do not let it dominate the main task.

### Deck wording

Use this statement in the presentation:

> This MVP validates the memory-reentry interaction and recovery model using representative media. It does not validate production-scale Google Photos retrieval accuracy.

### Acceptance criteria

- [ ] The prototype does not imply access to a real Google Photos library.
- [ ] Invented metadata is clearly disclosed.
- [ ] The limitation is included in the deck and MVP-testing notes.

---

## 4.2 Add a clear relationship to Ask Photos

The prototype should not suggest that Memory Trails replaces Ask Photos.

Add a short explanation to the About or Research page:

```text
Ask Photos helps you ask questions about your library.
Memory Trails helps you recognize and navigate a remembered moment.
```

Optional entry-point copy:

> A visual way to revisit a memory when a conversational answer is not enough.

### Acceptance criteria

- [ ] Ask Photos is acknowledged as an existing capability.
- [ ] Memory Trails is positioned as complementary.
- [ ] The distinction is about recognition, episode context, and recovery.
- [ ] The prototype does not claim that Ask Photos cannot search naturally.

---

# 5. Use a new demo scenario for testing

## Recommended test task

Use the new graduation scenario instead of the fellowship examples:

> **Find the photo of the handmade cake from your sister’s graduation. You remember the event and what the photo looked like, but not the exact date or album.**

### What to observe

- Does the user understand that exact wording is not required?
- Do they start with the description or choose a cue?
- Do they understand the editable clues?
- Can they identify the useful episode?
- Do they open `Why this moment?`?
- Can they reject a near miss and recover?
- Do they explicitly confirm the right item?

## Additional optional tasks

Use only if the prototype data supports them:

1. **College performance:**
   > Find the group photo after your college performance. You remember the people and event, but not when it happened.

2. **Handwritten note:**
   > Find the photo of a handwritten note from your old apartment. You remember the note and place, but not the date or album.

3. **Pet memory:**
   > Find the photo of your dog near a blue suitcase. You remember the scene, but not when it was taken.

Do not use the medicine or Goa café tasks in the main demo.

---

# 6. Suggested event tracking

Add lightweight tracking so the MVP can be evaluated against the case-study metric.

| Event | Meaning |
|---|---|
| `memory_reentry_started` | User opened Find a memory |
| `memory_description_submitted` | User submitted a memory description |
| `memory_anchor_selected` | User added a memory cue |
| `memory_clue_removed` | User removed an inferred clue |
| `memory_clue_undo` | User restored a removed clue |
| `moments_shown` | Episode candidates were displayed |
| `episode_opened` | User opened a visual episode |
| `evidence_viewed` | User opened Why this moment? evidence |
| `episode_rejected` | User selected Not this moment |
| `recovery_action_selected` | User chose a recovery option |
| `episode_shifted_earlier` | User moved to an earlier time window |
| `episode_shifted_later` | User moved to a later time window |
| `retrieval_confirmed` | User selected That’s the one |
| `prototype_exited` | User left without confirmation |

## Primary prototype metric

> **Confirmed retrieval rate:** the percentage of test tasks where the user selects the intended item using `That’s the one` within the test session.

## Supporting metrics

- Time to first useful episode.
- Time to confirmation.
- Number of clue edits.
- Number of episodes opened.
- Near-miss recovery rate.
- Evidence-view rate.
- Abandonment rate.
- User confidence after confirmation.

---

# 7. Priority order

## P0 — Fix before the next review

- [ ] Replace Goa and medicine examples.
- [ ] Add the graduation/cake demo scenario.
- [ ] Add an explicit success state after `That’s the one`.
- [ ] Clarify the `Not this moment` recovery flow.
- [ ] Keep the representative-data disclaimer clear.

## P1 — Strongly recommended

- [ ] Change `Memory anchor` to `Add one thing you remember`.
- [ ] Replace city/filter-heavy chips with memory cue types.
- [ ] Strengthen the `Describe the moment, not the photo` copy.
- [ ] Make `Why this moment?` and `See evidence` more prominent.
- [ ] Keep the memory breadcrumb visible on results and episode screens.
- [ ] Add the Ask Photos comparison to the About or Research page.

## P2 — Later improvements

- [ ] Add side-by-side comparison with regular Search.
- [ ] Add more demo scenarios.
- [ ] Add event tracking and a small results dashboard.
- [ ] Add accessibility review for keyboard, screen reader, and colour contrast.
- [ ] Test mobile layouts at 320px and 375px widths.

---

# 8. Final review checklist

Before presenting the prototype, verify:

- [ ] The opening example is not from the fellowship brief.
- [ ] The experience does not look like a standard search form.
- [ ] The user can start with incomplete information.
- [ ] The system shows episodes, not only isolated photos.
- [ ] Each episode explains why it appeared.
- [ ] The user can correct clues without restarting.
- [ ] The user can recover after a near miss.
- [ ] The user explicitly confirms successful retrieval.
- [ ] The prototype does not overclaim production AI accuracy.
- [ ] Ask Photos is positioned as complementary, not ignored or misrepresented.
- [ ] The demo can be completed using the graduation/cake task.
- [ ] The deck uses the same examples and terminology as the prototype.

## Product guardrail

The experience should make the user feel:

> **I’m getting back into the memory.**

It should not make the user feel:

> **I need to write the perfect search query.**
