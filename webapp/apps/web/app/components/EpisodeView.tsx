"use client";

import { useState } from "react";
import { formatWindow, type EpisodeSequence } from "@/lib/api";

/**
 * Screen 4. The user re-enters the surrounding moment and scrubs it.
 * Nothing is auto-confirmed: the first photo is selected, not accepted.
 */
export function EpisodeView({
  sequence,
  onConfirm,
  onReject,
  onBack,
  onAssetOpened,
}: {
  sequence: EpisodeSequence;
  onConfirm: (photoId: string) => void;
  onReject: () => void;
  onBack: () => void;
  onAssetOpened: (photoId: string) => void;
}) {
  const [index, setIndex] = useState(0);
  const photo = sequence.photos[index];
  const days = Array.from(new Set(sequence.photos.map((p) => p.date).filter(Boolean)));

  function select(i: number) {
    setIndex(i);
    const next = sequence.photos[i];
    if (next) onAssetOpened(next.id);
  }

  return (
    <section className="episode-view">
      <button className="linkish" onClick={onBack}>
        ← Back to moments
      </button>
      <h2>{sequence.episode || "Photos"}</h2>
      <p className="when">
        {[sequence.location, `${sequence.count} photo${sequence.count === 1 ? "" : "s"}`]
          .filter(Boolean)
          .join(" · ")}
        {days.length > 0 && ` · ${formatWindow(days[0], days[days.length - 1])}`}
      </p>

      {photo && (
        <figure className="selected">
          <img src={`/${photo.file}`} alt={`Photo taken ${photo.date} in ${photo.location}`} />
          <figcaption>
            {formatWindow(photo.date, photo.date)}
            {photo.location && ` · ${photo.location}`}
          </figcaption>
        </figure>
      )}

      <div className="scrub" role="group" aria-label="Photos in this moment">
        {sequence.photos.map((p, i) => (
          <button
            key={p.id}
            className={i === index ? "thumb current" : "thumb"}
            aria-current={i === index}
            aria-label={`Photo ${i + 1} of ${sequence.photos.length}, ${p.date}`}
            onClick={() => select(i)}
          >
            <img src={`/${p.file}`} alt="" loading="lazy" />
          </button>
        ))}
      </div>

      <div className="ask-row">
        <button className="primary" onClick={() => photo && onConfirm(photo.id)}>
          That&rsquo;s the one
        </button>
        <button className="secondary" onClick={onReject}>
          Not this moment
        </button>
      </div>
    </section>
  );
}
