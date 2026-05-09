#!/usr/bin/env python3
"""Stage 1 — manifest ingest.

Sources:
  - /home/soliax/dev/vfp2/ufouap/data/records.json   (pursue-ufo-files manifest)
  - /home/soliax/dev/vfp2/ufouap/data/download-failures.json
  - /home/soliax/dev/vfp2/ufouap/pdfs/                (locally downloaded PDFs)
  - /home/soliax/Documents/github/vfp2/UFO-USA/converted/  (OCR'd Markdown)

Produces: one `document` entity per record, with shape detection, agency tag,
and acquisition-status flag. Idempotent — re-running deletes and re-inserts.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from _typedb import write_tx, escape_tql

PURSUE_DATA = Path("/home/soliax/dev/vfp2/ufouap/data")
PDF_DIR     = Path("/home/soliax/dev/vfp2/ufouap/pdfs")
OCR_DIR     = Path("/home/soliax/Documents/github/vfp2/UFO-USA/converted")

# TypeDB 'datetime' (not datetime-tz) — drop the zone suffix for the literal.
NOW = datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")

# ── shape detection ────────────────────────────────────────────────────────
SHAPE_RULES = [
    # (regex on lowercased filename or title, shape)
    (re.compile(r"_serial_\d|_section_\d"),                    "fbi-hq-section"),
    (re.compile(r"^65_hs1.*sub_a"),                            "fbi-hq-section"),
    (re.compile(r"^fbi[_-]photo|composite[_-]sketch|sighting"),"visual-artifact"),
    (re.compile(r"^usper-statement"),                          "visual-artifact"),
    (re.compile(r"^western_us_event"),                         "multi-incident-deck"),
    (re.compile(r"^dow-uap-d.*mission[_-]report"),             "mission-report"),
    (re.compile(r"^dow-uap-d.*range[_-]fouler"),               "range-fouler-debrief"),
    (re.compile(r"^dow-uap-d.*range[_-]fouler[_-]reporting[_-]form"), "range-fouler-debrief"),
    (re.compile(r"^dow-uap-d.*department[_-]of[_-]the[_-]air[_-]force"), "mission-report"),
    (re.compile(r"^dow-uap-d.*launch[_-]summary"),             "mission-report"),
    (re.compile(r"^dow-uap-d.*email[_-]correspond"),           "email-correspondence"),
    (re.compile(r"^dow-uap-d.*unresolved"),                    "mission-report"),
    (re.compile(r"^nasa-uap-d.*transcript|crew[_-]debrief"),   "crew-transcript"),
    (re.compile(r"^dos-uap-d|cable-\d|^\d{3}uap\d"),           "state-cable"),
    (re.compile(r"^(18_|38_|59_|255_|331_|341_|342_)"),        "nara-historical"),
]

def detect_shape(title: str, filename: str) -> str:
    blob = f"{filename} {title}".lower()
    for rx, shape in SHAPE_RULES:
        if rx.search(blob):
            return shape
    return "unknown"

# ── filesystem reconciliation ─────────────────────────────────────────────
def find_local_pdf(filename: str) -> Path | None:
    """Match a record's link-derived filename to a downloaded PDF."""
    if not filename:
        return None
    candidates = [
        PDF_DIR / filename,
        PDF_DIR / filename.lower(),
        PDF_DIR / filename.replace(" ", "_"),
    ]
    for c in candidates:
        if c.exists():
            return c
    # last-resort: tolerant case-insensitive match
    target = filename.lower()
    for p in PDF_DIR.iterdir():
        if p.name.lower() == target:
            return p
    return None

def find_ocr_dir(record_idx: int, title: str) -> Path | None:
    """UFO-USA folders are numbered NNN-... matching dataset_row."""
    needle = f"{record_idx:03d}-"
    for p in OCR_DIR.iterdir():
        if p.is_dir() and p.name.startswith(needle):
            return p
    return None

# ── main ───────────────────────────────────────────────────────────────────
def main() -> None:
    records = json.loads((PURSUE_DATA / "records.json").read_text())
    failures = json.loads((PURSUE_DATA / "download-failures.json").read_text())
    failed_titles = {f["title"] for f in failures}

    # delete any pre-existing documents (idempotent re-run)
    with write_tx() as tx:
        tx.query("match $d isa document; delete $d;").resolve()

    inserted = 0
    shape_counts: dict[str, int] = {}
    with write_tx() as tx:
        for idx, rec in enumerate(records, start=1):
            title       = rec.get("title") or ""
            agency      = rec.get("agency") or ""
            description = rec.get("description") or ""
            link        = rec.get("pdf_link") or rec.get("dvids_id") or ""
            inc_date    = rec.get("incident_date") or ""
            # filename portion of the URL
            fname = link.rsplit("/", 1)[-1] if link else ""
            shape = detect_shape(title, fname)

            # acquisition status
            local_pdf = find_local_pdf(fname) if fname.endswith(".pdf") else None
            if local_pdf:
                acq = "downloaded"
                size = local_pdf.stat().st_size
            elif title in failed_titles:
                acq = "download_failed"
                size = 0
            elif rec.get("type") == "VID":
                acq = "video_only"
                size = 0
            else:
                acq = "not_attempted"
                size = 0

            ocr_dir = find_ocr_dir(idx, title)
            total_pages = 0
            if ocr_dir:
                total_pages = len(list(ocr_dir.glob("page-*.md")))

            # build TypeQL insert
            ident = f"doc-{idx:03d}"
            parts = [
                f'$d isa document',
                f'has identifier "{ident}"',
                f'has name "{escape_tql(title)}"',
                f'has shape "{shape}"',
                f'has acquisition-status "{acq}"',
                f'has first-seen-at {NOW}',
                f'has last-seen-at {NOW}',
                f'has removed-from-source false',
            ]
            if fname:        parts.append(f'has filename "{escape_tql(fname)}"')
            if link:         parts.append(f'has url "{escape_tql(link)}"')
            if description:  parts.append(f'has description "{escape_tql(description[:5000])}"')
            if total_pages:  parts.append(f'has total-pages {total_pages}')
            if size:         parts.append(f'has file-size {size}')

            insert = "insert " + ", ".join(parts) + ";"
            tx.query(insert).resolve()
            inserted += 1
            shape_counts[shape] = shape_counts.get(shape, 0) + 1

    print(f"inserted {inserted} document entities")
    for shape, n in sorted(shape_counts.items(), key=lambda x: -x[1]):
        print(f"  {n:4d}  {shape}")

if __name__ == "__main__":
    main()
