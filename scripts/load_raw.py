#!/usr/bin/env python
"""
Load the Kaggle "US Construction Zones (Dec 2021)" CSV into raw.us_constructions.

Usage, from the repo root with the venv active:

    python scripts/load_raw.py --csv "/path/to/US_Constructions_Dec21.csv"

Connection defaults match the case-study Postgres instance (127.0.0.1:5433, case_study).
Override with --host / --port / --dbname / --user / --password if needed.

Design choices
--------------
* raw is a faithful copy of the source: typed columns, snake_case names, nothing else.
  No filtering, dedup, or derived fields -- that happens in dbt staging, where every
  transformation is visible, documented, and testable.
* Typed (not text) on purpose: a value that doesn't parse fails the COPY loudly, which
  surfaces data-quality problems at ingestion rather than hiding them downstream.
* COPY ... FROM STDIN streams the file through the client, so the database server never
  needs filesystem access to the CSV. ~6.2M rows / 2.7 GB -- expect a few minutes.
* Indexes go on after the load; loading into an indexed table is much slower.
* The primary key on id doubles as a uniqueness check on the source. If it fails, the
  data stays loaded and the duplicate count is reported instead of aborting the run.
"""

import argparse
import sys
import time

import psycopg2
from psycopg2 import errors

SCHEMA = "raw"
TABLE = "us_constructions"
FQ_TABLE = f"{SCHEMA}.{TABLE}"

CREATE_TABLE = f"""
create schema if not exists {SCHEMA};

drop table if exists {FQ_TABLE};
create table {FQ_TABLE} (
    id                      text,
    severity                smallint,
    start_time              timestamp,          -- local time; see timezone column
    end_time                timestamp,
    start_lat               double precision,
    start_lng               double precision,
    end_lat                 double precision,
    end_lng                 double precision,
    distance_mi             double precision,
    description             text,
    street_number           double precision,   -- source stores it as a float
    street                  text,
    side                    text,
    city                    text,
    county                  text,
    state                   text,
    zipcode                 text,
    country                 text,
    timezone                text,
    airport_code            text,
    weather_timestamp       timestamp,
    temperature_f           double precision,
    wind_chill_f            double precision,
    humidity_pct            double precision,
    pressure_in             double precision,
    visibility_mi           double precision,
    wind_direction          text,
    wind_speed_mph          double precision,
    precipitation_in        double precision,
    weather_condition       text,
    amenity                 boolean,
    bump                    boolean,
    crossing                boolean,
    give_way                boolean,
    junction                boolean,
    no_exit                 boolean,
    railway                 boolean,
    roundabout              boolean,
    station                 boolean,
    stop                    boolean,
    traffic_calming         boolean,
    traffic_signal          boolean,
    turning_loop            boolean,
    sunrise_sunset          text,
    civil_twilight          text,
    nautical_twilight       text,
    astronomical_twilight   text
);
"""

COPY_SQL = f"copy {FQ_TABLE} from stdin with (format csv, header true)"

ADD_PRIMARY_KEY = f"alter table {FQ_TABLE} add primary key (id)"

POST_LOAD = [
    ("create index (state, city)", f"create index on {FQ_TABLE} (state, city)"),
    ("create index (start_time)", f"create index on {FQ_TABLE} (start_time)"),
    ("analyze", f"analyze {FQ_TABLE}"),
]

SANITY_CHECK = f"""
select
    count(*)                 as rows_loaded,
    min(start_time)          as first_start,
    max(start_time)          as last_start,
    count(distinct state)    as states,
    count(distinct city)     as cities
from {FQ_TABLE}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--csv", required=True, help="path to US_Constructions_Dec21.csv")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5433)
    parser.add_argument("--dbname", default="case_study")
    parser.add_argument("--user", default="andrew")
    parser.add_argument("--password", default="", help="empty is fine with local trust auth")
    return parser.parse_args()


def timed(label: str, fn) -> None:
    """Run fn() and print how long it took, so load timings end up in the process log."""
    start = time.perf_counter()
    fn()
    print(f"  {label:<32} {time.perf_counter() - start:7.1f}s")


def copy_csv(cur, csv_path: str) -> None:
    with open(csv_path, "rb") as f:
        cur.copy_expert(COPY_SQL, f)


def add_primary_key(conn, cur) -> None:
    """Add the PK; if ids aren't unique, keep the data and report instead of failing."""
    try:
        timed("add primary key (id)", lambda: cur.execute(ADD_PRIMARY_KEY))
        conn.commit()
    except errors.UniqueViolation:
        conn.rollback()
        cur.execute(f"select count(*) - count(distinct id) from {FQ_TABLE}")
        dupes = cur.fetchone()[0]
        print(f"  WARNING: id is not unique ({dupes} duplicate rows). "
              f"No primary key added; handle dedup in staging.")


def main() -> int:
    args = parse_args()
    print(f"Loading {args.csv} -> {args.dbname}.{FQ_TABLE} on {args.host}:{args.port}")

    conn = psycopg2.connect(
        host=args.host, port=args.port, dbname=args.dbname,
        user=args.user, password=args.password,
    )
    try:
        with conn.cursor() as cur:
            timed("create schema + table", lambda: cur.execute(CREATE_TABLE))
            conn.commit()

            timed("copy csv -> table", lambda: copy_csv(cur, args.csv))
            conn.commit()

            add_primary_key(conn, cur)

            for label, sql in POST_LOAD:
                timed(label, lambda sql=sql: cur.execute(sql))
            conn.commit()

            cur.execute(SANITY_CHECK)
            columns = [d[0] for d in cur.description]
            values = cur.fetchone()
            print("\nSanity check:")
            for col, val in zip(columns, values):
                print(f"  {col:<14} {val}")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
