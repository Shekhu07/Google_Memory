import { dayLabel, daysOf, type Gallery } from "@/lib/gallery";

/** Above-the-fold cells load eagerly: loading="lazy" on the first screenful
 *  costs a visible blank flash on first paint and saves nothing. */
const EAGER = 9;

/** The library the retrieval flow is trying to get back into, laid out as the
 *  Photos timeline is: months, then days, every photo a tap away from full
 *  screen. `onOpen` receives the photo's position in newest-first order, which
 *  is the order `allPhotos(gallery)` returns and the viewer swipes through. */
export function GalleryGrid({
  gallery,
  onOpen,
}: {
  gallery: Gallery;
  onOpen: (index: number) => void;
}) {
  let n = 0;
  return (
    <>
      {gallery.sections.map((s) => {
        const days = daysOf(s.photos);
        const rows = days.reduce((sum, d) => sum + Math.ceil(d.photos.length / 3), 0);
        return (
          <section className="month" key={s.month} data-label={s.label}>
            <h2 className="month-label">{s.label}</h2>
            {/* Rows and day headers are knowable before layout, so the reserved
                height is exact and the scrollbar does not jump as content-visibility
                measures each month for real. */}
            <div
              className="month-body"
              style={{ "--rows": rows, "--days": days.length } as React.CSSProperties}
            >
              {days.map((d) => (
                <div className="day" key={d.day}>
                  <h3 className="day-label">{dayLabel(d.day)}</h3>
                  <div className="grid">
                    {d.photos.map((p) => {
                      const index = n++;
                      return (
                        <button
                          key={p.f}
                          className="cell"
                          onClick={() => onOpen(index)}
                          aria-label={`Open photo, ${dayLabel(p.d)}${p.p ? `, ${p.p}` : ""}`}
                        >
                          <img
                            src={`/${p.f}`}
                            alt={p.t}
                            loading={index < EAGER ? "eager" : "lazy"}
                            decoding="async"
                          />
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </section>
        );
      })}
    </>
  );
}
