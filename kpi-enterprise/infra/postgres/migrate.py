#!/usr/bin/env python3
"""Apply Postgres migrations in order.

Usage:
    DATABASE_URL=postgresql://kpi:kpi_dev@localhost:5432/kpi python migrate.py
    python migrate.py --dry-run

Each file under `migrations/` is executed inside a single transaction.
A `kpi_schema_migrations` ledger table tracks which files have been applied.

The migration runner is dependency-light on purpose: stdlib + psycopg
(if installed) or psql shell-out as fallback.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIGRATIONS_DIR = ROOT / "migrations"
LEDGER_DDL = """
CREATE SCHEMA IF NOT EXISTS kpi;
CREATE TABLE IF NOT EXISTS kpi.kpi_schema_migrations (
  filename     text PRIMARY KEY,
  applied_at   timestamptz NOT NULL DEFAULT now(),
  sha256       text
);
"""


def _files() -> list[Path]:
    return sorted(p for p in MIGRATIONS_DIR.glob("*.sql"))


def _applied_with_psycopg(dsn: str) -> set[str]:
    import psycopg  # type: ignore[import-not-found]

    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(LEDGER_DDL)
        rows = conn.execute("SELECT filename FROM kpi.kpi_schema_migrations").fetchall()
    return {r[0] for r in rows}


def _apply_with_psycopg(dsn: str, file: Path) -> None:
    import psycopg  # type: ignore[import-not-found]

    sql = file.read_text(encoding="utf-8")
    with psycopg.connect(dsn) as conn:
        with conn.transaction():
            conn.execute(sql)
            conn.execute(
                "INSERT INTO kpi.kpi_schema_migrations(filename) VALUES (%s)",
                (file.name,),
            )


def _apply_with_psql(dsn: str, file: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY] would apply {file.name} via psql")
        return
    cmd = ["psql", dsn, "-v", "ON_ERROR_STOP=1", "-f", str(file)]
    subprocess.run(cmd, check=True)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsn", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv[1:])

    if not args.dsn and not args.dry_run:
        print("DATABASE_URL not set. Pass --dsn or --dry-run.", file=sys.stderr)
        return 2

    files = _files()
    if args.dry_run:
        print("Migrations on disk:")
        for f in files:
            print(f"  - {f.name}  ({f.stat().st_size} B)")
        return 0

    try:
        applied = _applied_with_psycopg(args.dsn)
        engine = "psycopg"
    except ImportError:
        applied = set()
        engine = "psql-shell"

    pending = [f for f in files if f.name not in applied]
    if not pending:
        print(f"[{engine}] no pending migrations.")
        return 0

    for f in pending:
        print(f"[{engine}] applying {f.name} ...")
        if engine == "psycopg":
            _apply_with_psycopg(args.dsn, f)
        else:
            _apply_with_psql(args.dsn, f, args.dry_run)

    print(f"[{engine}] applied {len(pending)} migration(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
