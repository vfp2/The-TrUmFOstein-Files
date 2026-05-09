#!/usr/bin/env python3
"""Stage 4 — replace placeholder visual-artifact claims with real Claude-vision
descriptions, and reclassify the four documents misclassified as
visual-artifact that are actually witness-statement text.

Inputs are hardcoded from a Claude vision pass over each PDF / PNG. The
descriptions are intentionally specific (timestamps, scale, what's at the
crosshair) so the substrate can answer questions like "show all sensor
frames where the UAP appears as a paired signature at zoomed scale".
"""
from __future__ import annotations
from typedb.driver import TransactionType
from _typedb import driver, DB, escape_tql

# ── 33 truly-visual documents: per-doc description from native vision read ──
# Each entry is (doc_ident, description). The composite sketch (doc-157) was
# read in entry 04; the FBI Photo A and B series were read in this stage.
VISUAL_DESCRIPTIONS: dict[str, str] = {
    # FBI Photo A series — 8 PNG sensor frames, daytime IR/EO of arid terrain.
    # Simpler reticle (ticks + a "5" mark on the right). Heavy black redaction
    # blocks at the edges. Most show a small dark dot at or near the crosshair.
    "doc-107": "FBI Photo A1 (PNG sensor frame, daytime IR/EO). Open desert / smooth flat terrain at the centre, no clear UAP signature visible at this resolution. Heavy black rectangular redactions occupy most of the upper, left, and right edges of the frame. Reticle: simple crosshair with measurement ticks plus a '5' mark on the right axis. Greyscale aerial view from above.",
    "doc-108": "FBI Photo A2 (PNG sensor frame). Aerial IR/EO view of vegetation / scrub terrain with a rough texture. Small dark dot visible just left of the crosshair centre. Same redaction-block layout as A1. Greyscale.",
    "doc-109": "FBI Photo A3 (PNG sensor frame). Rocky / vegetated terrain. A small dark dot is visible right at the crosshair centre — likely the UAP signature. Same reticle and redaction layout.",
    "doc-110": "FBI Photo A4 (PNG sensor frame). Arid dune / sand terrain. Small dark dot near the crosshair. Frame is partially cropped on the left edge.",
    "doc-111": "FBI Photo A5 (PNG sensor frame). Mottled vegetation / soil terrain. Small dark dot at the crosshair centre — sensor appears locked on the UAP.",
    "doc-112": "FBI Photo A6 (PNG sensor frame). Sand / dune terrain with a dark dot near the crosshair. Reticle and redaction-block layout consistent with the rest of the A series.",
    "doc-113": "FBI Photo A7 (PNG sensor frame). Open ground; a small bright orb / bright reflective dot is visible at the crosshair (different from the dark-dot signature on most other frames in the series).",
    "doc-114": "FBI Photo A8 (PNG sensor frame). Smooth ground / dune terrain. Small dark dot near the crosshair. Consistent with the rest of the A series.",

    # FBI Photo B series — 24 PDF frames timestamped 12/31/99 18:10:00–18:21:02.
    # Two zoom scales: wide (-15..+15 ticks) and tight (-3..+3 ticks). The tight
    # frames show a paired/double dark UAP signature; the wide frames show
    # single dark dot or, in B7/B8, a clearly visible helicopter above the
    # crosshair. Time-stamps are sequential — this is sensor-video frame
    # extraction.
    "doc-115": "FBI Photo B1 (PDF sensor frame, timestamp 12/31/99 18:11:19, wide scale -15..+15). Greyscale IR/EO view; small dark UAP signature visible just above the crosshair at roughly +3 along the vertical, with mountainous horizon lower-right. Heavy black redaction blocks on three sides.",
    "doc-126": "FBI Photo B2 (timestamp 18:11:27, wide). Same scene as B1 a few seconds later; UAP dark dot has shifted slightly. Mountains visible bottom-right. Sequential frame.",
    "doc-132": "FBI Photo B3 (timestamp 18:11:34, wide). Same scene; dark UAP dot just left of the crosshair. Sequential frame in the B1–B6 wide-scale set.",
    "doc-133": "FBI Photo B4 (timestamp 18:12:16, wide). Dark dot signature near the crosshair upper-quadrant. Mountains visible far lower-right. Sequential frame.",
    "doc-134": "FBI Photo B5 (timestamp 18:12:20, wide). Similar to B4 but showing fainter dot trail or partial occlusion.",
    "doc-135": "FBI Photo B6 (timestamp 18:10:00, wide). HELICOPTER clearly visible above the crosshair (dark blob with rotor disc shape, distinct silhouette) — first frame of the sequence chronologically. This is a friendly helicopter on station.",
    "doc-136": "FBI Photo B7 (timestamp 18:10:02, wide). Helicopter still visible above-right of crosshair, two seconds after B6. Sequential pair establishing the helicopter's presence near the UAP target area.",
    "doc-137": "FBI Photo B8 (timestamp 18:10:18, wide). Helicopter no longer visible; only the dark UAP dot remains near the crosshair. Mountainous horizon clear in lower portion.",
    "doc-116": "FBI Photo B10 (timestamp 18:10:26, wide). Dark UAP dot signature at left of crosshair, ~5 ticks left of centre. Sequential frame.",
    "doc-117": "FBI Photo B11 (timestamp 18:10:50, wide). Dark UAP dot near the crosshair upper-left. Mountain horizon in lower portion. Sequential frame.",
    "doc-118": "FBI Photo B12 (timestamp 18:11:06, wide). Small dark dot signature at upper-right of crosshair. Mountains visible.",
    "doc-119": "FBI Photo B13 (timestamp 18:11:12, wide). Dark dot at upper-right of crosshair, ~5 ticks above centre. Mountains in lower portion of frame.",
    "doc-120": "FBI Photo B14 (timestamp 18:18:53, wide). Dark UAP signature directly above crosshair — sensor closely tracking. No helicopter present in this section of the sequence.",
    "doc-121": "FBI Photo B15 (timestamp 18:18:58, wide). Small dark dot upper-right of crosshair. Sequential frame.",
    "doc-122": "FBI Photo B16 (timestamp 18:19:06, wide). Dark dot just above the crosshair centre. Sequential frame in the 18:18-18:19 set.",
    "doc-123": "FBI Photo B17 (timestamp 18:19:19, ZOOMED tight scale -3..+3). PAIRED dark UAP signature visible upper-right of crosshair — TWO distinct dark spots in close formation, sensor locked at high zoom. This is the formation-pair signature also visible at B22/B23/B24.",
    "doc-124": "FBI Photo B18 (timestamp 18:19:33, tight zoom -3..+3). Dark UAP signature at right of crosshair. Single elongated/blurred shape suggesting either motion or two objects fused.",
    "doc-125": "FBI Photo B19 (timestamp 18:19:40, tight zoom). Dark UAP signature directly at the crosshair centre — sensor locked perfectly on target.",
    "doc-127": "FBI Photo B20 (timestamp 18:19:54, tight zoom). PAIRED dark signature at right of crosshair — two distinct objects in horizontal formation. Same formation-pair pattern as B17.",
    "doc-128": "FBI Photo B21 (timestamp 18:20:08, tight zoom). PAIRED dark signature in upper-right quadrant — same paired UAP formation, slightly displaced from previous frame.",
    "doc-129": "FBI Photo B22 (timestamp 18:20:22, tight zoom). PAIRED dark signature in upper-right quadrant — formation persistent across multiple frames.",
    "doc-130": "FBI Photo B23 (timestamp 18:20:41, tight zoom). PAIRED dark signature now visible in upper-quadrant of crosshair, slightly reformed.",
    "doc-131": "FBI Photo B24 (timestamp 18:20:48, tight zoom). PAIRED dark signature directly below crosshair centre, second-to-last frame in this tight-zoom set.",
    "doc-138": "FBI Photo B9 (timestamp 18:21:02, tight zoom -3..+3). PAIRED dark signature right of crosshair — final tight-zoom frame in the sequence at 18:21:02. Formation visible to the end of recording.",

    # FBI September 2023 Composite Sketch — already enriched in entry 04
    "doc-157": "Pure-image document. Digital photo-composite/render: a saucer-shaped craft with a brilliant white halo above a grassy field with tree line, daylight scene. No text on page. Source: native Claude vision read of 2024-04-30-composite-sketch.pdf. This is the FBI September 2023 sighting witness recreation, depicting the cigar/linear/saucer-shaped object described in Serial 3/4/5 witness statements.",
}

