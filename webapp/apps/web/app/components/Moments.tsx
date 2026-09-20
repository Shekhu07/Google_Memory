import type { Episode } from "@/lib/api";
import { formatWindow } from "@/lib/api";

/** Screen 3. At most five candidates, ordered by usefulness, never by a score. */
export const MAX_CANDIDATES = 5;

export function Moments({
  episodes,
  onOpen,
}: {
  episodes: Episode[];
  onOpen: (ep: Episode) => void;
}) {
  return (
    <ol className="trail">
      {episodes.slice(0, MAX_CANDIDATES).map((ep) => {
        const stray = !ep.episode_id;
        const when = formatWindow(ep.date_from, ep.date_to);
        return (
          <li key={ep.episode_id || ep.photos[0]?.id} className={stray ? "station stray" : "station"}>
            <h2>{[ep.location, when].filter(Boolean).join(" · ") || ep.episode}</h2>
            <p className="when">
              {ep.episode !== "Other photos" && <strong>{ep.episode}</strong>}
              {ep.episode !== "Other photos" && " · "}
              {ep.episode_total} photo{ep.episode_total === 1 ? "" : "s"}
              {ep.count < ep.episode_total && ` · ${ep.count} match your clues`}
            </p>
            <div className="strip">
              {ep.photos.slice(0, 4).map((p) => (
                <img key={p.id} src={`/${p.file}`} alt={`Photo from ${ep.episode}`} loading="lazy" />
              ))}
            </div>
            {ep.why.length > 0 && (
              <>
                <p className="why-head">Why this moment?</p>
                <ul className="why">
                  {ep.why.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              </>
            )}
            {!stray && (
              <button className="secondary" onClick={() => onOpen(ep)}>
                Open moment
              </button>
            )}
          </li>
        );
      })}
    </ol>
  );
}
