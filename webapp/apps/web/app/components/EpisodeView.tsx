"use client";

import { useState } from "react";
import { formatWindow, type EpisodeSequence } from "@/lib/api";

/**
 * Episode title and context, large image, scrubber, then explicit actions.
 * Nothing is auto-confirmed: the user owns the recognition decision.
 */
export function EpisodeView({
  sequence,
  onConfirm,
  onReject,
  onAssetOpened,
  startAt,
}: {
  sequence: EpisodeSequence;
  /** Absent when revisiting a moment after confirming: there is nothing left to decide. */
  onConfirm?: (photoId: string) => void;
  onReject?: () => void;
  onAssetOpened: (photoId: string) => void;
  /** Open on this photo rather than the first. */
  startAt?: string;
}) {
  const [index, setIndex] = useState(() =>
    Math.max(0, startAt ? sequence.photos.findIndex((p) => p.id === startAt) : 0)
  );
  const photo = sequence.photos[index];
  const days = sequence.photos.map((p) => p.date).filter(Boolean);
  const window = days.length ? formatWindow(days[0], days[days.length - 1]) : "";

  function select(i: number) {
    setIndex(i);
    const next = sequence.photos[i];
    if (next) onAssetOpened(next.id);
  }

  return (
    <section aria-label="Episode">
      <h1 className="t-section">
        {sequence.episode ? sequence.episode.charAt(0).toUpperCase() + sequence.episode.slice(1) : "Photos"}
      </h1>
      <p className="t-meta">
        {[window, sequence.location, `${sequence.count} photo${sequence.count === 1 ? "" : "s"}`]
          .filter(Boolean)
          .join(" · ")}
      </p>

      {photo && (
        <figure className="hero">
          <img
            src={`/${photo.file}`}
            alt={`${sequence.episode}, photo ${index + 1} of ${sequence.photos.length}, ${photo.date}${
              photo.location ? ` in ${photo.location}` : ""
            }`}
          />
          <figcaption className="t-support">
            {formatWindow(photo.date, photo.date)}
            {photo.location && ` · ${photo.location}`}
          </figcaption>
        </figure>
      )}

      <div className="scrubber" role="group" aria-label="Photos in this moment">
        {sequence.photos.map((p, i) => (
          <button
            key={p.id}
            className="thumb"
            aria-current={i === index}
            aria-label={`${sequence.episode}, photo ${i + 1} of ${sequence.photos.length}, ${p.date}`}
            onClick={() => select(i)}
          >
            <img src={`/${p.file}`} alt="" loading="lazy" />
          </button>
        ))}
      </div>

      <p aria-live="polite" className="visually-hidden">
        Photo {index + 1} of {sequence.photos.length} selected.
      </p>

      {onConfirm && onReject && (
        <div className="actions">
          <button className="btn primary" onClick={() => photo && onConfirm(photo.id)}>
            That&rsquo;s the one
          </button>
          <button className="btn ghost" onClick={onReject}>
            Not this moment
          </button>
        </div>
      )}
    </section>
  );
}
