# Memory Trails — Post-Update Fixes

## Purpose

This document records the remaining fixes and validation steps after the latest Memory Trails deployment:

<https://memory-trails-v2.vercel.app>

The latest version has already improved the entry experience with:

- **Describe the moment, not the photo**
- **Add one thing you remember**
- New graduation, cake, family, handwritten-note, college-performance, and dog cues
- The graduation/cake example as the primary scenario
- Removal of the Goa and medicine examples from the entry screen
- A clearer representative-data disclaimer

The remaining work is primarily about validating the complete flow from memory entry to confirmed retrieval.

---

# 1. P0 — Validate the primary entry flow

## 1.1 Test the graduation example

Use this as the primary demo task:

> Find the photo of the handmade cake from your sister’s graduation. You remember the event and what the photo looked like, but not the exact date or album.

### Verify

- [ ] Open `Find a memory`.
- [ ] Confirm the heading says **Describe the moment, not the photo**.
- [ ] Confirm the supporting copy says users can be unsure about the date, place, or exact words.
- [ ] Tap the graduation/cake example under `Try a memory like`.
- [ ] Confirm the full example appears in the text field.
- [ ] Confirm the text is treated as entered content, not merely placeholder text.
- [ ] Confirm the primary action becomes available.
- [ ] Tap `Continue`.

## 1.2 Validate the primary button state

The current primary action is labelled **Continue** and appears disabled until the user provides a memory or selects a cue.

### Expected behavior

| User state | Button behavior |
|---|---|
| Empty text field and no cue | Disabled |
| Text entered | Enabled |
| One cue selected | Enabled |
| Text plus cue selected | Enabled |
| Search request running | Disabled with loading label |
| Results returned | Normal state restored or replaced by results view |

### Verify

- [ ] The button is visibly disabled only when no memory information exists.
- [ ] Selecting a preset example enables the button.
- [ ] Selecting one memory cue enables the button.
- [ ] Typing a vague description enables the button.
- [ ] Whitespace-only input does not enable the button.
- [ ] The button does not submit twice on rapid taps.
- [ ] A loading state such as `Looking for moments…` is shown during retrieval.

## 1.3 Check mobile visibility

The entry screen is vertically scrollable. Make sure the main action is not easy to miss.

### Verify

- [ ] `Continue` appears after the examples without excessive scrolling.
- [ ] The button has sufficient contrast against the background.
- [ ] The button is large enough to tap comfortably.
- [ ] The user does not need to scroll past the disclaimer to find the action.
- [ ] The text field remains visually connected to the primary action.

---

# 2. P0 — Complete the end-to-end retrieval journey

The prototype should be tested as one continuous experience:

```text
Memory description
→ Continue
→ Looking for moments…
→ Episode results
→ Why this moment?
→ Open moment
→ Not this moment / recovery
→ That’s the one
→ You found the moment
```

## 2.1 Results screen

### Verify

- [ ] The results screen retains the user’s original memory description.
- [ ] The selected memory cues remain visible.
- [ ] Results are grouped into moments or episodes, not shown only as isolated images.
- [ ] Each episode includes an approximate date or date range where available.
- [ ] Each episode includes location or contextual information where available.
- [ ] Each episode includes representative thumbnails.
- [ ] The strongest candidate is visually distinguishable without appearing certain too early.
- [ ] The results explain what was found in plain language.

## 2.2 Loading and empty states

### Loading state

Use simple copy:

> **Looking for moments…**
>
> I’m connecting the clues you remember.

### No close match state

Use simple copy:

> **No close match yet**
>
> I couldn’t find a moment that feels right. We can look more broadly.

### Verify

- [ ] Loading state is visible for long enough to communicate progress but not feel artificial.
- [ ] Loading state does not imply that real Google Photos data is being searched.
- [ ] No-close-match state does not blame the user for a vague description.
- [ ] The user receives at least one clear recovery action.
- [ ] The user can return to the memory without restarting from the home screen.

---

# 3. P0 — Validate recognition and confirmation

## 3.1 `Why this moment?`

This is a core trust feature and should be easy to find on the results screen.

### Verify

- [ ] Each candidate episode has a visible `Why this moment?` explanation.
- [ ] `See evidence` is easy to notice.
- [ ] The explanation connects the candidate to the remembered clues.
- [ ] Evidence distinguishes between direct image evidence and nearby-context evidence.
- [ ] Approximate information is labelled as approximate.
- [ ] The explanation does not present invented metadata as certain fact.

### Recommended evidence format

```text
Cake-like scene · detected in this photo
Family gathering · detected in nearby photos
Date · approximate
```

## 3.2 Open moment

### Verify

