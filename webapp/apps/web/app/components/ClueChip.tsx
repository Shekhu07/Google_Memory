import type { Chip } from "@/lib/api";

/** Grounded labels: name the evidence and its uncertainty, never assert the memory. */
export function clueKind(cue: string): string {
  if (cue === "temporal_approx") return "Approximate time";
  if (cue === "exact_date") return "Date you gave";
  if (cue === "event_anchor") return "Nearby sequence";
  if (cue === "place_named") return "Place";
  if (cue === "object") return "Category";
  return "Possible clue";
}

export function ClueChip({ chip, onRemove }: { chip: Chip; onRemove?: (c: Chip) => void }) {
  return (
    <span className="clue">
      <span>{chip.label}</span>
      <span className="kind">{clueKind(chip.cue)}</span>
      {onRemove && (
        <button className="x" onClick={() => onRemove(chip)} aria-label={`Remove clue ${chip.label}`}>
          ×
        </button>
      )}
    </span>
  );
}

export function ClueList({
  chips,
  onRemove,
  rail = false,
}: {
  chips: Chip[];
  onRemove?: (c: Chip) => void;
  rail?: boolean;
}) {
  return (
    <div className={rail ? "clue-rail" : "clues"}>
      {chips.map((c) => (
        <ClueChip key={c.id} chip={c} onRemove={onRemove} />
      ))}
    </div>
  );
}
