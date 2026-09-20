import Link from "next/link";

export function Masthead({ here }: { here: "trails" | "evidence" | "attribution" }) {
  return (
    <header className="masthead">
      <p className="wordmark">Memory Trails</p>
      <nav>
        {here !== "trails" && <Link href="/">Find a memory</Link>}
        {here !== "evidence" && <Link href="/evidence">What the research found</Link>}
        {here !== "attribution" && <Link href="/attribution">Photo credits</Link>}
      </nav>
    </header>
  );
}
