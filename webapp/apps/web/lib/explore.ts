import type { Gallery, GalleryPhoto } from "@/lib/gallery";

/** Search-page collections, grouped the way the Photos app groups "Things": a
 *  handful of broad shelves rather than the library's 59 raw categories. A
 *  category missing from this list lands on an "Other" shelf rather than vanishing. */
export const THINGS: [string, string[]][] = [
  ["Food", ["food", "home food", "dal", "roti", "biryani", "dosa", "idli", "thali", "paneer",
    "samosa", "chaat", "paratha", "pav bhaji", "poha", "sweets"]],
  ["Landmarks & temples", ["landmark", "temple"]],
  ["Screenshots", ["screenshot"]],
  ["Receipts", ["receipt"]],
  ["Documents & notes", ["document", "notes"]],
  ["Beaches", ["beach"]],
  ["Mountains", ["mountain"]],
  ["Sky & rain", ["sky", "rain"]],
  ["Pets", ["pet"]],
  ["Festivals", ["festival", "holi", "ganesh", "kite", "rangoli", "puja"]],
  ["Weddings", ["wedding", "mehndi"]],
  ["Cafés", ["cafe"]],
  ["Tea & coffee", ["tea", "chai stall"]],
  ["Flowers & plants", ["flower", "plant"]],
  ["Friends & family", ["family", "friends"]],
  ["Work", ["desk", "whiteboard"]],
  ["Medicine", ["medicine"]],
  ["Streets & travel", ["street", "commute", "auto rickshaw", "railway", "parking"]],
  ["Shopping", ["shopping", "groceries", "product"]],
  ["At home", ["pressure cooker", "utensils", "matka"]],
  ["Sport & outdoors", ["cricket", "gym", "park"]],
  ["Books", ["book"]],
];

/** Scenic categories make the better cover for a place than its receipts. */
const COVER = ["landmark", "beach", "mountain", "temple", "sky", "street", "festival", "cafe", "wedding"];

export type Shelf = { name: string; kind: "place" | "thing"; cover: GalleryPhoto; photos: GalleryPhoto[] };

/** The library keeps 19th-century bills of sale for enslaved people among its
 *  "receipts" (a deliberate choice, 22 Sep). They may be found; they are never
 *  the picture on a shelf. */
const NEVER_COVER = /bill of sale|enslaved/i;

function cover(photos: GalleryPhoto[], preferScenic = true): GalleryPhoto {
  const ok = photos.filter((p) => !NEVER_COVER.test(p.t));
  const pool = ok.length ? ok : photos;
  if (preferScenic) {
    for (const c of COVER) {
      const hit = pool.find((p) => p.c === c);
      if (hit) return hit;
    }
  }
  return pool[0];
}

export function placesOf(all: GalleryPhoto[]): Shelf[] {
  const by = new Map<string, GalleryPhoto[]>();
  for (const p of all) if (p.p) by.set(p.p, [...(by.get(p.p) ?? []), p]);
  return [...by.entries()]
    .sort((a, b) => b[1].length - a[1].length)
    .map(([name, photos]) => ({ name, kind: "place", cover: cover(photos), photos }));
}

export function thingsOf(all: GalleryPhoto[]): Shelf[] {
  const shelfOf = new Map<string, string>();
  for (const [name, cats] of THINGS) for (const c of cats) shelfOf.set(c, name);
  const by = new Map<string, GalleryPhoto[]>();
  for (const p of all) {
    const name = shelfOf.get(p.c) ?? "Other";
    by.set(name, [...(by.get(name) ?? []), p]);
  }
  const order = [...THINGS.map(([n]) => n), "Other"];
  return order
    .filter((n) => by.has(n))
    .map((name) => {
      const photos = by.get(name)!;
      return { name, kind: "thing" as const, cover: cover(photos, false), photos };
    });
}

export function galleryIndex(gallery: Gallery): Map<string, GalleryPhoto> {
  return new Map(gallery.sections.flatMap((s) => s.photos).map((p) => [p.f, p]));
}

/** "goa trip" -> "Goa trip"; "friend's sangeet" -> "Friend's sangeet". */
export function titleCase(s: string): string {
  return s ? s[0].toUpperCase() + s.slice(1) : s;
}

/** The library's 25 episodes, shown as albums: newest first, each with its span. */
export function albumsOf(all: GalleryPhoto[]): Shelf[] {
  const by = new Map<string, GalleryPhoto[]>();
  for (const p of all) if (p.e) by.set(p.e, [...(by.get(p.e) ?? []), p]);
  return [...by.entries()]
    .sort((a, b) => (b[1][0].d > a[1][0].d ? 1 : -1))
    .map(([name, photos]) => ({ name: titleCase(name), kind: "thing" as const, cover: cover(photos), photos }));
}

/** Sidebar collections that are one query over categories. */
export const COLLECTIONS: Record<"documents" | "screenshots" | "pets", { name: string; cats: string[] }> = {
  documents: { name: "Documents", cats: ["document", "notes", "receipt", "whiteboard"] },
  screenshots: { name: "Screenshots", cats: ["screenshot"] },
  pets: { name: "Pets", cats: ["pet"] },
};

export function collectionOf(all: GalleryPhoto[], key: keyof typeof COLLECTIONS): Shelf {
  const { name, cats } = COLLECTIONS[key];
  const photos = all.filter((p) => cats.includes(p.c));
  return { name, kind: "thing", cover: cover(photos, false), photos };
}
