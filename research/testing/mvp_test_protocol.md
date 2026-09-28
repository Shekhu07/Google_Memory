# Memory Trails: User Testing & Recall Evaluation Protocol (W1)

**Target Window:** 1 – 4 Oct 2026 (the Part 6 follow-up, with people from the Part 3 interviews)  
**Primary Goal:** Measure **confirmed retrieval**: the share of tasks where the participant selects the intended photo with *That’s the one*. This is a task-level test measure; the product metric stays user-level URR (Part 7).

**Carry to the deck (checklist 4.1):** *This MVP validates the memory-reentry interaction and recovery model using representative media. It does not validate production-scale Google Photos retrieval accuracy.*

---

## 1. Participant Consent & Privacy

> [!IMPORTANT]
> **Mandatory Consent Statement to Read to Participant:**
> *"What you type into the demo will be recorded as text for this study."*

**Privacy Assurance:**
- All query text and interactions are held **strictly in-memory** during the session.
- Nothing is stored in `localStorage`, `sessionStorage`, or cookies.
- No text is sent to or retained by any remote logging server.
- The facilitator captures the session log at the conclusion of the test via the facilitator button.

---

## 2. Experimental Design & Arms

Each participant is assigned a Study ID (e.g. `P01`, `P02`). The study runs two arms in alternating order to counter learning effects:

1. **Arm A (Plain Search / Incumbent Baseline):**
   - The Search tab (`baseline` mode).
   - Standard text-to-photo semantic search over the library.
2. **Arm B (Memory Trails Re-Entry):**
   - The Spark icon / Memory Trails flow.
   - Episode-first re-entry with visual recap, clue chips, truth ledgers, and time ribbons.

---

## 3. Session Setup

1. Open an incognito browser window.
2. Navigate to:
   ```
   https://memory-trails-demo.vercel.app/?study=P01
   ```
   (Replace `P01` with the participant ID).
3. Confirm that the top bar displays: `Study: P01` with the button `End session: copy log`.

---

## 4. Tasks (updated 28 Sep, fixes checklist §5)

The library holds representative photos, not the participant's own, so tasks are representative. Read
the task aloud; never show the wording on screen.

**Main task:**
> Find the photo of the handmade cake from your sister’s graduation. You remember the event and what
> the photo looked like, but not the exact date or album.

**Optional tasks** (the library has an answer for each):
1. **College performance:** find the group photo after your college performance. You remember the people and the event, but not when it happened.
2. **Handwritten note:** find the photo of a handwritten note from your old apartment. You remember the note and the place, but not the date or album.
3. **Pet:** find the photo of your dog curled up in the suitcase. You remember the scene, but not when it was taken.

Do not use the medicine or Goa café tasks.

**Observe:**
- Did they understand that exact wording is not required?
- Did they start with a description, or with a cue chip?
- Did they understand, edit or add clues?
- Could they identify the useful moment?
- Did they open *Why this moment?* / *See evidence*?
- If they rejected a near miss, did they recover (which answer to *What feels wrong?*)?
- Did they explicitly confirm the right photo? Were they sure?

**Before the session:** ask for one real incident of their own and note the words they would have
used (Part 3 critical-incident step). Code its cue level. It cannot be run against this library,
but it tells you whether the representative task sits at the same level.

## 5. Per-Task Facilitator Rubric

For each retrieval task, record:

| Metric | Measurement / Criteria |
|---|---|
| **Confirmed retrieval** | Selected the intended photo with *That’s the one* within **5 minutes** (`retrieval_confirmed`, Yes / No). |
| **Time to First Plausible Moment** | Seconds until the participant opens the target or adjacent moment. |
| **Path to Success** | Path taken: `typed_query → moment`, `time_ribbon`, `anchor`, `added_clue`, `recovery`, `outside_dates`, or `chip_alternative`. |
| **Near-miss recovery** | After *Not this moment*: which answer (`recovery_action_selected`), and whether a confirmation followed. |
| **First Query Cue Level** | Code the first query: **L3** (time + place + category word), **L2** (two vague cues, paraphrased), **L1** (one vague cue + paraphrased), or **L0** (content description only). |
| **False Confirmations** | Participant confirmed a photo that was NOT the target (Guardrail). |
| **Evidence & clue interactions** | `evidence_viewed` count and clue edits (`clueEdits` in the log summary). |
| **Abandonment** | Left without confirming (`prototype_exited`). |
| **Confidence after confirming** | Answer to *Did this help you get back to the memory?* plus one spoken line. |

---

## 6. Session Wrap-Up

1. Click **"End session: copy log"** on the study bar.
2. Paste the copied JSON into `research/testing/sessions/P01_session.json`.
3. Add any new real queries to `data/eval/tasks_wild.jsonl` for offline scoring.
