#!/usr/bin/env python3
"""Build a checkpointed SQLite dataset from public CrossFit Open leaderboards.

The CrossFit Games site currently renders leaderboards from the public
`c3po.crossfit.com` API. This script keeps the original API responses in
SQLite, normalizes the competition rows, and can resume without refetching
successful pages.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_DB = Path("data/crossfit-open/crossfit_open_2026.sqlite")
USER_AGENT = "leblancfg.com CrossFit Open research dataset (contact: https://leblancfg.com)"
LEADERBOARD_URL = (
    "https://c3po.crossfit.com/api/leaderboards/v2/competitions/"
    "{competition_type}/{year}/leaderboards?division={division_id}&sort={sort}&page={page}"
)
ATHLETE_URL = "https://games.crossfit.com/athlete/{competitor_id}"


DIVISIONS_2026: dict[int, dict[str, str]] = {
    1: {"name": "Men", "category": "individual", "gender": "M"},
    2: {"name": "Women", "category": "individual", "gender": "F"},
    3: {"name": "Men 45-49", "category": "age_group", "gender": "M"},
    4: {"name": "Women 45-49", "category": "age_group", "gender": "F"},
    5: {"name": "Men 50-54", "category": "age_group", "gender": "M"},
    6: {"name": "Women 50-54", "category": "age_group", "gender": "F"},
    7: {"name": "Men 55-59", "category": "age_group", "gender": "M"},
    8: {"name": "Women 55-59", "category": "age_group", "gender": "F"},
    11: {"name": "Teams", "category": "team", "gender": ""},
    12: {"name": "Men 40-44", "category": "age_group", "gender": "M"},
    13: {"name": "Women 40-44", "category": "age_group", "gender": "F"},
    14: {"name": "Boys 14-15", "category": "teen", "gender": "M"},
    15: {"name": "Girls 14-15", "category": "teen", "gender": "F"},
    16: {"name": "Boys 16-17", "category": "teen", "gender": "M"},
    17: {"name": "Girls 16-17", "category": "teen", "gender": "F"},
    18: {"name": "Men 35-39", "category": "age_group", "gender": "M"},
    19: {"name": "Women 35-39", "category": "age_group", "gender": "F"},
    36: {"name": "Men 60-64", "category": "age_group", "gender": "M"},
    37: {"name": "Women 60-64", "category": "age_group", "gender": "F"},
    40: {"name": "Men 65-69", "category": "age_group", "gender": "M"},
    41: {"name": "Women 65-69", "category": "age_group", "gender": "F"},
    42: {"name": "Men 70+", "category": "age_group", "gender": "M"},
    43: {"name": "Women 70+", "category": "age_group", "gender": "F"},
}


SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_fetches (
  source_type TEXT NOT NULL,
  year INTEGER NOT NULL,
  competition_type TEXT NOT NULL,
  division_id INTEGER NOT NULL DEFAULT -1,
  page INTEGER NOT NULL DEFAULT -1,
  competitor_id TEXT NOT NULL DEFAULT '',
  url TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  http_status INTEGER NOT NULL,
  sha256 TEXT,
  body TEXT,
  error TEXT,
  PRIMARY KEY (source_type, year, competition_type, division_id, page, competitor_id)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS divisions (
  year INTEGER NOT NULL,
  competition_type TEXT NOT NULL,
  division_id INTEGER NOT NULL,
  division_name TEXT NOT NULL,
  category TEXT NOT NULL,
  gender TEXT,
  total_pages INTEGER,
  total_competitors INTEGER,
  discovered_at TEXT NOT NULL,
  PRIMARY KEY (year, competition_type, division_id)
);

CREATE TABLE IF NOT EXISTS athletes (
  competitor_id TEXT PRIMARY KEY,
  competitor_name TEXT,
  first_name TEXT,
  last_name TEXT,
  gender TEXT,
  country_code TEXT,
  country_name TEXT,
  region_id TEXT,
  region_name TEXT,
  affiliate_id TEXT,
  affiliate_name TEXT,
  age INTEGER,
  height_raw TEXT,
  weight_raw TEXT,
  profile_pic_s3_key TEXT,
  status TEXT,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leaderboard_entries (
  year INTEGER NOT NULL,
  competition_type TEXT NOT NULL,
  division_id INTEGER NOT NULL,
  competitor_id TEXT NOT NULL,
  overall_rank INTEGER,
  overall_rank_raw TEXT,
  overall_score TEXT,
  rank_fraction REAL,
  performance_percentile REAL,
  next_stage TEXT,
  scaled INTEGER,
  source_page INTEGER NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (year, competition_type, division_id, competitor_id)
);

CREATE TABLE IF NOT EXISTS workout_scores (
  year INTEGER NOT NULL,
  competition_type TEXT NOT NULL,
  division_id INTEGER NOT NULL,
  competitor_id TEXT NOT NULL,
  ordinal INTEGER NOT NULL,
  workout_label TEXT,
  rank INTEGER,
  rank_raw TEXT,
  score_raw TEXT,
  score_display TEXT,
  valid TEXT,
  scaled INTEGER,
  video INTEGER,
  judge TEXT,
  affiliate TEXT,
  time_seconds INTEGER,
  breakdown TEXT,
  score_identifier TEXT,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (year, competition_type, division_id, competitor_id, ordinal)
);

CREATE TABLE IF NOT EXISTS athlete_open_ranks (
  competitor_id TEXT NOT NULL,
  year INTEGER NOT NULL,
  scope TEXT NOT NULL,
  division_name TEXT NOT NULL DEFAULT '',
  rank_raw TEXT,
  rank INTEGER,
  url TEXT,
  parsed_at TEXT NOT NULL,
  PRIMARY KEY (competitor_id, year, scope, division_name)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS benchmark_stats (
  competitor_id TEXT NOT NULL,
  stat_name TEXT NOT NULL,
  raw_value TEXT NOT NULL,
  numeric_value REAL,
  unit TEXT,
  parsed_at TEXT NOT NULL,
  PRIMARY KEY (competitor_id, stat_name)
);

CREATE INDEX IF NOT EXISTS idx_leaderboard_division_rank
  ON leaderboard_entries (year, competition_type, division_id, overall_rank);
CREATE INDEX IF NOT EXISTS idx_scores_workout_rank
  ON workout_scores (year, competition_type, division_id, ordinal, rank);
CREATE INDEX IF NOT EXISTS idx_athletes_country
  ON athletes (country_code, region_name);
"""


