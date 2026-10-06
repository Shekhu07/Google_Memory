# Google Photos Deck — Point-of-View Language Fixes

## Purpose

The case study positions the presenter as a **Product Manager on the Core Experience team at Google Photos**. The deck should therefore sound like a PM presenting an evidence-backed recommendation to Google Photos managers.

The current deck is mostly written in an objective, third-person research style. That is appropriate for describing user behaviour and evidence, but the deck needs more deliberate **first-person plural ownership** when presenting:

- The team’s interpretation
- The product recommendation
- The MVP decision
- The experiment plan
- The next steps

## Recommended language model

Use a deliberate blend rather than rewriting the entire deck into first person.

| Content type | Preferred POV | Example |
|---|---|---|
| User behaviour | Third person | “Users remember the event but lose the exact date.” |
| Research evidence | Neutral or first-person plural | “Our survey shows that 9 of 15 participants scrolled first.” |
| Customer voice | First person inside quotation marks | “I remember the event and roughly when…” |
| Product recommendation | First-person plural | “We recommend placing Memory Trails inside Search.” |
| Experiment plan | First-person plural | “We will test whether the flow increases confirmed retrieval.” |
| Uncertainty or hypothesis | First-person plural plus qualification | “Our hypothesis is that…” |
| Competitors | Third person | “Rivals could build a similar interaction.” |

## Core principle

> **Use third person for evidence, first-person plural for decisions, and first person inside quotes for the user’s voice.**

Do not use first person merely to make every sentence sound personal. Use **“we”** when the team owns a decision or recommendation.

---

# P0 — Required language fixes

## 1. Make the strategic goal team-owned

### Current style

> Goal: more users retrieve a photo they remember but can’t precisely describe.

### Recommended wording

> **Our goal is to increase the number of users who successfully retrieve a photo they remember but cannot precisely describe.**

### Why

This makes the strategic objective sound like a Core Experience team goal rather than an external observation.

---

## 2. Make the segment choice sound like a deliberate team decision

### Current style

> Why not an age band? The failure comes from memory state and library habits, not age, and nothing in our evidence points to an age gap. Age is a diagnostic cut in the A/B, not the targeting rule.

### Recommended wording

> **We did not choose an age band because our evidence points to memory state and library habits—not age—as the relevant driver. We will use age as a diagnostic cut in the A/B test, not as the targeting rule.**

### Why

This directly answers the manager’s likely question:

> “Why did we choose this segment?”

It also makes clear that the absence of an age segment was a considered decision, not an omission.

---

## 3. Turn the problem-to-product conclusion into a recommendation

### Current style

> So the product should find the time window and group the moments for them.

### Recommended wording

> **We recommend that Photos take this manual step for the user: convert the rough time cue into a date window and group the surrounding moments.**

### Why

This preserves the customer insight while making the PM recommendation explicit.

---

## 4. Rewrite the Google advantage statement

### Current style

> Why Google could win Hypothesis years of each user's own dates, places and faces, joined into moments by the UX. Rivals could build it too.

### Recommended wording

> **Our hypothesis for why Google can win:** we can combine long-term personal-library signals—dates, places, and people—with an episode-recognition experience. The advantage is not the data alone; competitors could build a similar interaction. We need to validate whether this combination improves confirmed retrieval.

### Why

The current wording is grammatically awkward and sounds distant. The revised version:

- Clearly identifies the team’s hypothesis.
- Avoids overstating Google’s competitive advantage.
- Shows what still needs to be validated.
- Sounds appropriate for a manager-facing recommendation.

---

## 5. Make the MVP placement a team recommendation

### Current style

> It sits inside search, where the failure happens.

### Recommended wording

> **We recommend placing Memory Trails inside Search, where the failure currently happens.**

### Why

The current sentence describes the location of the feature. The revised sentence communicates a product decision.

---

## 6. Make the AI-agent design decision explicit

### Current style

> Each failure gets one AI step; the person confirms.

