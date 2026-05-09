#!/usr/bin/env python3
"""Stage 3 — structured extraction for high-value document shapes.

Parses MISREP form-fields into typed relations (mission, equipment-loadout,
personnel-chain, timeline, reaction-event, observation-event, isr-collection).
Adds Western US Event slides as multi-incident with USPER1–7 participants.
Encodes the D28 manifest-vs-body disagreement explicitly. Adds visual-artifact
stub claims for the ~25 image-only documents.

This is opinionated extraction — not exhaustive. The goal is to demonstrate
the substrate's expressiveness on representative cases. Deeper extraction is
deferred to a later stage; substrate quality matters more than coverage here.
"""
from __future__ import annotations
import re
from pathlib import Path
from typedb.driver import TransactionType
from _typedb import driver, DB, escape_tql

OCR_DIR = Path("/home/soliax/Documents/github/vfp2/UFO-USA/converted")
PDF_DIR = Path("/home/soliax/dev/vfp2/ufouap/pdfs")
YAML_FM = re.compile(r"^---\n.*?\n---\n", re.DOTALL)

# ── MISREP field patterns (markdown form output from UFO-USA Gemini OCR) ──
# Lines look like:  "* **MAJCOM:** AFSOC"  or  "* Major Command (MAJCOM): AFSOC"
FIELD_RE = re.compile(
    r"^\s*[-*]\s*\*?\*?\s*([A-Za-z][A-Za-z0-9 _/\(\)\-]*?)\s*\*?\*?\s*:\s*(.+?)\s*$",
    re.MULTILINE,
)

# Section headers
SECTION_RE = re.compile(r"^#{1,4}\s*(.+?)\s*$", re.MULTILINE)

# UAP gentext markers
UAP_INITIAL_RE = re.compile(r"Initial Contact DTG:\s*(\S+)", re.IGNORECASE)


def read_doc_text(doc_dir: Path) -> str:
    pages = sorted(doc_dir.glob("page-*.md"))
    return "\n\n".join(YAML_FM.sub("", p.read_text(errors="replace"), count=1) for p in pages)


def parse_fields(text: str) -> dict[str, str]:
    """Return last-occurrence wins so deeper sections override boilerplate."""
    out: dict[str, str] = {}
    for m in FIELD_RE.finditer(text):
        key = re.sub(r"\s+", " ", m.group(1)).strip().lower()
        val = m.group(2).strip()
        # Strip markdown emphasis around the value
        val = val.strip("*").strip()
        if val and val not in {"-", "—"}:
            out[key] = val
    return out


def find_misreps(d, target_shapes=("mission-report",)) -> list[tuple[int, str, Path]]:
    """Return (idx, ident, ocr_dir) for all docs matching shape."""
    found = []
    idents: list[str] = []
    with d.transaction(DB, TransactionType.READ) as tx:
        for shape in target_shapes:
            rows = tx.query(
                f'match $doc isa document, has identifier $i, has shape "{shape}"; select $i;'
            ).resolve()
            for r in rows.as_concept_rows():
                idents.append(r.get("i").as_attribute().get_value())
    for ident in idents:
        m = re.match(r"doc-(\d{3})", ident)
        if not m:
            continue
        idx = int(m.group(1))
        # find the OCR folder
        for p in OCR_DIR.iterdir():
            if p.is_dir() and p.name.startswith(f"{idx:03d}-"):
                found.append((idx, ident, p))
                break
    return sorted(found)


# Process-level cache: each (kind, ident) we know is already inserted in DB.
# Populated lazily as we go so we don't re-attempt and poison transactions.
_INSERTED: set[tuple[str, str]] = set()


# ── reusable insert builders ───────────────────────────────────────────────
def upsert_entity(tx, kind: str, ident: str, attrs: dict[str, object]) -> None:
    """Insert entity if not already present. Uses match-then-insert so
    duplicate keys never poison the transaction.
    """
    if (kind, ident) in _INSERTED:
        return
    # Check existence
    rows = tx.query(
        f'match $x isa {kind}, has identifier "{ident}"; select $x;'
    ).resolve()
    found = any(True for _ in rows.as_concept_rows())
    if found:
        _INSERTED.add((kind, ident))
        return
    parts = [f'$x isa {kind}, has identifier "{ident}"']
    for k, v in attrs.items():
        if v is None or v == "":
            continue
        if isinstance(v, (int, float, bool)):
            parts.append(f'has {k} {str(v).lower() if isinstance(v, bool) else v}')
        else:
            parts.append(f'has {k} "{escape_tql(str(v))}"')
    tx.query('insert ' + ', '.join(parts) + ';').resolve()
    _INSERTED.add((kind, ident))


