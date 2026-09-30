"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { JustifiedGrid } from "@/app/components/JustifiedGrid";
import { search, type SearchResult } from "@/lib/api";
import { EXAMPLES } from "@/lib/examples";
import { galleryIndex, placesOf, thingsOf, type Shelf } from "@/lib/explore";
import { allPhotos, type Gallery, type GalleryPhoto } from "@/lib/gallery";

/** The library's own search, shown honestly.
 *
 *  Typed queries run the real `baseline` mode - plain CLIP over every photo, no
 *  episode grouping, no clue extraction - and not a keyword matcher written to
 *  fail. On the 30 evaluation tasks, over this 1,282-photo library, that path
 *  puts the right photo in the top 20 1.2% of the time and ranks it first 0% of
 *  the time, so the failure a visitor watches is the failure the report measured.
 *
 *  Places and Things are shown at full strength, as the Photos app offers them:
 *  every photo tagged with that place or category. That is the incumbent's real
 *  capability, and the case is stronger for showing it - browsing "Bengaluru"
 *  means scrolling 580 photos, which is the problem, not a strawman of it.
 *
 *  Caveat worth keeping in mind: /search groups before returning, so flattening
 *  recovers exactly the top-20 set (what recall@20 scores) but not its internal
 *  rank order - groups are ordered by usefulness. The alternative, per-photo
 *  scores, is ruled out by the design rule against exposing false precision.
 */
export function SearchView({
  gallery,
  query,
  width,
  onQuery,
  onShelf,
  onOpenTrails,
  onOpenPhoto,
}: {
  gallery: Gallery;
  query: string;
  width: number;
  onQuery: (q: string) => void;
  onShelf: (s: Shelf) => void;
  onOpenTrails: (seed: string) => void;
  onOpenPhoto: (photos: GalleryPhoto[], index: number) => void;
}) {
  const [result, setResult] = useState<SearchResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [allThings, setAllThings] = useState(false);

  const all = useMemo(() => allPhotos(gallery), [gallery]);
  const byFile = useMemo(() => galleryIndex(gallery), [gallery]);
  const places = useMemo(() => placesOf(all), [all]);
  const things = useMemo(() => thingsOf(all), [all]);

  // Warms the function instance: module import, numpy/onnxruntime and the index
  // load here. It does NOT build the text encoder - /health only inspects the
  // lru_cache (`encoder.cache_info()`), and encoder() is called first inside
  // do_search, by design. The first real query still pays for the model.
  useEffect(() => {
    void fetch("/api/py/health").catch(() => {});
  }, []);

  // The first query after a cold start is slow by design, so a second one can
  // easily overtake it. Only the newest request may write.
  const latest = useRef(0);

  useEffect(() => {
    const q = query.trim();
    const seq = ++latest.current;
    if (!q) {
      setResult(null);
      setError(null);
      setBusy(false);
      return;
    }
    setBusy(true);
    setError(null);
    search(q, {}, "baseline", [])
      .then((res) => {
        if (seq === latest.current) setResult(res);
      })
      .catch(() => {
        if (seq !== latest.current) return;
        // Drop the old grid too: leaving it up captions one query's photos with
        // another query's words.
        setResult(null);
        setError("Search didn’t respond. You can still start from what you remember.");
      })
      .finally(() => {
        if (seq === latest.current) setBusy(false);
      });
  }, [query]);

  // Search returns {id, file}; the manifest supplies the date, place and credit
  // the viewer shows. A file the manifest lacks cannot be opened, so it is dropped.
  const photos: GalleryPhoto[] = result
    ? result.episodes.flatMap((e) => e.photos).map((p) => byFile.get(p.file)).filter((p): p is GalleryPhoto => !!p)
    : [];
  const searched = !!query.trim();

  return (
    <div className="view search-view">
      {busy && (
        <div className="skeleton" aria-live="polite">
          <div /><div /><div />
        </div>
      )}

      {error && <p className="t-support search-note">{error}</p>}

      {/* Before any query as well as after one, so the way forward exists even
          if the service is slow or down. */}
      <Handoff seed={query} scored={!!result} onOpenTrails={onOpenTrails} />

      {result && !busy && (
        <>
          <p className="t-support search-note" aria-live="polite">
            Top {photos.length} match{photos.length === 1 ? "" : "es"} for “{query}” from{" "}
            {thousands(gallery.count)} photos
          </p>
          <JustifiedGrid
            groups={[{ label: "", items: photos }]}
            width={width}
            labels={false}
            onOpen={(i) => onOpenPhoto(photos, i)}
          />
        </>
      )}

      {!searched && (
        <>
          <section className="explore" aria-labelledby="places-h">
            <h2 id="places-h" className="explore-h">Places</h2>
            <div className="places-row">
              {places.map((s) => (
                <button key={s.name} className="place" onClick={() => onShelf(s)}>
                  <img src={`/${s.cover.f}`} alt="" loading="lazy" decoding="async" />
                  <span>{s.name}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="explore" aria-labelledby="things-h">
            <h2 id="things-h" className="explore-h">Things</h2>
            <div className="things-grid">
              {(allThings ? things : things.slice(0, width < 600 ? 9 : 12)).map((s) => (
                <button key={s.name} className="thing" onClick={() => onShelf(s)}>
                  <img src={`/${s.cover.f}`} alt="" loading="lazy" decoding="async" />
                  <span>{s.name}</span>
                </button>
              ))}
            </div>
            {!allThings && (
              <button className="btn ghost show-all" onClick={() => setAllThings(true)}>
                View all {things.length}
              </button>
            )}
          </section>

          <section className="explore" aria-labelledby="try-h">
            <h2 id="try-h" className="explore-h">Try a memory like</h2>
            <div className="examples">
              {EXAMPLES.map((ex) => (
                <button key={ex} className="example" onClick={() => onQuery(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

/** "1250" -> "1,250", identically on the server and in every browser. */
export function thousands(n: number): string {
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
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
      <div>
        <h2 className="t-section">{scored ? "Didn’t find the right photo?" : "Can’t describe it?"}</h2>
        {scored ? (
          <p className="t-support">
            Keywords don’t always capture how we remember moments. Try searching by what you
            recall — like a rough timeframe, a place, or what you&rsquo;d have seen — a colour, what someone wore.
          </p>
        ) : (
          <p className="t-support">
            Describe the moment, not the photo — what was happening, roughly when, what you&rsquo;d have seen — a colour, what someone wore.
            A visual way to revisit a memory when a keyword or a conversational answer is not enough.
          </p>
        )}
      </div>
      <button className="btn primary" onClick={() => onOpenTrails(seed)}>
        Find a memory
      </button>
    </section>
  );
}
