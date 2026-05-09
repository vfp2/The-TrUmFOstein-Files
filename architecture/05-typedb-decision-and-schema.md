# 05 — TypeDB decision and substrate schema

*Status: open. Fifth entry. Closes the design phase; commits to a store and ships a working schema.*
*Date: 2026-05-08, ~23:00 UTC. Working corpus: 130/161 PDFs locally + the full UFO-USA OCR Markdown.*

[01](01-hypergraph-hypothesis-and-prior-art.md)–[04](04-native-pdf-analysis.md) explored. This entry **decides**, **schemas**, and **ships** the substrate.

## Decision

**Primary store: TypeDB 3.x.** Reasoning condensed from the prior entries:

- **Recursive composition** — entry 04 showed Mission Reports are tree-shaped hyperedges (Mission ⊃ Equipment / Personnel / Timeline / UAP-Event / Reaction / Observation / ISR), each layer 5–12-arity, total ~100 fields per MISREP. TypeDB is the only candidate where relations playing roles in other relations is a first-class primitive; the alternative stores need a reified-Incident node per layer.
- **n-ary fidelity** — UAP events with (witness, time, sensor, asset, location, signatures, classification, role-typed observers) collapse poorly to binary edges; TypeDB's role-typed n-ary relations handle this without reification.
- **Closed kind enum** — TypeDB's value-type / abstract-type system enforces the 9-value `kind` enum at write time, which is what we want.
- **Provenance** — page-level `(documentId, pageId, charStart, charEnd)` lives on the `claim` entity, not the hyperedge. TypeDB's weak provenance story (vs RDF-star's PROV-O nativity) doesn't matter once provenance is one layer down.
- **Cross-tranche durability** — `firstSeenAt / lastSeenAt / removedFromSource` lives at the manifest level; no native bitemporality required at the substrate.
- **Counter we accept**: TypeDB's ecosystem is smaller than Neo4j's. We'll take it.

The accompanying *supporting* layers (vocab extraction, manifest with removal-tracking, OCR fallback chain, page-level provenance, signature attestation) come from the patterns in [02](02-peer-substrate-survey.md). Nothing has changed in those.

## Schema

The TypeQL schema is committed at [`substrate/schema/schema.tql`](../substrate/schema/schema.tql); a brief tour here for the architectural log.

**Top-level entity types**:

```
document         — every PDF/file in the manifest
page             — every page of every document
claim            — atomic, page-linked, kind-typed assertion
                    (kind ∈ factual, witness, speculation, instruction,
                              procedural, metadata, analytical_assessment,
                              visual_artifact, redacted_placeholder)

agency           — DOW, FBI, NASA, DOS, NARA-prefixed record-groups, AARO, …
participant      ↳ abstract; subtypes:
  person                — named individual or USPER-anonymised
  unit                  — squadron, wing, AOC, CAOC (50 ATKS, 609 CAOC, 16 SOS, …)
  asset                 — typed-but-anonymised aircraft, often [1.4a]-redacted
  sensor                — FMV / IR / EO / SWIR / MX-20 / MX-25 / radar / NVG / …
  vessel                — Russian Navy hulls, etc. (Slava CG-055, Udaloy DD-626)
  craft                 — UAP / SU-30 / SU-27 / B-52 / generic enemy aircraft
operation        — INHERENT RESOLVE, OP HUMMER SICKLE, OP PHANTOM FLEX
location         — typed: ICAO, MGRS-grid, place-name, grid-area
time_anchor      — Zulu DTG, calendar date, year, period (e.g. dusk on 2 days)
classification   — SECRET, REL TO USA FVEY, NOFORN, FOUO, CUI, UNCLASSIFIED, …
foia_exemption   — (b)(1), (b)(3), (b)(6), (b)(7), [1.4a], [3.5c], …
incident         — the analytical anchor; participants joined via hyperedge
```

**The hyperedge primitive** (TypeDB `relation`s with role types):

