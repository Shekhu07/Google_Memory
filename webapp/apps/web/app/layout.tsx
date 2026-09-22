import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// Google Sans is not publicly distributable; Inter is the specified web fallback.
const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Memory Trails",
  description:
    "Start with what you remember. A memory re-entry experience inside a photo library, over 1,250 real images.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  // Without cover, env(safe-area-inset-bottom) is always 0 and the bottom nav
  // sits under the iOS home indicator.
  viewportFit: "cover",
  themeColor: "#F7F8FA",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
