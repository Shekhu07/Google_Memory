# Memory Trails v2: Fix Plan, brief-aligned (24 to 27 Sep 2026)

**Replaces:** `memory-trails-fix-plan.md` (23 Sep). Keep v1 for the record.
**What changed and why:** v1 fixed bugs but did not test the plan against the brief. The brief is explicit:

> The user knows that the photo exists, but may not remember **when** it was taken, **where** it was taken, **what album** it belongs to, or **the exact words** needed to search for it.
> Goal: increase the percentage of users who **successfully retrieve** a photo they remember but **cannot precisely describe** when they start searching.
> **The challenge is not to improve search in general.**

Three consequences:
1. **Work that serves precise descriptions is off-brief.** Exact numeric dates ("25/12/2025") and full-vocabulary queries belong to "improving search in general". They are frozen: no more work on them, and no claims based on them.
2. **The current benchmark measures the wrong population.** Every `real_test` query hands the system the date, the exact place and the library's own category word. It is a precisely described photo, so 0.866 cannot be the headline.
3. **The goal is session success, not one query's rank.** A user "successfully retrieves" by any path: typing, the time ribbon, opening a moment, or editing a chip. recall@20 becomes one component.

**Hard stop on building:** end of Sun 27 Sep. The delayed-recall tests start 28 Sep.

---

## 0. The brief filter

Every item below carries a tag. An item that serves none of the first four tags, or trust, is cut or frozen.

| Tag | Brief's missing cue | What the MVP does for it today | Gap this plan closes |
|---|---|---|---|
| `WHEN` | doesn't remember when | vague-time parsing, time ribbon, soft date scoring | wrong windows (P1, P2, P4); hidden interpretation (F2); misdated memory (F4) |
| `WHERE` | doesn't remember where | place anchors, soft place boost | false place evidence (B1); outside-window strip ignores place (S2) |
| `ALBUM` | doesn't know the album | episodes as "moments" | partial episode names don't match (F3) |
| `WORDS` | doesn't have the exact words | CLIP semantic search, category synonyms | 46 of 59 categories unreachable (P7); "may", "road" misreads (P5, P6) |
| `TRUST` | n/a | evidence, chips | cards claim clues they don't have (B1) |
| `MEASURE` | n/a | recall@20 on templated queries | cue-dropout eval (E1), session success (W1) |
| **Frozen** | precise description | numeric and exact dates work | no new work, not claimed on the deck |

**Corpus backing** (144 specific attempts): `temporal_approx` 40 and `event_anchor` 9 are on-brief `WHEN` cues. `exact_date` 14 is the precise-description minority.

---

## 1. Schedule

| Day | Work | Done when |
|---|---|---|
| **Wed 24** | B1 to B4 blockers; P1, P2, P4 to P7 parser bugs | §8 probe table rows 1 to 11 pass locally |
| **Thu 25** | F1 per-card match ledger (UI); F2 resolved chips with vague-time alternatives | Ledger renders ✓/✗ at 320px; date chips show their window |
| **Fri 26** | F3 episode aliases; **E1 cue-dropout eval**; S1 to S3 | E1 table (§6) filled in PROGRESS |
| **Sat 27** | Deploy; incognito probe; W1 study-mode kit; S4 and S5; (optional F4) | Live link passes §8; recall-test kit ready |

**Cut order if behind:** F4, then S4, then F2 alternatives (keep the resolved-window label), then F3 beyond the aliases in §4.
**Never cut:** B1 to B4, P1, P4, E1, W1.

**Rules for the block:**
- Parity gates stay green: `tests/test_service_parity.py`, `tests/test_export_onnx.py`, the full suite, and `webapp/apps/retrieval/tests`.
- Tune on `real_dev` and synthetic only. E1's cue-dropout set is written and frozen **before** its first score, then scored once.
- Pin today at `2026-09-23` (B3). Every probe here assumes it.

---

## 2. Blockers (Wed 24)

