// Per-NodeKind visual styling: colour + relative size + glow

import type { NodeKind } from "./types";

export interface NodeStyle {
  color:    string;   // hex/rgb for Three.js material
  size:     number;   // val passed to react-force-graph nodeRelSize multiplier
  glow:     number;   // 0..1 emissive strength
  legend:   string;
}

export const NODE_STYLE: Record<NodeKind, NodeStyle> = {
  // Documents — cool cyan, the "files" of the corpus
  "document":                   { color: "#54d3ff", size: 5, glow: 0.4, legend: "Document" },

  // Agencies — bright gold, the "publishers" — anchor every document
  "agency":                     { color: "#ffd84d", size: 9, glow: 0.9, legend: "Agency" },

  // Incidents — orange, the anomalous events
  "incident":                   { color: "#ff9550", size: 6, glow: 0.7, legend: "Incident" },

  // Anonymised witnesses — pink
  "person":                     { color: "#ff77c0", size: 5, glow: 0.5, legend: "Person (USPER)" },

  // Operational structure — amber/violet/emerald
  "unit":                       { color: "#ffc857", size: 4, glow: 0.3, legend: "Unit" },
  "operation":                  { color: "#b888ff", size: 5, glow: 0.5, legend: "Operation" },
  "location":                   { color: "#5ee3a4", size: 4, glow: 0.3, legend: "Location" },

  // Time + classification — quieter
  "time-anchor":                { color: "#7d8597", size: 2, glow: 0.1, legend: "Time anchor" },
  "classification":             { color: "#ff6b6b", size: 3, glow: 0.4, legend: "Classification" },
  "foia-exemption":             { color: "#ff6b6b", size: 3, glow: 0.4, legend: "FOIA exemption" },

  // Claims (sparingly used in main graph — only manifest-disagreement claims)
  "claim":                      { color: "#e6e6e6", size: 3, glow: 0.3, legend: "Claim" },

  // Hyperedge hubs — distinctive shapes/colors
  "rel:mission":                { color: "#9d6cff", size: 4, glow: 0.6, legend: "Mission hyperedge" },
  "rel:incident-event":         { color: "#ffb347", size: 4, glow: 0.8, legend: "Incident-event hyperedge" },
  "rel:manifest-disagreement":  { color: "#ff4d6d", size: 5, glow: 0.9, legend: "Manifest disagreement" },
};

export const EDGE_COLOR: Record<string, string> = {
  "mission":               "#9d6cff",
  "incident-event":        "#ffb347",
  "incident-sequence":     "#5ee3a4",
  "manifest-disagreement": "#ff4d6d",
  "issued-by":             "#ffd84d",
};

export function styleFor(kind: NodeKind): NodeStyle {
  return NODE_STYLE[kind] ?? { color: "#ffffff", size: 3, glow: 0.2, legend: kind };
}
