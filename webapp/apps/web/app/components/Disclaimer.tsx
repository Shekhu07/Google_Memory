import Link from "next/link";

const ENGINE_URL = "https://retrieval-discovery-engine.vercel.app";

/** Rendered twice, one copy per layout: at the foot of the sidebar on a desktop,
 *  and at the end of the photo panel on a phone, which has no sidebar. */
export function Disclaimer() {
  return (
    <p className="disclaimer">
      <strong>Concept prototype.</strong> Uses representative public images and invented
      metadata. Not affiliated with Google. The demo treats today as 23 Sep 2026.{" "}
      <Link href="/about">About</Link> · <Link href="/attribution">Photo credits</Link> ·{" "}
      <a href={ENGINE_URL}>Research</a>
    </p>
  );
}
