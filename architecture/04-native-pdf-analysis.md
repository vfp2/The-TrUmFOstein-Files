# 04 — Native PDF analysis: document-shape diversity and substrate updates

*Status: open. Fourth entry in the ongoing architectural discussion. Updates [03](03-empirical-calibration.md) — most importantly its arity bound — using direct Claude vision-capable PDF reads.*
*Date: 2026-05-08, ~22:30 UTC. Working corpus: PDFs at `/home/soliax/dev/vfp2/ufouap/pdfs/` (116 of ~161 successfully downloaded via [pursue-ufo-files](../../pursue-ufo-files/), per `data/download-failures.json` showing 111 retry events with `page.evaluate: Target page, context or browser has been closed` — Playwright browser termination, not server rejection).*

[03](03-empirical-calibration.md) calibrated the substrate against UFO-USA's OCR'd Markdown and concluded incident arity is bounded ≤ 12. **That conclusion was an artefact of looking only at narrative event participants and missing the structured form fields around them.** Reading the actual PDFs natively — Claude's vision-capable PDF mode renders layout, embedded figures, redaction visual style, and recovers page semantics that text-only OCR collapses — surfaces a different picture.

Four PDFs read in this pass:

| File | Type | Pages |
|---|---|---|
| `dow-uap-d28-mission-report-east-china-sea-2024.pdf` | DOW Mission Report | 6 |
| `western_us_event_slides_5.08.2026.pdf` | Multi-incident slide deck | 4 |
| `2024-04-30-composite-sketch.pdf` | Pure-image visual artifact | 1 |
| `dow-uap-d52-email-correspondance-na-august-2024.pdf` | Internal disclosure-process email | 2 |

Each one teaches something distinct about the substrate.

## Findings per document

### `dow-uap-d28` — Iraq, not East China Sea, and ~100 typed fields per MISREP

**The filename is wrong.** The PDF is titled `dow-uap-d28-mission-report-east-china-sea-2024.pdf` at war.gov, and the source `uap-csv.csv` manifest carries the same "East China Sea" titling. **The actual content is unambiguously Iraq**: ARMED OVERWATCH at AYN AL ASAD AIRBASE (AAAB), takeoff and landing at OKAS (Al Asad ICAO), Restricted Operating Zone RAINDROP, the dates 20–21 SEP 24, weapons release of an AGM-176, and grid coordinates `38SKC63` (an MGRS grid in Iraq, not the East China Sea). UFO-USA's folder name [`045-DOW-UAP-D28-_Mission_Report-_Iraq-_September_2024`](../../UFO-USA/converted/045-DOW-UAP-D28-_Mission_Report-_Iraq-_September_2024/) is correct; **war.gov's source titling is not**.

This is a **page-level provenance win**. Anything we extract from this document and tag with "East China Sea" because we trusted the filename will be subtly wrong; anything tagged with "Iraq" because we read the body text will be right. Architecturally: **trust PDF content over manifest metadata, and surface the disagreement as data, not silently overwrite**.

The bigger structural finding is the **MISREP form depth**. The visible structured fields across the 6 pages are:

| Section | Field count | Examples |
|---|---|---|
| Document header | 4 | declass authority, declass date, classification + caveats |
| `CLASSIFICATION` | 4 | Classification, Caveats, Source, Declass Date |
| `OPERATION` | 5 | Operation, Domain, Ops Center, MAJCOM, COCOM |
| `MSGID` | 3 | Report Type, Originator, Submit Date |
| `MSNID` | 5 | Tasking Order, Mission Type, ATO Mission Number, Country, Service |
| `POC / QC / APPROVER / INGEST` | ~9 each = ~36 | Rank, Full Name, Unit, Wing, Phone, Email, Service, Ops Center |
| `ACEQUIP` | ~30 | Aircraft Callsign, Radar (4 fields), RWR (4), MWS (4), IRCM (4), ECM (4), CMD, Chaff, Flares, AAM, Gun, TGT Pod, Avionics, Data Link, Gentext |
| `Timeline` (Takeoff, Landing, On Station, Off Station) | ~16 | Each with Callsign, ICAO, DTG, gentext, etc. |
| `UAP` event | ~40 | Initial Contact DTG, Maneuverability, Response, MDS Type, Aircraft Loc/Alt/Speed/Trajectory, Observer Assessment, Op Range, Physical State, Propulsion, Signatures, Serial Number, observer Rank/Name/Email, Kinetic Altitude/Depth/Velocity/Trajectory (each with Accuracy), First/Last Coordinate, etc. |
| `GENTEXT/UAP` | 2 narrative blocks | Description, Event Description |

