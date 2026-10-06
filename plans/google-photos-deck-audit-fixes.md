# Google Photos Case Study Deck — Audit Fixes

## Audit context

This checklist is based on a review of the submitted 10-slide deck:

- **File reviewed:** `NL_GooglePhotos.pdf`
- **Deck length:** 10 slides
- **Case-study topic:** Google Photos vague-memory retrieval
- **Review criteria:** Case-study discussion feedback, original brief, problem-definition quality, research quality, MVP alignment, experimentation, metrics, risks, and presentation requirements

## Overall assessment

The deck is **substantially strong and mostly follows the discussion guidance**. It is evidence-led rather than solution-led, contains a deeper root-cause analysis than “search is difficult,” includes user research and discovery-engine evidence, demonstrates the MVP, and includes metrics and risks.

It is not fully submission-ready until the P0 fixes below are completed.

---

# P0 — Required before submission

## 1. Correct the A/B-test wording

### Problem

The success-metrics slide currently uses wording similar to:

> “Success is URR rising from 40% to 45% in a user-level A/B test.”

This sounds as if the A/B test has already happened and produced a result. However, the footer says that the thresholds are proposed and not measured results.

### Fix

Replace the title with one of the following:

> **The next test should measure whether Memory Trails lifts confirmed retrieval**

or:

> **The MVP should be evaluated by whether URR can move from 40% toward 45%**

Add this clarification:

> Baseline and target are proposed experiment thresholds, not observed results. The A/B test will validate whether Memory Trails improves confirmed retrieval without increasing false confidence.

### Acceptance criteria

- [ ] No slide implies that the A/B test has already been completed.
- [ ] Baseline, target, and sample-size figures are clearly labelled as proposed.
- [ ] Observed MVP-test results remain separate from future experiment targets.
- [ ] The primary metric is confirmed retrieval, not clicks or feature usage.

---

## 2. Add an explicit rationale for not choosing an age segment

### Problem

The deck correctly defines the segment by memory state and behaviour rather than age, but it does not fully explain why age was not used.

### Fix

Add this sentence to the target-segment slide or speaker notes:

> **We did not choose an age band because the failure is defined by memory state and library behaviour, not by age. Our evidence does not support an age-specific difference, so we use a behavioural segment and will measure age as a diagnostic variable rather than as the targeting rule.**

### Acceptance criteria

- [ ] The deck explains why the segment is behavioural.
- [ ] The deck explicitly answers “Why not age?”
- [ ] Age is not implied to be irrelevant; it is simply not the primary targeting variable.
- [ ] Any future age analysis is described as diagnostic or exploratory unless supported by evidence.

---

## 3. Align the repository source with the submitted Google Photos deck

### Problem

The submitted PDF is a Google Photos deck, but the current repository file:

```text
/home/ubuntu/CaseStudy2/docs/deck/deck-source.html
```

is still an older Myntra wishlist deck. It contains Myntra-specific content, links, metrics, and titles.

### Fix

Do one of the following:

1. Replace the old deck source with the current Google Photos deck source; or
2. Save the Google Photos source under a separate, clearly named path, for example:

```text
/home/ubuntu/CaseStudy2/docs/deck/google-photos-retrieval-deck.html
```

If the Myntra deck is still needed, keep it in a separate folder with an explicit name.

### Acceptance criteria

- [ ] The final Google Photos PDF can be regenerated from the repository source.
- [ ] No Google Photos deck source contains Myntra content.
- [ ] All links in the source point to Google Photos research, survey, discovery-engine, and prototype artefacts.
- [ ] The final source and exported PDF have the same slide order and claims.
- [ ] The repository README identifies the correct final deck source.

---

# P1 — Strongly recommended before submission

## 4. Strengthen the competitor analysis

### Problem

The deck mentions Apple Photos and Ask Photos, but the comparison is brief. The case-study feedback specifically asks why users choose one option over another from the relevant product perspective.

### Fix

Add a compact comparison table or speaker-note explanation:

| Existing option | What it helps with | Remaining gap for vague-memory retrieval |
|---|---|---|
| Standard Photos Search | Known people, places, objects, and dates | Requires the user to convert memory into searchable terms |
| Ask Photos | Natural-language questions | May return related content without helping the user recognise the intended episode |
| Apple Photos | Natural-language visual description | Does not demonstrate the same Google Photos library/context advantage |
| Memory Trails | Rough time/event → date window → visual episode → explanation → recovery | Designed specifically for memory re-entry |

Use this positioning statement:

