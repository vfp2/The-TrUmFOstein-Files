# substrate/

The TypeDB-backed substrate that loads the war.gov PURSUE corpus into the
architecture from [../architecture/](../architecture/). This is the first
working version: schema in [`schema/schema.tql`](schema/schema.tql),
ingestion in [`ingest/`](ingest/), verification in [`queries/`](queries/).

## Prerequisites

- **Docker**: TypeDB Core 3.x runs as a container (no Java needed — TypeDB 3.x is Rust-native).
- **Python 3.10+** with the `typedb-driver` package (`pip install typedb-driver`).
- The corpus prerequisites:
  - PDFs at `/home/soliax/dev/vfp2/ufouap/pdfs/` (downloaded via the preserved [`vfp2/pursue-ufo-files`](https://github.com/vfp2/pursue-ufo-files)).
  - UFO-USA OCR Markdown at `/home/soliax/Documents/github/vfp2/UFO-USA/converted/`.
  - Manifest JSON at `/home/soliax/dev/vfp2/ufouap/data/records.json`.

## Run from scratch

```bash
# 1. Start TypeDB (gRPC :1729, HTTP :8000)
docker run -d --name typedb-trumfostein -p 1729:1729 typedb/typedb:latest

# 2. Load schema (drops the trumfostein DB if present, then re-creates)
python3 substrate/ingest/00_load_schema.py

# 3. Ingest the manifest → 161 document entities
python3 substrate/ingest/01_manifest.py

# 4. Load pages + vocab-extracted claims (~30s for 4174 pages, 9615 claims)
python3 substrate/ingest/02_pages_and_claims.py

# 5. Structured extraction for high-value shapes
python3 substrate/ingest/03_misreps_and_specials.py

# 6. Verify
python3 substrate/queries/verify.py
```

## What's loaded

After running stages 0–3 against the May 8, 2026 PURSUE Release 01:

| Concept | Count |
|---|---|
| `document`            | 161 |
| `page`                | 4,174 |
| `claim`               | 9,654 |
| `incident`            | 22 |
| `mission` (relation)  | 46 |
| `incident-event` (relation) | 22 |
| `incident-sequence` (relation) | 1 |
| `manifest-disagreement` (relation) | 1 |
| `claim-provenance` (relation) | 9,654 |
| `has-page` (relation) | 4,174 |
| Person (USPER1–USPER7 anonymised) | 7 |
| `operation`           | 10 |
| `unit`                | 21 |

## Coverage by document shape

| Shape | Documents | Extraction |
|---|---|---|
| `mission-report`            | 46 | Structured form-fields → `mission`, `operation`, `unit`, `time-anchor`, `location`, `incident`, `incident-event` |
| `multi-incident-deck`       | 1  | 4 incidents + 7 USPER persons + 1 temporal-sequence relation (full) |
| `visual-artifact`           | 37 | One `claim(kind=visual_artifact)` per doc; composite-sketch enriched from native Claude PDF read |
| `fbi-hq-section`            | 19 | Pages + vocab claims (deeper structured extraction deferred) |
| `nara-historical`           | 13 | Pages + vocab claims (deferred) |
| `range-fouler-debrief`      | 6  | Pages + vocab claims (form structure similar to MISREP — could share extractor) |
| `crew-transcript`           | 6  | Pages + vocab claims (deferred dialogue parser) |
| `state-cable`               | 5  | Pages + vocab claims (deferred telegram parser) |
| `email-correspondence`      | 3  | Pages + vocab claims (deferred tear-line extractor) |
| `unknown`                   | 25 | Pages + vocab claims; mostly DVIDS video records and edge cases |

## Demonstration queries

The verify script exercises the architectural decisions:

- **Q1 — D28 manifest disagreement**: surfaces the war.gov-says-East-China-Sea-but-content-says-Iraq mismatch as data, per [`architecture/04`](../architecture/04-native-pdf-analysis.md). Both claims are preserved, joined by a `manifest-disagreement` relation.
- **Q2 — USPER5 ∩ USPER6**: returns all 4 Western US incidents, demonstrating the typed-anonymised-participant design from [`architecture/03 §Q5`](../architecture/03-empirical-calibration.md) and the multi-incident-document case from [`architecture/04`](../architecture/04-native-pdf-analysis.md).
- **Q3 — incident-sequence**: surfaces the "Transparent Kite ~30 minutes after Dark Kite" temporal-sequence edge.
- **Q4 / Q5 — missions by COCOM / Operation**: demonstrates the `mission` hyperedge with role-typed participants. INHERENT RESOLVE has 10 missions across the corpus.
- **Q9 — claim density per shape**: extraction-completeness telemetry; useful for spotting under-extracted shapes.

## Schema highlights

- **Hierarchical hyperedges**: `mission` contains-incident / contains-reaction / contains-observation / contains-isr — each itself a multi-arity relation. Recursive composition is the reason TypeDB won the [`architecture/05`](../architecture/05-typedb-decision-and-schema.md) decision.
- **9-value `kind` enum** on `claim`: `factual / witness / speculation / instruction / procedural / metadata / analytical_assessment / visual_artifact / redacted_placeholder` (the latter with sub-types `redacted_inline / redacted_block / redacted_whole_page`).
- **Manifest-vs-body disagreement** as a first-class relation type, not an exception.
- **Cross-tranche durability** via `acquisition-status`, `first-seen-at`, `last-seen-at`, `removed-from-source` on `document`.

## What this version does NOT yet do

- Deeper structured extraction for FBI HQ sections, NARA historical, NASA crew transcripts, State cables, email correspondence beyond vocab-level claims.
- Sub-relations under `mission`: equipment-loadout, personnel-chain, timeline, reaction-event, observation-event, isr-collection are defined in the schema but populated only at the top level. The MISREP extractor builds the `mission` envelope and the central `incident-event`; full sub-relations land in the next iteration.
- Cross-document USPER linking — if the same anonymised token recurs in a future document, we should match it; right now USPERs only exist in the Western US deck.
- Vision-LLM transcription for the 37 visual-artifact documents (placeholder claims are present; the composite-sketch is the only one with an enriched description).
- A query/synthesis surface beyond the verify script — notebook, CLI, dashboard.

These are tracked in [`architecture/05` Open for entry 06](../architecture/05-typedb-decision-and-schema.md#open-for-entry-06).

## Server lifecycle

```bash
# stop / restart
docker stop typedb-trumfostein
docker start typedb-trumfostein

# reset (drops all data)
docker rm -f typedb-trumfostein
docker run -d --name typedb-trumfostein -p 1729:1729 typedb/typedb:latest

# query interactively
docker exec -it typedb-trumfostein /opt/typedb-server-linux-x86_64/typedb console
```
