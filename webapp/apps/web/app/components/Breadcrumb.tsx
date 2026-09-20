import type { Chip } from "@/lib/api";

/**
 * The memory breadcrumb. Persists through episode browsing so the user keeps
 * their mental thread and can always see what the system is currently chasing.
 */
export function Breadcrumb({
  heard,
  chips,
  onRemove,
}: {
  heard: string;
  chips: Chip[];
  onRemove?: (c: Chip) => void;
}) {
  return (
    <nav className="crumbs" aria-label="Your memory so far">
      <span className="crumb origin" title={heard}>
        Your memory
      </span>
      {chips.map((c) => (
        <span className="crumb" key={c.id}>
          {c.label}
          {onRemove && (
            <button onClick={() => onRemove(c)} aria-label={`Remove clue ${c.label}`}>
              ×
            </button>
          )}
        </span>
      ))}
    </nav>
  );
}
