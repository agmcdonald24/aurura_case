# Aurora Case Study — Environment Setup Recap

**Date:** October 23, 2026  
**Status:** PostgreSQL, GitHub clone, Python environment, and dbt installation complete. dbt project initialization and database connection are next.

## 1. Created a separate PostgreSQL instance

An existing PostgreSQL 17 server was already running on the Mac. We created a second, independent PostgreSQL instance for the case study so the existing data would not be disturbed.

| Setting | Existing instance | Case study instance |
|---|---|---|
| PostgreSQL | 17 | 17 (17.11 reported by database client) |
| Port | `5432` | `5433` |
| Data directory | `/opt/homebrew/var/postgresql@17` | `/Users/andrew/postgres-case-study` |
| Database | Existing databases | `case_study` |
| Database user | `andrew` | `andrew` |

### Commands used

Check running PostgreSQL processes:

```bash
ps aux | grep '[p]ostgres'
```

Check the original instance's port and data directory:

```bash
/opt/homebrew/opt/postgresql@17/bin/psql -d postgres -Atc "SHOW port; SHOW data_directory;"
```

Initialize the second instance:

```bash
/opt/homebrew/opt/postgresql@17/bin/initdb -D "$HOME/postgres-case-study"
```

Configure its port:

```bash
echo "port = 5433" >> "$HOME/postgres-case-study/postgresql.conf"
```

Start its PostgreSQL server:

```bash
/opt/homebrew/opt/postgresql@17/bin/pg_ctl -D "$HOME/postgres-case-study" -l "$HOME/postgres-case-study/server.log" start
```

Verify the new instance's port and directory:

```bash
/opt/homebrew/opt/postgresql@17/bin/psql -h 127.0.0.1 -p 5433 -U andrew -d postgres -Atc "SHOW port; SHOW data_directory;"
```

Create the project database:

```bash
/opt/homebrew/opt/postgresql@17/bin/createdb -h 127.0.0.1 -p 5433 -U andrew case_study
```

Set a password for `andrew` in the new instance:

```bash
/opt/homebrew/opt/postgresql@17/bin/psql -h 127.0.0.1 -p 5433 -U andrew -d case_study -c '\password andrew'
```

Inspect authentication rules:

```bash
grep -nE '^[[:space:]]*(local|host)[[:space:]]' "$HOME/postgres-case-study/pg_hba.conf"
```

**Authentication note:** The new instance is still configured with `trust` authentication for local connections. Although a password was set, PostgreSQL currently does not require it for those local connections. We decided not to change this for a temporary local case study using non-sensitive data. Do not expose the server to an untrusted network.

**Result:** A separate PostgreSQL server and `case_study` database are running on port `5433`. A database client successfully connected (PostgreSQL JDBC driver 42.7.13; SSL not used).

## 2. Cloned and connected the GitHub repository

The GitHub repository was cloned locally to:

```text
/Users/andrew/Desktop/Aurora Case Study/aurura_case
```

Remote repository:

<https://github.com/agmcdonald24/aurura_case>

Verify the configured remote:

```bash
git -C "/Users/andrew/Desktop/Aurora Case Study/aurura_case" remote -v
```

The `origin` remote pointed to the repository for both fetching and pushing. The GitHub repository's default branch is `main`.

**Important:** The PostgreSQL **data directory** is separate from the Git repository. Database storage files should not be added to source control. Git is for the project code, SQL, dbt models, configuration, and documentation.

## 3. Verified Python and PyCharm's virtual environment

The installed Python version was **3.14.6**. An existing `.venv` directory was found inside the local case study repository. PyCharm was already using it, so no new environment or manual activation was necessary.

List the repository contents:

```bash
ls -la "/Users/andrew/Desktop/Aurora Case Study/aurura_case"
```

Verify the interpreter in PyCharm's terminal:

```bash
python -c "import sys; print(sys.executable)"
```

Confirmed interpreter:

```text
/Users/andrew/Desktop/Aurora Case Study/aurura_case/.venv/bin/python
```

