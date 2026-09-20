# Memory Trails MVP — Design Specification

## 1. Design intent

Memory Trails is a focused **memory re-entry experience** for Google Photos. It helps a user recognize and enter an old visual episode when they remember the moment but cannot precisely describe the photo.

It is not a redesign of Google Photos Search. The experience should therefore feel like a calm, temporary mode for reconstructing a memory—not like an advanced search form, a chatbot transcript, or a dashboard.

### Product promise

> **Start with what you remember. We’ll help you recognize the moment.**

### Design qualities

The interface should feel:

- **Reassuring:** imperfect recollection is expected.
- **Visual:** recognition through thumbnails and sequences comes before text-heavy filtering.
- **Grounded:** the UI shows evidence without pretending inference is certainty.
- **Lightweight:** one useful question at a time, not a questionnaire.
- **Reversible:** every clue can be removed, every near miss can be corrected, and exiting changes nothing in the library.

## 2. Experience principles

### 2.1 Recognition over recall

Use representative images, surrounding photos, date ranges, and place context to help users recognize a moment. Do not ask users to translate their memory into the system’s taxonomy before they see anything useful.

### 2.2 The memory remains visible

Keep the user’s original recollection and current clues available throughout the flow. The user should never wonder what the system is currently trying to find.

### 2.3 One question, only when useful

Ask one optional follow-up question when it can materially separate candidate episodes. Always provide `Not sure` and `Skip`. Do not turn the feature into a multi-step intake form.

### 2.4 Evidence, not certainty

A candidate episode should say why it appeared using available evidence:

- `Goa location`
- `Text detected in some images`
- `Nearby sequence`
- `Food-like indoor scenes`
- `Photos grouped around 14–18 Dec 2023`

Avoid model-confidence percentages, invented narratives, and unsupported claims about the user’s life.

### 2.5 Near misses are progress

A wrong episode is useful if the user can say what was wrong. Recovery actions must change one dimension at a time and preserve the original memory.

### 2.6 Explicit and private by default

The user explicitly starts the flow. The product must not proactively surface sensitive memories or create permanent inferred events from the session.

## 3. Visual direction

### 3.1 Overall style

Use a **quiet gallery** aesthetic: warm off-white surfaces, dark graphite text, soft blue as the action colour, and generous image-led cards. The experience should sit naturally within Google Photos without copying every standard Photos screen.

Avoid:

- Dense analytics or filter-panel layouts.
- Chat bubbles as the primary structure.
- Heavy gradients and decorative AI effects.
- Excessive borders around every element.
- “Magic” language or glowing confidence badges.

### 3.2 Colour tokens

| Token | Value | Use |
|---|---|---|
| `--page` | `#F7F8FA` | Memory Trails background |
| `--surface` | `#FFFFFF` | Cards, sheets, inputs |
| `--surface-subtle` | `#F1F4F8` | Recap panel, secondary controls |
| `--ink` | `#202124` | Primary text |
| `--ink-soft` | `#5F6368` | Secondary text |
| `--ink-muted` | `#80868B` | Supporting metadata |
| `--line` | `#E3E6EA` | Hairlines and card borders |
| `--blue` | `#1A73E8` | Primary action, selected state, links |
| `--blue-soft` | `#E8F0FE` | Selected chips, selected episode |
| `--blue-dark` | `#185ABC` | Pressed/hover text |
| `--green` | `#18866B` | Privacy reassurance and positive completion |
| `--amber-soft` | `#FFF4E5` | Approximation or caution state |
| `--scrim` | `rgba(32,33,36,.42)` | Bottom-sheet backdrop |

Use the blue token for intent and navigation, not for every label. Use green only for privacy or successful confirmation. Never use red to indicate that a memory is wrong; a near miss is not an error.

### 3.3 Typography

Use the Google Sans / system sans stack where available:

```css
font-family: "Google Sans", "Google Sans Text", Inter, system-ui, sans-serif;
```

