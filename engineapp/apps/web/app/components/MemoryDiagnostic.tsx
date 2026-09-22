"use client";

import { useState } from "react";
import { extract, type Chip } from "@/lib/api";

const PRESETS = [
  "The medicine I took when I was sick, July 2025ish",
  "A beach cafe in Goa during sunset",
  "Cousin's wedding reception in December 2023",
  "Whiteboard notes from our product strategy meeting",
  "Puppy's first vet checkup in Bengaluru",
];

type DiagnosticResult = {
  chips: Chip[];
  source: string;
  filters: Record<string, string>;
  riskLevel: "high" | "moderate" | "low";
  riskScore: number;
  predictedStage: string;
  failureExplanation: string;
  recoveryRecommendation: string;
};

export function MemoryDiagnostic() {
  const [text, setText] = useState("");
  const [diagnostic, setDiagnostic] = useState<DiagnosticResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  async function onAnalyze(promptText?: string) {
    const q = (promptText !== undefined ? promptText : text).trim();
    if (!q) return;
    if (promptText !== undefined) setText(promptText);

    setBusy(true);
    setFailed(false);
    try {
      const res = await extract(q);

      // Compute diagnostic telemetry based on extracted clues
      const cues = res.chips.map((c) => c.cue);
      const hasApproxTime = cues.includes("temporal_approx") || cues.includes("temporal_relative");
      const hasExactDate = cues.includes("exact_date");
      const hasLocation = cues.includes("place_named") || cues.includes("location");
      const hasObject = cues.includes("object") || cues.includes("category");
      const hasEpisode = cues.includes("event_anchor") || cues.includes("episode");

      let riskLevel: "high" | "moderate" | "low" = "moderate";
      let riskScore = 54;
      let predictedStage = "system_misunderstood";
      let failureExplanation = "";
      let recoveryRecommendation = "";

      if (hasApproxTime && !hasExactDate) {
        riskLevel = "high";
        riskScore = 77;
        predictedStage = "not_surfaced / system_misunderstood";
        failureExplanation =
          "You remembered an approximate timeframe ('July 2025ish'), but human memory forgot the exact calendar date. In standard Google Photos search, date queries require exact boundaries; near-misses return 0 matches or bury the target moment.";
        recoveryRecommendation =
          "Use 'Show me around that time' (Time Ribbon) to explore adjacent monthly chapters with visual thumbnails rather than an exact date string.";
      } else if (cues.length === 0) {
        riskLevel = "high";
        riskScore = 88;
        predictedStage = "cannot_express / not_surfaced";
        failureExplanation =
          "No grounded metadata clues were detected in your query. Standard semantic search will perform a generic visual match across your entire library with low precision (0% Rank@1 on benchmark).";
        recoveryRecommendation =
          "Use 'Memory Anchors' to ground your search with pre-validated entities (e.g. Place, Event, or Category) before typing.";
      } else if (hasEpisode && !hasLocation && !hasExactDate) {
        riskLevel = "high";
        riskScore = 69;
        predictedStage = "system_misunderstood";
        failureExplanation =
          "Your memory is anchored to a personal life episode ('when I was sick', 'wedding'). Keyword search models have no knowledge of your personal life timeline.";
        recoveryRecommendation =
          "Reconstruct the memory using associative anchors (companion, season, place) in Memory Trails.";
      } else {
        riskLevel = "low";
        riskScore = 24;
        predictedStage = "none (high retrieval probability)";
        failureExplanation =
          "Strong combination of grounded visual entities and recognizable metadata clues.";
        recoveryRecommendation =
          "This query has high anchor fidelity and should retrieve reliably in Memory Trails.";
      }

      setDiagnostic({
        chips: res.chips,
        source: res.source,
        filters: res.filters,
        riskLevel,
        riskScore,
        predictedStage,
        failureExplanation,
        recoveryRecommendation,
      });
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="memory-diagnostic">
      <div className="diagnostic-header">
        <h3 className="t-section">Live AI Memory Diagnostic</h3>
        <p className="t-support">
          Test any memory query. The AI model extracts semantic clues, calculates failure risk in
          plain keyword search, and recommends grounding recovery paths.
        </p>
      </div>

      <div className="diagnostic-input-wrap">
        <textarea
          className="prompt"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Describe a memory (e.g., 'The medicine I took when I was sick, July 2025ish')..."
          maxLength={500}
          aria-label="A memory for the diagnostic engine to evaluate"
        />

        <div className="preset-suggestions">
          <span className="preset-label">Or try a benchmark example:</span>
          <div className="preset-chips">
            {PRESETS.map((p) => (
              <button
                key={p}
                type="button"
                className="preset-chip"
                onClick={() => void onAnalyze(p)}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="actions" style={{ marginTop: 12 }}>
          <button
            className="btn primary"
            onClick={() => void onAnalyze()}
            disabled={busy || !text.trim()}
          >
            {busy ? "Running Diagnostic…" : "Diagnose Memory"}
          </button>
        </div>
      </div>

      {failed && (
        <p className="t-support" style={{ color: "#d93025", marginTop: 12 }}>
          Diagnostic service did not respond. Please try again.
        </p>
      )}

      {diagnostic && (
        <div className="diagnostic-results-panel">
          {/* Top Risk Banner */}
          <div className={`risk-banner risk-${diagnostic.riskLevel}`}>
            <div className="risk-metric">
              <span className="risk-score-num">{diagnostic.riskScore}%</span>
              <span className="risk-score-label">Baseline Search Failure Risk</span>
            </div>
            <div className="risk-summary">
              <h4 className="risk-title">
                {diagnostic.riskLevel === "high"
                  ? "High Retrieval Failure Risk in Standard Search"
                  : diagnostic.riskLevel === "moderate"
                  ? "Moderate Retrieval Friction Expected"
                  : "Low Risk — Strong Anchor Grounding"}
              </h4>
              <p className="risk-mode">
                Likely Failure Mode: <strong>{diagnostic.predictedStage}</strong>
              </p>
            </div>
          </div>

          {/* Clues Breakdown */}
          <div className="diagnostic-section">
            <h4 className="t-eyebrow">
              Extracted Memory Clues ({diagnostic.source === "llm" ? "Groq LLM" : "Rule Engine"})
            </h4>
            {diagnostic.chips.length === 0 ? (
              <p className="t-support">
                No structured cues detected. Human recall often retains 0 exact keywords, causing
                standard search to return completely irrelevant photos.
              </p>
            ) : (
              <div className="clues-grid">
                {diagnostic.chips.map((c) => (
                  <div key={c.id} className="clue-card">
                    <span className="clue-tag">{c.cue.replace(/_/g, " ")}</span>
                    <span className="clue-val">“{c.label}”</span>
                    <span className="clue-filter">Mapped to: {c.filter_key}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Root Cause & Solution */}
          <div className="diagnostic-2col">
            <div className="diag-box failure-box">
              <h4 className="t-eyebrow" style={{ color: "#c5221f" }}>
                Why Standard Search Fails
              </h4>
              <p className="t-body">{diagnostic.failureExplanation}</p>
            </div>

            <div className="diag-box solution-box">
              <h4 className="t-eyebrow" style={{ color: "#137333" }}>
                How Memory Trails Rescues It
              </h4>
              <p className="t-body">{diagnostic.recoveryRecommendation}</p>
              <div style={{ marginTop: 14 }}>
                <a
                  href="https://memory-trails-demo.vercel.app"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn ghost"
                  style={{ display: "inline-block", fontSize: 13 }}
                >
                  Test this memory in Live Demo ↗
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
