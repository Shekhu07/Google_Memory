# Google Photos Case Study Deck — Evaluator Audit and Slide Heading Options

## Deck reviewed

- **Topic:** Memory Trails for vague-memory retrieval in Google Photos
- **Length:** 10 slides
- **Evaluation criteria:**
  1. Presentation and communication skills
  2. Clarity and depth of thought
  3. Creativity of solution
  4. Data and metrics orientation

## Overall verdict

The current deck follows all four evaluation dimensions **well**, especially in its problem depth, evidence structure, and measurement plan.

The main remaining opportunity is **communication simplicity**. The deck is intellectually strong but sometimes uses research and machine-learning language that a general manager may need to decode. The solution is not to remove the rigour; it is to make every slide answer one simple question:

> **What did we learn, why does it matter, and what decision should we make?**

### Overall assessment

| Evaluation area | Current assessment | Main improvement needed |
|---|---|---|
| Presentation and communication | Strong, but dense | Shorter copy, simpler words, clearer narrative titles |
| Clarity and depth of thought | Very strong | Make the logic easier to follow for a non-specialist reader |
| Creativity of solution | Strong and differentiated | Explain the unique interaction in one memorable sentence |
| Data and metrics orientation | Very strong | Label observed, modelled, proposed, and proxy metrics consistently |

---

# 1. Presentation and communication skills

## Assessment: Strong, with a readability risk

### What the deck does well

- Uses conclusion-style slide titles rather than generic titles.
- Has a clear sequence from business goal to research, root cause, MVP, testing, and risks.
- Uses evidence before presenting the solution.
- Includes customer language, such as:

> “I remember the event and roughly when, but Photos wants a date or keyword I've forgotten.”

- Shows professional ownership through phrases such as:

> “We recommend…”

> “Our next steps…”

> “We propose…”

- Clearly distinguishes proposed A/B testing from observed MVP testing.

### Communication risks

1. Some slides are visually dense, particularly Slides 2, 3, 4, 6, 7, and 10.
2. Terms such as `URR`, `I/S/R`, `Jaccard`, `κ`, `CLIP`, `Moment@5`, and `cue dropout` may distract a non-specialist manager.
3. Some table text is too compressed to be understood quickly during a presentation.
4. The story is clear when read carefully, but the audience may not immediately know the one message to remember from each slide.

### Recommended communication rule

Use the **headline + one-sentence takeaway + evidence** structure:

- **Headline:** What is the conclusion?
- **Takeaway:** Why does it matter?
- **Evidence:** What proves or supports it?

### Language simplifications

| Current type of wording | Clearer alternative |
|---|---|
| “The engine demoted hypothesis ranking and pivoted to failure stages.” | “Our audit showed that failure stages were more reliable than our original hypothesis ranking, so we changed direction.” |
| “Cue dropout level” | “How much of the user’s memory is missing” |
| “Moment@5” | “Correct moment in the top five” |
| “Recall@20” | “Correct photo in the top 20” |
| “Plain CLIP” | “Baseline image similarity” |
| “Failure at I or S” | “The clue was misunderstood or the photo never appeared” |
| “User Retrieval Rate” | “The share of users who eventually reach the photo” |

Keep the technical term in a small footnote or appendix if it is needed for credibility, but use the plain-English version in the main visual.

---

# 2. Clarity and depth of thought

## Assessment: Very strong

This is the strongest dimension of the deck.

### What the deck does well

The deck does not stop at “Google Photos search is difficult.” It decomposes the retrieval journey into:

1. Expressing the memory
2. Interpreting the clue
3. Surfacing the right photo
4. Recognising the right photo
5. Trying again after failure

It then identifies a specific root cause:

> **People keep the episode or rough time but lose the exact date, while Photos primarily indexes items and dates.**

The target segment is also behaviour-based rather than an arbitrary age group:

> Long-time Google Photos users searching for a personal moment they can place only roughly.

The deck further demonstrates good thinking discipline by showing that the audit changed the original direction.

### Remaining improvement

Make the reasoning chain more explicit on every slide:

> **Observation → interpretation → product implication → decision**

For example:

