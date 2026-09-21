export type Tab = "photos" | "search";

/** Two tabs, not five. The library and the way into it are the only surfaces
 *  this case study needs; albums and sharing would be scope with no marks behind it. */
export function BottomNav({ tab, onTab }: { tab: Tab; onTab: (t: Tab) => void }) {
  return (
    <nav className="bottom-nav" aria-label="Library">
      <button onClick={() => onTab("photos")} aria-current={tab === "photos" ? "page" : undefined}>
        <PhotoGlyph />
        Photos
      </button>
      <button onClick={() => onTab("search")} aria-current={tab === "search" ? "page" : undefined}>
        <SearchGlyph />
        Search
      </button>
    </nav>
  );
}

/* Hand-written rather than an icon package: the app carries no UI library and
   two glyphs do not justify starting one. */
function PhotoGlyph() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="5" width="18" height="14" rx="3" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="8.5" cy="10" r="1.6" fill="currentColor" />
      <path d="M4 17l4.5-4.5L12 16l3-2.5 5 4.5" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    </svg>
  );
}

function SearchGlyph() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="11" cy="11" r="6.2" stroke="currentColor" strokeWidth="1.8" />
      <path d="M15.6 15.6L20 20" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