### Recommended wording

> **Our MVP assigns one AI capability to each observed failure, while keeping the final confirmation with the user.**

### Why

This makes the team’s design philosophy clear:

- AI interprets and organizes.
- The user remains the authority.
- The product does not auto-confirm an uncertain memory.

---

## 7. Make the next-version fixes team-owned

### Current style

> Three fixes for the next version

### Recommended wording

> **Based on the six observed tests, we will address three issues before the next version:**

1. Compound-time parsing
2. More visible clues
3. Faster loading through pre-cached moments

### Why

This connects the fixes to evidence and shows that the team has an action plan.

---

## 8. Make the experiment plan sound like an owned decision

### Current style

> Planned test, not yet run: 8 weeks, randomised by user; ~1,600 users per arm for 80% power at α 0.05.

### Recommended wording

> **We propose an eight-week user-level A/B test, not yet run, with approximately 1,600 users per arm for 80% power at α = 0.05.**

### Why

This keeps the important caveat that the test has not run, while making the proposal explicit.

---

## 9. Make ship/extend/stop ownership explicit

### Current style

> Ship, extend or stop is decided in advance.

### Recommended wording

> **We will decide in advance when to ship, extend, or stop the experiment.**

### Why

This shows experimental discipline and makes ownership clear.

---

## 10. Make the final next steps manager-facing

### Current style

> Next: compound dates, clearer clues, a one-market test.

### Recommended wording

> **Our next steps are to improve compound-date parsing, make active clues clearer, and run the A/B test in one market.**

### Why

A manager should leave the presentation knowing exactly what the team recommends doing next.

---

# P1 — Recommended language improvements

## 11. Add a customer-first problem statement in the team’s framing

Keep the customer quote in first person:

> “I remember the event and roughly when, but Photos wants a date or keyword I’ve forgotten.”

Then follow it with a team interpretation:

> **We interpret this as a memory-to-recognition problem, not a generic search-quality problem.**

This creates a useful transition from customer evidence to PM judgment.

---

## 12. Clarify what the team has learned

Where the deck currently says:

> “The audit changed the answer.”

Consider:

> **Our audit changed the direction: the largest actionable break was before retry, at interpretation and surfacing—not only at recovery.**

This makes the thought process sound owned and explicit.

---

## 13. Clarify the relationship with Ask Photos

Recommended wording:

> **Ask Photos already helps users express natural-language questions. Our opportunity is different: we help users recognise and navigate the surrounding episode when the first answer is related but not the intended moment.**

This avoids presenting Ask Photos as inadequate and clearly defines the complementary role of Memory Trails.

---

## 14. Make uncertainty explicit in the team voice

Use:

> **Our current evidence supports the direction, but it does not yet establish production-scale retrieval lift.**

Avoid:

> “This will improve retrieval.”

Use:

> **We will validate whether it improves confirmed retrieval in a controlled experiment.**

This distinction is especially important for manager-level communication.

---

# P2 — Optional polish

## 15. Add a short presenter-style transition on selected slides

These can be used as slide subtitles or speaker notes, not necessarily as visible slide copy.

### After research

> **What this tells us:** users often remember an episode, but Search asks them to reconstruct exact terms.

### After segment selection

> **Our decision:** start with users who retain a rough time or event cue but lose the date.

### Before MVP

> **Our recommendation:** build a memory re-entry loop around recognition and recovery.

### Before testing

> **Our testable claim:** grouping moments and preserving the user’s mental thread should improve confirmed retrieval.

### Before final slide

> **Our decision request:** approve a constrained one-market test after the three next-version fixes are addressed.

---

# Language to preserve

The following language is already appropriate and should remain:

## Customer voice

> “I remember the event and roughly when…”

> “I scroll by hand, and even then I’m not sure the photo I found is the one.”

## Evidence language

> “A directional survey…”

> “The A/B has not yet run.”

> “Modelled…”

> “Observed…”

> “The evidence is small and mostly self-reported.”

