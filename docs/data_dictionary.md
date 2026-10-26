# Data dictionary — US Road Construction and Closures (2016–2021)

Reference for `raw.us_constructions`. Column descriptions here are the source of truth for
`sources.yml`; cite this file rather than inferring meaning from column names.

## Provenance

| | |
|---|---|
| Kaggle dataset | https://www.kaggle.com/datasets/sobhanmoosavi/us-road-construction-and-closures |
| Author | Sobhan Moosavi (same author and pipeline as the US Accidents and LSTW datasets) |
| File | `US_Constructions_Dec21.csv` — 6,170,628 rows, 47 columns, 2.7 GB |
| Period | January 2016 through December 2021 (Kaggle description) |
| Coverage | 49 US states (Kaggle description). The author's sibling LSTW dataset notes that some states have no data before Aug 2017 — worth checking here when profiling coverage by year |
| License | CC BY-NC-SA 4.0 — distributed for research / non-commercial use only (Kaggle usage policy) |
| Collection | "Multiple APIs that provide streaming traffic incident (or event) data", which broadcast data captured by US and state DOTs, law enforcement, traffic cameras and road-network sensors (Kaggle description). The page does not name the providers; the author's US Accidents paper names MapQuest Traffic and Bing Map Traffic for the sibling pipeline — likely the same here, but not confirmed for this file |
| Paper to cite | Karimi Monsefi, Amin, Sobhan Moosavi, and Rajiv Ramnath. "Will there be a construction? Predicting road constructions based on heterogeneous spatiotemporal data." Proceedings of the 30th ACM SIGSPATIAL 2022. https://arxiv.org/abs/2209.06813 |