> **Memory Trails is not competing on better general ranking. It competes on the interaction loop around recognition and recovery.**

### Acceptance criteria

- [ ] The comparison is specific to vague-memory retrieval.
- [ ] Ask Photos is treated as an existing capability, not a straw man.
- [ ] Competitor claims are supported or clearly labelled as hypotheses.
- [ ] The deck explains why users might still need Memory Trails after trying regular Search or Ask Photos.

---

## 5. Make the competitive advantage more defensible

### Problem

The claim that Google “already holds every user's dates, places and faces” and that no standalone app has comparable data is too absolute.

### Fix

Replace it with:

> **Google’s potential advantage is the combination of a long-lived personal library, first-party timestamps, location and people signals, and the ability to connect those signals into visual episodes. This is a hypothesis to validate, not a claim that competitors have no comparable capability.**

Explain that the advantage is not data alone:

1. First-party personal-library data
2. Longitudinal history
3. Existing Photos context signals
4. Episode grouping and recognition UX
5. Evidence-based explanations and recovery

### Acceptance criteria

- [ ] The deck distinguishes a potential advantage from a proven advantage.
- [ ] The competitive advantage includes both data and interaction design.
- [ ] Absolute claims about competitors are removed unless sourced.
- [ ] The advantage is tied directly to the root cause.

---

## 6. Explicitly show the AI-agent loop

### Problem

The MVP uses AI-native behaviour, but the deck does not explicitly map each agent capability to the user problem.

### Fix

Add a small mapping:

| User problem | AI-agent behaviour |
|---|---|
| User remembers only rough time | Converts relative time into a date window |
| User gives mixed clues | Extracts event, object, people, and place cues |
| Flat results are hard to evaluate | Groups photos into visual episodes |
| User is unsure why a result appeared | Generates evidence-based “Why this moment?” explanations |
| Candidate is wrong | Converts rejection into a targeted recovery action |

### Acceptance criteria

- [ ] Each core user failure has a corresponding MVP capability.
- [ ] The AI role is shown as interpretation, grouping, explanation, and recovery—not as generic “AI search.”
- [ ] The human confirmation step remains explicit.
- [ ] The deck does not imply that the system can always identify the correct memory automatically.

---

## 7. Reduce slide density without reducing the font size

### Problem

The deck appears to meet the minimum font-size requirement, but several slides are content-dense. The solution should not be to shrink the font below 14pt.

### Fix

Reduce density by:

- Removing repeated methodology caveats.
- Moving secondary details into speaker notes.
- Keeping one primary insight per slide.
- Shortening long table cells.
- Removing duplicate explanations of sample limitations.
- Increasing whitespace around the main conclusion.

### Suggested slides to simplify

- Slide 2: Discovery engine methodology
- Slide 3: Discovery-engine findings
- Slide 4: User research
- Slide 5: Target segment and root cause
- Slide 6: Problem and solution rationale
- Slide 7: MVP and evaluation data
- Slide 10: Risks and limitations

### Acceptance criteria

- [ ] Minimum font size remains at least 14pt.
- [ ] The slide can be understood from the title and main visual in under 30 seconds.
- [ ] No table requires the audience to read every cell to understand the message.
- [ ] Secondary details are available in speaker notes or linked artefacts.

---

## 8. Improve colour-blind accessibility

### Problem

The deck uses blue, orange, green, and red. Most meaning is also written as text, but some status distinctions rely strongly on colour.

### Fix

- Add text labels such as `Supported`, `Refined`, `Not tested`, and `Risk`.
- Avoid using red and green as the only distinction between outcomes.
- Add icons, symbols, or patterns where practical.
- Check contrast for small text and coloured panels.
- Keep colour as a reinforcement, not the primary carrier of meaning.

### Acceptance criteria

- [ ] Every colour-coded status also has a text label.
- [ ] Green/red outcomes remain understandable in grayscale.
- [ ] Body text and labels have sufficient contrast.
- [ ] No conclusion depends only on colour.

---

# P2 — Recommended polish

## 9. Add a direct customer-perspective problem statement

The deck already contains a strong root-cause statement. Make it more prominent by adding a short customer-first version:

> **When I remember a photo only through its event, people, or approximate time, Google Photos makes me translate that memory into exact search terms—and leaves me unsure when the results are merely related.**

This can appear above or beside the current analytical problem statement.

---

## 10. Clarify that the research is directional

The deck already discloses the sample sizes and limitations. Add the word **directional** to the main user-research heading or subtitle:

