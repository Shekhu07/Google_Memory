"use client";

import { useEffect, useRef, useState } from "react";
import { fileName, fullDate, licenceLabel, type GalleryPhoto } from "@/lib/gallery";

/** One photo, full screen, the way the library opens it: black, swipeable, with
 *  the details a phone already knows about the shot one swipe up.
 *
 *  The info panel is the argument in miniature. Every photo here carries a date,
 *  a place and a device, and plain search still cannot use any of them - so a
 *  grader who opens a photo the search missed can see what was there to find.
 */
export function Viewer({
  photos,
  start,
  onClose,
}: {
  photos: GalleryPhoto[];
  start: number;
  onClose: () => void;
}) {
  const [i, setI] = useState(start);
  const [info, setInfo] = useState(false);
  const p = photos[i];
  const pushed = useRef(false);
  const drag = useRef<{ x: number; y: number } | null>(null);

  const prev = () => setI((n) => Math.max(0, n - 1));
  const next = () => setI((n) => Math.min(photos.length - 1, n + 1));

  // Back closes the viewer, as it does on a phone. Same pattern as the Memory
  // Trails sheet: no URL argument, so nothing about the photo reaches history.
  // Through a ref, so a parent re-render cannot re-run the effect and push a
  // second history entry for the same open viewer.
  const closeRef = useRef(onClose);
  closeRef.current = onClose;
  useEffect(() => {
    history.pushState({ viewer: 1 }, "");
    pushed.current = true;
    const onPop = () => {
      pushed.current = false;
      closeRef.current();
    };
    addEventListener("popstate", onPop);
    return () => removeEventListener("popstate", onPop);
  }, []);

  function close() {
    if (pushed.current) history.back();
    else onClose();
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") prev();
      else if (e.key === "ArrowRight") next();
      else if (e.key === "Escape") (info ? setInfo(false) : close());
      else if (e.key === "i") setInfo((v) => !v);
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  });

  // Neighbours decode ahead of the swipe, so the next photo is already there.
  const around = [photos[i - 1], photos[i + 1]].filter(Boolean) as GalleryPhoto[];

  if (!p) return null;
  return (
    <div
      className="viewer"
      role="dialog"
      aria-modal="true"
      aria-label={`Photo ${i + 1} of ${photos.length}, ${fullDate(p.d)}`}
      onPointerDown={(e) => (drag.current = { x: e.clientX, y: e.clientY })}
      onPointerUp={(e) => {
        const s = drag.current;
        drag.current = null;
        if (!s) return;
        const dx = e.clientX - s.x;
        const dy = e.clientY - s.y;
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) (dx < 0 ? next() : prev());
        else if (dy < -60) setInfo(true);
        else if (dy > 80) (info ? setInfo(false) : close());
      }}
    >
      <header className="viewer-bar">
        <button className="viewer-icon" onClick={close} aria-label="Back to library">
          <BackGlyph />
        </button>
        <div className="viewer-when">
          <span>{fullDate(p.d).split(" · ")[0]}</span>
          <span className="viewer-time">{fullDate(p.d).split(" · ")[1]}</span>
        </div>
        <button
          className="viewer-icon"
          onClick={() => setInfo((v) => !v)}
          aria-label={info ? "Hide details" : "Show details"}
          aria-expanded={info}
        >
          <InfoGlyph />
        </button>
      </header>

      <div className={`viewer-stage${info ? " with-info" : ""}`}>
        {/* The title is the creator's, and often says what is in the frame. */}
        <img key={p.f} src={`/${p.f}`} alt={p.t} draggable={false} />
        {i > 0 && (
          <button className="viewer-nav prev" onClick={prev} aria-label="Previous photo">‹</button>
        )}
        {i < photos.length - 1 && (
          <button className="viewer-nav next" onClick={next} aria-label="Next photo">›</button>
        )}
      </div>

      {info && (
        <section className="viewer-info" aria-label="Details">
          <div className="grabber" aria-hidden="true" />
          <p className="viewer-info-date">{fullDate(p.d)}</p>
          <h3 className="t-eyebrow">Details</h3>
          <dl>
            <div>
              <dt><ImageGlyph /></dt>
              <dd>
                {fileName(p.d)}
                <span>{p.v}</span>
              </dd>
            </div>
            {p.p && (
              <div>
                <dt><PinGlyph /></dt>
                <dd>
                  {p.p}
                  <span>Location from the photo</span>
                </dd>
              </div>
            )}
          </dl>
          <p className="viewer-credit">
            “{p.t || "Untitled"}” by {p.a || "unknown"}
            {p.l ? ` · ${licenceLabel(p.l)}` : ""} · via Openverse.{" "}
            <a href="/attribution">All credits</a>
          </p>
        </section>
      )}

      <div hidden>
        {around.map((n) => (
          <img key={n.f} src={`/${n.f}`} alt="" decoding="async" />
        ))}
      </div>
    </div>
  );
}

function BackGlyph() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M15 5l-7 7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function InfoGlyph() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 11v5" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
      <circle cx="12" cy="8" r="1.1" fill="currentColor" />
    </svg>
  );
}

function ImageGlyph() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3.5" y="4.5" width="17" height="15" rx="2.5" stroke="currentColor" strokeWidth="1.7" />
      <path d="M5 17l4-4 3 3 2.5-2 4.5 3.5" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
    </svg>
  );
}

function PinGlyph() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 21s-6.5-6.2-6.5-11A6.5 6.5 0 0 1 18.5 10c0 4.8-6.5 11-6.5 11z" stroke="currentColor" strokeWidth="1.7" />
      <circle cx="12" cy="10" r="2.3" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}