def utcnow() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    set_metadata(con, "schema_version", "1")
    set_metadata(con, "generated_by", "scripts/crossfit_open_dataset.py")
    return con


def set_metadata(con: sqlite3.Connection, key: str, value: str) -> None:
    con.execute(
        """
        INSERT INTO metadata (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """,
        (key, value, utcnow()),
    )


def parse_int(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"\d+", str(value).replace(",", ""))
    return int(match.group(0)) if match else None


def parse_float_with_unit(raw_value: str) -> tuple[float | None, str | None]:
    clean = " ".join(raw_value.split())
    if not clean or clean == "--":
        return None, None
    match = re.match(r"^(-?\d+(?:\.\d+)?)(?:\s*([A-Za-z]+))?$", clean)
    if not match:
        return None, None
    return float(match.group(1)), match.group(2)


def performance_percentile(rank: int | None, total: int | None) -> float | None:
    if not rank or not total or total < 1:
        return None
    if total == 1:
        return 100.0
    return round(100.0 * (1.0 - ((rank - 1) / (total - 1))), 4)


def rank_fraction(rank: int | None, total: int | None) -> float | None:
    if not rank or not total:
        return None
    return round(rank / total, 8)


def fetch(
    con: sqlite3.Connection,
    *,
    source_type: str,
    year: int,
    competition_type: str,
    url: str,
    division_id: int | None = None,
    page: int | None = None,
    competitor_id: str | None = None,
    sleep_seconds: float = 1.0,
    refresh: bool = False,
) -> str:
    division_key = division_id if division_id is not None else -1
    page_key = page if page is not None else -1
    competitor_key = competitor_id if competitor_id is not None else ""
    existing = con.execute(
        """
        SELECT body, http_status, error
        FROM source_fetches
        WHERE source_type = ?
          AND year = ?
          AND competition_type = ?
          AND division_id = ?
          AND page = ?
          AND competitor_id = ?
        """,
        (source_type, year, competition_type, division_key, page_key, competitor_key),
    ).fetchone()
    if existing and existing["http_status"] == 200 and existing["body"] and not refresh:
        return str(existing["body"])

    if sleep_seconds > 0:
        time.sleep(sleep_seconds)

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    status = 0
    body = ""
    error = None
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = int(response.status)
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        error = str(exc)
        body = exc.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 - stored for restartable diagnostics.
        status = 0
        error = f"{type(exc).__name__}: {exc}"

    digest = hashlib.sha256(body.encode("utf-8")).hexdigest() if body else None
    con.execute(
        """
        INSERT INTO source_fetches (
          source_type, year, competition_type, division_id, page, competitor_id,
          url, fetched_at, http_status, sha256, body, error
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT DO UPDATE SET
          url=excluded.url,
          fetched_at=excluded.fetched_at,
          http_status=excluded.http_status,
          sha256=excluded.sha256,
          body=excluded.body,
          error=excluded.error
        """,
        (
            source_type,
            year,
            competition_type,
            division_key,
            page_key,
            competitor_key,
            url,
            utcnow(),
            status,
            digest,
            body,
            error,
        ),
    )
    con.commit()
    if status != 200:
        raise RuntimeError(f"fetch failed ({status}) for {url}: {error or body[:200]}")
    return body


