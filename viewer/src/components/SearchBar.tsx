"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { GraphData, GraphNode } from "@/lib/types";
import { styleFor } from "@/lib/colors";

interface Props {
  data: GraphData;
  query: string;
  onQuery: (q: string) => void;
  onSelect: (id: string) => void;
}

export default function SearchBar({ data, query, onQuery, onSelect }: Props) {
  const [open, setOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Cmd/Ctrl-K to focus
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        inputRef.current?.focus();
        setOpen(true);
      }
      if (e.key === "Escape") {
        setOpen(false);
        inputRef.current?.blur();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    const out: GraphNode[] = [];
    for (const n of data.nodes) {
      const hay = [
        n.label, n.id,
        ...Object.values(n.attrs).map((v) => Array.isArray(v) ? v.join(" ") : String(v)),
      ].join(" ").toLowerCase();
      if (hay.includes(q)) out.push(n);
      if (out.length >= 50) break;
    }
    return out;
  }, [data, query]);

  return (
    <div className="relative w-full">
      <div className="glass flex items-center gap-2 px-3 py-2">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             strokeWidth="2" className="opacity-60">
          <circle cx="11" cy="11" r="7" />
          <path d="m20 20-3.5-3.5" />
        </svg>
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => { onQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          placeholder="Search documents, incidents, USPERs, locations… (⌘K)"
          className="w-full bg-transparent outline-none text-sm placeholder:text-fg-mute/70"
        />
        {query && (
          <button
            onClick={() => { onQuery(""); setOpen(false); }}
            className="text-xs text-fg-mute hover:text-fg"
          >clear</button>
        )}
      </div>
      {open && matches.length > 0 && (
        <div className="glass absolute mt-2 w-full max-h-[60vh] overflow-y-auto scroll-thin z-20">
          {matches.map((n) => {
            const s = styleFor(n.kind);
            return (
              <button
                key={n.id}
                onClick={() => { onSelect(n.id); setOpen(false); }}
                className="w-full text-left px-3 py-2 hover:bg-white/5 flex items-center gap-3 border-b border-stroke/30 last:border-0"
              >
                <span
                  className="w-2.5 h-2.5 rounded-full inline-block shrink-0"
                  style={{ background: s.color, boxShadow: `0 0 10px ${s.color}` }}
                />
                <span className="flex-1 truncate text-sm">{n.label}</span>
                <span className="text-xs text-fg-mute">{n.kind}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
