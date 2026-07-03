#!/usr/bin/env python3
"""Export a compact 2026 CrossFit Open dataset from the crawl checkpoint.

The checkpoint database keeps raw API responses so the crawler can resume.
This exporter deliberately excludes those source bodies and emits the smaller
normalized tables that are useful for article analysis and reuse.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import sqlite3
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_DB = Path.home() / ".cache/crossfit-open/crossfit_open_2026_checkpoint.sqlite"
DEFAULT_OUT_DIR = Path("dist/crossfit-open-2026-compact-v1")
DEFAULT_ARCHIVE = Path("dist/crossfit-open-2026-compact-v1.tar.gz")
DATASET_VERSION = "v1"
DATASET_NAME = "crossfit-open-2026-compact"
RELEASE_TAG = "crossfit-open-2026-compact-v1"

LB_TO_KG = 0.45359237
IN_TO_CM = 2.54


@dataclass(frozen=True)
class CsvTable:
    name: str
    columns: tuple[str, ...]
    description: str


TABLES = (
    CsvTable(
        "divisions.csv",
        (
            "year",
            "competition_type",
            "division_id",
            "division_name",
            "category",
            "sex",
            "total_pages",
            "total_competitors",
            "leaderboard_entries",
            "discovered_at",
        ),
        "CrossFit Open leaderboard divisions included in the 2026 crawl.",
    ),
    CsvTable(
        "athletes.csv",
        (
            "athlete_id",
            "athlete_name",
            "first_name",
            "last_name",
            "sex",
            "country_code",
            "country_name",
            "region_id",
            "region_name",
            "affiliate_id",
            "affiliate_name",
            "age",
            "height_cm",
            "weight_kg",
            "status",
        ),
        "Unique athletes and public profile fields seen in the crawled leaderboards.",
    ),
    CsvTable(
        "leaderboard_entries.csv",
        (
            "year",
            "competition_type",
            "division_id",
            "athlete_id",
            "overall_rank",
            "overall_score",
            "rank_fraction",
            "performance_percentile",
            "next_stage",
            "scaled",
            "source_page",
        ),
        "One row per athlete per division leaderboard entry.",
    ),
    CsvTable(
        "workout_scores.csv",
        (
            "year",
            "competition_type",
            "division_id",
            "athlete_id",
            "workout_ordinal",
            "workout_label",
            "workout_rank",
            "score_display",
            "score_reps",
            "score_time_seconds",
            "valid",
            "scaled",
            "breakdown",
        ),
        "One row per athlete workout score, with display score and parseable reps/time fields.",
    ),
    CsvTable(
        "sample_benchmark_stats.csv",
        (
            "athlete_id",
            "stat_name",
            "raw_value",
            "value",
            "unit",
            "value_kg",
            "time_seconds",
            "parsed_at",
        ),
        "Small sampled proof-of-parser table from public athlete profile benchmark stats.",
    ),
)


def utcnow() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def clean_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def clean_float(value: Any, *, digits: int | None = None) -> float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if digits is not None:
        parsed = round(parsed, digits)
    return parsed


def format_float(value: Any, digits: int) -> str | None:
    parsed = clean_float(value)
    if parsed is None:
        return None
    return f"{parsed:.{digits}f}"


def normalize_measure(raw: Any, *, kind: str) -> float | None:
    text = clean_text(raw)
    if not text or text == "--":
        return None
    match = re.match(r"^(-?\d+(?:\.\d+)?)\s*([A-Za-z]+)$", text)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).lower()
    if kind == "height":
        if unit == "cm":
            return round(value, 1)
        if unit in {"in", "inch", "inches"}:
            return round(value * IN_TO_CM, 1)
    if kind == "weight":
        if unit == "kg":
            return round(value, 1)
        if unit in {"lb", "lbs", "pound", "pounds"}:
            return round(value * LB_TO_KG, 1)
    return None


def parse_reps(score_display: Any, breakdown: Any) -> int | None:
    text = clean_text(score_display)
    if text:
        match = re.match(r"^(\d[\d,]*)\s+reps?$", text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1).replace(",", ""))
    detail = clean_text(breakdown)
    if detail:
        match = re.search(r"^(\d[\d,]*)\s+reps?$", detail, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return int(match.group(1).replace(",", ""))
    return None


def parse_time_seconds(raw: Any) -> int | None:
    text = clean_text(raw)
    if not text:
        return None
    match = re.match(r"^(?:(\d+):)?(\d{1,2}):(\d{2})$", text)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        return hours * 3600 + minutes * 60 + seconds
    match = re.match(r"^(\d{1,2}):(\d{2})$", text)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))
    return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def connect(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(path)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def write_csv(path: Path, columns: tuple[str, ...], rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})
            count += 1
    return count


def table_count(con: sqlite3.Connection, table: str) -> int:
    return int(con.execute(f'select count(*) from "{table}"').fetchone()[0])


def export_divisions(con: sqlite3.Connection, out_dir: Path) -> int:
    rows = []
    for row in con.execute(
        """
        select
          d.year,
          d.competition_type,
          d.division_id,
          d.division_name,
          d.category,
          nullif(d.gender, '') as sex,
          d.total_pages,
          d.total_competitors,
          count(le.competitor_id) as leaderboard_entries,
          d.discovered_at
        from divisions d
        left join leaderboard_entries le
          using (year, competition_type, division_id)
        group by d.year, d.competition_type, d.division_id
        order by d.division_id
        """
    ):
        rows.append(dict(row))
    return write_csv(out_dir / "divisions.csv", TABLES[0].columns, rows)


def export_athletes(con: sqlite3.Connection, out_dir: Path) -> int:
    def rows() -> Iterable[dict[str, Any]]:
        for row in con.execute(
            """
            select
              competitor_id,
              competitor_name,
              first_name,
              last_name,
              gender,
              country_code,
              country_name,
              region_id,
              region_name,
              affiliate_id,
              affiliate_name,
              age,
              height_raw,
              weight_raw,
              status
            from athletes
            order by cast(competitor_id as integer)
            """
        ):
            yield {
                "athlete_id": clean_text(row["competitor_id"]),
                "athlete_name": clean_text(row["competitor_name"]),
                "first_name": clean_text(row["first_name"]),
                "last_name": clean_text(row["last_name"]),
                "sex": clean_text(row["gender"]),
                "country_code": clean_text(row["country_code"]),
                "country_name": clean_text(row["country_name"]),
                "region_id": clean_text(row["region_id"]),
                "region_name": clean_text(row["region_name"]),
                "affiliate_id": clean_text(row["affiliate_id"]),
                "affiliate_name": clean_text(row["affiliate_name"]),
                "age": clean_int(row["age"]),
                "height_cm": normalize_measure(row["height_raw"], kind="height"),
                "weight_kg": normalize_measure(row["weight_raw"], kind="weight"),
                "status": clean_text(row["status"]),
            }

    return write_csv(out_dir / "athletes.csv", TABLES[1].columns, rows())


def export_leaderboard_entries(con: sqlite3.Connection, out_dir: Path) -> int:
    def rows() -> Iterable[dict[str, Any]]:
        for row in con.execute(
            """
            select
              year,
              competition_type,
              division_id,
              competitor_id,
              overall_rank,
              overall_score,
              rank_fraction,
              performance_percentile,
              next_stage,
              scaled,
              source_page
            from leaderboard_entries
            order by division_id, overall_rank, cast(competitor_id as integer)
            """
        ):
            yield {
                "year": clean_int(row["year"]),
                "competition_type": clean_text(row["competition_type"]),
                "division_id": clean_int(row["division_id"]),
                "athlete_id": clean_text(row["competitor_id"]),
                "overall_rank": clean_int(row["overall_rank"]),
                "overall_score": clean_text(row["overall_score"]),
                "rank_fraction": format_float(row["rank_fraction"], 8),
                "performance_percentile": format_float(row["performance_percentile"], 4),
                "next_stage": clean_text(row["next_stage"]),
                "scaled": clean_int(row["scaled"]),
                "source_page": clean_int(row["source_page"]),
            }

    return write_csv(out_dir / "leaderboard_entries.csv", TABLES[2].columns, rows())


def export_workout_scores(con: sqlite3.Connection, out_dir: Path) -> int:
    def rows() -> Iterable[dict[str, Any]]:
        for row in con.execute(
            """
            select
              year,
              competition_type,
              division_id,
              competitor_id,
              ordinal,
              workout_label,
              rank,
              score_display,
              time_seconds,
              valid,
              scaled,
              breakdown
            from workout_scores
            order by division_id, cast(competitor_id as integer), ordinal
            """
        ):
            score_time_seconds = clean_int(row["time_seconds"])
            if score_time_seconds is None:
                score_time_seconds = parse_time_seconds(row["score_display"])
            yield {
                "year": clean_int(row["year"]),
                "competition_type": clean_text(row["competition_type"]),
                "division_id": clean_int(row["division_id"]),
                "athlete_id": clean_text(row["competitor_id"]),
                "workout_ordinal": clean_int(row["ordinal"]),
                "workout_label": clean_text(row["workout_label"]),
                "workout_rank": clean_int(row["rank"]),
                "score_display": clean_text(row["score_display"]),
                "score_reps": parse_reps(row["score_display"], row["breakdown"]),
                "score_time_seconds": score_time_seconds,
                "valid": clean_int(row["valid"]),
                "scaled": clean_int(row["scaled"]),
                "breakdown": clean_text(row["breakdown"]),
            }

    return write_csv(out_dir / "workout_scores.csv", TABLES[3].columns, rows())


def export_sample_benchmark_stats(con: sqlite3.Connection, out_dir: Path) -> int:
    def rows() -> Iterable[dict[str, Any]]:
        for row in con.execute(
            """
            select
              competitor_id,
              stat_name,
              raw_value,
              numeric_value,
              unit,
              parsed_at
            from benchmark_stats
            order by cast(competitor_id as integer), stat_name
            """
        ):
            unit = clean_text(row["unit"])
            value = clean_float(row["numeric_value"], digits=4)
            value_kg = None
            if value is not None and unit:
                if unit.lower() == "kg":
                    value_kg = round(value, 1)
                elif unit.lower() in {"lb", "lbs"}:
                    value_kg = round(value * LB_TO_KG, 1)
            yield {
                "athlete_id": clean_text(row["competitor_id"]),
                "stat_name": clean_text(row["stat_name"]),
                "raw_value": clean_text(row["raw_value"]),
                "value": value,
                "unit": unit,
                "value_kg": value_kg,
                "time_seconds": parse_time_seconds(row["raw_value"]),
                "parsed_at": clean_text(row["parsed_at"]),
            }

    return write_csv(out_dir / "sample_benchmark_stats.csv", TABLES[4].columns, rows())


def build_metadata(con: sqlite3.Connection, row_counts: dict[str, int]) -> dict[str, Any]:
    source_metadata = {
        row["key"]: row["value"]
        for row in con.execute("select key, value from metadata order by key")
    }
    source_counts = {
        table: table_count(con, table)
        for table in (
            "divisions",
            "athletes",
            "leaderboard_entries",
            "workout_scores",
            "benchmark_stats",
        )
    }
    source_counts["source_fetches_excluded"] = table_count(con, "source_fetches")
    source_counts["unique_athletes_in_leaderboards"] = int(
        con.execute("select count(distinct competitor_id) from leaderboard_entries").fetchone()[0]
    )
    division_counts = [
        dict(row)
        for row in con.execute(
            """
            select
              d.division_id,
              d.division_name,
              d.category,
              nullif(d.gender, '') as sex,
              d.total_competitors,
              count(le.competitor_id) as leaderboard_entries
            from divisions d
            left join leaderboard_entries le
              using (year, competition_type, division_id)
            group by d.year, d.competition_type, d.division_id
            order by d.division_id
            """
        )
    ]
    return {
        "dataset": DATASET_NAME,
        "version": DATASET_VERSION,
        "release_tag": RELEASE_TAG,
        "generated_at": utcnow(),
        "year": 2026,
        "competition_type": "open",
        "source": {
            "checkpoint": "crossfit_open_2026_checkpoint.sqlite (local checkpoint; not included)",
            "leaderboard_api": source_metadata.get("source_leaderboard_api"),
            "robots_txt": source_metadata.get("source_robots_txt"),
            "checkpoint_generated_by": source_metadata.get("generated_by"),
            "checkpoint_schema_version": source_metadata.get("schema_version"),
        },
        "normalization": {
            "raw_api_bodies": "excluded",
            "height": "height_raw converted to height_cm; inches multiplied by 2.54; rounded to 0.1 cm",
            "weight": "weight_raw converted to weight_kg; pounds multiplied by 0.45359237; rounded to 0.1 kg",
            "percentiles": "rank-derived performance_percentile rounded to 4 decimals",
            "workout_scores": "score_display retained; score_reps and score_time_seconds populated when parseable",
        },
        "source_counts": source_counts,
        "exported_row_counts": row_counts,
        "division_counts": division_counts,
        "files": [table.name for table in TABLES] + ["metadata.json", "schema.json"],
    }


def build_schema() -> dict[str, Any]:
    return {
        "dataset": DATASET_NAME,
        "version": DATASET_VERSION,
        "tables": {
            table.name: {
                "description": table.description,
                "columns": list(table.columns),
            }
            for table in TABLES
        },
        "notes": [
            "Athletes can appear in multiple divisions; leaderboard_entries is the division-specific table.",
            "Percentile is derived from rank and division field size rather than copied from athlete profile pages.",
            "The raw source_fetches table from the checkpoint SQLite is intentionally absent from this compact release.",
        ],
    }


def make_archive(out_dir: Path, archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, "w:gz") as tar:
        for path in sorted(out_dir.rglob("*")):
            tar.add(path, arcname=str(Path(out_dir.name) / path.relative_to(out_dir)))


def write_sha256s(archive_path: Path) -> Path:
    sha_path = archive_path.parent / "SHA256SUMS"
    sha_path.write_text(f"{sha256_file(archive_path)}  {archive_path.name}\n", encoding="utf-8")
    return sha_path


def write_release_notes(out_dir: Path, archive_path: Path, sha_path: Path, metadata: dict[str, Any]) -> Path:
    sha = sha_path.read_text(encoding="utf-8").split()[0]
    notes = out_dir.parent / f"{RELEASE_TAG}-notes.md"
    counts = metadata["exported_row_counts"]
    notes.write_text(
        "\n".join(
            [
                "# CrossFit Open 2026 Compact Dataset v1",
                "",
                "Compact normalized export from the 2026 CrossFit Open all-division leaderboard crawl.",
                "",
                "## Assets",
                "",
                f"- `{archive_path.name}`: normalized CSV dataset, metadata, and schema",
                f"- `{sha_path.name}`: SHA-256 checksum file",
                "",
                "## Contents",
                "",
                f"- Divisions: {counts['divisions.csv']:,}",
                f"- Athletes: {counts['athletes.csv']:,}",
                f"- Leaderboard entries: {counts['leaderboard_entries.csv']:,}",
                f"- Workout scores: {counts['workout_scores.csv']:,}",
                f"- Sample benchmark stats: {counts['sample_benchmark_stats.csv']:,}",
                "",
                "The release excludes raw API response bodies and the checkpoint SQLite database.",
                "",
                "## Verification",
                "",
                "```bash",
                "sha256sum -c SHA256SUMS",
                "```",
                "",
                f"`{archive_path.name}` SHA-256: `{sha}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return notes


def export_dataset(db_path: Path, out_dir: Path, archive_path: Path) -> dict[str, Any]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    con = connect(db_path)
    row_counts = {
        "divisions.csv": export_divisions(con, out_dir),
        "athletes.csv": export_athletes(con, out_dir),
        "leaderboard_entries.csv": export_leaderboard_entries(con, out_dir),
        "workout_scores.csv": export_workout_scores(con, out_dir),
        "sample_benchmark_stats.csv": export_sample_benchmark_stats(con, out_dir),
    }
    metadata = build_metadata(con, row_counts)
    metadata["source"]["checkpoint"] = f"{db_path.name} (local checkpoint; not included)"
    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "schema.json").write_text(
        json.dumps(build_schema(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    make_archive(out_dir, archive_path)
    sha_path = write_sha256s(archive_path)
    notes_path = write_release_notes(out_dir, archive_path, sha_path, metadata)
    metadata["archive"] = {
        "path": str(archive_path),
        "sha256": sha256_file(archive_path),
        "sha256s_path": str(sha_path),
        "release_notes_path": str(notes_path),
    }
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Checkpoint SQLite database")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Export directory")
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE, help="Output tar.gz path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metadata = export_dataset(args.db, args.out_dir, args.archive)
    print(json.dumps(metadata["exported_row_counts"], indent=2))
    print(f"archive={metadata['archive']['path']}")
    print(f"sha256={metadata['archive']['sha256']}")
    print(f"sha256s={metadata['archive']['sha256s_path']}")
    print(f"release_notes={metadata['archive']['release_notes_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