| Role | Size | Weight | Line height |
|---|---:|---:|---:|
| Page title | 28–32 px | 600 | 1.12 |
| Section title | 18–20 px | 600 | 1.2 |
| Body | 15–16 px | 400 | 1.45 |
| Supporting text | 13–14 px | 400 | 1.4 |
| Eyebrow / label | 11–12 px | 600 | 1.2 |
| Button | 14 px | 600 | 1 |
| Metadata | 12–13 px | 500 | 1.25 |

Avoid all-caps body copy. Use sentence case for questions, buttons, and explanations. Eyebrow labels may use uppercase with letter spacing when they help establish hierarchy.

### 3.4 Shape and elevation

- Base radius: `12px` for controls and compact cards.
- Large radius: `20px` for episode cards and mobile sheets.
- Full pill radius for clue chips and privacy status.
- Use one soft shadow level for elevated sheets and selected episode cards:

```css
box-shadow: 0 10px 30px rgba(32, 33, 36, 0.10);
```

Prefer surface contrast and spacing over hard borders. Use a 1px border only where it improves grouping or field affordance.

## 4. Layout system

### 4.1 Desktop

- Maximum content width: `1120px`.
- Two-column composition:
  - Main content: `minmax(0, 1fr)`.
  - Context rail: `320–360px` when showing memory recap or help.
- Page gutter: `32px` at 1024px and above.
- Primary episode cards use full available width; thumbnails may run in a horizontal strip.

```text
┌─────────────────────────────────────────────────────────────┐
│ Top bar                                                     │
├──────────────────────────────────┬──────────────────────────┤
│ Memory Trail content              │ Memory recap / help     │
│ 640–760px                         │ 280–340px               │
└──────────────────────────────────┴──────────────────────────┘
```

### 4.2 Mobile

- Single column.
- Page gutter: `16px`.
- Keep the original memory in a compact sticky context row beneath the top bar.
- Use a bottom sheet for clarifying questions and recovery actions.
- Keep the primary action within thumb reach and visible without excessive scrolling.
- Use horizontal scrolling for thumbnail sequences; do not shrink images until they become unrecognizable.

### 4.3 Responsive breakpoints

| Breakpoint | Behavior |
|---|---|
| `< 600px` | Single column, bottom sheets, horizontal thumbnail rails |
| `600–899px` | Single column with wider cards and inline recap |
| `900–1199px` | Two-column layout; recap rail may remain sticky |
| `≥ 1200px` | Two-column layout with wider episode imagery and stable max width |

## 5. Screen designs

### 5.1 Find a memory

#### Purpose

Start the user from a memory-shaped prompt instead of a generic search field.

#### Layout

```text
┌──────────────────────────────────────────┐
│ ×                         Find a memory  │
│                                          │
│ Start with what you remember             │
│ Describe a moment. It doesn’t have to    │
│ be exact.                                │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ A small café during our Goa trip…    │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ Try a memory like                         │
│ [the medicine photo from last year]      │
│ [a birthday at home]                     │
│ [that beach trip with my cousins]        │
│                                          │
│                           [Continue]     │
└──────────────────────────────────────────┘
```

#### Components

- `MemoryTopBar`
- `MemoryPromptField`
- `ExampleMemoryChip`
- `PrimaryButton`
- `PrivateByDefaultNote`

#### Behavior

- The prompt field is the visual focus on entry.
- Examples populate the field but do not submit automatically.
- The primary button label is `Continue`, not `Search`.
- A close action exits without changing the library.

### 5.2 Memory recap

#### Purpose

Show how the system interpreted the recollection and allow correction before episode exploration.

#### Layout

```text
┌──────────────────────────────────────────┐
│ ←                          Your memory   │
│                                          │
│ Here’s what I heard                      │
│ “A small café during our Goa trip”       │
│                                          │
│ Memory clues                              │
│ [Goa ×] [café / food ×] [trip ×]         │
│                                          │
│ Some clues may be approximate.            │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ One question may help narrow this    │ │
│ │ Do you remember where it was?        │ │
│ │ [Near the beach] [In a town]         │ │
│ │ [Not sure]                            │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ [Show moments]                           │
└──────────────────────────────────────────┘
```