def leaderboard_url(year: int, competition_type: str, division_id: int, page: int, sort: int) -> str:
    return LEADERBOARD_URL.format(
        competition_type=urllib.parse.quote(competition_type),
        year=year,
        division_id=division_id,
        sort=sort,
        page=page,
    )


def upsert_division(
    con: sqlite3.Connection,
    *,
    year: int,
    competition_type: str,
    division_id: int,
    total_pages: int | None,
    total_competitors: int | None,
) -> None:
    info = DIVISIONS_2026.get(division_id, {"name": f"Division {division_id}", "category": "unknown", "gender": ""})
    con.execute(
        """
        INSERT INTO divisions (
          year, competition_type, division_id, division_name, category, gender,
          total_pages, total_competitors, discovered_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(year, competition_type, division_id) DO UPDATE SET
          division_name=excluded.division_name,
          category=excluded.category,
          gender=excluded.gender,
          total_pages=excluded.total_pages,
          total_competitors=excluded.total_competitors,
          discovered_at=excluded.discovered_at
        """,
        (
            year,
            competition_type,
            division_id,
            info["name"],
            info["category"],
            info["gender"],
            total_pages,
            total_competitors,
            utcnow(),
        ),
    )


def normalize_leaderboard_page(
    con: sqlite3.Connection,
    *,
    year: int,
    competition_type: str,
    division_id: int,
    source_page: int,
    payload: dict[str, Any],
) -> int:
    pagination = payload.get("pagination") or {}
    total_competitors = parse_int(pagination.get("totalCompetitors"))
    total_pages = parse_int(pagination.get("totalPages"))
    upsert_division(
        con,
        year=year,
        competition_type=competition_type,
        division_id=division_id,
        total_pages=total_pages,
        total_competitors=total_competitors,
    )
    ordinals = {int(o["ordinal"]): str(o.get("columnName") or o["ordinal"]) for o in payload.get("ordinals") or []}
    rows = payload.get("leaderboardRows") or []
    now = utcnow()

    for row in rows:
        entrant = row.get("entrant") or {}
        competitor_id = str(entrant.get("competitorId") or "")
        if not competitor_id:
            continue
        overall_rank = parse_int(row.get("overallRank"))
        con.execute(
            """
            INSERT INTO athletes (
              competitor_id, competitor_name, first_name, last_name, gender,
              country_code, country_name, region_id, region_name, affiliate_id,
              affiliate_name, age, height_raw, weight_raw, profile_pic_s3_key,
              status, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(competitor_id) DO UPDATE SET
              competitor_name=excluded.competitor_name,
              first_name=excluded.first_name,
              last_name=excluded.last_name,
              gender=excluded.gender,
              country_code=excluded.country_code,
              country_name=excluded.country_name,
              region_id=excluded.region_id,
              region_name=excluded.region_name,
              affiliate_id=excluded.affiliate_id,
              affiliate_name=excluded.affiliate_name,
              age=excluded.age,
              height_raw=excluded.height_raw,
              weight_raw=excluded.weight_raw,
              profile_pic_s3_key=excluded.profile_pic_s3_key,
              status=excluded.status,
              updated_at=excluded.updated_at
            """,
            (
                competitor_id,
                entrant.get("competitorName"),
                entrant.get("firstName"),
                entrant.get("lastName"),
                entrant.get("gender"),
                entrant.get("countryOfOriginCode"),
                entrant.get("countryOfOriginName"),
                entrant.get("regionId"),
                entrant.get("regionName"),
                entrant.get("affiliateId"),
                entrant.get("affiliateName"),
                parse_int(entrant.get("age")),
                entrant.get("height"),
                entrant.get("weight"),
                entrant.get("profilePicS3key"),
                entrant.get("status"),
                now,
            ),
        )
        con.execute(
            """
            INSERT INTO leaderboard_entries (
              year, competition_type, division_id, competitor_id, overall_rank,
              overall_rank_raw, overall_score, rank_fraction, performance_percentile,
              next_stage, scaled, source_page, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(year, competition_type, division_id, competitor_id) DO UPDATE SET
              overall_rank=excluded.overall_rank,
              overall_rank_raw=excluded.overall_rank_raw,
              overall_score=excluded.overall_score,
              rank_fraction=excluded.rank_fraction,
              performance_percentile=excluded.performance_percentile,
              next_stage=excluded.next_stage,
              scaled=excluded.scaled,
              source_page=excluded.source_page,
              updated_at=excluded.updated_at
            """,
            (
                year,
                competition_type,
                division_id,
                competitor_id,
                overall_rank,
                row.get("overallRank"),
                row.get("overallScore"),
                rank_fraction(overall_rank, total_competitors),
                performance_percentile(overall_rank, total_competitors),
                row.get("nextStage"),
                parse_int((payload.get("competition") or {}).get("scaled")),
                source_page,
                now,
            ),
        )
        for score in row.get("scores") or []:
            ordinal = parse_int(score.get("ordinal"))
            if ordinal is None:
                continue
            con.execute(
                """
                INSERT INTO workout_scores (
                  year, competition_type, division_id, competitor_id, ordinal,
                  workout_label, rank, rank_raw, score_raw, score_display,
                  valid, scaled, video, judge, affiliate, time_seconds,
                  breakdown, score_identifier, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(year, competition_type, division_id, competitor_id, ordinal) DO UPDATE SET
                  workout_label=excluded.workout_label,
                  rank=excluded.rank,
                  rank_raw=excluded.rank_raw,
                  score_raw=excluded.score_raw,
                  score_display=excluded.score_display,
                  valid=excluded.valid,
                  scaled=excluded.scaled,
                  video=excluded.video,
                  judge=excluded.judge,
                  affiliate=excluded.affiliate,
                  time_seconds=excluded.time_seconds,
                  breakdown=excluded.breakdown,
                  score_identifier=excluded.score_identifier,
                  updated_at=excluded.updated_at
                """,
                (
                    year,
                    competition_type,
                    division_id,
                    competitor_id,
                    ordinal,
                    ordinals.get(ordinal),
                    parse_int(score.get("rank")),
                    score.get("rank"),
                    score.get("score"),
                    score.get("scoreDisplay"),
                    score.get("valid"),
                    parse_int(score.get("scaled")),
                    parse_int(score.get("video")),
                    score.get("judge"),
                    score.get("affiliate"),
                    parse_int(score.get("time")),
                    score.get("breakdown"),
                    score.get("scoreIdentifier"),
                    now,
                ),
            )
    return len(rows)