# ── 4 misclassified documents: actually witness-statement text, not visual ──
# For each, we change shape to 'witness-statement' and add structured witness
# claims extracted from the text.
WITNESS_STATEMENTS: dict[str, dict] = {
    "doc-156": {
        # USPER Statement — 3-page senior US intelligence official narrative
        "old_shape": "visual-artifact",
        "new_shape": "witness-statement",
        "claims": [
            ("primary witness: senior US intelligence official, naked-eye observation aided by helicopter spotlight, NVG, and FLIR; multi-hour mission 2025 (date redacted), helicopter call-sign CALL SIGN 1, accompanied by a second senior US intelligence official, two STATE PARTNER ORGANIZATION pilots", "witness"),
            ("location: mountain range west of [SITE CODE NAME], approximately 4 miles east of SITE CODE NAME; helicopter operated from OPERATIONS CENTER", "factual"),
            ("at 2202 hours: LP/OP using FLIR spotted a 'super-hot' orb hovering at ground level, then heading east then south at high speed, then breaking into TWO objects", "witness"),
            ("at 2218 hours: pilots (NVG) and witness (naked eye) spotted a swarm of lights too many to count moving in all directions, generally west of [redacted] heading south", "witness"),
            ("at 2227 hours: two large oval-shaped orange orbs with white/yellow centers appeared in close proximity to CALL SIGN 1, west and above the rotor disc; a third orb flared up below them, then another, until 4-5 orbs were visible in vertical stacking; flared down in reverse order", "witness"),
            ("at 2228 hours: 4-5 similar orbs flared up in horizontal formation above MILITARY AIRCRAFT to the west; flared down sequentially after 10-15 seconds", "witness"),
            ("at 2233 hours: similar orb formation observed to the east toward NEARBY TOWN NAME; horizontal flare-up then flare-down", "witness"),
            ("at 2241 hours: single orb flared up west of SITE CODE NAME over the mountain", "witness"),
            ("at 2249 hours: swarm of lights including three orbs in TRIANGLE FORMATION, west of [redacted]", "witness"),
            ("witness comments: orbs appeared to break off from CALL SIGN 1 and pursue the MILITARY AIRCRAFT; pilots indicated they were recording but many sightings were above the helicopter outside the FLIR camera angle", "factual"),
            ("classification: SECRET//NOFORN (struck through, declassified for release)", "procedural"),
        ],
    },
    "doc-158": {
        # FBI September 2023 Sighting - Serial 3 — FD-302 form witness interview
        "old_shape": "visual-artifact",
        "new_shape": "witness-statement",
        "claims": [
            ("FD-302 (Rev. 5-8-10) FBI witness interview form, Date of entry 10/[redacted]/2023, Investigation 09/[redacted]/2023 in United States in person", "metadata"),
            ("witness account: cigar-shaped object with extremely bright light to the southwest, approximately 500 to 3000 feet above the nearest tree line", "witness"),
            ("witness account: object was almost hovering, slowly moving east to west; light was intense diamond-white with a ring around it on the eastern end of the object", "witness"),
            ("witness account: object was 'metallic bronze in color' and was the length of two or three Blackhawk helicopters lined up nose to tail", "witness"),
            ("witness account: object width approximately the width of one and a half Blackhawks; object was completely silent", "witness"),
            ("witness account: watched the object for five to ten seconds, then it just disappeared; sky was clear with no clouds; object did not leave any contrails", "witness"),
            ("witness account: no interference observed with vehicle's engine while object was visible; only one object observed; co-worker passenger in second vehicle also reported seeing the object", "witness"),
            ("witness account: would not have reported the object if seen alone; some co-workers subsequently made fun of her for reporting", "witness"),
            ("witness context: had seen most of US military aircraft and drones during fifteen years working at [redacted]; never seen anything like the object observed", "factual"),
        ],
    },
    "doc-159": {
        # Serial 4 — second witness, vehicle 2
        "old_shape": "visual-artifact",
        "new_shape": "witness-statement",
        "claims": [
            ("FD-302 FBI witness interview form, separate witness from Serial 3, FaceTime video interview", "metadata"),
            ("witness account: at around 9:00 am, driving east to test site to acquire data for LiDAR testing; witness 1 + 2 in F150, witness 3 driving GMC AT4, witness 4 driving sprinter van", "witness"),
            ("witness account: vehicles drove through a couple of gates; saw a bright light over the horizon; light was stationary in the air, then started moving to the right and then disappeared", "witness"),
            ("witness account: light was bright white, visible for ten seconds before it disappeared; light stayed the same size throughout the incident; thought light was ten to twenty miles away", "witness"),
            ("witness account: pointed the light out to a colleague but they looked in the wrong direction; second witness was tall and had seat leaned back, indifferent to the light until reaching first test site where two other passengers said they saw it too", "witness"),
            ("witness speculation: thought the light might have been a meteor coming straight toward them and burning up in the atmosphere", "speculation"),
        ],
    },
    "doc-160": {
        # Serial 5 — third witness, similar to Serial 3 but different observer
        "old_shape": "visual-artifact",
        "new_shape": "witness-statement",
        "claims": [
            ("FD-302 FBI witness interview form, separate witness from Serial 3 and Serial 4, FaceTime video interview", "metadata"),
            ("witness account: at the gate that was giving witness 1 trouble, at about three quarters of the windshield up, saw a linear object with a super bright light on the east side", "witness"),
            ("witness account: light was bright white and bright enough to see bands within the light; object was 'metallic / gray in color', no wings or exhaust", "witness"),
            ("witness account: object was smaller than a 737, one to two Blackhawk helicopters in length, definitely bigger than a drone", "witness"),
            ("witness account: object was approximately 5000 feet above ground level, moved east to west parallel to the ground", "witness"),
            ("witness account: object was visible for five to ten seconds, then the light went out and the object vanished; sky was clear and witness couldn't find the object again", "witness"),
            ("witness account: object stayed the same size and same light intensity during observation; no interference with vehicles noted", "witness"),
            ("witness aftermath: that night a storm came through and TV went out in hotel room; witness was 'still freaked out' and went downstairs to check other TVs; had weird dreams and trouble sleeping for first two nights after sighting", "witness"),
        ],
    },
}


