"use client";

import { useState } from "react";
import { Masthead } from "@/app/components/Masthead";
import { DataTable } from "@/app/components/DataTable";
import { extract, type Chip } from "@/lib/api";
import evidence from "@/public/data/evidence.json";

type Tab = "try" | "problems" | "how";

export default function Evidence() {
  const [tab, setTab] = useState<Tab>("try");
  const [text, setText] = useState("");
  const [chips, setChips] = useState<Chip[] | null>(null);
  const [busy, setBusy] = useState(false);

  const specific = evidence.counts.specific;

  async function onRead() {
    if (!text.trim()) return;
    setBusy(true);
    try {
      setChips((await extract(text.trim())).chips);
    } catch {
      setChips([]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <Masthead here="evidence" />
      <div className="prose">
        <h1>Why people cannot find photos they remember</h1>
        <p>
          85,140 public posts were collected, screened and read into {evidence.counts.episodes} structured
          episodes, {specific} of them specific retrieval attempts. Every figure below is a share of {specific}
          unless it says otherwise.
        </p>
      </div>

      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "try"} onClick={() => setTab("try")}>Try a memory</button>
        <button role="tab" aria-selected={tab === "problems"} onClick={() => setTab("problems")}>Where retrieval breaks</button>
        <button role="tab" aria-selected={tab === "how"} onClick={() => setTab("how")}>How this was built</button>
      </div>

      {tab === "try" && (
        <section className="prose">
          <p>
            This runs the pipeline&rsquo;s own clue extractor on your sentence — the same code that read the{" "}
            {evidence.counts.episodes} episodes.
          </p>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="The medicine I took when I was sick, July 2025ish"
            maxLength={500}
            aria-label="A memory to read"
            style={{ width: "100%", minHeight: "4rem" }}
          />
          <div className="ask-row">
            <button className="primary" onClick={onRead} disabled={busy || !text.trim()}>
              {busy ? "Reading…" : "Read the clues"}
            </button>
          </div>
          {chips && (
            <div className="chips" style={{ marginTop: "1rem" }}>
              {chips.length === 0 ? <p>No clues found in that sentence.</p> : chips.map((c) => (
                <span className="chip" key={c.id}>
                  {c.label}
                  <span className="cue">{c.cue.replace(/_/g, " ")}</span>
                </span>
              ))}
            </div>
          )}
        </section>
      )}

      {tab === "problems" && (
        <section>
          <DataTable
            rows={evidence.failure_stages.map((r) => ({
              "failure stage": r.stage,
              count: r.count,
              "share of 144": `${(r.share * 100).toFixed(1)}%`,
            }))}
            caption={`Where retrieval broke down, across all ${specific} specific attempts`}
          />
          <DataTable rows={evidence.ranking} caption="Hypotheses scored by the pre-registered rule" />
          <DataTable rows={evidence.cues} caption="What people still remembered, and how those attempts ended" />
        </section>
      )}

      {tab === "how" && (
        <section>
          <DataTable rows={evidence.funnel} caption="From collected posts to scoreable attempts" />
          <div className="prose">
            <h2>What this evidence cannot show</h2>
            <ul>
              <li>Play Store is 86% of extracted episodes, over the plan&rsquo;s own 60% per-source cap.</li>
              <li>
                Two models read the same posts independently. They agree moderately on where retrieval broke
                (κ 0.509) and poorly on which hypothesis it supports (Jaccard 0.347), so the hypothesis ranking
                does not come from this engine.
              </li>
              <li>
                Code-mixed querying was never tested: the language field returned &ldquo;en&rdquo; for every
                post, so a zero there is silence, not evidence.
              </li>
              <li>Retrieval-rate baselines are modelled, not measured. There is no telemetry behind them.</li>
            </ul>
          </div>
        </section>
      )}
    </main>
  );
}
