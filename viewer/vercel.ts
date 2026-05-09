import { type VercelConfig } from "@vercel/config/v1";

// The graph.json + per-doc bundles are regenerated locally with
// `python3 substrate/export/export_graph.py` before deploy. We do not
// regenerate at build time on Vercel because the deploy environment
// can't reach the local TypeDB instance.
export const config: VercelConfig = {
  framework: "nextjs",
  buildCommand: "next build",
  headers: [
    {
      source: "/graph.json",
      headers: [
        { key: "Cache-Control", value: "public, max-age=300, s-maxage=3600, stale-while-revalidate=86400" },
      ],
    },
    {
      source: "/docs/(.*).json",
      headers: [
        { key: "Cache-Control", value: "public, max-age=300, s-maxage=3600, stale-while-revalidate=86400" },
      ],
    },
    {
      source: "/visual-artifacts/(.*)",
      headers: [
        { key: "Cache-Control", value: "public, max-age=86400, immutable" },
      ],
    },
  ],
};

export default config;