- **Observation:** 40 attempts retained rough time, while 37 lost the date.
- **Interpretation:** Users remember episodes, not calendar values.
- **Product implication:** Search must translate an episode into a time window.
- **Decision:** Build a memory re-entry flow rather than a general search redesign.

This chain is already present in the deck, but it should be easier to see at a glance.

### Recommended sentence to add before the MVP

> **Our decision is to solve the memory-to-recognition gap—not to redesign Search for every query.**

This protects the deck from sounding like a generic search-improvement proposal.

---

# 3. Creativity of solution

## Assessment: Strong and clearly differentiated

### What makes the idea creative

The solution does not simply add another text-search box. It changes the retrieval interaction:

- Rough time becomes a date window.
- Mixed memory clues become editable chips.
- A flat grid becomes grouped visual moments.
- The system explains why a moment appeared.
- The user can reject a moment and recover through nearby moments.
- The user remains the final confirmer.

The clearest product idea is:

> **Help people recognise the moment they remember, rather than forcing them to remember better search terms.**

### Why the solution is differentiated

The deck makes a useful distinction:

- Standard Photos Search helps when the user knows searchable terms.
- Ask Photos helps users ask natural-language questions.
- Memory Trails helps users recognise the intended moment when the answer is only related.

This is a meaningful distinction and avoids claiming that Memory Trails replaces Ask Photos.

### Remaining improvement

Make the creative leap more memorable in one sentence on Slide 7:

> **Memory Trails does not ask the user to describe the photo perfectly; it helps them recognise the right moment from a short trail of possibilities.**

Also make the competitive advantage more precise:

> **Our potential advantage is the combination of Google’s long-lived personal-library signals and a recognition-first interaction—not the data alone.**

### Creativity scorecard

| Creativity question | Answer |
|---|---|
| Does the solution address the defined problem? | Yes: it directly addresses rough time, lost dates, and recognition uncertainty. |
| Is it different from standard search? | Yes: it is an episodic memory re-entry flow, not another keyword-ranking improvement. |
| Does Google have a possible advantage? | Yes: long-term personal-library signals plus Photos context, but this remains a hypothesis to validate. |

---

# 4. Data and metrics orientation

## Assessment: Very strong

### What the deck does well

The deck includes:

- A clear business metric: User Retrieval Rate
- A decomposition of the retrieval journey
- 85,140 public posts collected
- 144 specific failed-search attempts
- 203 audited pairs
- A structured survey of 15 stories
- Six MVP tests
- Modelled retrieval results
- A proposed user-level A/B test
- Early signals for each retrieval stage
- False-confirmation guardrails
- Ship, extend, and stop rules
- Explicit limitations and sample-size caveats

This is significantly stronger than presenting only a feature concept.

### What should be made clearer

The audience must immediately distinguish four types of numbers:

| Label | Meaning | Examples in the deck |
|---|---|---|
| **Observed** | Directly collected or tested | 144 attempts, 15 survey stories, 6 MVP tests |
| **Modelled** | Results from an evaluation library or model | Recall@20, Moment@5 |
| **Proposed** | Future thresholds or targets | URR 40% toward 45%, A/B guardrails |
| **Proxy** | An imperfect stand-in for the real product metric | “Sure they found it” in self-reported testing |

The deck already uses these labels in important places. Keep them visually consistent on every slide.

### Important language fix

Use:

> **The current user-test “sure” score is a self-reported proxy, not production URR.**

Avoid implying that the six-person test measured the true product metric.

### Metrics recommendation

When presenting to managers, lead with only three metrics:

1. **Primary outcome:** Confirmed retrieval / URR
2. **Quality guardrail:** False confirmation
3. **Experience diagnostic:** Time to first useful moment

Keep the remaining diagnostic signals in smaller text or speaker notes.

---

# Plain-English improvement plan

## Use one idea per sentence

Instead of:

> “The audit showed hypothesis agreement was low while failure stage agreement was solid, so the engine demoted hypothesis ranking and pivoted to failure stages.”

Use:

> **Our audit did not reliably support the original hypothesis ranking. It did reliably identify the stage where retrieval failed. We therefore changed the analysis to focus on failure stages.**

