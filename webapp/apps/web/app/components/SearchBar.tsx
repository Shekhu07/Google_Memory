"use client";

/** The Photos tab's search affordance. Tapping it switches to the Search tab,
 *  where SearchTab renders the real input - the same pill in both places, so
 *  tapping reads as focusing the thing you already saw. */
export function SearchBar({ onFocusSearch }: { onFocusSearch: () => void }) {
  return (
    <button className="searchbar" onClick={onFocusSearch}>
      <svg className="glyph" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="11" cy="11" r="6.2" stroke="currentColor" strokeWidth="1.8" />
        <path d="M15.6 15.6L20 20" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
      Search your photos
    </button>
  );
}
