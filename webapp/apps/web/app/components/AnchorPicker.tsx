import type { Anchor } from "@/lib/api";
import { clueKind } from "@/app/components/ClueChip";

export function AnchorPicker({
  anchors,
  selectedAnchorIds,
  onToggleAnchor,
}: {
  anchors: Anchor[];
  selectedAnchorIds: Set<string>;
  onToggleAnchor: (anchor: Anchor) => void;
}) {
  if (!anchors || anchors.length === 0) return null;

  return (
    <div className="anchors-section">
      <p className="t-eyebrow anchors-label">Add one thing you remember</p>
      <p className="t-support anchors-help">
        A place, a person, an object, an event, a type of image or a season — whatever stuck.
      </p>
      <div className="anchors-list" role="group" aria-label="Examples of things you might remember">
        {anchors.map((anchor) => {
          const selected = selectedAnchorIds.has(anchor.id);
          return (
            <button
              key={anchor.id}
              type="button"
              className={`anchor-chip ${selected ? "selected" : ""}`}
              onClick={() => onToggleAnchor(anchor)}
              aria-pressed={selected}
            >
              <span className="anchor-icon">{selected ? "✓" : "+"}</span>
              <span className="anchor-label">{anchor.label}</span>
              <span className="anchor-cue">{anchor.kind_label ?? clueKind(anchor.cue)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
