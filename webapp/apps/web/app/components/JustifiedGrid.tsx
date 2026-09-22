import { justify, type Group } from "@/lib/justify";
import { dayLabel, dayLabelShort, type GalleryPhoto } from "@/lib/gallery";

/** Row height the grid aims for: shorter on a phone, where three narrow
 *  columns' worth of photo must fit across. */
export function targetHeight(width: number): number {
  return width < 600 ? 120 : width < 1000 ? 170 : 210;
}

/** Photos at their real aspect ratio in full-width rows, with a day label above
 *  each day's first photo. `first` is the index of this block's first photo in
 *  the list the viewer swipes through, so a tap can open the right one. */
export function JustifiedGrid({
  groups,
  width,
  first = 0,
  eager = 0,
  onOpen,
  labels = true,
}: {
  groups: Group<GalleryPhoto>[];
  width: number;
  first?: number;
  eager?: number;
  onOpen: (index: number) => void;
  labels?: boolean;
}) {
  const { rows, height } = justify(groups, {
    width,
    targetHeight: targetHeight(width),
    gap: 4,
    groupGap: labels ? 16 : 4,
    headerHeight: labels ? 44 : 0,
  });
  let n = first;
  return (
    <div className="jgrid" style={{ height }}>
      {rows.map((row) => {
        // Each label may run until the next one in its row starts. A day with one
        // narrow photo gets the short form rather than colliding with its neighbour.
        const starts = row.cells.filter((c) => c.label).map((c) => c.x);
        return row.cells.map((c) => {
          const index = n++;
          const p = c.item;
          const room = c.label ? (starts.find((x) => x > c.x) ?? width) - c.x - 10 : 0;
          return (
            <div key={p.f}>
              {labels && c.label && (
                <h3 className="jlabel" style={{ left: c.x, top: row.top - 44, maxWidth: room }} title={dayLabel(c.label)}>
                  {room < 130 ? dayLabelShort(c.label) : dayLabel(c.label)}
                </h3>
              )}
              <button
                className="jcell"
                style={{ left: c.x, top: row.top, width: c.width, height: row.height }}
                onClick={() => onOpen(index)}
                aria-label={`Open photo, ${dayLabel(p.d)}${p.p ? `, ${p.p}` : ""}`}
              >
                <img
                  src={`/${p.f}`}
                  alt={p.t}
                  loading={index - first < eager ? "eager" : "lazy"}
                  decoding="async"
                />
              </button>
            </div>
          );
        });
      })}
    </div>
  );
}

/** Photos grouped by day, newest first - the grouping every timeline-like view uses. */
export function byDay(photos: GalleryPhoto[]): Group<GalleryPhoto>[] {
  const out: Group<GalleryPhoto>[] = [];
  for (const p of photos) {
    const day = p.d.slice(0, 10);
    if (!out.length || out[out.length - 1].label !== day) out.push({ label: day, items: [] });
    out[out.length - 1].items.push(p);
  }
  return out;
}
