"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import SpriteText from "three-spritetext";
import type { GraphData, GraphNode, NodeKind } from "@/lib/types";
import { styleFor, EDGE_COLOR } from "@/lib/colors";

// react-force-graph-3d uses Three.js + DOM and only runs client-side.
// Cast through unknown so we can use our own (looser) callback shapes —
// the runtime accessor signature is `(node) => …`, the package's strict
// generics require shapes we don't need.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ForceGraph3D = dynamic(() => import("react-force-graph-3d"), { ssr: false }) as unknown as React.ComponentType<any>;

interface Props {
  data: GraphData;
  visibleKinds: Set<NodeKind>;
  searchQuery: string;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

interface ForceNode extends GraphNode {
  // these get added by force-graph at runtime
  x?: number; y?: number; z?: number;
  fx?: number; fy?: number; fz?: number;
}

export default function Graph3D({
  data, visibleKinds, searchQuery, selectedId, onSelect,
}: Props) {
  const fgRef = useRef<unknown>(null);
  const [hoverNodeId, setHoverNodeId] = useState<string | null>(null);

  // Filter to currently visible kinds.
  const filtered = useMemo(() => {
    const nodes = data.nodes.filter((n) => visibleKinds.has(n.kind));
    const ids = new Set(nodes.map((n) => n.id));
    const links = data.edges.filter((e) => ids.has(e.source) && ids.has(e.target));
    return { nodes: nodes as ForceNode[], links };
  }, [data, visibleKinds]);

  // Search highlighting: a node is "matched" if its label or any attr value
  // contains the query (case-insensitive).
  const matchedIds = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return null;
    const set = new Set<string>();
    for (const n of filtered.nodes) {
      const hay = [
        n.label,
        n.id,
        ...Object.values(n.attrs).map((v) => Array.isArray(v) ? v.join(" ") : String(v)),
      ].join(" ").toLowerCase();
      if (hay.includes(q)) set.add(n.id);
    }
    return set;
  }, [filtered.nodes, searchQuery]);

  // Camera orbit auto-rotate after first frame for life
  useEffect(() => {
    const r = fgRef.current as { controls?: () => { autoRotate: boolean; autoRotateSpeed: number } } | null;
    if (!r?.controls) return;
    const ctrls = r.controls();
    ctrls.autoRotate = true;
    ctrls.autoRotateSpeed = 0.35;
  }, []);

  // Center camera on selected node smoothly
  useEffect(() => {
    if (!selectedId) return;
    const node = filtered.nodes.find((n) => n.id === selectedId) as ForceNode | undefined;
    if (!node || node.x == null) return;
    const r = fgRef.current as {
      cameraPosition?: (
        coords: { x: number; y: number; z: number },
        lookAt: { x: number; y: number; z: number },
        ms: number,
      ) => void;
    } | null;
    if (!r?.cameraPosition) return;
    const dist = 200;
    const ratio = 1 + dist / Math.hypot(node.x, node.y!, node.z!);
    r.cameraPosition(
      { x: node.x! * ratio, y: node.y! * ratio, z: node.z! * ratio },
      { x: node.x!, y: node.y!, z: node.z! },
      900,
    );
  }, [selectedId, filtered.nodes]);

  return (
    <ForceGraph3D
      ref={fgRef as never}
      graphData={filtered}
      backgroundColor="rgba(0,0,0,0)"
      nodeRelSize={4}
      nodeOpacity={0.95}
      linkOpacity={0.32}
      linkWidth={(l: { kind?: string }) =>
        l.kind === "manifest-disagreement" ? 2 :
        l.kind === "incident-sequence"     ? 1.6 : 0.6
      }
      linkColor={(l: { kind?: string }) =>
        EDGE_COLOR[l.kind ?? ""] ?? "rgba(255,255,255,0.32)"
      }
      linkDirectionalParticles={(l: { kind?: string }) =>
        l.kind === "incident-sequence" ? 4 :
        l.kind === "manifest-disagreement" ? 2 : 0
      }
      linkDirectionalParticleSpeed={0.005}
      linkDirectionalParticleColor={(l: { kind?: string }) =>
        EDGE_COLOR[l.kind ?? ""] ?? "#ffffff"
      }
      // Nodes — draw an emissive sphere with a sprite label that only
      // shows on hover/selection
      nodeThreeObject={(n: ForceNode) => {
        const s = styleFor(n.kind);
        const isMatched = matchedIds?.has(n.id) ?? false;
        const isSel = n.id === selectedId;
        const isHover = n.id === hoverNodeId;
        const dim = matchedIds && !isMatched && !isSel ? 0.18 : 1;
        const radius = s.size * (isSel ? 1.5 : isHover ? 1.25 : 1);

        const geom = new THREE.SphereGeometry(radius, 14, 14);
        const mat = new THREE.MeshStandardMaterial({
          color:           s.color,
          emissive:        s.color,
          emissiveIntensity: s.glow * (isSel ? 1.6 : 1),
          opacity:         dim,
          transparent:     true,
          roughness:       0.4,
          metalness:       0.1,
        });
        const mesh = new THREE.Mesh(geom, mat);

        if (isSel || isHover) {
          const text = new SpriteText(n.label.slice(0, 80));
          text.color = "#ffffff";
          text.backgroundColor = "rgba(15,20,32,0.92)";
          text.borderColor = s.color;
          text.borderWidth = 0.5;
          text.borderRadius = 4;
          text.padding = 3;
          text.textHeight = 4;
          text.position.set(0, radius + 5, 0);
          mesh.add(text);
        }
        return mesh;
      }}
      nodeThreeObjectExtend={false}
      onNodeClick={(n: { id: string }) => onSelect(n.id)}
      onNodeHover={(n: { id: string } | null) => setHoverNodeId(n?.id ?? null)}
      onBackgroundClick={() => onSelect(null)}
      enableNodeDrag={false}
      controlType="orbit"
      cooldownTicks={120}
      warmupTicks={20}
    />
  );
}
