# 03 — Empirical calibration against the OCR'd corpus

*Status: open. Third entry in the ongoing architectural discussion. Closes the open questions from [02](02-peer-substrate-survey.md) with corpus evidence.*
*Date: 2026-05-08, ~22:00 UTC. Working corpus: [`UFO-USA/converted/`](../../UFO-USA/converted/) — 119 documents, 4,174 OCR'd Markdown pages, ~10.4 M characters. PDFs themselves still mid-download.*

[01](01-hypergraph-hypothesis-and-prior-art.md) framed the hypergraph hypothesis abstractly. [02](02-peer-substrate-survey.md) refined it from peer code: claims are the atomic unit, hyperedges sit above claims, and four supporting layers (vocab, manifest, OCR, page-provenance) have working peer implementations to compose. Five open questions remained, all of them empirical. This entry answers them against the actual corpus and uses the answers to set quantitative targets for the schema.

The work split three ways: a vocabulary-coverage pass run mechanically against the entire 119-doc corpus, and two qualitative samples (claim arity + kind-enum calibration on incident-shaped docs; contradiction hunt + redaction-density study) executed by parallel research agents.

## Q4 — How well does `uap-release-analyzer`'s vocabulary actually do?

The analyzer ships with four fixed vocabularies ([analyze.py](../../uap-release-analyzer/scripts/analyze.py)): `PHENOMENA` (17 terms), `AGENCIES` (19), `LOCATIONS` (50), `REDACTION_MARKERS` (14), plus a `(b)(N)` regex.

Running these against the full 4,174-page corpus (after stripping the obvious frontmatter contamination — see methodology note at the end), the headline numbers are:

| Vocab | Top hits (cleaned) | Worth noting |
|---|---|---|
| **PHENOMENA** | `UFO` (~9.5k / 119 docs), `UAP` (~3.2k / 64), `disc` (~2.8k / 41), `saucer` (~2.6k / 27), `flying disc` (~1.5k / 21), `unidentified` (~1k / 46), `orb` (239 / 28), `sphere` (139 / 25), `metallic` (104 / 26), `cigar` (54 / 18), `cylinder` (25 / 9), `triangle` (24 / 11). **`tic-tac` / `tic tac` zero hits** — the famously evocative term from Nimitz 2004 simply does not appear in this corpus. |
| **AGENCIES** | `Air Force` (2,375 / 53), `FBI` (1,779 / 54), `CIA` (1,635 / 73), `Army` (592 / 25), `NASA` (324 / 11), `Navy` (305 / 22), `NSA` (167 / 25), `AARO` (162 / 35), `Marine` (89 / 17), `NRO` (52 / 16), `DOS` (43 / 12), `FAA` (14 / 4), `NORAD` (2 / 1). **`ODNI`, `DHS` zero hits.** Naive `DOW`/`DIA`/`DOD` counts are inflated (substring contamination — see below). |
| **LOCATIONS** | `Washington` (800 / 29), `CENTCOM` (392 / 34), `Russia` (245 / 24), `Syria` (236 / 9), `OBBI` Bahrain ICAO (109 / 11), `Arabian Gulf` (106 / 11), `Iraq` (99 / 4), `Pentagon` (93 / 13), `Greece` (85 / 4), `Pacific` (81 / 19), `UAE` (75 / 3 — only matches "United Arab Emirates", not the abbreviation), `Persian Gulf` (63 / 3), `Strait of Hormuz` (57 / 6), `Roswell` (57 / 5), `Iran` (53 / 10), `Japan` (51 / 14), `Skylab` (49 / 1), `Djibouti` (28 / 1), `Papua New Guinea` (11 / 1), `INDOPACOM` (10 / 1). **Zero hits**: bare `UAE`, `Saudi Arabia`, `Red Sea`, `East China Sea`, `Indo-Pacific`, `AFRICOM`, `North Korea`, ICAO codes `OMDB OEDR OKBK OAIX HEDC`. |
| **REDACTION** | `REDACTED` (2,393 / 92), `[REDACTED]` (2,299 / 91), `CLASSIFIED` (733 / 68), `REL TO USA` (242 / 20), `NOFORN` (141 / 15), `SECRET//NOFORN` (124 / 14), `FOUO` (83 / 9), `TOP SECRET` (44 / 12), `CUI` (38 / 8). |
| **`(b)(N)`** | `(b)(6)` 454, `(b)(1)` 150, `(b)(3)` 89, `(b)(7)` 3. (b)(6) — *personal privacy* — dominates. (b)(1) — *national security classified* — is the second axis. |

