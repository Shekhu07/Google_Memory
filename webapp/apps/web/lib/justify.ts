/** Justified rows, the way the Photos web grid lays out a timeline: every photo
 *  at its real aspect ratio, each full row stretched to the container's exact
 *  width, and consecutive days sharing a row - each day's label sitting above its
 *  first photo in that row.
 *
 *  Pure and dependency-free so it can be checked with plain Node.
 */

export type Sized = { w: number; h: number };
export type Group<T extends Sized> = { label: string; items: T[] };

export type Cell<T> = { item: T; x: number; width: number; label?: string };
export type Row<T> = { cells: Cell<T>[]; height: number; top: number; header: boolean };

export type JustifyOptions = {
  width: number;
  targetHeight: number;
  gap?: number; // between photos of the same group
  groupGap?: number; // between two groups sharing a row
  headerHeight?: number; // the label strip above a row where a group starts
  maxStretch?: number; // a full row may grow to at most targetHeight * maxStretch
};

export function justify<T extends Sized>(groups: Group<T>[], opts: JustifyOptions): { rows: Row<T>[]; height: number } {
  const { width, targetHeight } = opts;
  const gap = opts.gap ?? 4;
  const groupGap = opts.groupGap ?? 16;
  const headerHeight = opts.headerHeight ?? 40;
  const maxStretch = opts.maxStretch ?? 1.6;

  type Pending = { item: T; aspect: number; label?: string; gapBefore: number };
  const rows: Row<T>[] = [];
  let pending: Pending[] = [];
  let top = 0;

  const aspectOf = (it: T) => (it.w > 0 && it.h > 0 ? it.w / it.h : 1);
  const gapsOf = (ps: Pending[]) => ps.reduce((s, p, i) => s + (i ? p.gapBefore : 0), 0);

  function flush(full: boolean) {
    if (!pending.length) return;
    const aspects = pending.reduce((s, p) => s + p.aspect, 0);
    const free = Math.max(1, width - gapsOf(pending));
    // A full row fills the width exactly; the last row keeps the target height
    // unless even that would overflow.
    let height = full ? free / aspects : Math.min(targetHeight, free / aspects);
    height = Math.min(height, targetHeight * maxStretch);
    const header = pending.some((p) => p.label !== undefined);
    let x = 0;
    const cells: Cell<T>[] = pending.map((p, i) => {
      if (i) x += p.gapBefore;
      const c: Cell<T> = { item: p.item, x, width: p.aspect * height, label: p.label };
      x += c.width;
      return c;
    });
    if (full && cells.length) {
      // Rounding leaves the last cell a fraction short; give it the remainder.
      const last = cells[cells.length - 1];
      last.width = Math.max(1, width - last.x);
    }
    const rowTop = top + (header ? headerHeight : 0);
    rows.push({ cells, height, top: rowTop, header });
    top = rowTop + height + gap;
    pending = [];
  }

  for (const g of groups) {
    g.items.forEach((item, i) => {
      const next: Pending = {
        item,
        aspect: aspectOf(item),
        label: i === 0 ? g.label : undefined,
        gapBefore: i === 0 ? groupGap : gap,
      };
      pending.push(next);
      const aspects = pending.reduce((s, p) => s + p.aspect, 0);
      if (aspects * targetHeight + gapsOf(pending) >= width) flush(true);
    });
  }
  flush(false);
  return { rows, height: Math.max(0, top - gap) };
}
