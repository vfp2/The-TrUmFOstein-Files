"""Shared TypeDB client helpers for ingestion stages."""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
from typedb.driver import TypeDB, Credentials, DriverOptions, TransactionType

REPO = Path(__file__).resolve().parents[2]
DB = "trumfostein"
ADDR = "localhost:1729"

def driver():
    return TypeDB.driver(ADDR, Credentials("admin", "password"), DriverOptions(is_tls_enabled=False))

@contextmanager
def write_tx():
    with driver() as d:
        with d.transaction(DB, TransactionType.WRITE) as tx:
            yield tx
            tx.commit()

@contextmanager
def read_tx():
    with driver() as d:
        with d.transaction(DB, TransactionType.READ) as tx:
            yield tx

def escape_tql(s: str) -> str:
    """Escape a Python string for embedding inside a TypeQL string literal."""
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")
