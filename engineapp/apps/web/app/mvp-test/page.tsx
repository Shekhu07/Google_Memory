import type { Metadata } from "next";
import { ResponsePage, type ResponseData } from "@/app/components/ResponsePage";
import mvpTest from "@/public/data/mvp-test.json";

export const metadata: Metadata = {
  title: "MVP user test · Retrieval discovery engine",
  description: "Every question and all 6 anonymised answers from the Memory Trails prototype test.",
};

export default function MvpTestPage() {
  return (
    <ResponsePage
      data={mvpTest as ResponseData}
      eyebrow="Primary research · Part 6 · deck slide 8"
      title="MVP user test: “Try a new way to find an old photo”"
      lead={
        <>
          A self-serve, unmoderated test. Each person first searched their own Google Photos, then used the{" "}
          <a href="https://memory-trails-v2.vercel.app" target="_blank" rel="noopener noreferrer">
            Memory Trails prototype ↗
          </a>{" "}
          for two tasks: the cat from last year&apos;s Diwali, and the dog by a tree from the Diwali before that.
          R01–R06 match the testers on deck slide 8.
        </>
      }
      csvHref="/data/mvp-test-responses.csv"
      idRange="R01–R06"
      other={{ href: "/survey", label: "← Survey" }}
    />
  );
}
