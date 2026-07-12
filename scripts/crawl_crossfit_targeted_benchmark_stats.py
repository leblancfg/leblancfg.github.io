#!/usr/bin/env python3
"""Fetch public CrossFit profile benchmarks around selected leaderboard cutoffs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup

LB_TO_KG = 0.45359237
PROFILE_URL = "https://games.crossfit.com/athlete/{athlete_id}"


@dataclass(frozen=True)
class TargetAthlete:
    athlete_id: str
    division_id: str
    division_name: str
    target_percentile: int
    overall_rank: int
    performance_percentile: float
    window_start_rank: int
    window_end_rank: int


def int_or_none(value: str | None) -> int | None:
    return int(value) if value not in (None, "") else None


def float_or_none(value: str | None) -> float | None:
    return float(value) if value not in (None, "") else None


def parse_time_seconds(raw_value: str) -> int | None:
    value = raw_value.strip()
    if not re.fullmatch(r"\d{1,2}:\d{2}(?::\d{2})?", value):
        return None
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    hours, minutes, seconds = parts
    return hours * 3600 + minutes * 60 + seconds


def parse_numeric_unit(raw_value: str) -> tuple[float | None, str]:
    value = " ".join(raw_value.split())
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)?", value)
    if not match:
        return None, ""
    number = float(match.group(1))
    unit = (match.group(2) or "").lower()
    return number, unit


def value_kg(number: float | None, unit: str) -> float | None:
    if number is None:
        return None
    if unit == "kg":
        return round(number, 1)
    if unit in {"lb", "lbs"}:
        return round(number * LB_TO_KG, 1)
    return None


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def target_cutoff_rank(entries: list[dict[str, str]], percentile: int) -> int:
    eligible = [
        row
        for row in entries
        if float_or_none(row["performance_percentile"]) is not None
        and float(row["performance_percentile"]) >= percentile
    ]
    return max(int(row["overall_rank"]) for row in eligible if row["overall_rank"])


def select_targets(
    data_dir: Path,
    division_names: set[str],
    percentiles: tuple[int, ...],
    half_window: int,
) -> list[TargetAthlete]:
    divisions = {
        row["division_id"]: row
        for row in load_csv(data_dir / "divisions.csv")
        if row["division_name"] in division_names
    }
    entries_by_division: dict[str, list[dict[str, str]]] = {division_id: [] for division_id in divisions}
    for row in load_csv(data_dir / "leaderboard_entries.csv"):
        if row["division_id"] in entries_by_division and row["overall_rank"]:
            entries_by_division[row["division_id"]].append(row)

    targets: dict[tuple[str, str, int], TargetAthlete] = {}
    for division_id, rows in entries_by_division.items():
        rows_by_rank = {int(row["overall_rank"]): row for row in rows}
        max_rank = max(rows_by_rank)
        for percentile in percentiles:
            cutoff = target_cutoff_rank(rows, percentile)
            start = max(1, cutoff - half_window)
            end = min(max_rank, cutoff + half_window)
            for rank in range(start, end + 1):
                row = rows_by_rank.get(rank)
                if not row:
                    continue
                athlete_id = row["athlete_id"]
                targets[(athlete_id, division_id, percentile)] = TargetAthlete(
                    athlete_id=athlete_id,
                    division_id=division_id,
                    division_name=divisions[division_id]["division_name"],
                    target_percentile=percentile,
                    overall_rank=rank,
                    performance_percentile=float(row["performance_percentile"]),
                    window_start_rank=start,
                    window_end_rank=end,
                )
    return sorted(targets.values(), key=lambda item: (item.division_name, item.target_percentile, item.overall_rank))


def cache_path(cache_dir: Path, athlete_id: str) -> Path:
    digest = hashlib.sha256(athlete_id.encode("utf-8")).hexdigest()[:16]
    return cache_dir / f"{athlete_id}-{digest}.html"


def fetch_profile(athlete_id: str, cache_dir: Path, timeout: int = 20) -> tuple[str, str, int, str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_path(cache_dir, athlete_id)
    url = PROFILE_URL.format(athlete_id=athlete_id)
    if path.exists():
        return athlete_id, path.read_text(encoding="utf-8", errors="replace"), 200, "cache"
    response = requests.get(
        url,
        headers={"User-Agent": "leblancfg-crossfit-open-research/1.0"},
        timeout=timeout,
    )
    response.raise_for_status()
    path.write_text(response.text, encoding="utf-8")
    time.sleep(0.05)
    return athlete_id, response.text, response.status_code, "network"


def parse_benchmark_stats(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one("#benchmarkStats")
    if container is None:
        return []
    rows = []
    for tr in container.select("tr"):
        header = tr.select_one("th.stats-header")
        value_cell = tr.select_one("td")
        if header is None or value_cell is None:
            continue
        stat_name = " ".join(header.stripped_strings)
        raw_value = " ".join(value_cell.stripped_strings)
        if not stat_name or not raw_value or raw_value == "--":
            continue
        number, unit = parse_numeric_unit(raw_value)
        rows.append(
            {
                "stat_name": stat_name,
                "raw_value": raw_value,
                "value": "" if number is None else f"{number:g}",
                "unit": unit,
                "value_kg": "" if value_kg(number, unit) is None else f"{value_kg(number, unit):.1f}",
                "time_seconds": "" if parse_time_seconds(raw_value) is None else str(parse_time_seconds(raw_value)),
            }
        )
    return rows


def crawl_profiles(targets: Iterable[TargetAthlete], cache_dir: Path, workers: int) -> dict[str, tuple[str, int, str]]:
    athlete_ids = sorted({target.athlete_id for target in targets}, key=lambda value: int(value) if value.isdigit() else value)
    results: dict[str, tuple[str, int, str]] = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_by_id = {executor.submit(fetch_profile, athlete_id, cache_dir): athlete_id for athlete_id in athlete_ids}
        for index, future in enumerate(as_completed(future_by_id), start=1):
            athlete_id = future_by_id[future]
            try:
                _, html, status, source = future.result()
                results[athlete_id] = (html, status, source)
            except Exception as exc:  # noqa: BLE001 - report crawl failures in output CSV by omission.
                print(f"failed {athlete_id}: {exc}")
            if index % 50 == 0:
                print(f"fetched {index}/{len(athlete_ids)} profiles")
    return results


def write_targeted_stats(targets: list[TargetAthlete], profile_html: dict[str, tuple[str, int, str]], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "athlete_id",
        "division_id",
        "division_name",
        "target_percentile",
        "overall_rank",
        "performance_percentile",
        "window_start_rank",
        "window_end_rank",
        "http_status",
        "fetch_source",
        "stat_name",
        "raw_value",
        "value",
        "unit",
        "value_kg",
        "time_seconds",
        "parsed_at",
    ]
    parsed_at = datetime.now(timezone.utc).isoformat()
    count = 0
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for target in targets:
            html, status, source = profile_html.get(target.athlete_id, ("", 0, "missing"))
            for stat in parse_benchmark_stats(html):
                writer.writerow(
                    {
                        "athlete_id": target.athlete_id,
                        "division_id": target.division_id,
                        "division_name": target.division_name,
                        "target_percentile": target.target_percentile,
                        "overall_rank": target.overall_rank,
                        "performance_percentile": f"{target.performance_percentile:.4f}",
                        "window_start_rank": target.window_start_rank,
                        "window_end_rank": target.window_end_rank,
                        "http_status": status,
                        "fetch_source": source,
                        "parsed_at": parsed_at,
                        **stat,
                    }
                )
                count += 1
    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path.home() / ".cache/leblancfg/crossfit-open-2026-compact-v1/crossfit-open-2026-compact-v1")
    parser.add_argument("--output", type=Path, default=Path("content/data/crossfit_open_2026_targeted_benchmark_stats.csv"))
    parser.add_argument("--cache-dir", type=Path, default=Path.home() / ".cache/crossfit-open/targeted-profile-html")
    parser.add_argument("--half-window", type=int, default=15)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--divisions", nargs="+", default=["Men", "Women", "Men 35-39", "Women 35-39", "Men 40-44", "Women 40-44"])
    parser.add_argument("--percentiles", nargs="+", type=int, default=[90, 95, 99])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    targets = select_targets(args.data_dir, set(args.divisions), tuple(args.percentiles), args.half_window)
    print(f"selected {len(targets)} division-percentile target rows for {len({target.athlete_id for target in targets})} unique athletes")
    profile_html = crawl_profiles(targets, args.cache_dir, args.workers)
    rows = write_targeted_stats(targets, profile_html, args.output)
    print(f"wrote {rows} benchmark rows to {args.output}")


if __name__ == "__main__":
    main()