def scrape_leaderboard(
    con: sqlite3.Connection,
    *,
    year: int,
    competition_type: str,
    division_id: int,
    sort: int,
    sleep_seconds: float,
    max_pages: int | None,
    refresh: bool,
) -> None:
    first_body = fetch(
        con,
        source_type="leaderboard",
        year=year,
        competition_type=competition_type,
        division_id=division_id,
        page=1,
        url=leaderboard_url(year, competition_type, division_id, 1, sort),
        sleep_seconds=sleep_seconds,
        refresh=refresh,
    )
    first_payload = json.loads(first_body)
    total_pages = parse_int((first_payload.get("pagination") or {}).get("totalPages")) or 0
    target_pages = total_pages if max_pages is None else min(total_pages, max_pages)
    rows = normalize_leaderboard_page(
        con,
        year=year,
        competition_type=competition_type,
        division_id=division_id,
        source_page=1,
        payload=first_payload,
    )
    con.commit()
    print(f"division={division_id} page=1/{total_pages} rows={rows}")

    for page in range(2, target_pages + 1):
        body = fetch(
            con,
            source_type="leaderboard",
            year=year,
            competition_type=competition_type,
            division_id=division_id,
            page=page,
            url=leaderboard_url(year, competition_type, division_id, page, sort),
            sleep_seconds=sleep_seconds,
            refresh=refresh,
        )
        payload = json.loads(body)
        rows = normalize_leaderboard_page(
            con,
            year=year,
            competition_type=competition_type,
            division_id=division_id,
            source_page=page,
            payload=payload,
        )
        con.commit()
        print(f"division={division_id} page={page}/{total_pages} rows={rows}")


