"use client";

import { useState } from "react";
import { MemoryTopBar } from "@/app/components/MemoryTopBar";
import { Disclaimer } from "@/app/components/Disclaimer";
import { ClueList } from "@/app/components/ClueChip";
import { Moments, MAX_CANDIDATES } from "@/app/components/Moments";
import { EpisodeView } from "@/app/components/EpisodeView";
import { NoMatch, type Change } from "@/app/components/NoMatch";
import { Breadcrumb } from "@/app/components/Breadcrumb";
import { MemoryStrength, STRENGTH_TO_KEY, type Strength } from "@/app/components/MemoryStrength";
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
import { EXAMPLES } from "@/lib/examples";

type Stage = "compose" | "recap" | "moments" | "episode" | "confirmed" | "empty";

const TITLES: Record<Stage, string> = {
  compose: "Find a memory",
  recap: "Your memory",
  moments: "Likely moments",
  episode: "Moment",
  confirmed: "Found it",
  empty: "No close match yet",
};

/** The memory re-entry flow. Mounted full-screen over the photo app by PhotoApp;
 *  unmounted on exit, which is what clears its state. */
export function MemoryTrails({
  initialText = "",
  onExit,
}: {
  /** Carries a query typed into the Photos search bar into the composer, so the
   *  user does not describe the same memory twice. Seeds only - they still press
   *  Continue, because auto-extracting would hide the step being demonstrated. */
  initialText?: string;
  onExit: () => void;
}) {
  const [stage, setStage] = useState<Stage>("compose");
  const [text, setText] = useState(initialText);
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
  const [strength, setStrength] = useState<Strength | null>(null);
  const [rejected, setRejected] = useState<string[]>([]);
  const [undo, setUndo] = useState<{ chip: Chip; filters: Filters } | null>(null);
  const [helped, setHelped] = useState<string | null>(null);

  async function runSearch(f: Filters, m: "trails" | "baseline", skip = rejected) {
    setBusy(true);
    setError(null);
    try {
      const res = await search(text, f, m, skip);
      setResult(res);
      setStage(res.episodes.length === 0 ? "empty" : "moments");
    } catch {
      setError("The service didn’t respond. Your memory is still here — ask for the moments again.");
    } finally {
      setBusy(false);
    }
  }

  async function onContinue() {
    const query = text.trim();
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
      setError("The service didn’t respond. Your memory is still here — try continuing again.");
    } finally {
      setBusy(false);
    }
  }

  function onRemoveChip(chip: Chip) {
    track("memory_clue_removed", { cue: chip.cue });
    track("memory_recap_edited");
    const next = withoutChip(filters, chip);
    setUndo({ chip, filters });
    setFilters(next);
    setChips(chips.filter((c) => c.id !== chip.id));
    // Never re-extract: the correction is the point of this step.
    if (stage === "moments") void runSearch(next, mode);
  }

  /** Memory reconstruction is exploratory; a removed clue may turn out to matter. */
  function onUndo() {
    if (!undo) return;
    setFilters(undo.filters);
    setChips([...chips, undo.chip].sort((a, b) => a.id.localeCompare(b.id)));
    setUndo(null);
    if (stage === "moments") void runSearch(undo.filters, mode);
  }

  async function onOpenEpisode(ep: Episode) {
    track("episode_opened", { episode_id: ep.episode_id });
    // Without this a failed open leaves its message sitting above the episode
    // that opens fine on the next try. runSearch already clears the same way.
    setError(null);
    setBusy(true);
    try {
      setSequence(await fetchEpisode(ep.episode_id));
      setStage("episode");
    } catch {
      setError("That moment wouldn’t open. The others are still here.");
    } finally {
      setBusy(false);
    }
  }

  function onConfirm(photoId: string) {
    track("retrieval_confirmed", { photo_id: photoId });
    setConfirmedFile(sequence?.photos.find((p) => p.id === photoId)?.file ?? null);
    setStage("confirmed");
  }

  function onRejectEpisode() {
    const id = sequence?.episode_id;
    track("episode_rejected", { episode_id: id });
    // Session evidence, not a preference: don't offer this moment again this session.
    const skip = id ? [...rejected, id] : rejected;
    setRejected(skip);
    setSequence(null);
    setStage("moments");
    void runSearch(filters, mode, skip);
  }

  function onChange(c: Change) {
    track("recovery_action_selected", { change: c.id });
    const next = c.apply(filters);
    setFilters(next);
    setChips(chips.filter((ch) => ch.filter_key in next));
    void runSearch(next, mode);
  }

  /** Start a new memory without leaving the flow. */
  function restart() {
    setStage("compose");
    setResult(null);
    setSequence(null);
    setChips([]);
    setFilters({});
    setConfirmedFile(null);
    setText("");
    setNotice(null);
    setRejected([]);
    setUndo(null);
    setStrength(null);
    setHelped(null);
  }

  /** Leave the flow entirely and return to the library. No resets: PhotoApp
   *  unmounts this component, which destroys every useState above. */
  function closeTrails() {
    track("memory_reentry_exited");
    onExit();
  }

  function onBack() {
    if (stage === "episode") return setStage("moments");
    if (stage === "moments" || stage === "empty") return setStage("recap");
    return closeTrails();
  }

  const shown = result ? Math.min(result.episodes.length, MAX_CANDIDATES) : 0;

  return (
    <div className="trails-sheet shell">
      <MemoryTopBar
        title={TITLES[stage]}
        onBack={onBack}
        backLabel={stage === "compose" || stage === "recap" ? "Close Memory Trails" : "Go back"}
      />

      {stage === "compose" && (
        <section className="compose">
          <span className="privacy">Private by default · only searches when you ask</span>
          <h1 className="t-page">Start with what you remember</h1>
          <p className="sub">Describe a moment. It doesn’t have to be exact.</p>
          <textarea
            className="prompt"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="A small café during our Goa trip…"
            maxLength={500}
            aria-label="Describe the moment you remember"
            autoFocus
          />
          <p className="t-eyebrow examples-label">Try a memory like</p>
          <div className="examples">
            {EXAMPLES.map((ex) => (
              // Fills the field; the user still chooses to continue.
              <button key={ex} className="example" onClick={() => setText(ex)}>
                {ex}
              </button>
            ))}
          </div>
          <div className="actions">
            <button className="btn primary" onClick={onContinue} disabled={busy || !text.trim()}>
              {busy ? "Reading…" : "Continue"}
            </button>
          </div>
        </section>
      )}

      {stage === "recap" && (
        <section className="recap">
          <p className="t-eyebrow">Here’s what I heard</p>
          <p className="heard">“{heard}”</p>
          <p className="t-eyebrow">Memory clues</p>
          {chips.length > 0 ? (
            <ClueList chips={chips} onRemove={onRemoveChip} />
          ) : (
            <p className="t-support">No clues left. I’ll go on the words alone.</p>
          )}
          {undo && (
            <p className="t-support undo-row">
              Removed “{undo.chip.label}”.
              <button className="btn quiet" onClick={onUndo}>
                Undo
              </button>
            </p>
          )}
          <p className="t-support">Some clues may be approximate.</p>
          {notice && <p className="t-support">{notice}</p>}
          <MemoryStrength value={strength} onChange={setStrength} />
          <div className="actions">
            <button className="btn primary" onClick={() => runSearch(filters, mode)} disabled={busy}>
              {busy ? "Looking…" : "Show moments"}
            </button>
          </div>
        </section>
      )}

      {error && (
        <div className="panel">
          <h2 className="t-section">Something interrupted this</h2>
          <p>{error}</p>
          <button className="btn ghost" onClick={() => runSearch(filters, mode)}>
            Show moments
          </button>
        </div>
      )}

      {busy && stage === "moments" && !result && (
        <div className="skeleton" aria-live="polite">
          <div /><div /><div />
        </div>
      )}

      {stage === "moments" && result && !error && (
        <>
          <Breadcrumb heard={heard} chips={chips} onRemove={onRemoveChip} />
          {undo && (
            <p className="t-support undo-row">
              Removed “{undo.chip.label}”.
              <button className="btn quiet" onClick={onUndo}>
                Undo
              </button>
            </p>
          )}
          {rejected.length > 0 && (
            <p className="t-support">
              Not showing {rejected.length} moment{rejected.length === 1 ? "" : "s"} you ruled out.
            </p>
          )}
          <div className="actions" style={{ marginTop: 0, marginBottom: 16 }}>
            <p className="t-meta" style={{ flex: "1 1 auto" }} aria-live="polite">
              {shown} likely moment{shown === 1 ? "" : "s"}
              {result.episodes.length > shown && ` of ${result.episodes.length} found`}
            </p>
            <button
              className="btn quiet"
              onClick={() => {
                const next = mode === "trails" ? "baseline" : "trails";
                setMode(next);
                void runSearch(filters, next);
              }}
            >
              {mode === "trails" ? "Compare with plain search" : "Back to Memory Trails"}
            </button>
          </div>
          <Moments episodes={result.episodes} onOpen={onOpenEpisode} />
        </>
      )}

      {stage === "episode" && sequence && (
        <>
          <Breadcrumb heard={heard} chips={chips} />
          <EpisodeView
            sequence={sequence}
            onConfirm={onConfirm}
            onReject={onRejectEpisode}
            onAssetOpened={(id) => track("asset_opened", { photo_id: id })}
          />
        </>
      )}

      {stage === "confirmed" && (
        <section className="panel">
          <h2 className="t-section done">That’s the one</h2>
          {confirmedFile && (
            <img className="confirmed-media" src={`/${confirmedFile}`} alt="The photo you confirmed" />
          )}
          <p>
            Found in {secondsToConfirm() ?? "—"} seconds. Nothing was saved and your library is
            unchanged.
          </p>
          {helped === null ? (
            <div className="feedback">
              <p className="t-eyebrow">Did this help you get back to the memory?</p>
              <div className="options">
                {["Yes", "Partly", "No"].map((a) => (
                  <button
                    key={a}
                    className="example"
                    onClick={() => {
                      setHelped(a);
                      track("memory_reentry_exited", { helped: a });
                    }}
                  >
                    {a}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <p className="t-support">Thanks — noted for this session only.</p>
          )}
          <button className="btn ghost" onClick={restart}>
            Find another memory
          </button>
        </section>
      )}

      {stage === "empty" && !error && (
        <NoMatch filters={filters} onChange={onChange} onExit={closeTrails} />
      )}

      <Disclaimer />
    </div>
  );
}