def relation_insert(tx, var: str, rel_type: str, roles: dict[str, str],
                    match_clauses: list[str], attrs: dict[str, object] | None = None) -> None:
    """Build and execute a TypeDB 3.x relation insert in canonical form:
       match <clauses>; insert $var isa <rel_type>, links (role: $x, role: $y), has X "...", has Y "...";
    """
    role_pairs = ", ".join(f"{r}: {v}" for r, v in roles.items())
    insert_parts = [f'${var} isa {rel_type}, links ({role_pairs})']
    if attrs:
        for k, v in attrs.items():
            if v is None or v == "":
                continue
            if isinstance(v, (int, float, bool)):
                insert_parts.append(f'has {k} {str(v).lower() if isinstance(v, bool) else v}')
            else:
                insert_parts.append(f'has {k} "{escape_tql(str(v))}"')
    q = f'match {"; ".join(match_clauses)}; insert ' + ", ".join(insert_parts) + ';'
    tx.query(q).resolve()


# ── Stage 3a: MISREPs ──────────────────────────────────────────────────────
def ingest_misrep(d, idx: int, doc_ident: str, doc_dir: Path) -> dict:
    text = read_doc_text(doc_dir)
    fields = parse_fields(text)

    op = fields.get("operation")
    domain = fields.get("domain")
    ops_center = fields.get("operations center")
    majcom = fields.get("major command (majcom)") or fields.get("majcom")
    cocom = fields.get("combatant command (cocom)") or fields.get("cocom")
    originator = fields.get("originator (unit or squadron)") or fields.get("originator")
    classification = fields.get("classification")
    caveats = fields.get("associated caveats")
    report_type = fields.get("report type")
    mission_type = fields.get("mission type")
    ato = fields.get("tasking order (ato)") or fields.get("ato") or fields.get("tasking order")

    takeoff_icao   = fields.get("takeoff location (icao code)")
    takeoff_dtg    = fields.get("takeoff time dtg")
    landing_icao   = fields.get("last land location (icao code)")
    landing_dtg    = fields.get("last land time")
    on_station_dtg = fields.get("time on station dtg")
    off_station_dtg = fields.get("time off station dtg")

    # UAP event
    uap_dtg       = fields.get("initial contact dtg")
    uap_assessment = fields.get("observer assessment of uap")
    uap_signatures = fields.get("uap signatures")
    uap_state      = fields.get("uap physical state")
    friendly_loc   = fields.get("friendly aircraft location")
    friendly_alt   = fields.get("friendly aircraft altitude/depth") or fields.get("friendly aircraft altitude")

    # Reaction
    reaction_dtg = None
    enemy_type = fields.get("enemy aircraft type")
    enemy_nationality = fields.get("enemy aircraft nationality")
    # initial contact dtg may collide between UAP and REACTION sections; use first

    has_uap = "uap" in fields.get("uap event type", "").lower() or uap_dtg is not None
    has_reaction = enemy_type is not None
    has_observation = "observation" in text.lower()

    counts = {
        "mission": 1,
        "incident": 1 if has_uap else 0,
        "reaction": 1 if has_reaction else 0,
        "operation": 1 if op else 0,
        "units": sum(1 for x in [ops_center, majcom, cocom, originator] if x),
    }

    with d.transaction(DB, TransactionType.WRITE) as tx:
        # Operation entity (only owns operation-name + identifier)
        if op:
            upsert_entity(tx, "operation", f"op-{op.lower().replace(' ', '-')[:60]}",
                          {"operation-name": op})

        # Units (MAJCOM, COCOM, originator, ops-center)
        for label, val in [("majcom", majcom), ("cocom", cocom),
                           ("originator", originator), ("ops-center", ops_center)]:
            if val:
                slug = re.sub(r"[^a-z0-9-]+", "-", val.lower())[:60]
                upsert_entity(tx, "unit", f"unit-{slug}", {"name": val})

        # Classification
        if classification:
            slug = re.sub(r"[^a-z0-9-]+", "-", classification.lower())[:30]
            cls_ident = f"cls-{slug}-{caveats[:20].lower().replace(' ', '-') if caveats else 'plain'}"
            attrs = {"classification-level": classification}
            if caveats:
                attrs["caveat"] = caveats
            upsert_entity(tx, "classification", cls_ident, attrs)

        # Time anchors for the mission timeline
        for kind_lbl, dtg in [("takeoff", takeoff_dtg), ("landing", landing_dtg),
                              ("on-station", on_station_dtg), ("off-station", off_station_dtg),
                              ("uap-initial", uap_dtg)]:
            if dtg:
                t_ident = f"time-{doc_ident}-{kind_lbl}"
                upsert_entity(tx, "time-anchor", t_ident, {"zulu-dtg": dtg})

        # ICAO locations
        for icao in {takeoff_icao, landing_icao}:
            if icao:
                upsert_entity(tx, "location", f"loc-icao-{icao.lower()}",
                              {"icao-code": icao, "place-name": icao})

        # Incident entity for the UAP event
        if has_uap:
            inc_ident = f"inc-{doc_ident}-uap1"
            inc_name = f"UAP event in {doc_ident}"
            upsert_entity(tx, "incident", inc_ident,
                          {"name": inc_name, "description": (uap_signatures or "")[:500]})

        # Build the mission relation using relation_insert helper
        match_parts = [f'$doc isa document, has identifier "{doc_ident}"']
        roles: dict[str, str] = {"mission-document": "$doc"}
        if op:
            slug = op.lower().replace(' ', '-')[:60]
            match_parts.append(f'$op isa operation, has identifier "op-{slug}"')
            roles["operation"] = "$op"
        if ops_center:
            slug = re.sub(r"[^a-z0-9-]+", "-", ops_center.lower())[:60]
            match_parts.append(f'$opsc isa unit, has identifier "unit-{slug}"')
            roles["ops-center"] = "$opsc"
        if majcom:
            slug = re.sub(r"[^a-z0-9-]+", "-", majcom.lower())[:60]
            match_parts.append(f'$mc isa unit, has identifier "unit-{slug}"')
            roles["majcom-unit"] = "$mc"
        if cocom:
            slug = re.sub(r"[^a-z0-9-]+", "-", cocom.lower())[:60]
            match_parts.append(f'$cc isa unit, has identifier "unit-{slug}"')
            roles["cocom-unit"] = "$cc"
        if originator:
            slug = re.sub(r"[^a-z0-9-]+", "-", originator.lower())[:60]
            match_parts.append(f'$origu isa unit, has identifier "unit-{slug}"')
            roles["originating-unit"] = "$origu"
        if has_uap:
            match_parts.append(f'$inc isa incident, has identifier "inc-{doc_ident}-uap1"')
            roles["contains-incident"] = "$inc"

        attrs: dict[str, object] = {}
        if domain:       attrs["domain"] = domain
        if mission_type: attrs["mission-type"] = mission_type
        if ato:           attrs["ato"] = ato
        if report_type:  attrs["report-type"] = report_type

        try:
            relation_insert(tx, "m", "mission", roles, match_parts, attrs)
        except Exception as e:
            counts["mission"] = 0
            print(f"    {doc_ident}: mission insert failed: {str(e)[:200]}")

        # incident-event (the UAP)
        if has_uap and uap_dtg:
            inc_match = [
                f'$inc isa incident, has identifier "inc-{doc_ident}-uap1"',
                f'$t isa time-anchor, has identifier "time-{doc_ident}-uap-initial"',
                f'$doc2 isa document, has identifier "{doc_ident}"',
            ]
            try:
                relation_insert(tx, "ie", "incident-event",
                                {"incident": "$inc", "anchor-time": "$t", "originating-document": "$doc2"},
                                inc_match)
            except Exception as e:
                print(f"    {doc_ident}: incident-event failed: {str(e)[:200]}")

        tx.commit()

    return counts


