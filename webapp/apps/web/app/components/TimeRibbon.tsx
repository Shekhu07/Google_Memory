"use client";

import type { MonthlyChapter } from "@/lib/api";

export function TimeRibbon({
  chapters,
  activeDateFrom,
  activeDateTo,
  onShift,
}: {
  chapters: MonthlyChapter[];
  activeDateFrom?: string | null;
  activeDateTo?: string | null;
  onShift: (chapter: MonthlyChapter, direction: "earlier" | "later" | "chapter") => void;
}) {
  if (!chapters || chapters.length === 0) return null;

  // Determine active index based on activeDateFrom or month matching
  let activeIndex = -1;
  if (activeDateFrom) {
    const activeMonth = activeDateFrom.slice(0, 7);
    activeIndex = chapters.findIndex((c) => c.month === activeMonth);
  }

  const prevChapter = activeIndex > 0 ? chapters[activeIndex - 1] : null;
  const nextChapter = activeIndex >= 0 && activeIndex < chapters.length - 1 ? chapters[activeIndex + 1] : null;

  return (
    <div className="time-ribbon" aria-label="Show me around that time ribbon">
      <div className="ribbon-header">
        <div className="ribbon-title-wrap">
          <p className="t-eyebrow">Around that time</p>
          <p className="t-support">Shift to nearby months to explore surrounding moments</p>
        </div>
        <div className="ribbon-nav">
          <button
            type="button"
            className="btn quiet ribbon-step-btn"
            disabled={!prevChapter}
            onClick={() => prevChapter && onShift(prevChapter, "earlier")}
            aria-label={prevChapter ? `Shift earlier to ${prevChapter.label}` : "No earlier chapter"}
          >
            ← Earlier
          </button>
          <button
            type="button"
            className="btn quiet ribbon-step-btn"
            disabled={!nextChapter}
            onClick={() => nextChapter && onShift(nextChapter, "later")}
            aria-label={nextChapter ? `Shift later to ${nextChapter.label}` : "No later chapter"}
          >
            Later →
          </button>
        </div>
      </div>

      <div className="ribbon-scroll" role="list">
        {chapters.map((ch, idx) => {
          const isActive = idx === activeIndex;
          return (
            <button
              key={ch.month}
              type="button"
              className={`chapter-card ${isActive ? "active" : ""}`}
              onClick={() => onShift(ch, "chapter")}
              aria-pressed={isActive}
              aria-label={`${ch.label}, ${ch.count} photos`}
            >
              <div className="chapter-thumb-wrap">
                <img
                  src={`/${ch.thumbnail}`}
                  alt={ch.label}
                  className="chapter-thumb"
                  loading="lazy"
                />
                {isActive && <span className="chapter-active-badge">Active</span>}
              </div>
              <div className="chapter-info">
                <span className="chapter-name">{ch.label}</span>
                <span className="chapter-count">{ch.count} photos</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
