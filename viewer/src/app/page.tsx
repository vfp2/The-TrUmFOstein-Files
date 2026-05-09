"use client";

import { useEffect, useMemo, useState } from "react";
import Graph3D from "@/components/Graph3D";
import SearchBar from "@/components/SearchBar";
import FilterChips from "@/components/FilterChips";
import DetailPanel from "@/components/DetailPanel";
import StatsBadge from "@/components/StatsBadge";
import type { GraphData, NodeKind } from "@/lib/types";

const ALL_KINDS: NodeKind[] = [
  "document", "agency", "incident", "person", "unit", "operation", "location",
  "time-anchor", "classification", "foia-exemption", "claim",
  "rel:mission", "rel:incident-event", "rel:manifest-disagreement",
];

const DEFAULT_VISIBLE: NodeKind[] = [
  "document", "agency", "incident", "person", "unit", "operation", "location",
  "classification", "claim",
  "rel:mission", "rel:incident-event", "rel:manifest-disagreement",
  // time-anchor hidden by default — there are 116 of them and they
  // crowd the layout. User can toggle them back on.
];

export default function Page() {
  const [data, setData] = useState<GraphData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [visibleKinds, setVisibleKinds] = useState<Set<NodeKind>>(
    new Set(DEFAULT_VISIBLE)
  );
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    fetch("/graph.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`graph.json: HTTP ${r.status}`))))
      .then((d: GraphData) => setData(d))
      .catch((e: Error) => setError(e.message));
  }, []);

  const headerStats = useMemo(() => {
    if (!data) return null;
    return data;
  }, [data]);

  const onToggle = (kind: NodeKind) =>
    setVisibleKinds((prev) => {
      const next = new Set(prev);
      next.has(kind) ? next.delete(kind) : next.add(kind);
      return next;
    });

  return (
    <main className="relative w-screen h-screen overflow-hidden text-fg">
      {/* The 3D canvas fills the viewport */}
      <div className="absolute inset-0 z-0">
        {data && (
          <Graph3D
            data={data}
            visibleKinds={visibleKinds}
            searchQuery={query}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        )}
        {!data && !error && (
          <div className="absolute inset-0 flex items-center justify-center text-fg-mute">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 rounded-full border-2 border-stroke border-t-accent animate-spin"></div>
              <div className="text-sm">Loading substrate…</div>
            </div>
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center text-anomaly p-8 text-center">
            <div>
              <div className="text-lg font-medium mb-2">Couldn't load graph.json</div>
              <div className="text-sm text-fg-mute mb-4">{error}</div>
              <div className="text-xs text-fg-mute leading-relaxed max-w-md">
                Run <code className="font-mono px-1 py-0.5 rounded bg-white/10">python3 substrate/export/export_graph.py</code> from the repo root with TypeDB running on <code>localhost:1729</code>.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Top bar — title + search + stats */}
      <header className="absolute top-3 left-3 right-3 z-10 flex items-start gap-3 pointer-events-none">
        <div className="glass pointer-events-auto px-4 py-2.5 flex flex-col gap-0.5 shrink-0">
          <div className="text-[11px] tracking-[0.18em] uppercase text-fg-mute">
            The TrUmFOstein Files
          </div>
          <div className="text-sm font-medium leading-tight">
            PURSUE · war.gov/UFO · 8 May 2026
          </div>
        </div>
        <div className="flex-1 max-w-xl pointer-events-auto">
          {data && <SearchBar data={data} query={query} onQuery={setQuery} onSelect={setSelectedId} />}
        </div>
        <div className="pointer-events-auto">
          {headerStats && <StatsBadge data={headerStats} />}
        </div>
      </header>

      {/* Bottom bar — filter chips + legend hint */}
      {data && (
        <footer className="absolute bottom-3 left-3 right-3 z-10 flex items-end gap-3 pointer-events-none">
          <div className="pointer-events-auto max-w-3xl">
            <FilterChips data={data} visible={visibleKinds} onToggle={onToggle} />
          </div>
          <div className="ml-auto pointer-events-auto glass px-3 py-2 text-[11px] text-fg-mute">
            <kbd className="px-1.5 py-0.5 mr-1 rounded bg-white/10 text-fg">⌘K</kbd>search
            ·  drag to orbit  ·  scroll to zoom  ·  click any node
          </div>
        </footer>
      )}

      {/* Right detail panel */}
      {data && (
        <DetailPanel
          data={data}
          selectedId={selectedId}
          onSelect={setSelectedId}
          onClose={() => setSelectedId(null)}
        />
      )}
    </main>
  );
}
