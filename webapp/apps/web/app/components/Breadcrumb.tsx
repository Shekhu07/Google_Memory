import type { Chip } from "@/lib/api";
import { clueKind } from "@/app/components/ClueChip";

/**
 * The memory breadcrumb. Persists through episode browsing so the user keeps
 * their mental thread and can always see what the system is currently chasing.
 */
export function Breadcrumb({
  heard,
  chips,
  onRemove,
  onAdd,
}: {
  heard: string;
  chips: Chip[];
  onRemove?: (c: Chip) => void;
  /** Opens the clue editor, so a remembered detail can be added without restarting. */
  onAdd?: () => void;
}) {
  return (
    <nav className="crumbs" aria-label="Your memory so far">
      <span className="crumb origin" title={heard}>
        Your memory:
      </span>
      {chips.map((c) => (
        <span className="crumb" key={c.id}>
          <span>{c.label}</span>
          <span className="crumb-kind" style={{ opacity: 0.7, marginLeft: 4 }}>
            · {clueKind(c.cue)}
          </span>
          {onRemove && (
            <button onClick={() => onRemove(c)} aria-label={`Remove clue ${c.label}`}>
              ×
            </button>
          )}
        </span>
      ))}
      {onAdd && (
        <button className="crumb add" onClick={onAdd}>
          + Add a clue
        </button>
      )}
    </nav>
  );
}
