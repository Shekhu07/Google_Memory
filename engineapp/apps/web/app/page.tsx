"use client";

import { useState } from "react";
import Link from "next/link";
import { Findings } from "@/app/components/Findings";
import { OpportunityTable } from "@/app/components/OpportunityTable";
import { MemoryDiagnostic } from "@/app/components/MemoryDiagnostic";
import { EpisodeExplorer } from "@/app/components/EpisodeExplorer";
import { FunnelChart } from "@/app/components/FunnelChart";
import { AuditVisualizer } from "@/app/components/AuditVisualizer";
import { DataTable } from "@/app/components/DataTable";
import evidence from "@/public/data/evidence.json";

type Tab = "findings" | "opportunities" | "diagnostic" | "episodes" | "analytics" | "audit";

const MVP_URL = "https://memory-trails-v2.vercel.app";

export default function DiscoveryEngine() {
  const [tab, setTab] = useState<Tab>("findings");

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
          A discovery pipeline: <strong>85,140 public user posts</strong> across Google Play, Apple App Store, Reddit, and YouTube
          → <strong>720 structured retrieval episodes</strong> → <strong>144 specific recall failures</strong>,
          independently audited by a second model family.
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
          <span className="stat-label">Break at Interpretation or Surfacing (111/144)</span>
        </div>
        <div className="stat-card">
          <span className="stat-num">45</span>
          <span className="stat-label">Brief Partial-Memory Population</span>
        </div>
        <div className="stat-card">
          <span className="stat-num">2</span>
          <span className="stat-label">Audited Model Families</span>
        </div>
      </div>

      {/* Primary research: the two questionnaires behind the deck */}
      <section className="research-links" aria-label="Primary research forms">
        <p className="t-eyebrow">Primary research</p>
        <div className="research-grid">
          <div className="research-card">
            <span className="research-title">User research survey</span>
            <span className="t-support">15 responses, 23–30 Sep 2026. Structured questionnaire mapped onto the engine&apos;s fields.</span>
            <span className="research-actions">
              <Link href="/survey">See every question and answer →</Link>
            </span>
          </div>
          <div className="research-card">
            <span className="research-title">MVP user test form</span>
            <span className="t-support">6 responses, 3–4 Oct 2026. Self-serve test of the Memory Trails prototype.</span>
            <span className="research-actions">
              <Link href="/mvp-test">See every question and answer →</Link>
            </span>
          </div>
        </div>
        <p className="t-support" style={{ marginTop: 8 }}>
          Responses are anonymised: contact details removed, timestamps cut to the date, each respondent given an ID
          (S01–S15, R01–R06).
        </p>
      </section>

      {/* Navigation Tabs */}
      <div className="tabs" role="tablist">
        <button
          role="tab"
          aria-selected={tab === "findings"}
          onClick={() => setTab("findings")}
        >
          Findings (Answers to Brief)
        </button>
        <button
          role="tab"
          aria-selected={tab === "opportunities"}
          onClick={() => setTab("opportunities")}
        >
          Opportunity Areas (O1–O9)
        </button>
        <button
          role="tab"
          aria-selected={tab === "diagnostic"}
          onClick={() => setTab("diagnostic")}
        >
          Compare Your Memory
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

      {/* Tab 1: Findings (Answers to Brief) — Default */}
      {tab === "findings" && (
        <section className="tab-pane">
          <Findings />
        </section>
      )}

      {/* Tab 2: Opportunity Areas (O1-O9) */}
      {tab === "opportunities" && (
        <section className="tab-pane">
          <OpportunityTable />
        </section>
      )}

      {/* Tab 3: Compare Your Memory (Evidence Diagnostic) */}
      {tab === "diagnostic" && (
        <section className="tab-pane">
          <MemoryDiagnostic />
        </section>
      )}

      {/* Tab 4: Real Episode Explorer */}
      {tab === "episodes" && (
        <section className="tab-pane">
          <EpisodeExplorer />
        </section>
      )}

      {/* Tab 5: Visual Analytics & Pipeline Funnel */}
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
                caption="Where retrieval broke down (77.1% break at interpretation or surfacing)"
              />

              <DataTable
                rows={evidence.cues.map((r) => ({
                  "what they remembered": r.cue,
                  posts: r.posts,
                  "ended badly": r["ended badly (of known outcomes)"],
                  "most common failure": r["most common failure"],
                }))}
                caption="Cues people actually remember (approximate time is #1 with 40/144)"
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

      {/* Tab 6: Dual-Model Audit Lab */}
      {tab === "audit" && (
        <section className="tab-pane">
          <AuditVisualizer />
        </section>
      )}
    </main>
  );
}
