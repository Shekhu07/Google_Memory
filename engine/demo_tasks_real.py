"""Generate real-phrasing evaluation tasks (Idea A1 / Task T1).

Re-authors the 30 evaluation tasks into phrasing patterns taken from real
reviews and verbatims ('about 2 years ago', 'last winter', 'Halloween 2024',
'25/12/2024', 'restaurant we visited in Udaipur last winter').

Fixed today anchor: 2026-09-23.
Split is by phrasing family: dev (tune on it) vs test (held-out).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_SYNTHETIC = ROOT / "data" / "eval" / "tasks.jsonl"
LIBRARY_FILE = ROOT / "webapp" / "apps" / "retrieval" / "data" / "library.jsonl"
OUT_FILE = ROOT / "data" / "eval" / "tasks_real.jsonl"

TODAY_STR = "2026-09-23"

DEV_FAMILIES = {
    "numeric_date",
    "festival_year",
    "relative_season",
    "n_years_ago",
    "hinglish_relative",
}

TEST_FAMILIES = {
    "day_month_word",
    "natural_question",
    "trip_relative",
    "festival_relative",
    "short_search",
}

FESTIVALS = {
    "diwali 2025": ("Diwali 2025", "Diwali ke time"),
    "onam lunch": ("Onam 2024", "Onam celebration"),
    "goa trip": ("Goa trip 2023", "a few weeks after the Goa trip"),
    "cousin wedding": ("cousin's wedding 2024", "shaadi ke time"),
    "office offsite": ("office offsite 2024", "team retreat"),
    "pondicherry trip": ("Pondicherry trip 2025", "trip to Pondicherry"),
    "manali trip": ("Manali trip 2025", "Manali vacation"),
    "laptop repair": ("laptop repair 2025", "repair receipt"),
    "puppy vet visits": ("puppy vet visit 2026", "new puppy checkup"),
    "friend's sangeet": ("sangeet 2025", "sangeet night"),
}

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def render_variants_for_task(base_task: dict, target: dict) -> list[dict]:
    """Render 2 real-phrasing queries for a base task."""
    date_str = target.get("date") or "2024-06-01"
    year = int(date_str[:4])
    month = int(date_str[5:7])
    day = int(date_str[8:10])
    episode = target.get("episode") or ""
    location = target.get("location") or ""
    category = target.get("category") or ""
    cues = base_task["cues_used"]

    # Calculate years ago relative to 2026-09-23
    years_ago = 2026 - year
    years_phrase = "about a year ago" if years_ago == 1 else f"about {years_ago} years ago"
    hinglish_years = "pichle saal" if years_ago == 1 else f"{years_ago} saal pehle"

    # Season mapping
    if month in (12, 1, 2):
        season_en = "last winter" if year >= 2025 else f"winter {year}"
    elif month in (7, 8, 9):
        season_en = "this monsoon" if year == 2026 else ("last monsoon" if year == 2025 else f"monsoon {year}")
    elif month in (5, 6):
        season_en = "last summer" if year >= 2025 else f"summer {year}"
    else:
        season_en = f"spring {year}"

    variants = []

    # Variant 1: Dev family (numeric_date, festival_year, relative_season, n_years_ago, hinglish_relative)
    if "exact_date" in cues:
        v1_query = f"{day:02d}/{month:02d}/{year}"
        v1_family = "numeric_date"
        v1_source = "real"
    elif episode and episode in FESTIVALS and ("diwali" in episode or "onam" in episode):
        v1_query = FESTIVALS[episode][0]
        v1_family = "festival_year"
        v1_source = "real"
    elif "temporal_approx" in cues:
        if base_task["id"] in ("task:002", "task:006", "task:013", "task:019"):
            v1_query = f"{hinglish_years} {location}".strip() if location else f"{hinglish_years} wali photo"
            v1_family = "hinglish_relative"
            v1_source = "constructed"
        elif base_task["id"] in ("task:003", "task:012", "task:018", "task:021", "task:024"):
            v1_query = f"{season_en} {category}".strip()
            v1_family = "relative_season"
            v1_source = "real"
        else:
            v1_query = f"{years_phrase} {category}".strip() if category else years_phrase
            v1_family = "n_years_ago"
            v1_source = "real"
    elif "place_named" in cues:
        v1_query = f"{hinglish_years} {location} me"
        v1_family = "hinglish_relative"
        v1_source = "constructed"
    else:
        v1_query = f"{years_phrase} {category}".strip()
        v1_family = "n_years_ago"
        v1_source = "real"

    # Variant 2: Test family (day_month_word, natural_question, trip_relative, festival_relative, short_search)
    if "exact_date" in cues:
        v2_query = f"{day} {MONTH_NAMES[month - 1]} {year}"
        v2_family = "day_month_word"
        v2_source = "real"
    elif episode and "goa" in episode:
        v2_query = "beach photo a few weeks after the Goa trip"
        v2_family = "trip_relative"
        v2_source = "real"
    elif episode and "wedding" in episode:
        v2_query = "just before the wedding ceremony"
        v2_family = "trip_relative"
        v2_source = "real"
    elif episode and episode in FESTIVALS and "ke time" in FESTIVALS[episode][1]:
        v2_query = f"{FESTIVALS[episode][1]} {location}".strip()
        v2_family = "festival_relative"
        v2_source = "constructed"
    elif location and category:
        v2_query = f"the {category} we visited in {location} {season_en}"
        v2_family = "natural_question"
        v2_source = "real"
    elif location:
        v2_query = f"photos in {location}"
        v2_family = "short_search"
        v2_source = "real"
    elif "text_in_image" in cues:
        v2_query = f"document with writing {season_en}"
        v2_family = "natural_question"
        v2_source = "real"
    else:
        v2_query = f"{day} {MONTH_NAMES[month - 1]} {year}"
        v2_family = "day_month_word"
        v2_source = "real"

    var1 = {
        "id": f"{base_task['id']}:v1",
        "base_task_id": base_task["id"],
        "query": v1_query.strip(),
        "phrasing_family": v1_family,
        "source": v1_source,
        "split": "dev" if v1_family in DEV_FAMILIES else "test",
        "cues_used": base_task["cues_used"],
        "target_id": base_task["target_id"],
        "answer_ids": base_task["answer_ids"],
        "n_answers": len(base_task["answer_ids"]),
    }

    var2 = {
        "id": f"{base_task['id']}:v2",
        "base_task_id": base_task["id"],
        "query": v2_query.strip(),
        "phrasing_family": v2_family,
        "source": v2_source,
        "split": "test" if v2_family in TEST_FAMILIES else "dev",
        "cues_used": base_task["cues_used"],
        "target_id": base_task["target_id"],
        "answer_ids": base_task["answer_ids"],
        "n_answers": len(base_task["answer_ids"]),
    }

    return [var1, var2]


def generate_real_tasks() -> list[dict]:
    synthetic = [json.loads(l) for l in TASKS_SYNTHETIC.open(encoding="utf-8")]
    library = {r["id"]: r for r in (json.loads(l) for l in LIBRARY_FILE.open(encoding="utf-8"))}

    tasks_real = []
    for t in synthetic:
        target = library.get(t["target_id"], {})
        variants = render_variants_for_task(t, target)
        tasks_real.extend(variants)

    return tasks_real


def main():
    tasks = generate_real_tasks()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    dev_count = sum(1 for t in tasks if t["split"] == "dev")
    test_count = sum(1 for t in tasks if t["split"] == "test")
    print(f"Generated {len(tasks)} real-phrasing tasks -> {OUT_FILE}")
    print(f"  Dev split:  {dev_count} tasks ({dev_count/len(tasks)*100:.1f}%)")
    print(f"  Test split: {test_count} tasks ({test_count/len(tasks)*100:.1f}%)")
    for t in tasks[:6]:
        print(f"  [{t['split'].upper()}] {t['id']}: {t['query']!r} ({t['phrasing_family']}, {t['source']})")


if __name__ == "__main__":
    main()
