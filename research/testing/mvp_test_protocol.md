# Memory Trails: User Testing & Recall Evaluation Protocol (W1)

**Target Window:** 28 Sep – 2 Oct 2026  
**Primary Goal:** Measure **session retrieval success** for users attempting to retrieve a real remembered photo they cannot precisely describe.

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
   https://memory-trails-v2.vercel.app/?study=P01
   ```
   (Replace `P01` with the participant ID).
3. Confirm that the top bar displays: `Study: P01` with the button `End session: copy log`.

---

## 4. Per-Task Facilitator Rubric

For each retrieval task, record:

| Metric | Measurement / Criteria |
|---|---|
| **Session Success** | Photo located within **5 minutes** (Yes / No). |
| **Time to First Plausible Moment** | Seconds until the participant opens the target or adjacent moment. |
| **Path to Success** | Path taken: `typed_query → moment`, `time_ribbon`, `anchor`, `outside_dates`, or `chip_alternative`. |
| **First Query Cue Level** | Code the first query: **L3** (time + place + category word), **L2** (two vague cues, paraphrased), **L1** (one vague cue + paraphrased), or **L0** (content description only). |
| **False Confirmations** | Participant confirmed a photo that was NOT the target (Guardrail). |
| **Ledger Interactions** | Count of `ledger_viewed` events and chip edits. |

---

## 5. Session Wrap-Up

1. Click **"End session: copy log"** on the study bar.
2. Paste the copied JSON into `data/eval/sessions/P01_session.json`.
3. Add any new real queries to `data/eval/tasks_wild.jsonl` for offline scoring.
