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
};

export type Anchor = {
  id: string;
  cue: string;
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
};

export const DEFAULT_ANCHORS: Anchor[] = [
  { id: "a1", cue: "place_named", label: "Goa", filter_key: "location", value: "Goa" },
  { id: "a2", cue: "object", label: "café", filter_key: "category", value: "cafe" },
  { id: "a3", cue: "object", label: "beach", filter_key: "category", value: "beach" },
  { id: "a4", cue: "place_named", label: "Bengaluru", filter_key: "location", value: "Bengaluru" },
  { id: "a5", cue: "object", label: "food", filter_key: "category", value: "food" },
  { id: "a6", cue: "object", label: "mountain", filter_key: "category", value: "mountain" },
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
  source: string;
};

export type SequencePhoto = { id: string; file: string; date: string; location: string };

export type LedgerEntry = {
  dimension: string;
  matched: boolean;
  user_value: string;
  actual_value: string;
  offset_days?: number | null;
};

export type MatchLedger = Record<string, LedgerEntry>;

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

export type SearchResult = {
  episodes: Episode[];
  total: number;
  mode: "trails" | "soft" | "baseline";
  filters_applied: Filters;
  outside_window?: OutsidePhoto[];
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
) {
  return post<SearchResult>("/api/py/search", {
    text,
    filters,
    mode,
    rejected,
    boost_key: boostKey || undefined,
  });
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
      locations: ["Goa", "Bengaluru", "Mumbai", "Chennai"],
      categories: ["cafe", "beach", "food", "mountain"],
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
export function formatWindow(from: string | null, to: string | null): string {
  if (!from) return "";
  const a = parts(from);
  if (!to || from === to) return `${a.d} ${a.m} ${a.y}`;
  const b = parts(to);
  if (a.y === b.y && a.m === b.m) return `${a.d}\u2013${b.d} ${a.m} ${a.y}`;
  if (a.y === b.y) return `${a.d} ${a.m} \u2013 ${b.d} ${b.m} ${a.y}`;
  return `${a.d} ${a.m} ${a.y} \u2013 ${b.d} ${b.m} ${b.y}`;
}
