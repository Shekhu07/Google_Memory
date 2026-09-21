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

/** The same endpoint contract the MVP uses, against this project's own service. */
export async function extract(text: string): Promise<ExtractResult> {
  const res = await fetch("/api/py/extract", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`extract failed (${res.status})`);
  return res.json();
}
