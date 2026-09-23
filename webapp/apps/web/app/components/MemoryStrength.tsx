export type Strength = "place" | "scene" | "time" | "unsure";

const OPTIONS: { id: Strength; label: string }[] = [
  { id: "place", label: "Where it was" },
  { id: "scene", label: "What it showed" },
  { id: "time", label: "When it happened" },
  { id: "unsure", label: "Not sure" },
];

/**
 * Asked before any narrowing question. It weights the cue the user trusts most,
 * so a throwaway phrase like "small café" cannot outweigh a confident "Goa".
 * Answering is optional — "Not sure" is a real answer, not a failure.
 */
export function MemoryStrength({
  value,
  onChange,
}: {
  value: Strength | null;
  onChange: (s: Strength) => void;
}) {
  return (
    <div className="strength">
      <p className="t-eyebrow">What part feels most certain?</p>
      <div className="options" role="group" aria-label="What part feels most certain?">
        {OPTIONS.map((o) => (
          <button
            key={o.id}
            className={value === o.id ? "example selected" : "example"}
            aria-pressed={value === o.id}
            onClick={() => onChange(o.id)}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}

/** Which clue the chosen certainty protects from removal-by-default and boosts. */
export const STRENGTH_TO_KEY: Record<Strength, string | null> = {
  place: "location",
  scene: "category",
  time: "date",
  unsure: null,
};
