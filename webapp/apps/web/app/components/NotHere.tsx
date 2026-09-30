import type { Change } from "@/app/components/NoMatch";
import { SeenCues } from "@/app/components/SeenCues";
import type { CueSuggestion } from "@/lib/api";

/**
 * A set-level "none of these", asked quietly under the moments rather than after
 * every search. Its first job is measurement (did the target surface at all?);
 * the options are a cheap next step, not a recovery flow.
 *
 * Nothing is ruled out: a cover shows four photos, so "not here" is often wrong.
 */
export function NotHere({
  open,
  remaining,
  changes,
  cues = [],
  onOpen,
  onNextPage,
  onChange,
  onEditClues,
  onPickSeen,
}: {
  open: boolean;
  remaining: number;
  changes: Change[];
  cues?: CueSuggestion[];
  onOpen: () => void;
  onNextPage: () => void;
  onChange: (c: Change) => void;
  onEditClues: () => void;
  onPickSeen?: (label: string, rank: number) => void;
}) {
  if (!open) {
    return (
      <div className="not-here">
        <button className="btn quiet" onClick={onOpen}>
          Not in any of these?
        </button>
      </div>
    );
  }

  const next = Math.min(remaining, 5);
  return (
    <section className="panel not-here-panel" aria-live="polite">
      <h2 className="t-section">Not in these moments</h2>
      <p className="t-support">
        It may still be inside one of them — each card shows only a few photos.
      </p>
      {cues.length > 0 && onPickSeen && (
        <SeenCues cues={cues} surface="not_here" onPick={onPickSeen} />
      )}
      <div className="options">
        {next > 0 && (
          <button className="btn ghost" onClick={onNextPage}>
            Show the next {next} moment{next === 1 ? "" : "s"}
          </button>
        )}
        {changes.map((c) => (
          <button key={c.id} className="btn ghost" onClick={() => onChange(c)}>
            {c.label}
          </button>
        ))}
        <button className="btn ghost" onClick={onEditClues}>
          Edit my clues
        </button>
      </div>
    </section>
  );
}

