"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { albumSubtitle, CollectionsHub, ShelfCards, ShelfView } from "@/app/components/Collections";
import { Disclaimer } from "@/app/components/Disclaimer";
import { FastScroller } from "@/app/components/FastScroller";
import { GeminiSpark, GooglePhotosLogo, Icon, type IconName } from "@/app/components/Icons";
import { MemoryTrails } from "@/app/components/MemoryTrails";
import { SearchView } from "@/app/components/SearchView";
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

/** The library as the Photos app lays it out: an app bar, the photos on a
 *  rounded panel, and tabs for Photos, Collections and Search. Full-bleed on a
 *  phone, framed on a desktop. The Memory Trails flow opens over it and hands
 *  back the exact scroll position when it closes. */
export function AppShell({ gallery }: { gallery: Gallery }) {
  const [view, setView] = useState<View>({ k: "photos" });
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState("");
  const [trails, setTrails] = useState<{ seed: string } | null>(null);
  const [viewer, setViewer] = useState<{ photos: GalleryPhoto[]; start: number } | null>(null);
  const [studyId, setStudyId] = useState<string | null>(null);
  const [copiedLog, setCopiedLog] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [theme, setTheme] = useState<"system" | "light" | "dark">("system");
  const [width, setWidth] = useState(378);

  function toggleTheme() {
    const isDark =
      document.documentElement.getAttribute("data-theme") === "dark" ||
      (!document.documentElement.getAttribute("data-theme") &&
        typeof window !== "undefined" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);
    const next = isDark ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
  }
  const pushed = useRef(false);
  const main = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const s = params.get("study");
      if (s) {
        setStudyId(s);
        import("@/lib/track").then((m) => m.setStudyParticipant(s));
      }
    }
  }, []);

  const all = useMemo(() => allPhotos(gallery), [gallery]);
  const albums = useMemo(() => albumsOf(all), [all]);
  const places = useMemo(() => placesOf(all), [all]);
  const documents = useMemo(() => collectionOf(all, "documents"), [all]);
  const screenshots = useMemo(() => collectionOf(all, "screenshots"), [all]);
  const pets = useMemo(() => collectionOf(all, "pets"), [all]);

  // One measurement for every grid. The server renders at the default width -
  // the panel inside a 390px phone less its padding, so the first paint on a
  // phone already has the right rows - and the first effect corrects it.
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

  // The Collections tab's rows, top to bottom. Albums get their own cards below.
  const collections = [
    { key: "documents", label: "Documents", onClick: () => openShelf(documents), count: documents.photos.length },
    { key: "screenshots", label: "Screenshots", onClick: () => openShelf(screenshots), count: screenshots.photos.length },
    { key: "pets", label: "Pets", onClick: () => openShelf(pets), count: pets.photos.length },
    { key: "places", label: "Places", onClick: () => go({ k: "places" }), count: places.length },
  ];

  return (
    <div className="stage">
      <div className="phone">
        {/* Mobile status bar simulation for phone mockup on desktop */}
        <div className="phone-status-bar" aria-hidden="true">
          <span className="status-time">9:41</span>
          <span className="dynamic-island" />
          <div className="status-icons">
            <svg width="15" height="11" viewBox="0 0 17 11" fill="currentColor">
              <path d="M1 9h2V2H1v7zm4 0h2V0H5v9zm4 0h2V4H9v5zm4 0h2V6h-2v3z" />
            </svg>
            <svg width="15" height="11" viewBox="0 0 15 11" fill="currentColor">
              <path d="M7.5 3a7.48 7.48 0 0 1 5.3 2.2l-1.4 1.4A5.48 5.48 0 0 0 7.5 5c-1.5 0-2.9.6-4 1.6L2.1 5.2A7.48 7.48 0 0 1 7.5 3zm0 4c1.1 0 2.1.4 2.8 1.2L7.5 11 4.7 8.2A3.98 3.98 0 0 1 7.5 7z" />
            </svg>
            <span className="battery-pill">
              <span className="battery-level" />
            </span>
          </div>
        </div>

        {studyId && (
          <aside className="study-bar" aria-label="Study Mode Controls">
            <span className="study-badge">Study: <strong>{studyId}</strong></span>
            <button
              type="button"
              className="study-copy-btn"
              onClick={async () => {
                const { copySessionLog } = await import("@/lib/track");
                await navigator.clipboard.writeText(copySessionLog());
                setCopiedLog(true);
                setTimeout(() => setCopiedLog(false), 2000);
              }}
            >
              {copiedLog ? "✓ Copied Log" : "End session: copy log"}
            </button>
          </aside>
        )}
        <div className="app" inert={trails || viewer ? true : undefined}>
          <header className="appbar">
            <div className="brand">
              <GooglePhotosLogo size={28} />
              <span className="brand-name">Photos</span>
              <span className="brand-tag">Concept</span>
            </div>
            <button
              className="ask-photos-pill"
              onClick={() => openTrails("")}
              aria-label="Ask Photos or find a memory"
              title="Describe a memory with Memory Trails"
            >
              <GeminiSpark size={16} />
              <span className="ask-photos-text">Ask Photos</span>
            </button>
            <button
              className="profile-avatar-btn"
              onClick={() => setProfileOpen((v) => !v)}
              aria-label="Account information and case study options"
              title="Account & Case Study Details"
            >
              <span className="avatar-circle">A</span>
            </button>
          </header>

          {/* Profile & Concept Modal */}
          {profileOpen && (
            <div className="profile-overlay" onClick={() => setProfileOpen(false)}>
              <div className="profile-sheet" onClick={(e) => e.stopPropagation()}>
                <div className="profile-header">
                  <div className="profile-avatar-lg">A</div>
                  <div>
                    <h3 className="profile-name">Google Photos Case Study</h3>
                    <p className="profile-email">Memory Trails Prototype · v2</p>
                  </div>
                  <button className="icon-btn close-profile" onClick={() => setProfileOpen(false)} aria-label="Close">
                    <Icon name="close" size={18} />
                  </button>
                </div>
                <div className="profile-storage">
                  <div className="storage-info">
                    <span>1,282 photos</span>
                    <span className="storage-badge">Private &amp; On-device</span>
                  </div>
                  <div className="storage-track">
                    <div className="storage-fill" />
                  </div>
                </div>
                <div className="profile-menu">
                  <button className="profile-item" onClick={() => { setProfileOpen(false); openTrails(""); }}>
                    <GeminiSpark size={18} />
                    <span>Launch Memory Trails</span>
                  </button>
                  <a className="profile-item" href={ENGINE_URL} target="_blank" rel="noreferrer">
                    <Icon name="help" size={18} />
                    <span>Research &amp; Benchmark Data</span>
                  </a>
                  <a className="profile-item" href="/attribution">
                    <Icon name="photos" size={18} />
                    <span>Openverse Photo Credits</span>
                  </a>
                  <button className="profile-item" onClick={toggleTheme}>
                    <Icon name="sliders" size={18} />
                    <span>Theme: {theme === "dark" ? "Dark Mode 🌙" : "Light Mode ☀️"}</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Search lives on its own tab, as in the app, not above the library. */}
          {view.k === "search" && (
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
                placeholder="Search your photos"
                aria-label="Search your photos"
                type="search"
                autoFocus
              />
            </form>
          )}

          <main className="lib-panel" ref={main}>
            {view.k === "photos" && (
              <Timeline
                gallery={gallery}
                width={width}
                onOpen={(i) => openPhoto(all, i)}
                onOpenTrails={openTrails}
              />
            )}
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
                entries={collections.map((c) => ({ key: c.key, name: c.label, count: c.count ?? 0, onOpen: c.onClick }))}
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

          <div className="phone-home-indicator" aria-hidden="true" />
        </div>

        {/* Inside the frame, so on a desktop they open over the phone, not the page. */}
        {viewer && <Viewer photos={viewer.photos} start={viewer.start} onClose={closeViewer} />}
        {trails && <MemoryTrails initialText={trails.seed} onExit={closeSheet} />}
      </div>
      <Disclaimer />
    </div>
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
