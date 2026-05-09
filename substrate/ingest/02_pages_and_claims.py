#!/usr/bin/env python3
"""Stage 2 — load pages, raw text, and vocab-extracted claims.

For each document:
  - Read all UFO-USA `converted/<NNN-…>/page-NNNN.md` files.
  - Strip YAML frontmatter (entry 03 §methodology caveat).
  - Insert one `page` entity per page, with `text-content`.
  - Connect via `has-page` relation.
  - Run vocab + regex extraction over each page; surface claims with
    extraction-method=regex.

Idempotent: deletes existing pages and claims before reinserting.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from typedb.driver import TransactionType
from _typedb import driver, DB, escape_tql

OCR_DIR = Path("/home/soliax/Documents/github/vfp2/UFO-USA/converted")

YAML_FM = re.compile(r"^---\n.*?\n---\n", re.DOTALL)

# ── vocab from architecture/03 (analyzer base + operational extension) ─────
VOCAB = {
    "phenomena": [
        "UAP", "UFO", "unidentified", "anomalous", "flying disc", "saucer",
        "tic-tac", "tic tac", "orb", "sphere", "cylinder", "disc",
        "triangle", "cigar", "metallic",
    ],
    "agency": [
        "FBI", "DOW", "DOD", "DoD", "ODNI", "CIA", "NSA", "NASA", "NRO",
        "DOS", "DIA", "AARO", "DHS", "FAA", "NORAD", "Air Force", "Navy",
        "Marine", "Army", "USCENTCOM", "USEUCOM", "USINDOPACOM", "NAVCENT",
    ],
    "doc_type": [
        "MISREP", "MSGID", "MSNID", "ACEQUIP", "ATO", "GENTEXT",
        "Mission Report", "Range Fouler", "Crew Debriefing",
    ],
    "command": ["MAJCOM", "COCOM", "CAOC", "AOC", "AFSOC", "ACC"],
    "sensor": ["FMV", "EO", "IR", "SWIR", "ISR", "SIGINT", "IMINT",
               "MX-20", "MX-25", "AIRHANDLER", "NVG", "radar"],
    "operation": ["INHERENT RESOLVE", "OP HUMMER SICKLE", "OP PHANTOM FLEX",
                  "ARMED OVERWATCH", "RECONNAISSANCE", "TARGET DEV"],
    "icao": ["OKAS", "LICZ", "OBBI", "OMAM", "OMDB"],
    "redaction_marker": ["[REDACTED]", "REDACTED", "NOFORN", "SECRET//NOFORN",
                         "TOP SECRET", "REL TO USA", "FOUO", "CUI",
                         "Approved for Release"],
}
TOKEN_REDACTION = re.compile(r"\[1\.4[a-g]\]|\[3\.5[a-z]?\]")
FOIA_RE         = re.compile(r"\(b\)\s?\(([1-9])\)")
MGRS_RE         = re.compile(r"\b\d{1,2}[A-Z]{3}\d{2,4}\b")
ZULU_DTG_RE     = re.compile(r"\b\d{6}:\d{2}Z[A-Z]{3}\d{2}\b|\b\d{4}Z\b")

# ── boundary-aware vocab match ─────────────────────────────────────────────
def find_vocab_matches(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for category, terms in VOCAB.items():
        hits: list[str] = []
        for term in terms:
            # Word-boundary regex; case-sensitive for acronyms (DOW vs "down"),
            # case-insensitive for multi-word general terms.
            if term.isupper() and len(term) <= 6:
                pat = rf"(?:^|[^A-Za-z]){re.escape(term)}(?:[^A-Za-z]|$)"
                if re.search(pat, text):
                    hits.append(term)
            else:
                if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
                    hits.append(term)
        if hits:
            out[category] = hits
    # Token redactions
    rs = TOKEN_REDACTION.findall(text)
    if rs:
        out["redaction_token"] = sorted(set(rs))
    fs = FOIA_RE.findall(text)
    if fs:
        out["foia_exemption"] = sorted({f"(b)({n})" for n in fs})
    mgrs = MGRS_RE.findall(text)
    if mgrs:
        out["mgrs"] = sorted(set(mgrs))[:8]   # cap to avoid claim explosion on ISR pages
    zd = ZULU_DTG_RE.findall(text)
    if zd:
        out["zulu_dtg"] = sorted(set(zd))[:8]
    return out

# ── insert helpers ─────────────────────────────────────────────────────────
def main() -> None:
    print(f"scanning {OCR_DIR} ...")
    doc_dirs = sorted(p for p in OCR_DIR.iterdir() if p.is_dir())
    print(f"  {len(doc_dirs)} document folders found")

    total_pages = 0
    total_claims = 0

    with driver() as d:
        # Wipe existing pages, has-page, claims, claim-provenance
        with d.transaction(DB, TransactionType.WRITE) as tx:
            for q in [
                "match $r isa claim-provenance; delete $r;",
                "match $r isa has-page; delete $r;",
                "match $c isa claim; delete $c;",
                "match $p isa page; delete $p;",
            ]:
                tx.query(q).resolve()
            tx.commit()

        for doc_dir in doc_dirs:
            m = re.match(r"^(\d{3})-(.+)", doc_dir.name)
            if not m:
                continue
            idx = int(m.group(1))
            doc_ident = f"doc-{idx:03d}"
            page_files = sorted(doc_dir.glob("page-*.md"))
            if not page_files:
                continue

            # Confirm doc exists in DB
            with d.transaction(DB, TransactionType.READ) as tx:
                exists = any(True for _ in tx.query(
                    f'match $d isa document, has identifier "{doc_ident}"; select $d;'
                ).resolve().as_concept_rows())
            if not exists:
                continue

            # Batch into transactions of ~50 pages (each page may have multiple claims)
            with d.transaction(DB, TransactionType.WRITE) as tx:
                for pf in page_files:
                    page_num = int(re.search(r"page-(\d+)", pf.name).group(1))
                    raw = pf.read_text(errors="replace")
                    # Strip YAML frontmatter
                    stripped = YAML_FM.sub("", raw, count=1)
                    text_to_index = stripped[:8000]   # cap per-page text in DB

                    page_ident = f"{doc_ident}-p{page_num:04d}"
                    # Insert page
                    tx.query(
                        f'insert $p isa page, has identifier "{page_ident}", '
                        f'has page-number {page_num}, '
                        f'has text-content "{escape_tql(text_to_index)}";'
                    ).resolve()
                    # Connect to document
                    tx.query(
                        f'match $d isa document, has identifier "{doc_ident}"; '
                        f'$p isa page, has identifier "{page_ident}"; '
                        f'insert (document: $d, page: $p) isa has-page;'
                    ).resolve()
                    total_pages += 1

                    # Vocab extraction → claims
                    matches = find_vocab_matches(stripped)
                    claim_idx = 0
                    for category, hits in matches.items():
                        for hit in hits:
                            claim_idx += 1
                            cident = f"{page_ident}-c{claim_idx:03d}"
                            kind = "metadata"
                            ctext = f"{category}:{hit}"
                            tx.query(
                                f'insert $c isa claim, has identifier "{cident}", '
                                f'has kind "{kind}", '
                                f'has extraction-method "regex", '
                                f'has text-content "{escape_tql(ctext)}";'
                            ).resolve()
                            tx.query(
                                f'match $c isa claim, has identifier "{cident}"; '
                                f'$p isa page, has identifier "{page_ident}"; '
                                f'$d isa document, has identifier "{doc_ident}"; '
                                f'insert (claim: $c, page: $p, document: $d) isa claim-provenance;'
                            ).resolve()
                            total_claims += 1
                tx.commit()

            if idx % 10 == 0 or idx == len(doc_dirs):
                print(f"  doc {doc_ident}: cumulative pages={total_pages}, claims={total_claims}")

    print(f"\nDone. Pages inserted: {total_pages}. Vocab claims inserted: {total_claims}.")

if __name__ == "__main__":
    main()
