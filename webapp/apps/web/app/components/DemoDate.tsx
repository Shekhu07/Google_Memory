"use client";

import { useEffect, useState } from "react";
import { facetsCached, formatWindow } from "@/lib/api";

/**
 * The date the parser reads "last winter" or "pichle saal" against. Read from the
 * retrieval service (DEMO_TODAY) rather than written into the page, so the words can
 * never disagree with what the parser actually does. Renders nothing until it knows.
 */
export function DemoDate({ prefix = "The demo treats today as " }: { prefix?: string }) {
  const [today, setToday] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    void facetsCached().then((f) => {
      if (live && f.demo_today) setToday(f.demo_today);
    });
    return () => {
      live = false;
    };
  }, []);
  if (!today) return null;
  return (
    <>
      {prefix}
      {formatWindow(today, today)}.
    </>
  );
}
