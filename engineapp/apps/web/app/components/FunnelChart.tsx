"use client";

import { useState } from "react";

type Stage = {
  name: string;
  count: number;
  pctOfTotal: string;
  dropoff: string;
  description: string;
  breakdown?: { label: string; count: number; share: string }[];
};

const STAGES: Stage[] = [
  {
    name: "1. Raw Collection",
    count: 85140,
    pctOfTotal: "100%",
    dropoff: "93.8% non-retrieval posts",
    description: "Public reviews, comments, and threads gathered from 4 sources.",
    breakdown: [
      { label: "Play Store", count: 81256, share: "95.4%" },
      { label: "App Store", count: 2732, share: "3.2%" },
      { label: "YouTube", count: 696, share: "0.8%" },
      { label: "Reddit", count: 456, share: "0.5%" },
    ],
  },
  {
    name: "2. Keyword Screen (Gate A)",
    count: 5305,
    pctOfTotal: "6.2%",
    dropoff: "74.9% irrelevant/general bugs",
    description: "Free regex filter matching search, memory, find, missing, date, or retrieval keywords.",
    breakdown: [
      { label: "Play Store", count: 4939, share: "93.1%" },
      { label: "App Store", count: 202, share: "3.8%" },
      { label: "Reddit", count: 134, share: "2.5%" },
      { label: "YouTube", count: 30, share: "0.6%" },
    ],
  },
  {
    name: "3. Relevance Screen (Gate B)",
    count: 819,
    pctOfTotal: "0.96%",
    dropoff: "12.1% unscoreable",
    description: "Binary classifier screening for genuine attempts to find past photos vs generic crashes.",
    breakdown: [
      { label: "Play Store", count: 637, share: "77.8%" },
      { label: "App Store", count: 110, share: "13.4%" },
      { label: "Reddit", count: 62, share: "7.6%" },
      { label: "YouTube", count: 10, share: "1.2%" },
    ],
  },
  {
    name: "4. Structured Extraction",
    count: 720,
    pctOfTotal: "0.85%",
    dropoff: "80.0% general complaints",
    description: "Fixed schema extraction requiring exact quote validation from the original text.",
    breakdown: [
      { label: "Play Store", count: 621, share: "86.2%" },
      { label: "Reddit", count: 62, share: "8.6%" },
      { label: "App Store", count: 36, share: "5.0%" },
      { label: "YouTube", count: 1, share: "0.1%" },
    ],
  },
  {
    name: "5. Specific Attempts",
    count: 144,
    pctOfTotal: "0.17%",
    dropoff: "Final analyzed cohort",
    description: "Concrete user retrieval episodes with identifiable cues, search modes, and verified outcomes.",
    breakdown: [
      { label: "Play Store", count: 123, share: "85.4%" },
      { label: "Reddit", count: 12, share: "8.3%" },
      { label: "App Store", count: 8, share: "5.6%" },
      { label: "YouTube", count: 1, share: "0.7%" },
    ],
  },
];

export function FunnelChart() {
  const [selectedIdx, setSelectedIdx] = useState<number>(4);
  const current = STAGES[selectedIdx];

  return (
    <div className="funnel-container">
      <div className="funnel-header">
        <h3 className="t-section">Evidence Ingestion Funnel</h3>
        <p className="t-support">
          Click any stage to inspect platform breakdown and drop-off filtering
        </p>
      </div>

      <div className="funnel-steps" role="list">
        {STAGES.map((s, idx) => {
          const isSelected = idx === selectedIdx;
          const maxCount = STAGES[0].count;
          const widthPct = Math.max(16, (s.count / maxCount) * 100);

          return (
            <button
              key={s.name}
              type="button"
              className={`funnel-bar-wrap ${isSelected ? "active" : ""}`}
              onClick={() => setSelectedIdx(idx)}
              aria-pressed={isSelected}
            >
              <div className="funnel-label-row">
                <span className="funnel-stage-name">{s.name}</span>
                <span className="funnel-stage-count">{s.count.toLocaleString()} posts</span>
              </div>
              <div className="funnel-bar-track">
                <div
                  className={`funnel-bar-fill stage-${idx}`}
                  style={{ width: `${widthPct}%` }}
                />
              </div>
            </button>
          );
        })}
      </div>

      {current && (
        <div className="funnel-detail-panel">
          <div className="detail-meta-row">
            <div>
              <h4 className="detail-title">{current.name}</h4>
              <p className="detail-desc">{current.description}</p>
            </div>
            <div className="detail-stat">
              <span className="detail-big-num">{current.count.toLocaleString()}</span>
              <span className="detail-pct">{current.pctOfTotal} of total</span>
            </div>
          </div>

          {current.breakdown && (
            <div className="detail-breakdown-grid">
              {current.breakdown.map((b) => (
                <div key={b.label} className="breakdown-card">
                  <span className="breakdown-platform">{b.label}</span>
                  <span className="breakdown-count">{b.count.toLocaleString()}</span>
                  <span className="breakdown-share">{b.share}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
