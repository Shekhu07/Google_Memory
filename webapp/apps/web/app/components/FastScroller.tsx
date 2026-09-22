"use client";

import { useEffect, useRef, useState, type RefObject } from "react";

/** The drag handle on the timeline's right edge. Five years of photos is too far
 *  to flick through, so the library offers a jump - and while it is held, a
 *  bubble names the month under the thumb. Months come from each section's
 *  data-label, so this knows nothing about the gallery's data. */
export function FastScroller({ target }: { target: RefObject<HTMLDivElement | null> }) {
  const [pos, setPos] = useState(0); // 0..1 through the scrollable range
  const [label, setLabel] = useState("");
  const [visible, setVisible] = useState(false);
  const [dragging, setDragging] = useState(false);
  const track = useRef<HTMLDivElement>(null);
  const hide = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  function labelAt(el: HTMLDivElement): string {
    const sections = el.querySelectorAll<HTMLElement>("section[data-label]");
    let current = sections[0]?.dataset.label ?? "";
    for (const s of sections) {
      if (s.offsetTop - el.offsetTop > el.scrollTop + 8) break;
      current = s.dataset.label ?? current;
    }
    return current;
  }

  useEffect(() => {
    const el = target.current;
    if (!el) return;
    const onScroll = () => {
      const range = el.scrollHeight - el.clientHeight;
      setPos(range > 0 ? el.scrollTop / range : 0);
      setLabel(labelAt(el));
      setVisible(true);
      clearTimeout(hide.current);
      hide.current = setTimeout(() => setVisible(false), 1400);
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      el.removeEventListener("scroll", onScroll);
      clearTimeout(hide.current);
    };
  }, [target]);

  function jump(clientY: number) {
    const el = target.current;
    const t = track.current;
    if (!el || !t) return;
    const r = t.getBoundingClientRect();
    const f = Math.min(1, Math.max(0, (clientY - r.top) / r.height));
    el.scrollTop = f * (el.scrollHeight - el.clientHeight);
  }

  return (
    <div
      ref={track}
      className={`fast-scroller${visible || dragging ? " shown" : ""}`}
      aria-hidden="true"
      onPointerDown={(e) => {
        (e.target as HTMLElement).setPointerCapture(e.pointerId);
        setDragging(true);
        jump(e.clientY);
      }}
      onPointerMove={(e) => dragging && jump(e.clientY)}
      onPointerUp={() => setDragging(false)}
      onPointerCancel={() => setDragging(false)}
    >
      <div className="fs-thumb" style={{ top: `calc(${pos} * (100% - 44px))` }}>
        {dragging && label && <span className="fs-bubble">{label}</span>}
      </div>
    </div>
  );
}
