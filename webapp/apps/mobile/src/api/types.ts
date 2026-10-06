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
  kind?: string;
};

export type Anchor = {
  id: string;
  cue: string;
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
  demo_today?: string;
};

export type Filters = Record<string, string>;

export type Photo = {
  id: string;
  file: string;
  date?: string;
  location?: string;
  category?: string;
  episode?: string;
};

export type Reason =
  | { kind: "episode" | "location" | "category"; value: string }
  | { kind: "date_window"; value: string; to: string };

export type EvidenceDetail = {
  dimension: string;
  value: string;
  certainty: "strong" | "possible" | "approximate";
  scope?: "direct" | "nearby" | "approximate";
  source: string;
};

export type LedgerEntry = {
  kind: "episode" | "location" | "category" | "date_window";
  value: string;
  to?: string;
  matched: boolean;
  n?: number;
  offset_days?: number | null;
};

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
  ledger?: LedgerEntry[];
  clue_hits?: number;
  full_match?: boolean;
};

export type SuggestedCategory = {
  category: string;
  word: string;
  label?: string;
};

export type ExtractResult = {
  filters: Filters;
  chips: Chip[];
  suggested_categories?: SuggestedCategory[];
  source?: string;
  notice?: string | null;
};

export type SearchResult = {
  results: Episode[];
  total: number;
  applied: Filters;
  suggested_relaxations?: string[];
};
