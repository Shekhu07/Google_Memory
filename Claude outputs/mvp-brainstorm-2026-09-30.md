# Memory Trails: brainstorm on how the MVP could be better (30 Sep 2026)

Skills used: product-brainstorming (framing, inversion, SCAMPER), brainstorm-ideas-existing (PM, designer and engineer views), design-critique (on the live screenshots), customer-journey-map, prioritize-features.
Excluded on purpose: anything already in `plans/retrieval-ideas.md` (A1–A7, section B) or the enhancement roadmap, unless it's a new angle on it.

## The frame: the MVP is built for the rememberer we rarely see

Three facts from our own data point the same way:

- **Real people keep few clues.** Of 144 real attempts, 47 kept no usable clue and 79 kept one. Only 6 kept three.
- **The gain sits in the three-clue case.** Memory Trails beats plain search by +0.79 at three clues, +0.07 at one or two, and 0 at none.
- **Only search by what's visible worked.** In the own-library probe, the only natural search that found the photo described something you could see ("orange t-shirt"). Searches by festival, ritual or phase all failed, and every miss was "no idea why".

**How might we help someone holding one clue, or none, reach the photo without asking them to remember more?**

People are much better at *recognising* than *recalling*. The current MVP still starts with recall (describe it, add clues, what feels certain). Most of the ideas below move the work from recall to recognition.

## Design critique of the live flow (screenshots, 28 Sep)

| Finding | Severity | Fix |
|---|---|---|
| The top moment for "sister's graduation" shows a cake reading **"Congratulations James, Class of 2013"** inside a card dated "around Jun 2025". Any grader who looks will see the date contradiction. | 🔴 | Swap that photo out of the demo episode today. It's also a good argument for OCR (idea 6). |
| The moment card is mostly text: title, counts, place, ledger, "why", evidence, button. The thumbnails are about a quarter of the card, and only 2.5 are visible. Recognition is visual. | 🟡 | Pictures first (idea 3). |
| "What part feels most certain?" asks a question about the user's own memory before they have seen any results. People can't judge that from the inside, and it adds a step. | 🟡 | Remove it, or ask it only after a miss. |
| On the "Not this moment" screen, **"'sister's graduation' is ruled out"** reads as if the *clue* was thrown away, not that one moment was. | 🟡 | "This moment is hidden. Your clues are kept. What was off?" |
| "Wrong people" is offered, but the library has no people data. | 🟢 | Remove it until people data exists. |
| On the describe screen, "handwritten note" is offered as a suggested clue for a cake memory. The suggestions aren't about the query. | 🟢 | Suggest from the query, or show none. |
| **Works well:** "Describe the moment, not the photo" is the thesis in five words. The privacy pill, the ✓ ledger, and "from what the images look like, not from any label you gave" are honest and specific. | | Keep all of them. |

## Journey: where the MVP enters, and where it could

| Stage | What the user does | Feeling | Pain | Opportunity |
|---|---|---|---|---|
| Trigger | A doctor, a sibling or nostalgia asks for "that photo" | Urgent or wistful | Needs it now | None; outside the app |
| First search | Types one word (`wedding`, `gym`) | Hopeful | Hundreds of look-alikes, or nothing | Read the query visibly (built as chips, but only inside Memory Trails) |
| **Dead end** | Rephrases or gives up | **Confused: "no idea why"** | No signal about how the query was read | **This is the moment of truth, and the MVP isn't there by default.** Idea 4. |
| Workaround | Scrolls to "roughly then", searches WhatsApp, asks family | Tedious | 7 of 10 scrollers with a known outcome didn't find it | Make scrolling smart (idea 1) |
| Outcome | Found late, not found, or gets the document again | Relief, or real cost | Utility photos have deadlines | OCR for documents (idea 6) |

## Ideas

### PM view

1. **Recognition search by hot and cold ("before or after this?")** — for 0–1 clue users. Show two moment covers from far apart in the library and ask "closer to this one or that one?" Each tap roughly halves the search space, so a 200-moment library is about 8 taps. It needs no typing and no clue, and it is the natural version of scrolling to roughly then, which is what users already do (15 of 21 workarounds). It is different from A6 (tap a trip or month), which still needs you to know the trip or month.
2. **Position Memory Trails as the explanation layer over any search, including Ask Photos.** The chips, the ✓ ledger and "why this moment" don't depend on the ranking model underneath. That answers "why not Ask Photos" without a head-to-head: Google shipped better guessing, and users asked for control (the March 2026 toggle). This gives them control. Zero build; it's a reframe for slides 7 and 8.
3. **Treat the zero-result screen as the entry point (a stronger A5).** Don't wait for the user to find "Can't describe it?". On a failed or thin search, show the reading immediately: *"I read 'pichle saal diwali' as Diwali, Nov 2025. No photo is labelled Diwali, but you took 146 photos that week. See them as moments?"* That is the dead end with a diagnosis, the exact gap the probe found.
4. **The failure metric is really a speed metric.** Most probe misses were found eventually by scrolling. Consider "time to photo" alongside URR: a find that takes 15 minutes is a partial failure. It's cheap to measure in the tests you're about to run (time to "That's the one").
5. **Utility photos as a separate product promise.** The Utility Hunter has the highest cost of failure and the lowest current coverage (text-in-image recall 0.000). Don't stretch Memory Trails to cover them; name a sibling feature (a document shelf with OCR) on the roadmap slide. Scoping it out openly reads as judgement.