def discover(
    con: sqlite3.Connection,
    *,
    year: int,
    competition_type: str,
    sleep_seconds: float,
    refresh: bool,
) -> None:
    for division_id in DIVISIONS_2026:
        body = fetch(
            con,
            source_type="leaderboard",
            year=year,
            competition_type=competition_type,
            division_id=division_id,
            page=1,
            url=leaderboard_url(year, competition_type, division_id, 1, 0),
            sleep_seconds=sleep_seconds,
            refresh=refresh,
        )
        payload = json.loads(body)
        pagination = payload.get("pagination") or {}
        upsert_division(
            con,
            year=year,
            competition_type=competition_type,
            division_id=division_id,
            total_pages=parse_int(pagination.get("totalPages")),
            total_competitors=parse_int(pagination.get("totalCompetitors")),
        )
        con.commit()
        info = DIVISIONS_2026[division_id]
        print(
            f"{division_id:>2} {info['name']:<14} "
            f"pages={pagination.get('totalPages')} competitors={pagination.get('totalCompetitors')}"
        )


BENCHMARK_RE = re.compile(
    r'<tr>\s*<th[^>]*class="[^"]*stats-header[^"]*"[^>]*>(?P<name>.*?)</th>\s*<td[^>]*>(?P<value>.*?)</td>\s*</tr>',
    re.IGNORECASE | re.DOTALL,
)
OPEN_ROW_RE = re.compile(r"<tr>\s*<td[^>]*>\s*(?P<year>20\d{2})\s*</td>(?P<body>.*?)</tr>", re.DOTALL)
RANK_LINK_RE = re.compile(
    r'<span class="rank">(?:<a href="(?P<url>[^"]+)">)?(?P<rank>[^<]+?)(?:<small>[^<]+</small>)?(?:</a>)?</span>\s*'
    r'<span class="division">(?P<division>[^<]+)</span>',
    re.DOTALL,
)


def clean_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    return " ".join(html.unescape(text).split())


def parse_profile(con: sqlite3.Connection, competitor_id: str, body: str) -> None:
    parsed_at = utcnow()
    if "Benchmark Stats" in body:
        benchmark_section = body.split("Benchmark Stats", 1)[1]
        for match in BENCHMARK_RE.finditer(benchmark_section):
            name = clean_text(match.group("name"))
            value = clean_text(match.group("value"))
            if not name or not value or value == "--":
                continue
            numeric, unit = parse_float_with_unit(value)
            con.execute(
                """
                INSERT INTO benchmark_stats (
                  competitor_id, stat_name, raw_value, numeric_value, unit, parsed_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(competitor_id, stat_name) DO UPDATE SET
                  raw_value=excluded.raw_value,
                  numeric_value=excluded.numeric_value,
                  unit=excluded.unit,
                  parsed_at=excluded.parsed_at
                """,
                (competitor_id, name, value, numeric, unit, parsed_at),
            )

    open_section = body.split("<h4>Open</h4>", 1)
    if len(open_section) == 2:
        section = open_section[1].split("</table>", 1)[0]
        for row in OPEN_ROW_RE.finditer(section):
            year = int(row.group("year"))
            for idx, rank_match in enumerate(RANK_LINK_RE.finditer(row.group("body"))):
                raw_rank = clean_text(rank_match.group("rank"))
                division_name = clean_text(rank_match.group("division"))
                scope = "worldwide" if idx < 2 else f"profile_scope_{idx + 1}"
                con.execute(
                    """
                    INSERT INTO athlete_open_ranks (
                      competitor_id, year, scope, division_name, rank_raw, rank, url, parsed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT DO UPDATE SET
                      rank_raw=excluded.rank_raw,
                      rank=excluded.rank,
                      url=excluded.url,
                      parsed_at=excluded.parsed_at
                    """,
                    (
                        competitor_id,
                        year,
                        scope,
                        division_name,
                        raw_rank,
                        parse_int(raw_rank),
                        html.unescape(rank_match.group("url") or ""),
                        parsed_at,
                    ),
                )


