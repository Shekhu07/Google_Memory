"use client";

import { useEffect, useState } from "react";
import { BottomNav, type Tab } from "@/app/components/BottomNav";
import { GalleryGrid } from "@/app/components/GalleryGrid";
import { MemoryTrails } from "@/app/components/MemoryTrails";
import { SearchBar } from "@/app/components/SearchBar";
import { SearchTab } from "@/app/components/SearchTab";
import type { Gallery } from "@/lib/gallery";

export function PhotoApp({ gallery }: { gallery: Gallery }) {
  const [tab, setTab] = useState<Tab>("photos");
  const [trails, setTrails] = useState<{ seed: string } | null>(null);

  // Back closes the sheet instead of leaving the page. pushState with no URL
  // argument leaves the address bar untouched, which matters: the interface
  // promises nothing is saved, and a typed memory in the URL would contradict
  // that in history, in a screen-share and in a screenshot.
  useEffect(() => {
    if (!trails) return;
    history.pushState({ trails: 1 }, "");
    const onPop = () => setTrails(null);
    addEventListener("popstate", onPop);
    return () => removeEventListener("popstate", onPop);
  }, [trails]);

  return (
    <>
      {/* Kept mounted behind the sheet, so closing it restores the exact scroll
          position. `inert` takes it out of the tab order and the a11y tree. */}
      <div className="tabview" inert={trails ? true : undefined}>
        <header className="app-bar">
          <h1>Photos</h1>
        </header>
        {tab === "photos" ? (
          <>
            <SearchBar onFocusSearch={() => setTab("search")} />
            <div className="phone-scroll">
              <GalleryGrid gallery={gallery} />
            </div>
          </>
        ) : (
          <div className="phone-scroll search-pane">
            <SearchTab onOpenTrails={(seed) => setTrails({ seed })} />
          </div>
        )}
        <BottomNav tab={tab} onTab={setTab} />
      </div>

      {trails && (
        <MemoryTrails initialText={trails.seed} onExit={() => setTrails(null)} />
      )}
    </>
  );
}
