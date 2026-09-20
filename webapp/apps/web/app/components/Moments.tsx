"use client";

import { useState } from "react";
import { formatWindow, type Episode, type Reason } from "@/lib/api";

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
  if (ep.count < ep.episode_total) parts.push(`${ep.count} match your clues`);
  return parts.join(" · ");
}

function Evidence({ ep }: { ep: Episode }) {
  const [open, setOpen] = useState(false);
  if (ep.why.length === 0) return null;
  return (
    <>
      <p className="t-eyebrow why-label">Why this moment?</p>
      <p className="evidence">{evidenceLine(ep)}</p>
      {ep.evidence.length > 0 && (
        <>
          <button className="btn quiet see" aria-expanded={open} onClick={() => setOpen(!open)}>
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