def main() -> None:
    with driver() as d:
        # ── A) Update the 33 truly-visual claims with real descriptions ────
        with d.transaction(DB, TransactionType.WRITE) as tx:
            updated = 0
            for doc_ident, desc in VISUAL_DESCRIPTIONS.items():
                cident = f"claim-{doc_ident}-visual-stub"
                # Remove the placeholder claim entirely (delete it), then re-create with rich content.
                tx.query(
                    f'match $c isa claim, has identifier "{cident}"; '
                    f'delete $c;'
                ).resolve()
                # Re-insert
                tx.query(
                    f'insert $c isa claim, '
                    f'has identifier "{cident}", '
                    f'has kind "visual_artifact", '
                    f'has extraction-method "claude-vision", '
                    f'has depicted-subject "{escape_tql(desc[:1500])}", '
                    f'has text-content "{escape_tql(desc[:1500])}";'
                ).resolve()
                # Re-link claim-provenance
                tx.query(
                    f'match $c isa claim, has identifier "{cident}"; '
                    f'$d isa document, has identifier "{doc_ident}"; '
                    f'insert $cp isa claim-provenance, links (claim: $c, document: $d);'
                ).resolve()
                updated += 1
            tx.commit()
        print(f"Updated {updated} visual-artifact claims with real Claude-vision descriptions.")

        # ── B) Reclassify the 4 misclassified documents to witness-statement ─
        with d.transaction(DB, TransactionType.WRITE) as tx:
            for doc_ident, info in WITNESS_STATEMENTS.items():
                # Delete the old visual-artifact stub claim and its provenance
                stub_ident = f"claim-{doc_ident}-visual-stub"
                tx.query(
                    f'match $c isa claim, has identifier "{stub_ident}"; '
                    f'delete $c;'
                ).resolve()

                # Update document.shape: delete old, insert new
                tx.query(
                    f'match $d isa document, has identifier "{doc_ident}", has shape $s; '
                    f'delete has $s of $d;'
                ).resolve()
                tx.query(
                    f'match $d isa document, has identifier "{doc_ident}"; '
                    f'insert $d has shape "{info["new_shape"]}";'
                ).resolve()

                # Add structured witness claims
                for i, (text, kind) in enumerate(info["claims"], start=1):
                    cident = f"claim-{doc_ident}-witness-{i:03d}"
                    tx.query(
                        f'insert $c isa claim, '
                        f'has identifier "{cident}", '
                        f'has kind "{kind}", '
                        f'has extraction-method "claude-vision", '
                        f'has text-content "{escape_tql(text[:1500])}";'
                    ).resolve()
                    tx.query(
                        f'match $c isa claim, has identifier "{cident}"; '
                        f'$d isa document, has identifier "{doc_ident}"; '
                        f'insert $cp isa claim-provenance, links (claim: $c, document: $d);'
                    ).resolve()
            tx.commit()
        n_wit = len(WITNESS_STATEMENTS)
        n_claims = sum(len(info["claims"]) for info in WITNESS_STATEMENTS.values())
        print(f"Reclassified {n_wit} documents to witness-statement; "
              f"added {n_claims} structured witness claims.")


if __name__ == "__main__":
    main()
