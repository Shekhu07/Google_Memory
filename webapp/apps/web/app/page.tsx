"use client";

import { useState } from "react";
import { Masthead } from "@/app/components/Masthead";
import { Chips } from "@/app/components/Chips";
import { Moments, MAX_CANDIDATES } from "@/app/components/Moments";
import { EpisodeView } from "@/app/components/EpisodeView";
import { NoMatch, type Change } from "@/app/components/NoMatch";
import {
  episode as fetchEpisode,
  extract,
  search,
  withoutChip,
  type Chip,
  type Episode,
  type EpisodeSequence,
  type Filters,
  type SearchResult,
} from "@/lib/api";
import { reset, secondsToConfirm, track } from "@/lib/track";

/** The wireframe's state model, §6. */
type Stage = "compose" | "recap" | "moments" | "episode" | "confirmed" | "empty";

const EXAMPLES = [
  "That small café we went to during our Goa trip",
  "The medicine I took when I was sick, July 2025ish",
  "whiteboard from the product workshop",
  "my dog around monsoon 2025",
];

export default function Page() {
  const [stage, setStage] = useState<Stage>("compose");
  const [text, setText] = useState("");
  const [heard, setHeard] = useState("");
  const [chips, setChips] = useState<Chip[]>([]);
  const [filters, setFilters] = useState<Filters>({});
  const [result, setResult] = useState<SearchResult | null>(null);
  const [sequence, setSequence] = useState<EpisodeSequence | null>(null);
  const [confirmedFile, setConfirmedFile] = useState<string | null>(null);
  const [mode, setMode] = useState<"trails" | "baseline">("trails");
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSearch(f: Filters, m: "trails" | "baseline") {
    setBusy(true);
    setError(null);
    try {
      const res = await search(text, f, m);
      setResult(res);
      setStage(res.episodes.length === 0 ? "empty" : "moments");
    } catch {
      setError("The search service did not respond. Try again in a moment.");
    } finally {
      setBusy(false);
    }
  }

  async function onContinue(q = text) {
    const query = q.trim();
    if (!query) return;
    reset();
    track("memory_reentry_started");
    track("memory_description_submitted", { length: query.length });
    setBusy(true);
    setError(null);
    try {
      const read = await extract(query);
      setHeard(query);
      setChips(read.chips);
      setFilters(read.filters);
      setNotice(read.notice);
      setStage("recap");
    } catch {
      setError("The search service did not respond. Try again in a moment.");
    } finally {
      setBusy(false);
    }
  }

  function onRemoveChip(chip: Chip) {
    track("memory_clue_removed", { cue: chip.cue });
    track("memory_recap_edited");
    setFilters(withoutChip(filters, chip));
    setChips(chips.filter((c) => c.id !== chip.id));
    // Never re-extract: the correction is the point of this step.
  }

  async function onOpenEpisode(ep: Episode) {
    track("episode_opened", { episode_id: ep.episode_id });
    setBusy(true);
    try {
      setSequence(await fetchEpisode(ep.episode_id));
      setStage("episode");
    } catch {
      setError("Could not open that moment.");
    } finally {
      setBusy(false);
    }
  }

  function onConfirm(photoId: string) {
    track("retrieval_confirmed", { photo_id: photoId });
    const photo = sequence?.photos.find((p) => p.id === photoId);
    setConfirmedFile(photo?.file ?? null);
    setStage("confirmed");
  }

  function onRejectEpisode() {
    track("episode_rejected", { episode_id: sequence?.episode_id });
    setSequence(null);
    setStage("moments");
  }

  function onChange(c: Change) {
    track("recovery_action_selected", { change: c.id });
    const next = c.apply(filters);
    setFilters(next);
    setChips(chips.filter((ch) => ch.filter_key in next));
    void runSearch(next, mode);
  }

  function onExit() {
    track("memory_reentry_exited");
    setStage("compose");
    setResult(null);
    setSequence(null);
    setChips([]);
    setFilters({});
    setConfirmedFile(null);
    setText("");
  }

  function onToggle(next: "trails" | "baseline") {
    setMode(next);
    void runSearch(filters, next);
  }

  const shown = result ? Math.min(result.episodes.length, MAX_CANDIDATES) : 0;

  return (
    <main className="shell">
      <Masthead here="trails" />

      {stage === "compose" && (
        <section className="ask">
          <h1>Start with what you remember.</h1>
          <p className="lede">Describe a moment. It doesn&rsquo;t have to be exact.</p>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="A small café, somewhere on that trip…"
            maxLength={500}
            aria-label="Describe the moment you remember"
          />
          <div className="ask-row">
            <button className="primary" onClick={() => onContinue()} disabled={busy || !text.trim()}>
              {busy ? "Reading…" : "Continue"}
            </button>
          </div>
          <p className="when">Try:</p>
          <div className="examples">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => {
                  setText(ex);
                  void onContinue(ex);
                }}
              >
                {ex}
              </button>
            ))}
          </div>
        </section>
      )}

      {(stage === "recap" || stage === "moments" || stage === "empty") && (
        <section className="read-as">
          {stage === "recap" ? (
            <>
              <button className="linkish" onClick={onExit}>
                ← Start again
              </button>
              <p>Here&rsquo;s what I heard</p>
              <blockquote className="heard">“{heard}”</blockquote>
            </>
          ) : (
            <button className="linkish" onClick={() => setStage("recap")}>
              ← Change a clue
            </button>
          )}
          <p>Memory clues {chips.length > 0 && "— remove any that are wrong."}</p>
          {chips.length > 0 ? (
            <Chips chips={chips} onRemove={onRemoveChip} />
          ) : (
            <p className="when">No clues left. I&rsquo;ll search on the words alone.</p>
          )}
          <p className="when">Some clues may be approximate.</p>
          {notice && <p className="notice">{notice}</p>}
          {stage === "recap" && (
            <div className="ask-row">
              <button className="primary" onClick={() => runSearch(filters, mode)} disabled={busy}>
                {busy ? "Looking…" : "Show moments"}
              </button>
            </div>
          )}
        </section>
      )}

      {error && (
        <div className="empty">
          <h2>Something went wrong</h2>
          <p>{error}</p>
          <button className="secondary" onClick={() => runSearch(filters, mode)}>
            Try again
          </button>
        </div>
      )}

      {stage === "moments" && result && !error && (
        <>
          <div className="resultbar">
            <p>
              {shown} moment{shown === 1 ? "" : "s"} to explore
              {result.episodes.length > shown && ` (of ${result.episodes.length} found)`}
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
          <Moments episodes={result.episodes} onOpen={onOpenEpisode} />
        </>
      )}

      {stage === "episode" && sequence && (
        <EpisodeView
          sequence={sequence}
          onConfirm={onConfirm}
          onReject={onRejectEpisode}
          onBack={() => setStage("moments")}
          onAssetOpened={(id) => track("asset_opened", { photo_id: id })}
        />
      )}

      {stage === "confirmed" && (
        <section className="empty">
          <h2>Found it</h2>
          {confirmedFile && <img className="confirmed" src={`/${confirmedFile}`} alt="The photo you confirmed" />}
          <p>
            Reached in {secondsToConfirm() ?? "—"} seconds. Your library is unchanged.
          </p>
          <button className="secondary" onClick={onExit}>
            Find another memory
          </button>
        </section>
      )}

      {stage === "empty" && !error && (
        <NoMatch filters={filters} onChange={onChange} onExit={onExit} />
      )}
    </main>
  );
}
