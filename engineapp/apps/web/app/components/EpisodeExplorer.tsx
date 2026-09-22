"use client";

import { useMemo, useState } from "react";
import episodesData from "@/public/data/episodes_specific.json";

type Episode = {
  id: string;
  source: string;
  date: string;
  asset_type: string;
  failure_stage: string;
  workaround: string;
  outcome: string;
  cues_retained: string[];
  cues_lost: string[];
  hypotheses: string[];
  evidence: string;
  confidence: number;
};

const ALL_EPISODES: Episode[] = episodesData as Episode[];

const PLATFORMS = [
  { id: "all", label: "All Sources" },
  { id: "playstore", label: "Play Store (123)" },
  { id: "reddit", label: "Reddit (12)" },
  { id: "appstore", label: "App Store (8)" },
  { id: "youtube", label: "YouTube (1)" },
];

const STAGES = [
  { id: "all", label: "All Stages" },
  { id: "not_surfaced", label: "Not surfaced (60)" },
  { id: "system_misunderstood", label: "System misunderstood (51)" },
  { id: "browse_path_changed", label: "Browse path changed (12)" },
  { id: "cannot_evaluate_results", label: "Cannot evaluate (2)" },
  { id: "slow_or_broken_ui", label: "Slow / broken UI (2)" },
  { id: "cannot_express", label: "Cannot express (2)" },
  { id: "cannot_refine", label: "Cannot refine (1)" },
  { id: "none", label: "Retrieved (14)" },
];

export function EpisodeExplorer() {
  const [platform, setPlatform] = useState<string>("all");
  const [stage, setStage] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null);

  const filtered = useMemo(() => {
    return ALL_EPISODES.filter((ep) => {
      if (platform !== "all" && ep.source !== platform) return false;
      if (stage !== "all" && ep.failure_stage !== stage) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesEvidence = ep.evidence.toLowerCase().includes(q);
        const matchesCues = ep.cues_retained.some((c) => c.toLowerCase().includes(q));
        const matchesLost = ep.cues_lost.some((c) => c.toLowerCase().includes(q));
        if (!matchesEvidence && !matchesCues && !matchesLost) return false;
      }
      return true;
    });
  }, [platform, stage, searchQuery]);

  return (
    <div className="episode-explorer">
      <div className="explorer-header">
        <div>
          <h3 className="t-section">Real Episode Telemetry Explorer</h3>
          <p className="t-support">
            Browse and filter the 144 specific photo retrieval failures extracted from public posts.
          </p>
        </div>
        <div className="explorer-count-badge">
          {filtered.length} of {ALL_EPISODES.length} attempts
        </div>
      </div>

      {/* Filters Bar */}
      <div className="explorer-filters">
        <div className="filter-group">
          <label className="filter-label">Source Platform</label>
          <div className="filter-pills" role="radiogroup">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                type="button"
                className={`pill-btn ${platform === p.id ? "active" : ""}`}
                onClick={() => setPlatform(p.id)}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <div className="filter-group">
          <label className="filter-label">Failure Stage</label>
          <div className="filter-pills" role="radiogroup">
            {STAGES.map((s) => (
              <button
                key={s.id}
                type="button"
                className={`pill-btn ${stage === s.id ? "active" : ""}`}
                onClick={() => setStage(s.id)}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        <div className="filter-search-wrap">
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search evidence quotes (e.g. 'recent photo', 'medicine', 'vacation', 'date')..."
            className="explorer-search-input"
            aria-label="Search real user episodes"
          />
        </div>
      </div>

      {/* Episodes Grid */}
      <div className="episodes-grid" role="list">
        {filtered.length === 0 ? (
          <div className="no-episodes-msg">
            <p className="t-section">No episodes match that filter</p>
            <p className="t-support">Try clearing your search or switching failure stages.</p>
          </div>
        ) : (
          filtered.map((ep) => (
            <article
              key={ep.id}
              className={`episode-card stage-border-${ep.failure_stage}`}
              onClick={() => setSelectedEpisode(ep)}
            >
              <div className="episode-card-meta">
                <div className="meta-left">
                  <span className={`source-tag tag-${ep.source}`}>
                    {ep.source}
                  </span>
                  <span className="episode-date">{ep.date}</span>
                </div>
                <span className={`stage-tag tag-${ep.failure_stage}`}>
                  {ep.failure_stage.replace(/_/g, " ")}
                </span>
              </div>

              <blockquote className="episode-quote">
                “{ep.evidence}”
              </blockquote>

              <div className="episode-tags-row">
                <div className="cue-chips-wrap">
                  <span className="cue-label">Remembered:</span>
                  {ep.cues_retained.length > 0 ? (
                    ep.cues_retained.map((c) => (
                      <span key={c} className="cue-pill retained">
                        {c.replace(/_/g, " ")}
                      </span>
                    ))
                  ) : (
                    <span className="cue-none">none</span>
                  )}
                </div>

                {ep.cues_lost.length > 0 && (
                  <div className="cue-chips-wrap">
                    <span className="cue-label">Forgot:</span>
                    {ep.cues_lost.map((c) => (
                      <span key={c} className="cue-pill lost">
                        {c.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))
        )}
      </div>

      {/* Selected Episode Modal/Drawer */}
      {selectedEpisode && (
        <div className="modal-backdrop" onClick={() => setSelectedEpisode(null)}>
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="modal-header">
              <h3>Episode Analysis</h3>
              <button
                className="btn quiet"
                onClick={() => setSelectedEpisode(null)}
                aria-label="Close dialog"
              >
                ✕ Close
              </button>
            </div>
            <div className="modal-body">
              <div className="modal-meta-row">
                <span className={`source-tag tag-${selectedEpisode.source}`}>
                  {selectedEpisode.source}
                </span>
                <span className={`stage-tag tag-${selectedEpisode.failure_stage}`}>
                  {selectedEpisode.failure_stage.replace(/_/g, " ")}
                </span>
                <span className="t-meta">Asset: {selectedEpisode.asset_type}</span>
              </div>

              <div className="modal-section">
                <label className="t-eyebrow">Verbatim Evidence Quote</label>
                <blockquote className="modal-quote">
                  “{selectedEpisode.evidence}”
                </blockquote>
              </div>

              <div className="modal-grid-2">
                <div className="modal-box">
                  <label className="t-eyebrow">What they remembered</label>
                  <div className="pills-list">
                    {selectedEpisode.cues_retained.map((c) => (
                      <span key={c} className="cue-pill retained">
                        {c.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="modal-box">
                  <label className="t-eyebrow">What they had forgotten</label>
                  <div className="pills-list">
                    {selectedEpisode.cues_lost.length > 0 ? (
                      selectedEpisode.cues_lost.map((c) => (
                        <span key={c} className="cue-pill lost">
                          {c.replace(/_/g, " ")}
                        </span>
                      ))
                    ) : (
                      <span className="t-support">No specific cue loss noted</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="modal-section">
                <label className="t-eyebrow">Supported Hypotheses</label>
                <div className="pills-list">
                  {selectedEpisode.hypotheses.map((h) => (
                    <span key={h} className="hypo-pill">
                      {h}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
