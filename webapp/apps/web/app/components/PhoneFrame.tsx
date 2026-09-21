import { Disclaimer } from "@/app/components/Disclaimer";

/** Full-bleed on a phone; a framed device on a desktop. Deliberately plain - no
 *  notch, status bar or home indicator. A rounded rect with a shadow reads as a
 *  phone in under a second, and the rest is styling the brief does not score. */
export function PhoneFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="stage">
      <div className="phone">{children}</div>
      <Disclaimer />
    </div>
  );
}
