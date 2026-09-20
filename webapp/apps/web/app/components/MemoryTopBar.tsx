import Link from "next/link";

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
          {backLabel?.startsWith("Close") ? "×" : "←"}
        </button>
      ) : null}
      <h2>{title}</h2>
      {showPrivacy && (
        <span className="privacy">Private by default · only searches when you ask</span>
      )}
      {links && (
        <nav>
          <Link href="/evidence">Research</Link>
          <Link href="/attribution">Credits</Link>
        </nav>
      )}
    </header>
  );
}
