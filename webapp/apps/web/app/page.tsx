import { PhoneFrame } from "@/app/components/PhoneFrame";
import { PhotoApp } from "@/app/components/PhotoApp";
import gallery from "@/public/data/gallery.json";
import type { Gallery } from "@/lib/gallery";

/** A Server Component: the 33 KB manifest streams as flight data and never
 *  enters the client bundle. Same pattern as /attribution. */
export default function Page() {
  return (
    <PhoneFrame>
      <PhotoApp gallery={gallery as Gallery} />
    </PhoneFrame>
  );
}