```
incident                         — top-level UAP / sighting / event
  roles: anchor-time, anchor-location, witness, asset, sensor,
         craft (the UAP itself or conventional aircraft), observation-method,
         classification, originating-document

mission                          — DOW MISREP envelope
  roles: operation, domain (AIR/SEA/LAND), ops-center, MAJCOM, COCOM,
         originating-unit, classification, declassification-authority,
         report-type, contains-event*  ← contains incidents/reactions/observations/ISR

equipment-loadout                — ACEQUIP block
  roles: aircraft-callsign, radar, RWR, MWS, IRCM, ECM, CMD,
         chaff, flares, AAM-radar, AAM-IR, gun, TGT-pod, avionics, data-link

personnel-chain                  — POC/QC/APPROVER/INGEST
  roles: poc, qc, approver, ingest

personnel-entry
  roles: person, rank, unit, wing, ops-center, contact-method

timeline                         — Mission timeline
  roles: takeoff, landing, on-station, off-station

mission-event
  roles: location, time, callsign, activity-type

reaction                         — friendly-vs-enemy aircraft encounter
  roles: friendly-asset, enemy-craft, time, location, distance,
         enemy-formation, source-of-id, results

observation                      — discrete sighting of conventional asset
  roles: observer-asset, observed-craft, time, location,
         observation-method, certainty (probable/confirmed)

isr-collection                   — ISR target list
  roles: observer-asset, time-on, time-off, supported-unit,
         supported-operation, target* ← multi-arity over geographic targets

vessel-observation               — sub-relation under isr-collection
  roles: vessel, hull-number, time, location, heading, certainty

contradicts                      — derived relation, axis-typed
  roles: claim-a, claim-b
  attribute: axis ∈ {date, location, morphology, witness-count, sensor-modality, …}

incident-sequence                — temporal/sequence link between incidents
  roles: source-incident, target-incident
  attribute: kind ∈ {temporal-sequence, comparative, re-described, follow-up}

manifest-disagreement            — D28-style: source metadata ≠ body content
  roles: document, manifest-claim, body-claim
  attribute: field ∈ {location, title, agency, incident-date, …}
```

**Document-shape taxonomy** (from [04](04-native-pdf-analysis.md)) is a queryable attribute on `document`:

```
document.shape ∈ {
  mission-report,           — DOW MISREP (~45)
  range-fouler-debrief,     — DOW debrief form (~10)
  crew-transcript,          — NASA Apollo/Gemini/Skylab (~7)
  state-cable,              — DOS telegram (~5)
  fbi-hq-section,           — bulk historical correspondence (~16)
  multi-incident-deck,      — slide deck like Western US (1+)
  email-correspondence,     — process emails (~3)
  visual-artifact,          — pure-image (composite sketch + 24 FBI photos)
  nara-historical,          — 1944–1965 archival (~15)
  unknown,                  — fallback during ingestion
}
```

**Claim provenance** is a relation, not nested fields:

```
claim-provenance
  roles: claim, page, document
  attributes: char-start, char-end, extraction-method (regex|gemini|pdfplumber|tesseract|gpt-4o|claude-vision)
```

## Ingestion pipeline

Lives at [`substrate/ingest/`](../substrate/ingest/), composed of stages that can run independently and idempotently:

