/** The committed manifest written by engine/export_web.py's build_gallery().
 *  Short keys because all 1,250 rows stream to the client as flight data. */
export type GalleryPhoto = {
  f: string; // servable path, library/0000.jpg
  t: string; // the creator's title on Openverse
  i: string; // library id, demo:0000
  d: string; // ISO date-time, synthetic
  p: string; // place
  v: string; // device
  c: string; // category
  a: string; // creator
  l: string; // licence, e.g. "by 2.0"
};
export type GallerySection = { month: string; label: string; photos: GalleryPhoto[] };
export type Gallery = { count: number; built: string; sections: GallerySection[] };

/* Hand-rolled rather than Intl: the grid renders on the server and again in the
   browser, and any locale or ICU difference between the two is a hydration error. */
const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
  "September", "October", "November", "December"];

function parts(iso: string) {
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  // UTC so the weekday cannot shift with the viewer's time zone.
  const weekday = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
  const hh = Number(iso.slice(11, 13)) || 0;
  const mm = iso.slice(14, 16) || "00";
  return { y, m, d, weekday, hh, mm };
}

/** Timeline day header: "Sat, 14 Jun 2025". The library ends in May 2026, so the
 *  year always shows - dropping it for "this year" would depend on the clock. */
export function dayLabel(iso: string): string {
  if (!iso) return "Undated";
  const { y, m, d, weekday } = parts(iso);
  return `${DAYS[weekday].slice(0, 3)}, ${d} ${MONTHS[m - 1].slice(0, 3)} ${y}`;
}

/** Viewer header and info panel: "Saturday, 14 June 2025 · 7:42 pm". */
export function fullDate(iso: string): string {
  if (!iso) return "Undated";
  const { y, m, d, weekday, hh, mm } = parts(iso);
  const h12 = hh % 12 === 0 ? 12 : hh % 12;
  return `${DAYS[weekday]}, ${d} ${MONTHS[m - 1]} ${y} · ${h12}:${mm} ${hh < 12 ? "am" : "pm"}`;
}

/** The camera-style file name a phone would have written for this timestamp. */
export function fileName(iso: string): string {
  if (!iso) return "IMG.jpg";
  const digits = iso.replace(/[^0-9]/g, "");
  return `IMG_${digits.slice(0, 8)}_${digits.slice(8, 14).padEnd(6, "0")}.jpg`;
}

/** "by-sa 2.0" -> "CC BY-SA 2.0"; "cc0 1.0" -> "CC0 1.0". */
export function licenceLabel(l: string): string {
  if (!l) return "";
  const [kind, ver = ""] = l.split(" ");
  return kind.toLowerCase() === "cc0" ? `CC0 ${ver}`.trim() : `CC ${kind.toUpperCase()} ${ver}`.trim();
}

/** Every photo, newest first: the order the timeline shows and the viewer swipes. */
export function allPhotos(gallery: Gallery): GalleryPhoto[] {
  return gallery.sections.flatMap((s) => s.photos);
}

/** Month sections split into days, keeping newest-first order. */
export function daysOf(photos: GalleryPhoto[]): { day: string; photos: GalleryPhoto[] }[] {
  const out: { day: string; photos: GalleryPhoto[] }[] = [];
  for (const p of photos) {
    const day = p.d.slice(0, 10);
    if (!out.length || out[out.length - 1].day !== day) out.push({ day, photos: [] });
    out[out.length - 1].photos.push(p);
  }
  return out;
}