### B1: Evidence claims are false on non-matching cards · `TRUST` `WHERE`

**Seen live:** "restaurant we went to in Goa last winter", soft mode. The Manali, Pondicherry and Bengaluru cards say *"Goa location · cafe-like scenes"*, See evidence shows *Place: Goa, strong*, and the Manali card says "3 match your clues" when none do.

**Cause:** `search.py → search()` copies the same `reasons` and `detail` onto every group. `Moments.tsx:32` shows hit count (`ep.count`) as "match your clues".

**Fix: a per-episode ledger computed from that episode's own hit photos.**

`webapp/apps/retrieval/search.py`:
```python
from datetime import date

def _days_outside(d, lo, hi):
    """Signed distance from the window: 0 inside, -N before, +N after."""
    if not d:
        return None
    try:
        rd = date.fromisoformat(d[:10])
    except ValueError:
        return None
    if lo and rd < date.fromisoformat(lo):
        return -(date.fromisoformat(lo) - rd).days
    if hi and rd > date.fromisoformat(hi):
        return (rd - date.fromisoformat(hi)).days
    return 0


def _matches(r, kind, want):
    # Same rules as engine.demo_index.soft_search, so the ledger and the ranking agree.
    if kind == "category":
        return r.get("category") == want
    return want.lower() in (r.get(kind) or "").lower()     # location, episode: substring


def match_ledger(hit_rows, filters):
    ledger = []
    for kind in ("episode", "location", "category"):
        want = filters.get(kind)
        if want:
            n = sum(_matches(r, kind, want) for r in hit_rows)
            ledger.append({"kind": kind, "value": want, "matched": n > 0, "n": n})
    lo, hi = filters.get("date_from"), filters.get("date_to")
    if lo or hi:
        offs = [o for o in (_days_outside(r.get("date"), lo, hi) for r in hit_rows) if o is not None]
        best = min(offs, key=abs) if offs else None
        ledger.append({"kind": "date_window", "value": lo, "to": hi,
                       "matched": best == 0, "offset_days": best})
    return ledger


def clue_hits(hit_rows, filters):
    """Photos in this moment that satisfy every clue given (date inside the window)."""
    lo, hi = filters.get("date_from"), filters.get("date_to")
    def ok(r):
        if any(filters.get(k) and not _matches(r, k, filters[k]) for k in ("episode", "location", "category")):
            return False
        return not (lo or hi) or _days_outside(r.get("date"), lo, hi) == 0
    return sum(ok(r) for r in hit_rows)
```
Replace the copy loop in `search()`:
```python
by_id = {r["id"]: r for r in ctx.records}
for g in groups:
    rows = [by_id[p["id"]] for p in g["photos"] if p["id"] in by_id]
    ledger = match_ledger(rows, applied)
    g["ledger"] = ledger
    g["why"] = [{k: v for k, v in x.items() if k in ("kind", "value", "to")} for x in ledger if x["matched"]]
    g["evidence"] = evidence_detail(g["why"])
    g["clue_hits"] = clue_hits(rows, applied)
```
**Frontend:**
- Add `ledger` and `clue_hits` to the `Episode` type in `lib/api.ts`.
- `Moments.tsx:32`: show "N match all your clues" only when `clue_hits > 0`.

**Tests** (`webapp/apps/retrieval/tests/test_search.py`):
- A non-Goa group returned for `{location: "Goa"}` has no location item in `why`.
- `clue_hits <= count` for every group.
- A photo 9 days after `date_to` gives `offset_days == 9`.

**Parity:** photo-level output is unchanged, so `test_service_parity.py` passes untouched.

---

### B2: Production calls Groq on every extract, fails, and prints "Live extraction unavailable" · `TRUST`

**Seen live:** `/health` reports `groq: true`, but every `/extract` returns `source: "rules"` plus the notice, which the recap screen shows. Extract takes 0.5 to 4.7 s. The probable cause is that `engine/groq.py` writes its ledger to a read-only path on Vercel.