### Designer view

6. **Pictures-first moment cards.** Make each card a 3×3 contact sheet with one line underneath (`Pune · Jun 2025 · graduation ✓ cake ✓`). Put the evidence behind a tap. The user recognises the moment in about a second instead of reading a paragraph.
7. **Translate context clues into visible ones, in the open.** When a clue is about context ("haldi", "previous gym", "Diwali"), show what the system will look for: *"haldi → yellow turmeric, marigolds, daytime courtyard"*. It's editable like a chip. This teaches the one lesson the probe found (visible descriptions work) without a tutorial.
8. **Remove the "most certain" question and the "Continue" step.** Go from typing straight to moments, with clues editable on the results page. Two fewer screens. This is the SCAMPER "eliminate" option.
9. **Voice entry.** People describe memories in speech more naturally, and they code-mix ("woh Goa wali trip, Diwali ke baad"). That lowers the effort of describing and gives H4, which is still untested, its first real input. The prototype could use the browser's speech API.

### Engineer view

10. **A visual lexicon for Indian events (CLIP prompt expansion).** CLIP doesn't know what "haldi" or "sangeet" looks like, but it knows "people covered in yellow paste" and "women dancing in a decorated hall at night". A table of about 20 events, each mapped to 2–3 visual prompts, is half a day of work. **You can measure it offline before any user sees it:** write 10–15 tasks that name an Indian event, and compare recall with and without expansion. It's the most testable idea on this list.
11. **Detect life phases from recurring places.** "Previous gym", "old flat" and "first job" are phases, not trips. A place you visited weekly that stops appearing marks the end of a phase. Resolve "previous / old / new X" to that time window. This is what the probe's gym searches needed, and A3 (relative to trips) doesn't cover it.
12. **Use text in the image as a date witness, not only a search target.** The "Class of 2013" cake shows the case: OCR text that contains a year or name can confirm or contradict a moment's date. It raises precision where OCR recall helps least.
13. **Widen time for WhatsApp-origin photos.** In India many wedding and event photos arrive through WhatsApp days or weeks later, and they carry the date they were received (`IMG-YYYYMMDD-WA`). Detect them and widen or shift their window. This is a hypothesis: check with 2–3 test participants whether their event photos came through WhatsApp.
14. **Blur the time around year boundaries.** The only year the probe guessed was off by one, with the real date in January. When a user says "2024", let the window soften into January–February 2025 instead of cutting off. The misdated-memory flag you already built covers conflicts; this covers the edges.

## Top 5 (ranked for the next 7 days)

| # | Idea | Why it made the cut | Effort | Riskiest assumption | Cheapest test |
|---|---|---|---|---|---|
| 1 | **Swap the "James, 2013" cake** | A visible contradiction on the demo's main task. It costs credibility for 10 minutes of work. | 10 min | — | Re-screenshot slide 8 |
| 2 | **Visual lexicon for events (10)** | Straight from the probe; measurable offline; gives the India angle a number instead of a claim | ½ day | CLIP can see the visual signature of these events in the library | 10–15 event tasks, recall with and without expansion |
| 3 | **Pictures-first cards and drop the "certain" step (6 + 8)** | Recognition is the mechanism; fewer screens before value | ½ day | Users recognise from thumbnails without reading the ledger | Time to "That's the one" and evidence-open count in this week's tests |
| 4 | **Explanation layer, not a rival search (2)** | Closes the "why not Ask Photos" gap on the slides with no build | 0 (slides) | Users want to see the reading, not just better results | Ask each tester: "Would you want to see how search read your words?" |
| 5 | **Hot/cold recognition search (1)** | The only idea aimed at the 0–1 clue majority, where the current gain disappears | 1–1.5 days | People can reliably say "closer to A or B" for their own memories | **Paper test in the sessions:** show pairs of moment covers for the task and count the taps to the right month |

**Recommendation:** do 1 today. Do 2 and 3 before the tests on 1–3 Oct, only if they fit in the time you've set aside and don't delay the deck. Put 4 into slides 7 and 8. Test 5 on paper during the sessions, then put it on the roadmap slide as the next iteration with its evidence ("most people keep 0–1 clues; the gain there is +0.07"). That turns the weakest number in the deck into the reason for the next step.

**Set aside for now:** voice (9), phases (11), WhatsApp dates (13), year blur (14), OCR as date witness (12). All are good roadmap lines, but none should be built before 7 Oct. Idea 3 (zero-result entry) waits until the survey says how often people search first.