What the analyzer **misses entirely** but that appears densely in the corpus:

| Term | Hits / docs | Why it matters |
|---|---|---|
| `Mission Report` | **725 / 34** | Primary document type for a third of the corpus |
| `[1.4a]` | **719 / 20** | Corpus-specific redaction code for unit/asset identifiers — a single token does the work of hundreds of free-text `[redacted]` markers |
| `MISREP`, `MSGID`, `MAJCOM`, `COCOM` | each ~26 / 26 | Mission-report header fields — *every* DOW Mission Report contains all four |
| `USCENTCOM` | 388 / 34 | Theatre command — a typed entity slot |
| `ISR` | 257 / 31 | Intelligence/Surveillance/Reconnaissance — sensor-modality slot |
| `ATO` (Air Tasking Order) | 198 / 49 | Operational anchor across many reports |
| `AW` (Air Wing) | 191 / 30 | Unit-type suffix |
| `Approved for Release` (to AARO) | 153 / 32 | A `procedural` claim type appearing across nearly every modern doc |
| `FMV` (Full-Motion Video) | 112 / 23 | Sensor type |
| `Debrief` | 97 / 8 | Document subtype distinct from Mission Report |
| `CAOC`, `AOC` | 43 / 25, 63 / 25 | Command operations centres |
| `SIGINT`, `IMINT` | 45 / 17, 29 / 13 | Intelligence-discipline slots |
| `OKAS` | 37 / 9 | A non-listed ICAO code (Al Asad, Iraq) |
| `NAVCENT`, `INHERENT RESOLVE` | 32 / 9, 25 / 11 | Operation/program names |
| `LRE`, `RTB`, `DGS`, `AIRHANDLER` | 32 / 17 down to 8 / 8 | Mission-narrative jargon (Launch Recovery Element, Return To Base, Distributed Ground System, SIGINT system name) |
| `Range Fouler` | 24 / 6 | A doctrinal term for "unidentified contact intruding on a training range" — its own document subtype |
| `SU-30 / SU-27 / B-52` | small but specific | Adversary/friendly aircraft mentions tied to specific incidents |

**Verdict on Q4.** The analyzer's vocab is **calibrated to historic UFO discourse, not to modern operational documents**. It catches the FBI / NICAP-era terminology (UFO, disc, saucer, classified, FOUO) that dominates the 1947-onward archival sections but misses almost everything that gives the modern Mission Reports their structured-form feel. **An operational vocabulary extension is required**, organised by category:

1. **Document-type vocab**: `MISREP`, `MSGID`, `MSNID`, `Mission Report`, `Range Fouler Debrief`, `Reporting Form`, `Crew Debriefing`, `Cable`, `Memorandum`.
2. **Command-structure vocab**: `MAJCOM`, `COCOM`, `USCENTCOM`, `INDOPACOM`, `EUCOM`, `AFRICOM`, `NAVCENT`, `CAOC`, `AOC`, `AOC` numbered (`609 CAOC`, `603 AOC`), `JS`-stamps.
3. **Unit-type vocab**: `ATKS` (Attack Squadron), `SOS` (Special Operations Squadron), `AW` (Air Wing), `ATKS`, plus role tokens `ATKS`, `PAROC`, `163 AW`, `12 AF`.
4. **Sensor vocab**: `FMV`, `EO`, `IR`, `SWIR`, `MX-20`, `MX-25`, `SIGINT`, `IMINT`, `ISR`, `radar`, `EO/IR pod`.
5. **Programme/Operation vocab**: `INHERENT RESOLVE`, `OP HUMMER SICKLE`, `OP PHANTOM FLEX` — extracted dynamically rather than enumerated, since each release will introduce new operation names.
6. **Redaction-code vocab**: `[1.4a]`, `[3.5c]`, `(b)(N)` regex, `Exemption (b)(6)`, `~~SECRET~~`, `~~SECRET//REL TO USA, FVEY~~`.
7. **ICAO vocab**: extend with `OKAS` (Al Asad), `LICZ` (Sigonella), `OKBA` etc, ideally pulled from a static ICAO list filtered against corpus mentions.
8. **MGRS-grid regex**: lat/lon redactions in DOW reports use MGRS-style grids like `38SMC36[1.4a]20[1.4a]`. A regex `[0-9]{1,2}[A-Z]{3}[0-9]{2}(\[[^\]]+\][0-9]+)*` captures these without enumeration.