**Decision:** rules are the product extractor, because they beat the LLM on the held-out split (0.818 vs 0.718). E1 re-checks this on vague queries (§6): if the LLM wins at cue levels L0 and L1, that becomes a roadmap finding, not a Saturday switch.

`main.py`:
```python
@lru_cache(maxsize=1)
def groq_client():
    if os.environ.get("EXTRACTOR", "rules") != "llm" or not os.environ.get("GROQ_API_KEY"):
        return None
    os.environ.setdefault("GROQ_LEDGER", "/tmp/groq_usage.json")   # Vercel FS is read-only
    from engine.groq import GroqClient
    ...
```
`llm_clues.py`:
```python
def extract(text, facets, client, today=None):
    today = today or date.today()
    if client is None:                                    # deliberate rules path: no notice
        return dict(extract_clues(text, facets, today), notice=None)
    fallback = dict(extract_clues(text, facets, today),
                    notice="Live extraction unavailable - used rule-based clue matching.")
    ...
```
- Remove `GROQ_API_KEY` from the Vercel project, or leave `EXTRACTOR` unset.
- Update `tests/test_llm_clues.py` if it asserts the notice.
- **Done when:** live `/extract` returns in under 1 s warm, with `notice: null`, and `/health` shows `groq: false`.

---

### B3: Pin "today" for the frozen library · `MEASURE`

Relative phrases drift after submission; on 1 Jan 2027 every "last year" result changes.
```python
# main.py
DEMO_TODAY = date.fromisoformat(os.environ.get("DEMO_TODAY", "2026-09-23"))
return llm_clues.extract(text, FACETS, groq_client(), today=DEMO_TODAY)
```
Import the same constant into `engine/demo_eval.py` and `engine/demo_tasks_real.py`. Add to the disclaimer: *"The demo treats today as 23 Sep 2026."*

---

### B4: The benchmark measures precisely described photos · `MEASURE`

`real_test` queries look like *"the medicine we visited in Kochi last winter"*. Each gives a date phrase, the target's exact library location, and its exact category word. README calls them "natural user queries" and tags them `source: real`.

- **Relabel:** in `engine/demo_tasks_real.py`, change `source: "real"` to `source: "real_pattern"`. Update `tests/test_demo_tasks_real.py`.
- **README and PROGRESS wording:** *"60 template-rendered queries using phrasing patterns seen in real verbatims. Every query contains the target's place and category word, so this set measures a **fully described** photo (cue level L3). Performance when cues are missing is measured separately (E1)."*
- **Deck:** 0.866 moves off the headline. It becomes the L3 row of the E1 table (§6).

---

## 3. Parser fixes (Wed 24): `webapp/apps/retrieval/clues.py`

Only the fixes that serve vague or missing cues. **Exact numeric dates are frozen.** Leave the current DD/MM handling as-is and add no alternatives.

### P1: "last winter" spans 15 months · `WHEN`
Today: 2024-12-01 → 2026-02-28. Expected: 2025-12-01 → 2026-02-28.
```python
if re.search(r"\blast winter\b", low):
    end_year = today.year if today.month >= 3 else today.year - 1   # most recent winter that has ended
    feb_last = calendar.monthrange(end_year, 2)[1]
    return f"{end_year - 1}-12-01", f"{end_year}-02-{feb_last:02d}", "temporal_approx", "last winter"
```
`demo_tasks_real.py:73` labels any 2025+ winter photo "last winter", which agrees with the bug. Fix the generator the same way and regenerate as `tasks_real_v2.jsonl`. Keep v1.

### P2: "last summer" and "last monsoon" pick the wrong year · `WHEN`
```python
summer_year  = today.year if today.month >= 7  else today.year - 1   # May-Jun done by July
monsoon_year = today.year if today.month >= 10 else today.year - 1   # Jul-Sep done by October
```
Apply the same change to `demo_tasks_real.py:77`.

