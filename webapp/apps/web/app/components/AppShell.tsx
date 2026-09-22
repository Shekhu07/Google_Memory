"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { albumSubtitle, CollectionsHub, ShelfCards, ShelfView } from "@/app/components/Collections";
import { Disclaimer } from "@/app/components/Disclaimer";
import { FastScroller } from "@/app/components/FastScroller";
import { Icon, type IconName } from "@/app/components/Icons";
import { MemoryTrails } from "@/app/components/MemoryTrails";
import { SearchView, thousands } from "@/app/components/SearchView";
import { Timeline } from "@/app/components/Timeline";
import { Viewer } from "@/app/components/Viewer";
import { albumsOf, collectionOf, placesOf, type Shelf } from "@/lib/explore";
import { allPhotos, type Gallery, type GalleryPhoto } from "@/lib/gallery";

type View =
  | { k: "photos" }
  | { k: "search" }
  | { k: "albums" }
  | { k: "places" }
  | { k: "collections" }
  | { k: "shelf"; shelf: Shelf; back: View };

const ENGINE_URL = "https://retrieval-discovery-engine.vercel.app";

/** The library, laid out as the Photos web app is: a sidebar of collections, a
 *  search pill across the top and the photos on a rounded panel. Below 900px the
 *  sidebar becomes a bottom tab bar. The Memory Trails flow opens over all of it
 *  and hands back the exact scroll position when it closes. */