- [ ] `Open moment` opens the episode view rather than only one isolated image.
- [ ] The episode view shows surrounding photos in sequence.
- [ ] The user can move through the nearby photos.
- [ ] The original memory clues remain available while browsing.
- [ ] The user can return to the candidate list without losing progress.

## 3.3 Confirmed retrieval

After the user taps `That’s the one`, show an unmistakable success state.

### Recommended copy

> **You found the moment.**
>
> This photo matches the memory you described.

### Recommended actions

- `Open photo`
- `View the surrounding moment`
- `Done`

### Verify

- [ ] `That’s the one` requires an explicit user action.
- [ ] The prototype does not claim success merely because a result was opened.
- [ ] The success state names the retrieved photo or moment.
- [ ] The user can open the selected image.
- [ ] The user can view the surrounding moment.
- [ ] The user can finish with `Done`.
- [ ] The success state can be tracked as `retrieval_confirmed`.

---

# 4. P1 — Validate near-miss recovery

## 4.1 `Not this moment`

The rejection action should help the system learn what was wrong instead of sending the user back to the beginning.

### Recommended follow-up heading

> **What feels wrong about this moment?**

### Recommended options

- `Wrong day`
- `Wrong place`
- `Wrong people`
- `Wrong type of image`
- `I’m not sure`

### Verify

- [ ] `Not this moment` is visible on the episode view.
- [ ] The follow-up question is understandable without explanation.
- [ ] The user can select one reason.
- [ ] Each reason changes a meaningful retrieval dimension.
- [ ] The next state explains what changed.
- [ ] Rejected moments are not immediately shown again.
- [ ] An `Undo` action is available where appropriate.

### Recommended feedback examples

After `Wrong day`:

> Keeping the event clue. Looking at nearby days.

After `Wrong place`:

> Keeping the time clue. Looking for a different place.

After `Wrong type of image`:

> Keeping the event clue. Looking for different visual scenes.

## 4.2 Around-the-time navigation

The prototype includes earlier/later exploration. Validate that it feels like memory navigation rather than a standard date filter.

### Verify

- [ ] The section is labelled `Around that time`.
- [ ] The user understands that dates are approximate.
- [ ] `Earlier` moves to a meaningful nearby chapter.
- [ ] `Later` moves to a meaningful nearby chapter.
- [ ] The active chapter is visually clear.
- [ ] The user can return to the original candidate chapter.
- [ ] The original clues remain visible after moving in time.

---

# 5. P1 — Validate memory cue behavior

The updated entry screen now uses **Add one thing you remember**. This is a strong improvement, but the cues should remain optional and memory-oriented.

## 5.1 Cue selection

### Verify

- [ ] Selecting `graduation` adds an event clue.
- [ ] Selecting `cake` adds an object clue.
- [ ] Selecting `family` adds a people clue.
- [ ] Selecting `handwritten note` adds a type-of-image clue.
- [ ] Selecting `college performance` adds an event clue.
- [ ] Selecting `dog` adds a pet clue.
- [ ] Selected cues have a clear selected state.
- [ ] Selected cues can be removed.
- [ ] Removing a cue does not clear the entire memory.
- [ ] The user can combine a text description with one or more cues.

## 5.2 Avoid filter-like behavior

The cues should not imply that users need to know exact categories before starting.

### Verify

- [ ] The user can proceed with only a vague description.
- [ ] The user can proceed with only one broad cue.
- [ ] The cue section does not dominate the text entry field.
- [ ] The copy uses memory language rather than filter language.
- [ ] No city-heavy list appears on the first screen.

---

# 6. P1 — Keep the Ask Photos relationship clear

Memory Trails should be positioned as complementary to Ask Photos, not as a replacement or correction.

Add or verify this explanation in the About or Research area:

```text
Ask Photos helps you ask questions about your library.
Memory Trails helps you recognize and navigate a remembered moment.
```

### Verify

- [ ] Ask Photos is acknowledged as an existing Google Photos capability.
- [ ] The prototype does not imply that Ask Photos cannot understand natural language.
- [ ] The distinction focuses on recognition, episode context, and recovery.
- [ ] The relationship is explained in plain language.
- [ ] The presentation uses the same positioning.

---

# 7. P1 — Prototype trust and disclosure

The prototype uses representative public images and invented metadata. This is acceptable for concept testing, but the limitation must remain clear.

### Current disclaimer

> Concept prototype. Uses representative public images and invented metadata. Not affiliated with Google.

### Verify

- [ ] The disclaimer is visible near the prototype information link.
- [ ] The disclaimer is readable on mobile.
- [ ] It does not obscure the primary task.
- [ ] It appears in screenshots used in the presentation where practical.
- [ ] The deck states that the prototype validates the interaction model, not production retrieval accuracy.