# ── Stage 3b: Western US Event slides ──────────────────────────────────────
def ingest_western_us_slides(d) -> None:
    """Hard-coded extraction from the slide deck (entry 04).
    4 incidents, USPER1–7 participants, sequence relation between Dark/Transparent Kite.
    """
    # Find the doc
    with d.transaction(DB, TransactionType.READ) as tx:
        rows = tx.query(
            'match $doc isa document, has shape "multi-incident-deck", has identifier $i; select $i;'
        ).resolve()
        idents = [r.get("i").as_attribute().get_value() for r in rows.as_concept_rows()]
    if not idents:
        print("  no multi-incident-deck found")
        return
    doc_ident = idents[0]

    incidents = [
        ("orbs-launching-orbs", "Orbs Launching Orbs",
         "Orange 'mother' orbs emitting groups of red orbs, witnessed across two days at dusk in Western U.S.",
         ["USPER1", "USPER2", "USPER3", "USPER4", "USPER5", "USPER6"], "dusk"),
        ("large-fiery-orb", "Large, Fiery Orb",
         "Orange glowing orb perched near rock pinnacle, ~1050 m distant (AARO post-hoc), 12-18 m diameter (AARO post-hoc).",
         ["USPER5", "USPER6"], "dusk"),
        ("dark-kite", "Dark Kite",
         "Kite-shaped object with red and white lights observed via NVGs, pre-dawn.",
         ["USPER5", "USPER6"], "pre-dawn"),
        ("transparent-kite", "Transparent Kite",
         "Kite-shaped object ~30 minutes after Dark Kite, transparent in NVGs, USPER7 did not see it.",
         ["USPER5", "USPER6", "USPER7"], "pre-dawn"),
    ]

    with d.transaction(DB, TransactionType.WRITE) as tx:
        # Anonymised USPER persons (deduplicated across incidents)
        for usper in {u for inc in incidents for u in inc[3]}:
            upsert_entity(tx, "person", f"person-{usper.lower()}",
                          {"name": usper, "anonymised-token": usper})

        # Time anchors (period-typed)
        upsert_entity(tx, "time-anchor", "time-westus-dusk",
                      {"period": "dusk"})
        upsert_entity(tx, "time-anchor", "time-westus-pre-dawn",
                      {"period": "pre-dawn"})

        # Western US location (broad)
        upsert_entity(tx, "location", "loc-western-us",
                      {"place-name": "Western United States"})

        # Each incident
        for slug, name, desc, witnesses, period in incidents:
            inc_ident = f"inc-westus-{slug}"
            upsert_entity(tx, "incident", inc_ident,
                          {"name": name, "description": desc})
            time_ident = "time-westus-dusk" if period == "dusk" else "time-westus-pre-dawn"
            # incident-event with witnesses
            match_parts = [
                f'$inc isa incident, has identifier "{inc_ident}"',
                f'$t isa time-anchor, has identifier "{time_ident}"',
                f'$loc isa location, has identifier "loc-western-us"',
                f'$doc isa document, has identifier "{doc_ident}"',
            ]
            roles_dict: dict[str, str] = {
                "incident": "$inc",
                "anchor-time": "$t",
                "anchor-location": "$loc",
                "originating-document": "$doc",
            }
            # Build role-pairs explicitly because we have multiple witness roles
            for i, w in enumerate(witnesses, start=1):
                match_parts.append(f'$w{i} isa person, has identifier "person-{w.lower()}"')

            role_pairs = ", ".join(f"{r}: {v}" for r, v in roles_dict.items())
            for i in range(1, len(witnesses) + 1):
                role_pairs += f", witness: $w{i}"
            tx.query(
                f'match {"; ".join(match_parts)}; '
                f'insert $ie isa incident-event, links ({role_pairs});'
            ).resolve()

        # Temporal-sequence: Dark Kite → Transparent Kite (~30 min later)
        tx.query(
            'match '
            '$src isa incident, has identifier "inc-westus-dark-kite"; '
            '$tgt isa incident, has identifier "inc-westus-transparent-kite"; '
            'insert (source-incident: $src, target-incident: $tgt) isa incident-sequence, '
            'has sequence-kind "temporal-sequence";'
        ).resolve()

        tx.commit()
    print("  Western US Event: 4 incidents, USPER1–7 participants, 1 sequence link inserted.")