> **Directional user research shows what people remember and forget**

Recommended wording:

> Our survey and MVP tests identify patterns and failure modes; they do not estimate population prevalence.

---

## 11. Separate measured results from modelled results

Create a consistent visual label system:

- **Observed:** discovery-engine counts, survey responses, six MVP test outcomes
- **Modelled:** URR decomposition and retrieval-score estimates
- **Proposed:** A/B targets, guardrails, and launch thresholds
- **Hypothesis:** Google data advantage and expected production lift

This avoids confusion between research evidence and future assumptions.

---

## 12. Make the MVP boundary explicit

Keep this statement visible in the MVP slide or speaker notes:

> **This MVP validates the memory-re-entry interaction and recovery model. It does not validate production-scale Google Photos retrieval accuracy.**

Also retain the boundaries:

- No universal search redesign
- No proactive sensitive-memory surfacing
- No permanent inferred life-event profile
- No promise that every memory can be recovered

---

# Claims to review before final export

Check every number and external claim against its source:

- [ ] 1.5B+ Google Photos users
- [ ] 9T+ photos and videos stored
- [ ] 370M+ monthly searchers
- [ ] 150M Google One subscribers
- [ ] 85,140 public posts
- [ ] 144 specific failed searches
- [ ] 203 audited pairs
- [ ] Survey n=15 / 14 deduplicated
- [ ] MVP testing n=6
- [ ] 40% baseline and 45% target
- [ ] Approximately 1,600 users per A/B arm
- [ ] Apple Photos comparison
- [ ] Ask Photos comparison
- [ ] Google data advantage claim

Use source labels directly on the slide or in speaker notes. Do not present modelled or proposed values as measured outcomes.

---

# Final acceptance checklist

## Story and reasoning

- [ ] The deck begins with the customer retrieval problem, not only Google’s business value.
- [ ] The business metric is explained clearly.
- [ ] Evidence appears before the MVP.
- [ ] The target segment is behavioural and justified.
- [ ] The deck explicitly answers why this segment was selected.
- [ ] The root cause is more precise than “search is difficult.”
- [ ] The solution directly addresses the root cause.

## Research and AI discovery engine

- [ ] Discovery-engine process is understandable.
- [ ] AI is shown as a structuring tool, not the source of creative product thinking.
- [ ] Human audit and decision-making are visible.
- [ ] Survey findings are labelled directional.
- [ ] MVP test findings are separated from population claims.
- [ ] User behaviour and workarounds are clearly described.

## Product and competitive advantage

- [ ] The MVP flow is easy to understand.
- [ ] The AI-agent loop is explicit.
- [ ] Ask Photos appears as an existing capability and comparator.
- [ ] Competitor analysis is specific to vague-memory retrieval.
- [ ] Google’s advantage is framed as a hypothesis supported by data plus product experience.
- [ ] The MVP is not presented as a generic search improvement.

## Measurement and risk

- [ ] The primary success metric is confirmed retrieval.
- [ ] A/B testing is presented as a future test unless already run.
- [ ] Observed, modelled, proposed, and hypothesised values are distinguished.
- [ ] False confirmation is a guardrail.
- [ ] Sensitive-memory privacy risk is addressed.
- [ ] Risks and mitigations are included on the final slide.

## Presentation quality

- [ ] Exactly 10 slides.
- [ ] Minimum font size remains at least 14pt.
- [ ] Titles communicate the slide’s conclusion.
- [ ] No slide is unnecessarily dense.
- [ ] Colour is not the only way meaning is conveyed.
- [ ] Links to the discovery engine, survey, prototype, and research artefacts work.
- [ ] The final PDF matches the repository source.
- [ ] The final PDF is below 40 MB.

---

# Priority summary

## Must fix

1. Correct the A/B-test wording.
2. Add the explicit age-segment rationale.
3. Align the repository source with the Google Photos PDF.

## Should fix

4. Strengthen competitor analysis.
5. Make the competitive advantage more defensible.
6. Map the AI-agent loop to user problems.
7. Reduce density without reducing font size.
8. Improve colour-blind accessibility.

## Good to polish

9. Make the customer-perspective problem statement more prominent.
10. Label research as directional.
11. Separate observed, modelled, proposed, and hypothesised claims.
12. Restate the MVP boundary.

## Final product thesis

> **Help people recognise the moment they remember—not force them to remember better search terms.**

The current deck supports this thesis. The fixes above make the reasoning more precise, the claims more defensible, and the submission safer against evaluator questions.
