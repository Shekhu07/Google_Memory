# Google Photos case study: new-skills cross-check (30 Sep 2026)

Deadline: **Wed 7 Oct, 3:59 PM IST** (7 days). Personal done-date: Mon 5 Oct.
Checked against: `deck/deck_skeleton.md`, `research/analysis/facts_table.md`, `part_4_problem_definition.md`, the probe results (26 Sep), the survey proto-personas, `data/eval/*_dropout.json`, the live MVP and engine links, and a web check on Ask Photos and Apple Photos.

## Verdict

The thesis holds and the deck is honest about its limits. Five places are weaker than the deck currently says. Fix these before building slides, because each is a Clarity risk of the kind that cost CS2 14 points:

1. **The MVP headline number sits on the rarest cue mix.** L3 recall@20 is 0.962, but only 6 of 144 real attempts (4%) kept three cues. Re-weighted by how many cues real people kept, plain search scores 0.259 and Memory Trails 0.334 (+7.5 pp). Show that line next to the ladder.
2. **"Why not Ask Photos" is untested.** The probe didn't record search mode, and only 10 of the 144 attempts name Ask Photos. Replay the failed searches in Ask Photos mode this week.
3. **Cutting Expression and Recovery rests on absence of evidence.** People who never type a query can't appear in a corpus of posts about failed searches. The survey has to decide this.
4. **Slide 2 and slide 10 use different URR formulas.** Slide 2 keeps Recovery, slide 10 and Part 4 drop it.
5. **Two numbers are overstated.** "4 of 6 never found" is 3 confirmed plus 1 unrecorded. "74% ended not found" comes from the field with the weakest audit agreement (κ 0.161) in a complaint-biased sample.

## Skills run

Run: red-team-prd, pre-mortem, identify-assumptions-existing, opportunity-solution-tree, user-personas, competitor-analysis (scoped to "why not X"), north-star-metric, ab-test-analysis (applied to the eval ladder and probe), accessibility-review, synthesize-research.
Skipped as not relevant to this deliverable: NDA, privacy policy, SQL and data skills, S&P Global, pm-ai-shipping code audits, GTM, resume and proofread (proofread is worth running on the final deck text).

## 1. Red-team: kill-assumptions, ranked

| # | Claim | Fails if | Cheapest test (this week) | Kill criterion |
|---|---|---|---|---|
| 1 | Ask Photos doesn't solve the clue problem (slide 7) | Ask Photos already resolves "pichle saal diwali", "haldi", "previous gym"; the probe may have run on classic search | Re-run the 4 failed natural searches in Ask Photos mode. Record mode, year of festival 1, and wedding 2 result B. About 15 minutes. | If Ask Photos finds 2 or more of 4, slide 7 changes from "can't interpret" to "can't explain or correct" |
| 2 | Memory Trails' gain is decisive (slide 8) | Users keep 1 clue, not 3. In the engine: 0 cues 47, 1 cue 79, 2 cues 12, 3 cues 6. Gain at L1 and L2 is about +0.07. | Give test participants an L1 task ("sometime last winter") as well as the cake task | If L1 confirmed retrieval isn't clearly better than plain search, claim the interaction (recognition by moment), not recall |
| 3 | Expression (1.4%) and Recovery (0.7%) can be cut | The corpus excludes people who never searched. The probe's "why it missed" was "no idea" on every miss. | Survey Q4 (first move) and Q12 ("didn't know what to try next"). Check n first. | If more than about 15% scroll first or pick "didn't know what to try next", restore them as measured secondary stages |
| 4 | "77% fail before recovery" ranks Interpretation and Surfacing | Stage labels are model-assigned (κ 0.509, raw agreement 61.6%). Interpretation CI is 28–44%, Surfacing 34–50%, so they can't be ranked. | Present them jointly. Hand-check 30 stage labels. | If hand-checked agreement is below 60%, soften slide 2 to "before recovery" and drop the ordering |
| 5 | The segment is real | 29% (CI 22–37%) from complaint posts; the interviews were never run | Survey persona tagging; 3 test participants confirm fit | Fewer than 2 of 3 testers place the photo by event or rough time: reword the segment |

