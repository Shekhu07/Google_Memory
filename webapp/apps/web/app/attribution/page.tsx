import Link from "next/link";
import { MemoryTopBar } from "@/app/components/MemoryTopBar";
import credits from "@/public/data/attribution.json";

export const metadata = { title: "Photo credits — Memory Trails" };

export default function Attribution() {
  return (
    <main className="shell">
      <MemoryTopBar title="Photo credits" showPrivacy={false} />
      <div className="prose">
        <h1>Photo credits</h1>
        <p>
          <Link href="/">← Back to the prototype</Link>
        </p>
        <p>
          All {credits.length} photographs come from Openverse under Creative Commons licences, and belong to
          the people who made them. Dates, places and episodes attached to them are synthetic — invented to
          build a testable library, and describing nothing real about these photographs.
        </p>
      </div>
      <div className="credits">
        {credits.map((c) => (
          <p key={c.file}>
            <a href={c.source_url} target="_blank" rel="noreferrer noopener">
              {c.title || c.file}
            </a>{" "}
            — {c.creator || "unknown"}, CC {c.license}
          </p>
        ))}
      </div>
    </main>
  );
}
