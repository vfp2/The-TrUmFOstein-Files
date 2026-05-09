import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The TrUmFOstein Files — substrate viewer",
  description:
    "3D navigable knowledge graph of the U.S. Department of War PURSUE UAP/UFO release (war.gov/UFO, 8 May 2026). Documents, incidents, anonymised witnesses, missions, and visual evidence.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
