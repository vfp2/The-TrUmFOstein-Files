#!/usr/bin/env python3
"""Export the TypeDB substrate to a static JSON graph for the Next.js
viewer. Runs against the live `trumfostein` database and produces
viewer/public/graph.json + per-document bundles.

The viewer needs no live DB connection at runtime — graph.json is the
single source of truth.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from typedb.driver import TransactionType                                  # noqa: E402
from _typedb import driver, DB                                             # noqa: E402

REPO       = Path(__file__).resolve().parents[2]
OUT_GRAPH  = REPO / "viewer" / "public" / "graph.json"
OUT_DOCS   = REPO / "viewer" / "public" / "docs"
OUT_DOCS.mkdir(parents=True, exist_ok=True)


def fetch_entities(tx, kind: str, attr_names: list[str]) -> list[dict[str, Any]]:
    """For a given entity kind, return [{id, attrs:{...}}] with the named
    attributes. Each attribute is OPTIONAL (try-block) so entities with a
    sparse attribute set still appear.
    """
    out: list[dict[str, Any]] = []
    rows = tx.query(
        f'match $x isa {kind}, has identifier $i; select $i;'
    ).resolve()
    idents = [r.get("i").get_string() for r in rows.as_concept_rows()]
    for ident in idents:
        attrs: dict[str, Any] = {"identifier": ident}
        for an in attr_names:
            try:
                rows = tx.query(
                    f'match $x isa {kind}, has identifier "{ident}", '
                    f'has {an} $v; select $v;'
                ).resolve()
                vals = []
                for r in rows.as_concept_rows():
                    v = r.get("v")
                    try:
                        vals.append(v.get_string())
                    except Exception:
                        try:
                            vals.append(v.get_integer())
                        except Exception:
                            try:
                                vals.append(v.get_boolean())
                            except Exception:
                                vals.append(str(v))
                if vals:
                    attrs[an] = vals[0] if len(vals) == 1 else vals
            except Exception:
                pass
        out.append({"id": ident, "attrs": attrs})
    return out


def main() -> None:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    def add_node(ident: str, kind: str, label: str, attrs: dict[str, Any]) -> None:
        if ident in seen_ids:
            return
        seen_ids.add(ident)
        nodes.append({"id": ident, "kind": kind, "label": label, "attrs": attrs})

    def add_edge(source: str, target: str, kind: str, role: str = "") -> None:
        edges.append({"source": source, "target": target, "kind": kind, "role": role})

    # Per-kind attribute schedules
    SCHED = {
        "document":       ["name", "shape", "filename", "url", "description",
                           "total-pages", "file-size", "acquisition-status",
                           "first-seen-at", "last-seen-at", "removed-from-source"],
        "agency":         ["name"],
        "incident":       ["name", "description"],
        "person":         ["name", "anonymised-token"],
        "unit":           ["name"],
        "operation":      ["operation-name"],
        "location":       ["place-name", "icao-code", "mgrs-grid"],
        "time-anchor":    ["zulu-dtg", "year", "period"],
        "classification": ["classification-level", "caveat"],
        "foia-exemption": ["foia-code"],
    }
    LABEL_KEY = {
        "document": "name",
        "agency":   "name",
        "incident": "name",
        "person":   "anonymised-token",
        "unit":     "name",
        "operation":"operation-name",
        "location": "place-name",
        "time-anchor": "zulu-dtg",
        "classification": "classification-level",
        "foia-exemption": "foia-code",
    }

    with driver() as d:
        # ── Tier 1 entities ────────────────────────────────────────────
        with d.transaction(DB, TransactionType.READ) as tx:
            for kind, ans in SCHED.items():
                ents = fetch_entities(tx, kind, ans)
                lk = LABEL_KEY[kind]
                for e in ents:
                    label_val = e["attrs"].get(lk) or e["attrs"].get("identifier", e["id"])
                    label = str(label_val) if not isinstance(label_val, list) else str(label_val[0])
                    add_node(e["id"], kind, label[:120], e["attrs"])

        # ── Tier 1 relations as reified hubs + binary edges ───────────
        with d.transaction(DB, TransactionType.READ) as tx:
            mission_role_pairs = [
                ("mission-document", "document"),
                ("operation",        "operation"),
                ("ops-center",       "unit"),
                ("majcom-unit",      "unit"),
                ("cocom-unit",       "unit"),
                ("originating-unit", "unit"),
                ("classification",   "classification"),
                ("contains-incident","incident"),
            ]
            mission_hubs: dict[str, str] = {}

            def mission_hub(doc_ident: str, doc_label: str) -> str:
                if doc_ident in mission_hubs:
                    return mission_hubs[doc_ident]
                hub_id = f"rel-mission-{doc_ident}"
                add_node(hub_id, "rel:mission",
                         f"Mission ({doc_label})",
                         {"of-document": doc_ident})
                mission_hubs[doc_ident] = hub_id
                return hub_id

            doc_label_lookup = {n["id"]: n["label"] for n in nodes if n["kind"] == "document"}

            for role_name, _role_kind in mission_role_pairs:
                rows = tx.query(
                    'match $m isa mission; '
                    f'$m links (mission-document: $doc, {role_name}: $rp); '
                    '$doc has identifier $doci; '
                    '$rp has identifier $rpi; '
                    'select $doci, $rpi;'
                ).resolve()
                for r in rows.as_concept_rows():
                    doc_ident = r.get("doci").get_string()
                    rp_ident  = r.get("rpi").get_string()
                    doc_label = doc_label_lookup.get(doc_ident, doc_ident)
                    hub = mission_hub(doc_ident, doc_label)
                    add_edge(hub, rp_ident, "mission", role_name)

            # incident-event
            ie_role_pairs = [
                ("incident",              "incident"),
                ("anchor-time",           "time-anchor"),
                ("anchor-location",       "location"),
                ("originating-document",  "document"),
                ("witness",               "person"),
            ]
            ie_hubs: dict[str, str] = {}

            def ie_hub(inc_ident: str, inc_label: str) -> str:
                if inc_ident in ie_hubs:
                    return ie_hubs[inc_ident]
                hub_id = f"rel-incidentevent-{inc_ident}"
                add_node(hub_id, "rel:incident-event",
                         f"IE: {inc_label}",
                         {"of-incident": inc_ident})
                ie_hubs[inc_ident] = hub_id
                return hub_id

            inc_label_lookup = {n["id"]: n["label"] for n in nodes if n["kind"] == "incident"}

            for role_name, _role_kind in ie_role_pairs:
                rows = tx.query(
                    'match $ie isa incident-event; '
                    f'$ie links (incident: $i, {role_name}: $rp); '
                    '$i has identifier $ii; '
                    '$rp has identifier $rpi; '
                    'select $ii, $rpi;'
                ).resolve()
                for r in rows.as_concept_rows():
                    inc_ident = r.get("ii").get_string()
                    rp_ident  = r.get("rpi").get_string()
                    if rp_ident not in seen_ids:
                        continue
                    inc_label = inc_label_lookup.get(inc_ident, inc_ident)
                    hub = ie_hub(inc_ident, inc_label)
                    if rp_ident != inc_ident:
                        add_edge(hub, rp_ident, "incident-event", role_name)
                    else:
                        add_edge(hub, inc_ident, "incident-event", "incident")

            # incident-sequence
            rows = tx.query(
                'match $seq isa incident-sequence, has sequence-kind $k; '
                '$seq links (source-incident: $src, target-incident: $tgt); '
                '$src has identifier $si; $tgt has identifier $ti; '
                'select $k, $si, $ti;'
            ).resolve()
            for r in rows.as_concept_rows():
                k = r.get("k").get_string()
                si = r.get("si").get_string()
                ti = r.get("ti").get_string()
                add_edge(si, ti, "incident-sequence", k)

            # issued-by — direct binary edge document → agency
            # (no hub needed; this is genuinely binary)
            rows = tx.query(
                'match $r isa issued-by, links (document: $d, agency: $a); '
                '$d has identifier $di; $a has identifier $ai; '
                'select $di, $ai;'
            ).resolve()
            for r in rows.as_concept_rows():
                di = r.get("di").get_string()
                ai = r.get("ai").get_string()
                add_edge(di, ai, "issued-by", "issued-by")

            # manifest-disagreement
            rows = tx.query(
                'match $md isa manifest-disagreement, has disagreement-field $f; '
                '$md links (document-of: $d, manifest-claim: $mc, body-claim: $bc); '
                '$d has identifier $di; '
                '$mc has identifier $mci, has text-content $mctxt; '
                '$bc has identifier $bci, has text-content $bctxt; '
                'select $f, $di, $mci, $bci, $mctxt, $bctxt;'
            ).resolve()
            for r in rows.as_concept_rows():
                d_ident = r.get("di").get_string()
                mc_id   = r.get("mci").get_string()
                bc_id   = r.get("bci").get_string()
                mc_txt  = r.get("mctxt").get_string()
                bc_txt  = r.get("bctxt").get_string()
                hub = f"rel-manifest-disagree-{d_ident}"
                add_node(hub, "rel:manifest-disagreement", "Manifest disagreement",
                         {"field": r.get("f").get_string()})
                add_node(mc_id, "claim", mc_txt[:80],
                         {"text-content": mc_txt, "side": "manifest"})
                add_node(bc_id, "claim", bc_txt[:80],
                         {"text-content": bc_txt, "side": "body"})
                add_edge(hub, d_ident, "manifest-disagreement", "document-of")
                add_edge(hub, mc_id, "manifest-disagreement", "manifest-claim")
                add_edge(hub, bc_id, "manifest-disagreement", "body-claim")

        # ── Per-document bundles ──────────────────────────────────────
        with d.transaction(DB, TransactionType.READ) as tx:
            doc_idents: list[str] = []
            rows = tx.query('match $d isa document, has identifier $i; select $i;').resolve()
            for r in rows.as_concept_rows():
                doc_idents.append(r.get("i").get_string())

        for di in doc_idents:
            with d.transaction(DB, TransactionType.READ) as tx:
                pages = []
                rows = tx.query(
                    f'match $d isa document, has identifier "{di}"; '
                    f'(document: $d, page: $p) isa has-page; '
                    f'$p has identifier $pi, has page-number $pn, has text-content $tc; '
                    f'select $pi, $pn, $tc;'
                ).resolve()
                for r in rows.as_concept_rows():
                    pages.append({
                        "id":   r.get("pi").get_string(),
                        "page": r.get("pn").get_integer(),
                        "text": r.get("tc").get_string()[:6000],
                    })
                pages.sort(key=lambda p: p["page"])

                claims = []
                rows = tx.query(
                    f'match $d isa document, has identifier "{di}"; '
                    f'(document: $d, claim: $c) isa claim-provenance; '
                    f'$c has identifier $ci, has kind $ck, has text-content $tc, '
                    f'has extraction-method $em; '
                    f'select $ci, $ck, $tc, $em;'
                ).resolve()
                for r in rows.as_concept_rows():
                    kind = r.get("ck").get_string()
                    if kind == "metadata":
                        continue
                    claims.append({
                        "id":     r.get("ci").get_string(),
                        "kind":   kind,
                        "text":   r.get("tc").get_string()[:3000],
                        "method": r.get("em").get_string(),
                    })

                # vocab claim count for the badge
                rows = tx.query(
                    f'match $d isa document, has identifier "{di}"; '
                    f'(document: $d, claim: $c) isa claim-provenance; '
                    f'reduce $n = count;'
                ).resolve()
                total_claims = next(rows.as_concept_rows()).get("n").get_integer()

            (OUT_DOCS / f"{di}.json").write_text(json.dumps({
                "document":      di,
                "pages":         pages,
                "claims":        claims,
                "total_claims":  total_claims,
            }, ensure_ascii=False))

    OUT_GRAPH.write_text(json.dumps({
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "kind_counts": _count_by_key(nodes, "kind"),
        },
    }, ensure_ascii=False))
    print(f"Exported {len(nodes)} nodes, {len(edges)} edges → {OUT_GRAPH}")
    print(f"Per-doc bundles → {OUT_DOCS}/<doc-id>.json ({len(doc_idents)} docs)")


def _count_by_key(items, key):
    out: dict[str, int] = {}
    for it in items:
        k = it[key]
        out[k] = out.get(k, 0) + 1
    return out


if __name__ == "__main__":
    main()