# ── Stage 3c: D28 manifest disagreement ────────────────────────────────────
def ingest_d28_disagreement(d) -> None:
    """The filename/manifest says 'East China Sea'; the body says Iraq.
    Surface as a manifest-disagreement relation with two claim entities.
    """
    # Find D28 (it's UFO-USA folder 045-DOW-UAP-D28...)
    target = None
    with d.transaction(DB, TransactionType.READ) as tx:
        rows = tx.query(
            'match $doc isa document, has identifier $i, has filename $f; '
            f'$f contains "dow-uap-d28"; select $i;'
        ).resolve()
        for r in rows.as_concept_rows():
            target = r.get("i").as_attribute().get_value()
            break
    if not target:
        print("  D28 not found")
        return

    with d.transaction(DB, TransactionType.WRITE) as tx:
        # Find first page of D28 to attach claim provenance
        rows = tx.query(
            f'match $d isa document, has identifier "{target}"; '
            f'(document: $d, page: $p) isa has-page; '
            f'$p has page-number 1, has identifier $pi; '
            f'select $pi;'
        ).resolve()
        page_ident = None
        for r in rows.as_concept_rows():
            page_ident = r.get("pi").as_attribute().get_value()
            break
        if not page_ident:
            print(f"  D28 page 1 not found, skipping disagreement claim provenance")
            return

        # Two claim entities (manifest claim, body claim)
        for cident, ctext, kind, method in [
            (f"claim-{target}-manifest-loc", "location:East China Sea (per war.gov filename and uap-csv.csv)", "metadata", "manual"),
            (f"claim-{target}-body-loc", "location:Iraq (AYN AL ASAD AIRBASE / OKAS / MGRS 38SKC63 — extracted from PDF body)", "factual", "claude-vision"),
        ]:
            upsert_entity(tx, "claim", cident,
                          {"text-content": ctext, "kind": kind, "extraction-method": method})
            tx.query(
                f'match $c isa claim, has identifier "{cident}"; '
                f'$p isa page, has identifier "{page_ident}"; '
                f'$d isa document, has identifier "{target}"; '
                f'insert $cp isa claim-provenance, links (claim: $c, page: $p, document: $d);'
            ).resolve()

        # The disagreement relation
        tx.query(
            f'match $d isa document, has identifier "{target}"; '
            f'$mc isa claim, has identifier "claim-{target}-manifest-loc"; '
            f'$bc isa claim, has identifier "claim-{target}-body-loc"; '
            f'insert $md isa manifest-disagreement, '
            f'links (document-of: $d, manifest-claim: $mc, body-claim: $bc), '
            f'has disagreement-field "location";'
        ).resolve()

        tx.commit()
    print(f"  D28 ({target}) manifest-disagreement encoded.")


