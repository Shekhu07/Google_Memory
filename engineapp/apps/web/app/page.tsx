"use client";

import { useState } from "react";
import { DataTable } from "@/app/components/DataTable";
import { extract, type Chip } from "@/lib/api";
import evidence from "@/public/data/evidence.json";

type Tab = "try" | "remember" | "problems" | "how";

const MVP_URL = "https://memory-trails-demo.vercel.app";

export default function DiscoveryEngine() {
  const [tab, setTab] = useState<Tab>("try");
  const [text, setText] = useState("");
  const [result, setResult] = useState<{ chips: Chip[]; source: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  const specific = evidence.counts.specific;

  async function onRead() {
    if (!text.trim()) return;
    setBusy(true);
    setFailed(false);
    try {
      const r = await extract(text.trim());
      setResult({ chips: r.chips, source: r.source });
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <h2>Retrieval discovery engine</h2>
        <nav>
          <a href={MVP_URL}>See the MVP it led to →</a>
        </nav>
      </header>

      <div className="prose">
        <h1 className="t-page">Why people cannot find photos they remember</h1>
        <p>
          85,140 public posts from the Play Store, App Store, YouTube and Reddit, screened and read
          into <strong>{evidence.counts.episodes} structured episodes</strong>, {specific} of them
          specific retrieval attempts. Every episode was read twice, by two different model families.
        </p>
        <p>
          Shares are of {specific} unless stated. The workflow below is the extractor itself — run it
          on a sentence of your own.
        </p>
      </div>

      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "try"} onClick={() => setTab("try")}>
          Try the extractor
        </button>
        <button role="tab" aria-selected={tab === "remember"} onClick={() => setTab("remember")}>
          What people remember
        </button>
        <button role="tab" aria-selected={tab === "problems"} onClick={() => setTab("problems")}>
          Where retrieval breaks
        </button>
        <button role="tab" aria-selected={tab === "how"} onClick={() => setTab("how")}>
          How it works
        </button>
      </div>

      {tab === "try" && (
        <section className="prose">
          <p>
            This runs the pipeline&rsquo;s own extraction prompt on your sentence — the same code
            that read all {evidence.counts.episodes} episodes. Nothing you type is stored.
          </p>
          <textarea
            className="prompt"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="The medicine I took when I was sick, July 2025ish"
            maxLength={500}
            aria-label="A memory for the extractor to read"
          />
          <div className="actions">
            <button className="btn primary" onClick={onRead} disabled={busy || !text.trim()}>
              {busy ? "Reading…" : "Extract the clues"}
            </button>
          </div>

          {failed && <p className="t-support">The extractor did not respond. Try again in a moment.</p>}

          {result && (
            <>
              <p className="t-eyebrow" style={{ marginTop: 20 }}>
                Clues found {result.source === "rules" && "(rule-based fallback)"}
              </p>
              {result.chips.length === 0 ? (
                <p className="t-support">
                  No clues in that sentence. That is itself the finding: most real descriptions carry
                  one weak cue, usually an approximate time.
                </p>
              ) : (
                <div className="clues">
                  {result.chips.map((c) => (
                    <span className="clue" key={c.id}>
                      <span>{c.label}</span>
                      <span className="kind">{c.cue.replace(/_/g, " ")}</span>
                    </span>
                  ))}
                </div>
              )}
            </>
          )}
        </section>
      )}

      {tab === "remember" && (
        <section>
          <DataTable
            rows={evidence.asset_types.map((r) => ({
              "kind of photo": r.value, count: r.count, "share of 144": r.share,
            }))}
            caption="What kinds of old photos people struggle to retrieve"
          />
          <DataTable
            rows={evidence.cues.map((r) => ({
              "what they still remembered": r.cue,
              posts: r.posts,
              "ended badly": r["ended badly (of known outcomes)"],
              "most common failure": r["most common failure"],
            }))}
            caption="What information people actually remember about a photo"
          />
          <DataTable
            rows={evidence.cues_lost.map((r) => ({
              "what they had forgotten": r.value, count: r.count, "share of 144": r.share,
            }))}
            caption="What information they had forgotten"
          />
          <DataTable
            rows={evidence.search_modes.map((r) => ({
              "how they searched": r.value, count: r.count, "share of 144": r.share,
            }))}
            caption="How people formulate searches when memory is incomplete"
          />
          <p className="t-support">
            The headline: the most-retained cue is an approximate time (40 of 144), and the
            most-forgotten is the exact date (37). People remember roughly <em>when</em> — which is
            exactly what the index cannot use.
          </p>
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
        </section>
      )}

      {tab === "how" && (
        <section>
          <DataTable rows={evidence.funnel} caption="From collected posts to scoreable attempts" />
          <div className="prose">
            <h2 className="t-section">What this evidence cannot show</h2>
            <ul>
              <li>Play Store is 86% of extracted episodes, over the plan&rsquo;s own 60% per-source cap.</li>
              <li>
                Two model families read the same posts independently. They agree moderately on where
                retrieval broke (κ 0.509) and poorly on which hypothesis it supports (Jaccard 0.347),
                so <strong>the hypothesis ranking does not come from this engine</strong>.
              </li>
              <li>
                Code-mixed querying was never tested: the language field returned &ldquo;en&rdquo; for
                every post, so a zero there is silence, not evidence.
              </li>
              <li>Retrieval-rate baselines are modelled, not measured. There is no telemetry behind them.</li>
              <li>Extraction was closed deliberately at 720 of 819 relevant posts, once the budget bound.</li>
            </ul>
          </div>
        </section>
      )}
    </main>
  );
}