**Total typed fields ≈ 95–105** before counting nested gentext. **Entry 03's arity-≤-12 conclusion was wrong by an order of magnitude** — but only because it was measuring the wrong thing. The narrative event still has 8–11 participants ("UAP flew through sensor between munition release and impact") — that part of [03](03-empirical-calibration.md) holds. What entry 03 missed is that a Mission Report is a **hierarchical composition** where each section is itself a structured n-ary record:

```
Mission(operation, domain, ops-center, MAJCOM, COCOM, classification, ...)
├── Equipment-loadout(callsign, radar, RWR, MWS, IRCM, ECM, weapons, sensors, ...)
├── Personnel-chain(POC, QC, APPROVER, INGEST)
│   ├── POC(rank, name, unit, wing, contact, ...)
│   ├── QC(rank, name, unit, wing, contact, ...)
│   ├── APPROVER(rank, name, unit, wing, contact, ...)
│   └── INGEST(...)
├── Timeline(Takeoff, Landing, On-Station, Off-Station)
│   ├── Takeoff(callsign, ICAO, DTG, ...)
│   ├── Landing(...)
│   ├── On-Station(...)
│   └── Off-Station(...)
└── UAP-Event(time, sensor, response, asset, location, signatures, observer-chain, ...)
    └── GENTEXT(description, event-description)
```

That is, a Mission Report is a **tree of hyperedges**, not a flat hyperedge. Each layer's arity is bounded around 5–12; the depth is 3–4 levels. The total structural width is the product. **This is a different schema target than entry 03 assumed**, and it has direct store-choice consequences (see "Substrate updates" below).

### `western_us_event_slides` — multi-incident document with shared anonymised witnesses

This is a **single PDF that contains four distinct incidents**:

1. *"Orbs Launching Orbs"* — orange "mother" orbs emitting red orbs, witnessed by USPER1–USPER6, dusk, two-day period, Western U.S.
2. *"Large, Fiery Orb"* — USPER5 + USPER6, dusk, hovering near rock pinnacle, ~1050 m away (AARO measured) and 12–18 m diameter (AARO measured), no sound.
3. *"Dark Kite"* — USPER5 + USPER6, pre-dawn, kite-shaped object with red and white lights, observed via NVGs.
4. *"Transparent Kite"* — USPER5 + USPER6 + USPER7, ~30 minutes after Dark Kite, kite-shape with transparency observed via NVGs and bare eye.

**Three architectural facts at once**, all of which contradict an assumption baked into entry 03:

1. **Multi-incident documents are real.** Entry 03 treated documents as 0-or-1 incident. This one has 4. Schema must support 1:N.
2. **Incidents reference each other** within and across documents. "Transparent Kite" begins: *"About 30 minutes after the 'Dark Kite' sighting…"* — that is a **structured temporal-sequence relationship**, not a free-text reference. Cross-incident edges are first-class.
3. **The USPER1–USPER7 pattern empirically validates the typed-anonymised-participant design** sketched in [03 §Q5](03-empirical-calibration.md#q5). Each USPER is a distinct, identity-preserved, non-disclosed participant. USPER5 and USPER6 appear in three incidents together; USPER7 joins for one (and "did not see the object"). Querying *"all incidents involving USPER5 + USPER6"* is the canonical example of why anonymised-but-typed nodes matter — and the data already supports that query natively, with no inference required.

There is also a **fourth finding at a different epistemic layer**: the slide footnotes mark **AARO post-hoc analytical claims** distinct from witness claims:

> Witness: "approximately 500–600 meters"
> *AARO post-hoc: "Measurements later gathered by AARO assess the object to have been ~1050 meters away from the observers."*

This is not a contradiction in the [03 §Q3](03-empirical-calibration.md#q3-contradictions) sense — it's a **structured derivation**: the witness reports something, the agency analytically refines it, and both versions are preserved. The kind enum needs a new value: **`analytical_assessment`** (post-hoc instrumented or analytical claim attached to a witness claim, with an explicit derivation source).

Both slides 2 and 3 also embed visual artefacts: *"Artist Rendering"* (a digital orange-orb image) and *"Image 1: Recreation of drawing provided by USPER6 of object seen in night vision goggles"* (a simple geometric figure with a red and a white light). UFO-USA's OCR transcribed the captions but lost the figures themselves; native PDF rendering keeps them addressable. **Embedded figures are first-class entities, not just illustrations**.

### `2024-04-30-composite-sketch` — pure visual, zero text

The PDF is **a single page that is entirely an image**: a digital composite/render of a saucer-shaped craft with a brilliant white halo over a grassy field with a tree line. **There is no text on the page at all**. UFO-USA's text-OCR pipeline captures effectively nothing for this file — the [`116-FBI_September_2023_Sighting_-_Composite_Sketch/`](../../UFO-USA/converted/116-FBI_September_2023_Sighting_-_Composite_Sketch/) folder presumably has either an empty MD or just the YAML frontmatter.

This is the canonical **pure-visual-evidence document**. Plus the 24 FBI Photos (B1–B24) are similarly image-only. **The substrate's ingestion pipeline cannot rely on text extraction for ~25 of the 161 documents** (~15% of the corpus). These need:

- A separate ingestion path (vision-LLM transcription/description, not OCR).
- A `kind` value of `visual_artifact` for claims derived from the image: e.g. `("composite-sketch-2024-04-30", visual_artifact, "saucer-shaped craft with luminous corona above a grassy field, photo-composite style, daylight scene")` — verbatim about the *image*, not the *event*.
- A clear distinction between *the witness's account* (text claim, kind: `witness`) and *the artist's depiction* (image claim, kind: `visual_artifact`) — these are different epistemic objects even when they describe the same event.

The OCR'd Markdown corpus genuinely cannot model these documents. The PDF read can.

### `dow-uap-d52` — process correspondence, with block-style redactions

Two pages of internal email, **not about a UAP event but about the disclosure of one**:

> "Could you please approve the use of the year this incident took place? Currently you have approved the month and the day, we request it includes the year."

The actual incident summary is a single sentence buried in the body, behind a tear line:

> "31 OCT 24, U.S Aircraft observed a possible UAP. It appeared to be oval/orb shaped, likely moving at a low speed. The U.S Aircraft had eyes on the poss UAP for over 2 hours."

Two architectural facts:

1. **Some documents are about the disclosure process, not the phenomena.** Schema needs a `document_type` field — `incident_report | process_correspondence | photographic_evidence | witness_summary | analytical_briefing | …` — that is a queryable axis distinct from `agency` and `kind`. Entries 02 and 03 implicitly assumed every document was an incident report; this one isn't.

2. **The visual style of redaction is itself information.** This document shows **redactions as enormous red `(b) (6)` lettering on solid black backgrounds**, consuming entire vertical sections of the page. That is a *qualitatively* different redaction event from the `[1.4a]` inline tokens in Mission Reports or the `~~SECRET//NOFORN~~` strikethroughs. The OCR pipeline captures the textual representation but loses the visual scale (which conveys "this entire block of content was suppressed", as opposed to "this individual word was suppressed"). The `redacted_placeholder` kind needs sub-types:

   - `redacted_inline` — single token replaced (`[1.4a]`, `[redacted]`).
   - `redacted_block` — multi-line section blacked out with FOIA exemption code annotation.
   - `redacted_whole_page` — entire page suppressed (we see this in some FBI sections).

   Each carries the same FOIA exemption code(s) but different scale-of-suppression metadata.

## Document-shape taxonomy

Across the four PDFs read directly plus inference from filenames and UFO-USA's OCR work, the corpus contains at least **nine distinct document shapes**, each with different ingestion needs:

| Shape | Approximate count | Distinguishing structure | Ingestion path |
|---|---|---|---|
| **DOW Mission Report (MISREP)** | ~45 | 80–100 typed fields, hierarchical (mission→equipment/personnel/timeline/UAP-event) | Form-field extraction + narrative LLM extraction |
| **Range Fouler / Crew Debrief** | ~10 | Form-shaped but smaller; pilot Q&A + tabular metadata | Form-field extraction |
| **NASA crew transcript** | ~7 | Multi-speaker dialogue (CDR/CMP/LMP/CC), timestamped utterances | Speaker-diarised text extraction |
| **State Department cable** | ~5 | Telegram format, reporting chain, witness account quoted | Cable-format parser |
| **FBI HQ correspondence section** | ~16 | Bulk historical correspondence, 100–200 pages, 1947–1968 era | Page-by-page text + entity extraction |
| **Multi-incident slide deck** | 1 (Western US) — likely more in future tranches | Multiple incidents per doc, embedded figures, AARO post-hoc footnotes | Slide-segmentation + per-incident extraction |
| **Email correspondence (process)** | ~3 (D50, D51, D52) | Email format, internal AARO/disclosure context, tear-line summaries | Email parser + tear-line extractor |
| **Composite sketch / FBI photo** | ~25 (1 sketch + 24 photos) | Pure visual, no text | Vision-LLM description, no OCR |
| **NARA historical file** | ~15 | Scanned WWII / post-war records, 1944–1965 | Vision-LLM OCR + period-specific entity extraction |

This is a **ragged corpus**. A monolithic ingestion pipeline like UFO-USA's "PDF → Gemini OCR → Markdown" gets ~70% of the value (the textual document shapes) but loses the ~25% that need shape-specific handling. **The ingestion pipeline must dispatch by document shape**, with shape detection itself an early-stage step (extension to [`uap-release-analyzer`](../../uap-release-analyzer/)'s prefix-mapping vocab in [03 §Q4](03-empirical-calibration.md)).

## Substrate updates

Five updates to the stack from [03](03-empirical-calibration.md):

### 1. Arity is bounded *per layer*, not absolute

Entry 03 said arity ≤ 12. **That holds for individual hyperedges within the hierarchy** (a single UAP-event hyperedge has 8–11 participants; a Personnel-chain entry has ~9 fields each). What entry 03 missed is that a Mission Report assembles 4 layers of these hyperedges into a tree of total structural width ~100 fields. **Entry 03's bound stands as a per-layer bound, not as a total-width bound.**

Implication: **the schema needs recursive composition** — hyperedges that can take hyperedges as participants. Three candidate stores from [01](01-hypergraph-hypothesis-and-prior-art.md) handle this differently:

- **TypeDB**: native — relations can play roles in other relations. Strongly preferred for this use.
- **RDF / RDF-star**: works via reified-statement chains, ergonomically heavier, but expressively complete.
- **Property graph (Neo4j) + reified Incident node per layer**: works; produces a node-per-layer pattern. Verbose but mature.

This is the strongest argument so far for TypeDB as the primary store.

### 2. Multi-incident documents need first-class support

Schema cardinality: `Document — 0..N — Incident`. Plus an explicit `IncidentReference(source: incident_id, target: incident_id, kind: temporal-sequence | comparative | re-described)` edge. The "Transparent Kite ~30 min after Dark Kite" reference is a **structured temporal-sequence edge between two incidents in the same document**, not free-text — the substrate must capture it as such.

### 3. The kind enum extends to nine values

Final list (with sub-types where applicable):

```
kind ∈ {
  factual,
  witness,
  speculation,
  instruction,
  procedural,
  metadata,
  analytical_assessment,             ← NEW (entry 04)
  visual_artifact,                   ← NEW (entry 04)
  redacted_placeholder,
}

redacted_placeholder.subkind ∈ {
  redacted_inline,
  redacted_block,
  redacted_whole_page,
}
```

`analytical_assessment` carries an explicit `derivation_source` (e.g. "AARO post-hoc measurement"), distinct from `factual` (where the source is the document itself) and `witness` (where the source is a participant).

`visual_artifact` carries `extraction_method: vision_llm` and a `depicted_subject` field separate from the textual `text` field — a vision-LLM description of what the image shows, not OCR text.

### 4. `document_type` becomes a queryable axis

Independent from `agency` and `kind`. Initial values from §Document-shape taxonomy above. New shapes get added as new tranches arrive (the Western US slide deck shape is plausibly going to recur).

### 5. Trust the PDF, not the manifest

`dow-uap-d28-mission-report-east-china-sea-2024.pdf` is about Iraq. The manifest is wrong. **The substrate must record both the manifest claim and the body-extracted claim and flag the disagreement** — not silently overwrite. Architecturally:

```
Document.metadata_claim_location  = "East China Sea"   ← from manifest
Document.body_extracted_location  = "Iraq (AYN AL ASAD AIRBASE, OKAS)"   ← from PDF
Document.location_disagreement    = true   ← derived flag
```

This pattern generalises — any field where manifest and body disagree should preserve both and surface the disagreement. It's a degenerate case of [03 §Q3](03-empirical-calibration.md#q3-contradictions)'s contradiction edge, but at the document-vs-its-own-metadata level rather than between two source documents.

## Open for entry 05

1. **Confirm the hierarchy holds outside MISREPs.** Read 1 NASA crew transcript natively, 1 State cable, 1 FBI HQ section sample. Different shapes will have different hierarchies (or none).
2. **Build the document-shape detector.** Prefix-mapping in [`uap-release-analyzer`](../../uap-release-analyzer/) gets the agency; we need a similar layer for shape. Probably a small classifier over filename + first-page features.
3. **Compare UFO-USA OCR side-by-side with PDF on a single MISREP.** I noticed in passing that the PDF shows partial coordinates `38SKC63 2` whereas the corresponding UFO-USA Markdown collapses these to `[redacted]` placeholders. If true broadly, **UFO-USA's Gemini OCR is over-aggressive about redacting** — and our claim layer should re-extract from PDFs for high-stakes Mission Reports rather than trusting Gemini's redaction calls. Verify on 3–5 documents.
4. **Quantify download success.** `data/download-failures.json` shows 111 failure events for what should be 161 records; the local directory has 116 PDFs. Reconcile the gap and surface it as `acquisitionStatus ∈ {downloaded, download_failed, removed_from_source, not_attempted}` extending abigailhaddad's pattern.
5. **Make the store decision.** Entry 02's stack now strongly favours **TypeDB** for the recursive-composition reasons in §1. The remaining counter is operational — TypeDB's ecosystem is smaller than Neo4j's. Entry 05 should commit and prototype. The single-Mission-Report round-trip target is now [`dow-uap-d28`](../../UFO-USA/converted/045-DOW-UAP-D28-_Mission_Report-_Iraq-_September_2024/) (the manifest-disagreement document), since the substrate's ability to represent *and surface* the East-China-Sea-vs-Iraq disagreement is itself a useful test.
