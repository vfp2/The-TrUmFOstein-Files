#!/usr/bin/env python3
"""Load the TrUmFOstein schema into a fresh `trumfostein` database on a
local TypeDB 3.x server.

Run:
  python3 substrate/ingest/00_load_schema.py
Idempotent: drops the database if it exists and re-creates from scratch.
"""
from pathlib import Path
from typedb.driver import TypeDB, Credentials, DriverOptions, TransactionType

REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "substrate" / "schema" / "schema.tql"
DB = "trumfostein"

def main() -> None:
    schema = SCHEMA.read_text()
    with TypeDB.driver("localhost:1729", Credentials("admin", "password"), DriverOptions(is_tls_enabled=False)) as driver:
        if driver.databases.contains(DB):
            print(f"dropping existing {DB}")
            driver.databases.get(DB).delete()
        driver.databases.create(DB)
        print(f"created {DB}")
        with driver.transaction(DB, TransactionType.SCHEMA) as tx:
            tx.query(schema).resolve()
            tx.commit()
        print(f"schema loaded ({len(schema):,} chars)")

if __name__ == "__main__":
    main()
