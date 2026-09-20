import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// Google Sans is not publicly distributable; Inter is the specified web fallback.
const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Memory Trails",
  description:
    "Start with what you remember. A memory re-entry experience for a photo library, over 494 real images.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
