"use client";

import type { GraphData, NodeKind } from "@/lib/types";
import { styleFor } from "@/lib/colors";

interface Props {
  data: GraphData;
  visible: Set<NodeKind>;
  onToggle: (kind: NodeKind) => void;
}

const ORDER: NodeKind[] = [
  "agency",
  "document",
  "incident",
  "person",
  "location",
  "operation",
  "unit",
  "classification",
  "time-anchor",
  "rel:mission",
  "rel:incident-event",
  "rel:manifest-disagreement",
  "claim",
];

export default function FilterChips({ data, visible, onToggle }: Props) {
  const counts = data.stats.kind_counts;
  return (
    <div className="glass p-3 flex flex-wrap gap-1.5">
      {ORDER.map((k) => {
        const n = counts[k] ?? 0;
        if (!n) return null;
        const s = styleFor(k);
        const on = visible.has(k);
        return (
          <button
            key={k}
            onClick={() => onToggle(k)}
            className={[
              "text-xs px-2 py-1 rounded-md flex items-center gap-1.5 transition",
              on
                ? "bg-white/[0.08] border border-stroke-strong/70"
                : "bg-transparent border border-stroke/40 opacity-50 hover:opacity-80",
            ].join(" ")}
            title={s.legend}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ background: s.color, boxShadow: on ? `0 0 8px ${s.color}` : "none" }}
            />
            <span>{s.legend}</span>
            <span className="text-fg-mute tabular-nums">{n}</span>
          </button>
        );
      })}
    </div>
  );
}
