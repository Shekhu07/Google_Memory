# Memory Trails v2: Fix Plan (24 to 27 Sep 2026)

**Source:** pre-deploy review of https://memory-trails-v2.vercel.app on 23 Sep 2026 (live API probes, a walkthrough at 375px phone width, and a code read).
**Companion files:** `implementation-plan.md` (T1 to T6) and `retrieval-ideas.md` (A1 to A7). This file comes before T6. Nothing here adds scope beyond the locked problem.
**Hard stop on building:** end of Sun 27 Sep. The delayed-recall tests start 28 Sep.

---

## 0. Rules for this block

1. **Parity gates stay green.** Run `tests/test_service_parity.py` and `tests/test_export_onnx.py` before each deploy, plus the full suite: `.venv/bin/python -m pytest -q tests` and `webapp/apps/retrieval/tests`.
2. **Tune on `real_dev` and synthetic only.** `real_test` was scored once on 23 Sep, and that number stays on record as-is (see §6).
3. **Every change names the failure stage it serves**, either `system_misunderstood` (35.4%) or `not_surfaced` (41.7%).
4. **Pin "today".** Every probe below assumes `today = 2026-09-23`.

---

## 1. Schedule

| Day | Work | Done when |
|---|---|---|
| **Wed 24** | B1 to B4 blockers, P1 to P7 parser bugs | Probe table in §7 passes on local |
| **Thu 25** | F1 per-card match ledger (UI), F2 resolved date chips with alternatives | Ledger renders ✓/✗ at 320px; chip shows the window |
| **Fri 26** | F3 episode aliases, S1 to S4, re-run `real_dev` and synthetic | New dev numbers in PROGRESS |
| **Sat 27** | Deploy, incognito probe, S5 docs, W1 study-mode query capture, (optional F4) | Live link passes §7; test kit ready |

**Cut order if behind:** F4, then S4, then F2 alternatives (keep the resolved-window label), then F3 aliases beyond the five in §4. **Never cut:** B1 to B4, P1, P4, W1.

---

## 2. Blockers (Wed 24)

### B1: Evidence claims are false on non-matching cards · `system_misunderstood`, trust guardrail

**Seen live:** query "restaurant we went to in Goa last winter" in soft mode. The Manali, Pondicherry and Bengaluru cards all say *"Goa location · cafe-like scenes"*, and See evidence shows *Place: Goa, strong*. The Manali card says "3 match your clues" when none of its photos match.

**Cause:** `search.py → search()` copies the same `reasons` and `detail` onto every group:
```python
for g in groups:
    g["why"] = list(reasons)
    g["evidence"] = list(detail)
```
Also, `"N match your clues"` in `Moments.tsx:32` is really the number of hits (`ep.count`), not the number of matches.

**Fix: compute a ledger per episode from its own hit photos.**

