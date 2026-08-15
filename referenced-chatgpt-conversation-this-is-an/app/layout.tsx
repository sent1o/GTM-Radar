import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GTM Radar — Competitive intelligence",
  description: "Track competitor pricing and positioning changes."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