### P3: "new year's eve" · `WHEN` (event anchor)
Add to `FIXED_HOLIDAYS`: `"new year's eve": (12, 31), "new years eve": (12, 31), "nye": (12, 31)`. It's cheap, and an event anchor is a vague WHEN cue.

### P4: A bare "after" or "before" drops the trip · `WHEN` `ALBUM`
"Goa trip photos after sunset" is read as *after the Goa trip*, and the episode and place are both dropped. The preposition must attach to the trip mention:
```python
def _mention_re(ep):
    names = [ep] + EPISODE_ALIASES.get(ep, [])            # F3 table
    return r"(?:" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")"

QTY = r"(?:(?P<n>\d+|a few|few|one|two|three|four|five|six)\s+(?P<unit>days?|weeks?|months?)\s+|(?P<adv>just|right|shortly)\s+)?"
DET = r"(?:the\s+|our\s+|my\s+|that\s+)?"

after_en  = re.search(QTY + r"after\s+"  + DET + m, low)            # m = _mention_re(matched_ep)
before_en = re.search(QTY + r"before\s+" + DET + m, low)
after_hi  = re.search(m + r"(?:\s+trip)?\s+(?:ke\s+)?baad\b", low)
before_hi = re.search(m + r"(?:\s+trip)?\s+(?:se\s+|ke\s+)?pehle\b", low)
```
- Take the amount and unit from the named groups.
- Replace the hard-coded goa/wedding/sangeet resolution with the F3 table.
- "Before" windows end at `ep_start`, not `ep_end`, to mirror "after".

### P5: "may" as a verb becomes the month of May · `WORDS`
In step 12, accept only full month names (plus "sept"). Accept "may" only with a preposition: `(in|during|around|early|mid|late|last|this|since) may`, or `may (mein|ke|me)`. Abbreviations stay valid only with a year.

### P6: "road trip" becomes the street category · `WORDS`
Remove `"road": "street"` from `CATEGORY_SYNONYMS`.

### P7: 46 of 59 categories can't be reached by words · `WORDS`
```python
synonyms = {c: c for c in facets.categories}
synonyms.update(CATEGORY_SYNONYMS)
for word in sorted(synonyms, key=len, reverse=True): ...
```
Add: `"parking lot": "parking", "car park": "parking", "parked": "parking", "screenshots": "screenshot", "rickshaw": "auto rickshaw", "chai": "chai stall"`.

**Tests:** one `test_clues.py` case per §8 row, plus the synthetic forms ("sometime in 2024", "July 2025ish") unchanged.

---

## 4. Features (Thu 25 and Fri 26)

### F1: Per-card match ledger (Thu) · `TRUST` `WHERE` `WHEN`
Under each moment card:

> **Goa** ✓ · **café** ✓ · **date** +21 days

- ✗ is shown muted ("not Goa"), never hidden. Dates show `offset_days` as "+N days" or "N days earlier".
- Soft scoring lets a moment appear even when a clue is wrong. The ledger is what makes that honest: a user who misremembered the place still sees the right moment, labelled "not Goa".
- 320px: two lines at most.
- Event `ledger_viewed`.

### F2: Chips show what the system understood · `WHEN`
- **Label:** date chips gain a second line built from `value` and `value_to`, for example `last winter · Dec 2025 – Feb 2026`. This applies to every date chip.
- **Alternatives, vague time only:**
  - `last/this {season}`, `last year`, `pichle saal`, `N years ago`: offer the adjacent period, for example *"or Dec 2024 – Feb 2025?"*.
  - Festival without a year ("around Diwali"): offer the previous year's festival.
- **No alternatives for numeric dates.** That is precise description, which is frozen.
- **UI:** one text button under the chip. Tapping swaps the filter and re-runs the search. Event `chip_alternative_taken`.

