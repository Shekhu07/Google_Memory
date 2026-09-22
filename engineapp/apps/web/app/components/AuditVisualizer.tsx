"use client";

import evidence from "@/public/data/evidence.json";

export function AuditVisualizer() {
  const audit = evidence.audit;
  const agreement = audit.agreement.fields;

  return (
    <div className="audit-visualizer">
      <div className="audit-header">
        <h3 className="t-section">Dual-Model Cross-Family Audit</h3>
        <p className="t-support">
          To ensure scientific rigor and eliminate model hallucination, 203 retrieval episodes were
          re-read independently by a completely different model family.
        </p>
      </div>

      <div className="model-comparison-banner">
        <div className="model-card primary-model">
          <span className="model-role">Primary Extraction Model</span>
          <span className="model-name">openai / gpt-oss-120b</span>
          <span className="model-task">720 episodes extracted</span>
        </div>
        <div className="vs-badge">VS</div>
        <div className="model-card audit-model">
          <span className="model-role">Independent Audit Model</span>
          <span className="model-name">{audit.audit_model}</span>
          <span className="model-task">203 pairs audited blind</span>
        </div>
      </div>

      <div className="audit-metrics-grid">
        <div className="metric-box">
          <span className="metric-label">Failure Stage Agreement</span>
          <span className="metric-big-val">κ 0.509</span>
          <span className="metric-interp">Moderate Agreement</span>
          <p className="t-support" style={{ marginTop: 8 }}>
            Both models agreed on whether retrieval failed before or after search in 61.6% of
            cases.
          </p>
        </div>

        <div className="metric-box">
          <span className="metric-label">Hypothesis Alignment</span>
          <span className="metric-big-val">Jaccard 0.347</span>
          <span className="metric-interp" style={{ color: "#c5221f" }}>
            High Divergence
          </span>
          <p className="t-support" style={{ marginTop: 8 }}>
            Models frequently attributed failures to different root causes, proving single-model
            summaries are unreliable.
          </p>
        </div>

        <div className="metric-box">
          <span className="metric-label">Verified Evidence Quotes</span>
          <span className="metric-big-val">97.0%</span>
          <span className="metric-interp" style={{ color: "#137333" }}>
            High Fidelity
          </span>
          <p className="t-support" style={{ marginTop: 8 }}>
            97% of audit quotes matched verbatim text in the user&rsquo;s original public post.
          </p>
        </div>
      </div>

      <div className="verdict-callout">
        <h4 className="t-section" style={{ fontSize: 16 }}>
          The Finding: Why the Hypothesis Ranking Does Not Come Blindly From the Engine
        </h4>
        <p className="t-body" style={{ marginTop: 6 }}>
          When the audit model re-read the posts, the top hypothesis ranking shifted from{" "}
          <strong>[H3, H1]</strong> to <strong>[H3, H6]</strong>. Both models agreed that{" "}
          <strong>H3 (Dead-End Failure)</strong> was the dominant problem. However, because their
          Jaccard agreement on root hypotheses was only 0.347, the final product verdicts were
          grounded in measured <strong>`failure_stage` telemetry (41.7% not surfaced + 35.4% system
          misunderstood)</strong> rather than an LLM&rsquo;s subjective opinion.
        </p>
      </div>

      <div className="audit-breakdown-table-wrap">
        <table className="audit-table">
          <thead>
            <tr>
              <th>Evaluated Field</th>
              <th>Observed Agreement</th>
              <th>Chance-Adjusted Metric</th>
              <th>Assessment</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Search Mode</td>
              <td>79.8%</td>
              <td>κ 0.522</td>
              <td><span className="badge-ok">Reliable</span></td>
            </tr>
            <tr>
              <td>Failure Stage</td>
              <td>61.6%</td>
              <td>κ 0.509</td>
              <td><span className="badge-ok">Reliable</span></td>
            </tr>
            <tr>
              <td>Cues Lost</td>
              <td>67.3%</td>
              <td>Jaccard 0.673</td>
              <td><span className="badge-ok">Reliable</span></td>
            </tr>
            <tr>
              <td>Cues Retained</td>
              <td>55.7%</td>
              <td>Jaccard 0.557</td>
              <td><span className="badge-warn">Moderate</span></td>
            </tr>
            <tr>
              <td>Hypotheses</td>
              <td>—</td>
              <td>Jaccard 0.347</td>
              <td><span className="badge-alert">Divergent (Overruled)</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
