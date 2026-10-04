import { byDay, JustifiedGrid } from "@/app/components/JustifiedGrid";
import { justify } from "@/lib/justify";
import type { Gallery } from "@/lib/gallery";
import { targetHeight } from "@/app/components/JustifiedGrid";
import { MemoriesCarousel } from "@/app/components/MemoriesCarousel";

/** Above-the-fold photos load eagerly: loading="lazy" on the first screenful
 *  costs a visible blank flash on first paint and saves nothing. */
const EAGER = 12;

/** The library the retrieval flow is trying to get back into, laid out as the
 *  Photos web timeline is: justified rows, days side by side, newest first.
 *
 *  Rows restart at each month so every month is its own block with a known
 *  height. That lets `content-visibility` skip layout, paint and image decode for
 *  the months off screen - what makes 1,250 plain <img> tags viable without a
 *  virtualiser - and gives the fast scroller a month to name. */
export function Timeline({
  gallery,
  width,
  onOpen,
  onOpenTrails,
}: {
  gallery: Gallery;
  width: number;
  onOpen: (index: number) => void;
  onOpenTrails?: (seed: string) => void;
}) {
  let first = 0;
  return (
    <>
      {onOpenTrails && <MemoriesCarousel onOpenTrails={onOpenTrails} />}
      {gallery.sections.map((s) => {
        const groups = byDay(s.photos);
        const { height } = justify(groups, { width, targetHeight: targetHeight(width), headerHeight: 44 });
        const start = first;
        first += s.photos.length;
        return (
          <section
            key={s.month}
            className="tl-month"
            data-label={s.label}
            aria-label={s.label}
            style={{ containIntrinsicSize: `auto ${Math.ceil(height)}px` }}
          >
            <JustifiedGrid
              groups={groups}
              width={width}
              first={start}
              eager={start === 0 ? EAGER : 0}
              onOpen={onOpen}
            />
          </section>
        );
      })}
    </>
  );
}
