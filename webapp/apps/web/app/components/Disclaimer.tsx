import Link from "next/link";

const ENGINE_URL = "https://retrieval-discovery-engine.vercel.app";

/** Rendered twice: inside the gallery scroll, which is the only place it can be
 *  seen on a real phone, and on the backdrop beside the frame on a desktop. */
export function Disclaimer() {
  return (
    <p className="disclaimer">
      <strong>Concept prototype.</strong> Not Google Photos, and not affiliated with Google. The
      library is 492 Creative Commons photographs from Openverse; the dates, places and moments
      attached to them are invented.{" "}
      <Link href="/attribution">Photo credits</Link> · <a href={ENGINE_URL}>Research</a>
    </p>
  );
}
