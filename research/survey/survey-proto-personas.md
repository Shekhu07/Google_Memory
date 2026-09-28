# Survey proto-personas: 5 hypotheses to test against real responses

> **These are hypotheses, not survey responses.** They predict how 5 kinds of respondent will answer the form *"Finding an old photo — 6 minutes"*. They're built from the discovery engine (144 real hunts) and our own-library probe. Use them to:
> - sort real respondents,
> - check the form tells these people apart,
> - see which predictions hold.
>
> On a slide, call them *"proto-personas (hypotheses)"*, and show real response counts beside them. Never present the predicted answers as data.

---

## The five at a glance

| | Persona | Remembers | Breaks at (the decomposition step it tests) | What they'd want from the product |
|---|---|---|---|---|
| **P1** | **The Phase Rememberer** | a life phase: "when I started bulking", "my old gym" | **Surfacing:** hundreds of near-identical photos | photos just before and after; a rough date range |
| **P2** | **The Festival & Family Archivist** | the event and who was there: "haldi at my cousin's wedding" | **Interpretation:** the event isn't understood as a date | the same trip or event, grouped |
| **P3** | **The Utility Hunter** | words inside the photo and roughly when: "the medicine strip, last monsoon" | **Surfacing:** a document isn't found by its words | better screenshots and documents; text in the image |
| **P4** | **The Ask Photos Sceptic** | a full sentence | **Recognition / recovery:** "related, but not mine", and no idea why | explain why a photo came up; let me correct it |
| **P5** | **The Scroller** | roughly when | **Expression:** never types | help me describe what I remember |

---

## P1 · The Phase Rememberer

**Who:** 20s–30s, fitness routine, 5,000–20,000+ items, mostly look-alike gym and progress shots.
**Memory:** "when I started bulking", "at my previous gym", "around Diwali 2023". Never a date.
**Evidence behind it:** our own probe. Gym photos were found by `gym` only 2 of 3 times, and every phase-based search failed ("my previous gym photos", "2023 sometime during diwali gym pics"). The only natural search that worked described what was visible ("orange t-shirt").
**Would prove it wrong:** P1-type respondents say "Found fairly quickly", or tick *exact date* as remembered.

## P2 · The Festival & Family Archivist

