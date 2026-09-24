"use client";

import { useState } from "react";
import { diagnose, type DiagnosisResult } from "@/lib/api";

const PRESETS = [
  "my grandmother's birthday in Pune a few years ago",
  "a receipt I photographed sometime last year",
  "the photo of my parking spot",
  "a picture of my kid with a cake a few birthdays ago",
  "that screenshot with some text I need",
];

const MVP_URL = "https://memory-trails-v2.vercel.app";

export function MemoryDiagnostic() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  async function onAnalyze(promptText?: string) {
    const q = (promptText !== undefined ? promptText : text).trim();
    if (!q) return;
    if (promptText !== undefined) setText(promptText);

    setBusy(true);
    setFailed(false);
    try {
      const res = await diagnose(q);
      setResult(res);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="memory-diagnostic">
      <div className="diagnostic-header">
        <h3 className="t-section">Compare your memory with real people's attempts</h3>
        <p className="t-support">
          Describe a photo you are trying to find. The engine extracts your cognitive cues using the pipeline
          schema, matches a cohort from the 144 verified user retrieval attempts, and displays empirical breakdown stages
          and real quotes.
        </p>
      </div>

      <div className="diagnostic-input-wrap">
        <textarea
          className="prompt"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Describe a memory (e.g. 'my grandmother's birthday in Pune a few years ago')..."
          maxLength={500}
          aria-label="A memory description to compare with real attempts"
        />

        <div className="preset-suggestions">
          <span className="preset-label">Or try a real episode archetype:</span>
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
            {busy ? "Comparing With Real Cohorts…" : "Compare Memory"}
          </button>
        </div>
      </div>

      {failed && (
        <p className="t-support" style={{ color: "#d93025", marginTop: 12 }}>
          Diagnostic service did not respond. Please try again.
        </p>
      )}

      {result && (
        <div className="diagnostic-results-panel">
          {/* Cognitive Profile extracted */}
          <div className="diag-box" style={{ background: "var(--surface)", border: "1px solid var(--line)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <span className="t-eyebrow">Pipeline Cognitive Profile</span>
              <span className="t-meta" style={{ background: "var(--surface-subtle)", padding: "2px 8px", borderRadius: 4 }}>
                Source: {result.source === "pipeline_prompt" ? `Pipeline prompt · ${result.model}` : "Keyword rules (fallback)"}
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
              <div>
                <span className="t-meta" style={{ display: "block", marginBottom: 6, color: "var(--green)" }}>
                  ✓ You remember ({result.profile.cues_retained.length}):
                </span>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {result.profile.cues_retained.length > 0 ? (
                    result.profile.cues_retained.map((c) => (
                      <span key={c} style={{ background: "#E6F4EA", color: "#137333", fontSize: 13, padding: "4px 10px", borderRadius: 999, fontWeight: 500 }}>
                        {c.replace(/_/g, " ")}
                      </span>
                    ))
                  ) : (
                    <span className="t-support">No cues detected (cannot express)</span>
                  )}
                </div>
              </div>

              <div>
                <span className="t-meta" style={{ display: "block", marginBottom: 6, color: "#C5221F" }}>
                  ✗ You've lost ({result.profile.cues_lost.length}):
                </span>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {result.profile.cues_lost.length > 0 ? (
                    result.profile.cues_lost.map((c) => (
                      <span key={c} style={{ background: "#FCE8E6", color: "#C5221F", fontSize: 13, padding: "4px 10px", borderRadius: 999, fontWeight: 500 }}>
                        {c.replace(/_/g, " ")}
                      </span>
                    ))
                  ) : (
                    <span className="t-support">None stated</span>
                  )}
                </div>
              </div>

              <div>
                <span className="t-meta" style={{ display: "block", marginBottom: 6, color: "var(--ink-soft)" }}>
                  Photo type:
                </span>
                <span style={{ background: "var(--surface-subtle)", color: "var(--ink)", fontSize: 13, padding: "4px 10px", borderRadius: 999, fontWeight: 600 }}>
                  {result.profile.asset_type.replace(/_/g, " ")}
                </span>
              </div>
            </div>
          </div>

          {/* Cohort Match Banner */}
          <div className="risk-banner" style={{ background: "#F1F4F8", border: "1px solid #D2E3FC", color: "var(--ink)" }}>
            <div className="risk-metric">
              <span className="risk-score-num" style={{ color: "var(--blue)" }}>{result.cohort.n}</span>
              <span className="risk-score-label" style={{ color: "var(--ink-soft)" }}>Real Attempts Matched</span>
            </div>
            <div className="risk-summary">
              <h4 className="risk-title" style={{ color: "var(--ink)" }}>
                {result.cohort.n === 0
                  ? "No real attempt to compare with yet"
                  : result.cohort.n >= 5
                  ? `${result.cohort.n} real attempts remembered a similar set of cues`
                  : `Too few real attempts match this combination (n = ${result.cohort.n})`}
              </h4>
              <p className="risk-mode" style={{ color: "var(--ink-soft)" }}>
                Cohort: {result.cohort.rule}. Drawn from the 144 specific retrieval attempts.
                {result.source === "rules" && " The model path was unavailable, so cues were read by keyword rules."}
              </p>
            </div>
          </div>

          {/* Real Breakdown: Where they broke & Outcomes */}
          <div className="diagnostic-2col">
            <div className="diag-box" style={{ borderLeft: "4px solid #F29900" }}>
              <h4 className="t-eyebrow" style={{ color: "#B06000", marginBottom: 8 }}>
                Where this cohort broke down
              </h4>
              {Object.keys(result.cohort.stages).length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {Object.entries(result.cohort.stages).map(([stage, count]) => (
                    <div key={stage} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 14 }}>
                      <span>{stage.replace(/_/g, " ")}</span>
                      <strong style={{ background: "var(--surface-subtle)", padding: "2px 8px", borderRadius: 4 }}>
                        {count} {result.cohort.n >= 5 ? `(${((count / result.cohort.n) * 100).toFixed(0)}%)` : ""}
                      </strong>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="t-support">No stage breakdowns available.</p>
              )}
            </div>

            <div className="diag-box" style={{ borderLeft: "4px solid var(--blue)" }}>
              <h4 className="t-eyebrow" style={{ color: "var(--blue)", marginBottom: 8 }}>
                Outcome of these attempts
              </h4>
              {Object.keys(result.cohort.outcomes).length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {Object.entries(result.cohort.outcomes).map(([outcome, count]) => (
                    <div key={outcome} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 14 }}>
                      <span>{outcome.replace(/_/g, " ")}</span>
                      <strong style={{ background: "var(--surface-subtle)", padding: "2px 8px", borderRadius: 4 }}>
                        {count} {result.cohort.n >= 5 ? `(${((count / result.cohort.n) * 100).toFixed(0)}%)` : ""}
                      </strong>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="t-support">No outcome counts available.</p>
              )}
              <p className="t-meta" style={{ marginTop: 12, fontSize: 12, color: "var(--ink-muted)" }}>
                Note: Outcomes are often unstated in reviews (57% unknown across full dataset; κ = 0.161 inter-model agreement).
              </p>
            </div>
          </div>

          {/* Real quotes from matching cohort */}
          {result.quotes.length > 0 && (
            <div className="diag-box">
              <h4 className="t-eyebrow" style={{ marginBottom: 12 }}>
                Real User Quotes from this Cohort ({result.quotes.length} examples)
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {result.quotes.map((q, idx) => (
                  <div key={idx} style={{ padding: "12px 14px", background: "var(--surface-subtle)", borderRadius: 8, border: "1px solid var(--line)" }}>
                    <p style={{ fontStyle: "italic", fontSize: 14, color: "var(--ink)", marginBottom: 6 }}>
                      “{q.evidence}”
                    </p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 10, fontSize: 12, color: "var(--ink-soft)" }}>
                      <span>Source: <strong>{q.source}</strong></span>
                      {q.era && <span>Era: <strong>{q.era.replace(/_/g, " ")}</strong></span>}
                      {q.date && <span>Date: <strong>{q.date}</strong></span>}
                      {q.failure_stage && <span>Stage: <strong>{q.failure_stage.replace(/_/g, " ")}</strong></span>}
                      {q.outcome && <span>Outcome: <strong>{q.outcome.replace(/_/g, " ")}</strong></span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Call to action connecting to MVP */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--r-control)" }}>
            <div>
              <h5 style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>See how the Memory Trails MVP addresses this retrieval gap</h5>
              <p className="t-support" style={{ fontSize: 13, marginTop: 2 }}>
                Designed specifically for vague time, anchor recognition, and browse-first recovery.
              </p>
            </div>
            <a
              href={MVP_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="btn primary"
              style={{ fontSize: 13, minHeight: 38, textDecoration: "none", display: "inline-flex", alignItems: "center" }}
            >
              Open Memory Trails v2 ↗
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
