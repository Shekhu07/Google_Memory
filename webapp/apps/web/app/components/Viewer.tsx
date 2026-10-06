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
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [toast, setToast] = useState<string | null>(null);
  const [filterMode, setFilterMode] = useState<"normal" | "vivid" | "mono">("normal");
  const p = photos[i];
  const pushed = useRef(false);
  const drag = useRef<{ x: number; y: number } | null>(null);
  const [zoomScale, setZoomScale] = useState(1);
  const touchDist = useRef<number | null>(null);

  useEffect(() => {
    setZoomScale(1);
  }, [i]);

  const prev = () => setI((n) => Math.max(0, n - 1));
  const next = () => setI((n) => Math.min(photos.length - 1, n + 1));

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(null), 2200);
  }

  function toggleFavorite() {
    if (!p) return;
    setFavorites((prev) => {
      const nextSet = new Set(prev);
      if (nextSet.has(p.f)) {
        nextSet.delete(p.f);
        showToast("Removed from Favorites");
      } else {
        nextSet.add(p.f);
        showToast("Added to Favorites ★");
      }
      return nextSet;
    });
  }

  async function handleShare() {
    if (!p) return;
    const url = typeof window !== "undefined" ? window.location.href : "";
    if (navigator.share) {
      try {
        await navigator.share({
          title: p.t || "Photo from Memory Trails",
          text: `${p.t ? `“${p.t}”` : "Photo"} · ${fullDate(p.d)}`,
          url,
        });
        return;
      } catch {
        // user cancelled or share failed, fallback to copy
      }
    }
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(window.location.origin + "/" + p.f);
      showToast("Photo link copied to clipboard");
    }
  }

  function cycleFilter() {
    setFilterMode((curr) => {
      if (curr === "normal") { showToast("Style: Vivid"); return "vivid"; }
      if (curr === "vivid") { showToast("Style: Monochromatic"); return "mono"; }
      showToast("Style: Original");
      return "normal";
    });
  }

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
      else if (e.key === "f") toggleFavorite();
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  });

  // Neighbours decode ahead of the swipe, so the next photo is already there.
  const around = [photos[i - 1], photos[i + 1]].filter(Boolean) as GalleryPhoto[];

  if (!p) return null;
  const isFav = favorites.has(p.f);

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
        if (!s || zoomScale > 1.1) return;
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

      {toast && (
        <div className="viewer-toast" role="status" aria-live="polite">
          {toast}
        </div>
      )}

      <div
        className={`viewer-stage${info ? " with-info" : ""}`}
        onTouchStart={(e) => {
          if (e.touches.length === 2) {
            touchDist.current = Math.hypot(
              e.touches[0].clientX - e.touches[1].clientX,
              e.touches[0].clientY - e.touches[1].clientY
            );
          }
        }}
        onTouchMove={(e) => {
          if (e.touches.length === 2 && touchDist.current !== null) {
            const dist = Math.hypot(
              e.touches[0].clientX - e.touches[1].clientX,
              e.touches[0].clientY - e.touches[1].clientY
            );
            const factor = dist / touchDist.current;
            setZoomScale((scale) => Math.min(3, Math.max(1, scale * factor)));
            touchDist.current = dist;
          }
        }}
        onTouchEnd={(e) => {
          if (e.touches.length < 2) {
            touchDist.current = null;
          }
        }}
      >
        {/* The title is the creator's, and often says what is in the frame. */}
        <img
          key={p.f}
          src={`/${p.f}`}
          alt={p.t}
          draggable={false}
          onDoubleClick={() => setZoomScale((s) => (s > 1.2 ? 1 : 2))}
          className={`viewer-img ${filterMode !== "normal" ? `filter-${filterMode}` : ""}`}
          style={{
            transform: `scale(${zoomScale})`,
            transformOrigin: "center center",
            transition: zoomScale === 1 ? "transform 0.2s ease" : "none",
          }}
        />
        {i > 0 && (
          <button className="viewer-nav prev" onClick={prev} aria-label="Previous photo">‹</button>
        )}
        {i < photos.length - 1 && (
          <button className="viewer-nav next" onClick={next} aria-label="Next photo">›</button>
        )}
      </div>

      {/* Native-feeling mobile bottom action toolbar */}
      <footer className="viewer-bottom-bar" aria-label="Photo actions">
        <button className="viewer-action-btn" onClick={handleShare} aria-label="Share photo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
            <circle cx="18" cy="5" r="3" />
            <circle cx="6" cy="12" r="3" />
            <circle cx="18" cy="19" r="3" />
            <path d="M8.6 13.5l6.8 3.9M15.4 6.6l-6.8 3.9" />
          </svg>
          <span>Share</span>
        </button>
        <button className="viewer-action-btn" onClick={cycleFilter} aria-label="Tune photo style">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
            <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
            <circle cx="8" cy="6" r="2" fill="currentColor" />
            <circle cx="16" cy="12" r="2" fill="currentColor" />
            <circle cx="10" cy="18" r="2" fill="currentColor" />
          </svg>
          <span>Edit</span>
        </button>
        <button
          className={`viewer-action-btn ${isFav ? "active" : ""}`}
          onClick={toggleFavorite}
          aria-label={isFav ? "Remove from favorites" : "Add to favorites"}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill={isFav ? "#FBBC04" : "none"} stroke={isFav ? "#FBBC04" : "currentColor"} strokeWidth="1.9">
            <path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2-4.5-4.4 6.2-.9z" strokeLinejoin="round" />
          </svg>
          <span>Favorite</span>
        </button>
        <button
          className="viewer-action-btn"
          onClick={() => setInfo((v) => !v)}
          aria-label="Photo details"
          aria-expanded={info}
        >
          <InfoGlyph />
          <span>Details</span>
        </button>
      </footer>

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
