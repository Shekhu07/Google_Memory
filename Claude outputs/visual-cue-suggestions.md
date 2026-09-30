# Memory Trails: visual-cue suggestions after a miss

**Status:** proposed, not merged · **Date:** 29 Sep 2026 · **Area:** `webapp/apps/retrieval`, `webapp/apps/web`

## 1. Why

The 26 Sep search test on the PM's own library (`claude/probe-results-2026-09-26.md`):

- The only natural search that found its photo described what was **visible** ("me wearing orange t-shirt").
- Every search anchored on a festival, a life phase or a ritual failed ("during Diwali", "previous gym", "haldi").
- "Why it missed" was "no idea" every time.

Today the MVP never suggests keywords based on the user's own search. The "Add one thing you remember" row (`DEMO_ANCHORS` in `main.py`) and "Try a memory like" (`lib/examples.ts`) are the same fixed lists for everyone. After a miss, the only options are "loosen a filter" (`NoMatch.tsx`, `NotHere.tsx`) or generic advice ("a rough timeframe, a place, or who was there"). The advice also mentions "who was there", which the MVP can't search on.

**Change:** after a miss, offer 3–4 visible details, taken from the photos the search came closest to, that the user can tap to add.

> **Not in these moments? Try something you'd have seen**
> `orange` · `candles or diyas` · `traditional outfit` · `a stage`
> *Seen in 8 of the 24 closest photos*

## 2. How it works

### 2.1 Where the suggestions come from (no new model, no captions)

- A fixed, reviewed vocabulary of **36 visible details** in five groups:
  - **Colour:** red, orange, yellow, green, blue, pink, white, dark
  - **Wearing:** traditional outfit, t-shirt, formal wear, dress
  - **People:** one person, a group, a child
  - **Things:** flowers, candles/diyas, string lights, food on a table, drink, cake, pet, gym equipment, screen, paper with writing, vehicle, stage
  - **Setting:** indoors, outdoors, night, sunny daylight, sea/beach, hills, trees, street, building
- At the first search, each detail's CLIP text vector is scored against every photo's existing image vector (`data/index.npz`). The scores are z-scored across the library, so a detail "shows" in a photo when its score is more than 1 standard deviation above the mean. This takes about 0.6 s, once, and is cached with `lru_cache`, the same way as the encoder.
- The vocabulary leaves out anything about bodies, age, skin, health or what a document says. "No people" was dropped because CLIP handles negation badly.

### 2.2 Which details get offered

The candidates are the top 24 photos of the current search. A detail is offered only if:

1. **It has evidence:** it shows in at least 15% of the candidates.
2. **It narrows the set:** it shows in no more than 80% of them. "Cake" on a cake query shows in 100%, so it is skipped.
3. **The query doesn't already say it:** no word overlap with the query, and the detail's text vector is not more than 0.12 above the median detail. Raw CLIP text-to-text cosines are uniformly high, so a fixed cutoff didn't work.
4. **It isn't already picked,** and at most 2 are shown per group.

Each detail is ranked by `share × (1 − share) × (1 + mean lift)`, so the most even split wins. The copy is grounded: "Seen in N of the 24 closest photos". It never says "your photo has…".

### 2.3 What a tap does

A picked detail becomes a removable chip ("Something you saw"). It is sent to `/search` as `seen: ["orange"]`, up to 3.

The server **steers the query vector**: `q' = normalise(q̂ + α · Σ cue_vec)`. It doesn't append words to the text: appending was tested and barely moves CLIP (§3). Picked details are never metadata filters, so a wrong pick only reorders the results and can't hide the photo.

## 3. Evidence so far (simulation, not user data)

Run on 191 unique queries from `tasks.jsonl`, `tasks_dropout.jsonl` and `tasks_real.jsonl`. The pipeline matches the product: rules extraction → soft search. A **miss** means the target is not among the top-20 photos.

| Measure | Result |
|---|---|
| Misses | 69 / 191 |
| Suggestions shown on a miss | 69 / 69 |
| At least one suggestion is true of the target photo | **37 / 69 (54%)** |
| The first suggestion is true of the target | 10 / 69 (14%) |
| Recovered by **appending the detail as text** | **4 / 69 (6%)** |
| Recovered by **steering the vector** (1 detail; α = 0.5 / 1.0 / 1.5) | 6 / 10 / **12** of 69 (8.7% / 14.5% / 17.4%). Among the 35 misses with a true suggestion, α = 1.0 recovers **10 / 35 (28.6%)**: the ≥20% gate **passes**. Re-run 30 Sep with the production ONNX encoder, so the counts above it moved slightly (35 true, 14 first-true, 3 appended). |

Read this with care:

- "True of the target" uses the same CLIP scores that pick the suggestions. It's an upper bound for a user who recognises the detail, not a measure of what real users will do.
- Appending text fails. Adding one word to a long query hardly moves the text vector, which is why §2.3 uses vector steering.
- The first suggestion is right only 14% of the time. Show 4 and never pre-select one.
- **Gate:** merge only if steering recovers at least 20% of the eligible misses and changes no current top-20 hit on tasks where the user wouldn't open the panel. Pick α from that run.

Sample suggestions from the prototype:

| Query | Offered |
|---|---|
| my photos during the haldi ceremony | candles or diyas · traditional outfit · orange · a stage |
| pichle saal diwali | candles or diyas · traditional outfit · food on a table · white |
| restaurant in Goa last winter | food on a table · candles or diyas · at night · red |
| previous gym photos | one person · dark · dress · no people *(now removed)* |

## 4. Changes by file

### Backend (`webapp/apps/retrieval`)

| File | Change |
|---|---|
| `cues.py` **(new)** | `VOCAB`, `build_bank(encoder, matrix)`, `suggest(bank, query, qv, rows, limit=4, exclude=[])`, `steer(bank, qv, labels)`, `known(label)`. Prototype saved at `Claude outputs/visual-cues-prototype/cues.py` |
| `search.py` | `SearchContext.cues = None` (default keeps tests and offline eval unchanged). `search(..., seen=None)` steers `qv` when `seen` is set (not in baseline mode). The result adds `cue_suggestions` (computed from the **unsteered** query) and `seen_applied` |
| `main.py` | `cue_bank()` with `lru_cache`. `SearchIn.seen: list[str]` (max 3). Returns 422 on an unknown label. Passes `cues=cue_bank()` into the context |
| `engine/demo_eval.py` | New strategy `soft+seen_oracle` that reproduces §3, so the number can be regenerated |

### Frontend (`webapp/apps/web`)

| File | Change |
|---|---|
| `lib/api.ts` | `CueSuggestion = {label, phrase, group, seen_in, of}`. `SearchResult.cue_suggestions?`, `seen_applied?`. `search(..., seen: string[] = [])` |
| `components/SeenCues.tsx` **(new)** | Chip row: heading "Try something you'd have seen", support line "Seen in N of the X closest photos" |
| `components/NotHere.tsx` | Render `SeenCues` inside the open panel, above "Show the next N moments" |
| `components/NoMatch.tsx` | Render `SeenCues` above "Keep the memory and try one small change". If the search is empty, use baseline candidates so there's still something to suggest from |
| `components/MemoryTrails.tsx` | `seen` state. `onPickSeen(label)` adds a chip, reruns `runSearch` and shows "Added 'orange'. Undo". Remove or undo reruns the search. `restart()` clears it |
| `components/Breadcrumb.tsx` / `ClueChip.tsx` | New `clueKind("seen")` → "Something you saw" |
| `components/SearchView.tsx` | Handoff copy: drop "who was there" (there's no people data). Replace it with "what you'd have seen — a colour, what someone wore" |

### Analytics (`lib/track.ts` events)

- `seen_cues_shown` `{labels, surface: "not_here" | "no_match"}`
- `seen_cue_picked` `{label, rank}` · `seen_cue_removed` `{label}`
- `retrieval_confirmed` gets `seen: [...]`, so the cue→find rate can be measured.

## 5. Tests to add

- `test_cues.py`:
  - cake query → "a cake" not offered (share > 80%)
  - "group photo" → "a group" not offered (the query says it)
  - fewer than 4 candidates → `[]`
  - `exclude` respected
  - at most 2 per group
  - unknown label ignored by `steer`
- `test_api.py`:
  - `/search` returns `cue_suggestions`
  - `seen: ["orange"]` changes the order without changing `filters_applied`
  - unknown label → 422
  - `seen` longer than 3 → 422
  - baseline mode → `cue_suggestions == []`
- Latency: first search adds about 0.6 s (bank build), later searches under 5 ms. Record it in `/health`.

Baseline before this change: 101 passed, 1 failed (`test_llm_clues.py::test_falls_back_to_rules_when_the_budget_is_gone`, which already failed and is unrelated).

## 6. Risks

| Risk | Mitigation |
|---|---|
| A wrong suggestion reads as the system claiming something about the photo | Grounded copy ("seen in 8 of 24 closest"); it steers the ranking and never filters |
| CLIP colour and clothing reads are noisy ("dress" on a gym query) | Split-based selection; 4 options, none pre-selected; remove with one tap |
| The deck calls this "better search", which reviewers push back on | Frame it as the recovery path: it appears only after "Not in any of these?" or an empty result, and costs nothing on a healthy search |
| The number is simulated | Label it as simulated on the slide; count `seen_cue_picked` → `retrieval_confirmed` in the user tests (Oct 1–3) |

## 7. Deck line (slide 8 or 9)

> The only natural search that worked in our probe described what was visible. After a miss, Memory Trails offers visible details from the closest photos. In simulation, a detail true of the target was offered in 54% of misses. Steering on it recovers **[X]%** *(fill in from the §3 rerun)*.