#### Visual rules

- Use a pale blue-gray panel for the recap, separating system interpretation from user content.
- Clues are white pills with a thin blue border. The remove control must be inside the pill and accessible.
- Clarifying question is a white card inside the recap panel; it should not resemble a chat message.
- `Not sure` is a secondary option, not a disabled fallback.

### 5.3 Likely moments

#### Purpose

Present a small set of episode candidates that users can visually recognize.

#### Episode card anatomy

```text
┌──────────────────────────────────────────┐
│ Goa · 14–18 Dec 2023         18 photos  │
│ Beach + food sequence                    │
│                                          │
│ [large] [large] [large] [large]          │
│                                          │
│ Why this moment?                         │
│ Goa location · café-like scenes ·       │
│ short travel sequence                    │
│                                          │
│                              [Open]      │
└──────────────────────────────────────────┘
```

#### Visual rules

- Show 3–5 episodes; each card must be scannable in under three seconds.
- Use a 4:3 or square thumbnail crop consistently within a sequence.
- Let the strongest candidate have a blue outline, not a large “Best match” badge.
- Keep explanations compact and evidence-led.
- Place `Open moment` at the bottom-right on desktop and as a full-width reachable action on mobile.
- Keep clues visible above the episode list in a compact horizontal rail.

### 5.4 Episode view

#### Purpose

Let the user enter the surrounding sequence and recognize the target photo.

#### Visual hierarchy

1. Episode title and date/place context.
2. Large selected image.
3. Sequence scrubber or thumbnail rail.
4. Evidence/context row.
5. Explicit confirmation and rejection actions.

#### Actions

- Primary: `That’s the one`
- Secondary: `Not this moment`
- Utility: `Open in Photos viewer`, if available

The system must not auto-confirm the selected image. The user owns the recognition decision.

### 5.5 Recovery sheet

#### Purpose

Make near misses productive.

#### Layout

Use a bottom sheet on mobile and a right-side sheet or modal on desktop:

```text
┌──────────────────────────────────────────┐
│ Not the right moment?                    │
│ Keep the memory and try:                 │
│                                          │
│ [Same place, different day]              │
│ [Same trip, different place]             │
│ [Earlier]                                │
│ [Later]                                  │
│ [More like these photos]                 │
│ [Change a memory clue]                   │
│                                          │
│ [Cancel]                                 │
└──────────────────────────────────────────┘
```

Each action should have a clear noun or dimension. Avoid generic `Try again` copy.

## 6. Component inventory

### Navigation

- `MemoryTopBar`: close/back action, title, optional privacy indicator.
- `MemoryContextRail`: persistent original recollection and current clues.
- `ExitConfirmation`: only needed if the user has an unfinished episode state; exiting should otherwise be immediate.

### Input and interpretation

- `MemoryPromptField`: multiline field with optional microphone affordance.
- `MemoryExampleChip`: fills the prompt field.
- `ClueChip`: editable/removable inferred cue.
- `ClueEditSheet`: simple edit control for one clue.
- `ClarifyingQuestionCard`: one question, 2–4 options, `Not sure`, and `Skip`.

### Episode discovery

- `EpisodeCard`: episode context, thumbnails, explanation, open action.
- `ThumbnailRail`: horizontally scrollable sequence of photos/videos.
- `EvidenceNote`: short grounded explanation.
- `MomentCount`: neutral metadata such as `18 photos · 3 places`.
- `EmptyMomentsState`: controlled expansion options and safe exit.

### Episode inspection

- `EpisodeHeader`
- `HeroMedia`
- `EpisodeScrubber`
- `RetrievalActions`
- `RecoverySheet`
- `ConfirmationToast`

## 7. Motion and state transitions

Motion should communicate continuity, not spectacle.

