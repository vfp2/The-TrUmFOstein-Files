#!/usr/bin/env python3
"""Verify queries against the loaded TrUmFOstein substrate.

Demonstrates that the architecture from entries 01-05 actually works on the
8 May 2026 PURSUE corpus.
"""
from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "ingest"))
from typedb.driver import TransactionType
from _typedb import driver, DB


def header(s: str) -> None:
    print(f"\n{'─' * 78}\n  {s}\n{'─' * 78}")


def main() -> None:
    with driver() as d:
        with d.transaction(DB, TransactionType.READ) as tx:

            # ── Q0: substrate health ─────────────────────────────────────────
            header("Q0 — substrate health")
            for kind in ["document", "page", "claim", "incident",
                         "operation", "unit", "person", "location",
                         "time-anchor", "classification", "agency"]:
                rows = tx.query(f"match $x isa {kind}; reduce $c = count;").resolve()
                cnt = next(rows.as_concept_rows()).get("c").get()
                print(f"  {kind:18s}  {cnt:6d}")
            for rel in ["mission", "incident-event", "incident-sequence",
                        "manifest-disagreement", "claim-provenance", "has-page"]:
                rows = tx.query(f"match $r isa {rel}; reduce $c = count;").resolve()
                cnt = next(rows.as_concept_rows()).get("c").get()
                print(f"  rel:{rel:14s}  {cnt:6d}")

            # ── Q1: D28 manifest disagreement ───────────────────────────────
            header("Q1 — D28 manifest-vs-body disagreement (entry 04 finding)")
            rows = tx.query(
                'match $md isa manifest-disagreement, has disagreement-field $f, '
                'links (document-of: $d, manifest-claim: $mc, body-claim: $bc); '
                '$d has filename $fn; '
                '$mc has text-content $mtxt; '
                '$bc has text-content $btxt; '
                'select $fn, $f, $mtxt, $btxt;'
            ).resolve()
            for r in rows.as_concept_rows():
                fn   = r.get("fn").get_string()
                f    = r.get("f").get_string()
                mtxt = r.get("mtxt").get_string()
                btxt = r.get("btxt").get_string()
                print(f"  document : {fn}")
                print(f"  field    : {f}")
                print(f"  manifest : {mtxt}")
                print(f"  body     : {btxt}")

            # ── Q2: Western US — incidents involving USPER5 + USPER6 ─────────
            header("Q2 — incidents witnessed by both USPER5 and USPER6 (entry 04 finding)")
            rows = tx.query(
                'match $u5 isa person, has anonymised-token "USPER5"; '
                '$u6 isa person, has anonymised-token "USPER6"; '
                '$ie isa incident-event, links (incident: $i, witness: $u5, witness: $u6); '
                '$i has name $n; '
                'select $n;'
            ).resolve()
            for r in rows.as_concept_rows():
                print(f"  - {r.get('n').get_string()}")

            # ── Q3: temporal-sequence between Dark Kite and Transparent Kite ─
            header("Q3 — incident-sequence relations")
            rows = tx.query(
                'match $seq isa incident-sequence, has sequence-kind $k, '
                'links (source-incident: $src, target-incident: $tgt); '
                '$src has name $sn; $tgt has name $tn; '
                'select $sn, $tn, $k;'
            ).resolve()
            for r in rows.as_concept_rows():
                print(f"  - [{r.get('k').get_string()}] "
                      f"{r.get('sn').get_string()} → "
                      f"{r.get('tn').get_string()}")

            # ── Q4: missions by COCOM ───────────────────────────────────────
            header("Q4 — DOW Mission Reports by COCOM (top-level hierarchical hyperedge)")
            rows = tx.query(
                'match $m isa mission, links (cocom-unit: $cc); '
                '$cc has name $n; '
                'reduce $c = count groupby $n;'
            ).resolve()
            for r in rows.as_concept_rows():
                print(f"  - {r.get('n').get_string():30s} "
                      f"{r.get('c').get()} missions")

            # ── Q5: missions by Operation ───────────────────────────────────
            header("Q5 — DOW Mission Reports by Operation")
            rows = tx.query(
                'match $m isa mission, links (operation: $op); '
                '$op has operation-name $n; '
                'reduce $c = count groupby $n;'
            ).resolve()
            for r in rows.as_concept_rows():
                print(f"  - {r.get('n').get_string():35s} "
                      f"{r.get('c').get()} missions")

            # ── Q6: visual-artifact documents ───────────────────────────────
            header("Q6 — visual-artifact documents (image-only, no OCR text)")
            rows = tx.query(
                'match $d isa document, has shape "visual-artifact", has name $n; '
                'reduce $c = count;'
            ).resolve()
            cnt = next(rows.as_concept_rows()).get("c").get()
            print(f"  {cnt} visual-artifact documents")
            rows = tx.query(
                'match $d isa document, has shape "visual-artifact", has name $n; '
                'limit 5; select $n;'
            ).resolve()
            for r in rows.as_concept_rows():
                print(f"  - {r.get('n').get_string()}")
            print("  ...")

            # ── Q7: document shape distribution ─────────────────────────────
            header("Q7 — document shape distribution (entry 04 taxonomy)")
            rows = tx.query(
                'match $d isa document, has shape $s; '
                'reduce $c = count groupby $s;'
            ).resolve()
            shape_counts = []
            for r in rows.as_concept_rows():
                shape_counts.append((r.get("s").get_string(),
                                     r.get("c").get()))
            for s, c in sorted(shape_counts, key=lambda x: -x[1]):
                print(f"  {c:5d}  {s}")

            # ── Q8: download status ─────────────────────────────────────────
            header("Q8 — acquisition status (cross-tranche durability plumbing)")
            rows = tx.query(
                'match $d isa document, has acquisition-status $s; '
                'reduce $c = count groupby $s;'
            ).resolve()
            for r in rows.as_concept_rows():
                print(f"  {r.get('c').get():5d}  {r.get('s').get_string()}")

            # ── Q9: claim density per shape ─────────────────────────────────
            header("Q9 — claim density per document shape (extraction completeness)")
            rows = tx.query(
                'match $d isa document, has shape $s; '
                '$cp isa claim-provenance, links (document: $d, claim: $c); '
                'reduce $n = count($c) groupby $s;'
            ).resolve()
            for r in rows.as_concept_rows():
                print(f"  {r.get('n').get():6d} claims  "
                      f"in shape={r.get('s').get_string()}")


if __name__ == "__main__":
    main()