**Well-reasoned:** pre-registered hypotheses with a verdict on each, the audit that overturned its own ranking, modelled-not-measured labels on baselines, the 0.583 "oracle ceiling" correction, honest limitation wording on the MVP, soft scoring so a wrong date never hides the photo.
**Couldn't assess:** Google-scale latency, real survey responses, interview evidence (none exists yet), whether the MVP review blockers are fixed in the currently deployed build (commits say yes; I checked only that both links load).

## 2. Cross-check: idea vs evidence

| Idea | Evidence found | Status |
|---|---|---|
| People remember episodes and lose dates | `temporal_approx` 40 most retained, `date` 37 most lost. Probe: 4 of 6 remembered by an anchor, 1 of 6 by month and year. | **Holds.** Refine: probe anchors include life phases ("previous gym"), which a calendar resolver can't handle, so say "event or phase". |
| 77% fail before recovery (111/144) | CI 70–83%. Complaint-post sample, 86.2% Play Store. | **Holds directionally.** Label it a share of failures, not of retrievals. |
| Chips and match ledger are the right fix | Probe: "why it missed" was "no idea" for every miss | **Strengthened.** Best new line for slides 5 and 7, with n=1 stated. |
| MVP recall 0.172 → 0.962 | L3 tasks name the target's exact place and category. Weighted by real cue counts: 0.259 → 0.334. | **Weakened as a headline.** Keep the ladder, add the weighted line. |
| Ask Photos isn't enough | Toggle announced 10 Mar 2026, fully rolled out July with automatic routing of inference queries. No test of vague-event queries under Ask Photos. | **Unproven.** Test #1 above. |
| 46 of 62 (74%) ended not found | Outcome field κ 0.161. Sample is people who posted about a failure. | **Weakened.** Say "of 62 posts that state an outcome, 46 describe not finding it." |
| Probe: 4 of 6 never found | Wedding 2 search B is unrecorded. Step 1 opens each photo first, which may have primed "recent" results (gym 1). | **Overstated by one.** Say "3 confirmed, 1 pending". Failure is if anything understated. |
| Slide 2 URR formula | Slide 2 includes Recovery. Slide 10 and Part 4 say no Recovery term. | **Contradiction.** Pick one (drop Recovery) and use it everywhere. |
| Proto-personas P1–P5 | P4 (Sceptic) and P5 (Scroller) map to the two stages the deck cuts | **Merge to 3** (below). Also, `survey-proto-personas.md` still points to old slide numbers ("Slide 3/4"). |
| Evidence-verified figure | 85.2% (audit sample, n=203) vs 90.4% (all 720) | Use one, with its n. `survey_design.md` still says "142 audited posts"; it's 203. |

## 3. Pre-mortem

**Launch-blocking tigers (before 7 Oct)**

| # | Risk | Mitigation | By |
|---|---|---|---|
| T1 | Slides 5 and 9 are empty: no interviews, tests not yet run | Run 3 sessions 1–3 Oct, include an L1 task, finish the probe (wedding 2, festival year), pool the survey but show it separately. State plainly that interviews weren't run. | 3 Oct |
| T2 | URR formula differs between slides | Single formula, no Recovery term | 1 Oct |
| T3 | "Why not Ask Photos" untested | Replay in Ask Photos mode | 1 Oct |
| T4 | Links unverified for the reader | Open engine, MVP, survey and any Drive links in incognito | 5 Oct |
| T5 | Name in PDF metadata, fonts under 14 pt, filename | Standard QA pass on the final PDF | 6 Oct |

**Fast-follow / track:** production extract latency (the 23 Sep review measured 0.5–4.7 s and a visible fallback notice; confirm fixed); chip-read assumption (count chip edits and evidence opens in tests); text-in-image is unaddressed (CLIP and oracle both 0.000), so name it as the next iteration.

