import type { Episode } from "@/lib/api";
import { formatWindow } from "@/lib/api";

export function Trail({ episodes }: { episodes: Episode[] }) {
  return (
    <ol className="trail">
      {episodes.map((ep) => {
        const stray = !ep.episode_id;
        return (
          <li key={ep.episode_id || ep.photos[0]?.id} className={stray ? "station stray" : "station"}>
            <h2>{ep.episode}</h2>
            <p className="when">
              {[formatWindow(ep.date_from, ep.date_to), ep.location, `${ep.count} photo${ep.count === 1 ? "" : "s"}`]
                .filter(Boolean)
                .join(" · ")}
            </p>
            {ep.why.length > 0 && (
              <ul className="why" aria-label="Why this episode is here">
                {ep.why.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            )}
            <div className="strip">
              {ep.photos.map((p) => (
                <img key={p.id} src={`/${p.file}`} alt="" loading="lazy" />
              ))}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