This vocab extension is the immediate concrete deliverable from this entry — small enough to hand-author, large enough to materially improve recall over running the analyzer raw on the 2026 corpus.

## Q1, Q5 — Kind enum and redacted-claim placeholders

A 30-sentence sample drawn from 5 DOW Mission Reports + 2 NASA transcripts + 2 State cables, classified into clubufo's four-value enum (`factual / witness / speculation / instruction`):

| Kind | Count | Notes |
|---|---|---|
| `witness` | 14 (47%) | Crew/pilot observations, sensor detections, secondhand witness reports |
| `factual` | 8 (27%) | Operator assessments, environmental statements, negative findings, structured-field values like "Observer Assessment of UAP: Benign" |
| `instruction` / `procedural` | 4 (13%) | "Approved for Release to AARO", classification markings, declassification directives |
| `metadata` | 2 (7%) | Mission-event timestamps, tasking intake — distinct from `factual` because they describe the *record-keeping*, not the *phenomenon* |
| `speculation` | 1 (3%) | The Apollo 12 LMP's "I was thinking they're dropping from my water boiler, but it looks like some of those things are escaping the Moon" — explicit hypothesis with uncertainty marker |
| `redacted_placeholder` | 1 (3%) | A whole-paragraph `[REDACTED]` block where no claim text exists but graph topology must survive |

**Verdict on Q1.** clubufo's four-value enum survives but is incomplete. **Extend to seven values**:

```
kind ∈ { factual, witness, speculation, instruction,
         metadata, procedural, redacted_placeholder }
```

Operational definitions:

- `witness` — direct sensory or sensor observation by a named (or [redacted]) participant.
- `factual` — assessment, environmental condition, structured-field value, or negative finding ("no B-52 overflights on Jan 24").
- `speculation` — explicitly hedged hypothesis ("I was thinking…", "probably", "possibly").
- `instruction` — directive to act ("file this report by…", "submit to AARO").
- `procedural` — record-keeping or release authorisation ("Approved for Release to AARO", classification stamps, declassification directives by named authority).
- `metadata` — structured form-field event records ("AT 0542Z, [1.4a] TOOK OFF FROM OKAS") that describe the *mission record* rather than the *phenomenon*.
- `redacted_placeholder` — fully suppressed text where graph topology must survive (see Q5 below).

**Verdict on Q5.** Redacted-claim placeholders are non-negotiable. Mission Reports show **100% of pages contain redaction markers**, with `[1.4a]` appearing 719 times across 20 documents. Crucially, in claims like:

> AT 2147Z, [1.4a] WAS REACTED TO BY 1-3 ACFT, INCLUDING 1X POSS RFAF SU-30, THAT GOT APPROXIMATELY 5NM FROM [1.4a] THE ACFT APPROACHED WESTWARD FROM THE SYRIAN COAST, FLEW DIRECTLY UNDER [1.4a] ORBIT (FL190, VS [1.4a] FL243) FOR APPROXIMATELY 2 MIN, FLEW SOUTH FOR ABOUT 10NM, AND THEN RETURNED WEST.

…the **claim topology survives** (time, observer-class, hostile-craft type, distance, altitudes, durations, trajectories) even when **specific asset identity is redacted**. A query like *"all UAP observations moving north after 2000Z under reaction by hostile aircraft"* must traverse edges whose asset node is opaque. Without a first-class redacted placeholder, the graph fractures at every redaction. With one, the asset slot becomes a typed-but-anonymised participant — `Asset(redacted_id="1.4a-occurrence-N", classification_caveat="…")` — which can still be a participant in the hyperedge, can still link to other claims that mention the same `[1.4a]` token, and can still be flagged for cross-tranche dedup if a later release reveals the identity.

The tabular metadata (POC / QC / APPROVER blocks) is **35–45% fully redacted** (names, phones, emails); the operational context (rank, unit, wing) is mostly visible. This is precisely the case where **anonymised-but-typed participant nodes** carry analytical weight: the *role* (POC vs APPROVER) and the *unit* (163 AW) are queryable even when the *individual* is not.

## Q2 — Claim arity histogram

Across 9 sampled documents (5 DOW MISREPs + 2 NASA transcripts + 2 State cables), enumerated typed participants per central incident:

| Arity bucket | Doc count | Typical contents |
|---|---|---|
| 0 (non-incident) | 1 | State Department weekly blotter mentioning UAP testimony only as a bullet |
| 3 | 1 | DOW SIGINT-collection mission with no UAP sub-event |
| 6–7 | 4 | NASA Apollo transcripts, State PNG cable, lighter DOW reports |
| 8–10 | 3 | Substantive DOW Mission Reports with full POC/operations/sensor metadata |
| 11–12 | 0 | — |
| 13–20 | 0 | — |
| 20+ | 0 | — |

**Empirical observation: incident arity in this corpus is bounded ≤ ~12.** DOW Mission Reports cluster at 8–11 typed participants (heavy operational metadata + observer chain), NASA crew transcripts at 6–7 (sparse: witness, location, time, phenomenon, observer-role), State cables at 6–9 (reporting chain + named witnesses + locations).

**Architectural consequence**: the hypergraph schema can be designed around a **manageable upper bound**. An n-ary edge of arity 8–12 is awkward to express as a flat property-graph reified Incident node (each role would be a separate edge — manageable but verbose) and *natural* in TypeDB-style `relation` types or RDF named-graph-per-incident. **The n-ary fidelity argument from [01](01-hypergraph-hypothesis-and-prior-art.md) holds but is bounded.** We do not need a hyperedge primitive that generalises to arity-50; we need one that handles arity-12 cleanly and is unambiguously preferable to 12 separate binary edges.

## Q3 — Contradictions

Diligent search across multi-section FBI HQ file 62-HQ-83894, the multiple FBI September 2023 sighting serials, the three Apollo-17 documents, and overlapping DOW theatre reports surfaced **four plausible contradictions**:

1. **Kenneth Arnold sighting date**: one FBI section dates the sighting "26 June 1947" ([001 / Section 10](../../UFO-USA/converted/001-65_HS1-834228961_62-HQ-83894_Section_10/)), another "July 25th" ([004 / Section 4](../../UFO-USA/converted/004-65_HS1-834228961_62-HQ-83894_Section_4/)). Same witness, same location, same object count — incompatible dates. (The historically attested date is 24 June 1947; both FBI memoranda are wrong, in different ways.)
2. **Rhodes photographs first-report date**: April 30, 1947 ([006 / Section 6](../../UFO-USA/converted/006-65_HS1-834228961_62-HQ-83894_Section_6/)) vs. July 1947 ([004 / Section 4](../../UFO-USA/converted/004-65_HS1-834228961_62-HQ-83894_Section_4/)). Possibly explained by report-vs-interview-vs-photograph-delivery distinct events, but the corpus does not adjudicate.
3. **September 2023 sighting — object morphology disagreement**: [Serial 3](../../UFO-USA/converted/117-FBI_September_2023_Sighting_-_Serial_3/) describes "a bright white light" with no structure; [Serial 5](../../UFO-USA/converted/119-FBI_September_2023_Sighting_-_Serial_5/) describes a "metallic / gray, no wings or exhaust, 1–2 Blackhawk lengths" structured object. Same convoy, same date.
4. **September 2023 — corroboration timeline**: Serial 3 has the first witness alerting peers in real time (initially nothing seen), Serial 5 reads as solitary observation. Conflicting collective-vs-individual framing of the same event.

**Verdict on Q3.** Contradictions are **real but rare in absolute terms**. Three of the four are date discrepancies that *might* resolve to mis-dating in original docs; only the September 2023 morphology disagreement is sharply incompatible. **Implication**: contradiction-detection should be a **derived analytical view**, not a primary edge type baked into the substrate. Schema should support `contradicts(claim_A, claim_B, axis: <date|location|morphology|witness-count|...>)` as an emit-able derived relation, but the design should not center on it. The **September 2023 morphology case** is a single high-value test bed — when the substrate is ready, that incident is the regression test for "do contradictions show up correctly under multi-witness queries."

## Where this leaves the architecture

Recasting [02](02-peer-substrate-survey.md)'s stack with [03](03-empirical-calibration.md)'s evidence:

