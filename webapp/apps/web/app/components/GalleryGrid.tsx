import { Disclaimer } from "@/app/components/Disclaimer";
import type { Gallery } from "@/lib/gallery";

/** Above-the-fold cells load eagerly: loading="lazy" on the first screenful
 *  costs a visible blank flash on first paint and saves nothing. */
const EAGER = 9;

/** The library the retrieval flow is trying to get back into. Its whole job is
 *  to exist: a library you cannot see is a library whose missing re-entry point
 *  cannot be shown. */
export function GalleryGrid({ gallery }: { gallery: Gallery }) {
  let n = 0;
  return (
    <>
      {gallery.sections.map((s) => (
        <section className="month" key={s.month}>
          <h2 className="t-eyebrow month-label">{s.label}</h2>
          {/* Rows are knowable before layout: 3 square columns. Without this the
              reserved height is a guess and the scrollbar jumps as content-visibility
              measures each section for real. */}
          <div
            className="month-body"
            style={{ "--rows": Math.ceil(s.photos.length / 3) } as React.CSSProperties}
          >
            <div className="grid">
              {s.photos.map((p) => {
                const eager = n++ < EAGER;
                return (
                  <img
                    key={p.f}
                    src={`/${p.f}`}
                    alt={p.t}
                    loading={eager ? "eager" : "lazy"}
                    decoding="async"
                  />
                );
              })}
            </div>
          </div>
        </section>
      ))}
      <Disclaimer />
    </>
  );
}
