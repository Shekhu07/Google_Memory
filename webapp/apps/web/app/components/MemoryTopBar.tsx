import Link from "next/link";

/** The Discovery Engine is its own deliverable and its own deployment. */
const ENGINE_URL = "https://retrieval-discovery-engine.vercel.app";

/** Close/back action, title, and the standing privacy indicator. */
export function MemoryTopBar({
  title,
  onBack,
  backLabel,
  showPrivacy = true,
  links,
}: {
  title: string;
  onBack?: () => void;
  backLabel?: string;
  showPrivacy?: boolean;
  links?: boolean;
}) {
  return (
    <header className="topbar">
      {onBack ? (
        <button className="icon" onClick={onBack} aria-label={backLabel ?? "Go back"}>
          {backLabel?.startsWith("Close") ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
          )}
        </button>
      ) : null}
      <h2>{title}</h2>
      {showPrivacy && (
        <span className="privacy">Private by default · only searches when you ask</span>
      )}
      {links && (
        <nav>
          {/* Separate deliverable, separate deployment - see engineapp/. */}
          <a href={ENGINE_URL}>Research</a>
          <Link href="/attribution">Credits</Link>
        </nav>
      )}
    </header>
  );
}
