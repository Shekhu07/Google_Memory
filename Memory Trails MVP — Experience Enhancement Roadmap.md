# Memory Trails MVP — Experience Enhancement Roadmap

## Scope guardrail

Memory Trails should not become a general search redesign. Improvements should be judged by one question:

> **Does this help a user recover a specific old visual memory when their description is incomplete?**

Search and AI retrieval are enabling capabilities. The product experience remains a memory-reconstruction and recognition flow.

## 1. Improve the retrieval model behind the experience

### 1.1 Treat the recollection as a bundle of weak signals

Do not reduce the user’s description to one query string. Parse it into independent evidence dimensions:

- Approximate time
- Place or route
- People or relationship
- Object or scene
- Text or document type
- Event or activity
- Surrounding-photo context
- User-provided certainty

Each dimension should be independently editable and independently suppressible. This lets the user say, “Goa is right, café is uncertain,” instead of rewriting the entire recollection.

### 1.2 Rank episodes, not only individual assets

The unit of retrieval should be a **moment cluster**: a short time-and-context window containing related photos and videos. Rank episodes using:

```text
Episode usefulness =
  memory-cue coverage
  × episode coherence
  × visual recognizability
  × evidence quality
```

This is not a single user-facing score. It is an internal ranking principle. The UI should explain the contributing evidence in plain language.

### 1.3 Use surrounding context as a first-class signal

A target photo may not contain the remembered café, person, or event clearly. Nearby photos may provide the strongest clues. Use:

- Photos taken shortly before and after the candidate.
- Same-day location transitions.
- Repeated faces or objects in the sequence.
- Related screenshots, receipts, tickets, or notes.
- Existing album and shared-album context when permissions allow.

The experience should say `nearby sequence` or `same-day context`, not imply that the target photo itself contains all the evidence.

### 1.4 Model uncertainty by dimension

Avoid one global confidence number. A candidate can have:

- Strong place evidence.
- Weak object evidence.
- Unknown date precision.

Represent this internally and expose it only when useful:

```text
Goa · strong location match
Café scene · possible
Date · approximate
```

This is more actionable than `87% match` and gives the user a clear correction path.

## 2. Improve the interaction flow

### 2.1 Add a “memory strength” start

Before showing questions, let the user indicate what they remember most clearly:

```text
What part feels most certain?
[Where it was] [Who was there] [What it showed] [When it happened] [Not sure]
```

This prevents the system from over-weighting a weak phrase such as “small café” when the user is much more certain about the trip location.

### 2.2 Ask questions based on candidate separation

The next question should be chosen because it separates the top candidate episodes, not simply because it is available.

Example:

- If all candidates are in Goa but span different trips, ask about time or companions.
- If candidates are in the same trip but differ by place, ask `near the beach or in a town?`.
- If the candidate set is already narrow, do not ask anything; show the moments.

The user should never experience a fixed questionnaire.

### 2.3 Offer “show me around it” before more questions

When the system has a plausible time window but weak semantic confidence, show a visual timeline immediately:

```text
Dec 14 ───── Dec 15 ───── Dec 16 ───── Dec 17
  beach        café?       market       hotel
```

Let the user recognize the episode from adjacent moments instead of answering another abstract question.

### 2.4 Make broadening controlled and reversible

When no candidate feels right, offer one-dimensional changes:

- `Widen the date by one month`
- `Look around Goa`
- `Include nearby places`
- `Show screenshots and documents`
- `Use the trip sequence, not the object clue`

After the user chooses one, show a short explanation:

> `Keeping Goa and the trip context. Looking across a wider date range.`

Never silently broaden every dimension at once.

### 2.5 Add a “memory breadcrumb”

Keep a compact trail visible above results:

```text
Your memory → Goa → trip → café? → Dec 2023
```

Each item can be removed or edited. This maintains the user’s mental thread while they browse and makes the system’s current interpretation legible.

## 3. Improve episode presentation

### 3.1 Create a stronger episode cover

The first thumbnail should be selected for **recognizability**, not only relevance. A good cover may be:

- A representative scene from the trip.
- A face or companion the user remembers.
- A place landmark.
- A document thumbnail with readable text.
- A small contact sheet when no single image represents the episode.

### 3.2 Add sequence density cues

Help the user understand the episode without opening it:

```text
Goa · 14–18 Dec 2023
18 photos · 3 places · 2 beach scenes · 4 food photos
```

These cues make clusters feel like real moments rather than arbitrary result buckets.

### 3.3 Support media-type pivots

A vague memory may be a screenshot, document, video frame, or motion photo rather than a standard camera photo. Add lightweight pivots:

- `Photos`
- `Videos`
- `Screenshots`
- `Documents`
- `All media`

These are memory aids, not general filters. Only show them when they are relevant to the recollection.

### 3.4 Add “nearby memories” deliberately

Once inside an episode, offer a small contextual strip:

- `Before this moment`
- `After this moment`
- `Same place`
- `Same people`
- `Same day`

This supports episodic recognition while preventing the user from getting lost in the whole library.

## 4. Improve correction and recovery

### 4.1 Turn every rejection into a structured signal

Instead of only `Not this`, offer a short set of likely mismatch dimensions:

```text
What feels wrong?
[Wrong trip] [Wrong place] [Wrong people] [Wrong type of image] [Not sure]
```

Use the selection to update the next candidate set. Keep this optional; users should not have to classify every miss.

### 4.2 Preserve rejected episodes within the session

Do not show the same rejected episode repeatedly. Treat a rejection as session-level evidence, not a permanent user preference.

### 4.3 Add undo everywhere

Every clue removal, broadening action, and recovery choice should have an `Undo` affordance. Memory reconstruction is exploratory; users may realize that a clue they removed was actually useful.

