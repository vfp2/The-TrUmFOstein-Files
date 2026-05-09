# Graph-view queries for TypeDB Studio

These queries are tuned for **Studio's graph visualization tab**, not the tabular results tab. The previous queries in [`../`](..) use `select $name, $count;` to return attribute values — perfect for tables, useless for graph rendering because there are no concepts to draw.

## How Studio renders graph results

Studio's graph view draws a node for **every concept** returned by a query and an edge for **every relation**. Two rules:

1. **Bind whole entities and relations** as variables. `match $i isa incident; …` puts an `incident` node on the canvas. `match $ie isa incident-event; …` puts the relation on the canvas with edges to all of its role-players (which Studio also draws as nodes — that's the n-ary fanout).
2. **Avoid `reduce`, `count`, and value-only `select`.** Those collapse to scalars and the graph view has nothing to draw.

Once the graph is drawn:

- **Drag** nodes to rearrange.
- **Double-click** any node to expand it — Studio fetches its neighbours (other relations it plays a role in) and adds them to the canvas. This is how you *navigate* the substrate.
- **Right-click** a node for context options (focus, hide, expand by relation type).
- **Schema tab** renders the entire schema as a separate graph (entity types, relation types, attribute types, role edges). Useful to start with for an overview.

## Recommended starting sequence in Studio

1. **Connect** to `localhost:1729` (admin / password, TLS off), select the `trumfostein` database.
2. **Schema tab first** — gives you the architecture (claim ↔ page ↔ document at the bottom; mission, incident-event, isr-collection as the n-ary hyperedges in the middle; manifest-disagreement and incident-sequence as the derived layer at the top).
3. **Switch to the Query tab**, paste [`g1_all_incidents_with_participants.tql`](g1_all_incidents_with_participants.tql) — gives you all 22 incidents and their role-players in one canvas. Most visually rich starting point.
4. **Paste [`g2_western_us_subgraph.tql`](g2_western_us_subgraph.tql)** — small focused subgraph (1 document → 4 incidents → 7 USPER persons → 1 temporal-sequence edge). Best for understanding the multi-incident-deck pattern.
5. From any node, **double-click to expand**. For example: double-click the document node to see all the claims attached to it; double-click an incident to see the missions that contain it.

## Query files

| File | Returns | Best for |
|---|---|---|
| [g1_all_incidents_with_participants.tql](g1_all_incidents_with_participants.tql) | All 22 incident-event hyperedges with their incidents, witnesses, times, locations, documents | Top-level overview of the n-ary primitive |
| [g2_western_us_subgraph.tql](g2_western_us_subgraph.tql) | 1 document → 4 incidents → 7 USPER persons → 1 sequence | Demonstrating multi-incident-document + anonymised participants |
| [g3_d28_mission_neighborhood.tql](g3_d28_mission_neighborhood.tql) | D28's full mission hyperedge: operation, COCOM, MAJCOM, ops-center, originator, contained incident | The hierarchical hyperedge from architecture/04 |
| [g4_d28_manifest_disagreement.tql](g4_d28_manifest_disagreement.tql) | D28 + the manifest-disagreement relation + both claim sides | The "trust the PDF, not the manifest" architectural finding made visible |
| [g5_all_missions_by_operation.tql](g5_all_missions_by_operation.tql) | Every mission and its operation | See INHERENT RESOLVE clustering and operation diversity at a glance |
| [g6_usper_cross_incident.tql](g6_usper_cross_incident.tql) | USPER5 + USPER6 + every incident-event they both witness | The n-ary witness query as a graph |
| [g7_d28_pages_and_claims.tql](g7_d28_pages_and_claims.tql) | D28's document → pages → first-page claims | Page-level provenance traceability |
| [g8_visual_artifacts_with_descriptions.tql](g8_visual_artifacts_with_descriptions.tql) | All 33 visual-artifact documents and their claude-vision claims | The corpus's visual evidence layer |

## Two warnings about the graph

- The **9,615 vocab claims** would crush the graph if loaded all at once. The graph queries here intentionally limit scope or filter to specific shapes/kinds. If you want to explore vocab claims for one document, use the limit-by-document pattern in [`g7_d28_pages_and_claims.tql`](g7_d28_pages_and_claims.tql).
- Studio's auto-layout can scramble large graphs. After running, manually drag the central nodes (incidents, missions) into a useful position; the satellites usually settle.
