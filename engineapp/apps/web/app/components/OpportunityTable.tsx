"use client";

import { useState } from "react";
import evidence from "@/public/data/evidence.json";

export function OpportunityTable() {
  const [expandedId, setExpandedId] = useState<string | null>("O1");

  const opportunities = evidence.opportunities;

  return (
    <div className="opportunity-pane">
      <div style={{
        padding: "20px 24px",
        background: "var(--surface)",
        borderRadius: "var(--r-control)",
        border: "1px solid var(--line)",
        marginBottom: 24
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
          <div>
            <span className="t-eyebrow" style={{ color: "var(--blue)" }}>Evidence-Based Prioritization</span>
            <h3 className="t-section" style={{ fontSize: 20, marginTop: 4 }}>
              Opportunity Areas Comparison (O1–O9)
            </h3>
            <p className="t-support" style={{ marginTop: 4, maxWidth: 800 }}>
              Synthesized strictly from fields independently verified with high agreement between model families: <strong>failure stage</strong> (κ = 0.509) and <strong>cues retained</strong> (Jaccard = 0.557). Areas overlap because a single attempt can retain multiple cues.
            </p>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ fontSize: 12, padding: "4px 8px", background: "#FEF7E0", color: "#B06000", borderRadius: 4, fontWeight: 600 }}>
              Judgement Columns Labelled
            </span>
          </div>
        </div>

        {/* Strategic Takeaway Banner */}
        <div style={{
          marginTop: 18,
          padding: "14px 16px",
          background: "#E8F0FE",
          border: "1px solid #D2E3FC",
          borderRadius: 8,
          display: "flex",
          gap: 16,
          alignItems: "center"
        }}>
          <div style={{ fontSize: 24 }}>💡</div>
          <div style={{ fontSize: 13, lineHeight: 1.45, color: "var(--ink)" }}>
            <strong>Why Memory Trails was built:</strong> <strong>O1 (Vague time)</strong> is the single largest opportunity area fitting the brief: <strong>42 attempts</strong> (and <strong>21 of the 45</strong> partial-memory attempts). Standard search fails because users know <em>whenish</em> a photo happened but not the exact day.
          </div>
        </div>
      </div>

      {/* Comparison Table */}
      <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--r-card)", overflow: "hidden" }}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "var(--surface-subtle)", borderBottom: "1px solid var(--line)", textAlign: "left" }}>
                <th style={{ padding: "12px 14px" }}>Opportunity Area</th>
                <th style={{ padding: "12px 14px", textAlign: "center" }}>Attempts (of 144)</th>
                <th style={{ padding: "12px 14px", textAlign: "center" }}>Brief Pop (of 45)</th>
                <th style={{ padding: "12px 14px" }}>Not Found / Known</th>
                <th style={{ padding: "12px 14px" }}>Top Failure Stage</th>
                <th style={{ padding: "12px 14px", textAlign: "center" }}>Pre vs Post Ask Photos</th>
                <th style={{ padding: "12px 14px", background: "#FEF7E0" }}>Brief Fit *</th>
                <th style={{ padding: "12px 14px", background: "#FEF7E0" }}>MVP Addresses *</th>
              </tr>
            </thead>
            <tbody>
              {opportunities.map((op: any) => {
                const isSelected = expandedId === op.id;
                const isO1 = op.id === "O1";

                return (
                  <tr
                    key={op.id}
                    onClick={() => setExpandedId(isSelected ? null : op.id)}
                    style={{
                      borderBottom: "1px solid var(--line)",
                      cursor: "pointer",
                      background: isO1 ? "#F4F8FE" : isSelected ? "var(--surface-subtle)" : "transparent",
                      transition: "background 0.15s ease"
                    }}
                  >
                    <td style={{ padding: "12px 14px", fontWeight: isO1 ? 700 : 600 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span>{op.name}</span>
                        {isO1 && (
                          <span style={{ fontSize: 10, background: "var(--blue)", color: "white", padding: "1px 6px", borderRadius: 4, fontWeight: 700 }}>
                            CORE
                          </span>
                        )}
                      </div>
                      <span className="t-meta" style={{ display: "block", fontSize: 11, marginTop: 2 }}>{op.description}</span>
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "center", fontWeight: isO1 ? 700 : 500 }}>
                      {op.attempts}
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "center", fontWeight: isO1 ? 700 : 500, color: op.in_brief_population > 0 ? "var(--blue-dark)" : "var(--ink-muted)" }}>
                      {op.in_brief_population}
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <span style={{
                        padding: "2px 8px",
                        borderRadius: 4,
                        fontSize: 12,
                        background: op.not_found_known.includes("7/15") || op.not_found_known.includes("5/8") || op.not_found_known.includes("14/15") ? "#FCE8E6" : "var(--surface-subtle)",
                        color: op.not_found_known.includes("7/15") || op.not_found_known.includes("5/8") || op.not_found_known.includes("14/15") ? "#C5221F" : "inherit"
                      }}>
                        {op.not_found_known}
                      </span>
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <code>{op.top_failure_stage}</code>
                    </td>
                    <td style={{ padding: "12px 14px", textAlign: "center" }}>
                      {op.pre_vs_post}
                    </td>
                    <td style={{ padding: "12px 14px", background: isO1 ? "#FFF9EE" : "rgba(254, 247, 224, 0.4)", fontWeight: 500 }}>
                      {op.brief_fit}
                    </td>
                    <td style={{ padding: "12px 14px", background: isO1 ? "#FFF9EE" : "rgba(254, 247, 224, 0.4)", fontWeight: 500 }}>
                      {op.mvp_addresses}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div style={{ padding: "12px 16px", background: "var(--surface-subtle)", borderTop: "1px solid var(--line)", fontSize: 12, color: "var(--ink-soft)" }}>
          * Columns marked with an asterisk (<strong>Brief Fit</strong> and <strong>MVP Addresses</strong>) are product judgement evaluations, not empirical model labels.
        </div>
      </div>

      {/* Selected Opportunity Quotes Drilldown */}
      {expandedId && (
        <div style={{ marginTop: 24, padding: "20px", background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--r-control)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <h4 className="t-section" style={{ fontSize: 16 }}>
              Evidence Quotes for {opportunities.find((o: any) => o.id === expandedId)?.name}
            </h4>
            <span className="t-meta">Click any row above to inspect user evidence</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 14 }}>
            {opportunities.find((o: any) => o.id === expandedId)?.quotes.map((q: string, idx: number) => (
              <div key={idx} style={{ padding: "12px 14px", background: "var(--surface-subtle)", borderRadius: 8, borderLeft: "3px solid var(--blue)" }}>
                <p style={{ fontStyle: "italic", fontSize: 13, color: "var(--ink)" }}>“{q}”</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Narrative Synthesis & Methodological Rigor */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16, marginTop: 24 }}>
        <div className="diag-box" style={{ background: "var(--surface)" }}>
          <h4 className="t-eyebrow" style={{ color: "var(--green)" }}>1. The Primary Opportunity (O1)</h4>
          <p className="t-body" style={{ fontSize: 14, marginTop: 6, lineHeight: 1.45 }}>
            <strong>O1 (Vague time)</strong> accounts for 42 attempts (21 in the brief's partial memory population). When users remember "sometime last year" or "around my birthday", standard exact-date search fails (20 break at <code>not_surfaced</code>). This directly justifies the MVP's <strong>Time Ribbon</strong> and episodic anchor architecture.
          </p>
        </div>

        <div className="diag-box" style={{ background: "var(--surface)" }}>
          <h4 className="t-eyebrow" style={{ color: "#C5221F" }}>2. The Sharpest Retrieval Gap (O2)</h4>
          <p className="t-body" style={{ fontSize: 14, marginTop: 6, lineHeight: 1.45 }}>
            <strong>O2 (Text inside photo)</strong> fails in 5 of 8 known outcomes (62.5% failure). When users remember a specific sign, receipt, or screenshot word, Google Photos frequently misunderstands or fails to surface it. The MVP explicitly flags this for the roadmap (OCR / Lens integration) rather than making false claims.
          </p>
        </div>

        <div className="diag-box" style={{ background: "var(--surface)" }}>
          <h4 className="t-eyebrow" style={{ color: "var(--ink-soft)" }}>3. Disciplined Scope Exclusions (O7 & O9)</h4>
          <p className="t-body" style={{ fontSize: 14, marginTop: 6, lineHeight: 1.45 }}>
            <strong>O7 (Exact date)</strong> and <strong>O9 (App update path changes)</strong> are explicitly excluded from our memory retrieval solution. App navigation regressions (12 attempts) represent UX updates, not cognitive retrieval problems.
          </p>
        </div>
      </div>
    </div>
  );
}