**Result:** Python packages for the case study can be installed inside this project's virtual environment without affecting other projects.

## 4. Created `.gitignore`

The following command was executed from the project directory:

```bash
printf ".venv/\n.DS_Store\n__pycache__/\n.env\nprofiles.yml\ntarget/\ndbt_packages/\nlogs/\n" > .gitignore
```

It excludes:

- `.venv/` — locally installed Python dependencies
- `.DS_Store` — macOS metadata
- `__pycache__/` — generated Python cache
- `.env` — local environment settings and possible secrets
- `profiles.yml` — local dbt connection settings (if placed in the repository)
- `target/` — compiled dbt artifacts
- `dbt_packages/` — installed dbt package files
- `logs/` — dbt logs

**Note:** The `>` operator overwrites `.gitignore` rather than appending; in this setup, the repository initially contained only `.git`, `.DS_Store`, and `.venv`.

## 5. Installed dbt Core and the PostgreSQL adapter

Install into the active PyCharm virtual environment:

```bash
python -m pip install "dbt-core>=1.12,<1.13" "dbt-postgres>=1.11,<1.12"
```

Versions confirmed by the installer and `dbt --version`:

| Package | Version | Purpose |
|---|---|---|
| `dbt-core` | `1.12.6` | Organize and run SQL transformation models, tests, and documentation |
| `dbt-postgres` | `1.11.0` | Connect dbt to PostgreSQL |

Check installed dbt components:

```bash
dbt --version
```

The output reported dbt Core and the Postgres plugin as installed and up to date. A notice about dbt v2 was informational; this project is currently using dbt Core v1.

## 6. Status and next steps

| Component | Status |
|---|---|
| Independent PostgreSQL instance on `5433` | Complete |
| `case_study` database | Complete |
| Database client connection | Complete |
| GitHub repository cloned and remote verified | Complete |
| Python virtual environment in PyCharm | Complete |
| `.gitignore` created | Complete |
| dbt Core and Postgres adapter installed | Complete |
| dbt project initialization | Not yet confirmed |
| dbt connection to the database | Not yet configured/tested |

The last command suggested was:

```bash
dbt init aurora_dbt --skip-profile-setup
```

**Its execution has not yet been confirmed.** It creates a new `aurora_dbt/` subfolder inside the existing repository. The plan was to organize the generated dbt files in the desired repository structure, configure the PostgreSQL connection, and run:

```bash
dbt debug
```

to confirm dbt can connect to the case study database.

### How the pieces fit together

- **PostgreSQL** stores the case study data locally.
- **Git/GitHub** versions and shares the project's SQL, dbt models, and documentation.
- **Python `.venv`** isolates local tooling and package dependencies.
- **dbt** will use the PostgreSQL adapter to transform raw database tables into analytical models and run data quality checks.

**Target dbt connection:** `localhost:5433`, database `case_study`, user `andrew`.

## 7. Connected dbt, seeded the routes, loaded the construction data

**Date:** October 23, 2026
**Status update to section 6:** `dbt init aurora_dbt` confirmed (scaffold present); `dbt debug` passed.

### profiles.yml

Created `~/.dbt/profiles.yml` — profile `aurora_dbt`, target `dev`: Postgres `127.0.0.1:5433`, database `case_study`, user `andrew`, default schema `analytics`, 4 threads. The `profile:` key in `dbt_project.yml` must match the top-level key in this file. `dbt debug` reported all checks passed.

### `sf_paths` as a dbt seed

- Copied `sf_paths.csv` to `aurora_dbt/seeds/` and declared it in `seeds/_seeds.yml` with explicit column types, descriptions, and tests (`unique` + `not_null` on `path_name`; `not_null` on `path_wkt`, `distance_mi`).
- `dbt seed` loads it to `analytics.sf_paths` (5 rows). Models reference it with `ref()`, not `source()`, because dbt owns it.
- Why a seed: five rows of static reference data that belongs in version control. The 2.7 GB construction file is not seed material — seeds are committed to git and inserted row by row.
- Gotcha: the YAML copied from chat carried list indentation; `seeds:` must sit at column 0, flush with `version:`.

