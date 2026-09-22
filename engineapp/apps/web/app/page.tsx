"use client";

import { useState } from "react";
import { FunnelChart } from "@/app/components/FunnelChart";
import { EpisodeExplorer } from "@/app/components/EpisodeExplorer";
import { MemoryDiagnostic } from "@/app/components/MemoryDiagnostic";
import { AuditVisualizer } from "@/app/components/AuditVisualizer";
import { DataTable } from "@/app/components/DataTable";
import evidence from "@/public/data/evidence.json";

type Tab = "diagnostic" | "episodes" | "analytics" | "audit";

const MVP_URL = "https://memory-anchors-demo.vercel.app";

export default function DiscoveryEngine() {
  const [tab, setTab] = useState<Tab>("diagnostic");

  return (
    <main className="shell">
      <header className="topbar">
        <h2>Photo Retrieval Discovery Engine</h2>
        <nav>
          <a href={MVP_URL} target="_blank" rel="noopener noreferrer">
            See the MVP it led to ↗
          </a>
        </nav>
      </header>

      {/* Hero Header */}
      <div className="prose">
        <h1 className="t-page">Why people cannot find photos they remember</h1>
        <p className="hero-lead">
          An AI discovery platform analyzing <strong>85,140 public user posts</strong> across Google
          Play, Apple App Store, Reddit, and YouTube. Filtered and structured into{" "}
          <strong>720 retrieval episodes</strong> (144 specific recall failures), independently
          verified by cross-family model audits.
        </p>
      </div>

      {/* Stats Counter Strip */}
      <div className="stat-counter-strip">
        <div className="stat-card">
          <span className="stat-num">85,140</span>
          <span className="stat-label">Raw Posts Ingested</span>
        </div>
        <div className="stat-card">
          <span className="stat-num">720</span>
          <span className="stat-label">Structured Episodes</span>
        </div>
        <div className="stat-card">
          <span className="stat-num">144</span>
          <span className="stat-label">Specific Retrieval Failures</span>
        </div>
        <div className="stat-card">
          <span className="stat-num">77.1%</span>
          <span className="stat-label">Fails Before Search Completes</span>
        </div>
        <div className="stat-card">
          <span className="stat-num">2</span>
          <span className="stat-label">Audited Model Families</span>
        </div>
      </div>

      {/* Modern Navigation Tabs */}
      <div className="tabs" role="tablist">
        <button
          role="tab"
          aria-selected={tab === "diagnostic"}
          onClick={() => setTab("diagnostic")}
        >
          AI Memory Diagnostic
        </button>
        <button
          role="tab"
          aria-selected={tab === "episodes"}
          onClick={() => setTab("episodes")}
        >
          Real Episode Explorer (144)
        </button>
        <button
          role="tab"
          aria-selected={tab === "analytics"}
          onClick={() => setTab("analytics")}
        >
          Pipeline Funnel & Cues
        </button>
        <button
          role="tab"
          aria-selected={tab === "audit"}
          onClick={() => setTab("audit")}
        >
          Dual-Model Audit Lab
        </button>
      </div>

      {/* Tab 1: AI Memory Diagnostic */}
      {tab === "diagnostic" && (
        <section className="tab-pane">
          <MemoryDiagnostic />
        </section>
      )}

      {/* Tab 2: Real Episode Explorer */}
      {tab === "episodes" && (
        <section className="tab-pane">
          <EpisodeExplorer />
        </section>
      )}

      {/* Tab 3: Visual Analytics & Pipeline Funnel */}
      {tab === "analytics" && (
        <section className="tab-pane">
          <FunnelChart />

          <div style={{ marginTop: 36 }}>
            <h3 className="t-section">Cognitive Clues & Failure Breakdown</h3>
            <p className="t-support" style={{ marginBottom: 16 }}>
              Quantified recall patterns across all 144 verified retrieval attempts.
            </p>

            <div className="tables-grid">
              <DataTable
                rows={evidence.failure_stages.map((r) => ({
                  "failure stage": r.stage,
                  count: r.count,
                  "share of 144": `${(r.share * 100).toFixed(1)}%`,
                }))}
                caption="Where retrieval broke down (77.1% happen before recovery)"
              />

              <DataTable
                rows={evidence.cues.map((r) => ({
                  "what they remembered": r.cue,
                  posts: r.posts,
                  "ended badly": r["ended badly (of known outcomes)"],
                  "most common failure": r["most common failure"],
                }))}
                caption="Cues people actually remember (approximate time is #1)"
              />

              <DataTable
                rows={evidence.cues_lost.map((r) => ({
                  "what they had forgotten": r.value,
                  count: r.count,
                  "share of 144": r.share,
                }))}
                caption="What information they had forgotten (exact date is #1)"
              />

              <DataTable
                rows={evidence.asset_types.map((r) => ({
                  "kind of photo": r.value,
                  count: r.count,
                  "share of 144": r.share,
                }))}
                caption="What kinds of photos people struggle to retrieve"
              />
            </div>
          </div>
        </section>
      )}

      {/* Tab 4: Dual-Model Audit Lab */}
      {tab === "audit" && (
        <section className="tab-pane">
          <AuditVisualizer />
        </section>
      )}
    </main>
  );
}
