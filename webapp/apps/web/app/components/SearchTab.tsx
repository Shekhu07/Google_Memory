"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { search, type SearchResult } from "@/lib/api";
import { EXAMPLES } from "@/lib/examples";
import { galleryIndex, placesOf, thingsOf, type Shelf } from "@/lib/explore";
import { allPhotos, type Gallery, type GalleryPhoto } from "@/lib/gallery";

/** The library's own search, shown honestly.
 *
 *  Typed queries run the real `baseline` mode - plain CLIP over every photo, no
 *  episode grouping, no clue extraction - and not a keyword matcher written to
 *  fail. On the 30 evaluation tasks, over this 1,250-photo library, that path
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
export function SearchTab({
  gallery,
  onOpenTrails,
  onOpenPhoto,
}: {
  gallery: Gallery;
  onOpenTrails: (seed: string) => void;
  onOpenPhoto: (photos: GalleryPhoto[], index: number) => void;
}) {
  const [q, setQ] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shelf, setShelf] = useState<Shelf | null>(null);
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

  async function run(text: string) {
    const query = text.trim();
    if (!query) return;
    setShelf(null);
    const seq = ++latest.current;
    setBusy(true);
    setError(null);
    try {
      const res = await search(query, {}, "baseline", []);
      if (seq !== latest.current) return;
      setResult(res);
    } catch {
      if (seq !== latest.current) return;
      // Drop the old grid too: leaving it up captions one query's photos with
      // another query's words.
      setResult(null);
      setError("Search didn’t respond. You can still start from what you remember.");
    } finally {
      if (seq === latest.current) setBusy(false);
    }
  }

  // Search returns {id, file}; the manifest supplies the date, place and credit
  // the viewer shows. A file the manifest lacks cannot be opened, so it is dropped.
  const photos: GalleryPhoto[] = result
    ? result.episodes.flatMap((e) => e.photos).map((p) => byFile.get(p.file)).filter((p): p is GalleryPhoto => !!p)
    : [];

  if (shelf) {
    return (
      <ShelfView
        shelf={shelf}
        onBack={() => setShelf(null)}
        onOpen={(i) => onOpenPhoto(shelf.photos, i)}
        onOpenTrails={onOpenTrails}
      />
    );
  }

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
          onChange={(e) => {
            setQ(e.target.value);
            if (!e.target.value) setResult(null);
          }}
          placeholder="Search your photos"
          aria-label="Search your photos"
          type="search"
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
            Top {photos.length} match{photos.length === 1 ? "" : "es"} from {thousands(gallery.count)} photos
          </p>
          <div className="grid" role="group" aria-label={`${photos.length} search results`}>
            {photos.map((p, i) => (
              <button key={p.i} className="cell" onClick={() => onOpenPhoto(photos, i)} aria-label={`Open result ${i + 1}`}>
                <img src={`/${p.f}`} alt={p.t} loading="lazy" decoding="async" />
              </button>
            ))}
          </div>
        </>
      )}

      {!result && !busy && (
        <>
          <section className="explore" aria-labelledby="places-h">
            <h2 id="places-h" className="explore-h">Places</h2>
            <div className="places-row">
              {places.map((s) => (
                <button key={s.name} className="place" onClick={() => setShelf(s)}>
                  <img src={`/${s.cover.f}`} alt="" loading="lazy" decoding="async" />
                  <span>{s.name}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="explore" aria-labelledby="things-h">
            <h2 id="things-h" className="explore-h">Things</h2>
            <div className="things-grid">
              {(allThings ? things : things.slice(0, 9)).map((s) => (
                <button key={s.name} className="thing" onClick={() => setShelf(s)}>
                  <img src={`/${s.cover.f}`} alt="" loading="lazy" decoding="async" />
                  <span>{s.name}</span>
                </button>
              ))}
            </div>
            {things.length > 9 && (
              <button className="btn ghost show-all" onClick={() => setAllThings((v) => !v)}>
                {allThings ? "Show fewer" : `View all ${things.length}`}
              </button>
            )}
          </section>
        </>
      )}
    </>
  );
}

/** "1250" -> "1,250", identically on the server and in every browser. */
function thousands(n: number): string {
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/** One place or thing: every photo tagged with it, newest first. */
function ShelfView({
  shelf,
  onBack,
  onOpen,
  onOpenTrails,
}: {
  shelf: Shelf;
  onBack: () => void;
  onOpen: (index: number) => void;
  onOpenTrails: (seed: string) => void;
}) {
  const many = shelf.photos.length > 60;
  return (
    <>
      <header className="shelf-bar">
        <button className="viewer-icon dark" onClick={onBack} aria-label="Back to search">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M15 5l-7 7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        <div>
          <h2 className="shelf-title">{shelf.name}</h2>
          <p className="t-support">{thousands(shelf.photos.length)} photos</p>
        </div>
      </header>
      {/* Browsing a big shelf is the old way back in; the handoff offers the new one. */}
      {many && (
        <p className="t-support shelf-note">
          Looking for one moment in here?{" "}
          <button className="linklike" onClick={() => onOpenTrails(shelf.kind === "place" ? shelf.name : "")}>
            Start with what you remember
          </button>
        </p>
      )}
      <div className="grid" role="group" aria-label={`${shelf.name}, ${shelf.photos.length} photos`}>
        {shelf.photos.map((p, i) => (
          <button key={p.i} className="cell" onClick={() => onOpen(i)} aria-label={`Open photo ${i + 1}`}>
            <img src={`/${p.f}`} alt={p.t} loading={i < 12 ? "eager" : "lazy"} decoding="async" />
          </button>
        ))}
      </div>
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
      <h2 className="t-section">{scored ? "Didn’t find the right photo?" : "Can’t describe it?"}</h2>
      {scored ? (
        <p className="t-support">
          Keywords don’t always capture how we remember moments. Try searching by what you
          recall — like a rough timeframe, a place, or who was there.
        </p>
      ) : (
        <p className="t-support">
          Start from the moment instead of the words — a place, a rough time, or who you were with.
        </p>
      )}
      <button className="btn primary" onClick={() => onOpenTrails(seed)}>
        Start with what you remember
      </button>
    </section>
  );
}
