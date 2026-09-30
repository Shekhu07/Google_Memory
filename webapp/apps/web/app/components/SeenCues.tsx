"use client";

import { useEffect, useRef, useState } from "react";
import type { CueSuggestion } from "@/lib/api";
import { track } from "@/lib/track";

export function SeenCues({
  cues,
  surface,
  onPick,
}: {
  cues: CueSuggestion[];
  surface: "not_here" | "no_match";
  onPick: (label: string, rank: number) => void;
}) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const trackedRef = useRef<string | null>(null);

  const key = cues.map((c) => c.label).join(",");

  useEffect(() => {
    if (cues.length > 0 && trackedRef.current !== key) {
      trackedRef.current = key;
      track("seen_cues_shown", {
        labels: cues.map((c) => c.label),
        surface,
      });
    }
  }, [cues, surface, key]);

  if (!cues || cues.length === 0) return null;

  const activeCue = (hoveredIdx !== null && cues[hoveredIdx]) ? cues[hoveredIdx] : cues[0];

  return (
    <div className="seen-cues" aria-label="Visual detail suggestions">
      <div className="seen-cues-title">Try something you&rsquo;d have seen</div>
      <div className="seen-cues-support">
        Seen in {activeCue.seen_in} of the {activeCue.of} closest photos
      </div>
      <div className="seen-cues-chips" role="group" aria-label="Visual cue chips">
        {cues.map((cue, idx) => (
          <button
            key={cue.label}
            type="button"
            className="seen-cue-chip"
            onClick={() => onPick(cue.label, idx)}
            onMouseEnter={() => setHoveredIdx(idx)}
            onMouseLeave={() => setHoveredIdx(null)}
            onFocus={() => setHoveredIdx(idx)}
            onBlur={() => setHoveredIdx(null)}
            title={`Seen in ${cue.seen_in} of ${cue.of} photos`}
          >
            <span>{cue.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