export function AppShell({ gallery }: { gallery: Gallery }) {
  const [view, setView] = useState<View>({ k: "photos" });
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState("");
  const [trails, setTrails] = useState<{ seed: string } | null>(null);
  const [viewer, setViewer] = useState<{ photos: GalleryPhoto[]; start: number } | null>(null);
  const [width, setWidth] = useState(1100);
  const pushed = useRef(false);
  const main = useRef<HTMLDivElement>(null);

  const all = useMemo(() => allPhotos(gallery), [gallery]);
  const albums = useMemo(() => albumsOf(all), [all]);
  const places = useMemo(() => placesOf(all), [all]);
  const documents = useMemo(() => collectionOf(all, "documents"), [all]);
  const screenshots = useMemo(() => collectionOf(all, "screenshots"), [all]);
  const pets = useMemo(() => collectionOf(all, "pets"), [all]);

  // One measurement for every grid. The server renders at the default width;
  // the first effect corrects it to the real panel.
  useEffect(() => {
    const el = main.current;
    if (!el) return;
    const measure = () => {
      const pad = parseFloat(getComputedStyle(el).paddingLeft) + parseFloat(getComputedStyle(el).paddingRight);
      setWidth(Math.max(240, Math.floor(el.clientWidth - pad)));
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Back closes the Memory Trails sheet instead of leaving the page. pushState
  // with no URL argument leaves the address bar untouched, which matters: the
  // interface promises nothing is saved, and a typed memory in the URL would
  // contradict that in history, in a screen-share and in a screenshot.
  useEffect(() => {
    if (!trails) return;
    history.pushState({ trails: 1 }, "");
    pushed.current = true;
    const onPop = () => {
      pushed.current = false;
      setTrails(null);
    };
    addEventListener("popstate", onPop);
    return () => removeEventListener("popstate", onPop);
  }, [trails]);

  /** Closing from the UI has to pop the entry the effect pushed, or it stays on
   *  the stack with nothing listening. */
  function closeSheet() {
    if (pushed.current) history.back();
    else setTrails(null);
  }

  const openPhoto = useCallback((photos: GalleryPhoto[], start: number) => setViewer({ photos, start }), []);
  const closeViewer = useCallback(() => setViewer(null), []);
  const openTrails = useCallback((seed: string) => setTrails({ seed }), []);

  function go(next: View) {
    setView(next);
    main.current?.scrollTo({ top: 0 });
  }
  const openShelf = (shelf: Shelf) => go({ k: "shelf", shelf, back: view });
  function runSearch(q: string) {
    setDraft(q);
    setQuery(q);
    go({ k: "search" });
  }

  const nav: { key: string; label: string; icon: IconName; active: boolean; onClick: () => void; count?: number }[] = [
    { key: "photos", label: "Photos", icon: "photos", active: view.k === "photos", onClick: () => go({ k: "photos" }) },
    { key: "memory", label: "Find a memory", icon: "spark", active: false, onClick: () => openTrails("") },
  ];
  const isShelf = (s: Shelf) => view.k === "shelf" && view.shelf.name === s.name;
  const collections: typeof nav = [
    { key: "albums", label: "Albums", icon: "albums", active: view.k === "albums" || (view.k === "shelf" && view.back.k === "albums"), onClick: () => go({ k: "albums" }), count: albums.length },
    { key: "documents", label: "Documents", icon: "documents", active: isShelf(documents), onClick: () => openShelf(documents), count: documents.photos.length },
    { key: "screenshots", label: "Screenshots", icon: "screenshots", active: isShelf(screenshots), onClick: () => openShelf(screenshots), count: screenshots.photos.length },
    { key: "pets", label: "Pets", icon: "pets", active: isShelf(pets), onClick: () => openShelf(pets), count: pets.photos.length },
    { key: "places", label: "Places", icon: "places", active: view.k === "places" || (view.k === "shelf" && view.back.k === "places"), onClick: () => go({ k: "places" }), count: places.length },
  ];

  return (
    <>
      <div className="app" inert={trails || viewer ? true : undefined}>
        <div className="brand">
          <span className="brand-mark" aria-hidden="true"><Icon name="photos" /></span>
          <span className="brand-name">Photos</span>
          <span className="brand-tag">Concept</span>
        </div>

        <form
          className="topsearch"
          role="search"
          onSubmit={(e) => {
            e.preventDefault();
            runSearch(draft);
          }}
        >
          <Icon name="search" />
          <input
            value={draft}
            onChange={(e) => {
              setDraft(e.target.value);
              if (!e.target.value) setQuery("");
            }}
            onFocus={() => view.k !== "search" && go({ k: "search" })}
            placeholder="Search your photos"
            aria-label="Search your photos"
            type="search"
          />
        </form>

        <div className="topicons">
          <a className="icon-btn" href={ENGINE_URL} target="_blank" rel="noreferrer" aria-label="About this prototype: the research behind it" title="About this prototype">
            <Icon name="help" />
          </a>
        </div>

        <nav className="sidebar" aria-label="Library">
          {nav.map(({ key, ...n }) => (
            <NavItem key={key} {...n} />
          ))}
          <p className="sidebar-h">Collections</p>
          {collections.map(({ key, ...n }) => (
            <NavItem key={key} {...n} />
          ))}
          <div className="sidebar-foot">
            <p className="t-support">{thousands(gallery.count)} photos · all Creative Commons</p>
            <Disclaimer />
          </div>
        </nav>

        <main className="lib-panel" ref={main}>
          {view.k === "photos" && <Timeline gallery={gallery} width={width} onOpen={(i) => openPhoto(all, i)} />}
          {view.k === "search" && (
            <SearchView
              gallery={gallery}
              query={query}
              width={width}
              onQuery={runSearch}
              onShelf={openShelf}
              onOpenTrails={openTrails}
              onOpenPhoto={openPhoto}
            />
          )}
          {view.k === "albums" && <ShelfCards title="Albums" shelves={albums} onShelf={openShelf} subtitle={albumSubtitle} />}
          {view.k === "places" && <ShelfCards title="Places" shelves={places} onShelf={openShelf} />}
          {view.k === "collections" && (
            <CollectionsHub
              entries={collections.filter((c) => c.key !== "albums").map((c) => ({ key: c.key, name: c.label, count: c.count ?? 0, onOpen: c.onClick }))}
              albums={albums}
              onShelf={openShelf}
            />
          )}
          {view.k === "shelf" && (
            <ShelfView
              shelf={view.shelf}
              width={width}
              onBack={() => go(view.back)}
              onOpen={openPhoto}
              onOpenTrails={openTrails}
            />
          )}
          <div className="lib-foot">
            <Disclaimer />
          </div>
        </main>
        {view.k === "photos" && <FastScroller target={main} />}

        <nav className="tabbar" aria-label="Library">
          <TabButton label="Photos" icon="photos" active={view.k === "photos"} onClick={() => go({ k: "photos" })} />
          <TabButton
            label="Collections"
            icon="albums"
            active={view.k === "collections" || view.k === "albums" || view.k === "places" || view.k === "shelf"}
            onClick={() => go({ k: "collections" })}
          />
          <TabButton label="Search" icon="search" active={view.k === "search"} onClick={() => go({ k: "search" })} />
        </nav>
      </div>

      {viewer && <Viewer photos={viewer.photos} start={viewer.start} onClose={closeViewer} />}
      {trails && <MemoryTrails initialText={trails.seed} onExit={closeSheet} />}
    </>
  );
}

function NavItem({ label, icon, active, onClick }: { label: string; icon: IconName; active: boolean; onClick: () => void }) {
  return (
    <button className={`nav-item${active ? " active" : ""}`} onClick={onClick} aria-current={active ? "page" : undefined}>
      <Icon name={icon} />
      <span>{label}</span>
    </button>
  );
}

function TabButton({ label, icon, active, onClick }: { label: string; icon: IconName; active: boolean; onClick: () => void }) {
  return (
    <button className={active ? "active" : ""} onClick={onClick} aria-current={active ? "page" : undefined}>
      <span className="tab-pill"><Icon name={icon} /></span>
      {label}
    </button>
  );
}
