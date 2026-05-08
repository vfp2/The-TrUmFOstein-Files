# 01 — Hypergraph hypothesis and prior art

*Status: open. First entry in an ongoing architectural discussion.*
*Date: 2026-05-09. Documents have not yet been ingested; this is pre-data architectural reconnaissance.*

## The hypothesis

A UAP "incident" is intrinsically n-ary. A single sighting binds, all at once:

> ⟨ witness(es), location, time, object/phenomenon, sensor/medium, evidence-type, originating-organisation, investigator, weather/atmospheric-conditions, classification-status, source-document(s) ⟩

A binary-edge property graph forces one of two distortions: (a) reify the incident as a node and explode the n-ary relation into many typed binary edges (losing "all together at once"), or (b) drop participants to keep the edge binary (losing fidelity). Our hypothesis is that the right primitive is a **hyperedge** — a single typed relation with role-checked participants — and that picking this up front avoids years of re-modelling later.

Equally, several of our project goals do **not** decompose to "edge arity":

- **Page-level provenance** — every claim, every participant, every relation must trace to `(file_id, page)`.
- **Cross-tranche durability** — the corpus grows every few weeks; conclusions made against tranche N must survive (and be diff-able) when tranche N+1 lands.
- **Contradiction / conflict detection** — when two agencies describe the same incident differently, we want to query the disagreement, not paper over it.

The architecture has to serve all of these together. This entry is the first pass at whether a pure hypergraph delivers.

## Prior art for UFO/UAP data

Direct search for hypergraph or n-ary approaches to UFO/UAP corpora returns essentially nothing. The terminology collisions are loud (Guizzardi's gUFO foundational ontology, Microsoft's UFO³ GUI agent) but no academic paper, dataset, or open-source project explicitly chose a true hypergraph or n-ary-first representation for UFO/UAP data. Negative finding, but a useful one — **the hypothesis is genuinely novel for this domain**.

What has been built, by shape:

| Project | Era | Storage | Schema shape |
|---|---|---|---|
| Larry Hatch *U* / uDb | 1980s–2000s | Flat single-file Win98 catalogue | 85 fields/record, 64 binary attribute flags, ~18k cases — closed controlled vocabulary, no provenance per claim |
| UFOCAT (CUFOS) | 1967 → present | Magnetic tape → dBase IV → Access → Excel | Wide-table relational, ~300k entries (~192k primary), one row per cross-source-merged report |
| NUFORC | 1974 → present | Flat records (CSV/JSON-grade) | (date, city, state, shape, summary, full-text, link) — community scrapes treat as line-delimited JSON |
| MUFON CMS | 2006 → present | MySQL + Perl CGI (LAMP) | Case-record table with categorical fields; BAASS funded $350k tune-up 2008 |
| Project Blue Book (NARA) | 1947–1969 | Paper case files; microfilm T-1206 (94 reels) | Page-level images + sparse metadata; modern digitisations (Fold3, Project Blue Book Archive, Black Vault) all preserve "page+JSON" shape |
| NICAP InterLink | 1990s–present | Static HTML web | Hand-edited cross-linked category pages; "NSID" is dBase-grade ~4k entries |
| The Black Vault | 1996 → present | Filesystem (~3.84M pages, ~6,000 agency/year directories) + Elasticsearch search | Document archive; page-level provenance via filename only |
| AARO public records | 2024 → | DoD-certified cloud (per SORN AARO-0001) | Schema undisclosed; mission language is "intake, indexing, visualization across multiple security domains" |
| BAASS / AAWSAP | 2008–2010, $22M DIA | 11 separate per-investigator case databases (per leaked 2009 Ten-Month Report) + MUFON-funded merge | No unified schema; chaotic Excel/relational silos |
| SkyWatch / ufocat.com | 2024–2026 | Property graph + vector ("GraphRAG with NVIDIA cuGraph") | 500k+ reports → "dynamic knowledge graphs"; binary edges, not hyperedges |
| CE3.io | 2025 | Property graph + vector (undisclosed stack) | Entities (people, programs, incidents) with temporal/org correlation |
| Enigma Labs | 2024–2025 | Weaviate + GraphQL + Llama 3 + RAG | Vector-led, not hyperedge-led |
| Wikidata | 2012 → | RDF-graph with reified statements + qualifiers | n-ary-via-reification; UAP coverage patchy entity-level, not incident-level |
| zvizdo/ufo-knowledge-base | 2026-05-08 (pre-PURSUE) | Markdown vault + YAML frontmatter, Obsidian wikilinks, embeddings via `qmd` | ~2,258 pages, ~29,000 wikilinks, 957 people / 406 concepts / 138 incidents — discourse map, not relational substrate |
| zexiro/uap-disclosure-archive | 2026-05-08 | Python pipeline → MiniSearch + Obsidian vault, TF-IDF + perceptual-hash similarity | 162 records, page-level OCR, no entity layer |
| clubufo (robzilla1738) | 2026-05-08 | Neon Postgres + pgvector, Drizzle, Next.js | RAG chat over 161 PDFs with page citations; document-and-chunk shape |
| DenisSergeevitch/UFO-USA | 2026-05-08 | PyMuPDF → Gemini OCR → Markdown + JSONL manifest | 4,174 page-MDs across 120 docs; pure document conversion, no entity layer |

