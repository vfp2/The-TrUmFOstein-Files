# Related GitHub repositories

A snapshot of other GitHub projects responding to the [war.gov UAP Release 01](https://www.war.gov/UFO/) of **8 May 2026**. Captured the same day, so most of these are hours old and will move fast.

The point of this list is not completeness — it is **situational awareness**: who is building what, what artifacts (manifests, OCR text, indexes) we may be able to consume rather than rebuild, and where the gaps are that justify our own approach.

Repos are grouped by what they're trying to do.

## Snapshot history

- **2026-05-09, ~08:07 UTC** (release + ~19 hr): 26 in-scope projects tracked + 1 gist. **+3 new**: `chinleez/uap-disclosure-2026` (first **bilingual Chinese / English** peer — re-organises the 161 records by agency and by geographic region, designed for in-browser GitHub viewing without cloning), `jayjonesvip/uap-release-01-brief` (single-file HTML brief with an **editorial 5-star "official weight" ranking** — first peer to weight files non-equally), `chris-advena/war-gov-ufo-release` (stub, README only). **−0 deleted**. Notable star deltas: `uap-release-analyzer` 67→107 (+40, **first repo in the survey to cross 100**; forks doubled 8→16), `uap-release-01` 29→46 (+17, crossing 45; forks 9→14), `UFO-USA` 42→50 (+8, crossing 50; forks 11→13), `vng9trmgr8-pixel/war-gov-ufo-release-1` 2→5 (crossing 5). The analyser-skill packaging continues to widen its lead while the corpus mirrors are still bunched near zero — the gap between *tooling that runs across tranches* and *one-shot static mirrors* is now visible in stars.
- **2026-05-09, ~00:43 UTC** (release + ~11 hr): 23 in-scope projects tracked + 1 gist. **+2 new**: `Decentricity/war-gov-ufo-release-01-interesting-files` (curatorial 10-case mirror with per-case observations; uses GitHub Releases for the 198 MB PR34 video), `KarmCraft/dept-of-war-ufo-dump` (PDF + image + video library with a multi-tab Excel research workbook as the analytic substrate). **−0 deleted**. Material star deltas: `uap-release-analyzer` 56→67 (+11, crossing 60), `uap-release-01` 24→29 (+5, crossing 25), `UFO-USA` 39→42 (crossing 40). Top of the survey is consolidating — the analyser skill is widening its lead.
- **2026-05-08, ~21:30 UTC** (release + ~8.5 hr): **+0 new, −0 deleted, no material star deltas.** Steady-state run via the [`related-repos-refresh`](.claude/skills/related-repos-refresh/) skill. Minor ticks (`uap-release-analyzer` 55→56, `uap-release-01` 23→24) below the +5★ threshold. Confirms the skill is working in idempotent mode after the busy 15-min window since the prior snapshot.
- **2026-05-08, ~21:15 UTC** (release + ~8 hr): 20 GitHub projects tracked + 1 gist. **+4 new since previous snapshot**: `Colbyashi/UFO-Files` (curated bulk mirror with PDF→PNG photo extraction), `Ledatic-Empire/pursue` (only peer doing **Ed25519 cryptographic attestation per file** — architecturally novel), `NoobAIDeveloper/uap-watch` (tactical dashboard with Palantir-Blueprint styling), `SeanLikesData/ufo-scrape-guide` (catalogue of 13 Akamai-bypass approaches that don't work, + 4 reference scripts). **−0 deleted**. Notable star deltas: `uap-release-analyzer` 48→55, `UFO-USA` 33→39 (10 forks). First refresh executed via the new [`related-repos-refresh`](.claude/skills/related-repos-refresh/) skill rather than by hand.
- **2026-05-08, ~19:30 UTC** (release + ~5 hr): 18 projects tracked. **+6 since first snapshot** (`uap-release-analyzer`, `uap` (sanderlegit), `alien-files`, `ufo-releases` (abigailhaddad), `WarGov` (wrek), `Chat-With-Aliens`, `ufo` (toor11), `uap-disclosure-tracker` (pre-release context)). **−1**: `davemorin/pursue-ufo-files` deleted; we have a local clone preserved at [vfp2/pursue-ufo-files](https://github.com/vfp2/pursue-ufo-files). Notable star deltas: `uap-release-analyzer` 0→48 (highest-traction), `UFO-USA` 26→33, `uap-release-01` 11→21.
- **2026-05-08, ~17:50 UTC** (release + ~3 hr): initial snapshot, 12 projects tracked.

---

## Mirrors and converted archives

These projects mostly re-host the corpus, often with light reformatting. Useful as alternative download sources and as a sanity-check on the manifest.

### [vng9trmgr8-pixel/war-gov-ufo-release-1](https://github.com/vng9trmgr8-pixel/war-gov-ufo-release-1) — 5 ★, 1 fork
*Created 2026-05-08 16:58 UTC.* Static-site mirror — 119 PDFs with summaries and thumbnails, plus 14 still images in a gallery. No framework: HTML/CSS/JS plus Python build scripts (`build_data.py`, `extract_text.py`) that turn the war.gov CSV manifest into a `data.json`. All file links point back to the official source rather than rehosting. Hosted on Vercel. ~5 commits. Useful as a reference for parsing the manifest.

### [DenisSergeevitch/UFO-USA](https://github.com/DenisSergeevitch/UFO-USA) — 50 ★, 13 forks
*Created 2026-05-08 14:46 UTC.* Converted-Markdown archive. 120 PDFs, 4,185 pages, OCR'd page-by-page via **Gemini AI at 200 DPI**, output as Markdown with YAML frontmatter. Includes conversion scripts, download logs, and a manifest tracking 4,174 successful conversions plus 11 errored pages. Probably the most directly consumable text corpus of the lot — if their OCR is clean we may not need to re-OCR. Currently the highest-starred *corpus* repo. We have a fork at [vfp2/UFO-USA](https://github.com/vfp2/UFO-USA).

### [Onebooming/US-WAR-GOV-UFO](https://github.com/Onebooming/US-WAR-GOV-UFO) — 0 ★
*Created 2026-05-08 15:29 UTC.* Stub — title points at `war.gov/UFO/` PDFs but the repo has effectively no content. Tracking only.

### [wrek/WarGov](https://github.com/wrek/WarGov) — 0 ★
*Created 2026-05-08 19:13 UTC.* Stated as "WarGov document archive and extracted markdown content" but currently empty. Tracking only — worth re-checking in a few hours.

### [Colbyashi/UFO-Files](https://github.com/Colbyashi/UFO-Files) — 0 ★
*Created 2026-05-08 19:41 UTC.* Curated bulk mirror — manually downloaded 157 of 161 documents (counting duplicates and retrieval errors), with embedded photos extracted from PDFs into stand-alone PNG files. Repository contains the actual files, not just scripts. README documents the gap between the source's listed 161 and the 157 successfully retrieved. Lighter than `vng9trmgr8-pixel/war-gov-ufo-release-1` and without its parsed `data.json` manifest, but the **photo-extraction sidecar is unique** in the survey — useful if we want to surface visual-only assets without re-extracting them ourselves.

### [Ledatic-Empire/pursue](https://github.com/Ledatic-Empire/pursue) — 0 ★
*Created 2026-05-08 20:32 UTC.* The only peer in the survey doing **cryptographic provenance / attestation**. Built in **Rail** (a "pure" language with no external runtime dependencies — no curl, no SQLite). Each downloaded document receives a **byte-level Ed25519 signature** binding the file to a timestamp ("pulse") and a witness key, producing tamper-evident archival records verifiable against a public key. Append-only JSONL manifest tracks file hashes, download status, and signatures. Public face at `ledatic.org/aliens`. **Architecturally directly relevant to our goals**: page-level provenance was framed in [architecture/02](architecture/02-peer-substrate-survey.md) as a `(documentId, pageId, charStart, charEnd)` tuple — Ledatic's per-file Ed25519 layer is one level above (whole-document attestation) but suggests a complementary pattern: every claim could carry a signature chain anchored to its source-document signature, giving cryptographic verifiability of the chain from page-MD to claim. Worth watching closely.

### [Decentricity/war-gov-ufo-release-01-interesting-files](https://github.com/Decentricity/war-gov-ufo-release-01-interesting-files) — 0 ★
*Created 2026-05-09 00:01 UTC.* Curatorial — selects **10 highest-interest cases** from the release (Greece IR / SWIR videos, Western U.S. orb/kite events, USPER witness statement, NASA Apollo 11/12/17, FBI Socorro 1964, FBI 2023 sketch, WWII foo-fighters, Senator Russell 1955, USAF 1949 reporting framework) and structures `files/` by case folder rather than by source-CSV row. `metadata/selected_manifest.json` is the canonical selection; `docs/observations.md` separates "why interesting" from "what it does not prove" per case — the only mirror so far that ships explicit epistemic caveats alongside the files. Reproducible Python downloader (`curl_cffi`-based, resumable). The 198 MB PR34 DVIDS MP4 is staged outside git as a **GitHub Release asset** — a tidy answer to the >100 MB blob ceiling that future tranches will keep hitting. Architecturally interesting as the only peer making **case-level (not file-level) the unit of organisation**, which is closer to what an incident-typed substrate would want.

### [KarmCraft/dept-of-war-ufo-dump](https://github.com/KarmCraft/dept-of-war-ufo-dump) — 0 ★
*Created 2026-05-08 23:24 UTC.* Comprehensive local research library: **128 PDFs**, **14 source images**, **28 MP4 videos** (with DVIDS metadata + thumbnails) — broader corpus coverage than most mirrors, which stop at PDFs. Each PDF gets a folder with extracted text, first-page preview, and selected **key-page screenshots** (615 in total). The distinguishing artefact is a **multi-tab Excel research workbook** (`ufo_research_index.xlsx`) with seven sheets: `Catalog`, `Research Tracker` (priority/status/tags/notes per doc), `Summaries` (heuristic summaries with extracted key facts), `Images`, `Source Images`, `Videos`, `Audit`. Python (`PyMuPDF` / `openpyxl`) for organisation; Node.js + Playwright for downloads (the same Akamai-aware path everyone converges on). Architecturally a non-web, non-database approach to the same problem — **Excel as the substrate**. Useful counterpoint to the Postgres/SQLite-based projects: shows what an analyst-rather-than-engineer workflow looks like, and what page-level provenance looks like when the substrate is a spreadsheet rather than a graph.

### [chinleez/uap-disclosure-2026](https://github.com/chinleez/uap-disclosure-2026) — 0 ★
*Created 2026-05-09 02:48 UTC.* **First non-English peer in the survey** — Chinese-language re-index of the 161-record release, with a parallel English mirror of every page (`README_en.md`, `by-fbi_en.md`, `by-location_en.md`, …). Re-organises the corpus along two cross-cutting axes: **by agency** (DOW 82, FBI 56, NASA 15, State 8) and **by geographic region** (Americas, Middle East, Europe & Central Asia, Asia-Pacific, Space & orbit, location-not-given). Translates titles, blurbs, locations, and field labels into Chinese; merges shared blurbs across multi-section case files (FBI 18, DOW MISREP 32, Apollo 5) so the same intro is not repeated per row; English originals are preserved in collapsible `<details>` blocks. Resource links point back to the original war.gov / CloudFront URLs so the whole index is browsable on GitHub without cloning. Optional Python downloader (`scripts/download_resources.py`) mirrors the 6.7 GB of resources locally with per-kind selectors (`--kinds thumb,image` ≈ 45 MB). CC BY 4.0. Architecturally distinctive as the only entry designed primarily for **GitHub-as-the-viewer** rather than a hosted site or local app, and the only one shipping translation as a first-class artefact (`translations_zh.json`, `uap_index.json`).

### [chris-advena/war-gov-ufo-release](https://github.com/chris-advena/war-gov-ufo-release) — 0 ★
*Created 2026-05-09 06:54 UTC.* Stub — README is two lines ("Exploring https://www.war.gov/UFO/"), no other files, no language detected. Tracking only — worth re-checking in a few hours.

---

## Searchable archives, reading rooms, and RAG interfaces

These go beyond mirroring: full-text search, OCR, RAG chat, or wiki-style cross-linking.

### [robzilla1738/clubufo](https://github.com/robzilla1738/clubufo) — 1 ★, 15 commits
*Created 2026-05-08 14:51 UTC.* "ClubUFO — a reading room for declassified UFO/UAP documents." Browsable library + RAG chat over 161 PDFs with **page-cited answers**. Stack: Next.js 15 / React 19 / Tailwind v4 / shadcn/ui frontend; Neon Postgres + pgvector; DeepSeek for chat, OpenAI `text-embedding-3-small` for embeddings; Drizzle ORM; `unpdf` for serverless PDF extraction; Vercel Blob storage; admin ingestion routes. The README frames sources as "public, declassified, and citizen-submitted" — broader than just war.gov. Hybrid search via `/api/chat`. Closest to a fully-shaped end-user product right now.

### [zexiro/uap-disclosure-archive](https://github.com/zexiro/uap-disclosure-archive) — 4 ★, 1 fork
*Created 2026-05-08 14:58 UTC.* Self-hosted searchable mirror of all 162 records. Python pipeline (CSV parse, concurrent download, OCR via `pdftotext` / `ocrmypdf`); MiniSearch index in the frontend; a single-page search UI; **Obsidian vault** with 162 cross-linked notes; **TF-IDF and perceptual-hash similarity** to surface content and visual relationships; 6-hour automated refresh; deployed on Railway with persistent volumes. Stated longer-term ambition: a "Disclosure Globe" aggregating AARO, NUFORC, Project Blue Book, and international archives. Architecturally the most aligned with what we want — worth watching closely. We have a fork at [vfp2/uap-disclosure-archive](https://github.com/vfp2/uap-disclosure-archive).

### [Pump-OS/alien-files](https://github.com/Pump-OS/alien-files) — 0 ★
*Created 2026-05-08 17:32 UTC.* "ALIEN.FILES — searchable, OCR-indexed mirror." Discovers the war.gov manifest, mirrors PDFs via **Playwright** (Akamai-aware), then runs a three-stage extraction: pdfplumber for born-digital text, **Tesseract** for scanned pages, then JSON serialisation. Search via **MiniSearch** (client-side BM25). Adds **Claude-powered RAG chat with inline citations**. Frontend is Next.js 15 / TypeScript / Tailwind v4. Deploys on Vercel with optional R2 / GitHub Releases for PDF hosting. 161 records indexed. Functional. Notable as the only project in the survey using Tesseract specifically — a fallback OCR engine worth knowing about for documents Gemini struggles on.

### [abigailhaddad/ufo-releases](https://github.com/abigailhaddad/ufo-releases) — 0 ★
*Created 2026-05-08 18:39 UTC, 5 commits.* Searchable, sortable interface positioned explicitly as a fix for the official site being "JS-heavy and inconvenient." Next.js / TypeScript / React; Playwright for browser automation. **Daily GitHub Actions** fetch the CSV metadata, merge new/updated records, and *preserve records flagged as removed from the source* — an explicit archival stance. Deploys on Vercel. All file links redirect to original government URLs. The "preserve-on-removal" pattern is architecturally interesting and aligns with what we'd want for cross-tranche durability.

### [zvizdo/ufo-knowledge-base](https://github.com/zvizdo/ufo-knowledge-base) — 0 ★
*Created 2026-05-08 04:14 UTC — about 13 hours **before** the war.gov release.* Pre-existing connected wiki of the UFO/UAP discourse: ~2,258 pages, ~29,000 wikilinks, covering 957 people, 406 concepts, 260 organisations, 138 incidents, 129 places, 103 documents, 84 programmes. Plain Markdown with YAML frontmatter, organised in `ufo-kb/wiki/` by entity type, raw sources in `ufo-kb/raw/`. Built with Claude Code custom skills (`kb-import`, `kb-query`, `kb-maintain`), embeddings index via `qmd`, Python YouTube-transcript ingestion, Obsidian-compatible. Explicitly frames itself as **mapping discourse, not adjudicating truth** — contested claims get conflict flags rather than resolution. As of this snapshot it does **not yet reference the war.gov release** (still 3 commits, no PURSUE references). This is the most interesting peer for our purposes: a mature schema for the surrounding context that the new corpus can be plugged into.

### [ChatWithAliens/Chat-With-Aliens](https://github.com/ChatWithAliens/Chat-With-Aliens) — 0 ★
*Created 2026-05-08 16:55 UTC.* RAG chat across 51 documents (3,037 pages, 2,416 indexed chunks) from FBI / CIA / DoD UFO/UAP files — **broader than just war.gov**, dipping into the older Vault. Five named "personas" (Affa, Ponnar, Monka, Orthon, Zemkla) interactively answer in-character using grounded retrieval. Stack: React/Vite frontend, Node.js/Express backend, **PostgreSQL with full-text search** (no vector DB), GPT-4o for generation. Architecturally simpler than the pgvector RAG path: classical FTS + LLM-over-retrieved-chunks. Notable mostly for the breadth of corpus and the choice of FTS-not-vectors; the persona framing is a UX layer, not an architectural one. (Note: as confirmed by [architecture/02](architecture/02-peer-substrate-survey.md), the public repo is documentation-only — actual implementation code is not committed.)

### [NoobAIDeveloper/uap-watch](https://github.com/NoobAIDeveloper/uap-watch) — 0 ★, 9 commits
*Created 2026-05-08 19:38 UTC.* Independent dashboard mirroring the war.gov release with a deliberate **Palantir-Blueprint-inspired military-intelligence aesthetic** — described by its author as "tactical." Next.js / TypeScript / Tailwind. Deployed at `uap-watch-flame.vercel.app`. Notable mostly as a UX data point: the only peer explicitly leaning into intelligence-product visual language. Architecturally a thin web shell over the manifest, no entity model.

---

## Download / automation tooling

### [toor11/ufo](https://github.com/toor11/ufo) — 0 ★
*Created 2026-05-08 17:51 UTC.* Bulk downloader for 161 records (PDFs, images, videos), preserving original filenames. Python + **Playwright (Chromium, visible)** — same Akamai-bot-detection bypass strategy as the deleted davemorin script. Tighter scope: just download, no analysis layer. Useful as a fallback or cross-check tool.

### [SeanLikesData/ufo-scrape-guide](https://github.com/SeanLikesData/ufo-scrape-guide) — 0 ★
*Created 2026-05-08 20:01 UTC.* Field guide + 4 Node.js reference scripts (run via `npm install && npm run all`). The README catalogues **13 approaches that don't work** against war.gov's Akamai protection (curl, headless Chrome, Playwright requests, etc.) and documents the working pattern: real Chrome + visible window + the manifest at `/Portals/1/Interactive/2026/UFO/uap-csv.csv`. The negative-results catalogue is the highest-value part — saves anyone else from rediscovering each failure mode. Pairs well with our preserved [`vfp2/pursue-ufo-files`](https://github.com/vfp2/pursue-ufo-files) and the stronger Akamai bypass in [`abigailhaddad/ufo-releases`](https://github.com/abigailhaddad/ufo-releases).

---

## Datasets and analyser skills

### [ckpxgfnksd-max/uap-release-01](https://github.com/ckpxgfnksd-max/uap-release-01) — 46 ★, 14 forks
*Created 2026-05-08 14:51 UTC.* "Mirror of the May 2026 war.gov PURSUE UAP/UFO release (132 files, 2.4 GB). LFS-backed example corpus for the uap-release-analyzer skill." Most useful as a **canonical, hash-stable, LFS-backed dataset** — the description even positions it as a fixture for evaluating an analyser tool. If we want a reproducible test corpus this may be the cleanest pin.

### [ckpxgfnksd-max/uap-release-analyzer](https://github.com/ckpxgfnksd-max/uap-release-analyzer) — **107 ★, 16 forks** *(highest traction in the survey, first repo to cross 100)*
*Created 2026-05-08 14:32 UTC — earliest tool repo of any tracked.* A **Claude Code skill** that turns a folder of declassified UAP/UFO documents into a structured analysis. Workflow: (1) inventory PDFs by agency / type / page count, (2) extract text via `pdfplumber` (flagging scanned files needing OCR), (3) tally token frequencies, surface entities, and characterise redaction patterns, (4) emit a standardised **11-section `REPORT.md`** with top terms, locations, agency breakdowns, and cross-document patterns. Tuned for UAP release structure (recognises agency filename prefixes, FOIA exemption codes, war.gov quirks) but explicitly designed to be reusable across **future PURSUE tranches and adjacent corpora (FBI Vault, NARA, AARO)** by adding new prefix mappings. Notable for being the only project that explicitly anticipates re-running against new tranches as they land — directly relevant to our cross-tranche durability goal. 107 stars by release + 19 hr (first in the survey to cross 100, forks doubled 8→16 in the same window) confirm the Claude-skill packaging format is gaining real momentum — it has consistently led the survey since the earliest snapshot and the gap is now widening, not closing.

---

## Structured analysis and databases

### [sanderlegit/uap](https://github.com/sanderlegit/uap) — 0 ★, 3 commits
*Created 2026-05-08 18:18 UTC — coincidentally 2 minutes after our own repo was created.* Self-described as "Analysis of 145 declassified UAP/UFO files." Importantly: **structured analysis, not RAG-over-PDFs**. Contains:

- An **SQLite database** (`incidents_v2.db`) holding incident-level records (schema not yet fully documented in the README).
- A **cross-reference graph visualisation** linking entities and incidents across documents.
- An **interactive map** and **timeline**.
- Targeted analytical reports — FBI deep dive, Apollo deep dive, **redaction analysis**.
- Python pipeline scripts for OCR, text extraction, data export, and DVIDS video downloads.

**Most directly aligned with our project's analytical ambitions** of any repo in the survey. Worth examining their SQLite schema closely — it may be the only public data point on what an actual structured incident model for this corpus looks like in practice. The cross-reference graph will tell us what level of entity granularity others are reaching at this stage.

---

## Analysis and commentary

### [joseph-schiro/WAR.GOV---UAP-Evidence-Analysis](https://github.com/joseph-schiro/WAR.GOV---UAP-Evidence-Analysis) — 0 ★
*Created 2026-05-08 16:22 UTC.* Stated as "Deep analysis of the UAP files released on War.gov/UFO" but contents are minimal — README, GPL-3.0 LICENSE, and a single `index.html`. Tracking; substance not yet visible.

### [RUFOIOT/editorial-uap-pursue](https://github.com/RUFOIOT/editorial-uap-pursue) — 0 ★
*Created 2026-05-08 15:47 UTC.* Spanish-language editorial commentary by Felipe Salgado — "El Gran Show de la Transparencia." Single HTML file, opinion/analysis rather than data. Useful as one data point on international reception.

### [jayjonesvip/uap-release-01-brief](https://github.com/jayjonesvip/uap-release-01-brief) — 0 ★
*Created 2026-05-09 01:14 UTC.* Single-file standalone HTML brief — open `ufo_release_01_ranked_brief.html` in a browser, no build step, no server, no npm. **First peer in the survey to assign non-equal weights to release files**: an editorial **5-star "official weight" ranking** scored on agency source, seniority of referenced officials, command-chain handling, trained-witness quality, AARO involvement, and usefulness of the public record. Filter by star rating / agency, search by title / year / highlight, dark-light toggle, print stylesheet, direct links to source. The README explicitly disclaims that the rank is editorial source-weighting, **not adjudication of what any object was**. The ranking rubric itself is the architectural data point — first attempt in the survey to make **per-record source-weight a first-class field** rather than treating all 161 records as flat. The closest analogue in our schema is the `claim.kind` 9-value enum (factual / witness / speculation / …) but applied at document scale rather than claim scale.

---

## Manifest snapshots and source captures

### [ahmetcadirci25 / uap-csv.csv (gist)](https://gist.github.com/ahmetcadirci25/e4edb7d30109fdb8ff14b73dc75f67bc)
*Created 2026-05-08 14:02 UTC — earliest public capture we've found, ~30 minutes before any tracked repo.* A single-file gist of the raw `uap-csv.csv` manifest as published on war.gov. **143 lines** at capture time vs **575 / 573** in the copies vendored by `UFO-USA` and `pursue-ufo-files` respectively — strongly suggesting either the manifest was extended after this snapshot, or our local copies expanded multi-line fields differently. Either way, this is a useful **point-in-time t₀ reference** for diff-ing how the canonical manifest evolves across release tranches.

Schema (column headers, identical across this gist and all three local repos — `UFO-USA`, `pursue-ufo-files`, `uap-disclosure-archive`):

```
Redaction, Release Date, Title, Type, Video Pairing, PDF Pairing,
Description Blurb, DVIDS Video ID, Video Title, Agency, Incident Date,
Incident Location, PDF | Image Link, Modal Image
```

That column set is effectively the **war.gov export schema** — a thin record-level model: agency, type (PDF/VID), incident date+location free-text, description blurb, link, and pairing fields tying a video to its PDF (or vice versa) via `Video Pairing` / `PDF Pairing`. Notably absent at the source: any structured witness, sensor, classification, or program field. Anything richer than this we have to derive.

`uap-disclosure-archive` also vendors a second, parallel CSV (`release-table.csv`) with a different but overlapping shape — `Asset File Name, Release Date, Title, Blurb, Agency, Incident Date, Incident Location, Document type, Document Link, Image, Videos`. Worth noting that two different CSVs exist on the source side; reconciliation is a small but real ingestion task.

---

## Pre-release / adjacent

### [PickleTime27/uap-disclosure-tracker](https://github.com/PickleTime27/uap-disclosure-tracker) — 0 ★
*Created 2026-02-25.* Pre-dates the war.gov release by ~10 weeks. Real-time UAP/UFO disclosure tracker monitoring congressional hearings, legislation, key players in the transparency push, and declassified documents. Next.js / TypeScript with AI-powered document summarisation. Useful as **context outside the corpus** — when the substrate needs to link an incident to the broader political/legislative timeline, this is the kind of feed that should be ingested.

---

## Removed / archived

### ~~[davemorin/pursue-ufo-files](https://github.com/davemorin/pursue-ufo-files)~~ — DELETED
*Existed 2026-05-08 17:34 UTC → deleted some time before 2026-05-08 ~19:30 UTC.* Original creator pulled the repo. Notable — author was Dave Morin (former Facebook/Path). Reason for deletion not stated. **We preserved a local clone before deletion**, with 1 commit, the Playwright/Akamai-aware download script, the original manifest, and the `ANALYSIS.md` / `KRIPAL_BRIEFING.md` scaffolding. Republished at **[vfp2/pursue-ufo-files](https://github.com/vfp2/pursue-ufo-files)** for archival continuity. The Akamai-bot-bypass technique it documented (in-browser fetch via Playwright to inherit the right TLS fingerprint) is captured in our copy and remains the canonical solution.

---

## Out of scope

### [ufo50bingo/ufo50bingo_classify](https://github.com/ufo50bingo/ufo50bingo_classify)
*Created 2026-05-08 17:04 UTC.* False positive — name and owner indicate this relates to **UFO 50** (the retro video game collection) and bingo card classification, not the war.gov release. Listed for completeness so it doesn't get re-evaluated.

### [knoelle-svg/ufo-data-engineering](https://github.com/knoelle-svg/ufo-data-engineering)
*Created 2026-05-08 17:37 UTC.* Personal portfolio project — README is two lines: "Exploring my technical skills using UFO data." No code, no clear connection to the war.gov release. Tracking only.

---

## Takeaways for our approach

- **OCR is largely solved** — at least three projects (UFO-USA via Gemini, uap-disclosure-archive via `ocrmypdf`, alien-files via Tesseract) have already produced full page-level text. We should evaluate consuming one of those rather than redoing OCR from PDFs ourselves.
- **A canonical dataset pin exists** in `ckpxgfnksd-max/uap-release-01` (LFS, 132 files, hash-stable). Worth using as an immutable reference even if we maintain our own working copy.
- **The Akamai/Playwright gotcha** is real — anyone building a download script needs to know this up front. The technique is preserved in our [vfp2/pursue-ufo-files](https://github.com/vfp2/pursue-ufo-files) clone and replicated independently in `Pump-OS/alien-files` and `toor11/ufo`.
- **Live-mirroring with archival preservation** (`abigailhaddad/ufo-releases` daily GHA + preserves removed records) is a small but architecturally useful pattern for cross-tranche durability.
- **The Claude-skill format is gaining real traction** — `ckpxgfnksd-max/uap-release-analyzer` is the highest-starred repo in this survey at 67 ★ (and still climbing 11 hr post-release), and explicitly anticipates being re-run across future tranches and adjacent corpora (FBI Vault, NARA, AARO). Worth understanding what its 11-section REPORT.md captures and whether our work should produce a Claude skill as one of its outputs.
- **The closest peer to our analytical ambitions is `sanderlegit/uap`** — it has an actual SQLite incident DB, a cross-reference graph, and targeted analyses (FBI, Apollo, redactions). Worth examining its schema directly to understand what level of entity granularity is reachable from the released documents at this stage. Even at 0 stars and 3 commits, this is the most architecturally relevant peer.
- **No one has yet attempted** what we want at the centre: a typed, queryable, n-ary or hyperedge-based substrate that connects this corpus to the wider UFO/UAP discourse with page-level provenance and cross-tranche bitemporality. `zvizdo/ufo-knowledge-base` has the schema for the surrounding context but not yet the new corpus; `zexiro/uap-disclosure-archive` has the corpus and similarity links but not the wider entity graph; `clubufo` has a polished RAG product but a single-corpus scope; `sanderlegit/uap` has structured analysis but with binary-edge SQLite and no provenance / cross-tranche layer.
- **The gap we should fill** is the substrate layer — an entity/event/claim model (likely n-ary or hyperedge-based, per [architecture/01](architecture/01-hypergraph-hypothesis-and-prior-art.md)) with page-level provenance and cross-tranche bitemporality — that the existing mirrors and RAG chat UIs can be re-pointed at, and that survives across every future release tranche.
