"use client";

import { useState } from "react";
import { formatMonths, formatWindow, type Episode, type LedgerEntry, type Reason } from "@/lib/api";
import { track } from "@/lib/track";

/** Three to five candidates, each scannable in under three seconds. */
export const MAX_CANDIDATES = 5;

/**
 * Noun phrases built only from what matched: "the sister's graduation event",
 * "cake-like images", "photos around 14–15 Jun 2025". Never a narrative, never a
 * confidence score.
 */
export function phrase(r: Reason): string {
  if (r.kind === "date_window") return `photos around ${formatWindow(r.value, r.to)}`;
  if (r.kind === "location") return `photos taken in ${r.value}`;
  if (r.kind === "category") return `${CATEGORY_WORDS[r.value] ?? r.value}-like images`;
  return `the ${r.value} event`;
}

/** "Matches the sister's graduation event, cake-like images and photos around …". */
function evidenceLine(ep: Episode): string {
  const parts = ep.why.map(phrase);
  if (parts.length === 0) return "";
  const list = parts.length === 1 ? parts[0] : `${parts.slice(0, -1).join(", ")} and ${parts[parts.length - 1]}`;
  return `Matches ${list}.`;
}

const SCOPE_WORDS: Record<string, string> = {
  direct: "in the first photo",
  nearby: "in nearby photos",
  approximate: "approximate",
};

/** "around Jun 2025" for a moment inside one month, "Jun – Jul 2025" across two. */
function around(from: string | null, to: string | null): string {
  if (!from) return "";
  const months = formatMonths(from, to);
  return from.slice(0, 7) === (to ?? from).slice(0, 7) ? `around ${months}` : months;
}

function titleCase(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** Density cues, so an episode reads as a real moment without being opened. */
function sequenceNote(ep: Episode): string {
  const parts = [`${ep.episode_total} photo${ep.episode_total === 1 ? "" : "s"}`];
  if (ep.places > 1) parts.push(`${ep.places} places`);
  for (const [name, n] of ep.scenes.slice(0, 2)) {
    if (n > 1) parts.push(`${n} ${name} scenes`);
  }
  if (ep.clue_hits !== undefined && ep.clue_hits > 0) {
    parts.push(`${ep.clue_hits} match all your clues`);
  } else if (ep.count < ep.episode_total && ep.count > 0 && ep.clue_hits === undefined) {
    parts.push(`${ep.count} match your clues`);
  }
  return parts.join(" · ");
}

const CATEGORY_WORDS: Record<string, string> = {
  cafe: "café", medicine: "medicine", notes: "handwritten note", pet: "pet", boxes: "moving box",
};

function renderLedger(ledger?: LedgerEntry[]) {
  if (!ledger || ledger.length === 0) return null;
  const items = ledger.map((entry) => {
    if (entry.kind === "date_window") {
      if (entry.matched) return { text: "date ✓", matched: true };
      const off = entry.offset_days;
      if (off === null || off === undefined) return { text: "date unknown", matched: false };
      const offText = off > 0 ? `+${off} days` : `${Math.abs(off)} days earlier`;
      return { text: `date ${offText}`, matched: false };
    }
    const label = entry.kind === "category" ? CATEGORY_WORDS[entry.value] ?? entry.value : entry.value;
    return entry.matched ? { text: `${label} ✓`, matched: true } : { text: `not ${label}`, matched: false };
  });

  return (
    <div className="ledger-row" aria-label="Match ledger">
      {items.map((it, idx) => (
        <span key={idx} className={`ledger-chip ${it.matched ? "matched" : "unmatched"}`}>
          {it.text}
          {idx < items.length - 1 && <span className="ledger-sep"> · </span>}
        </span>
      ))}
    </div>
  );
}

function Evidence({ ep }: { ep: Episode }) {
  const [open, setOpen] = useState(false);
  if (ep.why.length === 0) return null;

  function onToggle() {
    const next = !open;
    setOpen(next);
    if (next) track("evidence_viewed", { episode_id: ep.episode_id });
  }

  return (
    <div className="why">
      <button className="btn quiet see why-toggle" aria-expanded={open} onClick={onToggle}>
        {open ? "Hide evidence" : "Why this moment?"}
      </button>
      {open && (
        <div className="evidence-body">
          <p className="evidence">{evidenceLine(ep)}</p>
          {ep.evidence.length > 0 && (
            <dl className="evidence-detail">
              {ep.evidence.map((d) => (
                <div key={d.dimension}>
                  <dt>
                    {d.dimension} · {d.dimension === "Scene" ? CATEGORY_WORDS[d.value] ?? d.value : d.value}
                    <span className={`certainty ${d.scope ?? d.certainty}`}>
                      {SCOPE_WORDS[d.scope ?? ""] ?? d.certainty}
                    </span>
                  </dt>
                  <dd>{d.source}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      )}
    </div>
  );
}

export function Moments({
  episodes,
  onOpen,
  start = 0,
}: {
  episodes: Episode[];
  onOpen: (ep: Episode) => void;
  /** First moment to show; "Not in any of these?" pages forward in fives. */
  start?: number;
}) {
  return (
    <ul className="moments">
      {episodes.slice(start, start + MAX_CANDIDATES).map((ep, i) => {
        const named = Boolean(ep.episode_id);
        const when = formatWindow(ep.date_from, ep.date_to);
        // A moment reads as an event first ("Sister's graduation · around Jun 2025");
        // loose photos keep place and date, since they have no event to name.
        const title = named
          ? [titleCase(ep.episode), around(ep.date_from, ep.date_to)].filter(Boolean).join(" · ")
          : [ep.location, when].filter(Boolean).join(" · ") || ep.episode;
        const displayPhotos = ep.photos.slice(0, 6);
        const remainingCount = ep.photos.length - 6;

        return (
          <li
            key={ep.episode_id || ep.photos[0]?.id}
            className={i === 0 && start === 0 && named ? "episode strongest" : "episode"}
          >
            <div className="head">
              <h3 className="t-section">{title}</h3>
              <span className="t-meta">{sequenceNote(ep)}</span>
            </div>

            {/* Pictures-first contact sheet */}
            <div
              className="moment-contact-sheet"
              role="group"
              aria-label={`Photos from ${ep.episode}`}
              onClick={() => named && onOpen(ep)}
            >
              {displayPhotos.map((p, n) => {
                const isLast = n === 5 && remainingCount > 0;
                return (
                  <div key={p.id} className="contact-cell">
                    <img
                      src={`/${p.file}`}
                      alt={`${ep.episode}, photo ${n + 1} of ${ep.photos.length}${when ? `, ${when}` : ""}`}
                      loading="lazy"
                    />
                    {isLast && (
                      <span className="contact-more">+{remainingCount}</span>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Compact meta line underneath: place, date, match ledger */}
            <div className="moment-meta-line">
              <span className="meta-loc-date">
                {[ep.location, when || around(ep.date_from, ep.date_to)].filter(Boolean).join(" · ")}
              </span>
              {renderLedger(ep.ledger)}
            </div>

            <Evidence ep={ep} />

            {named && (
              <div className="foot">
                <button className="btn ghost" onClick={() => onOpen(ep)}>
                  Open moment
                </button>
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
