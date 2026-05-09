#!/usr/bin/env python3
"""Stage 5 — connect every document to a meaningful neighbour.

Two things:
1. Materialise agency entities (DOW, FBI, NASA, DOS) and `issued-by`
   relations from each document to its agency. Without this,
   ~114 of 161 documents have no Tier 1 edges and float disconnected
   in the 3D viewer.

2. Materialise three shared-event incidents that the corpus implies but
   we never wrote:
     - FBI September 2023 Sighting (4 docs: composite sketch + serials 3/4/5)
     - FBI Photo A surveillance series (8 daytime IR/EO frames)
     - FBI Photo B 1999 surveillance series (24 sequential sensor frames,
       12/31/99 18:10:00 - 18:21:02; helicopter visible in B6/B7;
       paired UAP signature in tight-zoom frames)

These tie clusters of documents to a shared incident anchor so the
graph layout reflects the documents' actual semantic relationships.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typedb.driver import TransactionType
from _typedb import driver, DB, escape_tql

PURSUE_DATA = Path("/home/soliax/dev/vfp2/ufouap/data")

AGENCY_MAP = {
    "Department of War":   ("agency-dow",  "DOW",  "U.S. Department of War"),
    "FBI":                 ("agency-fbi",  "FBI",  "Federal Bureau of Investigation"),
    "NASA":                ("agency-nasa", "NASA", "National Aeronautics and Space Administration"),
    "Department of State": ("agency-dos",  "DOS",  "U.S. Department of State"),
}

# Document-shape patterns we use to find the right docs by name (the manifest
# title carries enough signal to identify each cluster precisely).
FBI_SEPT2023_TITLE_PAT = re.compile(r"FBI September 2023 Sighting", re.IGNORECASE)
FBI_PHOTO_A_PAT        = re.compile(r"FBI Photo A\d+",              re.IGNORECASE)
FBI_PHOTO_B_PAT        = re.compile(r"FBI Photo B\d+",              re.IGNORECASE)


def upsert_entity_minimal(tx, kind: str, ident: str, attrs: dict[str, object]) -> bool:
    """Returns True if newly inserted, False if already existed."""
    rows = tx.query(
        f'match $x isa {kind}, has identifier "{ident}"; select $x;'
    ).resolve()
    if any(True for _ in rows.as_concept_rows()):
        return False
    parts = [f'$x isa {kind}, has identifier "{ident}"']
    for k, v in attrs.items():
        if v is None or v == "":
            continue
        if isinstance(v, (int, float, bool)):
            parts.append(f'has {k} {str(v).lower() if isinstance(v, bool) else v}')
        else:
            parts.append(f'has {k} "{escape_tql(str(v))}"')
    tx.query('insert ' + ', '.join(parts) + ';').resolve()
    return True


def main() -> None:
    records = json.loads((PURSUE_DATA / "records.json").read_text())

    with driver() as d:
        # ── 1. Agencies + issued-by ──────────────────────────────────────
        with d.transaction(DB, TransactionType.WRITE) as tx:
            for verbose, (ident, short, full) in AGENCY_MAP.items():
                upsert_entity_minimal(tx, "agency", ident, {"name": short})
            tx.commit()

        # Load the doc-ident → agency-ident mapping
        doc_to_agency: dict[str, str] = {}
        for idx, rec in enumerate(records, start=1):
            ag = (rec.get("agency") or "").strip()
            mapped = AGENCY_MAP.get(ag)
            if not mapped:
                continue
            doc_to_agency[f"doc-{idx:03d}"] = mapped[0]

        # Insert issued-by relations (idempotent: skip if already linked)
        with d.transaction(DB, TransactionType.READ) as tx:
            existing = set()
            rows = tx.query(
                'match $r isa issued-by, links (document: $d, agency: $a); '
                '$d has identifier $di; $a has identifier $ai; '
                'select $di, $ai;'
            ).resolve()
            for r in rows.as_concept_rows():
                existing.add((r.get("di").get_string(), r.get("ai").get_string()))

        inserted = 0
        with d.transaction(DB, TransactionType.WRITE) as tx:
            for doc_ident, ag_ident in doc_to_agency.items():
                if (doc_ident, ag_ident) in existing:
                    continue
                tx.query(
                    f'match $d isa document, has identifier "{doc_ident}"; '
                    f'$a isa agency, has identifier "{ag_ident}"; '
                    f'insert $r isa issued-by, links (document: $d, agency: $a);'
                ).resolve()
                inserted += 1
            tx.commit()
        print(f"issued-by relations inserted: {inserted} (total documents: {len(doc_to_agency)})")

        # ── 2. Shared-event incidents ────────────────────────────────────
        # Find docs by name pattern
        doc_to_name: dict[str, str] = {}
        with d.transaction(DB, TransactionType.READ) as tx:
            rows = tx.query(
                'match $d isa document, has identifier $i, has name $n; select $i, $n;'
            ).resolve()
            for r in rows.as_concept_rows():
                doc_to_name[r.get("i").get_string()] = r.get("n").get_string()

        # Group documents by event
        sept_2023_docs = [di for di, n in doc_to_name.items() if FBI_SEPT2023_TITLE_PAT.search(n)]
        photo_a_docs   = [di for di, n in doc_to_name.items() if FBI_PHOTO_A_PAT.search(n)]
        photo_b_docs   = [di for di, n in doc_to_name.items() if FBI_PHOTO_B_PAT.search(n)]
        print(f"FBI Sept 2023 docs:        {len(sept_2023_docs)}")
        print(f"FBI Photo A surveillance:  {len(photo_a_docs)}")
        print(f"FBI Photo B 1999 series:   {len(photo_b_docs)}")

        events = [
            {
                "incident_id":   "inc-fbi-sept-2023-sighting",
                "incident_name": "FBI September 2023 Sighting",
                "incident_desc": "Multi-witness sighting in September 2023 of a metallic / cigar / linear object near a restricted test site. Documented by an FBI composite sketch and three FD-302 witness interview serials (Serial 3/4/5).",
                "docs":          sept_2023_docs,
            },
            {
                "incident_id":   "inc-fbi-photo-a-surveillance",
                "incident_name": "FBI Photo A surveillance series",
                "incident_desc": "8-frame daytime IR/EO sensor surveillance series with crosshair reticle, heavy redaction blocks, small dark UAP signature visible at or near the crosshair in 7 of 8 frames; one frame shows a small bright orb instead.",
                "docs":          photo_a_docs,
            },
            {
                "incident_id":   "inc-fbi-photo-b-1999-12-31",
                "incident_name": "FBI Photo B sensor surveillance, 12/31/1999 18:10–18:21Z",
                "incident_desc": "24-frame sequential IR/EO sensor recording timestamped 12/31/1999 18:10:00–18:21:02. Two zoom scales (-15..+15 wide and -3..+3 tight). Helicopter visible above the crosshair in frames at 18:10:00 and 18:10:02. Paired/double dark UAP signature visible in 6+ tight-zoom frames between 18:19:54 and 18:21:02.",
                "docs":          photo_b_docs,
            },
        ]

        # Insert incidents + incident-event hyperedges per doc
        for ev in events:
            if not ev["docs"]:
                continue
            with d.transaction(DB, TransactionType.WRITE) as tx:
                upsert_entity_minimal(tx, "incident", ev["incident_id"],
                                      {"name": ev["incident_name"], "description": ev["incident_desc"]})
                tx.commit()
            # Link each document to the incident via an incident-event hub.
            with d.transaction(DB, TransactionType.READ) as tx:
                existing_links = set()
                rows = tx.query(
                    'match $ie isa incident-event, '
                    f'links (incident: $i, originating-document: $d); '
                    f'$i has identifier "{ev["incident_id"]}"; '
                    '$d has identifier $di; '
                    'select $di;'
                ).resolve()
                for r in rows.as_concept_rows():
                    existing_links.add(r.get("di").get_string())
            with d.transaction(DB, TransactionType.WRITE) as tx:
                added = 0
                for doc_ident in ev["docs"]:
                    if doc_ident in existing_links:
                        continue
                    tx.query(
                        f'match $i isa incident, has identifier "{ev["incident_id"]}"; '
                        f'$d isa document, has identifier "{doc_ident}"; '
                        f'insert $ie isa incident-event, '
                        f'links (incident: $i, originating-document: $d);'
                    ).resolve()
                    added += 1
                tx.commit()
            print(f"  {ev['incident_id']}: +{added} incident-event links "
                  f"(of {len(ev['docs'])} docs)")


if __name__ == "__main__":
    main()