**Paper tigers:** synthetic library (clearly labelled, and the MVP page says "invented metadata"); Play Store share 86.2% (disclosed, and yield is source-independent); the ladder looking self-serving (only a tiger if slide 1 quotes 0.962).

**Elephants**
- The Sep 16 plan listed 5 interviews as never-cut, and they didn't happen. The deck's honesty here is the strength; hiding it would be the failure.
- One person defined the metric, wrote the tasks, built the MVP and will test it. Independence is the weakest point; the testers' L1 task is the partial answer.
- The thesis moved from "recovery agent" (16 Sep) to "episode retrieval" (now). The probe's "no idea why" points back at explanation, so slide 7 must say clearly what was cut and why, or a reader will see the CS2 pattern.

## 4. Assumption map (existing-product lens)

| Risk area | Assumption | Confidence | Test |
|---|---|---|---|
| Value | Rough-time/event users are a big enough segment | Medium (29%, CI 22–37) | Survey tagging |
| Value | Recognising moments beats scrolling | Low–Medium (n=10 scroll outcomes) | Test arms A/B, time to confirm |
| Value | Failure has real cost | Low (outcome κ 0.161) | Survey Q15/Q16 |
| Usability | People read and edit clue chips | Low–Medium | Count chip edits and evidence opens |
| Usability | Hinglish time phrases work | Untested (H4) | Survey Q10 |
| Viability | Retrieval drives paid-storage retention | Reasoning only | Label as illustrative |
| Feasibility | Episode grouping and date resolution at scale | High (Photos already clusters trips) | Not needed for the deck |
| Feasibility | Recovery path adds no latency to healthy search | Medium | State the design, measure p95 in prod |

## 5. Opportunity solution tree

**Outcome:** URR, the share of users with a vague-intent task who reach the photo.

| Opportunity | Evidence | Solutions (3 each) | Status |
|---|---|---|---|
| O1 Clue misread (event and relative time) | 35.4% | Clue → window resolver with editable chips (built); event aliases from the user's own trips and calendar; one disambiguating question ("Diwali 2023 or 2024?", cut) | Built |
| O2 Target buried in a flat grid | 41.7% | Moment-grouped results (built); near-duplicate collapsing; before/after context strip | Built |
| O3 No idea why it missed | Probe: every miss | Match ledger (built); "why nothing matched" message; suggested relaxed query | Partly built |
| O4 Text in the image | 12 of 144 retained; CLIP and oracle 0.000 | OCR index; VLM captions; document filter | **Not addressed. Name it as next iteration.** |
| O5 Moved browse path | 8.3% | Restore path; onboarding note | Out of scope, said so |
| O6 Can't start (Expression) | 1.4% (biased) | Suggested clues; browse-by-moment | Cut, pending survey |

Experiments already fit the tree: L1 task in user testing, Ask Photos replay, chip-edit counting.

## 6. Personas: refined to three (hypotheses until survey n is known)

1. **Anchor Rememberer** (P1 + P2). Remembers a phase, festival or ritual, not a date. Pains: date-less queries return nothing or hundreds of look-alikes; no sign of how the query was read; wrong-year guesses. Gains: same trip or event grouped, a date range, a reason for each match. Unexpected insight (probe, n=1): the one natural search that worked described something visible ("orange t-shirt"); every search anchored on time or context failed. People search with the memory they trust least to be indexed. Fit: chips and ledger address it; phase anchors ("previous gym") need episode aliases.
2. **Utility Hunter** (P3). Prescriptions, bills, warranty cards. Failure has a real cost. Fit: not served today (text-in-image 0.000). Highest-consequence gap; name it honestly.
3. **Sceptic-Scroller** (P4 + P5). Can't tell why, or never types. Maps to the two cut stages. Keep only as a diagnostic unless the survey shows real counts.

## 7. Competitor check ("why not X", verified 30 Sep)

