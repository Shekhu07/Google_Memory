import Link from "next/link";

const ENGINE_URL = "https://retrieval-discovery-engine.vercel.app";

/** Rendered twice, one copy per layout: at the foot of the sidebar on a desktop,
 *  and at the end of the photo panel on a phone, which has no sidebar. */
export function Disclaimer() {
  return (
    <p className="disclaimer">
      <strong>Concept prototype.</strong> Not Google Photos, and not affiliated with Google. The
      library is 1,250 Creative Commons photographs from Openverse; the dates, places and moments
      attached to them are invented.{" "}
      <Link href="/attribution">Photo credits</Link> · <a href={ENGINE_URL}>Research</a>
    </p>
  );
}