## Explain specialist terms once

Recommended first-use definitions:

- **URR:** The share of users who eventually reach the photo.
- **Moment:** A group of related photos from the same episode.
- **False confirmation:** A user says “I found it” but continues searching.
- **Recovery:** What the product does after the first result is wrong.
- **Cue:** A clue from the user’s memory, such as time, place, people, or object.

## Prefer concrete verbs

| Avoid | Prefer |
|---|---|
| “Leverage episodic temporal signals” | “Use the rough time the user remembers” |
| “Improve retrieval efficacy” | “Help more users reach the right photo” |
| “Perform semantic interpretation” | “Understand what the user means” |
| “Surface candidate moments” | “Show nearby moments that may be the right one” |
| “Optimise recognition confidence” | “Help the user decide whether it is the right photo” |

---

# Recommended slide headings: Slides 2–10

The headings below are designed to be **memorable, manager-friendly, and conclusion-led**. They are intentionally shorter and less technical than the current section labels.

## Slide 2 — Discovery methodology

### Recommended heading

> **We turned public complaints into a structured map of failed retrievals**

### Why it works

It explains the value of the discovery engine without leading with “AI.” It also makes the process understandable to a general audience.

### Other heading options

1. **From 85,140 public posts to 144 real retrieval failures**
2. **We did not ask what people felt—we mapped where retrieval broke**
3. **The audit showed us where the search journey breaks**
4. **We converted noisy feedback into comparable evidence**
5. **Before building, we found the failure pattern**

### Best choice

> **We turned public complaints into a structured map of failed retrievals**

---

## Slide 3 — Discovery findings

### Recommended heading

> **People remember the episode, but Search needs the date**

### Why it works

It communicates the central finding in plain English and naturally leads to the root cause.

### Other heading options

1. **The date is forgotten—but the moment is still remembered**
2. **The biggest break happens before users try again**
3. **Users keep “roughly when”; Photos loses the thread**
4. **The problem is not effort—it is the missing date bridge**
5. **Search loses the memory before it can find the photo**

### Best choice

> **People remember the episode, but Search needs the date**

---

## Slide 4 — User research

### Recommended heading

> **When Search fails, people scroll—and still leave unsure**

### Why it works

It combines behaviour and outcome in one sentence.

### Other heading options

1. **Users do not stop remembering; they stop trusting the results**
2. **The workaround is scrolling, but the confidence gap remains**
3. **Most users search with their eyes before they search with words**
4. **People can find something related without finding the right memory**
5. **The last mile is recognition, not typing**

### Best choice

> **When Search fails, people scroll—and still leave unsure**

---

## Slide 5 — Target segment and root cause

### Recommended heading

> **Our target user remembers “when,” but not the calendar date**

### Why it works

It states both the segment and the defining behaviour without requiring the audience to read the table first.

### Other heading options

1. **The right segment is defined by memory state, not age**
2. **Users remember episodes; Photos indexes items and dates**
3. **The missing bridge is between “around then” and a date window**
4. **The root cause: Photos cannot turn rough time into search range**
5. **We are solving a memory mismatch, not a demographic problem**

### Best choice

> **Our target user remembers “when,” but not the calendar date**

---

## Slide 6 — Problem and solution rationale

### Recommended heading

> **We recommend helping users recognise the moment—not write a better query**

### Why it works

It clearly states the product strategy and differentiates the idea from general search improvement.

### Other heading options

1. **The product should follow the user’s memory, not fight it**
2. **From manual scrolling to guided memory re-entry**
3. **The user knows the story; Photos should find the scene**
4. **Our opportunity is the gap between related and right**
5. **Search can ask; Memory Trails helps users recognise**

### Best choice

> **We recommend helping users recognise the moment—not write a better query**

---

## Slide 7 — MVP

### Recommended heading

> **Memory Trails turns a vague memory into a trail of recognisable moments**

### Why it works

It explains the experience without relying on the product name alone.

### Other heading options