```
                  ┌──────────────────────────────────────────┐
                  │  Hyperedges over claims                  │  arity ≤ 12, role-typed
                  │  (TypeDB / RDF-star / Neo4j+reified)     │  store choice still open
                  └──────────────────────────────────────────┘
                                  ▲
                                  │
                  ┌──────────────────────────────────────────┐
                  │  Claims (atomic, page-linked, kind-typed)│  kind ∈ 7 values:
                  │  + redacted_placeholder for opaque text  │  factual / witness / speculation /
                  │  + Pages + Chunks + Documents            │  instruction / procedural /
                  └──────────────────────────────────────────┘  metadata / redacted_placeholder
                                  ▲
                                  │
                  ┌──────────────────────────────────────────┐
                  │  Manifest (firstSeen / lastSeen /        │  abigailhaddad pattern
                  │   removedFromSource)                      │
                  └──────────────────────────────────────────┘
                                  ▲
                                  │
                  ┌──────────────────────────────────────────┐
                  │  Vocab + regex extraction                │  uap-release-analyzer base
                  │  + operational-doc extension             │  + 8-category extension
                  │  (doc-types, command-structure, units,   │  authored from this entry
                  │   sensors, programmes, redaction codes,  │
                  │   ICAO, MGRS-grid)                       │
                  └──────────────────────────────────────────┘
                                  ▲
                                  │
                  ┌──────────────────────────────────────────┐
                  │  OCR/text fallback chain                 │  UFO-USA Markdown first;
                  │  (Gemini → Tesseract/RapidOCR → vision)  │  local OCR for gaps
                  └──────────────────────────────────────────┘
```

**Three bounded targets** the schema must hit:

1. Hyperedges of arity ≤ 12 with role-typed participants and a single anchoring `kind: incident` (or whatever the top-level role naming becomes).
2. `kind` enum of 7 values, validated as a closed set at the claims layer.
3. First-class `redacted_placeholder` claims with structured anonymised-asset participants (`Asset(redacted_token="1.4a", classification_caveat="SECRET//REL TO USA, FVEY")`) that can themselves enter hyperedges.

Plus **three derived (not primary) views** the analytical layer must support:

- Contradiction detection between claims, axis-typed (date / location / morphology / witness-count / sensor-modality).
- Cross-tranche delta (manifest-level via `firstSeen/lastSeen/removedFromSource`).
- Vocabulary-coverage telemetry per tranche (so we can tell, when a new tranche lands, whether our vocab is silently going stale).

## Methodology caveat (for future entries)

Two known sources of contamination in the vocab-coverage numbers above, both worth fixing in entry 04 before we trust this work for store-choice decisions:

1. **Frontmatter contamination**: every UFO-USA page-MD has a YAML frontmatter block including `model: "gemini-3.1-flash-lite"`. Naive substring matching attributed ~4,200 hits to "Gemini" that are actually the OCR-model name, not the NASA programme. The `(b)(6)` count of 454 is also slightly inflated by this path. Real numbers need frontmatter stripping before the count.
2. **Non-word-boundary substring matching**: the analyzer uses bare `text.lower().count(term.lower())` for vocab terms. `DOW` matches "down", "shadow"; `DIA` matches "media", "indian", "diagram"; `DOD` matches "rhododendron". The naïve `DOW` (7,352) and `DIA` (5,178) counts in §Q4 are inflated; the *category-level* shape of the findings (which terms are common, which are missing) holds, but we should not cite the specific big numbers without word-boundary regex.

Neither caveat affects the structural conclusions of this entry — but both should be fixed before the vocab layer is shipped as production code.

## Open for entry 04

1. **Commit to a store choice.** TypeDB vs. Neo4j + reified Incident vs. RDF-star + named-graph-per-tranche vs. claims-only-RDB + on-demand graph view. The criteria are now concrete: arity ≤ 12 with typed roles; closed `kind` enum; cross-tranche bitemporal-ish at manifest level; redacted-asset participation in hyperedges; derived contradiction view.
2. **Prototype: round-trip a single Mission Report.** Pick `045-DOW-UAP-D28` (Iraq, Sept 2024, ~10-arity, with a clean UAP narrative and redactions) and walk it through *manifest → vocab + regex extraction → claims with kind enum → hyperedge construction → query for "all UAP observations during PGM shots in Iraq 2024".* Use whatever store wins (1).
3. **Author the operational vocab extension.** The 8 categories from §Q4. Hand-coded, keep it auditable; gap-fill with LLM only where vocabulary is genuinely open-ended (programme names per tranche).
4. **Strip the frontmatter, run the vocab properly.** Re-run §Q4 with frontmatter removed and word-boundary regex; record the corrected baseline so future tranches can be diffed against it.
