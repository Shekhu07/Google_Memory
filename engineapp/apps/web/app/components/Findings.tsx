"use client";

import { useState } from "react";
import evidence from "@/public/data/evidence.json";

export function Findings() {
  const [useBriefPop, setUseBriefPop] = useState(false);

  const activeData = useBriefPop ? evidence.findings.brief_population : evidence.findings.all_144;
  const totalN = activeData.n;

  return (
    <div className="findings-pane">
      {/* Scope Filter Header */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: 12,
        padding: "16px 20px",
        background: "var(--surface)",
        borderRadius: "var(--r-control)",
        border: "1px solid var(--line)",
        marginBottom: 28
      }}>
        <div>
          <span className="t-eyebrow" style={{ color: "var(--blue)" }}>Case Study Brief Analysis</span>
          <h3 className="t-section" style={{ fontSize: 18, marginTop: 2 }}>
            Empirical Findings Across Four Core Questions
          </h3>
          <p className="t-support" style={{ fontSize: 13 }}>
            Structured answers derived directly from {totalN} verified user retrieval attempts.
          </p>
        </div>

        {/* Population Toggle */}
        <div style={{ display: "flex", gap: 8, alignItems: "center", background: "var(--surface-subtle)", padding: 4, borderRadius: 8 }}>
          <button
            type="button"
            className={`btn ${!useBriefPop ? "primary" : "ghost"}`}
            style={{ minHeight: 34, padding: "0 14px", fontSize: 13 }}
            onClick={() => setUseBriefPop(false)}
          >
            All Specific Attempts ({evidence.counts.specific})
          </button>
          <button
            type="button"
            className={`btn ${useBriefPop ? "primary" : "ghost"}`}
            style={{ minHeight: 34, padding: "0 14px", fontSize: 13 }}
            onClick={() => setUseBriefPop(true)}
          >
            Brief Population Only ({evidence.counts.brief_population})
          </button>
        </div>
      </div>

      {useBriefPop && (
        <div style={{
          padding: "10px 16px",
          background: "#E8F0FE",
          border: "1px solid #D2E3FC",
          borderRadius: 8,
          marginBottom: 24,
          fontSize: 13,
          color: "var(--blue-dark)"
        }}>
          <strong>Brief Population Active:</strong> Showing the 45 retrieval attempts where the user explicitly stated <em>both</em> something they remembered and something they had forgotten (the core focus of the prompt).
        </div>
      )}

      {/* Grid of 4 Panels */}
      <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>

        {/* Panel 1: What people actually remember */}
        <section className="diag-box" style={{ background: "var(--surface)", border: "1px solid var(--line)" }}>
          <div style={{ borderBottom: "1px solid var(--line)", paddingBottom: 14, marginBottom: 16 }}>
            <span className="t-eyebrow" style={{ color: "var(--green)" }}>Question 2 (Brief)</span>
            <h3 className="t-section" style={{ marginTop: 4 }}>What Information Do People Actually Remember?</h3>
            <p className="t-body" style={{ fontStyle: "italic", color: "var(--ink)", marginTop: 6, fontWeight: 500 }}>
              “Approximate time is the most-kept cue ({useBriefPop ? "21/45" : "40/144"}); {useBriefPop ? "all retain cues in this cohort" : "a third keep nothing searchable (47/144)"}.”
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
            <div>
              <h4 className="t-eyebrow" style={{ marginBottom: 12 }}>Cues Retained Distribution (n = {totalN})</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {activeData.cues_retained.map((c: any) => (
                  <div key={c.value} style={{ fontSize: 13 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                      <span style={{ fontWeight: 500 }}>{c.value.replace(/_/g, " ")}</span>
                      <span><strong>{c.count}</strong> ({c.share})</span>
                    </div>
                    <div style={{ width: "100%", height: 6, background: "var(--surface-subtle)", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ width: c.share, height: "100%", background: "var(--green)", borderRadius: 3 }} />
                    </div>
                  </div>
                ))}

                {!useBriefPop && (
                  <div style={{ fontSize: 13, marginTop: 4, paddingTop: 6, borderTop: "1px dashed var(--line)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                      <span style={{ color: "#C5221F", fontWeight: 600 }}>no cue retained (cannot express)</span>
                      <span style={{ color: "#C5221F" }}><strong>{evidence.findings.all_144.no_cue_count}</strong> ({evidence.findings.all_144.no_cue_share})</span>
                    </div>
                    <div style={{ width: "100%", height: 6, background: "var(--surface-subtle)", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ width: evidence.findings.all_144.no_cue_share, height: "100%", background: "#C5221F", borderRadius: 3 }} />
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12, justifyContent: "center" }}>
              <span className="t-eyebrow">Real User Evidence</span>
              {evidence.findings.sample_quotes.q2_remembered.map((q: any, i: number) => (
                <div key={i} style={{ padding: "12px 14px", background: "var(--surface-subtle)", borderRadius: 8, borderLeft: "3px solid var(--green)" }}>
                  <p style={{ fontStyle: "italic", fontSize: 13, color: "var(--ink)", marginBottom: 4 }}>“{q.quote}”</p>
                  <span className="t-meta" style={{ fontSize: 11 }}>Cue: <strong>{q.cue}</strong> · Source: {q.source}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Panel 2: What people have forgotten */}
        <section className="diag-box" style={{ background: "var(--surface)", border: "1px solid var(--line)" }}>
          <div style={{ borderBottom: "1px solid var(--line)", paddingBottom: 14, marginBottom: 16 }}>
            <span className="t-eyebrow" style={{ color: "#C5221F" }}>Question 3 (Brief)</span>
            <h3 className="t-section" style={{ marginTop: 4 }}>What Information Have They Forgotten?</h3>
            <p className="t-body" style={{ fontStyle: "italic", color: "var(--ink)", marginTop: 6, fontWeight: 500 }}>
              “Date and album are lost most. Exact words and place are lost less often, but 'text in image' fails most when kept (5 of 8 known outcomes not found).”
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
            <div>
              <h4 className="t-eyebrow" style={{ marginBottom: 12 }}>The Brief's Unknowns (n = {totalN})</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {activeData.cues_lost.map((c: any) => (
                  <div key={c.value} style={{ fontSize: 13 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                      <span style={{ fontWeight: 500 }}>
                        {c.value === "date" ? "Exact Date (When)" :
                         c.value === "album" ? "Album / Folder (Storage)" :
                         c.value === "place" ? "Place (Where)" :
                         c.value === "exact_words" ? "Exact Words (Content)" :
                         c.value === "people" ? "People (Who)" : c.value}
                      </span>
                      <span><strong>{c.count}</strong> ({c.share})</span>
                    </div>
                    <div style={{ width: "100%", height: 6, background: "var(--surface-subtle)", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ width: c.share, height: "100%", background: "#C5221F", borderRadius: 3 }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12, justifyContent: "center" }}>
              <span className="t-eyebrow">Real User Evidence</span>
              {evidence.findings.sample_quotes.q3_lost.map((q: any, i: number) => (
                <div key={i} style={{ padding: "12px 14px", background: "var(--surface-subtle)", borderRadius: 8, borderLeft: "3px solid #C5221F" }}>
                  <p style={{ fontStyle: "italic", fontSize: 13, color: "var(--ink)", marginBottom: 4 }}>“{q.quote}”</p>
                  <span className="t-meta" style={{ fontSize: 11 }}>Lost: <strong>{q.cue}</strong> · Source: {q.source}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Panel 3: What kinds of photos people struggle to retrieve */}
        <section className="diag-box" style={{ background: "var(--surface)", border: "1px solid var(--line)" }}>
          <div style={{ borderBottom: "1px solid var(--line)", paddingBottom: 14, marginBottom: 16 }}>
            <span className="t-eyebrow" style={{ color: "var(--blue)" }}>Question 1 (Brief)</span>
            <h3 className="t-section" style={{ marginTop: 4 }}>What Kinds of Old Photos Do Users Struggle to Retrieve?</h3>
            <p className="t-body" style={{ fontStyle: "italic", color: "var(--ink)", marginTop: 6, fontWeight: 500 }}>
              “Standard photos dominate public complaints ({useBriefPop ? "24/45" : "80/144"}); utility photos (receipts, screenshots) are rare in public reviews ({useBriefPop ? "4/45" : "10/144"}).”
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
            <div>
              <h4 className="t-eyebrow" style={{ marginBottom: 12 }}>Photo / Asset Type Breakdown (n = {totalN})</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {activeData.asset_types.map((c: any) => (
                  <div key={c.value} style={{ fontSize: 13 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                      <span style={{ fontWeight: 500 }}>{c.value.replace(/_/g, " ")}</span>
                      <span><strong>{c.count}</strong> ({c.share})</span>
                    </div>
                    <div style={{ width: "100%", height: 6, background: "var(--surface-subtle)", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ width: c.share, height: "100%", background: "var(--blue)", borderRadius: 3 }} />
                    </div>
                  </div>
                ))}
              </div>

              <p className="t-meta" style={{ marginTop: 14, fontSize: 12, lineHeight: 1.4 }}>
                <strong>Evidence Caveat:</strong> In public store reviews, 15/144 specifically describe the photo as "old"; 14 describe recent photos. Utility documents/receipts represent only 3/144 public posts, cautioning against filing-cabinet over-indexing.
              </p>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12, justifyContent: "center" }}>
              <span className="t-eyebrow">Real User Evidence</span>
              {evidence.findings.sample_quotes.q1_photos.map((q: any, i: number) => (
                <div key={i} style={{ padding: "12px 14px", background: "var(--surface-subtle)", borderRadius: 8, borderLeft: "3px solid var(--blue)" }}>
                  <p style={{ fontStyle: "italic", fontSize: 13, color: "var(--ink)", marginBottom: 4 }}>“{q.quote}”</p>
                  <span className="t-meta" style={{ fontSize: 11 }}>Target Type: <strong>{q.type}</strong> · Source: {q.source}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Panel 4: How people formulate searches (Q4 / D4) */}
        <section className="diag-box" style={{ background: "var(--surface)", border: "1px solid var(--line)" }}>
          <div style={{ borderBottom: "1px solid var(--line)", paddingBottom: 14, marginBottom: 16 }}>
            <span className="t-eyebrow" style={{ color: "#B06000" }}>Question 4 (Brief)</span>
            <h3 className="t-section" style={{ marginTop: 4 }}>How Do Users Formulate Searches When Memory Is Incomplete?</h3>
            <p className="t-body" style={{ fontStyle: "italic", color: "var(--ink)", marginTop: 6, fontWeight: 500 }}>
              “In classic search, people reduce a rich memory to one noun ('dog', 'cake', 'restaurant'). Full sentences appear only with Ask Photos, and those were successes.”
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
            <div>
              <h4 className="t-eyebrow" style={{ marginBottom: 12 }}>Query Length Histogram (32 Verified Verbatim Queries)</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {evidence.query_lengths.map((q: any) => (
                  <div key={q.length} style={{ fontSize: 13 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                      <span style={{ fontWeight: 600 }}>{q.length}</span>
                      <span><strong>{q.count} queries</strong> ({q.share})</span>
                    </div>
                    <div style={{ width: "100%", height: 8, background: "var(--surface-subtle)", borderRadius: 4, overflow: "hidden" }}>
                      <div style={{ width: q.share, height: "100%", background: "#F29900", borderRadius: 4 }} />
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: 16, padding: "12px", background: "var(--surface-subtle)", borderRadius: 8 }}>
                <span className="t-eyebrow" style={{ display: "block", marginBottom: 6 }}>Key Empirical Finding:</span>
                <p className="t-support" style={{ fontSize: 13, lineHeight: 1.45 }}>
                  <strong>20 of 32 queries are a single word</strong> (e.g., “dog”, “cake”, “idea”). <strong>9 are two words</strong>. The only 2 full descriptive sentences in the entire dataset occurred under Ask Photos and both resulted in <code>found_fast</code>. Classic keyword search forces users into artificial single-noun queries where vague associative context is lost.
                </p>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12, justifyContent: "center" }}>
              <span className="t-eyebrow">Classic vs Ask Photos Comparison</span>
              {evidence.findings.sample_quotes.q4_search.map((q: any, i: number) => (
                <div key={i} style={{ padding: "12px 14px", background: "var(--surface-subtle)", borderRadius: 8, borderLeft: "3px solid #F29900" }}>
                  <p style={{ fontStyle: "italic", fontSize: 13, color: "var(--ink)", marginBottom: 4 }}>“{q.quote}”</p>
                  <span className="t-meta" style={{ fontSize: 11 }}>Pattern: <strong>{q.mode}</strong> · Source: {q.source}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Verbatim Viewer */}
          <div style={{ marginTop: 24, paddingTop: 18, borderTop: "1px solid var(--line)" }}>
            <h4 className="t-eyebrow" style={{ marginBottom: 12 }}>Sample Verbatim Queries from the 144 Attempts ({evidence.verbatims.length} total)</h4>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", fontSize: 13, borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "var(--surface-subtle)", borderBottom: "1px solid var(--line)" }}>
                    <th style={{ padding: "8px 10px", textAlign: "left" }}>Exact Query Typed</th>
                    <th style={{ padding: "8px 10px", textAlign: "center" }}>Words</th>
                    <th style={{ padding: "8px 10px", textAlign: "left" }}>Search Mode</th>
                    <th style={{ padding: "8px 10px", textAlign: "left" }}>Era</th>
                    <th style={{ padding: "8px 10px", textAlign: "left" }}>Failure Stage</th>
                    <th style={{ padding: "8px 10px", textAlign: "left" }}>Outcome</th>
                  </tr>
                </thead>
                <tbody>
                  {evidence.verbatims.slice(0, 10).map((v: any, idx: number) => (
                    <tr key={idx} style={{ borderBottom: "1px solid var(--line)" }}>
                      <td style={{ padding: "8px 10px", fontWeight: 600 }}>“{v.query}”</td>
                      <td style={{ padding: "8px 10px", textAlign: "center" }}>{v.words}</td>
                      <td style={{ padding: "8px 10px" }}>{v.search_mode.replace(/_/g, " ")}</td>
                      <td style={{ padding: "8px 10px" }}>{v.era.replace(/_/g, " ")}</td>
                      <td style={{ padding: "8px 10px" }}>{v.stage.replace(/_/g, " ")}</td>
                      <td style={{ padding: "8px 10px" }}>
                        <span style={{
                          padding: "2px 6px",
                          borderRadius: 4,
                          fontSize: 11,
                          fontWeight: 600,
                          background: v.outcome === "found_fast" ? "#E6F4EA" : v.outcome === "not_found" ? "#FCE8E6" : "var(--surface-subtle)",
                          color: v.outcome === "found_fast" ? "#137333" : v.outcome === "not_found" ? "#C5221F" : "var(--ink-soft)"
                        }}>
                          {v.outcome.replace(/_/g, " ")}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="t-meta" style={{ marginTop: 8, fontSize: 12 }}>
                Showing 10 of {evidence.verbatims.length} quoted verbatims across the 144 attempts.
              </p>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