1. **From “last Diwali” to the moment the user remembers**
2. **One AI step per failure; the user stays in control**
3. **We turn rough time into a date window, then show the moments**
4. **Not a better grid—a better path back to the memory**
5. **The MVP follows the memory until the user recognises it**

### Best choice

> **Memory Trails turns a vague memory into a trail of recognisable moments**

---

## Slide 8 — User testing

### Recommended heading

> **The MVP helped users find moments—but compound time still breaks it**

### Why it works

It presents both the positive signal and the most important remaining problem.

### Other heading options

1. **Six tests gave us confidence—and three fixes**
2. **Users valued the moment view; the date language needs work**
3. **The interaction works, but “year before last” still fails**
4. **We found the signal, the friction, and the next iteration**
5. **The MVP is promising, not finished**

### Best choice

> **The MVP helped users find moments—but compound time still breaks it**

---

## Slide 9 — Success metrics and experiment

### Recommended heading

> **We will test whether Memory Trails increases confirmed retrieval**

### Why it works

It leads with the outcome rather than the methodology.

### Other heading options

1. **The next decision should be made by retrieval, not clicks**
2. **Our test: more users reach the right photo without false confidence**
3. **From a promising prototype to a measurable product bet**
4. **We will ship only if retrieval rises and false confirmation stays low**
5. **The experiment has one goal and clear guardrails**

### Best choice

> **We will test whether Memory Trails increases confirmed retrieval**

---

## Slide 10 — Risks, limitations, and ask

### Recommended heading

> **The opportunity is real, but we need one controlled test before scaling**

### Why it works

It balances confidence and caution, while leading naturally to the approval request.

### Other heading options

1. **We know what to fix, what to measure, and what could go wrong**
2. **Our next step: fix the weak spots, then test in one market**
3. **A promising direction needs a disciplined launch decision**
4. **Before we scale, we will protect against false confidence**
5. **The recommendation: improve the MVP and run the one-market test**

### Best choice

> **The opportunity is real, but we need one controlled test before scaling**

---

# Recommended final heading set

For a consistent and compelling story, use this set:

| Slide | Recommended heading |
|---:|---|
| 2 | **We turned public complaints into a structured map of failed retrievals** |
| 3 | **People remember the episode, but Search needs the date** |
| 4 | **When Search fails, people scroll—and still leave unsure** |
| 5 | **Our target user remembers “when,” but not the calendar date** |
| 6 | **We recommend helping users recognise the moment—not write a better query** |
| 7 | **Memory Trails turns a vague memory into a trail of recognisable moments** |
| 8 | **The MVP helped users find moments—but compound time still breaks it** |
| 9 | **We will test whether Memory Trails increases confirmed retrieval** |
| 10 | **The opportunity is real, but we need one controlled test before scaling** |

## Story arc created by these headings

> **We mapped the failures → found the missing date bridge → observed the workaround → chose the behavioural segment → recommended recognition over query-writing → built a memory trail → tested it → defined the experiment → requested a controlled next step.**

---

# Final recommendations before submission

## Keep

- The current evidence-first structure.
- The behavioural segment rather than an arbitrary age group.
- The distinction between Ask Photos and Memory Trails.
- The explicit observed/modelled/proposed labels.
- The false-confirmation guardrail.
- The honest limitations.
- The manager-facing “we recommend,” “we propose,” and “our next steps” language.

## Change

1. Replace technical headings with the recommended conclusion-led headings.
2. Add a plain-English explanation beside every technical metric.
3. Keep only three primary metrics visible on Slide 9: confirmed retrieval, false confirmation, and time to first useful moment.
4. Move detailed formulae, reliability statistics, and model definitions into small footnotes or speaker notes.
5. Make the final Slide 10 ask explicit:

> **We ask for approval to fix the three observed issues and run a one-market A/B test.**

6. Ensure every slide has one dominant conclusion that can be repeated verbally.

## Suggested final closing statement

> **Our research shows that people often remember the moment but not the terms Search expects. We recommend Memory Trails as a constrained memory re-entry experience inside Search. We will improve the three observed failure points and validate the idea through a one-market A/B test, using confirmed retrieval as the primary outcome and false confirmation as the launch guardrail.**