### F3: Episode aliases (Fri) · `ALBUM` `WORDS`
The brief's "doesn't know the album" user describes the event in their own words, not its name.
```python
EPISODE_ALIASES = {
    "office offsite":     ["offsite", "off-site"],
    "fever week":         ["fever", "when i was sick", "when i was ill", "bimaar tha", "bimaar thi"],
    "new year goa":       ["new year's eve in goa", "new year in goa", "nye goa", "new year's eve goa"],
    "passport renewal":   ["passport renewal", "renewing my passport"],
    "dental work":        ["dentist", "dental"],
    "house move":         ["moving house", "house shifting", "shifting house"],
    "flat hunting":       ["flat hunt", "house hunting"],
    "puppy vet visits":   ["vet visit", "the vet"],
    "product workshop":   ["workshop"],
    "team strategy day":  ["strategy day"],
    "year-end party":     ["year end party", "office party"],
    "cousin wedding":     ["wedding", "shaadi"],
    "friend's sangeet":   ["sangeet"],
    "onam lunch":         ["onam sadhya", "sadhya", "sadya"],
    "goa trip":           ["goa trip"],
}
```
- Aliases apply only when no full episode name matched, with word boundaries, longest first.
- Never alias bare "goa", "diwali", "puppy" or "kerala".
- The chip shows the real episode name, so the interpretation stays visible and removable.

### F4 (optional, Sat): Flag misdated memories · `WHEN`
The brief says the user may not remember when, and sometimes they remember it *wrong*. When the matched episode and the date window don't overlap (for example "pichle saal wali Goa trip": the trip was Dec 2023, the window is 2025):
- `/extract` returns `conflicts: [{episode, episode_dates, window}]`.
- The recap screen says: *"Your Goa trip was Dec 2023, not last year. Showing both."*
- The date becomes a soft boost only.

**Label it a hypothesis.** The 720-episode corpus has no evidence of misdated memories. Test it in the recall sessions (W1): the story can place an event "last year" when the library dates it two years back.

---

## 5. Should fix (Fri 26 and Sat 27)

### S1: "What part feels most certain?" does nothing · `TRUST`
`strength` is stored but never sent. "Who was there" maps to `null`, since there's no people data.
- **Wire it (recommended):** send `boost_key` to `/search`, and `soft_search` doubles that dimension's β. The default `None` keeps parity. Remove "Who was there".
- **Or cut it.**

Either way, update README, which currently says there's no clarifying question.

### S2: "Just outside your dates" ignores place and category · `WHERE`
In `outside_window_photos`, in both engine copies:
```python
loc = filters.get("location", "").lower(); cat = filters.get("category", "")
if loc and loc not in (r.get("location") or "").lower(): continue
if cat and r.get("category") != cat: continue
```
Hide the strip if it's empty. New subtitle: *"Same clues, a little outside your dates"*.

### S3: Episode ranking has dead terms · `TRUST`
- `filter_cover = len(dims)/len(dims)` is always 1: use matched dims ÷ dims from the ledger.
- Evidence quality is the same for every group: use the group's matched count.
- `_recognizability` rewards episode size: use `clue_hits`, or document why size is intended.

README already calls these weights judgement. Keep saying so.

### S4: Composer and scroll
- Make *Continue* a sticky footer in the sheet. It's below the fold at 375px and looks clipped.
- On every stage change, run `sheetRef.current?.scrollTo({ top: 0 })`.
- Fix the Places and Things covers: Bengaluru shows a beach, and the Screenshots tile isn't a screenshot.

### S5: Docs (Sat)
- Use one test count (README says 188 and 164).
- Rename "Oracle (Perfect filters)" to "Date oracle (±45 d)".
- Clear PROGRESS "Waiting on you".
- Record B2's extractor decision and B4's L3 relabel.
- **Rewrite README's opening line around the brief** (see §9).

---

## 6. E1: Cue-dropout evaluation (Fri 26) · `MEASURE`

**Purpose:** measure the brief's population directly: retrieval success as cues go missing.