### Raw load — `scripts/load_raw.py`

Python + psycopg2 (already in the venv). Run from the repo root:

```bash
python scripts/load_raw.py --csv "/Users/andrew/Desktop/Aurora Case Study/US_Constructions_Dec21.csv"
```

What it does: creates schema `raw` and `raw.us_constructions` (47 typed, snake_case columns), streams the CSV with `COPY ... FROM STDIN`, commits, then adds the primary key on `id`, indexes on `(state, city)` and `(start_time)`, and runs `ANALYZE`. Each step prints its timing.

Design choices (also in the script's header):

| Choice | Why |
|---|---|
| `raw` is a faithful copy — no filtering, dedup, or derived fields | Every transformation lives in dbt staging, where it is visible, documented, and testable |
| Typed columns, not text | A value that doesn't parse fails the COPY loudly; data-quality problems surface at ingestion |
| `COPY FROM STDIN` through the client | The database server never needs filesystem access to the CSV |
| Indexes after the load | Loading into an indexed table is much slower |
| PK on `id` doubles as a uniqueness check | If it fails, the data stays loaded and the duplicate count is reported |

**Result:** 6,170,627 rows loaded (the `wc -l` figure of 6,170,628 includes the header). Primary key on `id` went on clean — every id is unique. Start times span 2016-01-31 to 2021-12-31; end times run to exactly 2022-01-01 00:00:00, the extract cutoff.

### DataGrip and the new schema

Two things that cost time and are worth knowing:

- DataGrip does not pick up new schemas automatically. Data source → **Properties → Schemas**, refresh the list, tick `raw` and `analytics`.
- Unqualified table names resolve via `search_path`, which defaults to `public`. One-time fix so `select ... from us_constructions` works in any session:

  ```sql
  alter database case_study set search_path = raw, analytics, public;
  ```

### AI usage for this step

- **Claude:** explained seeds vs. sources and `profiles.yml` vs. `sources.yml`; wrote the seed YAML and `scripts/load_raw.py` at my request; walked through the DataGrip schema and `search_path` fixes.
- **Me:** ran every command; pushed back on the `raw` schema after the DataGrip friction. Kept it: raw / staging / marts separation is the standard layout, keeps dbt's source declaration clean, and is what a reviewer expects. Noted that `public`-only with prefixes (as in my other dbt project) works but reads worse in a graded submission.
- **Miss on Claude's side:** should have said up front that a new schema needs DataGrip's schema list refreshed and the search path set. Flagged, not repeated.

## 8. Staging — `stg_construction`

**Date:** October 25, 2026

First dbt model. Keeps the 13 columns that touch the four questions; dedups provider re-pulls
(same start, end, start coordinates and description — only the weather columns differed);
derives `duration_hours`; rolls NYC's five county-boroughs up to one `city_normalized`;
classifies `event_type` as `seasonal_closure` when the description matches
`winter|snowfall|season|blizzard` (my word list), else `construction`; and flags
`is_open_at_extract` (end = 2022-01-01) and `is_batch_start` / `is_batch_end` (timestamp
shared by 100+ rows). Materialized as a table.

**Result:** 6,170,627 raw rows → 5,887,586 events. 283,041 duplicates removed (4.6%).

**AI usage:** Claude drafted the model from my first pass (my CTE skeleton had the right
shape but a `ref()` where a `source()` belonged, `lng` columns named `lon`, and the NYC case
keyed on city instead of county). I set the seasonal-closure terms and the rule that nothing
is dropped except exact duplicates — everything else is a flag applied downstream.

**Gotcha (found by me, 2026-10-25):** the first seasonal-closure pattern matched on the bare
word `winter`, which also matches street names — "Winter St", "Winter Haven Dr" — so ordinary
roadwork on those streets was being classified as a seasonal closure. Lesson: classify on
*phrases* that describe the closure ("closed for the winter", "seasonal closure"), not on
words that can appear in an address. Pattern to be rebuilt from the actual descriptions
rather than guessed.

**Seasonal-closure pattern, rebuilt from the data (2026-10-25):** exported every description
matching the first word list (2,047 distinct descriptions, 5,437 events — tiny against 5.9M).
Three groups: street names (Winter St, Winter Haven Dr, Winter Lake Rd, Seasons Rd, Winterset
Dr, Wintersville Rd — ordinary roadwork); real closures, which use two templated phrasings,
`winter closure.` and `closed for the season`; and a landmark, "Winter Closure Gate" on CA-108
and CA-158, where construction *near* the gate was being flagged as a closure. `snowfall` and
`blizzard` on their own appear only as weather notes on ordinary roadwork ("Closed due to
roadwork. Icy patches. Snowfall.") and were dropped from the pattern. Final pattern: phrases
only, with a negative lookahead for "gate". Claude ran the categorisation on the export; I
decided the word list.

**Duration distribution (2026-10-25):** no single value dominates (top value 4.7% of events),
so `duration_hours` is mostly observed rather than defaulted. But the top values are round
templates — 96 hours (exactly four days, 4.3%), then 6, 5, 8, 10, 9 and 2 hours — and about
15% of events are sub-hour "Slow traffic ... due to roadwork" congestion observations. "Hours
of construction" therefore means hours of *reported traffic impact*, mixing short flow
observations with multi-day advisories. Q1 is to be shown as events and hours side by side.

**Staging flag sizes (2026-10-25), after the rebuilt seasonal pattern:**

| | construction | seasonal_closure |
|---|---|---|
| events | 5,886,134 | 1,452 |
| open at extract (end = 2022-01-01) | 60 | 1 |
| batch start (timestamp shared by 100+ rows) | 433,466 (7.4%) | 2 |
| batch end | 534,664 (9.1%) | 53 |
| negative duration | 0 | 0 |
| mean / median hours | 398 / 7 | 1,049 / 5 |

What this settles: right-censoring is negligible (60 rows) and needs no handling beyond the
flag; there are no negative durations; batch-stamped rows are a real share and get a
with/without sensitivity column downstream; seasonal closures are ~0.1% of hours, so the
classification is correct but not a lever. The mean/median gap (398 vs 7) means city totals
are driven by the long tail of multi-day advisories, not the typical event — Q1 shows events
and hours side by side for that reason. Seasonal closures' median of 5 hours confirms they
are re-published short advisories, not single long records; chaining re-publications into
one event is noted as the more sophisticated alternative, not done.

**Attribution note on the seasonal pattern:** the word list (`winter`, `snowfall`, `season`,
`blizzard`) was mine; Claude turned it into the regex. Neither of us anticipated street
names. The fix came from exporting the matches and reading them, not from guessing a better
pattern.

## 9. Intermediate — `int_city_month_hours`, and the first spot checks

**Date:** October 25, 2026

One model: each event's hours are allocated to the calendar months it overlaps (a two-year
project contributes ~720 hours to each of 24 months rather than 17,000 hours to its start
date). Grain is (city, state, month), 2017–2021, with `construction_hours`,
`construction_hours_excl_batch` (the sensitivity column) and `seasonal_closure_hours` kept
separately. Claude wrote it; I built and spot-checked it. Right-censoring at the extract date
and "which year does a multi-year event belong to" are both handled by this allocation.

### Spot check 1 — Q1, all cities (top 6 by hours, 2017–2021)

| city | events | hours | hours excl. batch |
|---|---|---|---|
| New York, NY | 517,673 | 107.7M | 83.1M |
| Phoenix, AZ | 351,188 | 92.2M | 82.0M |
| Miami, FL | 221,820 | 51.7M | 37.5M |
| Chicago, IL | 100,202 | 25.7M | 22.0M |
| Denver, CO | 97,355 | 24.9M | 16.2M |
| Minneapolis, MN | 52,209 | 20.5M | 12.9M |

New York leads under our definition (five boroughs rolled up). Two caveats that the Q&A will
raise and the deck should raise first: Manhattan alone would not lead, and without
batch-stamped rows it is a near tie with Phoenix (83.1M vs 82.0M). Miami is third nationally
and is not one of the ten largest cities.

**What jumped out:** Los Angeles is nowhere near the top. The second-largest city in the US
ranks 7th of the ten with 47k events; San Diego is 10th with 1.4M hours, roughly 1/75th of New
York. Both Texas and California are thin. Hypothesis, stated as such: these APIs aggregate
what state DOTs publish, and some DOTs publish far more than others, so the ranking measures
reporting intensity as much as roadwork. It cannot be separated with this data.

### Spot check 2 — the ten cities, Q1 with a concurrency figure

| city | events | hours | hours excl. batch | avg. concurrent advisories |
|---|---|---|---|---|
| New York, NY | 517,673 | 107.7M | 83.1M | 2,459 |
| Phoenix, AZ | 351,188 | 92.2M | 82.0M | 2,105 |
| Chicago, IL | 100,202 | 25.7M | 22.0M | 586 |
| Houston, TX | 73,191 | 18.2M | 15.4M | 416 |
| Philadelphia, PA | 49,474 | 11.9M | 8.3M | 271 |
| Dallas, TX | 42,197 | 9.6M | 7.8M | 219 |
| Los Angeles, CA | 47,403 | 7.8M | 6.6M | 178 |
| San Antonio, TX | 19,447 | 3.9M | 3.0M | 89 |
| Austin, TX | 13,268 | 2.6M | 2.0M | 59 |
| San Diego, CA | 15,431 | 1.4M | 1.3M | 33 |

"Average concurrent advisories" is hours ÷ (5 × 8,760) — the number of construction
advisories active at any given moment, averaged over the window. It makes 107M hours
sayable: New York averaged about 2,460 active advisories around the clock.

### Spot check 3 — Q2 by year, and the finding that reframes everything

Every one of the ten cities jumps 5–10× from 2020 to 2021 (New York 11.0M → 88.8M; Phoenix
8.3M → 80.6M; Chicago 2.5M → 20.3M; Dallas 1.0M → 8.1M). Ten cities in ten states under
different DOTs do not all have an eight-fold construction boom in the same year. This is the
data source changing, not the roads. 82% of New York's five-year total is 2021 alone, so Q1's
"past five years" is mostly "2021".

Decomposition by start year (construction events only):

| year | events | mean hrs | median hrs | % exactly 96h | % under 1h | % batch-stamped |
|---|---|---|---|---|---|---|
| 2016 | 146,900 | 515 | 6.0 | 0.2 | 0.6 | 7.5 |
| 2017 | 200,369 | 596 | 6.0 | 0.1 | 1.2 | 5.2 |
| 2018 | 307,182 | 518 | 8.0 | 14.5 | 1.8 | 10.7 |
| 2019 | 556,471 | 691 | 82.0 | 27.7 | 1.4 | 16.9 |
| 2020 | 1,593,967 | 262 | 10.3 | 3.2 | 5.9 | 21.5 |
| 2021 | 3,081,245 | 386 | 2.65 | 0.0 | 26.7 | 11.5 |

Three separate changes are stacked here:

1. **2018–2019 — a 96-hour template.** A provider publishing advisories with a default
   four-day lifespan: 14.5% of 2018 events, 27.7% of 2019 (the 2019 median of 82 hours is this
   template). Gone by 2021.
2. **September 2020 — a short-event provider.** Monthly events jump from 195k (Aug) to 349k
   (Sep) while hours barely move. By 2021, 27% of events are sub-hour "Slow traffic ... due to
   roadwork" congestion observations and the median event is 2.65 hours.
3. **March–April 2021 — the hours step.** Monthly hours double twice (31M → 62M → 101M) and
   peak at 175M in August 2021. Short events don't carry hours, so this is a source that began
   publishing many long advisories, concentrated in big metros: nationally 2021 is ~2.7× 2020
   by hours, but New York and Phoenix are 8–10×.

Monthly national totals (events, hours) are kept in `analyses/` for the Q2 chart.

**Correction to an earlier conclusion.** Right-censoring was called negligible because only
60 rows end on the extract date. But Nov–Dec 2021 events stay high (511k, 495k) while hours
fall 58% from the October peak; the seasonal decline in earlier years is ~20%. The likely
explanation is that events still open at extraction are *absent* from the file, not
truncated to the extract date — the pipeline exported closed events only. The last two to
three months of 2021 are therefore missing their long-running advisories. The Q2 trend is
readable through roughly September 2021; the tail is incomplete. Found by reading the monthly
table, after the earlier conclusion was already logged — left in place so the sequence is
honest.

**For Q2 the answer is:** reported construction hours grew steadily 2017–2020 and then
stepped up roughly an order of magnitude in 2021 in every city at once — the signature of a
reporting change, not a construction boom. Presenting the 2021 line as "construction
increased" would be wrong.

### Spot check 4 — what changed in New York specifically

| year | events | mean hrs | % under 1h | % over 30 days | ≈ events over 30 days |
|---|---|---|---|---|---|
| 2016 | 5,429 | 230 | 1.0 | 6.0 | 330 |
| 2017 | 14,835 | 237 | 0.5 | 2.9 | 430 |
| 2018 | 17,870 | 132 | 4.4 | 2.1 | 375 |
| 2019 | 18,042 | 426 | 1.6 | 6.1 | 1,100 |
| 2020 | 99,035 | 110 | 20.7 | 2.6 | 2,575 |
| 2021 | 222,852 | 371 | 41.2 | 9.6 | 21,400 |

The 2021 hours step is month-or-longer advisories: ~1,100 in 2019 → ~21,400 in 2021, nearly
20×. Those carry the hours. The events step is a separate source: 41% of 2021 events are
sub-hour congestion observations that carry almost none. Two providers, two signatures, one
year. This is the sentence for the Q2 slide.

## 10. Q3 — `city_reference` seed and `fct_city_comparison`

**Date:** October 26, 2026

A 10-row seed of 2020 Census population and city-proper land area (Census Gazetteer) for the
ten cities, and a mart joining it to the five-year totals. Two normalizations: hours per
square mile (primary — the closest available proxy for exposure per road mile) and hours per
100k residents (because the city list is itself a population ranking). Road miles from OSM
would be the better denominator; noted as the alternative, skipped for time. Claude wrote
the seed values from memory and the model; I built them. Seed values to be spot-checked
against census.gov QuickFacts before the deck. YAML indentation bit me again on the seed
entry — list-item keys must align with `name`, and PyCharm auto-indents pastes.

| city | raw hours | per sq mi | per 100k residents | rank: raw / sq mi / capita |
|---|---|---|---|---|
| New York | 107.7M | 358k | 1.22M | 1 / 1 / 2 |
| Phoenix | 92.2M | 178k | 5.73M | 2 / 2 / 1 |
| Chicago | 25.7M | 113k | 0.93M | 3 / 3 / 3 |
| Philadelphia | 11.9M | 88k | 0.74M | 5 / 4 / 5 |
| Houston | 18.2M | 28k | 0.79M | 4 / 5 / 4 |
| Dallas | 9.6M | 28k | 0.74M | 6 / 6 / 6 |
| Los Angeles | 7.8M | 17k | 0.20M | 7 / 7 / 9 |
| Austin | 2.6M | 8k | 0.27M | 9 / 8 / 8 |
| San Antonio | 3.9M | 8k | 0.27M | 8 / 9 / 7 |
| San Diego | 1.4M | 4k | 0.10M | 10 / 10 / 10 |

**Finding (in the table):** normalization barely moves the ranking — top three and bottom
one identical under all three metrics; only Phoenix moves, to first per capita (5.7M hours
per 100k residents, ~5× New York).

**Hypothesis (not in the table):** the spread — New York has 81× San Diego's hours per square
mile, Phoenix 55× San Diego's per capita — is far larger than any plausible real difference
in roadwork between large US cities (assumption: real roadwork intensity varies by low
single-digit multiples, not 80×). The most likely explanation is that provider coverage
varies by state DOT. This dataset cannot confirm that directly. What would: (1) a provider
fingerprint by state — the two `wind_direction` encodings in `raw` mark two feeds; (2)
description templates by state; (3) the author's own note that some states have no data
before Aug 2017; (4) an external benchmark — FHWA Highway Statistics state DOT outlay and
lane-miles, to show California spends comparably but reports 1/50th the events.

**Correction (2026-10-26):** Claude first wrote the hypothesis as a finding ("no two US
cities differ 80-fold ... the spread *is* reporting coverage") and added an unsupported
flourish about Phoenix and AV testing. I challenged it; the paragraph above is the corrected
version, separating what the table shows from what is inferred. Logged as a Q6 example of
AI overconfidence caught on review.

## 11. Q4 — route exposure without PostGIS

**Date:** October 26, 2026

PostGIS is not installed on the case-study instance and I decided not to add it for one
question. Instead, three plain-SQL models (Claude wrote, I built and spot-checked):

- `stg_routes` — each route's WKT split into one row per vertex (~700 per route, a few tens
  of metres apart), with a ~100 m grid cell per vertex.
- `int_route_events` — Bay Area construction events represented by start point, end point,
  and points every 50 m along the straight line between them (events ≤ 5 miles); longer
  events on endpoints only and flagged. A grid join compares each point only to route
  vertices in the same or a neighbouring cell; an event matches a route if any of its
  points is within 100 m of a vertex. Hours allocated by year.
- `fct_route_exposure` — per route, per year and 2017–2021: events, hours, hours per
  route-mile (headline), events per mile, severity-weighted hours per mile, long-event count.

Before building, I asked how a 100-mile event could ever match a route when only its two
endpoints are known. Answer: it mostly can't, and the sizing query says how much that
matters — of 60,984 Bay Area events, 63.5% are under a mile, 94.4% under five, 5.6% (~3,400)
longer, max 267 miles. The ≤ 5-mile events are approximated well; the long ones are matched
on endpoints and counted per route so the undercount is visible.

### Result — 2017–2021 combined

| route | miles | events | hours | hours / mile | severity-wtd hours / mile | long events | rank |
|---|---|---|---|---|---|---|---|
| SF → Berkeley | 13.6 | 3,178 | 399,115 | 29,390 | 68,238 | 126 | 1 |
| SF → San Rafael | 18.7 | 3,884 | 434,365 | 23,278 | 57,417 | 126 | 2 |
| SF → San Leandro | 21.2 | 4,642 | 423,665 | 19,975 | 48,125 | 334 | 3 |
| SF → San Mateo | 19.3 | 3,776 | 325,651 | 16,873 | 42,305 | 44 | 4 |
| SF → Pacifica | 15.4 | 1,544 | 208,067 | 13,537 | 33,246 | 48 | 5 |

### Result — rank by hours per mile, by year

| year | 1st | 2nd | 3rd | 4th | 5th |
|---|---|---|---|---|---|
| 2017 | San Leandro | Berkeley | Pacifica | San Rafael | San Mateo |
| 2018 | San Leandro | Berkeley | San Rafael | Pacifica | San Mateo |
| 2019 | San Rafael | Berkeley | San Leandro | San Mateo | Pacifica |
| 2020 | San Rafael | San Leandro | Berkeley | Pacifica | San Mateo |
| 2021 | Berkeley | San Rafael | San Mateo | San Leandro | Pacifica |

**Answer:** SF → Berkeley carries the most construction exposure per mile, both for the
five-year window and for the most recent year, and severity-weighting gives the same order.
**But the leader changed every two years** (San Leandro → San Rafael → Berkeley), and
Berkeley's 2021 is 71% of its five-year total — the same reporting step-change seen in the
cities. What is stable: the three bridge routes (Berkeley, San Rafael, San Leandro) are
always the top three, and Pacifica is at or near the bottom every year.

Caveats specific to Q4: San Leandro has 334 long events to Berkeley's 126, so it is the
route most likely undercounted — plausibly second, not first. Berkeley and San Leandro
share the Bay Bridge approach, so bridge work counts against both; that is real exposure,
not double-counting. The shared downtown start (Van Ness / Mission) counts toward all five.

**Spot check:** the top matched descriptions on the Berkeley route in 2021 are I-80 at
Ashby Ave / CA-13, Cleveland St, the Bay Bridge piers, Treasure Island and the Yerba Buena
tunnel — the model found what a person would expect. Kept as a validation slide.

Assumptions: 100 m buffer; straight-line path for events ≤ 5 miles; endpoints only beyond
that; a matched event's full hours count toward the route; 2017–2021 window with 2021 led
and its Nov–Dec incompleteness noted.

## 12. The deck — `reports/`

**Date:** October 26, 2026

Built the way the Dollar Bank standard builds a document: committed queries → a pull script
that writes one CSV per query → a chart script → a deck script → the `.pptx`, with a README
mapping every slide to its query and a data-validation section kept out of the deck. Four
deliberate deviations, each asked for by the brief: narrative order rather than
summary-first, AI tools named (Q6), the analytics environment named (the code is what is
being graded), and an alternatives slide. Cover photo and logos from Aurora's public media
kit.

Seventeen slides: cover; what was asked and how it was built; environment and load; what
the data is; the three problems found first; staging rules; Q1; Q2 (three slides: the 2021
step, the three feed changes, New York decomposed); Q3; Q4 (two: the result, the matched
events); Q5; Q6; assumptions and alternatives; the query map.

**AI usage:** Claude wrote the queries, the three scripts, the README and the slide text
from the findings in this log; validated the chart palette for colour-vision separation;
rendered the deck and fixed the layout collisions it found (eight slides on the first pass).
I chose the format, the order, the cover image, and I review every number against the
tables above before it is presented. The CSVs in `reports/data/` were transcribed from my
DataGrip output during the build; `pull_deck_data.py` replaces them with the database's own
grids on the next run.

**Rewrite (2026-10-26):** the first deck read as machine-written — headlines phrased as
lessons, bullets with bold lead-ins, phrases like "a faithful copy of the file". I dictated
the narrative for the first half in my own words and Claude rebuilt every slide as
first-person prose in that voice, dropped two slides, and fixed Q1: it had shown the ten
cities from Q3's list instead of the ten cities with the most hours overall. Q1 now ranks
every city; Q2 follows those same ten. Q3 through Q6 are drafted from what I said in
conversation and still need my pass. Fifteen slides.

**Second pass on the deck (2026-10-26):** cut the background paragraphs from the questions
slide (the reader knows why construction matters to a truck); slide titles are now the
questions as the brief words them; Q2 is two slides, the ten cities and then all cities;
Q1 shows hours only, since that is what was asked; every slide links to the model or query
behind it in the repo; the staging slide shows what the first seasonal filter actually
caught (query 13); and the Q4 method is written in plain words with no tooling named.

I asked how we knew three of the routes cross bridges, since I hadn't looked. We hadn't
shown it. `reports/check_route_bridges.py` now measures each route's closest approach to the
Bay Area bridges from the seed coordinates: Berkeley and San Leandro pass 165 m from Yerba
Buena Island (the Bay Bridge), San Rafael 87 m from the Golden Gate's mid-span; San Mateo
and Pacifica never come within 5 km of a bridge. The matched descriptions on the Berkeley
route (SFOBB Pier 1, Treasure Island, Yerba Buena tunnel) say the same thing. The slide now
cites the check instead of asserting it.
