import { byDay, JustifiedGrid } from "@/app/components/JustifiedGrid";
import { Icon, type IconName } from "@/app/components/Icons";
import { thousands } from "@/app/components/SearchView";
import type { Shelf } from "@/lib/explore";
import { dayLabel, type GalleryPhoto } from "@/lib/gallery";

const CATEGORY_ICONS: Record<string, IconName> = {
  documents: "documents",
  screenshots: "screenshots",
  pets: "pets",
  places: "places",
};

/** Cards for a set of shelves - albums or places - newest or largest first. */
export function ShelfCards({
  title,
  shelves,
  onShelf,
  subtitle,
}: {
  title: string;
  shelves: Shelf[];
  onShelf: (s: Shelf) => void;
  subtitle?: (s: Shelf) => string;
}) {
  return (
    <div className="view">
      <h1 className="view-title">{title}</h1>
      <div className="cards">
        {shelves.map((s) => (
          <button key={s.name} className="card" onClick={() => onShelf(s)}>
            <img src={`/${s.cover.f}`} alt="" loading="lazy" decoding="async" />
            <span className="card-title">{s.name}</span>
            <span className="card-sub">{subtitle ? subtitle(s) : `${thousands(s.photos.length)} items`}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

/** An album's subtitle: its size and when it happened. */
export function albumSubtitle(s: Shelf): string {
  const newest = s.photos[0]?.d ?? "";
  const oldest = s.photos[s.photos.length - 1]?.d ?? "";
  const when = dayLabel(oldest).split(", ")[1] ?? "";
  const span = oldest.slice(0, 10) === newest.slice(0, 10) ? when : `from ${when}`;
  return `${s.photos.length} items · ${span}`;
}

/** One place, thing, album or collection: every photo in it, grouped by day. */
export function ShelfView({
  shelf,
  width,
  onBack,
  onOpen,
  onOpenTrails,
}: {
  shelf: Shelf;
  width: number;
  onBack: () => void;
  onOpen: (photos: GalleryPhoto[], index: number) => void;
  onOpenTrails: (seed: string) => void;
}) {
  const many = shelf.photos.length > 60;
  return (
    <div className="view">
      <header className="shelf-bar">
        <button className="icon-btn" onClick={onBack} aria-label="Back">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M15 5l-7 7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        <div>
          <h1 className="view-title flush">{shelf.name}</h1>
          <p className="t-support">{thousands(shelf.photos.length)} items</p>
        </div>
      </header>
      {/* Browsing a big shelf is the old way back in; this offers the new one. */}
      {many && (
        <p className="t-support shelf-note">
          Looking for one moment in here?{" "}
          <button className="linklike" onClick={() => onOpenTrails(shelf.kind === "place" ? shelf.name : "")}>
            Start with what you remember
          </button>
        </p>
      )}
      <JustifiedGrid
        groups={byDay(shelf.photos)}
        width={width}
        eager={12}
        onOpen={(i) => onOpen(shelf.photos, i)}
      />
    </div>
  );
}

/** Phones have no sidebar, so Collections gets its own tab listing what the
 *  sidebar holds on a desktop. */
export function CollectionsHub({
  entries,
  albums,
  onShelf,
}: {
  entries: { key: string; name: string; count: number; onOpen: () => void }[];
  albums: Shelf[];
  onShelf: (s: Shelf) => void;
}) {
  return (
    <div className="view collections-view">
      <h1 className="view-title">Collections</h1>
      <div className="collections-grid">
        {entries.map((e) => (
          <button key={e.key} className={`category-tile cat-${e.key}`} onClick={e.onOpen}>
            <div className="category-tile-icon">
              <Icon name={CATEGORY_ICONS[e.key] ?? "albums"} size={22} />
            </div>
            <div className="category-tile-text">
              <span className="category-tile-title">{e.name}</span>
              <span className="category-tile-count">{thousands(e.count)}</span>
            </div>
          </button>
        ))}
      </div>
      <h2 className="explore-h">Albums</h2>
      <div className="cards">
        {albums.map((s) => (
          <button key={s.name} className="card" onClick={() => onShelf(s)}>
            <img src={`/${s.cover.f}`} alt="" loading="lazy" decoding="async" />
            <span className="card-title">{s.name}</span>
            <span className="card-sub">{albumSubtitle(s)}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
