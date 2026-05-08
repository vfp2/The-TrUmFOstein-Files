# The TrUmFOstein Files

A working repository for ingesting, structuring, and strategically analysing the UAP/UFO documents released by the U.S. Department of War on **8 May 2026** under the **PURSUE** programme (Presidential Unsealing and Reporting System for UAP Encounters), at <https://www.war.gov/UFO/>.

## Background

On 8 May 2026, at the direction of President Donald J. Trump, the Department of War (formerly Department of Defense) published the first batch of declassified UAP records from a multi-agency effort spanning the FBI, DoD, NASA, and the State Department. The portal commits to releasing additional tranches "on a rolling basis... every few weeks" as documents are discovered and declassified.

Reported figures vary by source and by what counts as a "file":

| Source | Count |
|---|---|
| CNN / NBC | 162 files (FBI, DoD, NASA, State) |
| Several mirrors | 161 records / 119 PDFs (~8–10 GB) |
| `ckpxgfnksd-max/uap-release-01` | 132 files (118 PDFs, 8 PNG, 6 JPG, ~2.4 GB, ~4,157 PDF pages) |
| `DenisSergeevitch/UFO-USA` | 120 PDFs / 4,185 pages OCR'd |

The discrepancies are themselves a useful early signal — the manifest is moving and the corpus is being interpreted differently across mirrors. Reconciling those views is part of the work.

## Project intent

The community will produce many download mirrors and many quick "ask‑a‑bot" interfaces. Our angle is different.

We are aiming for **a structured, durable substrate** — not just a chat box bolted onto a pile of PDFs. The order of operations matters:

1. **Architecture first.** Decide how the corpus should be modelled — entities (people, organisations, programmes, incidents, locations, dates), provenance (source agency, release tranche, originating archive), confidence/conflict flags, and cross‑references both inside this corpus and to the wider public record (Project Blue Book, AARO, NUFORC, congressional hearings, FOIA archives, international equivalents).
2. **Ingestion second.** Pull the files, OCR everything, normalise, tag, and stage. Treat OCR fidelity, page-level provenance, and reproducibility of the manifest as first-class concerns.
3. **Synthesis third.** Use the structured layer to drive analyses that a chat-only interface cannot produce: timeline reconstruction, entity graphs, contradiction detection between agencies, cross-tranche change tracking as new releases land, and prompts that anchor LLM output in cited page-level sources.

The bet: post-release, raw curiosity will be served by dozens of mirrors and chat UIs within hours. **Strategic value compounds over weeks**, in the substrate that lets you ask second- and third-order questions, re-run them when the next tranche drops, and trust the citations.

## What this repo contains

We are getting our reference frame straight before ingesting documents.

- [README.md](README.md) — this file.
- [related-repos.md](related-repos.md) — a survey of other GitHub projects already working on the same release, with notes on each one's approach, tech, and stage. Knowing what others are building helps us not duplicate effort and identifies useful prior art (data manifests, OCR outputs, indexes) we may be able to consume rather than rebuild.
- [architecture/](architecture/) — the ongoing architectural discussion. Numbered entries; each one is open until superseded.
  - [01 — Hypergraph hypothesis and prior art](architecture/01-hypergraph-hypothesis-and-prior-art.md) — does the substrate want to be a true hypergraph? Survey of historic and current UFO/UAP database architectures, candidate n-ary stores (TypeDB, RDF-star, Datomic, Neo4j+reification), and an early take that the answer is probably hybrid pending document-content evidence.
  - [02 — Peer substrate survey: schemas, pipelines, and what to steal](architecture/02-peer-substrate-survey.md) — read peer code (sanderlegit/uap, zvizdo, clubufo, uap-release-analyzer, alien-files, abigailhaddad, vng9trmgr8) and extract concrete patterns. Refines the hypothesis: claims become the atomic unit (clubufo-shaped), hyperedges sit above claims, and several layers below the hypergraph (vocab, manifest, OCR, page-provenance) have working peer implementations to compose.
  - [03 — Empirical calibration against the OCR'd corpus](architecture/03-empirical-calibration.md) — close the open questions from 02 with corpus evidence. Vocab coverage measured against all 4,174 OCR'd pages; arity histogram and kind-enum calibration sampled across DOW Mission Reports, NASA transcripts, State cables; contradiction hunt; redaction density. Sets quantitative targets: arity ≤ 12, 7-value kind enum, first-class redacted-claim placeholders, 8-category operational vocab extension authored from the evidence.
  - [04 — Native PDF analysis: document-shape diversity and substrate updates](architecture/04-native-pdf-analysis.md) — read PDFs directly via Claude's vision-capable PDF mode, recovering layout, embedded figures, and visual redaction style that text-OCR collapses. Mission Reports are *hierarchical hyperedges* (~100 typed fields across 4 layers, not flat ≤12); multi-incident documents are real (Western US slide deck has 4 incidents with shared anonymised witnesses USPER1–7); ~25 of 161 documents are pure-visual; the war.gov manifest is sometimes wrong about its own PDFs (D28 is Iraq, not "East China Sea"). Kind enum extends to 9 values plus 3 redaction sub-types; `document_type` becomes a queryable axis; recursive-composition argues strongly for TypeDB.

## Roadmap (provisional)

The next pieces, roughly in order:

- **Manifest ingestion** — pull the war.gov CSV/index, capture file hashes, agency, release tranche, and persist the raw manifest under version control so changes between tranches are diff‑able.
- **Document acquisition** — bulk download, with awareness that war.gov is fronted by Akamai and rejects naive CLI fetchers (`davemorin/pursue-ufo-files` documents using Playwright's in-browser fetch to pass TLS fingerprinting).
- **OCR + page-level normalisation** — page-as-record, with text, source PDF, page number, and any embedded figures kept as separate addressable assets.
- **Schema design for the structured layer** — entities, events, claims, and provenance edges. Likely a graph-shaped store (or a relational schema modelled graph-style) with full-text + vector indexes layered on top.
- **Synthesis tooling** — analyses that consume the structured layer, not the raw PDFs: timeline views, entity dossiers, conflict detection, cross-tranche change reports.
- **Re-ingestion discipline** — every component must assume the corpus will grow with each new release tranche, without re-doing prior work.

## Conventions

- Plain text, version-controlled, citeable. Where we generate intermediate artifacts (OCR, embeddings, indexes), we keep the build scripts in-repo so the artifacts are reproducible.
- Page-level provenance is non-negotiable. Every claim, summary, or LLM-generated synthesis must trace back to `(file_id, page)`.
- We document our assumptions and our disagreements with other mirrors (e.g. file counts) rather than papering over them.

## Sources

- Department of War portal: <https://www.war.gov/UFO/>
- Press release: <https://www.war.gov/News/Releases/Release/Article/4480582/department-of-war-releases-unidentified-anomalous-phenomena-files-in-historic-t/>
- Coverage: [CNN](https://www.cnn.com/2026/05/08/politics/ufo-files-pentagon-release-aliens), [CBS News](https://www.cbsnews.com/news/pentagon-begins-release-ufo-files/), [NBC News](https://www.nbcnews.com/science/ufos-and-anomalous-phenomena/ufo-uap-files-pentagon-release-trump-rcna344204), [Fox News](https://www.foxnews.com/politics/trump-admin-releases-highly-anticipatedfiles-documents-ufos-extraterrestrial-life), [Aerotime](https://www.aerotime.aero/articles/us-releases-ufo-uap-files)
