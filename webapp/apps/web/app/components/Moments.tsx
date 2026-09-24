"use client";

import { useState } from "react";
import { formatWindow, type Episode, type LedgerEntry, type Reason } from "@/lib/api";
import { track } from "@/lib/track";

/** Three to five candidates, each scannable in under three seconds. */
export const MAX_CANDIDATES = 5;

/**
 * Noun phrases, per the spec's evidence examples: "Goa location",
 * "café-like scenes", "Photos grouped around 8–11 Dec 2023".
 * Never a narrative, never a confidence score.
 */
export function phrase(r: Reason): string {
  if (r.kind === "date_window") return `Photos grouped around ${formatWindow(r.value, r.to)}`;
  if (r.kind === "location") return `${r.value} location`;
  if (r.kind === "category") return `${r.value}-like scenes`;
  return "Nearby sequence";
}

function evidenceLine(ep: Episode): string {
  return ep.why.map(phrase).join(" · ");
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

const CATEGORY_WORDS: Record<string, string> = { cafe: "café", medicine: "medicine" };

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
    if (next) {
      track("ledger_viewed", {
        episode_id: ep.episode_id,
        episode: ep.episode,
      });
    }
  }

  return (
    <>
      <p className="t-eyebrow why-label">Why this moment?</p>
      <p className="evidence">{evidenceLine(ep)}</p>
      {ep.evidence.length > 0 && (
        <>
          <button className="btn quiet see" aria-expanded={open} onClick={onToggle}>
            {open ? "Hide evidence" : "See evidence"}
          </button>
          {open && (
            <dl className="evidence-detail">
              {ep.evidence.map((d) => (
                <div key={d.dimension}>
                  <dt>
                    {d.dimension} · {d.value}
                    <span className={`certainty ${d.certainty}`}>{d.certainty}</span>
                  </dt>
                  <dd>{d.source}</dd>
                </div>
              ))}
            </dl>
          )}
        </>
      )}
    </>
  );
}

export function Moments({
  episodes,
  onOpen,
}: {
  episodes: Episode[];
  onOpen: (ep: Episode) => void;
}) {
  return (
    <ul className="moments">
      {episodes.slice(0, MAX_CANDIDATES).map((ep, i) => {
        const named = Boolean(ep.episode_id);
        const when = formatWindow(ep.date_from, ep.date_to);
        const title = [ep.location, when].filter(Boolean).join(" · ") || ep.episode;
        return (
          <li
            key={ep.episode_id || ep.photos[0]?.id}
            className={i === 0 && named ? "episode strongest" : "episode"}
          >
            <div className="head">
              <h3 className="t-section">{title}</h3>
              <span className="t-meta">{sequenceNote(ep)}</span>
            </div>
            {named && <p className="t-support subtitle">{ep.episode}</p>}

            {renderLedger(ep.ledger)}

            <div className="rail-imgs" role="group" aria-label={`Photos from ${ep.episode}`}>
              {ep.photos.slice(0, 4).map((p, n) => (
                <img
                  key={p.id}
                  src={`/${p.file}`}
                  alt={`${ep.episode}, photo ${n + 1} of ${ep.photos.length}${when ? `, ${when}` : ""}`}
                  loading="lazy"
                />
              ))}
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
