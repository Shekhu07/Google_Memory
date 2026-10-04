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
import { Recover, type RecoveryReason } from "@/app/components/Recover";
import {
  DEFAULT_ANCHORS,
  anchorToChip,
  episode as fetchEpisode,
  extract,
  dateMetaFor,
  facetsCached,
  formatMonths,
  formatWindow,
  search,
  withoutChip,
  type Alternative,
  type Anchor,
  type Chip,
  type Conflict,
  type Episode,
  type EpisodeSequence,
  type Filters,
  type MonthlyChapter,
  type OutsidePhoto,
  type SearchResult,
} from "@/lib/api";
import { reset, secondsToConfirm, track } from "@/lib/track";
import { EXAMPLES, PRIMARY_EXAMPLE } from "@/lib/examples";

type Stage = "compose" | "recap" | "moments" | "episode" | "recover" | "confirmed" | "empty";

const TITLES: Record<Stage, string> = {
  compose: "Find a memory",
  recap: "Your memory",
  moments: "Likely moments",
  episode: "Moment",
  recover: "Not this moment",
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
  const [confirmedId, setConfirmedId] = useState<string | null>(null);
  const [confirmedSeq, setConfirmedSeq] = useState<EpisodeSequence | null>(null);
  const [revisit, setRevisit] = useState(false);
  const [zoom, setZoom] = useState(false);
  const [rejectedSeq, setRejectedSeq] = useState<EpisodeSequence | null>(null);
  const [recoveryNote, setRecoveryNote] = useState<string | null>(null);
  const [recoveryUndo, setRecoveryUndo] = useState<{
    filters: Filters;
    chips: Chip[];
    rejected: string[];
  } | null>(null);
  const [addText, setAddText] = useState("");
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
  const [seen, setSeen] = useState<string[]>([]);
  const [seenUndo, setSeenUndo] = useState<string | null>(null);
  const [helped, setHelped] = useState<string | null>(null);
  const [anchors, setAnchors] = useState<Anchor[]>(DEFAULT_ANCHORS);
  const [selectedAnchorIds, setSelectedAnchorIds] = useState<Set<string>>(new Set());
  const [monthlyChapters, setMonthlyChapters] = useState<MonthlyChapter[]>([]);

  useEffect(() => {
    sheetRef.current?.scrollTo({ top: 0 });
  }, [stage]);

  useEffect(() => {
    void facetsCached().then((res) => {
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
      track("memory_anchor_removed", { cue: anchor.cue, value: anchor.value });
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
      track("memory_anchor_selected", { cue: anchor.cue, value: anchor.value });
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
    if (direction === "earlier") track("episode_shifted_earlier", { month: chapter.month });
    if (direction === "later") track("episode_shifted_later", { month: chapter.month });
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
    st: Strength | null = strength,
    s = seen
  ) {
    setBusy(true);
    setError(null);
    try {
      const boostKey = st ? STRENGTH_TO_KEY[st] : null;
      const res = await search(text, f, m, skip, boostKey, dateMetaFor(chips, f.date_from), s);
      setResult(res);
      setPage(0);
      setNoneOpen(false);
      setStage(res.episodes.length === 0 ? "empty" : "moments");
      if (res.episodes.length > 0) {
        track("moments_shown", { count: Math.min(res.episodes.length, MAX_CANDIDATES), mode: m });
      }
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
    if (chip.cue === "seen" || chip.filter_key === "seen") {
      track("seen_cue_removed", { label: chip.label });
      track("memory_recap_edited");
      const nextSeen = seen.filter((s) => s !== chip.label);
      setSeen(nextSeen);
      setChips((prev) => prev.filter((c) => c.id !== chip.id));
      if (seenUndo === chip.label) setSeenUndo(null);
      if (stage === "moments" || stage === "empty") {
        void runSearch(filters, mode, rejected, strength, nextSeen);
      }
      return;
    }
    track("memory_clue_removed", { cue: chip.cue });
    track("memory_recap_edited");
    const next = withoutChip(filters, chip);
    setUndo({ chip, filters });
    setFilters(next);
    setChips((prev) => prev.filter((c) => c.id !== chip.id));
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

  function onPickSeen(label: string, rank: number) {
    if (seen.length >= 3 || seen.includes(label)) return;
    track("seen_cue_picked", { label, rank });
    const nextSeen = [...seen, label];
    setSeen(nextSeen);
    setSeenUndo(label);
    const seenChip: Chip = {
      id: `seen_${label}`,
      cue: "seen",
      label: label,
      filter_key: "seen",
      value: label,
      editable: false,
    };
    setChips((prev) => [...prev, seenChip]);
    void runSearch(filters, mode, rejected, strength, nextSeen);
  }

  function onUndoSeen() {
    if (!seenUndo) return;
    const label = seenUndo;
    track("seen_cue_removed", { label });
    const nextSeen = seen.filter((s) => s !== label);
    setSeen(nextSeen);
    setChips((prev) => prev.filter((c) => c.id !== `seen_${label}`));
    setSeenUndo(null);
    void runSearch(filters, mode, rejected, strength, nextSeen);
  }

  /** Memory reconstruction is exploratory; a removed clue may turn out to matter. */
  function onUndo() {
    if (!undo) return;
    setFilters(undo.filters);
    setChips([...chips, undo.chip].sort((a, b) => a.id.localeCompare(b.id)));
    setUndo(null);
    track("memory_clue_undo", { cue: undo.chip.cue });
    if (stage === "moments") void runSearch(undo.filters, mode);
  }

  /** Add a remembered detail to the current memory without starting over. */
  async function onAddClue() {
    const more = addText.trim();
    if (!more) return;
    setBusy(true);
    setError(null);
    try {
      const read = await extract(more);
      // Only one clue per dimension can steer the search, so a new detail never
      // silently replaces one the user already has: it joins the description, which
      // the image search reads, and the note says so. Remove a clue to swap it.
      const have = new Set(chips.map((c) => c.filter_key));
      const fresh = read.chips.filter((c) => !have.has(c.filter_key));
      const clash = read.chips.filter((c) => have.has(c.filter_key));
      if (fresh.length > 0) {
        const stamp = Date.now();
        setChips([...chips, ...fresh.map((c, i) => ({ ...c, id: `c_add${stamp}_${i}` }))]);
        const next = { ...filters };
        for (const c of fresh) {
          next[c.filter_key] = read.filters[c.filter_key];
          if (c.filter_key === "date_from" && read.filters.date_to) next.date_to = read.filters.date_to;
        }
        setFilters(next);
        track("memory_clue_added", { cues: fresh.map((c) => c.cue) });
      }
      setNotice(
        fresh.length === 0 && clash.length === 0
          ? `Added “${more}” to your description.`
          : clash.length > 0
            ? `Added “${more}” to your description. You already have ${clash
                .map((c) => `“${chips.find((h) => h.filter_key === c.filter_key)?.label}”`)
                .join(", ")} as that kind of clue — remove it if “${clash
                .map((c) => c.label)
                .join(", ")}” should steer instead.`
            : null
      );
      setHeard(heard ? `${heard} · ${more}` : more);
      setText(text ? `${text} ${more}` : more);
      setAddText("");
    } catch {
      setError("The service didn’t respond. Your memory is still here — try adding it again.");
    } finally {
      setBusy(false);
    }
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
    track("retrieval_confirmed", { photo_id: photoId, seen });
    setConfirmedFile(sequence?.photos.find((p) => p.id === photoId)?.file ?? null);
    setConfirmedId(photoId);
    setConfirmedSeq(sequence);
    setRevisit(false);
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
      seen,
    });
    setConfirmedFile(photo.file);
    setConfirmedId(photo.id);
    setConfirmedSeq(null);
    setRevisit(false);
    setPreviewOutside(null);
    setStage("confirmed");
  }

  /** "Not this moment": rule it out, then ask once what felt wrong (checklist 1.4). */
  function onRejectEpisode() {
    const id = sequence?.episode_id;
    track("episode_rejected", { episode_id: id });
    setRejectedSeq(sequence);
    setSequence(null);
    setStage("recover");
  }

  function keptLabels(f: Filters): string {
    const labels = chips.filter((c) => c.filter_key in f || c.cue === "seen").map((c) => c.label);
    return labels.length ? `Keeping ${labels.join(", ")}.` : "Keeping your description.";
  }

  /** Each answer changes one dimension, says what changed, and can be undone. */
  function onRecover(reason: RecoveryReason) {
    const id = rejectedSeq?.episode_id;
    // Session evidence, not a preference: this moment is not offered again this session.
    const skip = id && !rejected.includes(id) ? [...rejected, id] : rejected;
    const before = { filters, chips, rejected };
    let next: Filters = { ...filters };
    let nextChips = chips;
    let note = "Ruled out that moment. Showing the next likely ones.";

    if (reason === "wrong_day") {
      const days = (rejectedSeq?.photos ?? []).map((p) => p.date).filter(Boolean).sort();
      const lo = filters.date_from ?? days[0]?.slice(0, 10);
      const hi = filters.date_to ?? days[days.length - 1]?.slice(0, 10) ?? lo;
      if (lo && hi) {
        const shift = (iso: string, d: number) => {
          const t = new Date(`${iso}T00:00:00Z`);
          t.setUTCDate(t.getUTCDate() + d);
          return t.toISOString().slice(0, 10);
        };
        next = { ...next, date_from: shift(lo, -30), date_to: shift(hi, 30) };
        const dateChip: Chip = {
          id: "c_nearby_days",
          cue: "temporal_approx",
          label: "nearby days",
          filter_key: "date_from",
          value: next.date_from,
          value_to: next.date_to,
          editable: true,
        };
        note = `${keptLabels(withoutKey(filters, "date_from"))} Looking at nearby days.`;
        nextChips = [...chips.filter((c) => c.filter_key !== "date_from"), dateChip];
      }
    } else if (reason === "wrong_place") {
      if (filters.location) {
        next = withoutKey(filters, "location");
        note = `${keptLabels(next)} Looking beyond ${filters.location}.`;
        nextChips = chips.filter((c) => c.filter_key !== "location");
      } else {
        note = `Ruled out that moment and its place. ${keptLabels(filters)}`;
      }
    } else if (reason === "wrong_people") {
      note = "This prototype can’t recognise people, so I’ve ruled out that moment and kept your clues.";
    } else if (reason === "wrong_type") {
      if (filters.category) {
        next = withoutKey(filters, "category");
        note = `${keptLabels(next)} Looking for a different kind of photo.`;
        nextChips = chips.filter((c) => c.filter_key !== "category");
      } else {
        note = `Ruled out that moment. ${keptLabels(filters)}`;
      }
    }

    track("recovery_action_selected", { change: reason, episode_id: id });
    setRecoveryUndo(before);
    setRecoveryNote(note);
    setRejected(skip);
    setFilters(next);
    setChips(nextChips);
    setRejectedSeq(null);
    void runSearch(next, mode, skip);
  }

  function onRecoveryUndo() {
    if (!recoveryUndo) return;
    track("recovery_action_selected", { change: "undo" });
    setFilters(recoveryUndo.filters);
    setChips(recoveryUndo.chips);
    setRejected(recoveryUndo.rejected);
    setRecoveryUndo(null);
    setRecoveryNote(null);
    void runSearch(recoveryUndo.filters, mode, recoveryUndo.rejected);
  }

  function onChange(c: Change) {
    track("recovery_action_selected", { change: c.id });
    const next = c.apply(filters);
    setFilters(next);
    setChips(chips.filter((ch) => ch.cue === "seen" || ch.filter_key in next));
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
    setSeen([]);
    setSeenUndo(null);
    setSelectedAnchorIds(new Set());
    setConfirmedFile(null);
    setConfirmedId(null);
    setConfirmedSeq(null);
    setRevisit(false);
    setZoom(false);
    setRejectedSeq(null);
    setRecoveryNote(null);
    setRecoveryUndo(null);
    setAddText("");
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
    // The abandonment signal: leaving without an explicit "That's the one".
    if (!confirmedId) track("prototype_exited", { stage });
    onExit();
  }

  function onBack() {
    if (stage === "confirmed" && revisit) return setRevisit(false);
    if (stage === "episode") return setStage("moments");
    if (stage === "recover") {
      // Backing out still rules the moment out: the user already said "not this".
      const id = rejectedSeq?.episode_id;
      const skip = id && !rejected.includes(id) ? [...rejected, id] : rejected;
      setRejected(skip);
      setRejectedSeq(null);
      return void runSearch(filters, mode, skip);
    }
    if (stage === "moments" || stage === "empty") return setStage("recap");
    return closeTrails();
  }

  const start = page * MAX_CANDIDATES;
  const visible = result ? result.episodes.slice(start, start + MAX_CANDIDATES) : [];
  const shown = visible.length;
  const remaining = result ? Math.max(result.episodes.length - start - shown, 0) : 0;

  const STAGE_STEPS: Record<Stage, { step: number; total: number; label: string }> = {
    compose: { step: 1, total: 4, label: "Describe memory" },
    recap: { step: 2, total: 4, label: "Review clues" },
    moments: { step: 3, total: 4, label: "Select moment" },
    episode: { step: 4, total: 4, label: "Confirm photo" },
    recover: { step: 3, total: 4, label: "Refine moment" },
    confirmed: { step: 4, total: 4, label: "Memory found" },
    empty: { step: 3, total: 4, label: "No match" },
  };

  return (
    <div className="trails-sheet shell" ref={sheetRef}>
      <div className="trails-sheet-handle" aria-hidden="true" />
      <MemoryTopBar
        title={TITLES[stage]}
        onBack={onBack}
        backLabel={stage === "compose" || stage === "recap" ? "Close Memory Trails" : "Go back"}
      />
      {stage !== "confirmed" && (
        <div className="trails-step-bar" aria-label={`Step ${STAGE_STEPS[stage].step} of ${STAGE_STEPS[stage].total}: ${STAGE_STEPS[stage].label}`}>
          <div className="step-dots">
            {[1, 2, 3, 4].map((s) => (
              <span
                key={s}
                className={`step-dot ${s === STAGE_STEPS[stage].step ? "active" : s < STAGE_STEPS[stage].step ? "completed" : ""}`}
              />
            ))}
          </div>
          <span className="step-label">Step {STAGE_STEPS[stage].step} of 4 · {STAGE_STEPS[stage].label}</span>
        </div>
      )}

      {stage === "compose" && (
        <section className="compose">
          <span className="privacy">Private by default · only searches when you ask</span>
          <h1 className="t-page">Describe the moment, not the photo</h1>
          <p className="sub">
            Start with what you remember. It’s okay if you are unsure about the date, place, or
            exact words.
          </p>
          <textarea
            className="prompt"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={`${PRIMARY_EXAMPLE.charAt(0).toUpperCase()}${PRIMARY_EXAMPLE.slice(1)}…`}
            maxLength={500}
            aria-label="Describe the moment you remember"
            autoFocus
          />
          <AnchorPicker
            anchors={anchors}
            selectedAnchorIds={selectedAnchorIds}
            query={text}
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
          {seenUndo && (
            <p className="t-support undo-row">
              Added “{seenUndo}”.
              <button className="btn quiet" onClick={onUndoSeen}>
                Undo
              </button>
            </p>
          )}
          <p className="t-support">Some clues may be approximate.</p>
          {notice && <p className="t-support">{notice}</p>}
          <div className="add-clue">
            <label className="t-eyebrow" htmlFor="add-clue">
              Remember something else?
            </label>
            <div className="add-clue-row">
              <input
                id="add-clue"
                className="add-clue-input"
                value={addText}
                onChange={(e) => setAddText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") void onAddClue();
                }}
                placeholder="e.g. my family was there"
                maxLength={200}
              />
              <button className="btn ghost" onClick={onAddClue} disabled={busy || !addText.trim()}>
                Add
              </button>
            </div>
          </div>
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
          <Breadcrumb
            heard={heard}
            chips={chips}
            onRemove={onRemoveChip}
            onAdd={() => setStage("recap")}
          />
          {(result.conflicts ?? []).map((c) => (
            <p key={c.episode} className="t-support recovery-note" role="note">
              {conflictNote(c, chips.find((ch) => ch.filter_key === "date_from")?.label)}
            </p>
          ))}
          {recoveryNote && (
            <p className="t-support recovery-note" aria-live="polite">
              {recoveryNote}
              {recoveryUndo && (
                <button className="btn quiet" onClick={onRecoveryUndo}>
                  Undo
                </button>
              )}
            </p>
          )}
          {undo && (
            <p className="t-support undo-row">
              Removed “{undo.chip.label}”.
              <button className="btn quiet" onClick={onUndo}>
                Undo
              </button>
            </p>
          )}
          {seenUndo && (
            <p className="t-support undo-row">
              Added “{seenUndo}”.
              <button className="btn quiet" onClick={onUndoSeen}>
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
            cues={result.cue_suggestions ?? []}
            onOpen={onNoneMatched}
            onNextPage={onNextPage}
            onChange={onChange}
            onEditClues={onEditClues}
            onPickSeen={onPickSeen}
          />
        </>
      )}

      {stage === "recover" && (
        <>
          <Breadcrumb heard={heard} chips={chips} />
          <Recover moment={rejectedSeq?.episode ?? ""} onPick={onRecover} />
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

      {stage === "confirmed" && revisit && confirmedSeq && (
        <>
          <Breadcrumb heard={heard} chips={chips} />
          <EpisodeView
            sequence={confirmedSeq}
            startAt={confirmedId ?? undefined}
            onAssetOpened={(id) => track("asset_opened", { photo_id: id })}
          />
          <div className="actions">
            <button className="btn ghost" onClick={() => setRevisit(false)}>
              Back to your photo
            </button>
          </div>
        </>
      )}

      {stage === "confirmed" && !revisit && (
        <section className="panel found" aria-labelledby="found-h">
          <h2 id="found-h" className="t-section done">
            You found the moment.
          </h2>
          <p>You confirmed this is the photo you remembered.</p>
          {confirmedFile && (
            <button
              className="confirmed-open"
              onClick={() => {
                track("confirmed_photo_opened", { photo_id: confirmedId });
                setZoom(true);
              }}
              aria-label="Open photo"
            >
              <img className="confirmed-media" src={`/${confirmedFile}`} alt="The photo you confirmed" />
            </button>
          )}
          <div className="actions found-actions">
            <button
              className="btn primary"
              onClick={() => {
                track("confirmed_photo_opened", { photo_id: confirmedId });
                setZoom(true);
              }}
            >
              Open photo
            </button>
            {confirmedSeq && (
              <button
                className="btn ghost"
                onClick={() => {
                  track("confirmed_moment_viewed", { episode_id: confirmedSeq.episode_id });
                  setRevisit(true);
                }}
              >
                View the surrounding moment
              </button>
            )}
            <button className="btn ghost" onClick={closeTrails}>
              Done
            </button>
          </div>
          <p className="t-support">
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
                      track("memory_question_answered", { helped: a });
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
          <button className="btn quiet" onClick={restart}>
            Find another memory
          </button>
        </section>
      )}

      {zoom && confirmedFile && (
        <div className="outside-modal-backdrop" onClick={() => setZoom(false)}>
          <div
            className="outside-modal-dialog"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Your photo"
          >
            <div className="outside-modal-head">
              <h2 className="t-section">Your photo</h2>
              <button className="icon-btn" onClick={() => setZoom(false)} aria-label="Close">
                ✕
              </button>
            </div>
            <figure className="outside-modal-hero">
              <img src={`/${confirmedFile}`} alt="The photo you confirmed" />
            </figure>
          </div>
        </div>
      )}

      {stage === "empty" && !error && (
        <>
          <TimeRibbon
            chapters={monthlyChapters}
            activeDateFrom={filters.date_from}
            activeDateTo={filters.date_to}
            onShift={onShiftTime}
          />
          {seenUndo && (
            <p className="t-support undo-row">
              Added “{seenUndo}”.
              <button className="btn quiet" onClick={onUndoSeen}>
                Undo
              </button>
            </p>
          )}
          <NoMatch
            filters={filters}
            cues={result?.cue_suggestions ?? []}
            onChange={onChange}
            onExit={closeTrails}
            onPickSeen={onPickSeen}
          />
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

function withoutKey(f: Filters, key: string): Filters {
  const next = { ...f };
  delete next[key];
  if (key === "date_from") delete next.date_to;
  return next;
}

/** "Photos from “goa trip” are dated Dec 2023, not pichle saal." plus what is actually on
 *  screen. The event is quoted as a name, so every episode reads grammatically. */
function conflictNote(c: Conflict, said?: string): string {
  const when = said ?? "the time you gave";
  const head = `Photos from “${c.episode}” are dated ${formatMonths(c.episode_dates[0], c.episode_dates[1])}, not ${when}.`;
  if (c.shown_episode && c.shown_window) return `${head} Showing moments from both.`;
  if (c.shown_episode) return `${head} Showing that moment; nothing from ${when} matched as closely.`;
  if (c.shown_window) return `${head} Showing moments from ${when}.`;
  return head;
}
