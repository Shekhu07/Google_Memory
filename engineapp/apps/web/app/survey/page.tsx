import type { Metadata } from "next";
import { ResponsePage, type ResponseData } from "@/app/components/ResponsePage";
import survey from "@/public/data/survey.json";

export const metadata: Metadata = {
  title: "User research survey · Retrieval discovery engine",
  description: "Every question and all 15 anonymised answers from the photo-retrieval survey.",
};

export default function SurveyPage() {
  return (
    <ResponsePage
      data={survey as ResponseData}
      eyebrow="Primary research · Part 3 · deck slide 4"
      title="User research survey: “Finding an old photo”"
      lead={
        <>
          A structured self-serve questionnaire about the last time each person could not find an old photo.
          Every answer maps onto the engine&apos;s own fields (what they remembered, what they forgot, where search
          broke), so the 15 stories can be read beside the 144 public ones.
        </>
      }
      csvHref="/data/survey-responses.csv"
      idRange="S01–S15"
      other={{ href: "/mvp-test", label: "MVP test →" }}
    />
  );
}
