export type Alternative = {
  label: string;
  value: string;
  value_to?: string;
};

export type Chip = {
  id: string;
  cue: string;
  label: string;
  filter_key: string;
  value: string;
  value_to?: string;
  editable: boolean;
  alternatives?: Alternative[];
  /** "festival" when the parser looked the year up rather than the user saying it. */
  kind?: string;
};

export type Anchor = {
  id: string;
  cue: string;
  /** What kind of thing this is - "An event", "An object" - shown instead of a filter name. */
  kind_label?: string;
  label: string;
  filter_key: string;
  value: string;
  value_to?: string;
};

export type MonthlyChapter = {
  month: string;
  label: string;
  date_from: string;
  date_to: string;
  count: number;
  thumbnail: string;
};

export type FacetsResult = {
  locations: string[];
  categories: string[];
  episodes: string[];
  top_anchors: Anchor[];
  monthly_chapters: MonthlyChapter[];
  /** ISO date the demo treats as today; absent from older deployments. */
  demo_today?: string;
};

/** Mirrors retrieval/main.py DEMO_ANCHORS; used only if /facets does not answer. */
export const DEFAULT_ANCHORS: Anchor[] = [
  { id: "a1", cue: "event_anchor", kind_label: "An event", label: "graduation", filter_key: "episode", value: "sister's graduation" },
  { id: "a2", cue: "object", kind_label: "An object", label: "cake", filter_key: "category", value: "cake" },
  { id: "a3", cue: "object", kind_label: "People", label: "family", filter_key: "category", value: "family" },
  { id: "a4", cue: "object", kind_label: "A type of image", label: "handwritten note", filter_key: "category", value: "notes" },
  { id: "a5", cue: "event_anchor", kind_label: "An event", label: "college performance", filter_key: "episode", value: "college performance" },
  { id: "a6", cue: "object", kind_label: "A pet", label: "dog", filter_key: "category", value: "pet" },
];

export function anchorToChip(anchor: Anchor): Chip {
  return {
    id: `c_${anchor.id}`,
    cue: anchor.cue,
    label: anchor.label,
    filter_key: anchor.filter_key,
    value: anchor.value,
    value_to: anchor.value_to,
    editable: true,
  };
}

export type Filters = Record<string, string>;

/** No similarity score: the wireframe forbids exposing a false precision number. */
export type Photo = { id: string; file: string };

/** Structured evidence. The client turns these into the spec's noun phrases. */
export type Reason =
  | { kind: "episode" | "location" | "category"; value: string }
  | { kind: "date_window"; value: string; to: string };

/** Per-dimension certainty, never one global confidence number. */
export type EvidenceDetail = {
  dimension: string;
  value: string;
  certainty: "strong" | "possible" | "approximate";
  /** In the photo shown first, elsewhere in the moment, or only a range. */
  scope?: "direct" | "nearby" | "approximate";
  source: string;
};

export type SequencePhoto = { id: string; file: string; date: string; location: string };

/** One clue checked against one moment, exactly as retrieval/search.py match_ledger returns it. */
export type LedgerEntry = {
  kind: "episode" | "location" | "category" | "date_window";
  value: string;
  to?: string;
  matched: boolean;
  n?: number;
  offset_days?: number | null;
};

export type MatchLedger = LedgerEntry[];

export type Episode = {
  episode_id: string;
  episode: string;
  location: string;
  date_from: string | null;
  date_to: string | null;
  count: number;
  episode_total: number;
  places: number;
  scenes: [string, number][];
  span_days: number;
  usefulness: number;
  why: Reason[];
  evidence: EvidenceDetail[];
  photos: Photo[];
  ledger?: MatchLedger;
  clue_hits?: number;
};

export type EpisodeSequence = {
  episode_id: string;
  episode: string;
  location: string;
  photos: SequencePhoto[];
  count: number;
};

/** F4: the named event sits well outside the remembered time. Computed by /search from
 *  the filters it applied, with what its first page actually shows. */
export type Conflict = {
  episode: string;
  episode_dates: [string, string];
  window: [string | null, string | null];
  shown_episode: boolean;
  shown_window: boolean;
};

/** How the current date clue was read, so the check can tell a lookup from a memory. */
export type DateMeta = { kind?: string | null; alternatives: [string, string | null][] };

export type ExtractResult = {
  filters: Filters;
  chips: Chip[];
  source: "llm" | "rules";
  notice: string | null;
};

