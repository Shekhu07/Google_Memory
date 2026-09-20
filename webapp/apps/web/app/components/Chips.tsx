import type { Chip } from "@/lib/api";

/** Wireframe trust language: name the uncertainty, never assert the memory. */
export function trustLabel(cue: string): string {
  if (cue === "temporal_approx") return "Approximate time";
  if (cue === "exact_date") return "Date you gave";
  if (cue === "event_anchor") return "Based on nearby photos";
  return "Possible clue";
}

export function Chips({
  chips,
  onRemove,
}: {
  chips: Chip[];
  onRemove?: (chip: Chip) => void;
}) {
  return (
    <div className="chips">
      {chips.map((chip) => (
        <span className="chip" key={chip.id}>
          <span>{chip.label}</span>
          <span className="cue">{trustLabel(chip.cue)}</span>
          {onRemove && (
            <button onClick={() => onRemove(chip)} aria-label={`Remove the clue ${chip.label}`}>
              ×
            </button>
          )}
        </span>
      ))}
    </div>
  );
}
