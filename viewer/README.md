# viewer/

> **Live**: [**the-trumfostein-files.vercel.app**](https://the-trumfostein-files.vercel.app)

Beautiful 3D navigable view of the TypeDB substrate from
[`../substrate/`](../substrate/), packaged as a single
**Next.js 16 / React 19 / TypeScript / Tailwind v4** app. Deploys to
**Vercel** with no live database dependency at runtime — the entire
graph is exported to a static `graph.json` ahead of time.

## What you get in the browser

- A live 3D force-directed graph of every Tier-1 entity and hyperedge
  in the substrate (~400 nodes / ~200 edges by default), rendered with
  `react-force-graph-3d` on a dark starfield background.
- Per-NodeKind colour, size, and glow — documents (cyan), incidents
  (orange), USPER persons (pink), missions (violet hyperedge hubs),
  manifest-disagreement (red hyperedge hub), and so on.
- **Cmd/Ctrl-K search** across labels and attributes — auto-completes
  to a clickable list of matching nodes.
- **Filter chips** along the bottom to toggle node kinds in/out
  (time-anchors are off by default to keep the layout readable).
- **Detail panel** when you click any node:
  - All its attributes (with hyperlinked URLs).
  - Connected nodes (incoming + outgoing) with their roles, click to
    pivot.
  - For documents: a `Document` tab embedding the PDF or PNG inline
    when bundled, or a war.gov link when it's not; a `Claims` tab
    showing the structured (non-vocab) claims; a `Pages` tab with the
    raw OCR text per page, expandable.
- Animated camera fly-to on selection.
- Subtle auto-orbit on idle.

## How the data gets in

Two stages, both reproducible from the repo:

```bash
# 1. Make sure TypeDB is running and the substrate is loaded — see ../substrate/README.md
docker ps --filter name=typedb-trumfostein   # should be Up
python3 ../substrate/ingest/00_load_schema.py
python3 ../substrate/ingest/01_manifest.py
python3 ../substrate/ingest/02_pages_and_claims.py
python3 ../substrate/ingest/03_misreps_and_specials.py
python3 ../substrate/ingest/04_visual_real_descriptions.py

# 2. Export the substrate to viewer/public/graph.json + per-doc bundles
python3 ../substrate/export/export_graph.py
# -> Exported 403 nodes, 206 edges → viewer/public/graph.json
# -> Per-doc bundles → viewer/public/docs/<doc-id>.json (161 docs)
```

Re-run step 2 whenever the substrate changes.

## Run locally

```bash
cd viewer
npm install
npm run dev
# -> http://localhost:3000
```

## Deploy to Vercel

The viewer is a pure static-friendly Next.js app — no API routes, no
DB connection at runtime. It deploys cleanly with the standard
defaults.

```bash
cd viewer
vercel             # first time: link the project, accept defaults
vercel --prod      # production deploy
```

`vercel.ts` (in this directory) sets framework + cache headers per the
Vercel session-start guidance. No `vercel.json` required.

The bundled visual-artifact assets in `public/visual-artifacts/`
(8 PNGs + 24 PDFs + 1 sketch, ~13 MB total) ship as static files.
Mission Report PDFs are *not* bundled — they're 2.4 GB total at
war.gov — and are linked directly to the source URLs in the manifest.

## Tech stack

| Layer | Choice |
|---|---|
| Framework | Next.js 16 (App Router) |
| UI       | React 19 + Tailwind CSS v4 (custom theme via `@theme`) |
| Graph    | [`react-force-graph-3d`](https://github.com/vasturiano/react-force-graph) (Three.js + d3-force) |
| Sprites  | `three-spritetext` for hover labels |
| Static data | `public/graph.json` (66 KB) + `public/docs/<id>.json` (~2 KB each) |

## File map

```
viewer/
├── README.md                     this file
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
├── vercel.ts                     framework + cache headers
├── public/
│   ├── graph.json                exported substrate (regenerate via export script)
│   ├── docs/<doc-id>.json        per-doc pages + claims, lazy-loaded on click
│   └── visual-artifacts/         bundled PNGs + small PDFs (FBI Photo A/B + sketch)
└── src/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx              top-level state, layout, panels
    │   └── globals.css           Tailwind + theme + starfield
    ├── components/
    │   ├── Graph3D.tsx           react-force-graph-3d wrapper
    │   ├── SearchBar.tsx         ⌘K-focused autocomplete
    │   ├── FilterChips.tsx       toggle node kinds
    │   ├── DetailPanel.tsx       slide-in panel; embeds PDFs/PNGs
    │   └── StatsBadge.tsx        top-right counts
    └── lib/
        ├── types.ts              GraphData / NodeKind / DocBundle
        └── colors.ts             per-kind palette + glow + size
```

## Known limitations

- `time-anchor` nodes (~116) are filtered out by default. Toggle the
  chip if you want to see them — but they currently have minimal
  context attached and clutter the layout.
- Mission Report PDFs link to war.gov and depend on the source being
  reachable. If war.gov rotates Akamai cookies or the URL pattern, the
  inline iframe may fail. The PDFs themselves are also not bundleable
  on Vercel's free tier (2.4 GB total). Production deploy should
  proxy via Vercel Blob or R2 — see `architecture/05` open questions.
- Search is case-insensitive substring across all attribute values; no
  full-text index. Fine for ~400 nodes, would need MiniSearch or
  similar at corpus scale beyond a few thousand nodes.
- Vocab claims (kind=metadata, ~9,600) are not in `graph.json` —
  they would crush the layout. They appear in per-doc bundles only,
  filtered out from the Claims tab to leave just the structured ones.

## What this is not, yet

A polished product. It's an architectural artefact — the substrate
made navigable. The next iterations should add: full-text search
across page bodies, a timeline view orthogonal to the graph, video
playback for the DVIDS records that aren't yet in the manifest,
and a sharable URL state so users can deep-link to a specific node
selection.