def scrape_profiles(
    con: sqlite3.Connection,
    *,
    year: int,
    competition_type: str,
    division_id: int,
    limit: int | None,
    sleep_seconds: float,
    refresh: bool,
) -> None:
    query = """
        SELECT competitor_id
        FROM leaderboard_entries
        WHERE year = ? AND competition_type = ? AND division_id = ?
        ORDER BY overall_rank IS NULL, overall_rank, competitor_id
    """
    params: list[Any] = [year, competition_type, division_id]
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    rows = con.execute(query, params).fetchall()
    for index, row in enumerate(rows, start=1):
        competitor_id = str(row["competitor_id"])
        body = fetch(
            con,
            source_type="athlete_profile",
            year=year,
            competition_type=competition_type,
            competitor_id=competitor_id,
            url=ATHLETE_URL.format(competitor_id=competitor_id),
            sleep_seconds=sleep_seconds,
            refresh=refresh,
        )
        parse_profile(con, competitor_id, body)
        con.commit()
        print(f"profile {index}/{len(rows)} competitor_id={competitor_id}")


def write_summary_assets(con: sqlite3.Connection, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    division_rows = con.execute(
        """
        SELECT d.*, COUNT(le.competitor_id) AS scraped_entries
        FROM divisions d
        LEFT JOIN leaderboard_entries le
          ON le.year = d.year
         AND le.competition_type = d.competition_type
         AND le.division_id = d.division_id
        GROUP BY d.year, d.competition_type, d.division_id
        ORDER BY d.division_id
        """
    ).fetchall()
    men_35_39 = con.execute(
        """
        SELECT
          COUNT(*) AS entries,
          MIN(overall_rank) AS best_rank,
          MAX(overall_rank) AS worst_rank,
          AVG(age) AS avg_age,
          SUM(country_code = 'CA') AS canada_entries,
          SUM(country_code = 'US') AS us_entries
        FROM leaderboard_entries le
        JOIN athletes a USING (competitor_id)
        WHERE le.year = 2026 AND le.competition_type = 'open' AND le.division_id = 18
        """
    ).fetchone()
    percentile_buckets = con.execute(
        """
        WITH bucketed AS (
          SELECT
            CASE
              WHEN performance_percentile >= 99 THEN '99-100'
              WHEN performance_percentile >= 95 THEN '95-99'
              WHEN performance_percentile >= 90 THEN '90-95'
              WHEN performance_percentile >= 75 THEN '75-90'
              WHEN performance_percentile >= 50 THEN '50-75'
              WHEN performance_percentile >= 25 THEN '25-50'
              ELSE '0-25'
            END AS bucket
          FROM leaderboard_entries
          WHERE year = 2026 AND competition_type = 'open' AND division_id = 18
        )
        SELECT bucket, COUNT(*) AS athletes
        FROM bucketed
        GROUP BY bucket
        ORDER BY
          CASE bucket
            WHEN '99-100' THEN 1
            WHEN '95-99' THEN 2
            WHEN '90-95' THEN 3
            WHEN '75-90' THEN 4
            WHEN '50-75' THEN 5
            WHEN '25-50' THEN 6
            ELSE 7
          END
        """
    ).fetchall()
    top_countries = con.execute(
        """
        SELECT a.country_code, a.country_name, COUNT(*) AS athletes
        FROM leaderboard_entries le
        JOIN athletes a USING (competitor_id)
        WHERE le.year = 2026 AND le.competition_type = 'open' AND le.division_id = 18
        GROUP BY a.country_code, a.country_name
        ORDER BY athletes DESC, a.country_name
        LIMIT 12
        """
    ).fetchall()
    top_90_cutoff = con.execute(
        """
        SELECT MIN(overall_rank) AS min_rank, MAX(overall_rank) AS max_rank, COUNT(*) AS athletes
        FROM leaderboard_entries
        WHERE year = 2026
          AND competition_type = 'open'
          AND division_id = 18
          AND performance_percentile >= 90
        """
    ).fetchone()
    score_cutoffs = con.execute(
        """
        SELECT ordinal, workout_label, MIN(rank) AS best_rank, MAX(rank) AS worst_rank
        FROM workout_scores ws
        JOIN leaderboard_entries le
          ON le.year = ws.year
         AND le.competition_type = ws.competition_type
         AND le.division_id = ws.division_id
         AND le.competitor_id = ws.competitor_id
        WHERE le.year = 2026
          AND le.competition_type = 'open'
          AND le.division_id = 18
          AND le.performance_percentile >= 90
        GROUP BY ordinal, workout_label
        ORDER BY ordinal
        """
    ).fetchall()
    profile_counts = con.execute(
        """
        SELECT
          (SELECT COUNT(*) FROM source_fetches WHERE source_type = 'athlete_profile' AND http_status = 200) AS fetched_profiles,
          (SELECT COUNT(DISTINCT competitor_id) FROM benchmark_stats) AS athletes_with_benchmarks,
          (SELECT COUNT(*) FROM benchmark_stats) AS benchmark_values
        """
    ).fetchone()
    summary = {
        "generated_at": utcnow(),
        "source": {
            "leaderboard_api": "https://c3po.crossfit.com/api/leaderboards/v2/competitions/open/2026/leaderboards",
            "games_robots": "https://games.crossfit.com/robots.txt",
            "athlete_page_example": "https://games.crossfit.com/athlete/911088",
        },
        "divisions": [dict(row) for row in division_rows],
        "men_35_39": dict(men_35_39 or {}),
        "men_35_39_90th_percentile_cutoff": dict(top_90_cutoff or {}),
        "men_35_39_percentile_buckets": [dict(row) for row in percentile_buckets],
        "men_35_39_top_countries": [dict(row) for row in top_countries],
        "men_35_39_top_10_percent_workout_rank_ranges": [dict(row) for row in score_cutoffs],
        "profile_counts": dict(profile_counts or {}),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "men-35-39-percentile-buckets.svg").write_text(
        render_bar_chart(
            "2026 Open Men 35-39 by performance percentile",
            [(row["bucket"], int(row["athletes"])) for row in percentile_buckets],
            width=760,
            height=360,
        ),
        encoding="utf-8",
    )
    (out_dir / "men-35-39-top-countries.svg").write_text(
        render_bar_chart(
            "Top countries in Men 35-39",
            [(row["country_code"] or "??", int(row["athletes"])) for row in top_countries],
            width=760,
            height=420,
        ),
        encoding="utf-8",
    )


def render_bar_chart(title: str, values: list[tuple[str, int]], *, width: int, height: int) -> str:
    margin_left = 120
    margin_right = 24
    margin_top = 58
    margin_bottom = 32
    bar_gap = 10
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    max_value = max((value for _, value in values), default=1)
    bar_height = max(14, (chart_height - bar_gap * max(len(values) - 1, 0)) / max(len(values), 1))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"<title>{html.escape(title)}</title>",
        "<desc>Horizontal bar chart generated from the local SQLite artifact.</desc>",
        '<rect width="100%" height="100%" fill="#f8f8f8"/>',
        f'<text x="{margin_left}" y="30" font-family="Source Sans Pro, Arial, sans-serif" font-size="22" font-weight="700" fill="#222">{html.escape(title)}</text>',
    ]
    for index, (label, value) in enumerate(values):
        y = margin_top + index * (bar_height + bar_gap)
        bar_width = chart_width * (value / max_value)
        parts.append(
            f'<text x="{margin_left - 12}" y="{y + bar_height * 0.68:.1f}" text-anchor="end" '
            'font-family="Source Code Pro, monospace" font-size="13" fill="#333">'
            f"{html.escape(label)}</text>"
        )
        parts.append(
            f'<rect x="{margin_left}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="#330033"/>'
        )
        parts.append(
            f'<text x="{margin_left + bar_width + 8:.1f}" y="{y + bar_height * 0.68:.1f}" '
            'font-family="Source Code Pro, monospace" font-size="13" fill="#333">'
            f"{value:,}</text>"
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def print_summary(con: sqlite3.Connection) -> None:
    for row in con.execute(
        """
        SELECT d.division_id, d.division_name, d.total_pages, d.total_competitors,
               COUNT(le.competitor_id) AS scraped_entries
        FROM divisions d
        LEFT JOIN leaderboard_entries le
          ON le.year = d.year
         AND le.competition_type = d.competition_type
         AND le.division_id = d.division_id
        GROUP BY d.year, d.competition_type, d.division_id
        ORDER BY d.division_id
        """
    ):
        print(
            f"{row['division_id']:>2} {row['division_name']:<14} "
            f"pages={row['total_pages'] or 0:<4} "
            f"competitors={row['total_competitors'] or 0:<7} "
            f"scraped={row['scraped_entries']}"
        )


def parse_divisions(value: str) -> list[int]:
    if value == "all":
        return list(DIVISIONS_2026)
    divisions = []
    for part in value.split(","):
        part = part.strip()
        if part:
            divisions.append(int(part))
    return divisions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--competition-type", default="open")
    sub = parser.add_subparsers(dest="command", required=True)

    discover_parser = sub.add_parser("discover", help="Fetch page 1 for known divisions and record totals.")
    discover_parser.add_argument("--sleep", type=float, default=1.0)
    discover_parser.add_argument("--refresh", action="store_true")

    scrape_parser = sub.add_parser("scrape-leaderboard", help="Fetch and normalize leaderboard pages.")
    scrape_parser.add_argument("--division", default="18", help="Division id, comma list, or all.")
    scrape_parser.add_argument("--sort", type=int, default=0)
    scrape_parser.add_argument("--sleep", type=float, default=1.0)
    scrape_parser.add_argument("--max-pages", type=int)
    scrape_parser.add_argument("--refresh", action="store_true")

    profiles_parser = sub.add_parser("scrape-profiles", help="Fetch athlete pages and parse benchmark stats.")
    profiles_parser.add_argument("--division", type=int, default=18)
    profiles_parser.add_argument("--limit", type=int)
    profiles_parser.add_argument("--sleep", type=float, default=3.0)
    profiles_parser.add_argument("--refresh", action="store_true")

    assets_parser = sub.add_parser("write-summary-assets", help="Write JSON and SVG article assets.")
    assets_parser.add_argument("--out-dir", type=Path, default=Path("data/crossfit-open"))

    sub.add_parser("summary", help="Print division scrape status.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    con = connect(args.db)
    set_metadata(con, "source_robots_txt", "https://games.crossfit.com/robots.txt")
    set_metadata(con, "source_leaderboard_api", "https://c3po.crossfit.com/api/leaderboards/v2/")
    con.commit()

    if args.command == "discover":
        discover(
            con,
            year=args.year,
            competition_type=args.competition_type,
            sleep_seconds=args.sleep,
            refresh=args.refresh,
        )
    elif args.command == "scrape-leaderboard":
        for division_id in parse_divisions(args.division):
            scrape_leaderboard(
                con,
                year=args.year,
                competition_type=args.competition_type,
                division_id=division_id,
                sort=args.sort,
                sleep_seconds=args.sleep,
                max_pages=args.max_pages,
                refresh=args.refresh,
            )
    elif args.command == "scrape-profiles":
        scrape_profiles(
            con,
            year=args.year,
            competition_type=args.competition_type,
            division_id=args.division,
            limit=args.limit,
            sleep_seconds=args.sleep,
            refresh=args.refresh,
        )
    elif args.command == "write-summary-assets":
        write_summary_assets(con, args.out_dir)
    elif args.command == "summary":
        print_summary(con)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
