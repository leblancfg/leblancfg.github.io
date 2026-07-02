# CrossFit Open Dataset Artifact

This folder contains a reproducible SQLite artifact built from public CrossFit Games leaderboard pages and APIs.

Current checked-in artifact:

- `crossfit_open_2026.sqlite`
- full 2026 Open Men 35-39 leaderboard: 29,171 athletes
- full 2026 Open Men 35-39 workout scores: 87,513 rows
- discovered page and competitor counts for 23 known 2026 Open divisions
- top-25 Men 35-39 public athlete profile sample for benchmark-stat parsing

The scraper is intentionally checkpointed and polite:

- raw successful responses are stored in `source_fetches`
- normalized leaderboard rows are stored in `leaderboard_entries`, `athletes`, and `workout_scores`
- re-running the same command skips already-successful fetches unless `--refresh` is passed
- the default delay is one second per leaderboard page and three seconds per athlete profile page

Robots check on July 2, 2026: `https://games.crossfit.com/robots.txt` disallowed `/register/open`, `/submit-scores`, and `/manage-competition/athlete`; the leaderboard and public athlete pages were allowed.

## Build

From the repository root:

```bash
python3 scripts/crossfit_open_dataset.py --db data/crossfit-open/crossfit_open_2026.sqlite discover --sleep 1.0
python3 scripts/crossfit_open_dataset.py --db data/crossfit-open/crossfit_open_2026.sqlite scrape-leaderboard --division 18 --sleep 1.0
python3 scripts/crossfit_open_dataset.py --db data/crossfit-open/crossfit_open_2026.sqlite scrape-profiles --division 18 --limit 25 --sleep 3.0
python3 scripts/crossfit_open_dataset.py --db data/crossfit-open/crossfit_open_2026.sqlite write-summary-assets --out-dir data/crossfit-open
```

To continue toward all known 2026 Open divisions:

```bash
python3 scripts/crossfit_open_dataset.py --db data/crossfit-open/crossfit_open_2026.sqlite scrape-leaderboard --division all --sleep 1.0
```

## Tables

- `metadata`: source and schema metadata.
- `source_fetches`: raw checkpointed HTTP responses, keyed by source type, year, division/page, or athlete id.
- `divisions`: discovered division names, categories, page counts, and competitor counts.
- `athletes`: athlete profile fields exposed in leaderboard rows.
- `leaderboard_entries`: one row per athlete per division, including rank fraction and rank-derived `performance_percentile`.
- `workout_scores`: one row per athlete per Open workout.
- `athlete_open_ranks`: optional profile-page rank history parsed from public athlete pages.
- `benchmark_stats`: optional self-reported benchmark values parsed from public athlete pages.

## Percentile Definition

CrossFit athlete pages did not expose an Open percentile field during the July 2, 2026 preflight. The dataset therefore derives:

```text
performance_percentile = 100 * (1 - ((overall_rank - 1) / (total_competitors - 1)))
```

The top-ranked athlete is 100.0. The last-ranked athlete approaches 0.0. A 90th percentile athlete is inside approximately the top 10 percent of their division.

## Provenance

- Leaderboard HTML page inspected: `https://games.crossfit.com/leaderboard/open/2026?division=18&sort=0`
- Leaderboard API used: `https://c3po.crossfit.com/api/leaderboards/v2/competitions/open/2026/leaderboards?division=18&sort=0&page=1`
- Athlete page sample inspected: `https://games.crossfit.com/athlete/911088`
- Robots file inspected: `https://games.crossfit.com/robots.txt`

This is an independent research artifact. CrossFit is a trademark of CrossFit LLC; the source data remains owned by its respective publisher.