export type OutsidePhoto = {
  id: string;
  file: string;
  date: string;
  offset_days: number;
  score: number;
  category?: string;
  location?: string;
  title?: string;
};

export type CueSuggestion = {
  label: string;
  phrase: string;
  group: string;
  seen_in: number;
  of: number;
};

export type SearchResult = {
  episodes: Episode[];
  total: number;
  mode: "trails" | "soft" | "baseline";
  filters_applied: Filters;
  outside_window?: OutsidePhoto[];
  conflicts?: Conflict[];
  cue_suggestions?: CueSuggestion[];
  seen_applied?: string[];
};

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`${path} failed (${res.status})`);
  }
  return (await res.json()) as T;
}

export function extract(text: string) {
  return post<ExtractResult>("/api/py/extract", { text });
}

export function search(
  text: string,
  filters: Filters,
  mode: "trails" | "soft" | "baseline",
  rejected: string[] = [],
  boostKey?: string | null,
  dateMeta?: DateMeta | null,
  seen: string[] = [],
) {
  return post<SearchResult>("/api/py/search", {
    text,
    filters,
    mode,
    rejected,
    boost_key: boostKey || undefined,
    date_meta: dateMeta || undefined,
    seen,
  });
}

/** The date chip's reading, for the misdated-memory check. */
export function dateMetaFor(chips: Chip[], dateFrom?: string): DateMeta | null {
  // Only a chip that still matches the applied window describes it: state can lag a
  // chip edit by one render, and a stale reading must not excuse a real conflict.
  const c = chips.find((ch) => ch.filter_key === "date_from" && ch.value === dateFrom);
  if (!c) return null;
  return {
    kind: c.kind ?? null,
    alternatives: (c.alternatives ?? []).map((a) => [a.value, a.value_to ?? null]),
  };
}

/** The pinned "today" the parser reads relative phrases against (retrieval DEMO_TODAY). */
let facetsOnce: Promise<FacetsResult> | null = null;
export function facetsCached(): Promise<FacetsResult> {
  facetsOnce ??= fetchFacets();
  return facetsOnce;
}

export function episode(episodeId: string) {
  return post<EpisodeSequence>("/api/py/episode", { episode_id: episodeId });
}

export async function fetchFacets(): Promise<FacetsResult> {
  try {
    const res = await fetch("/api/py/facets");
    if (!res.ok) throw new Error(`facets failed (${res.status})`);
    return (await res.json()) as FacetsResult;
  } catch {
    return {
      locations: ["Bengaluru", "Pune", "Chennai", "Mumbai"],
      categories: ["cake", "family", "notes", "pet"],
      episodes: [],
      top_anchors: DEFAULT_ANCHORS,
      monthly_chapters: [],
    };
  }
}

/** Removing a chip drops its filter key — and the paired end of a date window. */
export function withoutChip(filters: Filters, chip: Chip): Filters {
  const next = { ...filters };
  delete next[chip.filter_key];
  if (chip.filter_key === "date_from") delete next["date_to"];
  return next;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function parts(iso: string) {
  const [y, m, d] = iso.split("-");
  return { y, m: MONTHS[Number(m) - 1] ?? m, d: String(Number(d)) };
}

/** Human date windows, as the wireframe writes them: "14-18 Dec 2023". */
/** Month-level windows for a moment's title: "Jun 2025", "Jun – Jul 2025". */
export function formatMonths(from: string | null, to: string | null): string {
  if (!from) return "";
  const a = parts(from);
  const b = parts(to ?? from);
  if (a.y === b.y && a.m === b.m) return `${a.m} ${a.y}`;
  if (a.y === b.y) return `${a.m} \u2013 ${b.m} ${a.y}`;
  return `${a.m} ${a.y} \u2013 ${b.m} ${b.y}`;
}

export function formatWindow(from: string | null, to: string | null): string {
  if (!from) return "";
  const a = parts(from);
  if (!to || from === to) return `${a.d} ${a.m} ${a.y}`;
  const b = parts(to);
  if (a.y === b.y && a.m === b.m) return `${a.d}\u2013${b.d} ${a.m} ${a.y}`;
  if (a.y === b.y) return `${a.d} ${a.m} \u2013 ${b.d} ${b.m} ${a.y}`;
  return `${a.d} ${a.m} ${a.y} \u2013 ${b.d} ${b.m} ${b.y}`;
}
