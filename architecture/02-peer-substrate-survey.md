# 02 — Peer substrate survey: schemas, pipelines, and what to steal

*Status: open. Second entry in the ongoing architectural discussion. Refines [01](01-hypergraph-hypothesis-and-prior-art.md).*
*Date: 2026-05-08, ~20:30 UTC. Documents not yet ingested; this is reconnaissance against peer code.*

After [01](01-hypergraph-hypothesis-and-prior-art.md) framed the hypergraph hypothesis abstractly, we forked and cloned the most architecturally interesting peer repos and read their actual schemas and pipelines. The point of this entry is **not to crown a winner** — it is to extract what is genuinely worth stealing, what we should extend, and where peer choices reinforce or weaken the n-ary hypothesis.

The cloned forks live one directory up, under [`vfp2/`](https://github.com/vfp2): [`UFO-USA`](../../UFO-USA/), [`uap-disclosure-archive`](../../uap-disclosure-archive/), [`pursue-ufo-files`](../../pursue-ufo-files/), [`uap-release-analyzer`](../../uap-release-analyzer/), [`uap`](../../uap/) (sanderlegit), [`ufo-knowledge-base`](../../ufo-knowledge-base/) (zvizdo), [`clubufo`](../../clubufo/), [`alien-files`](../../alien-files/), [`ufo-releases`](../../ufo-releases/) (abigailhaddad), [`war-gov-ufo-release-1`](../../war-gov-ufo-release-1/), [`Chat-With-Aliens`](../../Chat-With-Aliens/) (empty shell).

---

## Schemas (data-model side)

### `sanderlegit/uap` — SQLite document-centric star schema

The closest *analytical* peer to our project commits to a flat star schema. From [`uap/analyze_v2.py`](../../uap/analyze_v2.py):

```sql
CREATE TABLE documents (
  id, filename, title, agency, release_date, incident_date,
  incident_date_parsed, incident_location, latitude, longitude,
  description, file_type, has_redaction, total_pages,
  text_length, extraction_method, decade, summary, ocr_applied
);

-- Satellite tables, all with shape (document_id FK, attribute_text):
CREATE TABLE sensors             (..., sensor_type, mention_count);
CREATE TABLE witnesses           (..., witness_type);
CREATE TABLE object_descriptions (..., shape, mention_count);
CREATE TABLE behaviors           (..., behavior);
CREATE TABLE entities            (..., entity_type, entity_value);
CREATE TABLE redactions          (..., redacted_pages, black_rect_count, black_area_pct);
CREATE TABLE cross_references    (..., reference);            -- free-text, no FK
CREATE TABLE graph_edges         (..., source_id, target_id, weight, edge_type);
```

Each "satellite" table is `(document_id, value_text, optional_count)` — these are typed *mentions*, not entities. There is no `sensors` *table-of-sensors* with deduped sensor instances; there's a list of sensor *mentions* per document. The same is true for witnesses, behaviors, and entities.

`graph_edges` derives binary edges between documents post-hoc, with three `edge_type`s: `content_similarity` (TF-IDF cosine), `media_pairing` (explicit same-case links), `same_case` (filename patterns). Edges are *secondary derivation*, not primary data.

**What this tells us**: even the closest analytical peer in the survey doesn't reify an Incident as anything. Every relationship dissolves into either a document-level mention or a derived TF-IDF similarity. **The hypergraph gap is real even versus the most analytically motivated peer.**

### `zvizdo/ufo-knowledge-base` — markdown wiki with YAML frontmatter

Files-as-database. Entities live under [`ufo-kb/wiki/entities/{people, organizations, incidents, places, programs, documents, craft-phenomena, tech-artifacts, symbols-glyphs}/`](../../ufo-knowledge-base/ufo-kb/wiki/). Each entity is a single markdown file. The structured layer is the YAML frontmatter; relationships are implicit `[[wikilink]]` references in the body.

Confirmed examples ([`1908-tunguska.md`](../../ufo-knowledge-base/ufo-kb/wiki/entities/incidents/1908-tunguska.md)):

```yaml
type: entity
summary: "June 30, 1908 aerial explosion over Siberia..."
sources: [raw/youtube-transcripts/JGE1NIGhBzw.md]
name: 1908 Tunguska Event
date: "1908-06-30"
location: Siberia, Russia (Podkamennaya Tunguska River region)
witnesses: [Evenki people (local)]
craft_type: null
corroboration: instrumented
tags: [tunguska, taurid-meteor-stream, airburst, cosmic-impact, siberia, 1908]
```

Schema is per-entity-type and not strictly enforced. Conflict tracking is *narrative*, not structured — inline `⚠ Potential conflict:` annotations in concept and synthesis pages, no `conflicts_with` field, no contradiction edges.

Four Claude skills under [`.claude/skills/`](../../ufo-knowledge-base/.claude/skills/) drive maintenance:
- `kb-import` — bulk markdown ingest, entity extraction, link resolution.
- `kb-query` — graph walk via `shortest-path.py` / `neighbors.py` / `shared-connections.py`.
- `kb-maintain` — frontmatter validation, jaccard-similarity for missing-link detection.
- `kb-evolve` — synthesis page generation, thematic clustering.

**No war.gov references yet** — `git grep` and log show three commits, latest is "feat: expand KB with new entities, concepts, and transcripts", nothing referencing PURSUE / 2026-05-08 / war.gov. The richest schema for the *surrounding* discourse, but it has not yet absorbed the new corpus. Plug-in surface for us.

**What this tells us**: discourse-shaped entities are well-modelled in plain markdown if you accept narrative-only conflict tracking and per-type loose schemas. The wikilink graph approximates a hyper*walk* but not a hyper*edge*.

### `robzilla1738/clubufo` — Postgres + pgvector with claims as a first-class table

The most production-shaped relational schema we've seen. From [`lib/db/schema.ts`](../../clubufo/lib/db/schema.ts), the hierarchy is **document → page → (chunk ⊕ claim)**:

```typescript
documents: { id, title, filename, sha256, mediaKind, agency, documentType,
             incidentDate, incidentLocation, tags[], status, searchTsv, ... }

pages:     { id, documentId FK, page, rawText, cleanedText, pageSummary,
             documentType, classification, inferredDate, redactions,
             entities: jsonb[],   // [{ name, type }]
             rawExtraction: jsonb, status }

chunks:    { id, documentId FK, pageId FK, page, chunkIndex, content,
             tokenCount, embedding: vector(1536) }

claims:    { id, pageId FK, documentId FK, text, charStart, charEnd,
             kind: enum('factual','witness','speculation','instruction'),
             embedding: vector(1536) }

conversations / messages with citations: jsonb[]
```

The standout is `claims`. Every claim is **atomic**, **page-linked**, **char-range-localised**, **typed by epistemic kind**, and **independently embedded**. Citations carry FKs to the originating chunk *and* claim *and* page. This is the closest existing peer schema to what we want as our atomic unit.

Hybrid retrieval ([`lib/search/hybrid.ts`](../../clubufo/lib/search/hybrid.ts) + [`app/api/chat/route.ts`](../../clubufo/app/api/chat/route.ts)): parallel pgvector cosine + Postgres FTS, reciprocal-rank fusion, top 12 of 18 requested. Chunking is recursive-character with `TARGET_CHARS = 3200, OVERLAP_CHARS = 400`.

**What this tells us**: the `claims` table shape is so close to what we want as the atomic unit that **we should design from there, not from scratch**. The kind enum (`factual|witness|speculation|instruction`) is a great starting epistemic taxonomy.

### `Chat-With-Aliens` — empty README shell

Schema not present. The repo contains only README, CHANGELOG, CONTRIBUTING, LICENSE — no SQL, no ORM, no source code. The Postgres-FTS-not-vectors choice mentioned in the description is unverifiable from the public artifact. Skip.

---

## Pipelines (extraction side)

### `ckpxgfnksd-max/uap-release-analyzer` — vocab-first, no LLM, idempotent

The 48★ Claude skill is *not* an LLM extraction system. It is a **regex + hardcoded-vocabulary** pipeline that runs four idempotent stages: [`scripts/inventory.py`](../../uap-release-analyzer/scripts/inventory.py) → [`extract_text.py`](../../uap-release-analyzer/scripts/extract_text.py) → [`analyze.py`](../../uap-release-analyzer/scripts/analyze.py) → [`build_report.py`](../../uap-release-analyzer/scripts/build_report.py), producing a fixed 11-section `REPORT.md`:

```
1. Inventory                          7. Redactions
2. What's actually in the release     8. Notable individual files
3. Where the activity is concentrated 9. Cross-document patterns
4. Phenomena terminology             10. What's missing / caveats
5. Agency cross-references           11. Files in this analysis
6. Year clusters
```

The vocabularies are auditable lists in code: phenomena terms (`UAP, UFO, unidentified, anomalous, flying disc, sphere, orb, cylinder, disc, triangle, saucer, cigar, tic-tac, ...`), agency tokens (`FBI, DOW, DOD, ODNI, CIA, NSA, NASA, NRO, DOS, DIA, AARO, ...`), redaction markers (`[REDACTED], NOFORN, SECRET//NOFORN, FOUO, CUI, /NOFORN, REL TO USA, ...` plus regex `(b)(N)`), locations including ICAO codes (`OMAM, OMDB, ...`). Agency-prefix mapping table at [`references/agency_vocab.md`](../../uap-release-analyzer/references/agency_vocab.md) maps filename prefixes (`65_hs1*`, `dow-uap*`, `nasa-uap-d*`, `dos-uap*`, `18_*`, `38_*`, `59_*`, ...) to agency / record-group identity.

**What this tells us**: pure rule-based extraction over a tight vocabulary is **fast, auditable, hallucination-free, and gets ~70% of the entity surfacing for ~0% of the LLM cost**. We should ship a vocab layer like this *underneath* whatever LLM-driven layer we add.

### `Pump-OS/alien-files` — three-stage OCR + MiniSearch + Claude RAG with strict citation discipline

OCR pipeline ([`pipeline/03_extract.py`](../../alien-files/pipeline/03_extract.py)):

1. Try PyMuPDF native text extraction.
2. If page yields `< 50 chars`, render at 300 DPI and Tesseract OCR.
3. Serialize to per-record JSON + flat `fulltext.json`.
4. `is_scan` flag set when `≥ 50%` of pages had to be OCR'd.

MiniSearch index schema ([`web/src/components/home-explorer.tsx`](../../alien-files/web/src/components/home-explorer.tsx)):

```typescript
new MiniSearch({
  fields: ["title", "description", "agency", "incident_location"],
  storeFields: ["id", "slug", "title", "description", "agency",
                "incident_location", "ext"],
  searchOptions: { boost: { title: 3, agency: 2 }, prefix: true, fuzzy: 0.15 }
});
```

Claude RAG system prompt ([`web/src/app/api/chat/route.ts`](../../alien-files/web/src/app/api/chat/route.ts)) is the strictest citation regimen we've seen — **every non-trivial sentence must end with `[N]` or `[N][M]`, the model is barred from outside knowledge, and a `Sources:` line is required**. Worth quoting if we adopt this style.

### `vng9trmgr8-pixel/war-gov-ufo-release-1` — one-shot manifest parser

[`build_data.py`](../../war-gov-ufo-release-1/build_data.py) parses the war.gov CSV into type-segregated arrays (pdfs / images / videos), with a threaded DVIDS poster fetcher (`ThreadPoolExecutor(max_workers=8)`). Per-record `aiSummary: true` flag suggests an LLM-summary layer downstream that we haven't located. Notable: uses **RapidOCR** (ONNX runtime, faster than Tesseract) as the OCR fallback in [`extract_text.py`](../../war-gov-ufo-release-1/extract_text.py) — an option we should know about. No removal tracking, no live update.

### `abigailhaddad/ufo-releases` — live mirror with removal tracking

The only peer with continuous ingestion. Two GitHub Actions workflows:

- **[`refresh-csv.yml`](../../ufo-releases/.github/workflows/refresh-csv.yml)** — daily 13:30 UTC; Playwright + stealth → fetch CSV → upsert merge → commit if changed.
- **[`extract-text.yml`](../../ufo-releases/.github/workflows/extract-text.yml)** — chained on `workflow_run: completed`, 350-min timeout; pdftoppm + OpenAI vision per-page OCR.

Three architectural patterns to steal:

1. **Akamai bypass via stealth-Playwright + cookie wait**, from [`scripts/fetch-csv.ts`](../../ufo-releases/scripts/fetch-csv.ts) — disables `AutomationControlled` blink feature, hides `navigator.webdriver`, **waits for `bm_sz=` or `ak_bmsc=` cookies** before fetching from inside the page context. Stronger than the basic Playwright pattern in our preserved [`pursue-ufo-files`](../../pursue-ufo-files/) clone.

2. **Removal-tracking upsert**: every record carries `firstSeenAt`, `lastSeenAt`, `removedFromSource: boolean`. Vanished records are flagged, not deleted:

   ```typescript
   merged.push({
     ...prev,
     firstSeenAt: prev.firstSeenAt ?? prev.releaseDate ?? today,
     lastSeenAt: prev.lastSeenAt ?? today,
     removedFromSource: true,   // key flag — preserves history
   });
   ```

   This is precisely the cross-tranche durability pattern entry 01 was reaching for, expressed at the manifest level.

3. **Strict transcription prompt** (paraphrased from [`scripts/extract-text.ts`](../../ufo-releases/scripts/extract-text.ts)): mandates `[illegible]`, `[unclear: best guess?]`, `[strikethrough: ...]`, `[blank page]` markers; bans paraphrasing; bans repeated-word artefacts; preserves marginalia and stamps.

---

## What we steal, extend, or avoid

| | Source | Why |
|---|---|---|
| **Steal outright** | uap-release-analyzer's vocabularies (agencies, phenomena, redaction markers, locations, ICAO codes, filename prefixes) | Auditable, hallucination-free, ~70% of entity surfacing for ~0% LLM cost. Run beneath any LLM layer we add. |
| **Steal outright** | abigailhaddad's `firstSeenAt / lastSeenAt / removedFromSource` upsert | Exactly the cross-tranche durability pattern entry 01 needed, at the right level (manifest), expressible in any store. |
| **Steal outright** | abigailhaddad's stealth-Playwright + Akamai-cookie-wait | Strongest Akamai bypass we've seen. Replaces our preserved davemorin script. |
| **Steal outright** | abigailhaddad's strict-transcription OCR prompt | Sets the right discipline for any vision-LLM OCR fallback. |
| **Steal outright** | clubufo's `claims` table shape — atomic, page-linked, char-range, kind-typed, embedded | The closest existing schema to what we want as our atomic unit. Use it as the foundation; the n-ary layer sits *above* claims, not below. |
| **Adapt** | clubufo's hybrid retrieval (pgvector cosine + Postgres FTS + RRF, top 12 of 18) | Solid retrieval pattern; we'll need it whatever store we pick. RRF over heterogeneous indexes generalises. |
| **Adapt** | uap-release-analyzer's 11-section REPORT.md format | Useful as a *baseline reproducibility artefact* for each tranche, even if our richer outputs are graph/notebook-shaped. |
| **Adapt** | alien-files' Claude system prompt (every sentence cited, no outside knowledge, `Sources:` line) | Adopt for our retrieval-grounded synthesis layer. |
| **Extend** | clubufo's `kind` enum (`factual / witness / speculation / instruction`) | Likely needs `analytical` (post-hoc agency analysis), `directive`, `redacted-claim` (where the claim itself is `[REDACTED]` but a placeholder must exist for graph topology). To be calibrated against actual document content in entry 03. |
| **Extend** | zvizdo's per-entity-type YAML schemas | They lack required-field discipline; we'll formalise them as TypeBox / Zod / JSON-Schema checked frontmatter that the substrate validates. |
| **Avoid** | sanderlegit's free-text `cross_references.reference` | Loses entity identity. Cross-references must resolve to typed entities or be flagged unresolved. |
| **Avoid** | sanderlegit's "satellite tables of mentions" pattern | Conflates *entity instances* with *mentions of attribute values*. We should keep mentions and entities at different layers. |
| **Avoid** | TF-IDF-only similarity edges as primary graph data | OK as a derived/exploratory layer; not as the canonical edge set. |
| **Avoid** | Conflict tracking as inline narrative | zvizdo's `⚠ Potential conflict:` is unqueryable. Contradictions need to be a structured edge type. |

---

## Where the hypergraph hypothesis stands after seeing peer code

Three updates to entry 01:

**1. The atomic unit should be the *claim*, not the *incident*.** Every peer that gets close — clubufo's `claims`, sanderlegit's mention-tables, zvizdo's `firsthand_claims` frontmatter — agrees implicitly. An "incident" is best modelled as a *participant role-set over claims*, not as a primary record. This means our hypergraph isn't `Incident({witness, time, location, sensor, ...})` directly — it is `Hyperedge({claim_a, claim_b, claim_c, ...}, role: "constitutes-incident-X")`. **Hyperedges-over-claims**, not hyperedges-over-raw-facts. The hypothesis survives but the bottom layer changes.

**2. Provenance is solved at the page-level layer, not the hypergraph layer.** clubufo's `(documentId, pageId, charStart, charEnd)` shape on `claims` is sufficient. The hypergraph layer doesn't need to re-implement provenance — it inherits it from its constituent claims. This simplifies the store choice: pure-hypergraph stores' weak provenance story matters less than entry 01 implied.

**3. Cross-tranche durability is a manifest-level concern, expressible alongside any store.** abigailhaddad's `firstSeenAt / lastSeenAt / removedFromSource` is store-agnostic. We don't need Datomic-style native bitemporality at the substrate; we need disciplined upsert merge at the manifest layer plus immutable claim records below. This further simplifies the store choice.

The candidate stack now looks like:

```
                  ┌──────────────────────────────────────────┐
                  │  Hyperedges over claims                  │  ← n-ary primitive
                  │  (TypeDB, RDF-star, or property-graph)   │     (still TBD; entry 03)
                  └──────────────────────────────────────────┘
                                  ▲
                                  │
                  ┌──────────────────────────────────────────┐
                  │  Claims (atomic, page-linked, kind-typed)│  ← clubufo-shaped, extended
                  │  + Pages + Chunks + Documents            │
                  └──────────────────────────────────────────┘
                                  ▲
                                  │
                  ┌──────────────────────────────────────────┐
                  │  Manifest with firstSeen/lastSeen/removed│  ← abigailhaddad pattern
                  └──────────────────────────────────────────┘
                                  ▲
                                  │
                  ┌──────────────────────────────────────────┐
                  │  Vocab + regex extraction (pre-LLM)      │  ← uap-release-analyzer
                  └──────────────────────────────────────────┘
                                  ▲
                                  │
                  ┌──────────────────────────────────────────┐
                  │  OCR/text fallback chain                 │  ← UFO-USA Markdown first,
                  │  (Gemini → Tesseract/RapidOCR → vision)  │     local OCR when needed
                  └──────────────────────────────────────────┘
```

The hypergraph store is now the *only* layer above clubufo-shaped claims still genuinely contested. The rest of the stack has working peer implementations we can compose.

---

## Open questions for the next entry

1. **What does the `kind` enum actually need to be?** clubufo's four values (`factual / witness / speculation / instruction`) is a hypothesis. Empirical calibration needs samples from actual documents — we now have 4,174 page-MDs in [UFO-USA `converted/`](../../UFO-USA/converted/) and 117 `.txt` files in [uap-disclosure-archive `raw/text/`](../../uap-disclosure-archive/raw/text/) to work against.
2. **What is the typical claim arity in incidents?** Entry 01's open question, now answerable: sample N incidents, count distinct claim participants per incident, build a histogram. This bears directly on whether n-ary buys us anything.
3. **Where do contradictions actually occur?** Find concrete cases in the corpus where two documents make incompatible claims about the same incident. Without these, the contradiction-edge type is hypothetical.
4. **How well does uap-release-analyzer's vocabulary actually do?** Run it against the corpus, count what it surfaces vs misses, decide what an LLM layer above it must add.
5. **Does the kind enum need a `redacted` value?** If a sentence is `[REDACTED]` but we still need a placeholder for graph topology, the claim exists but the text is suppressed. This is also where named-graph-per-classification-level may come in.

**Next entry (03)**: empirical calibration against the OCR'd corpus we already have — claim arity histogram, kind-enum field study, concrete contradiction-pair hunt, vocab-coverage measurement.