| Transition | Motion |
|---|---|
| Entry → recap | 180ms fade/slide up |
| Recap → moments | 180ms crossfade; preserve clue rail position |
| Episode open | 220ms card-to-detail expansion |
| Recovery sheet | 220ms bottom-sheet rise |
| Clue removal | 150ms opacity + slight scale; reflow naturally |
| Retrieval confirmation | 180ms toast and subtle check state |

Respect `prefers-reduced-motion`. Do not animate thumbnail grids with staggered effects; the user is scanning visual content and needs stability.

## 8. Copy system

### Preferred language

- `Find a memory`
- `Start with what you remember`
- `Here’s what I heard`
- `Some clues may be approximate`
- `Likely moments`
- `Why this moment?`
- `Open moment`
- `Not this moment`
- `Keep the memory and try`
- `Not sure`
- `I couldn’t find a moment that feels right`

### Avoid

- `Search query`
- `AI result`
- `Confidence: 87%`
- `Perfect match`
- `We know this is...`
- `Improve search`
- `Try again`
- `No results` as the only empty-state message

## 9. Accessibility

- Use semantic headings in the order: page title → section title → episode title.
- Give each thumbnail an accessible label containing episode, relative position, and available context.
- Make clue removal buttons individually labelled, for example `Remove clue Goa`.
- Provide a text alternative for every evidence note.
- Ensure the `Not sure` and `Exit` paths are keyboard reachable and visually equivalent in prominence to affirmative paths.
- Maintain at least 44×44px touch targets.
- Meet WCAG AA contrast for body text and controls.
- Never use thumbnail colour or visual similarity as the only way to distinguish episodes.
- Keep the selected episode state visible to screen readers with a polite status update.

## 10. Privacy and trust

### Product behavior

- The flow is user-initiated.
- No inferred memory becomes a durable label by default.
- Medical, relationship, and location-related memories are not proactively promoted.
- Shared album and partner-sharing behavior should follow existing Google Photos permissions.
- The user can exit without saving the memory description or inferred clues.

### UI treatment

Display a compact reassurance near the entry point:

> `Private by default · only searches when you ask`

Do not use alarmist warnings that make ordinary memory retrieval feel dangerous. The privacy treatment should be calm, visible, and specific.

## 11. Responsive acceptance criteria

### Mobile

- The user can complete the core path with one hand.
- The prompt, clue rail, and primary action are reachable without confusing scroll jumps.
- Episode thumbnails remain recognizable at 320px viewport width.
- Recovery options use a bottom sheet with clear dismissal.

### Desktop

- Episode cards and thumbnails use the additional horizontal space for context, not for a dense multi-column grid.
- The memory recap remains visible while episodes are scanned.
- The episode inspection view keeps the media and timeline aligned.

## 12. Prototype data assumptions

The visual prototype may use illustrative content for:

- Date ranges.
- Place labels.
- Thumbnail imagery.
- OCR snippets.
- Episode counts.
- Evidence explanations.

Prototype copy must label these as examples through the surrounding context and must not imply access to a real user’s Google Photos library.

## 13. MVP design checklist

- [ ] Dedicated `Find a memory` entry point, separate from general Search.
- [ ] Memory-shaped prompt and examples.
- [ ] Editable clue recap.
- [ ] One optional clarifying question.
- [ ] `Not sure` and `Skip` paths.
- [ ] Episode cards with recognizable sequences.
- [ ] Grounded “Why this moment?” explanations.
- [ ] Episode inspection with explicit user confirmation.
- [ ] Near-miss recovery without restart.
- [ ] Controlled no-match state.
- [ ] Explicit-search privacy behavior.
- [ ] Mobile-first and accessible interaction states.
- [ ] Instrumentation for retrieval confirmation, rejection, recovery, and abandonment.

## 14. Core design decision

The MVP should make the user feel:

> **“I’m getting back into the memory.”**

It should not make the user feel:

> **“I’m struggling to write the perfect search query.”**

That distinction is the design guardrail for every screen, component, and interaction in Memory Trails.
