export type Chip = {
  id: string;
  cue: string;
  label: string;
  filter_key: string;
  value: string;
  value_to?: string;
  editable: boolean;
};

export type Filters = Record<string, string>;

/** No similarity score: the wireframe forbids exposing a false precision number. */
export type Photo = { id: string; file: string };

/** Structured evidence. The client turns these into the spec's noun phrases. */
export type Reason =
  | { kind: "episode" | "location" | "category"; value: string }
  | { kind: "date_window"; value: string; to: string };

export type SequencePhoto = { id: string; file: string; date: string; location: string };

export type Episode = {
  episode_id: string;
  episode: string;
  location: string;
  date_from: string | null;
  date_to: string | null;
  count: number;
  episode_total: number;
  why: Reason[];
  photos: Photo[];
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

export type SearchResult = {
  episodes: Episode[];
  total: number;
  mode: "trails" | "baseline";
  filters_applied: Filters;
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

export function search(text: string, filters: Filters, mode: "trails" | "baseline") {
  return post<SearchResult>("/api/py/search", { text, filters, mode });
}

export function episode(episodeId: string) {
  return post<EpisodeSequence>("/api/py/episode", { episode_id: episodeId });
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