1. **Manifest ingest** — `uap-csv.csv` + `data/records.json` → 161 `document` entities with `firstSeenAt`, `lastSeenAt`, `removedFromSource`, `acquisitionStatus ∈ {downloaded, download_failed, not_attempted}`.
2. **Shape detection** — filename prefix (uap-release-analyzer's table) + first-page features → `document.shape`.
3. **Document-text load** — UFO-USA's `converted/` Markdown → `page` entities + raw text (one source-of-truth for now; native PDF reading on demand for high-stakes per-document re-extraction).
4. **Vocab + regex extraction** — analyzer base + the operational extension authored in [03 §Q4](03-empirical-calibration.md). Surfaces `agency`, `participant` mentions, `time_anchor`, `location`, `classification`, `foia_exemption`. These become `claim`s with `extraction_method=regex`.
5. **Shape-specific extractors**:
   - **Mission Report extractor** — parses YAML-like form fields directly (`Operation:`, `MAJCOM:`, `COCOM:`, `Aircraft Callsign:`, `Initial Contact DTG:`, etc.) into `mission`, `equipment-loadout`, `personnel-chain`, `timeline`, `reaction`, `observation`, `isr-collection` relations. Highest-fidelity path.
   - **Multi-incident deck extractor** — slide segmentation by H1/title heuristic → one `incident` per slide; USPER tokens preserved as `person.anonymised_token`.
   - **State cable extractor** — telegram header parse (MRN, DTG, From, Action, Subject) + numbered-paragraph segmentation.
   - **Visual artifact extractor** — for the 25 image-only docs, a `claim(kind=visual_artifact, depicted_subject=…)` from a one-shot Claude vision pass on the PDF.
   - **Other shapes** — minimum-viable: a `document` entity, page text, and analyzer-vocab claims, leaving deeper extraction for a later pass.
6. **Manifest-disagreement detection** — the D28 case generalises: any document where `manifest.location` (from CSV) doesn't substring-match any extracted `location` claim from the body gets a `manifest-disagreement` relation with `field=location`. Same for title, incident-date.
7. **Insert into TypeDB** — driven by the TypeDB Python driver (`typedb-driver`), using TypeQL `insert` queries assembled per document.

## What gets loaded *now* vs deferred

This entry ships an end-to-end working substrate, but at variable fidelity per shape:

| Shape | Documents | Extraction depth this round |
|---|---|---|
| `mission-report` | ~45 | Full structured-form extraction → all sub-relations |
| `multi-incident-deck` | 1 | Full per-slide incidents + USPER participants |
| `state-cable` | ~5 | Header + numbered-paragraph claims |
| `visual-artifact` | ~25 | Stub `document` + `claim(kind=visual_artifact)` from native PDF |
| `crew-transcript` | ~7 | `document` + page-level claims via vocab extraction |
| `email-correspondence` | ~3 | `document` + tear-line claim |
| `range-fouler-debrief` | ~10 | `document` + page-level claims |
| `fbi-hq-section` | ~16 sections (3000+ pages) | `document` + sampled-page claims; deep extraction deferred |
| `nara-historical` | ~15 | `document` + sampled-page claims; deep extraction deferred |

**Demonstration queries** the build must pass (TypeQL):

```typeql
# Q1: Surface the D28 manifest disagreement
match
  $disagreement isa manifest-disagreement,
    has field "location";
  $disagreement (document: $d, manifest-claim: $mc, body-claim: $bc);
  $d has filename "dow-uap-d28-mission-report-east-china-sea-2024.pdf";
  $mc has text $manifest_loc;
  $bc has text $body_loc;

# Q2: All UAP observations during PGM/weapons release in Iraq, 2024
match
  $i isa incident, has anchor-year 2024;
  ($i, location: $l) isa-relation;
  $l has place-name $place;
  { $place contains "Iraq"; } or { $place contains "AYN AL ASAD"; };
  ($i, contains-event: $event) isa-relation;
  $event has activity "PGM";

# Q3: All incidents involving USPER5 + USPER6
match
  $usper5 isa person, has anonymised-token "USPER5";
  $usper6 isa person, has anonymised-token "USPER6";
  ($i1, witness: $usper5, witness: $usper6) isa incident;
```

(Exact TypeQL adapted to TypeDB 3.x syntax in the actual schema/queries.)

## Risks and what we do not yet do

- **Extraction quality varies by shape.** MISREPs and slide decks are tractable; FBI HQ bulk correspondence is not at this fidelity. Deferred deep extraction is captured in `claim` density per document — measurable.
- **TypeQL 3.x syntax differences** from older TypeQL examples may catch us. We pin the TypeDB version explicitly in `substrate/Dockerfile` and verify against the running server.
- **The store choice is committed but reversible.** The schema is expressive enough that an export to RDF-star or property-graph + reified incidents is mechanical; the real lock-in is the *modelling decisions*, which are largely store-agnostic.
- **No analytical UI or query notebook in this entry.** The substrate is loaded; the surface (CLI, notebook, dashboard) is the next entry's work.

## Open for entry 06

1. **Quantify extraction completeness** per shape against the actual loaded corpus — claim density, MISREP form-field coverage, deferred-extraction TODO list.
2. **Deeper FBI HQ section extraction** — the 3000+ pages of bulk correspondence have rich content (Kenneth Arnold, William Rhodes, etc.) that's not captured by the analyzer-vocab pass alone.
3. **Cross-document USPER linking** — USPERs in the Western US deck might recur in other documents; the substrate should support that.
4. **The query / synthesis surface** — what does an analyst do with the loaded substrate? Notebook? CLI? Saved-question dashboard?
5. **Tranche-2 readiness drill** — when war.gov drops tranche 2, can the substrate ingest it without re-running tranche 1? The `firstSeenAt / lastSeenAt / removedFromSource` plumbing should make this trivial; verify.
