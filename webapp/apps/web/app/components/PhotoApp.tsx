"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BottomNav, type Tab } from "@/app/components/BottomNav";
import { Disclaimer } from "@/app/components/Disclaimer";
import { FastScroller } from "@/app/components/FastScroller";
import { GalleryGrid } from "@/app/components/GalleryGrid";
import { MemoryTrails } from "@/app/components/MemoryTrails";
import { SearchBar } from "@/app/components/SearchBar";
import { SearchTab } from "@/app/components/SearchTab";
import { Viewer } from "@/app/components/Viewer";
import { allPhotos, type Gallery, type GalleryPhoto } from "@/lib/gallery";

export function PhotoApp({ gallery }: { gallery: Gallery }) {
  const [tab, setTab] = useState<Tab>("photos");
  const [trails, setTrails] = useState<{ seed: string } | null>(null);
  const [viewer, setViewer] = useState<{ photos: GalleryPhoto[]; start: number } | null>(null);
  const pushed = useRef(false);
  const timeline = useRef<HTMLDivElement>(null);
  const all = useMemo(() => allPhotos(gallery), [gallery]);
  const openPhoto = useCallback((photos: GalleryPhoto[], start: number) => setViewer({ photos, start }), []);
  const closeViewer = useCallback(() => setViewer(null), []);

  // Back closes the sheet instead of leaving the page. pushState with no URL
  // argument leaves the address bar untouched, which matters: the interface
  // promises nothing is saved, and a typed memory in the URL would contradict
  // that in history, in a screen-share and in a screenshot.
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
   *  the stack with nothing listening: the next Back press would do nothing
   *  visible, and every open/close cycle would add another dead press. Going
   *  through history.back() lets the popstate handler do the closing. */
  function closeSheet() {
    if (pushed.current) history.back();
    else setTrails(null);
  }

  return (
    <>
      {/* Kept mounted behind the sheet, so closing it restores the exact scroll
          position. `inert` takes it out of the tab order and the a11y tree. */}
      <div className="tabview" inert={trails || viewer ? true : undefined}>
        <header className="app-bar">
          <h1>Photos</h1>
        </header>
        {tab === "photos" ? (
          <>
            <SearchBar onFocusSearch={() => setTab("search")} />
            <div className="timeline-wrap">
              <div className="phone-scroll" ref={timeline}>
                <GalleryGrid gallery={gallery} onOpen={(i) => openPhoto(all, i)} />
                <Disclaimer />
              </div>
              <FastScroller target={timeline} />
            </div>
          </>
        ) : (
          <div className="phone-scroll search-pane">
            <SearchTab
              gallery={gallery}
              onOpenTrails={(seed) => setTrails({ seed })}
              onOpenPhoto={openPhoto}
            />
            <Disclaimer />
          </div>
        )}
        <BottomNav tab={tab} onTab={setTab} />
      </div>

      {viewer && <Viewer photos={viewer.photos} start={viewer.start} onClose={closeViewer} />}

      {trails && (
        <MemoryTrails initialText={trails.seed} onExit={closeSheet} />
      )}
    </>
  );
}
