import Link from "next/link";
import { MemoryTopBar } from "@/app/components/MemoryTopBar";

export const metadata = { title: "About — Memory Trails" };

const ENGINE_URL = "https://retrieval-discovery-engine.vercel.app";

export default function About() {
  return (
    <main className="shell">
      <MemoryTopBar title="About" showPrivacy={false} />
      <div className="prose">
        <h1>About Memory Trails</h1>
        <p>
          <Link href="/">← Back to the prototype</Link>
        </p>

        <h2>What it is for</h2>
        <p>
          Getting back to a photo you remember but can’t describe precisely. You describe the
          moment — roughly when, what was happening, what was in it — and Memory Trails shows the
          moments that fit, explains why each one appeared, and lets you correct a clue or rule a
          moment out without starting over. Nothing counts as found until you say “That’s the one.”
        </p>

        <h2>How it relates to Ask Photos</h2>
        <p>
          Ask Photos helps you ask questions about your library. Memory Trails helps you recognise
          and navigate a remembered moment. They are complementary: Memory Trails is a visual way to
          revisit a memory when a conversational answer is not enough — it shows the whole moment
          around a photo, the evidence for each candidate, and a way back when a candidate is wrong.
        </p>

        <h2>What this prototype can and cannot show</h2>
        <p>
          <strong>Concept prototype.</strong> It uses representative public images and invented
          metadata, and is not affiliated with Google. The library is openly licensed photographs
          from Openverse; the dates, places and moments attached to them were invented to make a
          testable library and describe nothing real about those photographs. It has no access to
          anyone’s Google Photos library.
        </p>
        <p>
          It validates the memory re-entry interaction and the way a user recovers from a wrong
          candidate. It does not validate production-scale Google Photos retrieval accuracy. It
          cannot recognise people.
        </p>

        <p>
          <a href={ENGINE_URL}>The research behind it</a> · <Link href="/attribution">Photo credits</Link>
        </p>
      </div>
    </main>
  );
}
