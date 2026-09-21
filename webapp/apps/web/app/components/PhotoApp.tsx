"use client";

import { useEffect, useRef, useState } from "react";
import { BottomNav, type Tab } from "@/app/components/BottomNav";
import { Disclaimer } from "@/app/components/Disclaimer";
import { GalleryGrid } from "@/app/components/GalleryGrid";
import { MemoryTrails } from "@/app/components/MemoryTrails";
import { SearchBar } from "@/app/components/SearchBar";
import { SearchTab } from "@/app/components/SearchTab";
import type { Gallery } from "@/lib/gallery";

export function PhotoApp({ gallery }: { gallery: Gallery }) {
  const [tab, setTab] = useState<Tab>("photos");
  const [trails, setTrails] = useState<{ seed: string } | null>(null);
  const pushed = useRef(false);

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
      <div className="tabview" inert={trails ? true : undefined}>
        <header className="app-bar">
          <h1>Photos</h1>
        </header>
        {tab === "photos" ? (
          <>
            <SearchBar onFocusSearch={() => setTab("search")} />
            <div className="phone-scroll">
              <GalleryGrid gallery={gallery} />
              <Disclaimer />
            </div>
          </>
        ) : (
          <div className="phone-scroll search-pane">
            <SearchTab onOpenTrails={(seed) => setTrails({ seed })} />
            <Disclaimer />
          </div>
        )}
        <BottomNav tab={tab} onTab={setTab} />
      </div>

      {trails && (
        <MemoryTrails initialText={trails.seed} onExit={closeSheet} />
      )}
    </>
  );
}