### 4.4 Support parallel candidate comparison

When two episodes are similarly plausible, let the user compare them without losing the context:

```text
[Goa · Dec 2023]  [Goa · Jan 2022]
```

Show differences in date, place, sequence density, and evidence—not a generic side-by-side metadata table.

## 5. Improve trust and transparency

### 5.1 Explain evidence at the right level

Use short explanations with expandable detail:

```text
Why this moment?
Goa location · nearby food photos · Dec 2023 trip sequence
[See evidence]
```

The expanded state can show:

- Which photos contributed context.
- Whether a place came from geotagging or nearby photos.
- Whether text was detected in the image.
- Which clues were approximate.

### 5.2 Separate “found” from “confirmed”

The system can present a candidate, but only the user can confirm that it is the remembered photo. Use different language:

- System: `Likely moment`
- User action: `That’s the one`

Avoid `We found it` before the user confirms.

### 5.3 Use calibrated empty states

Do not say `This photo doesn’t exist` or `No results` as a final judgment. Use:

> `I couldn’t find a moment that feels right yet.`

Then offer controlled next steps and a safe exit.

### 5.4 Add a lightweight feedback loop

After confirmation or exit, ask one optional question:

```text
Did this help you get back to the memory?
[Yes] [Partly] [No]
```

For research, follow with `What was missing?` but avoid adding a survey burden to normal use.

## 6. Improve sensitive-memory handling

### 6.1 Keep the experience user-initiated

Do not proactively surface medical, relationship, financial, or location memories based on inferred significance. The user must start the session.

### 6.2 Avoid sensitive restatement in exposed surfaces

If the user types a medical memory, keep the text private to the session and avoid placing it in notifications, shared suggestions, or persistent history unless the user explicitly chooses to save it.

### 6.3 Provide a discreet mode

Offer a privacy control for shared-device use:

```text
Private session
This memory will not be saved as a suggestion or label.
```

### 6.4 Make permission boundaries visible

If a candidate uses a shared album, partner-shared photo, or location-derived context, label that context clearly and follow existing access controls.

## 7. Improve accessibility and inclusivity

- Provide a text-first version of visual episode explanations.
- Allow voice descriptions and voice answers where supported.
- Let users increase thumbnail size or switch to a larger contact-sheet layout.
- Do not rely on colour similarity or face recognition alone.
- Make `Not sure`, `Skip`, and `Exit` as accessible as affirmative actions.
- Support users who remember in non-date formats such as seasons, school terms, festivals, or life stages.
- Avoid assuming that users know venue names, people’s labels, or exact relationships.

## 8. Improve performance without broadening scope

### Technical priorities

1. Precompute lightweight episode features for time, location, sequence density, OCR presence, media type, and recurring visual entities.
2. Use progressive loading: show the memory recap immediately, then hydrate episode thumbnails and evidence.
3. Return a small first set of episodes quickly instead of waiting for exhaustive retrieval.
4. Cache only derived features, not user-facing conclusions that may become stale.
5. Keep the enhanced flow behind explicit memory-reentry entry points so ordinary Photos navigation remains unaffected.

### Performance measures

- Time to first useful episode.
- p95 episode-generation latency.
- Thumbnail loading completion.
- Rate of abandonment before episodes appear.
- Battery and network cost for large libraries.

## 9. Prioritized roadmap

| Priority | Enhancement | Why it matters | MVP timing |
|---|---|---|---|
| P0 | Episode-level ranking | Matches how people remember moments | MVP |
| P0 | Editable memory clues | Keeps imperfect interpretation correctable | MVP |
| P0 | Evidence-based explanations | Builds trust and supports correction | MVP |
| P0 | One-question clarification | Narrows without creating a form | MVP |
| P0 | Near-miss recovery | Prevents restart and abandonment | MVP |
| P1 | Memory strength start | Weights the most reliable cue | Early follow-up |
| P1 | Visual “show me around it” timeline | Enables recognition through context | Early follow-up |
| P1 | Mismatch-dimension feedback | Makes rejection more actionable | Early follow-up |
| P1 | Parallel episode comparison | Helps with ambiguous candidates | Early follow-up |
| P1 | Media-type pivots | Supports documents, screenshots, and videos | Early follow-up |
| P2 | Camera-to-memory bridge | Gives users a physical visual anchor | Later |
| P2 | Trusted-contact memory assist | Uses socially distributed memory | Later, high privacy cost |
| P2 | Durable personal memory graph | Could enable continuity but creates privacy risk | Do not include in MVP |

## 10. What not to add to the MVP

Avoid features that make the concept sound broader but do not directly improve memory recovery:

- A new global search ranking algorithm with no memory-specific interaction.
- A chat assistant that answers questions but does not help users inspect episodes.
- Numeric AI confidence scores.
- Automatic life-event labels.
- Proactive notifications about sensitive memories.
- Large filter panels.
- Social sharing before the single-user flow is validated.
- Endless result scrolling.
- Personalization that is invisible or impossible to correct.

## 11. Recommended next design revision

The strongest next revision should add five elements to the current MVP design:

1. **Memory strength selector** before clarification.
2. **Memory breadcrumb** that persists through episode browsing.
3. **Episode density cues** such as photo count, places, and sequence length.
4. **Optional mismatch reason** after a near miss.
5. **Evidence expansion** for users who want to understand why a moment appeared.

These improvements deepen the distinctive value of Memory Trails without turning it into general search. They make the experience more recognizable, more correctable, and more trustworthy.

## 12. Design success test

The experience is improving if users say:

> “I didn’t know the exact words, but I recognized the moment.”

It is not improving if users say:

> “I had to keep rewriting my query until the system guessed the right keyword.”
