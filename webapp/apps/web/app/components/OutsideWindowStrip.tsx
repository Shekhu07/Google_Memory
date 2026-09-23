"use client";

import { formatWindow, type OutsidePhoto } from "@/lib/api";

export function OutsideWindowStrip({
  photos,
  onOpenPhoto,
}: {
  photos: OutsidePhoto[];
  onOpenPhoto: (photo: OutsidePhoto) => void;
}) {
  if (!photos || photos.length === 0) return null;

  return (
    <section className="outside-window-strip" aria-label="Photos just outside your date window">
      <div className="outside-header">
        <h3 className="t-section">Just outside your dates</h3>
        <p className="t-support">Same clues, a little outside your dates</p>
      </div>
      <div className="outside-rail" role="group" aria-label="Photos outside date window">
        {photos.slice(0, 5).map((p) => {
          const sign = p.offset_days > 0 ? `+${p.offset_days}d` : `${p.offset_days}d`;
          const signFull = p.offset_days > 0 ? `+${p.offset_days} days` : `${p.offset_days} days`;
          const dateStr = formatWindow(p.date, p.date);
          return (
            <button
              key={p.id}
              className="outside-card"
              onClick={() => onOpenPhoto(p)}
              aria-label={`Photo from ${dateStr}, ${signFull}`}
            >
              <div className="outside-thumb-wrap">
                <img src={`/${p.file}`} alt="" loading="lazy" />
                <span className="outside-badge">{sign}</span>
              </div>
              <div className="outside-info">
                <span className="outside-date">{dateStr}</span>
                {p.location && <span className="outside-loc">{p.location}</span>}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