The Kaggle page is JavaScript-rendered, so its text was copied by hand (2026-10-23). The column
dictionary below is the author's published dictionary for the identically structured
US Accidents dataset (https://smoosavi.org/datasets/us_accidents); where his wording says
"accident", read "construction/closure event". Nothing else was changed.

### Kaggle description (verbatim)

> This is a countrywide dataset of road construction and closure events, which covers 49 states
> of the US. Construction events in this dataset could be any roadwork, ranging from fixing
> pavements to substantial projects that could take months to finish. The data is collected from
> Jan 2016 to Dec 2021, using multiple APIs that provide streaming traffic incident (or event)
> data. These APIs broadcast traffic data captured by a variety of entities, such as the US and
> state departments of transportation, law enforcement agencies, traffic cameras, and traffic
> sensors within the road-networks. Currently, there are about 6.2 million construction and
> closure records in this dataset.

The page's own suggested uses include "studying road constructions' life cycle" and guiding
planners to "choose constructions sites with least impact on traffic flow" — the same framing
as Q1–Q4 here. Note the phrase "from fixing pavements to substantial projects that could take
months to finish": the author expects a very wide duration range, so multi-month events are a
feature of the data, not necessarily errors.

## Why provenance matters for this analysis

The dataset is not a census of construction. It is whatever the two traffic APIs
broadcast, and each API's coverage varies by state, by city and over time. Any trend
("how has this changed over time") or cross-city comparison is a trend in *reported*
events and has to be read with that in mind. There is no `Source` column in this file
(the US Accidents dataset has one), so provider cannot be separated out directly.

## Columns

Source name → `raw.us_constructions` name, the type used in raw, and the author's description.

| # | Source column | Raw column | Raw type | Description (author's wording) |
|---|---|---|---|---|
| 1 | ID | `id` | text | This is a unique identifier of the record. |
| 2 | Severity | `severity` | smallint | Shows the severity of the event, a number between 1 and 4, where 1 indicates the least impact on traffic (i.e., short delay as a result of the event) and 4 indicates a significant impact on traffic (i.e., long delay). |
| 3 | Start_Time | `start_time` | timestamp | Shows start time of the event in local time zone. |
| 4 | End_Time | `end_time` | timestamp | Shows end time of the event in local time zone. End time here refers to when the impact on traffic flow was dismissed. |
| 5 | Start_Lat | `start_lat` | double precision | Shows latitude in GPS coordinate of the start point. |
| 6 | Start_Lng | `start_lng` | double precision | Shows longitude in GPS coordinate of the start point. |
| 7 | End_Lat | `end_lat` | double precision | Shows latitude in GPS coordinate of the end point. |
| 8 | End_Lng | `end_lng` | double precision | Shows longitude in GPS coordinate of the end point. |
| 9 | Distance(mi) | `distance_mi` | double precision | The length of the road extent affected by the event. |
| 10 | Description | `description` | text | Shows natural language description of the event. |
| 11 | Number | `street_number` | double precision | Shows the street number in address field. |
| 12 | Street | `street` | text | Shows the street name in address field. |
| 13 | Side | `side` | text | Shows the relative side of the street (Right/Left) in address field. |
| 14 | City | `city` | text | Shows the city in address field. |
| 15 | County | `county` | text | Shows the county in address field. |
| 16 | State | `state` | text | Shows the state in address field. |
| 17 | Zipcode | `zipcode` | text | Shows the zipcode in address field. |
| 18 | Country | `country` | text | Shows the country in address field. |
| 19 | Timezone | `timezone` | text | Shows timezone based on the location of the event (eastern, central, etc.). |
| 20 | Airport_Code | `airport_code` | text | Denotes an airport-based weather station which is the closest one to location of the event. |
| 21 | Weather_Timestamp | `weather_timestamp` | timestamp | Shows the time-stamp of weather observation record (in local time). |
| 22 | Temperature(F) | `temperature_f` | double precision | Shows the temperature (in Fahrenheit). |
| 23 | Wind_Chill(F) | `wind_chill_f` | double precision | Shows the wind chill (in Fahrenheit). |
| 24 | Humidity(%) | `humidity_pct` | double precision | Shows the humidity (in percentage). |
| 25 | Pressure(in) | `pressure_in` | double precision | Shows the air pressure (in inches). |
| 26 | Visibility(mi) | `visibility_mi` | double precision | Shows visibility (in miles). |
| 27 | Wind_Direction | `wind_direction` | text | Shows wind direction. |
| 28 | Wind_Speed(mph) | `wind_speed_mph` | double precision | Shows wind speed (in miles per hour). |
| 29 | Precipitation(in) | `precipitation_in` | double precision | Shows precipitation amount in inches, if there is any. |
| 30 | Weather_Condition | `weather_condition` | text | Shows the weather condition (rain, snow, thunderstorm, fog, etc.) |
| 31 | Amenity | `amenity` | boolean | A POI annotation which indicates presence of amenity in a nearby location. |
| 32 | Bump | `bump` | boolean | A POI annotation which indicates presence of speed bump or hump in a nearby location. |
| 33 | Crossing | `crossing` | boolean | A POI annotation which indicates presence of crossing in a nearby location. |
| 34 | Give_Way | `give_way` | boolean | A POI annotation which indicates presence of give_way in a nearby location. |
| 35 | Junction | `junction` | boolean | A POI annotation which indicates presence of junction in a nearby location. |
| 36 | No_Exit | `no_exit` | boolean | A POI annotation which indicates presence of no_exit in a nearby location. |
| 37 | Railway | `railway` | boolean | A POI annotation which indicates presence of railway in a nearby location. |
| 38 | Roundabout | `roundabout` | boolean | A POI annotation which indicates presence of roundabout in a nearby location. |
| 39 | Station | `station` | boolean | A POI annotation which indicates presence of station in a nearby location. |
| 40 | Stop | `stop` | boolean | A POI annotation which indicates presence of stop in a nearby location. |
| 41 | Traffic_Calming | `traffic_calming` | boolean | A POI annotation which indicates presence of traffic_calming in a nearby location. |
| 42 | Traffic_Signal | `traffic_signal` | boolean | A POI annotation which indicates presence of traffic_signal in a nearby location. |
| 43 | Turning_Loop | `turning_loop` | boolean | A POI annotation which indicates presence of turning_loop in a nearby location. |
| 44 | Sunrise_Sunset | `sunrise_sunset` | text | Shows the period of day (i.e. day or night) based on sunrise/sunset. |
| 45 | Civil_Twilight | `civil_twilight` | text | Shows the period of day (i.e. day or night) based on civil twilight. |
| 46 | Nautical_Twilight | `nautical_twilight` | text | Shows the period of day (i.e. day or night) based on nautical twilight. |
| 47 | Astronomical_Twilight | `astronomical_twilight` | text | Shows the period of day (i.e. day or night) based on astronomical twilight. |

## Reading notes for this assignment

- **Times are local**, not UTC — `start_time` and `end_time` can be subtracted directly for a
  duration without timezone conversion. (The author's LSTW dataset uses UTC; this one does not.)
- **`end_time` is when the traffic impact was dismissed**, not necessarily when work finished.
  "Hours of construction" in this dataset means hours of reported traffic impact.
- **Severity is traffic impact (1–4)**, not size or type of work.
- **`distance_mi` is the affected road extent**, which is the natural weight for a per-route
  exposure metric alongside duration.
- **Columns 20–30 are a weather snapshot** from the nearest airport station at `weather_timestamp`,
  and **31–43 are OpenStreetMap-style point-of-interest flags** near the event. Neither is needed
  for Q1–Q4; they are loaded for completeness and ignored in staging.
- **Columns 44–47** classify the event's start as day/night under four twilight definitions.

## Sources

- Karimi Monsefi, Moosavi & Ramnath (2022), the paper the dataset asks you to cite: https://arxiv.org/abs/2209.06813
- Author's US Accidents dictionary (identical schema): https://smoosavi.org/datasets/us_accidents
- Author's LSTW dataset page (lineage, license, coverage notes): https://smoosavi.org/datasets/lstw
- Kaggle dataset page: https://www.kaggle.com/datasets/sobhanmoosavi/us-road-construction-and-closures