- **Google Photos / Ask Photos:** launched Sep 2024, paused summer 2025 over latency, toggle announced 10 Mar 2026 after complaints about accuracy and latency, full rollout July 2026 with automatic routing (simple queries stay classic, inference queries like "what's my license plate?" go to Ask Photos). So the deck's "it fixed routing and speed" is supported. Whether it resolves event-relative time is still the open test.
- **Apple Photos (iOS 26):** natural-language search on themes, content and year. The source I fetched doesn't mention event-relative or text-in-image search, so I wouldn't claim Apple lacks them without a direct test.
- Not done: a full 5-competitor profile (Amazon Photos, OneDrive, Samsung Gallery not researched). It isn't needed unless slide 7 names them.

## 8. Metric and experiment fixes

- **Business game:** Productivity (task completion), not Attention. URR fits the seven North Star criteria except *leading indicator* and *actionable*, because "vague-intent task" and "target photo" aren't observable in telemetry.
- **Fix:** put an observable proxy on slide 10: a session with a failed or abandoned search followed within N minutes by open plus share, favourite or edit of one photo. Test-time proxy: "That's the one" confirmation. Say which is which.
- **Weighted recall (illustrative):** engine cue-count distribution × dropout ladder. Plain 0.259, Memory Trails 0.334. If 0-cue attempts are excluded: 0.234 vs 0.345. The mapping is approximate (some retained cues, like who-with and text, aren't indexed), which flatters the MVP slightly; say so.
- **A/B sizing** (per arm, two-sided α 0.05, 80% power):

| Baseline URR | +2 pp | +3 pp | +5 pp |
|---|---|---|---|
| 20% | 6,510 | 2,943 | 1,094 |
| 30% | 8,394 | 3,763 | 1,377 |
| 50% | 9,807 | 4,356 | 1,565 |

Baselines are modelled. Randomise by user, set a kill date, and guardrail on false confirmation and p95 latency.

## 9. Accessibility (MVP and deck)

- MVP contrast: body ink 16.5:1, blue 6.4:1, green 6.5:1, amber 5.5:1 all pass. **`ink-muted` #747775 fails 4.5:1 on the frame (4.33), subtle surface (4.10) and placeholder (3.89)**; it passes only on white (4.53). Darken to about #5F6368.
- Touch targets use 44px minimums. Reduced-motion is handled. 77 aria/role attributes exist; no screen-reader pass was run.
- The facilitator bar's light-blue text sits on dark slate, so it is fine.
- Deck: the MVP UI uses 9–13 px text. Crop screenshots and repeat any key text in 14 pt+ callouts. Check the ledger's ✓/✗ don't rely on green versus red alone.

## 10. Action list to submission

| When | Do |
|---|---|
| Wed 30 Sep – Thu 1 Oct | Ask Photos replay of the 4 failed searches; finish probe gaps; unify the URR formula; check survey n and tag respondents |
| Thu 1 – Sat 3 Oct | 3 test sessions (cake task plus an L1 task); count chip edits, evidence opens, false confirmations |
| Sat 3 Oct | Rewrite slides 5 and 9 from real results; add weighted-recall line to slide 8; reword the 74% and "4 of 6" lines |
| Sun 4 – Mon 5 Oct | Build the PDF; proofread pass; incognito link test; metadata scrub; ≥14 pt; filename NL_GooglePhotos |
| Tue 6 Oct | Buffer, one read-through: does every slide argue the same problem? |

## Sources

- [Google gives in to users' complaints over Ask Photos (TechCrunch, 10 Mar 2026)](https://techcrunch.com/2026/03/10/google-gives-in-to-users-complaints-over-ai-powered-ask-photos-search-feature/)
- [Google Photos classic search toggle (9to5Google, 20 Jul 2026)](https://9to5google.com/2026/07/20/google-photos-classic-search-toggle/)
- [Google Photos adding toggle between Ask Photos and classic search (9to5Google, 10 Mar 2026)](https://9to5google.com/2026/03/10/google-photos-ask-search-toggle/)
- [Inside Photos in iOS 26 (AppleInsider)](https://appleinsider.com/inside/ios-26/tips/inside-photos-in-ios-26-macos-26----refinements-in-apples-image-and-video-management-tool)
