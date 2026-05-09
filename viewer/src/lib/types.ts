// Types for the static graph.json shape produced by substrate/export/export_graph.py

export type NodeKind =
  | "document"
  | "agency"
  | "incident"
  | "person"
  | "unit"
  | "operation"
  | "location"
  | "time-anchor"
  | "classification"
  | "foia-exemption"
  | "claim"
  | "rel:mission"
  | "rel:incident-event"
  | "rel:manifest-disagreement";

export interface GraphNode {
  id: string;
  kind: NodeKind;
  label: string;
  attrs: Record<string, string | number | boolean | string[]>;
}

export interface GraphEdge {
  source: string;
  target: string;
  kind: string;
  role?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    node_count: number;
    edge_count: number;
    kind_counts: Record<string, number>;
  };
}

export interface DocBundle {
  document: string;
  pages: Array<{ id: string; page: number; text: string }>;
  claims: Array<{ id: string; kind: string; text: string; method: string }>;
  total_claims: number;
}
