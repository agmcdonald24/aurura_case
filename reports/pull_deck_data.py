#!/usr/bin/env python
"""
Run every query in reports/queries/ against the case-study database and write one CSV
per query into reports/data/, plus package.json with the pull time and row counts.

Usage, from the repo root with the venv active:

    python reports/pull_deck_data.py

The SQL is the source of every number on a slide. This script only runs it and saves
the grids; build_charts.py and build_deck.py read the CSVs and never touch the database,
so the deck can be rebuilt anywhere the repo is checked out.

Connection defaults match the case-study Postgres instance (127.0.0.1:5433, case_study).
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

HERE = Path(__file__).resolve().parent
QUERIES = HERE / "queries"
DATA = HERE / "data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5433)
    parser.add_argument("--dbname", default="case_study")
    parser.add_argument("--user", default="andrew")
    parser.add_argument("--password", default="")
    parser.add_argument("--only", help="run only the query whose filename starts with this, e.g. 08")
    return parser.parse_args()


def run_query(cur, sql_path: Path, csv_path: Path) -> tuple[int, float]:
    """Execute one query file and write its grid as CSV. Returns (rows, seconds)."""
    start = time.perf_counter()
    cur.execute(sql_path.read_text())
    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    return len(rows), time.perf_counter() - start


def main() -> int:
    args = parse_args()
    DATA.mkdir(exist_ok=True)

    sql_files = sorted(QUERIES.glob("*.sql"))
    if args.only:
        sql_files = [p for p in sql_files if p.name.startswith(args.only)]
    if not sql_files:
        print("no queries matched", file=sys.stderr)
        return 1

    conn = psycopg2.connect(
        host=args.host, port=args.port, dbname=args.dbname,
        user=args.user, password=args.password,
    )
    package_path = DATA / "package.json"
    package = json.loads(package_path.read_text()) if package_path.exists() else {"queries": {}}
    package["pulled_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="minutes")
    package["database"] = f"{args.host}:{args.port}/{args.dbname}"

    try:
        with conn.cursor() as cur:
            for sql_path in sql_files:
                csv_path = DATA / (sql_path.stem + ".csv")
                rows, secs = run_query(cur, sql_path, csv_path)
                package["queries"][sql_path.stem] = {"rows": rows, "seconds": round(secs, 1)}
                print(f"  {sql_path.name:<40} {rows:>6} rows  {secs:6.1f}s")
    finally:
        conn.close()

    package_path.write_text(json.dumps(package, indent=2) + "\n")
    print(f"\nwrote {len(sql_files)} CSVs to {DATA.relative_to(HERE.parent)}/ and package.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
