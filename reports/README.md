# reports/ — the take-home deck and everything behind it

The deliverable is `Aurora_Construction_Take_Home.pptx`, built by a committed script from
committed query results. The deck is an output; the scripts and SQL are the source. A number
that changes means re-pulling and re-building, never editing a slide by hand.

## Rebuild

```bash
# 1. on the Mac, against the case-study database (127.0.0.1:5433/case_study):
python reports/pull_deck_data.py        # runs queries/*.sql -> data/*.csv + package.json

# 2. anywhere the repo is checked out:
pip install -r reports/requirements.txt  # matplotlib, python-pptx
python reports/build_charts.py           # data/ -> figures/*.png
python reports/build_deck.py             # data/ + figures/ + media/ -> the .pptx
```

Steps 2 and 3 never touch the database, so the deck can be rebuilt from what it was built
from. The footer of every slide names its query and the pull date from `package.json`.

**The CSVs committed with the first build were transcribed from DataGrip output while the
pull script was being written.** Run `pull_deck_data.py` once to replace them with the
grids straight from the database; the numbers are the same, the provenance is cleaner, and
`03_q2_ten_cities_by_year.csv` gains the event counts the transcription left at zero.

## What is here

| Path | What it is |
|---|---|
| `queries/01–12_*.sql` | Every number on a slide, one query each, against the dbt models |
| `pull_deck_data.py` | Runs the queries, writes `data/` |
| `data/*.csv`, `data/package.json` | The grids the deck was built from, and when they were pulled |
| `build_charts.py` | Five figures, matplotlib, from `data/` |
| `figures/*.png` | The figures |
| `build_deck.py` | The deck, python-pptx, from `data/` + `figures/` + `media/` |
| `media/` | Aurora cover photo, wordmark and mark from the public media kit (aurora.tech/aurora-media-kit) |
| `Aurora_Construction_Take_Home.pptx` | The deliverable, 15 slides |

## Which slide reads which query

| Slide | Query | Reads |
|---|---|---|
| 3–5 Tools, looking at the data, staging | `10_staging_flags`, `12_row_counts` | raw, stg_construction |
| 6 Q1 | `01_q1_top_cities` | int_city_month_hours |
| 7 Q2, why the list looks like this | `03_q2_ten_cities_by_year` | int_city_month_hours |
| 8 Q2, over time | `04_q2_national_monthly`, `05_q2_decomposition_by_year` | int_city_month_hours, stg_construction |
| 9 Q3 | `07_q3_city_comparison` | fct_city_comparison |
| 10 Q4 | `08_q4_route_exposure` | fct_route_exposure |
| 11 Q4 check | `09_q4_berkeley_2021_descriptions` | int_route_events, stg_construction |
| — | `02_q1_ten_cities`, `06_q2_new_york_by_year`, `11_duration_distribution` | log only; not on a slide |

## Data validation

None of this is in the deck. It is here for whoever picks the work up.

- **Load.** 6,170,627 rows loaded with typed columns; the COPY would have failed on any value
  that did not parse, and did not. Primary key on `id` went on clean, so every id is unique.
  `wc -l` reports 6,170,628 because of the header.
- **Dedup.** 6,170,627 → 5,887,586 after removing rows that share start, end, start
  coordinates and description (283,041, 4.6%). The duplicate pairs found by hand differed
  only in the weather columns, consistent with a provider re-pull.
- **Flags.** Construction events: 60 end on the extract date; 433,466 share a start
  timestamp with 100+ other rows (7.4%); 534,664 share an end (9.1%); 0 negative durations.
  Seasonal closures: 1,452 events, median 5 hours — re-published short advisories, not single
  long records.
- **Seasonal-closure pattern.** Every description matching the first word list was exported
  (2,047 distinct, 5,437 events) and read. Street names (Winter St, Winter Haven Dr, Seasons
  Rd, …) and the "Winter Closure Gate" landmark were false positives; the final pattern
  matches phrasings only. Rows it matches average ~2,000 hours; rows it rejects average ~470.
- **Duration distribution.** No single value dominates (top value 4.7% of events). Round
  values (96 h = exactly four days, 4.3%; then 6, 5, 8, 10, 9, 2 h) are provider templates;
  ~15% of events are under an hour.
- **Month allocation.** Monthly national hours sum to the same total as event hours
  restricted to the window, by construction of the overlap join.
- **Q4 matching.** The twelve highest-hour descriptions matched to the Berkeley route in 2021
  are I-80 at Ashby, Cleveland St, the Bay Bridge piers, Treasure Island, the Yerba Buena
  tunnel and the shared Van Ness / Mission start — what a person would expect. Of 60,984 Bay
  Area events, 63.5% are under a mile, 94.4% under five; the 3,415 longer are matched on
  endpoints only and counted per route.
- **Seed values.** City population and land area are 2020 Census figures entered from
  memory; spot-check two against census.gov QuickFacts before the deck is presented.

## Deviations from the house document standard, on purpose

The deck follows the Dollar Bank standard (`docs/document.md` in the dbt_local repo) in
mechanics — script-built, every number traceable, captions carry denominators, limits stated
in-line, no tells — with four exceptions that the brief itself asks for:

1. **Narrative order, not summary-first, in the first person.** The deck walks through the
   work as it happened and reads the way it would be said out loud, because the brief says
   they are assessing "your reasoning through these questions".
2. **AI tools are named.** Q6 asks which tools were used and how.
3. **The analytics environment is named.** The brief says "submit all your code"; the code
   is the point.
4. **An alternatives slide exists.** The brief asks to "mention alternative more
   sophisticated ways to tackle the problem".

Charts use python-pptx-placed PNGs rather than the house builder's native charts because the
house builder is bound to the Dollar Bank template file. Fonts are Calibri on slides and
Arial on charts (both ship with Office and render true in LibreOffice for QA).

## The process log

`../process.md` is the running record: environment setup, every finding in the order it was
found, the decisions and who made them, and the three places the AI was wrong and how each
was caught. The deck's Q6 slide summarises it.
