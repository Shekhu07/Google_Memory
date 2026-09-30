import { formatWindow, type Alternative, type Chip } from "@/lib/api";

/** Grounded labels: name the evidence and its uncertainty, never assert the memory. */
export function clueKind(cue: string): string {
  if (cue === "temporal_approx") return "Approximate time";
  if (cue === "exact_date") return "Date you gave";
  if (cue === "event_anchor") return "Event";
  if (cue === "place_named") return "Place";
  if (cue === "object") return "Object or scene";
  if (cue === "seen") return "Something you saw";
  return "Possible clue";
}

export function ClueChip({
  chip,
  onRemove,
  onSelectAlternative,
}: {
  chip: Chip;
  onRemove?: (c: Chip) => void;
  onSelectAlternative?: (c: Chip, alt: Alternative) => void;
}) {
  const isDate = chip.filter_key === "date_from";
  const windowLabel = isDate ? formatWindow(chip.value, chip.value_to ?? null) : null;
  const showSub = windowLabel && windowLabel !== chip.label;
  const firstAlt = chip.alternatives && chip.alternatives.length > 0 ? chip.alternatives[0] : null;

  return (
    <div className="clue-wrap">
      <span className="clue">
        <div className="clue-content">
          <span>{chip.label}</span>
          {showSub && <span className="chip-window-label">{windowLabel}</span>}
        </div>
        <span className="kind">{clueKind(chip.cue)}</span>
        {onRemove && (
          <button className="x" onClick={() => onRemove(chip)} aria-label={`Remove clue ${chip.label}`}>
            ×
          </button>
        )}
      </span>
      {firstAlt && onSelectAlternative && (
        <button
          className="chip-alt-btn"
          onClick={() => onSelectAlternative(chip, firstAlt)}
        >
          {firstAlt.label}?
        </button>
      )}
    </div>
  );
}

export function ClueList({
  chips,
  onRemove,
  onSelectAlternative,
  rail = false,
}: {
  chips: Chip[];
  onRemove?: (c: Chip) => void;
  onSelectAlternative?: (c: Chip, alt: Alternative) => void;
  rail?: boolean;
}) {
  return (
    <div className={rail ? "clue-rail" : "clues"}>
      {chips.map((c) => (
        <ClueChip
          key={c.id}
          chip={c}
          onRemove={onRemove}
          onSelectAlternative={onSelectAlternative}
        />
      ))}
    </div>
  );
}
