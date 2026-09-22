import { AppShell } from "@/app/components/AppShell";
import gallery from "@/public/data/gallery.json";
import type { Gallery } from "@/lib/gallery";

/** A Server Component: the manifest streams as flight data and never enters the
 *  client bundle. Same pattern as /attribution. */
export default function Page() {
  return <AppShell gallery={gallery as Gallery} />;
}
