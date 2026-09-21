"use client";

import { useEffect, useState } from "react";
import { search, type SearchResult } from "@/lib/api";
import { EXAMPLES } from "@/lib/examples";

/** The library's own search, shown honestly.
 *
 *  This runs the real `baseline` mode - plain CLIP over every photo, no episode
 *  grouping, no clue extraction - and not a keyword matcher written to fail. On
 *  the 30 evaluation tasks that path puts the right photo in the top 20 5.3% of
 *  the time and ranks it first 0% of the time, so the failure a visitor watches
 *  here is the failure the report measured.
 *
 *  Caveat worth keeping in mind: /search groups before returning, so flattening
 *  recovers exactly the top-20 set (what recall@20 scores) but not its internal
 *  rank order - groups are ordered by usefulness. The alternative, per-photo
 *  scores, is ruled out by the design rule against exposing false precision.
 */
export function SearchTab({ onOpenTrails }: { onOpenTrails: (seed: string) => void }) {
  const [q, setQ] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // The retrieval function loads a 126 MB sharded encoder on first use. Paying
  // the cold start now keeps it off the visitor's first query.
  useEffect(() => {
    void fetch("/api/py/health").catch(() => {});
  }, []);

  async function run(text: string) {
    const query = text.trim();
    if (!query) return;
    setBusy(true);
    setError(null);
    try {
      setResult(await search(query, {}, "baseline", []));
    } catch {
      setError("Search didn’t respond. You can still start from what you remember.");
    } finally {
      setBusy(false);
    }
  }

  const photos = result ? result.episodes.flatMap((e) => e.photos) : [];

  return (
    <>
      <form
        className="searchbar"
        onSubmit={(e) => {
          e.preventDefault();
          void run(q);
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search your photos"
          aria-label="Search your photos"
          autoFocus
        />
      </form>

      {busy && (
        <div className="skeleton" aria-live="polite">
          <div /><div /><div />
        </div>
      )}

      {error && <p className="t-support search-note">{error}</p>}

      {!result && !busy && (
        <div className="search-empty">
          <p className="t-eyebrow">Try a memory like</p>
          <div className="examples">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                className="example"
                onClick={() => {
                  setQ(ex);
                  void run(ex);
                }}
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Before any query as well as after one, so the way forward exists even
          if the service is slow or down. */}
      <Handoff seed={q} scored={!!result} onOpenTrails={onOpenTrails} />

      {result && !busy && (
        <>
          <p className="t-support search-note" aria-live="polite">
            Top {photos.length} match{photos.length === 1 ? "" : "es"} from 494 photos
          </p>
          <div className="grid">
            {photos.map((p) => (
              <img key={p.id} src={`/${p.file}`} alt="" loading="lazy" decoding="async" />
            ))}
          </div>
        </>
      )}
    </>
  );
}

/** Placed above the results, not below them: this is the point of the demo, and
 *  a visitor who never scrolls past twenty thumbnails never finds it. */
function Handoff({
  seed,
  scored,
  onOpenTrails,
}: {
  seed: string;
  scored: boolean;
  onOpenTrails: (seed: string) => void;
}) {
  return (
    <section className="handoff">
      <h2 className="t-section">Can’t describe it?</h2>
      {scored ? (
        <p className="t-support">
          Plain search matched your words against every photo. On 30 test queries it put the right
          photo in the top 20 <strong>5.3%</strong> of the time, and ranked it first{" "}
          <strong>0%</strong> of the time.
        </p>
      ) : (
        <p className="t-support">
          Start from the moment instead of the words — a place, a rough time, who you were with.
        </p>
      )}
      <button className="btn primary" onClick={() => onOpenTrails(seed)}>
        Start with what you remember
      </button>
    </section>
  );
}
