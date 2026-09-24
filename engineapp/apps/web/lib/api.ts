export type CognitiveProfile = {
  asset_type: string;
  cues_retained: string[];
  cues_lost: string[];
  query_verbatim: string;
};

export type CohortSummary = {
  n: number;
  rule: string;
  stages: Record<string, number>;
  outcomes: Record<string, number>;
};

export type CohortQuote = {
  evidence: string;
  source: string;
  date: string;
  era: string;
  failure_stage: string;
  outcome: string;
};

export type DiagnosisResult = {
  profile: CognitiveProfile;
  chips: Array<{ id: string; cue: string; label: string; type: "retained" | "lost" }>;
  source: "pipeline_prompt" | "rules";
  model: string | null;
  fallback_reason: string | null;
  cohort: CohortSummary;
  quotes: CohortQuote[];
};

export async function diagnose(text: string): Promise<DiagnosisResult> {
  const res = await fetch("/api/py/diagnose", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`diagnose failed (${res.status})`);
  return res.json();
}

export type Chip = {
  id: string;
  cue: string;
  label: string;
  filter_key: string;
  value: string;
  editable: boolean;
};

export type ExtractResult = {
  filters: Record<string, string>;
  chips: Chip[];
  source: "llm" | "rules";
  notice: string | null;
};

/** Backwards compatibility wrapper for older extract calls. */
export async function extract(text: string): Promise<ExtractResult> {
  const res = await fetch("/api/py/extract", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`extract failed (${res.status})`);
  return res.json();
}
