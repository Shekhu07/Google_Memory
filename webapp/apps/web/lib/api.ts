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

export type Photo = { id: string; file: string; score: number };

export type Episode = {
  episode_id: string;
  episode: string;
  location: string;
  date_from: string | null;
  date_to: string | null;
  count: number;
  why: string[];
  photos: Photo[];
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

/** Removing a chip drops its filter key — and the paired end of a date window. */
export function withoutChip(filters: Filters, chip: Chip): Filters {
  const next = { ...filters };
  delete next[chip.filter_key];
  if (chip.filter_key === "date_from") delete next["date_to"];
  return next;
}

export function formatWindow(from: string | null, to: string | null): string {
  if (!from) return "";
  if (!to || from === to) return from;
  return `${from} to ${to}`;
}
