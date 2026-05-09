"use client";

import type { GraphData } from "@/lib/types";

export default function StatsBadge({ data }: { data: GraphData }) {
  const k = data.stats.kind_counts;
  return (
    <div className="glass px-3 py-2 text-xs flex items-center gap-3 leading-tight">
      <div className="flex flex-col">
        <span className="text-fg-mute">documents</span>
        <span className="font-medium tabular-nums">{k["document"] ?? 0}</span>
      </div>
      <span className="opacity-30">·</span>
      <div className="flex flex-col">
        <span className="text-fg-mute">incidents</span>
        <span className="font-medium tabular-nums">{k["incident"] ?? 0}</span>
      </div>
      <span className="opacity-30">·</span>
      <div className="flex flex-col">
        <span className="text-fg-mute">missions</span>
        <span className="font-medium tabular-nums">{k["rel:mission"] ?? 0}</span>
      </div>
      <span className="opacity-30">·</span>
      <div className="flex flex-col">
        <span className="text-fg-mute">USPER</span>
        <span className="font-medium tabular-nums">{k["person"] ?? 0}</span>
      </div>
      <span className="opacity-30">·</span>
      <div className="flex flex-col">
        <span className="text-fg-mute">edges</span>
        <span className="font-medium tabular-nums">{data.stats.edge_count}</span>
      </div>
    </div>
  );
}
