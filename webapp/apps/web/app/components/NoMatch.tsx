import type { Filters } from "@/lib/api";

export type Change = { id: string; label: string; apply: (f: Filters) => Filters };

/** Screen 6. One small change at a time, each one named, never "try again". */
export function changesFor(filters: Filters): Change[] {
  const out: Change[] = [];
  if (filters.date_from) {
    out.push({
      id: "widen-time",
      label: "Widen the time",
      apply: (f) => {
        const n = { ...f };
        delete n.date_from;
        delete n.date_to;
        return n;
      },
    });
  }
  if (filters.category) {
    out.push({
      id: "drop-category",
      label: `Remove “${filters.category}”`,
      apply: (f) => {
        const n = { ...f };
        delete n.category;
        return n;
      },
    });
  }
  if (filters.episode) {
    out.push({
      id: "drop-episode",
      label: `Look beyond “${filters.episode}”`,
      apply: (f) => {
        const n = { ...f };
        delete n.episode;
        return n;
      },
    });
  }
  if (filters.location) {
    out.push({
      id: "drop-location",
      label: `Look outside ${filters.location}`,
      apply: (f) => {
        const n = { ...f };
        delete n.location;
        return n;
      },
    });
  }
  return out;
}

export function NoMatch({
  filters,
  onChange,
  onExit,
}: {
  filters: Filters;
  onChange: (c: Change) => void;
  onExit: () => void;
}) {
  const changes = changesFor(filters);
  return (
    <section className="panel">
      <h2 className="t-section">No close match yet</h2>
      <p>
        I couldn&rsquo;t find a moment that feels right.
        {Object.keys(filters).length > 0 &&
          " I looked where " +
            Object.entries(filters)
              .map(([k, v]) => `${k.replace(/_/g, " ")} is ${v}`)
              .join(", ") +
            "."}
      </p>
      {changes.length > 0 ? (
        <>
          <p>Keep the memory and try one small change:</p>
          <div className="options">
            {changes.map((c) => (
              <button key={c.id} className="btn ghost" onClick={() => onChange(c)}>
                {c.label}
              </button>
            ))}
          </div>
        </>
      ) : (
        <p>There are no clues left to loosen. Your library is unchanged.</p>
      )}
      <p className="t-support">Or return to your library without changing anything.</p>
      <button className="btn ghost" onClick={onExit}>
        Exit
      </button>
    </section>
  );
}