> “Rivals could build it too.”

These phrases demonstrate honesty and should not be replaced with overconfident first-person claims.

---

# Language to avoid

Avoid making the deck sound like a generic report, a product advertisement, or an overconfident AI pitch.

## Avoid overly distant report language

- “The product should…”
- “Why Google could win…” without a hypothesis label
- “Next: …” without an owner
- “It sits inside Search…” without a recommendation

## Avoid unsupported certainty

- “This will solve vague-memory retrieval.”
- “Google has data competitors do not have.”
- “The A/B proves the feature works.”
- “Users prefer Memory Trails.”

## Avoid excessive first person

- “I think…”
- “I believe…”
- “I decided…” on every slide
- “We know…” when the evidence is only directional

Use **“we recommend,” “our evidence suggests,” “our hypothesis is,” and “we will validate.”**

---

# Slide-by-slide POV checklist

## Slide 1 — Business metric

- [ ] Change the goal to “Our goal is…”
- [ ] Keep users and the business in third person elsewhere.
- [ ] Avoid introducing the MVP as if it is already approved.

## Slide 2 — Discovery engine

- [ ] Keep the methodology objective.
- [ ] Add “Our audit…” only where explaining the team’s interpretation.
- [ ] Keep the AI process factual and non-promotional.

## Slide 3 — Discovery findings

- [ ] Keep findings in third person.
- [ ] Use “Our evidence supports…” only in the conclusion or speaker notes.

## Slide 4 — User research

- [ ] Keep participant quotes in first person.
- [ ] Keep results in third person or neutral wording.
- [ ] Use “Our survey shows…” where the team is interpreting the data.

## Slide 5 — Target segment and root cause

- [ ] Add “We did not choose an age band…”
- [ ] State why the behavioural segment was selected.
- [ ] Use “Our evidence points to…” for the segment rationale.

## Slide 6 — Problem and solution rationale

- [ ] Use the customer quote unchanged.
- [ ] Change “the product should” to “we recommend.”
- [ ] Rewrite “Why Google could win” using the proposed hypothesis wording.

## Slide 7 — MVP

- [ ] Change “It sits inside…” to “We recommend placing…”
- [ ] Change “Each failure gets one AI step…” to “Our MVP assigns…”
- [ ] Keep “Modelled” clearly separate from observed findings.

## Slide 8 — User testing

- [ ] Change “Three fixes for the next version” to “We will address…”
- [ ] Keep tester quotes in first person.
- [ ] Keep test outcomes objective and labelled observed.

## Slide 9 — Success metrics

- [ ] Change “Planned test” to “We propose…”
- [ ] Keep “not yet run” visible.
- [ ] Change “Ship, extend or stop is decided…” to “We will decide…”
- [ ] Keep proposed thresholds separate from observed results.

## Slide 10 — Risks and next steps

- [ ] Change “Next:” to “Our next steps are…”
- [ ] Add a clear recommendation or decision request if appropriate.
- [ ] Keep limitations objective and transparent.

---

# Final acceptance criteria

The deck is POV-ready when:

- [ ] User behaviour is described in third person.
- [ ] Customer quotes remain in first person.
- [ ] Team interpretations use “our evidence” or “our findings” where useful.
- [ ] Recommendations use “we recommend.”
- [ ] Experiment plans use “we propose” or “we will test.”
- [ ] Next steps use “we will.”
- [ ] Hypotheses are clearly labelled as hypotheses.
- [ ] The deck does not use “I” repeatedly or sound personally opinionated.
- [ ] The presenter sounds like a Core Experience PM owning a product decision.
- [ ] The deck still preserves an evidence-led and appropriately cautious tone.

## Final recommended voice

> **Our research shows that users remember episodes but lose the exact terms Search expects. We recommend Memory Trails as a constrained memory re-entry experience inside Search. We will validate it through a one-market A/B test, using confirmed retrieval as the primary outcome and false confirmation as the launch guardrail.**