# ── Stage 3d: Visual-artifact stub claims ──────────────────────────────────
def ingest_visual_stubs(d) -> None:
    """For every document with shape=visual-artifact, add one claim with
    kind=visual_artifact noting the document is image-only and needs vision-
    LLM description (deferred). The composite-sketch gets a one-shot
    description from our PDF read in entry 04.
    """
    with d.transaction(DB, TransactionType.READ) as tx:
        rows = tx.query(
            'match $doc isa document, has shape "visual-artifact", has identifier $i, has name $n; '
            'select $i, $n;'
        ).resolve()
        targets = [(r.get("i").as_attribute().get_value(),
                    r.get("n").as_attribute().get_value())
                   for r in rows.as_concept_rows()]

    inserted = 0
    with d.transaction(DB, TransactionType.WRITE) as tx:
        for ident, name in targets:
            cident = f"claim-{ident}-visual-stub"
            # Enriched description for the composite sketch (entry 04 native read)
            if "composite" in name.lower() or "sketch" in name.lower():
                desc = ("Pure-image document. Digital photo-composite/render: a "
                        "saucer-shaped craft with a brilliant white halo above a "
                        "grassy field with tree line, daylight scene. No text on "
                        "page. Source: native Claude vision read of "
                        "2024-04-30-composite-sketch.pdf.")
            else:
                desc = (f"Pure-image document ({name}). Vision-LLM description "
                        f"deferred; OCR pipeline cannot extract textual claims.")
            upsert_entity(tx, "claim", cident, {
                "kind": "visual_artifact",
                "extraction-method": "claude-vision" if "composite" in name.lower() else "deferred",
                "depicted-subject": desc,
                "text-content": desc,
            })
            # Provenance: link to document only (no page for image-only docs)
            tx.query(
                f'match $c isa claim, has identifier "{cident}"; '
                f'$d isa document, has identifier "{ident}"; '
                f'insert $cp isa claim-provenance, links (claim: $c, document: $d);'
            ).resolve()
            inserted += 1
        tx.commit()
    print(f"  Visual-artifact stubs: {inserted} claims inserted.")


# ── Main ───────────────────────────────────────────────────────────────────
def main() -> None:
    with driver() as d:
        # 3a) MISREPs
        misreps = find_misreps(d, target_shapes=("mission-report",))
        print(f"\nStage 3a: ingesting {len(misreps)} MISREPs ...")
        totals = {"mission": 0, "incident": 0, "reaction": 0, "operation": 0, "units": 0}
        for idx, ident, doc_dir in misreps:
            try:
                counts = ingest_misrep(d, idx, ident, doc_dir)
                for k, v in counts.items():
                    totals[k] = totals.get(k, 0) + v
            except Exception as e:
                print(f"  {ident}: failed: {str(e)[:200]}")
        print(f"  Totals: {totals}")

        # 3b) Western US slides
        print("\nStage 3b: Western US Event slides")
        ingest_western_us_slides(d)

        # 3c) D28 manifest disagreement
        print("\nStage 3c: D28 manifest-vs-body disagreement")
        ingest_d28_disagreement(d)

        # 3d) Visual-artifact stubs
        print("\nStage 3d: visual-artifact stub claims")
        ingest_visual_stubs(d)

        print("\nDone.")


if __name__ == "__main__":
    main()
