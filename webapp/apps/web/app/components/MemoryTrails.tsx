"use client";

import { useEffect, useRef, useState } from "react";
import { MemoryTopBar } from "@/app/components/MemoryTopBar";
import { Disclaimer } from "@/app/components/Disclaimer";
import { ClueList } from "@/app/components/ClueChip";
import { Moments, MAX_CANDIDATES } from "@/app/components/Moments";
import { EpisodeView } from "@/app/components/EpisodeView";
import { NoMatch, changesFor, type Change } from "@/app/components/NoMatch";
import { NotHere } from "@/app/components/NotHere";
import { Breadcrumb } from "@/app/components/Breadcrumb";
import { MemoryStrength, STRENGTH_TO_KEY, type Strength } from "@/app/components/MemoryStrength";
import { AnchorPicker } from "@/app/components/AnchorPicker";
import { TimeRibbon } from "@/app/components/TimeRibbon";
import { OutsideWindowStrip } from "@/app/components/OutsideWindowStrip";
import {
  DEFAULT_ANCHORS,
  anchorToChip,
  episode as fetchEpisode,
  extract,
  fetchFacets,
  formatWindow,
  search,
  withoutChip,
  type Alternative,
  type Anchor,
  type Chip,
  type Episode,
  type EpisodeSequence,
  type Filters,
  type MonthlyChapter,
  type OutsidePhoto,
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

/** The memory re-entry flow. Mounted full-screen over the photo app by AppShell;
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
  const sheetRef = useRef<HTMLDivElement>(null);
  const [stage, setStage] = useState<Stage>("compose");
  const [text, setText] = useState(initialText);
  const [heard, setHeard] = useState("");
  const [chips, setChips] = useState<Chip[]>([]);
  const [filters, setFilters] = useState<Filters>({});
  const [result, setResult] = useState<SearchResult | null>(null);
  const [sequence, setSequence] = useState<EpisodeSequence | null>(null);
  const [confirmedFile, setConfirmedFile] = useState<string | null>(null);
  const [mode, setMode] = useState<"trails" | "soft" | "baseline">("soft");
  const [previewOutside, setPreviewOutside] = useState<OutsidePhoto | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [strength, setStrength] = useState<Strength | null>(null);
  const [rejected, setRejected] = useState<string[]>([]);
  const [page, setPage] = useState(0);
  const [noneOpen, setNoneOpen] = useState(false);
  const [undo, setUndo] = useState<{ chip: Chip; filters: Filters } | null>(null);
  const [helped, setHelped] = useState<string | null>(null);
  const [anchors, setAnchors] = useState<Anchor[]>(DEFAULT_ANCHORS);
  const [selectedAnchorIds, setSelectedAnchorIds] = useState<Set<string>>(new Set());
  const [monthlyChapters, setMonthlyChapters] = useState<MonthlyChapter[]>([]);

  useEffect(() => {
    sheetRef.current?.scrollTo({ top: 0 });
  }, [stage]);

  useEffect(() => {
    void fetchFacets().then((res) => {
      if (res.top_anchors && res.top_anchors.length > 0) {
        setAnchors(res.top_anchors);
      }
      if (res.monthly_chapters && res.monthly_chapters.length > 0) {
        setMonthlyChapters(res.monthly_chapters);
      }
    });
  }, []);

  function onToggleAnchor(anchor: Anchor) {
    const isSelected = selectedAnchorIds.has(anchor.id);
    const nextIds = new Set(selectedAnchorIds);
    if (isSelected) {
      nextIds.delete(anchor.id);
      setSelectedAnchorIds(nextIds);
      track("anchor_removed", { cue: anchor.cue, value: anchor.value });
      const chipId = `c_${anchor.id}`;
      const targetChip = chips.find((c) => c.id === chipId);
      if (targetChip) {
        const nextFilters = withoutChip(filters, targetChip);
        setFilters(nextFilters);
        setChips(chips.filter((c) => c.id !== chipId));
      }
    } else {
      nextIds.add(anchor.id);
      setSelectedAnchorIds(nextIds);
      track("anchor_selected", { cue: anchor.cue, value: anchor.value });
      const chip = anchorToChip(anchor);
      const nextFilters = { ...filters, [anchor.filter_key]: anchor.value };
      if (anchor.value_to) nextFilters["date_to"] = anchor.value_to;
      setFilters(nextFilters);
      if (!chips.some((c) => c.id === chip.id)) {
        setChips((prev) => [...prev, chip]);
      }
    }
  }

  function onShiftTime(chapter: MonthlyChapter, direction: "earlier" | "later" | "chapter") {
    track("time_ribbon_shifted", { direction, month: chapter.month });
    const nextFilters: Filters = {
      ...filters,
      date_from: chapter.date_from,
      date_to: chapter.date_to,
    };
    const timeChip: Chip = {
      id: `c_month_${chapter.month}`,
      cue: "temporal_approx",
      label: chapter.label,
      filter_key: "date_from",
      value: chapter.date_from,
      value_to: chapter.date_to,
      editable: true,
    };
    const remainingChips = chips.filter(
      (c) => c.filter_key !== "date_from" && c.filter_key !== "date_to"
    );
    const nextChips = [...remainingChips, timeChip];
    setFilters(nextFilters);
    setChips(nextChips);
    setSelectedAnchorIds((prev) => {
      const next = new Set(prev);
      anchors.forEach((a) => {
        if (a.filter_key === "date_from") next.delete(a.id);
      });
      return next;
    });
    void runSearch(nextFilters, mode);
  }

  async function runSearch(
    f: Filters,
    m: "trails" | "soft" | "baseline",
    skip = rejected,
    st: Strength | null = strength
  ) {
    setBusy(true);
    setError(null);
    try {
      const boostKey = st ? STRENGTH_TO_KEY[st] : null;
      const res = await search(text, f, m, skip, boostKey);
      setResult(res);
      setPage(0);
      setNoneOpen(false);
      setStage(res.episodes.length === 0 ? "empty" : "moments");
    } catch {
      setError("The service didn’t respond. Your memory is still here — ask for the moments again.");
    } finally {
      setBusy(false);
    }
  }

  function onSelectAlternative(chip: Chip, alt: Alternative) {
    track("chip_alternative_taken", {
      chip_id: chip.id,
      from_value: chip.value,
      to_value: alt.value,
      label: alt.label,
    });
    const nextFilters: Filters = { ...filters };
    nextFilters[chip.filter_key] = alt.value;
    if (alt.value_to) {
      nextFilters["date_to"] = alt.value_to;
    } else {
      delete nextFilters["date_to"];
    }
    const updatedChips = chips.map((c) => {
      if (c.id === chip.id) {
        return {
          ...c,
          value: alt.value,
          value_to: alt.value_to,
          label: alt.label.replace(/^or\s+/, ""),
          alternatives: undefined,
        };
      }
      return c;
    });
    setFilters(nextFilters);
    setChips(updatedChips);
    void runSearch(nextFilters, mode, rejected, strength);
  }

  async function onContinue() {
    const query = text.trim();
    if (!query && chips.length === 0) return;
    reset();
    track("memory_reentry_started");
    if (query) {
      track("memory_description_submitted", { length: query.length });
    }
    setBusy(true);
    setError(null);
    try {
      if (query) {
        const read = await extract(query);
        setHeard(query);
        // Merge extracted chips with explicitly selected anchors
        const mergedFilters = { ...read.filters, ...filters };
        const mergedChips = [...chips];
        for (const extractedChip of read.chips) {
          if (!mergedChips.some((c) => c.filter_key === extractedChip.filter_key)) {
            mergedChips.push(extractedChip);
          }
        }
        setChips(mergedChips);
        setFilters(mergedFilters);
        setNotice(read.notice);
        setStage("recap");
      } else {
        const anchorLabels = chips.map((c) => c.label).join(" · ");
        const summaryText = `Photos with ${anchorLabels}`;
        setText(summaryText);
        setHeard(anchorLabels);
        setStage("recap");
      }
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
    if (chip.id.startsWith("c_")) {
      const anchorId = chip.id.slice(2);
      setSelectedAnchorIds((prev) => {
        const nextSet = new Set(prev);
        nextSet.delete(anchorId);
        return nextSet;
      });
    }
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

  function onOpenOutsidePhoto(photo: OutsidePhoto) {
    track("outside_window_opened", { photo_id: photo.id, offset_days: photo.offset_days });
    setPreviewOutside(photo);
  }

  function onConfirmOutside(photo: OutsidePhoto) {
    track("retrieval_confirmed", {
      photo_id: photo.id,
      outside_window: true,
      offset_days: photo.offset_days,
    });
    setConfirmedFile(photo.file);
    setPreviewOutside(null);
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

  /** Set-level miss: logged whatever the user does next, because it measures surfacing. */
  function onNoneMatched() {
    track("moments_none_matched", {
      shown,
      page,
      remaining,
      mode,
      episode_ids: visible.map((ep) => ep.episode_id).filter(Boolean),
    });
    setNoneOpen(true);
  }

  function onNextPage() {
    track("recovery_action_selected", { change: "next-moments" });
    setPage(page + 1);
    setNoneOpen(false);
    sheetRef.current?.scrollTo({ top: 0 });
  }

  function onEditClues() {
    track("recovery_action_selected", { change: "edit-clues" });
    setStage("recap");
  }

  /** Start a new memory without leaving the flow. */
  function restart() {
    setStage("compose");
    setResult(null);
    setSequence(null);
    setChips([]);
    setFilters({});
    setSelectedAnchorIds(new Set());
    setConfirmedFile(null);
    setPreviewOutside(null);
    setText("");
    setNotice(null);
    setRejected([]);
    setPage(0);
    setNoneOpen(false);
    setUndo(null);
    setStrength(null);
    setHelped(null);
  }

  /** Leave the flow entirely and return to the library. No resets: AppShell
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

  const start = page * MAX_CANDIDATES;
  const visible = result ? result.episodes.slice(start, start + MAX_CANDIDATES) : [];
  const shown = visible.length;
  const remaining = result ? Math.max(result.episodes.length - start - shown, 0) : 0;

  return (
    <div className="trails-sheet shell" ref={sheetRef}>
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
          <AnchorPicker
            anchors={anchors}
            selectedAnchorIds={selectedAnchorIds}
            onToggleAnchor={onToggleAnchor}
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
            <button
              className="btn primary"
              onClick={onContinue}
              disabled={busy || (!text.trim() && selectedAnchorIds.size === 0)}
            >
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
            <ClueList
              chips={chips}
              onRemove={onRemoveChip}
              onSelectAlternative={onSelectAlternative}
            />
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
            <button
              className="btn primary"
              onClick={() => runSearch(filters, mode, rejected, strength)}
              disabled={busy}
            >
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
          <TimeRibbon
            chapters={monthlyChapters}
            activeDateFrom={filters.date_from}
            activeDateTo={filters.date_to}
            onShift={onShiftTime}
          />
          <div className="actions" style={{ marginTop: 0, marginBottom: 16 }}>
            <p className="t-meta" style={{ flex: "1 1 auto" }} aria-live="polite">
              {page === 0
                ? `${shown} likely moment${shown === 1 ? "" : "s"}`
                : `Moments ${start + 1}–${start + shown}`}
              {result.episodes.length > shown && ` of ${result.episodes.length} found`}
            </p>
            <button
              className="btn quiet"
              onClick={() => {
                const next = mode === "baseline" ? "soft" : "baseline";
                setMode(next);
                void runSearch(filters, next);
              }}
            >
              {mode === "baseline" ? "Back to Memory Trails" : "Compare with plain search"}
            </button>
          </div>
          <Moments episodes={result.episodes} onOpen={onOpenEpisode} start={start} />
          {result.outside_window && result.outside_window.length > 0 && (
            <OutsideWindowStrip
              photos={result.outside_window}
              onOpenPhoto={onOpenOutsidePhoto}
            />
          )}
          <NotHere
            open={noneOpen}
            remaining={remaining}
            changes={changesFor(filters)}
            onOpen={onNoneMatched}
            onNextPage={onNextPage}
            onChange={onChange}
            onEditClues={onEditClues}
          />
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
        <>
          <TimeRibbon
            chapters={monthlyChapters}
            activeDateFrom={filters.date_from}
            activeDateTo={filters.date_to}
            onShift={onShiftTime}
          />
          <NoMatch filters={filters} onChange={onChange} onExit={closeTrails} />
        </>
      )}

      <Disclaimer />

      {previewOutside && (
        <div className="outside-modal-backdrop" onClick={() => setPreviewOutside(null)}>
          <div
            className="outside-modal-dialog"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Photo just outside date window"
          >
            <div className="outside-modal-head">
              <h2 className="t-section">Just outside your dates</h2>
              <button
                className="icon-btn"
                onClick={() => setPreviewOutside(null)}
                aria-label="Close"
              >
                ✕
              </button>
            </div>
            <figure className="outside-modal-hero">
              <img src={`/${previewOutside.file}`} alt="" />
              <figcaption className="t-support">
                <span className="outside-badge">
                  {previewOutside.offset_days > 0
                    ? `+${previewOutside.offset_days} days`
                    : `${previewOutside.offset_days} days`}
                </span>
                <span>{formatWindow(previewOutside.date, previewOutside.date)}</span>
                {previewOutside.location && <span> · {previewOutside.location}</span>}
              </figcaption>
            </figure>
            <div className="actions">
              <button className="btn primary" onClick={() => onConfirmOutside(previewOutside)}>
                That’s the one
              </button>
              <button className="btn ghost" onClick={() => setPreviewOutside(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
