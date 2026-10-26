-- scripts/load_raw.sql
-- Load the Kaggle "US Construction Zones (Dec 2021)" CSV into raw.us_constructions.
--
-- Usage, from the repo root, against the case-study Postgres instance:
--   psql -h 127.0.0.1 -p 5433 -d case_study \
--        -v csv_path="/absolute/path/to/US_Constructions_Dec21.csv" \
--        -f scripts/load_raw.sql
--
-- Design choices:
--   * raw is a faithful copy of the source: typed columns, snake_case names, nothing else.
--     No filtering, dedup, or derived fields -- that happens in dbt staging, where every
--     transformation is visible, documented, and testable.
--   * Typed (not text) on purpose: a value that doesn't parse fails the COPY loudly, which
--     surfaces data-quality problems at ingestion instead of hiding them downstream.
--   * Server-side COPY rather than \copy so the file path can be passed as a psql variable
--     (\copy doesn't interpolate variables). The server runs as the same local user, so it
--     can read the file directly. ~6.2M rows / 2.7 GB -- expect a few minutes.
--   * Indexes go on after the load; loading into an indexed table is much slower.

\set ON_ERROR_STOP on
\timing on

create schema if not exists raw;

drop table if exists raw.us_constructions;
create table raw.us_constructions (
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

copy raw.us_constructions from :'csv_path' with (format csv, header true);

-- primary key doubles as a uniqueness check on the source id
alter table raw.us_constructions add primary key (id);
create index on raw.us_constructions (state, city);
create index on raw.us_constructions (start_time);
analyze raw.us_constructions;

-- sanity check
select
    count(*)                 as rows_loaded,
    min(start_time)          as first_start,
    max(start_time)          as last_start,
    count(distinct state)    as states,
    count(distinct city)     as cities
from raw.us_constructions;