**Who:** any age, family-heavy library of weddings, Diwali, Holi and trips. Often searches in Hinglish.
**Memory:** what was going on (a festival, a wedding ritual) and who was there; forgets the year. Our probe's one year guess was off by one (thought 2024, actually January 2025).
**Evidence behind it:** in the probe, `wedding` and `diwali` found none of the 3 wedding and festival targets, and no recorded natural search found them either ("haldi ceremony", "pichle saal diwali"; one result wasn't recorded). The engine's "clue is misread" failure covers 35% of hunts.
**Would prove it wrong:** respondents with event memories mostly answer "Yes, fairly quickly", or choose "Too many similar results" over "got nothing back / wrong things".

## P3 · The Utility Hunter

**Who:** a working adult or caregiver who photographs prescriptions, bills, IDs and warranty cards as a filing cabinet.
**Memory:** words inside the photo, and roughly when.
**Evidence behind it:** 12 of the 144 hunts remembered text inside the photo. In this segment a failure has a real cost: getting the document again, or missing a deadline.
**Would prove it wrong:** document or medicine respondents answer "No, just annoying", or find it fast by keyword.

## P4 · The Ask Photos Sceptic

**Who:** has Ask Photos, has tried it, and switched back.
**Memory:** a well-phrased sentence. Ask Photos can work here: one real user found an Udaipur restaurant that way.
**Evidence behind it:** the Ask Photos backlash posts in the engine corpus. The failure isn't "no result" but "close, and I can't tell why".
**Would prove it wrong:** most Ask Photos users pick "It found what I wanted quickly", or "I did not have a problem".

## P5 · The Scroller

**Who:** rarely types; scrolls the timeline to "about then". May have been thrown when the app's layout changed.
**Memory:** roughly when.
**Evidence behind it:** scrolling to "roughly when" is a workaround the engine corpus shows people already use. 12 of 144 hunts (8%) said the browse path had moved.
**Would prove it wrong:** very few respondents pick "Scroll back through the timeline" as their first move. If so, drop P5 and fold it into P1 and P2.

---

## Predicted answers, question by question

A blank cell means no strong prediction; "–" means the respondent would skip that question.

| Form question | P1 Phase | P2 Festival/Family | P3 Utility | P4 Ask Photos sceptic | P5 Scroller |
|---|---|---|---|---|---|
| Main app | Google Photos | Google Photos | Google Photos | Google Photos | Google Photos / Both |
| Library size | 5k–20k / 20k+ | 5k–20k / 20k+ | 1k–5k / 5k–20k | 5k–20k | 20k+ |
| Looks for 1yr+ photos | A few times a month | A few times a year (spikes at festivals) | A few times a month | A few times a month | A few times a year |
| First move | Type in search | Type in search, or scroll | Type in search | Type in search | **Scroll the timeline** |
| Happened in last year? | Yes | Yes | Yes | Yes | Yes, but I don't remember when |
| Kind of photo | Ordinary | Ordinary | **Document/receipt, or medicine** | Ordinary | Ordinary |
| Still remembered | Roughly when; **what was going on**; what's in it | **What was going on**; who was with me; roughly when | **Words inside**; roughly when; what's in it | Place name; what's in it; who | Roughly when |
| Forgotten | When; exact words | **When**; which album | Exact words; when | Exact words | Exact words; album |
| What they typed | one word: `gym` | `wedding`, `pichle saal diwali` | `medicine`, `bill` | a full sentence | – (didn't search) |
| Times searched | 2 or 3 | 2 or 3 | 4 or more | 2 or 3 | Did not search |
| Language | English | **Hindi–English mix** | English | English | – (scrolls) |
| AI or normal search | Normal | Normal / don't know | Normal | **Tried both** | – |
| What went wrong | **Too many similar results** | **Got nothing back, or wrong things** | Results looked fine, but mine wasn't there | Results looked fine, but mine wasn't there | **Didn't know what to type** |
| What would help check it | Photos just before/after; date range | **Place / which trip**; who else was nearby | **Words in the image**; date | **A short reason why it came up** | Date range |
| What they did next | Scrolled timeline to about the date | Scrolled timeline; asked someone | **Took the photo / got the document again**; looked in WhatsApp | Switched to normal search | Scrolled through everything |
| Found it? | Right event, not the exact photo | Right event, not the exact photo | No, never | Something similar, but not sure | Yes, but it took long |
| Time spent | 5–15 min | 5–15 min | 15+ min / across days | 5–15 min | 5–15 min |
| Real trouble? | No, just annoying | No, just annoying | **Yes: had to get the document again, or lost time or money** | No, just annoying | No, just annoying |
| Heard of Ask Photos | Heard, not used | Not heard | Heard, not used | **Used it** | Not heard |
| Why not tried | Normal search is enough | Didn't know about it | Don't know what to ask it | – | Rather browse myself |
| Ask Photos worked? | – | – | – | **Related photos, not the one** | – |
| Biggest Ask Photos problem | – | – | – | **Couldn't tell why it showed those** | – |
| What it should do better | Photos before/after | **Same trip or event** | Screenshots and documents | **Explain why; carry on after a wrong result** | Help me describe |

---

## How to use this once real responses come in

1. **Tag each respondent** to the closest persona, using three answers: *kind of photo*, *first move* and *what went wrong*.
2. **Count per persona.** A persona with 0–1 real matches gets dropped or merged; say so on the slide.
3. **Score the predictions.** For each persona, count how many bolded predictions held (e.g. "P2: 4 of 5 held"). Wrong predictions are findings too.
4. **Slides:**
   - **Slide 3:** real counts per persona, plus one anonymous verbatim query each.
   - **Slide 4:** the persona the segment is chosen from, with its real *n*.

## Notes on the form itself

- **Goa example:** the help text for "What were you trying to find?" still uses a Goa example ("the receipt from that shop in Goa"). That's fine for respondents; change it if you'd rather keep Goa out entirely.
- **Personas the form can't separate:** P1 and P2 differ mainly on "what went wrong" (*too many similar* vs *nothing / wrong things*). That's single-choice, so it's clean. There's no gym-type option under "What kind of photo was it?"; P1 people will pick *ordinary*, so use their typed answer to spot them.
- **Library size and tenure:** the screener in the execution plan asks for 2+ years on Google Photos and 5,000+ items. The form has library size but no tenure question, so tenure can't be checked.
