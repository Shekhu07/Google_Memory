"use client";

import { GeminiSpark } from "@/app/components/Icons";

export interface MemoryStory {
  id: string;
  title: string;
  subtitle: string;
  cover: string;
  seed: string;
  isSpecial?: boolean;
}

const DEFAULT_MEMORIES: MemoryStory[] = [
  {
    id: "memory-trails",
    title: "Memory Trails",
    subtitle: "Describe a moment",
    cover: "/library/0225.jpg",
    seed: "",
    isSpecial: true,
  },
  {
    id: "goa-trip",
    title: "Trip to Goa",
    subtitle: "March 2026",
    cover: "/library/0225.jpg",
    seed: "Trip to Goa on the beach in March",
  },
  {
    id: "bengaluru-cafe",
    title: "Coffee & Cafés",
    subtitle: "May 2026",
    cover: "/library/0177.jpg",
    seed: "Having coffee and snacks at a café in Bengaluru",
  },
  {
    id: "one-year-ago",
    title: "1 Year Ago",
    subtitle: "Chai & Street Food",
    cover: "/library/0625.jpg",
    seed: "Drinking masala chai with friends",
  },
  {
    id: "pets-at-home",
    title: "Our Pets",
    subtitle: "April 2026",
    cover: "/library/0687.jpg",
    seed: "Dogs relaxing together on the couch",
  },
];

/** The signature Google Photos Memories carousel at the top of the photo stream.
 *  Gives mobile users an immediate, tactile entrypoint into memories. */
export function MemoriesCarousel({
  onOpenTrails,
}: {
  onOpenTrails: (seed: string) => void;
}) {
  return (
    <section className="memories-section" aria-label="Memories">
      <div className="memories-rail" role="region" aria-label="Recent memories">
        {DEFAULT_MEMORIES.map((story) => {
          if (story.isSpecial) {
            return (
              <button
                key={story.id}
                className="memory-card memory-special"
                onClick={() => onOpenTrails("")}
                aria-label="Find a memory with Memory Trails"
              >
                <div className="memory-special-bg" />
                <div className="memory-special-badge">
                  <GeminiSpark size={16} />
                  <span>Ask Photos</span>
                </div>
                <div className="memory-scrim" />
                <div className="memory-content">
                  <span className="memory-title">Memory Trails</span>
                  <span className="memory-sub">Find by what you recall</span>
                </div>
              </button>
            );
          }

          return (
            <button
              key={story.id}
              className="memory-card"
              onClick={() => onOpenTrails(story.seed)}
              aria-label={`View memory: ${story.title}, ${story.subtitle}`}
            >
              <img
                src={story.cover}
                alt=""
                className="memory-img"
                loading="lazy"
                decoding="async"
              />
              <div className="memory-scrim" />
              <div className="memory-content">
                <span className="memory-title">{story.title}</span>
                <span className="memory-sub">{story.subtitle}</span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