**Files:**
- new `engine/demo_tasks_dropout.py`
- new `data/eval/tasks_dropout.jsonl`
- new `data/eval/paraphrase_bank.json`
- new `tests/test_demo_tasks_dropout.py`
- in `engine/demo_eval.py`: a `--tasks dropout` flag and a `moment@5` metric

### Cue levels (per base task, same `answer_ids`)

| Level | What the query keeps | Example (target: a café photo, Goa trip, Dec 2023) |
|---|---|---|
| **L3** | vague time + exact place + library word | "the café we visited in Goa winter 2023" (today's set) |
| **L2** | two of: vague time / place / content, **content paraphrased** | "that place with wooden tables and coffee, on the Goa trip" |
| **L1** | one vague cue + paraphrased content | "wooden tables and coffee, sometime a couple of years ago" |
| **L0** | paraphrased content only, no time, no place, no library word | "a cosy spot with dark wood and a coffee cup" |

**Rules for writing the set:**
- **Paraphrase bank:** 2 to 3 hand-written descriptions per category that avoid the category's library word and its synonyms. For example, `receipt` becomes "the long paper slip from a shop" and "the bill I took a photo of". Write it before any scoring.
- **Vague-time phrases only:** "a while back", "a couple of years ago", "around the festive season", "sometime after a trip". **No numeric dates at any level.**
- **Place:** exact name only at L3. At L2, either the name or a vague description ("that beach state", "somewhere in the hills").
- **Volume:** 30 base tasks × 4 levels = 120 queries.
- **Scoring:** freeze the file (commit it) before the first score, then score once. Label the queries `constructed`.

### Metrics
- `recall@20` and `found@20`: the photo is in the top 20.
- **`moment@5`:** the target's episode is among the top 5 moment cards. This is the offline proxy for "retrievable in one tap", because the product is episode-first.
- Strategies: `baseline` (plain CLIP), `soft` (rules, deployed), and optionally `inferred_llm`. The LLM may help at L0 and L1, and that is worth knowing.

### Report table (goes in PROGRESS the day it's measured, then on the deck)

| Level | baseline recall@20 | soft recall@20 | soft moment@5 | n |
|---|---:|---:|---:|---:|
| L3 (fully described) | | | | 30 |
| L2 | | | | 30 |
| L1 | | | | 30 |
| **L0 (content only)** | | | | 30 |

**How to read it:**
- The slope from L3 to L0 is the story.
- If soft ≈ baseline at L0, the product's value is in the time/place cues, and the gap at L0 is the roadmap (A7 captions and OCR).
- If `moment@5` beats `recall@20` at L1 and L2, that is the evidence for episode-first re-entry.
- Report every row, including bad ones.

---

## 7. W1: Session success in the recall tests (Sat 27 kit, 28 Sep to 2 Oct run) · `MEASURE`

The brief's goal is "successfully retrieve", so **session success is the headline metric.**

**Per task, record:**
- found within 5 minutes (yes/no)
- **path to success:** typed query → moment, time ribbon, anchor, "just outside your dates", or chip edit or alternative
- time to the first plausible moment
- **cue level of the participant's first query**, coded L0 to L3 with the same rubric as E1
- false confirmations (guardrail)
- ledger opens (`ledger_viewed`) and chip edits

**Study mode:**
- `?study=P01` keeps typed queries **in memory only**, never localStorage and never on the server, so the "visitor text is never logged" promise holds.
- An "End session: copy log" button copies the JSON for the facilitator.
- Add a consent line to `research/testing/mvp_test_protocol.md`: *"What you type into the demo will be recorded as text for this study."*
- After the sessions, add the queries to `data/eval/tasks_wild.jsonl` and score all strategies once, by cue level.

**Arms (unchanged from T6):** the plain Search tab vs Memory Trails, alternating order.

---

## 8. Acceptance probe table (`today = 2026-09-23`)

Run locally on Wed and on the live URL on Sat, in an incognito window.

**Vague-cue parsing:**

| # | Query | Expected | Now (23 Sep) |
|---|---|---|---|
| 1 | restaurant we went to in Goa last winter | Goa · cafe · 2025-12-01 → 2026-02-28 | window 2024-12-01 → 2026-02-28 |
| 2 | last summer in kerala | episode summer in kerala · 2026-05 → 2026-06 | 2025 |
| 3 | new year's eve party in goa | episode new year goa · around 31 Dec 2025 | 1 Jan window, no episode |
| 4 | Goa trip photos after sunset | episode goa trip · Goa · no date | window after trip, Goa dropped |
| 5 | beach photo a few weeks after the Goa trip | beach · trip end → +42 d · no episode lock | ✅ already |
| 6 | photos just before the cousin wedding | window start − 14 d → **start** | runs to end of wedding |
| 7 | I may have taken a photo of a medicine strip | medicine · no date | May window |
| 8 | road trip to Manali | Manali · no category | category street |
| 9 | parking spot at the mall | parking | {} |
| 10 | whiteboard from the offsite | whiteboard · episode office offsite | whiteboard only |
| 11 | prescription from when I had fever | medicine · episode fever week | medicine only |

**Must not over-interpret** (an invented filter hides the photo):

| # | Query | Expected |
|---|---|---|
| 12 | a cosy spot with dark wood and a coffee cup | **no filters**; semantic search only |
| 13 | something from a while back, I think it was a bill | receipt · **no date** |
| 14 | that photo from sometime after a trip | **no date** (which trip is unknown); optional recap hint "Which trip?" via anchors |
| 15 | sometime in 2024 / July 2025ish | unchanged from the synthetic set |

**Card-level checks** (query 1, soft mode):
- No non-Goa card shows Goa as matched.
- "match all your clues" is absent on those cards.
- The outside-dates strip shows only Goa café photos, or is hidden.
- `/extract` returns `notice: null` in under 1 s warm; `/health` shows `groq: false`.

---

## 9. What changes on the deck

| Slide | Change |
|---|---|
| **1: Thesis** | "We don't make search better. We make retrieval work when the date, place, album or words are missing." The metric is the brief's own: successful retrieval for users who can't precisely describe the photo. |
| **MVP + evidence** | **E1 table** (cue levels L3 to L0) replaces 0.866 as the main result. 0.866 appears only as the L3 row, labelled "fully described". Rules are the extractor (measured). Exact-date handling isn't claimed. |
| **Solution rationale** | One row per missing cue from §0: WHEN → vague time, chips, ribbon; WHERE → soft place plus ledger; ALBUM → moments and aliases; WORDS → semantic search and synonyms. "Why this isn't Ask Photos": it shows its reading and where each moment agrees, and it never asserts. |
| **Testing** | Session success (W1) is the headline, split by path and by first-query cue level. Then false confirmations, ledger opens, chip edits. |
| **Risks** | "Users ignore evidence" (measured by `ledger_viewed`). "L0 content-only queries fail" (measured by E1). Soft scoring keeps a wrong clue from hiding the photo. |
| **Roadmap** | A7 captions and OCR, justified by the E1 L0 row and the oracle-zero rows. F4 if not built. A5 vague-query catch. |

---

## 10. Changes from v1

| v1 item | v2 |
|---|---|
| F2 numeric-date alternatives (DD/MM vs MM/DD) | **Removed.** That is precise description, which is frozen. |
| F2 removing the ±3-day widening for numeric dates | **Removed.** Numeric handling stays as-is. |
| P3 NYE | Kept, reframed as an event anchor (`WHEN`). |
| F4 conflict flag | Kept optional, reframed as serving the brief's "may not remember when". |
| Fri: `real_dev` re-run | **Replaced by E1**, the cue-dropout eval. |
| Headline number | `real_test` 0.866 moves to "L3, fully described". The headline becomes E1 plus W1 session success. |
| B4 | Now also states that the set measures fully described photos. |
| New | §0 brief filter, E1, the W1 session-success metrics, the over-interpretation probes (§8 rows 12 to 14), the deck slide-1 framing. |
