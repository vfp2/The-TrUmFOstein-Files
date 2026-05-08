# Related GitHub repositories

A snapshot of other GitHub projects responding to the [war.gov UAP Release 01](https://www.war.gov/UFO/) of **8 May 2026**. Captured the same day, so most of these are hours old and will move fast.

The point of this list is not completeness — it is **situational awareness**: who is building what, what artifacts (manifests, OCR text, indexes) we may be able to consume rather than rebuild, and where the gaps are that justify our own approach.

Repos are grouped by what they're trying to do.

---

## Mirrors and converted archives

These projects mostly re-host the corpus, often with light reformatting. Useful as alternative download sources and as a sanity-check on the manifest.

### [vng9trmgr8-pixel/war-gov-ufo-release-1](https://github.com/vng9trmgr8-pixel/war-gov-ufo-release-1)
*Created 2026-05-08 16:58 UTC.* Static-site mirror — 119 PDFs with summaries and thumbnails, plus 14 still images in a gallery. No framework: HTML/CSS/JS plus Python build scripts (`build_data.py`, `extract_text.py`) that turn the war.gov CSV manifest into a `data.json`. All file links point back to the official source rather than rehosting. Hosted on Vercel. ~5 commits. Useful as a reference for parsing the manifest.

### [DenisSergeevitch/UFO-USA](https://github.com/DenisSergeevitch/UFO-USA) — 26 stars
*Created 2026-05-08 14:46 UTC.* Converted-Markdown archive. 120 PDFs, 4,185 pages, OCR'd page-by-page via **Gemini AI at 200 DPI**, output as Markdown with YAML frontmatter. Includes conversion scripts, download logs, and a manifest tracking 4,174 successful conversions plus 11 errored pages. Probably the most directly consumable text corpus of the lot — if their OCR is clean we may not need to re-OCR.

### [Onebooming/US-WAR-GOV-UFO](https://github.com/Onebooming/US-WAR-GOV-UFO)
*Created 2026-05-08 15:29 UTC.* Stub — title points at `war.gov/UFO/` PDFs but the repo has effectively no content. Tracking only.

---

## Searchable archives / reading rooms

These go beyond mirroring: full-text search, OCR, RAG chat, or wiki-style cross-linking.

### [robzilla1738/clubufo](https://github.com/robzilla1738/clubufo)
*Created 2026-05-08 14:51 UTC, 13 commits.* "ClubUFO — a reading room for declassified UFO/UAP documents." Browsable library + RAG chat over 161 PDFs with **page-cited answers**. Stack: Next.js 15 / React 19 / Tailwind v4 / shadcn/ui frontend; Neon Postgres + pgvector; DeepSeek for chat, OpenAI `text-embedding-3-small` for embeddings; Drizzle ORM; `unpdf` for serverless PDF extraction; Vercel Blob storage; admin ingestion routes. The README frames sources as "public, declassified, and citizen-submitted" — broader than just war.gov. Closest to a fully-shaped end-user product right now.

### [zexiro/uap-disclosure-archive](https://github.com/zexiro/uap-disclosure-archive) — 1 star
*Created 2026-05-08 14:58 UTC.* Self-hosted searchable mirror of all 162 records. Python pipeline (CSV parse, concurrent download, OCR via `pdftotext` / `ocrmypdf`); MiniSearch index in the frontend; a single-page search UI; **Obsidian vault** with 162 cross-linked notes; **TF-IDF and perceptual-hash similarity** to surface content and visual relationships; 6-hour automated refresh; deployed on Railway with persistent volumes. Stated longer-term ambition: a "Disclosure Globe" aggregating AARO, NUFORC, Project Blue Book, and international archives. Architecturally the most aligned with what we want — worth watching closely.

### [zvizdo/ufo-knowledge-base](https://github.com/zvizdo/ufo-knowledge-base)
*Created 2026-05-08 04:14 UTC — about 13 hours **before** the war.gov release.* Pre-existing connected wiki of the UFO/UAP discourse: ~2,258 pages, ~29,000 wikilinks, covering 957 people, 406 concepts, 260 organisations, 138 incidents, 129 places, 103 documents, 84 programmes. Plain Markdown with YAML frontmatter, organised in `ufo-kb/wiki/` by entity type, raw sources in `ufo-kb/raw/`. Built with Claude Code custom skills (`kb-import`, `kb-query`, `kb-maintain`), embeddings index via `qmd`, Python YouTube-transcript ingestion, Obsidian-compatible. Explicitly frames itself as **mapping discourse, not adjudicating truth** — contested claims get conflict flags rather than resolution. As of this snapshot it does **not yet reference the war.gov release**. This is the most interesting peer for our purposes: a mature schema for the surrounding context that the new corpus can be plugged into.

---

## Download/automation tooling

### [davemorin/pursue-ufo-files](https://github.com/davemorin/pursue-ufo-files)
*Created 2026-05-08 17:34 UTC, 1 commit.* Node.js + Playwright (Chromium) automation for fetching the manifest, downloading all 119 PDFs (~8–10 GB), and emitting agency/theme summaries. Calls out a useful gotcha: **war.gov sits behind Akamai with bot detection**, so plain `curl` / `fetch` is rejected — only in-browser `fetch()` calls inherit the right TLS fingerprint. Uses base64 + HTTP Range requests for large files. Includes `ANALYSIS.md` and `KRIPAL_BRIEFING.md` scaffolding. Author Dave Morin (former Facebook/Path) gives this some signal weight despite the nascent state.

---

## Datasets and analyser skills

### [ckpxgfnksd-max/uap-release-01](https://github.com/ckpxgfnksd-max/uap-release-01) — 11 stars
*Created 2026-05-08 14:51 UTC.* "Mirror of the May 2026 war.gov PURSUE UAP/UFO release (132 files, 2.4 GB). LFS-backed example corpus for the uap-release-analyzer skill." Most useful as a **canonical, hash-stable, LFS-backed dataset** — the description even positions it as a fixture for evaluating an analyser tool. If we want a reproducible test corpus this may be the cleanest pin.

---

## Analysis / commentary

### [joseph-schiro/WAR.GOV---UAP-Evidence-Analysis](https://github.com/joseph-schiro/WAR.GOV---UAP-Evidence-Analysis)
*Created 2026-05-08 16:22 UTC.* Stated as "Deep analysis of the UAP files released on War.gov/UFO" but contents are minimal — README, GPL-3.0 LICENSE, and a single `index.html`. Tracking; substance not yet visible.

### [RUFOIOT/editorial-uap-pursue](https://github.com/RUFOIOT/editorial-uap-pursue)
*Created 2026-05-08 15:47 UTC.* Spanish-language editorial commentary by Felipe Salgado — "El Gran Show de la Transparencia." Single HTML file, opinion/analysis rather than data. Useful as one data point on international reception.

---

## Out of scope

### [ufo50bingo/ufo50bingo_classify](https://github.com/ufo50bingo/ufo50bingo_classify)
*Created 2026-05-08 17:04 UTC.* False positive — name and owner indicate this relates to **UFO 50** (the retro video game collection) and bingo card classification, not the war.gov release. Listed for completeness so it doesn't get re-evaluated.

### [knoelle-svg/ufo-data-engineering](https://github.com/knoelle-svg/ufo-data-engineering)
*Created 2026-05-08 17:37 UTC.* Personal portfolio project — README is two lines: "Exploring my technical skills using UFO data." No code, no clear connection to the war.gov release. Tracking only.

---

## Takeaways for our approach

- **OCR is largely solved** — at least two projects (UFO-USA, uap-disclosure-archive) have already produced full page-level text. We should evaluate consuming one of those rather than redoing OCR from PDFs ourselves.
- **A canonical dataset pin exists** in `ckpxgfnksd-max/uap-release-01` (LFS, 132 files, hash-stable). Worth using as an immutable reference even if we maintain our own working copy.
- **The Akamai/Playwright gotcha** is real — anyone building a download script needs to know this up front (`davemorin/pursue-ufo-files` documents it cleanly).
- **No one has yet attempted** what we want at the centre: a typed, queryable, graph-shaped substrate that connects this corpus to the wider UFO/UAP discourse. `zvizdo/ufo-knowledge-base` has the schema for the surrounding context but not yet the new corpus; `zexiro/uap-disclosure-archive` has the corpus and similarity links but not the wider entity graph; `clubufo` has a polished RAG product but a single-corpus scope.
- **The gap we should fill** is the substrate layer — an entity/event/claim model with page-level provenance — that the existing mirrors and RAG chat UIs can be re-pointed at, and that survives across every future release tranche.
