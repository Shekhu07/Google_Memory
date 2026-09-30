export type RecoveryReason = "wrong_day" | "wrong_place" | "wrong_people" | "wrong_type" | "not_sure";

export const REASONS: { id: RecoveryReason; label: string }[] = [
  { id: "wrong_day", label: "Wrong day" },
  { id: "wrong_place", label: "Wrong place" },
  { id: "wrong_type", label: "Wrong type of image" },
  { id: "not_sure", label: "I’m not sure" },
];

/**
 * After "Not this moment": one question, four answers, each changing a single
 * clue. It is a safety net, not the core of the product - near-miss recovery was
 * 0.7% of observed failures - so it asks once and never blocks: the moment is
 * already ruled out whichever answer is chosen.
 */
export function Recover({
  moment,
  onPick,
}: {
  moment: string;
  onPick: (reason: RecoveryReason) => void;
}) {
  return (
    <section className="panel recover" aria-labelledby="recover-h">
      <h2 id="recover-h" className="t-section">
        What was off?
      </h2>
      <p className="t-support">
        {moment ? `“${moment}” is hidden. ` : "This moment is hidden. "}Your clues are kept.
        Pick what was off and I’ll change just that.
      </p>
      <div className="options">
        {REASONS.map((r) => (
          <button key={r.id} className="btn ghost" onClick={() => onPick(r.id)}>
            {r.label}
          </button>
        ))}
      </div>
    </section>
  );
}