**Pattern**: every public UFO/UAP store is one of {flat file, wide-table RDBMS, document archive, vector + property-graph hybrid}. None reify an "incident" as a typed n-ary relation with role-checked participants. The closest production-grade pattern in *any* adjacent domain is **Palantir Gotham's Dynamic Ontology** — Object / Event / Link with reified Event objects, still binary-edge.

## Hypergraph prior art in adjacent domains

A wave of generic 2025–2026 hypergraph-RAG literature has appeared, none yet applied to UAP:

- **HyperGraphRAG** — Luo et al., NeurIPS 2025. n-ary relation extraction → bipartite hyperedge store + vector indices for entities *and* hyperedges; benchmarked in medicine, agriculture, CS, law. ([arXiv 2503.21322](https://arxiv.org/abs/2503.21322), [code](https://github.com/LHRLAB/HyperGraphRAG))
- **HyperRAG**, **PRoH**, **Order-Aware Hypergraph RAG** — all 2025–2026, all generic-domain.
- **Text2NKG** — schema-agnostic n-ary relation extraction supporting hyper-relational, event-based, role-based, and hypergraph schemas; directly applicable to incident-shaped corpora. ([arXiv 2310.05185](https://arxiv.org/abs/2310.05185))
- **Wolfram hypergraph rewriting** — mathematics-of-physics; no production storage layer. Inspirational only.

For event-shaped intelligence data the closest deployed analogues are still binary-edge:

- **Palantir Gotham Dynamic Ontology** — Object / Event / Link with reified Event objects.
- **GTD-derived Terrorism Knowledge Graph** (IEEE 8823450) — binary KG over GTD's ~120-variable wide-table cases.
- **IARPA Mercury / Aladdin** — programme literature emphasises event detection over store schema.

## Candidate storage technologies for n-ary modelling

Ranked roughly by fit-on-paper for our specific goals:

1. **TypeDB** ([typedb.com](https://typedb.com/)) — n-ary relations + role types are first-class. Enhanced ER model with inheritance and role constraints; called a "structured hypergraph" in their own materials. **3.0.0 released Dec 2024**, active. Strongest pure-hypergraph fit. Production stories cluster in cyber-threat-intel, finance, life sciences. Page-level provenance requires explicit Provenance relations.
2. **RDF + RDF-star / SPARQL-star** — W3C **RDF 1.2 / SPARQL 1.2** targeting Candidate Recommendation **Q2 2025**. Supported in GraphDB (full), Apache Jena/Fuseki (default), RDF4J (experimental), Stardog. Edge-as-subject + classical reification both available. **Strongest provenance story** of any candidate (PROV-O is native), but ergonomics are heavier.
3. **Datomic** — EAV+T datoms, immutable + bitemporal "as-of" queries. **1.0.7469 released Oct 2025**. n-ary modelled via entity-as-fact pattern. **Best fit for cross-tranche durability** — "what did we believe about Incident X on date Y" is a free query.
4. **Neo4j + reified Incident nodes** — every incident becomes a node, participants attach via typed binary edges with role labels. Loses one-shot hyperedge semantics; gains every existing tool, every existing graph-RAG framework, GQL/Cypher. The "boring" pragmatic winner that almost always wins in practice. Comparable to TypeDB on provenance.
5. **HypergraphDB (Kobrix)** — Java embedded, hyperedges-of-hyperedges, automatic reification. **Last release 1.3 in 2015**, blog dormant since 2017. **Do not pick** for production.
6. **HyperNetX** (PNNL, [GitHub](https://github.com/pnnl/HyperNetX)) — Python analysis library, **v2.4.3 Apr 2026**, active. No persistent store, no transactions. Use as analytics layer over whichever store we pick.
7. **Wolfram hypergraph framework** — Mathematica-only, physics-foundations work. Inspiration, not deployment.

## Preliminary compare and contrast, keyed to our goals

Against four explicit goals:

|  | n-ary fidelity | Page-level provenance | Cross-tranche durability (bitemporal) | Contradiction / conflict |
|---|---|---|---|---|
| TypeDB | **Native** (n-ary + roles) | Explicit Provenance relations | Application-level versioning | Typed roles make role-conflict diff easy |
| RDF-star | n-ary via reified statement (good) | **Native** (PROV-O, named graphs) | Application-level + named-graph-per-tranche | **Native** (named-graph-per-source, query the diff) |
| Datomic | Reified entity-as-fact (workable) | Native (every datom carries TX) | **Native** (bitemporal "as-of") | Time-travel diff is native; entity diff needs application logic |
| Neo4j + reified Incident | Workaround, but mature ecosystem | Equivalent to TypeDB | Application-level versioning | Application-level diff |
| HyperGraphRAG (academic) | Native | Not addressed | Not addressed | Not addressed |

No single candidate dominates across all four columns. **n-ary fidelity is most contested, but provenance and bitemporality are the more architecturally consequential axes** — once committed, they shape every downstream query.

### Three early conclusions

1. **A pure hypergraph store is not obviously the right answer**, despite the hypothesis being well-motivated for incident shape. The technologies that most cleanly serve provenance (RDF-star) and cross-tranche durability (Datomic) are not hypergraph-first. TypeDB is the only mature hypergraph-shaped store, and it requires application-level versioning for the bitemporal axis we need.
2. **A hybrid is the most likely outcome**. Two candidate hybrids worth investigating:
   - **TypeDB primary + RDF-star export view** — n-ary semantics in the working store; PROV-O / named-graph-per-tranche emitted as a published, citable companion graph.
   - **Datomic-style EAV substrate + n-ary view** — bitemporal claims as the foundation; an n-ary projection (TypeDB schema or HyperNetX in-memory analytics) layered for incident-shaped queries. Closer to the "claim-store + materialised views" pattern that has worked in legal-tech and intelligence systems.
3. **The "boring" Neo4j + reified Incident node pattern** still has to be benchmarked. It is what Palantir, Wikidata, and most production event-KGs settled on. If our gain over it is only "expressive fidelity" without any concrete query we couldn't otherwise write, the hypergraph thesis is weakened.

## Open questions to resolve in the next phase (document content investigation)

The right way to validate or refine the hypothesis is to look at the actual documents and count what's there. Specifically:

- **What is the typical arity of an incident as it appears in the released documents?** A 3-arity incident (witness, time, location) tells a different story than a 9-arity incident (witness, sensors, weather, classification, multiple investigators, multi-agency joint reports). UFO-USA's per-page Markdown is now usable for this — we can sample n documents and tally participant slots.
- **How often do two documents describe the same incident with different participants or different facts?** This sets the scale of the contradiction-detection problem and tells us how aggressively we need named-graph-per-source / bitemporal versioning.
- **What is the distribution of well-typed participants vs free-text only?** If most participants resolve to typed entities (named witnesses, identified bases, cataloguable sensors), n-ary is high-value. If most are unstructured prose, the hypergraph buys less and a document-store + extracted-entities sidecar buys more.
- **Are there events that genuinely cannot be expressed as a single n-ary relation?** Multi-stage incidents (sighting → pursuit → loss-of-contact → debrief) suggest sequence-of-hyperedges or temporal subgraphs, which TypeDB and Neo4j handle differently.
- **What does the cross-tranche delta actually look like?** When the next batch lands (war.gov says rolling, every few weeks), what fraction of facts are net-new vs corrections vs duplicates? This argues quantitatively for or against bitemporality.

## What we are not deciding yet

- Specific store (TypeDB vs Datomic vs RDF-star vs Neo4j).
- Whether to use HyperGraphRAG-the-codebase, or roll our own n-ary extraction with Text2NKG-derived patterns.
- Whether the published artefact is a graph, an Obsidian-style vault, an API, a query notebook, or all of the above.

These wait until we have content-shaped evidence. **Next entry**: structural and content investigation against the OCR'd corpus we already have ([UFO-USA](../../UFO-USA/converted/), [uap-disclosure-archive raw/text/](../../uap-disclosure-archive/raw/text/)), to decide which of the candidates above is actually pulling its weight.