### Recommended presentation wording

> This MVP validates the memory-reentry interaction and recovery model using representative media. It does not validate production-scale Google Photos retrieval accuracy.

---

# 8. P1 — Accessibility and mobile QA

## Accessibility

- [ ] All controls have meaningful accessible labels.
- [ ] The close control is labelled clearly.
- [ ] The text field has a label or useful accessible name.
- [ ] Memory cues are announced as selectable controls.
- [ ] Selected and unselected states are not communicated by colour alone.
- [ ] Focus order follows the visual order.
- [ ] Keyboard users can reach the primary action.
- [ ] Loading and error states are announced with `aria-live` where appropriate.
- [ ] Text and controls meet reasonable contrast requirements.

## Mobile layout

Test at minimum:

- 320px width
- 375px width
- 390px width
- Desktop browser width

### Verify

- [ ] The text field does not clip the graduation example.
- [ ] Cue chips wrap without overlapping.
- [ ] The primary action remains visible and tappable.
- [ ] Result cards do not become too narrow to compare.
- [ ] Evidence details remain readable.
- [ ] Earlier/later controls remain accessible.
- [ ] The bottom disclaimer does not cover content.

---

# 9. P2 — Add lightweight evaluation tracking

Track the following events if the prototype supports analytics:

| Event | Meaning |
|---|---|
| `memory_reentry_started` | User opened Find a memory |
| `memory_description_submitted` | User submitted a text description |
| `memory_anchor_selected` | User selected a memory cue |
| `moments_shown` | Candidate moments were displayed |
| `episode_opened` | User opened a candidate episode |
| `evidence_viewed` | User opened Why this moment? |
| `episode_rejected` | User selected Not this moment |
| `recovery_action_selected` | User selected a recovery reason |
| `episode_shifted_earlier` | User moved to an earlier chapter |
| `episode_shifted_later` | User moved to a later chapter |
| `retrieval_confirmed` | User selected That’s the one |
| `prototype_exited` | User left without confirmation |

## Primary metric

> **Confirmed retrieval rate:** the percentage of test tasks where the participant explicitly selects the intended item using `That’s the one`.

## Supporting metrics

- Time to first useful moment.
- Time to confirmation.
- Number of clue edits.
- Number of episodes opened.
- Evidence-view rate.
- Near-miss recovery rate.
- Abandonment rate.
- Self-reported confidence after confirmation.

---

# 10. Demo acceptance test

Use this script before the next presentation or user test.

## Task

> Find the photo of the handmade cake from your sister’s graduation. You remember the event and the cake, but not the date or album.

## Expected journey

1. Open `Find a memory`.
2. Read and understand `Describe the moment, not the photo`.
3. Select or enter the graduation/cake memory.
4. Tap `Continue`.
5. See a loading state.
6. Review grouped moments.
7. Open `Why this moment?`.
8. Open one moment.
9. Reject one near miss using `Not this moment`.
10. Use a recovery action or move earlier/later.
11. Select `That’s the one` on the intended moment.
12. See `You found the moment`.
13. Open the photo or surrounding moment.
14. Finish with `Done`.

## Pass criteria

- [ ] A first-time tester understands the entry point without coaching.
- [ ] The tester does not need an exact date or album.
- [ ] The tester understands why the top candidate appeared.
- [ ] The tester can reject a near miss.
- [ ] The tester can recover without restarting.
- [ ] The tester knows when retrieval has succeeded.
- [ ] The full task can be completed on a mobile-sized viewport.

---

# 11. Final priority list

## P0 — Required before the next review

- [ ] Validate preset example selection.
- [ ] Validate `Continue` enabled/disabled states.
- [ ] Validate loading and no-close-match states.
- [ ] Complete the full graduation/cake journey.
- [ ] Confirm the final `You found the moment` state works.
- [ ] Confirm `Not this moment` does not restart the experience.

## P1 — Strongly recommended

- [ ] Make `Why this moment?` prominent.
- [ ] Verify evidence quality and certainty labels.
- [ ] Verify earlier/later navigation.
- [ ] Add or verify Ask Photos positioning.
- [ ] Run mobile and accessibility QA.
- [ ] Keep the disclosure visible and readable.

## P2 — Later

- [ ] Add analytics events.
- [ ] Add a small evaluation dashboard.
- [ ] Add more original demo scenarios.
- [ ] Compare Memory Trails with standard Search in a user test.
- [ ] Test with 3–4 image-based survey tasks and compare responses with the prototype behavior.

## Product guardrail

The final experience should make users feel:

> **I’m getting back into the memory.**

It should not make them feel:

> **I need to write the perfect search query.**
