"use client";

import { useState } from "react";
import { Masthead } from "@/app/components/Masthead";
import { Trail } from "@/app/components/Trail";
import {
  extract,
  search,
  withoutChip,
  type Chip,
  type Filters,
  type SearchResult,
} from "@/lib/api";

const EXAMPLES = [
  "That small café we went to during our Goa trip",
  "The medicine I took when I was sick, July 2025ish",
  "whiteboard from the product workshop",
  "my dog around monsoon 2025",
];

export default function Page() {
  const [text, setText] = useState("");
  const [chips, setChips] = useState<Chip[]>([]);
  const [filters, setFilters] = useState<Filters>({});
  const [result, setResult] = useState<SearchResult | null>(null);
  const [mode, setMode] = useState<"trails" | "baseline">("trails");
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [asked, setAsked] = useState(false);

  async function runSearch(q: string, f: Filters, m: "trails" | "baseline") {
    setBusy(true);
    setError(null);
    try {
      setResult(await search(q, f, m));
    } catch {
      setError("The search service did not respond. Try again in a moment.");
    } finally {
      setBusy(false);
    }
  }

  async function onFind(q = text) {
    const query = q.trim();
    if (!query) return;
    setAsked(true);
    setBusy(true);
    setError(null);
    try {
      const read = await extract(query);
      setChips(read.chips);
      setFilters(read.filters);
      setNotice(read.notice);
      setResult(await search(query, read.filters, mode));
    } catch {
      setError("The search service did not respond. Try again in a moment.");
    } finally {
      setBusy(false);
    }
  }

  function onRemoveChip(chip: Chip) {
    const next = withoutChip(filters, chip);
    setFilters(next);
    setChips(chips.filter((c) => c.id !== chip.id));
    // Never re-extract: the correction is the point of this step.
    void runSearch(text, next, mode);
  }

  function onToggle(next: "trails" | "baseline") {
    setMode(next);
    void runSearch(text, filters, next);
  }

  function onWiden() {
    const next = { ...filters };
    delete next["date_from"];
    delete next["date_to"];
    setFilters(next);
    setChips(chips.filter((c) => c.filter_key !== "date_from"));
    void runSearch(text, next, mode);
  }

  const hasDate = Boolean(filters["date_from"]);

  return (
    <main className="shell">
      <Masthead here="trails" />

      <section className="ask">
        <h1>Start with what you remember.</h1>
        <label>
          <span className="visually-hidden" />
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="A small café, somewhere on that trip…"
            maxLength={500}
            aria-label="What do you remember about the photo?"
          />
        </label>
        <div className="ask-row">
          <button className="primary" onClick={() => onFind()} disabled={busy || !text.trim()}>
            {busy ? "Looking…" : "Find the moment"}
          </button>
        </div>
        <div className="examples">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              onClick={() => {
                setText(ex);
                void onFind(ex);
              }}
            >
              {ex}
            </button>
          ))}
        </div>
      </section>

      {asked && chips.length > 0 && (
        <section className="read-as">
          <p>We read your memory as these clues. Remove any that are wrong.</p>
          <div className="chips">
            {chips.map((chip) => (
              <span className="chip" key={chip.id}>
                {chip.label}
                <span className="cue">{chip.cue.replace(/_/g, " ")}</span>
                <button onClick={() => onRemoveChip(chip)} aria-label={`Remove ${chip.label}`}>
                  ×
                </button>
              </span>
            ))}
          </div>
          {notice && <p className="notice">{notice}</p>}
        </section>
      )}

      {error && (
        <div className="empty">
          <h2>Something went wrong</h2>
          <p>{error}</p>
          <button onClick={() => void runSearch(text, filters, mode)}>Try again</button>
        </div>
      )}

      {busy && !result && (
        <div className="skeleton" aria-live="polite">
          <div />
          <div />
          <div />
        </div>
      )}

      {result && !error && (
        <>
          <div className="resultbar">
            <p>
              {result.episodes.length === 0
                ? "No photos matched."
                : `${result.total} photo${result.total === 1 ? "" : "s"} across ${result.episodes.length} moment${
                    result.episodes.length === 1 ? "" : "s"
                  }`}
            </p>
            <div className="toggle" role="group" aria-label="Retrieval mode">
              <button aria-pressed={mode === "trails"} onClick={() => onToggle("trails")}>
                Memory Trails
              </button>
              <button aria-pressed={mode === "baseline"} onClick={() => onToggle("baseline")}>
                Plain search
              </button>
            </div>
          </div>

          {result.episodes.length === 0 ? (
            <div className="empty">
              <h2>Nothing inside that window</h2>
              <p>
                {Object.keys(result.filters_applied).length > 0
                  ? `Searching where ${Object.entries(result.filters_applied)
                      .map(([k, v]) => `${k.replace(/_/g, " ")} is ${v}`)
                      .join(", ")}.`
                  : "No clues were applied."}
              </p>
              {hasDate && <button onClick={onWiden}>Widen the dates</button>}
            </div>
          ) : (
            <Trail episodes={result.episodes} />
          )}
        </>
      )}
    </main>
  );
}