`webapp/apps/retrieval/search.py`:
```python
from datetime import date

def _days_outside(d: str, lo: str | None, hi: str | None) -> int | None:
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


def _matches(r: dict, kind: str, want: str) -> bool:
    # Same rules as engine.demo_index.soft_search, so the ledger and the ranking agree.
    if kind == "category":
        return r.get("category") == want
    return want.lower() in (r.get(kind) or "").lower()   # location, episode: substring


def match_ledger(hit_rows: list, filters: dict) -> list:
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


def clue_hits(hit_rows: list, filters: dict) -> int:
    """Photos in this moment that satisfy EVERY clue given (date inside the window)."""
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
The evidence and the ledger both come from matched items only, so the certainty word ("strong") can never be attached to a clue the card doesn't have.

**Frontend** (`web/lib/api.ts`, `web/app/components/Moments.tsx`):
- Add `ledger` and `clue_hits` to the `Episode` type.
- Line 32: `if (ep.clue_hits > 0) parts.push(\`${ep.clue_hits} match all your clues\`)`. When `clue_hits === 0`, show nothing, not "0 match".
- Render the ledger under "Why this moment?" as F1 (Thursday). On Wednesday, just stop the false text.

**Tests** (`webapp/apps/retrieval/tests/test_search.py`):
- `test_non_matching_episode_does_not_claim_place`: with filters `{location: "Goa"}` in soft mode, a returned group whose location is not Goa has no `location` item in `why` and has `ledger[location].matched == False`.
- `test_clue_hits_le_count` for every group.
- `test_ledger_date_offset_sign`: a photo 9 days after `date_to` gives `offset_days == 9`.

**Parity:** photo-level results are unchanged, because only per-group metadata changes. `test_service_parity.py` must still pass untouched.

---

### B2: Production calls Groq on every extract, fails, and shows "Live extraction unavailable" · latency, trust

**Seen live:** `/health` reports `groq: true`. Every `/extract` returns `source: "rules"` with the notice *"Live extraction unavailable - used rule-based clue matching."*, which the recap screen prints. Extract takes 0.5 to 4.7 s.
**Probable cause:** `engine/groq.py` writes its token ledger to `data/interim/groq_usage.json`, which is read-only on Vercel, so the call throws and falls back.
**Decision:** rules beat the LLM on `real_test` (0.818 vs 0.718 recall@20), so **rules are the product extractor**. Say that on the deck as a decision, not as a fallback.

`webapp/apps/retrieval/main.py`:
```python
@lru_cache(maxsize=1)
def groq_client():
    # Rules won on the held-out split; the LLM path is opt-in for experiments only.
    if os.environ.get("EXTRACTOR", "rules") != "llm" or not os.environ.get("GROQ_API_KEY"):
        return None
    os.environ.setdefault("GROQ_LEDGER", "/tmp/groq_usage.json")   # Vercel FS is read-only
    from engine.groq import GroqClient
    ...
```
`webapp/apps/retrieval/llm_clues.py`: a deliberate rules path carries no notice:
```python
def extract(text, facets, client, today=None):
    today = today or date.today()
    if client is None:
        return dict(extract_clues(text, facets, today), notice=None)
    fallback = dict(extract_clues(text, facets, today),
                    notice="Live extraction unavailable - used rule-based clue matching.")
    ...
```
- Update `tests/test_llm_clues.py` if it asserts the notice when `client is None`.
- In Vercel, remove `GROQ_API_KEY` from `memory-trails-v2` or leave `EXTRACTOR` unset. Either way `/health` should report `groq: false`.
- **Done when** a live `/extract` returns in under 1 s warm, with `notice: null`.

---

### B3: Pin "today" for the frozen library · eval/prod parity

`clues.extract_clues` and `llm_clues.extract` default to `date.today()`, which on Vercel is the real date in UTC. Relative phrases ("last year", "pichle saal", "last winter") will drift after submission, and on 1 Jan 2027 every relative-year result changes.

`main.py`:
```python
DEMO_TODAY = date.fromisoformat(os.environ.get("DEMO_TODAY", "2026-09-23"))
...
return llm_clues.extract(text, FACETS, groq_client(), today=DEMO_TODAY)
```
Use the same constant in `engine/demo_eval.py` and `engine/demo_tasks_real.py` (import it, don't copy it). Add a line to the disclaimer: *"The demo treats today as 23 Sep 2026."*

---

### B4: The "real-phrasing" set is templated from each target's own metadata · credibility

Test queries read like *"the medicine we visited in Kochi last winter"* and *"the whiteboard we visited in Mumbai winter 2024"*. Each one carries the target's exact library location and category word. README calls them "natural user queries" and the jsonl tags them `source: real`.

- `engine/demo_tasks_real.py`: change `source: "real"` to `source: "real_pattern"` (the pattern is seen in real verbatims; the sentence is rendered from a template). Keep `constructed` as-is. Update `tests/test_demo_tasks_real.py`.
- README and PROGRESS: replace "Evaluated on natural user queries" with *"Evaluated on 60 template-rendered queries using phrasing patterns found in real verbatims (numeric dates, festivals, relative seasons, Hinglish, trip-relative). Queries name the target's place and category; human-written queries are measured separately (W1)."*
- Add to the deck facts table: denominator, source label, and "templated".

---

## 3. Parser bugs (Wed 24): `webapp/apps/retrieval/clues.py` · `system_misunderstood`

### P1: "last winter" spans 15 months
Today it returns 2024-12-01 → 2026-02-28. It should return 2025-12-01 → 2026-02-28.
```python
if re.search(r"\blast winter\b", low):
    end_year = today.year if today.month >= 3 else today.year - 1   # most recent winter that has ended
    feb_last = calendar.monthrange(end_year, 2)[1]
    return f"{end_year - 1}-12-01", f"{end_year}-02-{feb_last:02d}", "temporal_approx", "last winter"
```
**Knock-on:** `demo_tasks_real.py:73` labels *any* 2025+ winter photo "last winter", which agrees with the bug. Change it to label "last winter" only if the target's date falls in Dec(Y-1) to Feb(Y) for the most recent ended winter; otherwise use "winter {year}". Regenerate as `tasks_real_v2.jsonl` and keep v1 for the record.

### P2: "last summer" and "last monsoon" pick the wrong year
Summer (May to Jun) 2026 has already passed, yet "last summer" returns 2025.
```python
summer_year  = today.year if today.month >= 7  else today.year - 1   # May-Jun done by July
monsoon_year = today.year if today.month >= 10 else today.year - 1   # Jul-Sep done by October
```
Fix `demo_tasks_real.py:77` the same way.

### P3: "new year's eve 2025" resolves to 1 Jan 2025
Add to `FIXED_HOLIDAYS` (the longest-first sort already makes these win over "new year's"):
```python
"new year's eve": (12, 31), "new years eve": (12, 31), "nye": (12, 31),
```
"new year 2025" still means 1 Jan 2025. The `new year goa` episode is picked up by F3 aliases.

### P4: A bare "after" or "before" drops the trip and moves the window
"Goa trip photos after sunset" is treated as *after the Goa trip*, and the Goa episode and location are both dropped.
The rule should be that a trip-relative reading needs the preposition **attached to the trip mention**.
```python
def _mention_re(ep: str) -> str:
    names = [ep] + EPISODE_ALIASES.get(ep, [])          # F3 table; reuse here
    return r"(?:" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")"

QTY  = r"(?:(?P<n>\d+|a few|few|one|two|three|four|five|six)\s+(?P<unit>days?|weeks?|months?)\s+|(?P<adv>just|right|shortly)\s+)?"
DET  = r"(?:the\s+|our\s+|my\s+|that\s+)?"

after_en  = re.search(QTY + r"after\s+"  + DET + m, low)            # m = _mention_re(matched_ep)
before_en = re.search(QTY + r"before\s+" + DET + m, low)
after_hi  = re.search(m + r"(?:\s+trip)?\s+(?:ke\s+)?baad\b", low)
before_hi = re.search(m + r"(?:\s+trip)?\s+(?:se\s+|ke\s+)?pehle\b", low)
```
Take the amount and unit from the named groups instead of the separate `m_w`/`m_d`/`m_m` searches. Replace the hard-coded goa/wedding/sangeet resolution with the F3 alias table.

### P5: "Just before X" includes the whole trip
The "before" branches set `hi = ep_end.isoformat()`. Use `hi = ep_start.isoformat()` to mirror "after", which starts at `ep_end`.

### P6: "may" as a verb becomes the month of May
"I may have taken a photo of a medicine strip" gives a May window. In step 12 (bare month):
```python
BARE_MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
BARE_MONTHS["sept"] = 9
m = re.search(r"\b(" + "|".join(BARE_MONTHS) + r")\b", low)
if m and m.group(1) == "may" and not re.search(r"\b(in|during|around|early|mid|late|last|this|since)\s+may\b|\bmay\s+(?:mein|ke|me)\b", low):
    m = None
```
Abbreviations ("mar", "jun", "dec") stay valid only with a year (step 4), not bare.

### P7: 46 of 59 categories can't be reached, and "road" means street
- In `extract_clues`, make every library category match its own name before synonyms apply:
  ```python
  synonyms = {c: c for c in facets.categories}
  synonyms.update(CATEGORY_SYNONYMS)
  for word in sorted(synonyms, key=len, reverse=True): ...
  ```
  This makes `parking`, `screenshot`, `rangoli`, `chai stall`, `pav bhaji`, `auto rickshaw`, `dosa`, `notes` and the rest reachable.
- Add: `"parking lot": "parking", "car park": "parking", "parked": "parking", "screenshots": "screenshot", "rickshaw": "auto rickshaw", "chai": "chai stall"`.
- Remove `"road": "street"`, because "road trip" is not a street scene.
- Keep the `fest_anchor` skip only for `festival`. "Holi 2025" should give category `holi` plus a date, which is correct.

**Tests** (`webapp/apps/retrieval/tests/test_clues.py`): one test per row of the §7 probe table, plus the existing synthetic forms ("sometime in 2024", "July 2025ish") returning unchanged output.

---

## 4. Features (Thu 25 and Fri 26)

### F1: Per-card match ledger (Thu) · `not_surfaced`, trust
This is the UI half of B1. Under each moment card:

> **Goa** ✓ · **café** ✓ · **date** +21 days

- ✓ is `matched: true`. ✗ is shown as muted text ("not Goa"), never hidden. Dates show `offset_days` as "+N days" or "N days earlier".
- "See evidence" lists only matched dimensions, with certainty and source, as today.
- 320px: the ledger wraps to two lines at most. Test at 320 and 375.
- New event `ledger_viewed` (on expand) in `track.ts`. This is the metric for the riskiest assumption: do people read evidence at all?

### F2: Chips show the resolved window, with one alternative (Thu) · `system_misunderstood`
- **Label:** `ClueChip.tsx` renders a second line for date chips: `last winter · Dec 2025 – Feb 2026`, formatted from `value` and `value_to`.
- **Alternatives:** `clues.py` adds `chip["alternatives"] = [{label, value, value_to}]` in two ambiguous cases only:
  - Numeric dates where day and month are both ≤ 12: offer MM/DD. For example "05/12/2025" reads as 5 Dec 2025, with the alternative 12 May 2025.
  - Relative seasons and years: offer the same season one year earlier.
- **UI:** one text button under the chip, *"or Dec 2024 – Feb 2025?"*. Tapping it swaps the filter and re-runs the search. New event `chip_alternative_taken`.
- Remove the ±3-day widening for ambiguous numeric dates. It doesn't address DD/MM vs MM/DD, and the alternative does.

### F3: Episode aliases (Fri) · `system_misunderstood`, filing-cabinet segment
Episode matching today requires the full name ("office offsite"), so "whiteboard from the offsite" and "prescription from when I had fever" miss.
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
- Aliases apply only if no full episode name matched. Use word boundaries and longest first.
- Don't alias bare "goa", "diwali", "puppy" or "kerala". They're ambiguous across episodes or are locations.
- The chip label shows the real episode name ("office offsite"), so the interpretation stays visible and removable.
- P4 reuses this table.

### F4 (optional, Sat): Flag conflicting clues
When `filters.episode` and the date window don't overlap (for example "pichle saal wali Goa trip": the trip is Dec 2023, the window is 2025), don't silently combine them. Add `conflicts: [{"episode": "goa trip", "episode_dates": [...], "window": [...]}]` to the `/extract` response, and show on the recap screen:
> *Your Goa trip was Dec 2023, not last year. Showing both.*

Then drop the date window to a soft boost only. **Label it a hypothesis.** The 720-episode corpus has no evidence of misdated memories, so it's tested in the recall sessions, not claimed.

---

## 5. Should fix (Fri 26 and Sat 27)

### S1: "What part feels most certain?" does nothing
`MemoryTrails.tsx` stores `strength` but never sends it, and "Who was there" maps to `null` because the library has no people data. The component docstring says it weights the trusted cue, and README says there's no clarifying question.
**Choose one:**
- **Wire it (recommended, about 1 hour):** send `boost_key` in `/search`. `soft_search` doubles the matching β (`beta_place`, `beta_cat` or `beta_date`), and the default `None` keeps parity. Remove the "Who was there" option.
- **Cut it:** delete the component and the `STRENGTH_TO_KEY` map.

Whichever you choose, update README so it doesn't contradict the UI.

### S2: "Just outside your dates" ignores place and category
The Goa café query shows Hyderabad and Mumbai thalis under "Photos matching your clues". In `engine/demo_index.outside_window_photos` (and the `webapp/apps/retrieval/engine/` copy, kept identical):
```python
loc = filters.get("location", "").lower(); cat = filters.get("category", "")
...
if loc and loc not in (r.get("location") or "").lower(): continue
if cat and r.get("category") != cat: continue
```
If nothing survives, hide the strip. Change the subtitle to *"Same clues, a little outside your dates"*.

### S3: Episode ranking formula has dead terms
In `search.group_by_episode`:
- `filter_cover = len(dims) / len(dims)` is always 1. Use the ledger: `matched_dims / dims`.
- Evidence quality is identical for every group: `0.6 + 0.1 * len(reasons)`. Use the group's matched count.
- `_recognizability` uses episode size, not match count, so big episodes win by default. Use `min(1, 0.4 + 0.15 * g["clue_hits"])` or document why size is intended.

README already says these weights are judgement. Keep saying that. The photo-level recall numbers don't change.

### S4: Composer and scroll
- **Continue below the fold:** at 375px, *Continue* sits under the anchors and examples, and the button looks clipped. Make it a sticky footer inside the sheet (`position: sticky; bottom: 0;` with a background and safe-area padding).
- **Screens open scrolled mid-page:** Recap and Moments open scrolled partway down. Add `useEffect(() => sheetRef.current?.scrollTo({ top: 0 }), [stage])`.
- **Mismatched tiles:** the Places tile for Bengaluru shows a beach, and the Screenshots tile isn't a screenshot. Choose covers by the most common category per place, and the first `screenshot` record for that tile.

### S5: Docs (Sat)
- **README test count:** it says 188 in the layout block and 164 in "Running it". Run the suite and use one number.
- **Oracle label:** "Oracle (Perfect filters)" on `real_test` is a ±45-day window around the answer's date, and it scores below the parser. Rename it *"Date oracle (±45 d)"* and add one sentence on why the parser beats it: festival windows are ±3 days.
- **PROGRESS:** the "Waiting on you" list is stale (HF Space, Apify). Mark each item done or dropped.
- **Extractor:** add B2's decision ("rules are the product extractor; LLM measured and rejected on held-out").

---

## 6. Test-split policy after these fixes

`real_test` was scored once, on 23 Sep, with the v2 parser. After P1 to P7 and F3, re-scoring it is **no longer held-out**.

| Number | Label on the deck |
|---|---|
| 0.866 / 0.500 / 0.900 (23 Sep) | "v2 parser, held-out, templated real-pattern queries" |
| Post-fix `real_dev` and synthetic | "tuning splits" |
| Post-fix `real_test` (optional) | "re-used split, not held-out", or don't report it |
| **W1 wild split** | **the headline for human phrasing** |

### W1: Capture human-written queries in the recall tests (Sat) · kit item for T6
`main.py` promises visitor text is never logged, so keep that promise. Capture on the client, in study mode only:
- `?study=P01` in the URL turns on study mode. Typed queries are kept **in memory** (not localStorage) with a timestamp and the task id.
- A "End session: copy log" button at the end copies the JSON to the clipboard for the facilitator to paste into `research/mvp_test_results.md`.
- Add a consent line to `research/mvp_test_protocol.md`: *"What you type into the demo will be recorded as text for this study."*
- After the sessions, add the queries to `data/eval/tasks_wild.jsonl` with the task's known `answer_ids`, and score all strategies **once**.

---

## 7. Acceptance probe table (`today = 2026-09-23`)

Run these against local on Wed and against the live URL on Sat, in an incognito window.

| # | Query | Expected filters | Now (23 Sep) |
|---|---|---|---|
| 1 | restaurant we went to in Goa last winter | Goa · cafe · 2025-12-01 → 2026-02-28 | window 2024-12-01 → 2026-02-28 |
| 2 | last summer in kerala | episode summer in kerala · 2026-05-01 → 2026-06-30 | 2025 |
| 3 | new year's eve party goa 2025 | Goa · around 2025-12-31 (±3) · episode new year goa | 29 Dec 2024 → 4 Jan 2025, no episode |
| 4 | Goa trip photos after sunset | episode goa trip · Goa · no date | window after trip, Goa dropped |
| 5 | beach photo a few weeks after the Goa trip | beach · trip end → +42 d · no episode lock | ✅ already |
| 6 | photos just before the cousin wedding | window start − 14 d → **start** | window runs to end of wedding |
| 7 | I may have taken a photo of a medicine strip | medicine · no date | May window |
| 8 | road trip to Manali | Manali · no category | category street |
| 9 | parking spot at the mall | parking | {} |
| 10 | whiteboard from the offsite | whiteboard · episode office offsite | whiteboard only |
| 11 | prescription from when I had fever | medicine · episode fever week | medicine only |
| 12 | 05/12/2025 receipt | receipt · 2025-12-05, alternative 2025-05-12 | ±3 window, no alternative |
| 13 | 25/12/2025 | 2025-12-25 exact | ✅ already |
| 14 | Diwali 2025 rangoli | episode diwali 2025 · rangoli · 2025-10-17 → 10-23 | no rangoli category |
| 15 | sometime in 2024 / July 2025ish | unchanged from synthetic set | ✅ must not change |

**Card-level checks** (query 1, soft mode):
- No card whose location is not Goa shows "Goa" as matched.
- "N match all your clues" is 0 or absent on those cards.
- "Just outside your dates" shows only Goa café photos, or is hidden.
- `/extract` returns `notice: null` in under 1 s warm, and `/health` shows `groq: false`.

---

## 8. What changes on the deck

| Slide | Change |
|---|---|
| MVP + evidence | Rules are the product extractor (measured beat LLM). Real-pattern set is labelled as templated. W1 wild split is the human-phrasing number |
| Solution rationale | "Why this isn't Ask Photos": the system shows its reading (resolved chips), shows where each moment agrees or disagrees (ledger), and lets you correct it. It never asserts |
| Risks | Risk #2 (hard filter hides the photo) is mitigated by soft scoring **and** made visible by the ledger. New risk: users ignore evidence. Measured by `ledger_viewed` and `chip_alternative_taken` |
| Testing | Chip edits, alternatives taken, ledger opens, false confirmations |
| Roadmap | F4 conflict flag (if not built), A7 captions/OCR, A5 vague-query catch |
