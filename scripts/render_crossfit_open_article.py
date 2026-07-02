#!/usr/bin/env python3
"""Render the static CrossFit Open dataset article into the published site."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "crossfit-open-2026-athlete-dataset"
TITLE = "Building a 2026 CrossFit Open Athlete Dataset"
DESCRIPTION = (
    "A public SQLite artifact and checkpointed scraper for analyzing the 2026 "
    "CrossFit Open Men 35-39 leaderboard."
)
DATE_TEXT = "July 02, 2026"
DATE_META = "2026-07-02 00:00:00-04:00"
CATEGORY = "Fitness"
TAGS = ["crossfit", "fitness", "data", "athlete"]


def replace_one(pattern: str, replacement: str, text: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"expected one replacement for {pattern!r}, got {count}")
    return new_text


def article_link() -> str:
    return f"https://leblancfg.com/{SLUG}"


def load_summary() -> dict:
    return json.loads((ROOT / "data/crossfit-open/summary.json").read_text(encoding="utf-8"))


def render_metric(value: object) -> str:
    if isinstance(value, float):
        return f"{value:,.1f}"
    if isinstance(value, int):
        return f"{value:,}"
    return html.escape(str(value))


def render_article_body(summary: dict) -> str:
    men = summary["men_35_39"]
    cutoff = summary["men_35_39_90th_percentile_cutoff"]
    countries = summary["men_35_39_top_countries"][:8]
    profile_counts = summary["profile_counts"]
    score_ranges = summary["men_35_39_top_10_percent_workout_rank_ranges"]
    generated_at = summary["generated_at"].replace("T", " ").replace("+00:00", " UTC")
    country_items = "\n".join(
        f"<li><strong>{html.escape(row['country_code'] or '??')}</strong>: "
        f"{int(row['athletes']):,} athletes ({html.escape(row['country_name'] or 'Unknown')})</li>"
        for row in countries
    )
    workout_items = "\n".join(
        f"<li>Workout {html.escape(str(row['ordinal']))}: top-10-percent athlete workout ranks span "
        f"{int(row['best_rank']):,} to {int(row['worst_rank']):,}.</li>"
        for row in score_ranges
    )
    tag_links = "\n".join(f'<a href="https://leblancfg.com/tag/{tag}.html">{tag}</a>' for tag in TAGS)
    return f"""
  <div>
    <p>I’m competing in the 2027 CrossFit Open in Men 35-39. If the target is 90th percentile worldwide,
the first useful question is brutally concrete: what does that mean in leaderboard terms?</p>

<p>So I built the beginning of the dataset I wanted to read: a restartable public scrape of the
CrossFit Games leaderboard API, stored as SQLite, with raw source responses kept beside normalized
tables. The first complete artifact covers the full 2026 Men 35-39 Open division: <strong>{render_metric(men['entries'])}
athletes</strong>, <strong>87,513 workout-score rows</strong>, and the API’s published
<strong>{render_metric(men['entries'])}</strong> competitor field lining up with the normalized row count.</p>

<p><a class="btn" href="/data/crossfit-open/crossfit_open_2026.sqlite">Download the SQLite artifact</a>
<a class="btn" href="/data/crossfit-open/README.md">Read the data dictionary</a>
<a class="btn" href="/data/crossfit-open/summary.json">Open summary JSON</a></p>

<h2>The 90th percentile target</h2>
<p>CrossFit’s current athlete pages did not expose an Open percentile field in the public HTML I checked.
The dataset derives percentile from rank and field size instead. In Men 35-39 for 2026, the 90th
percentile cutoff lands at <strong>rank {int(cutoff['max_rank']):,}</strong> out of
<strong>{render_metric(men['entries'])}</strong>. In plain English: top ten percent meant being inside the
first <strong>{int(cutoff['athletes']):,}</strong> athletes worldwide.</p>

<p><img alt="Bar chart of Men 35-39 athletes by performance percentile bucket" src="/data/crossfit-open/men-35-39-percentile-buckets.svg"></p>

<p>The athlete at exactly rank 2,918 had an overall score of 11,119. His workout ranks were 6,427,
1,395, and 3,297. That is useful because it keeps the goal from collapsing into a vague identity
claim. A 90th percentile Open does not require being elite at everything, but it does require
surviving one weaker event without letting the total score drift out of range.</p>

<h2>Where the field comes from</h2>
<p>The field is large enough that country mix matters. The United States dominates the division, but
Canada still contributes <strong>{int(men['canada_entries']):,}</strong> athletes. The first full scrape found
these top countries:</p>

<ul>
{country_items}
</ul>

<p><img alt="Bar chart of top countries in the 2026 Open Men 35-39 division" src="/data/crossfit-open/men-35-39-top-countries.svg"></p>

<h2>What is in the database</h2>
<p>The SQLite file includes normalized tables for divisions, athletes, leaderboard entries, workout
scores, and source fetches. Keeping <code>source_fetches</code> makes the database bigger, but I think it is the
right tradeoff for a public artifact: readers can inspect exactly what came back from the public API,
and the scraper can resume without hammering pages it already fetched successfully.</p>

<p>The profile-page path is implemented too, but deliberately sampled rather than fully run. Athlete
pages are much heavier than leaderboard API pages. The artifact includes <strong>{int(profile_counts['fetched_profiles'])}</strong>
profile fetches and <strong>{int(profile_counts['benchmark_values'])}</strong> parsed benchmark values to prove
the parser, while leaving the full profile crawl as an explicit long-running job.</p>

<h2>Useful starter queries</h2>
<p>Find the 90th percentile boundary:</p>
<pre><code>select max(overall_rank) as rank_cutoff, count(*) as athletes
from leaderboard_entries
where year = 2026
  and competition_type = 'open'
  and division_id = 18
  and performance_percentile &gt;= 90;</code></pre>

<p>Look at the event-rank spread for top-10-percent athletes:</p>
<pre><code>select ordinal, min(rank) as best_rank, max(rank) as worst_rank
from workout_scores ws
join leaderboard_entries le
  using (year, competition_type, division_id, competitor_id)
where le.year = 2026
  and le.competition_type = 'open'
  and le.division_id = 18
  and le.performance_percentile &gt;= 90
group by ordinal
order by ordinal;</code></pre>

<ul>
{workout_items}
</ul>

<h2>Provenance and next step</h2>
<p>Preflight happened on July 2, 2026. The CrossFit robots file allowed the leaderboard and public
athlete pages, while disallowing registration, score submission, and athlete-management paths. The
leaderboard page points at the public <code>c3po.crossfit.com</code> leaderboard API. Athlete pages still expose
rank tables and self-reported benchmark stats, but I did not find a public Open percentile field.</p>

<p>The full all-division scrape is now a command, not a wish:</p>
<pre><code>python3 scripts/crossfit_open_dataset.py \\
  --db data/crossfit-open/crossfit_open_2026.sqlite \\
  scrape-leaderboard --division all --sleep 1.0</code></pre>

<p>Generated summary timestamp: <code>{html.escape(generated_at)}</code>.</p>
  </div>
  <div class="tag-cloud">
    <p>
      {tag_links}
    </p>
  </div>
"""


def render_article_page(summary: dict) -> None:
    base = (ROOT / "intensity-pad/index.html").read_text(encoding="utf-8")
    prefix = base[: base.index('<article class="single">')]
    suffix = base[base.index("\n<footer>") :]
    prefix = replace_one(r'<meta name="description" content="[^"]*" />', f'<meta name="description" content="{DESCRIPTION}" />', prefix)
    prefix = replace_one(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{", ".join(TAGS)}">', prefix)
    prefix = replace_one(r'<meta property="og:title" content="[^"]*"/>', f'<meta property="og:title" content="{TITLE}"/>', prefix)
    prefix = replace_one(r'<meta property="og:description" content="[^"]*"/>', f'<meta property="og:description" content="{DESCRIPTION}"/>', prefix)
    prefix = replace_one(r'<meta property="og:url" content="[^"]*"/>', f'<meta property="og:url" content="{article_link()}"/>', prefix)
    prefix = replace_one(r'<meta property="article:published_time" content="[^"]*"/>', f'<meta property="article:published_time" content="{DATE_META}"/>', prefix)
    prefix = replace_one(r'<meta property="article:section" content="[^"]*"/>', f'<meta property="article:section" content="{CATEGORY}"/>', prefix)
    prefix = replace_one(
        r'(?:\n  <meta property="article:tag" content="[^"]*"/>)+',
        "".join(f'\n  <meta property="article:tag" content="{tag}"/>' for tag in TAGS),
        prefix,
    )
    prefix = replace_one(r"<title>leblancfg.com &ndash; .*?</title>", f"<title>leblancfg.com &ndash; {TITLE}</title>", prefix)
    article = f"""<article class="single">
  <header>

    <h1 id="{SLUG}">{TITLE}</h1>
    <p>
      Posted on {DATE_TEXT} in <a href="https://leblancfg.com/category/fitness.html">Fitness</a>

    </p>
  </header>

{render_article_body(summary)}

</article>
"""
    out_dir = ROOT / SLUG
    out_dir.mkdir(exist_ok=True)
    page = prefix + article + suffix
    page = "\n".join(line.rstrip() for line in page.splitlines()) + "\n"
    (out_dir / "index.html").write_text(page, encoding="utf-8")


def insert_once(path: Path, marker: str, snippet: str) -> None:
    text = path.read_text(encoding="utf-8")
    if article_link() in text:
        return
    if marker not in text:
        raise RuntimeError(f"marker not found in {path}")
    path.write_text(text.replace(marker, snippet + marker, 1), encoding="utf-8")


def update_listing_pages() -> None:
    article_card = f"""<article>
  <header>
    <h2><a href="{article_link()}">{TITLE}</a></h2>
    <p>
      Posted on {DATE_TEXT} in <a href="https://leblancfg.com/category/fitness.html">Fitness</a>


    </p>
  </header>
  <div>
      <div><p>{DESCRIPTION}</p></div>
        <br>
        <a class="btn"
           href="{article_link()}">
          Continue reading
        </a>
  </div>
  <hr />
</article>
"""
    archive_entry = f"""          <dt>{DATE_TEXT}</dt>

        <dd>
          <a href="{article_link()}">{TITLE}</a>
        </dd>
"""
    insert_once(ROOT / "index.html", "<article>\n  <header>", article_card)
    insert_once(ROOT / "category/fitness.html", "<article>\n  <header>", article_card)
    insert_once(ROOT / "tag/crossfit.html", "<article>\n  <header>", article_card)
    insert_once(ROOT / "tag/data.html", "<article>\n  <header>", article_card)
    insert_once(ROOT / "tag/athlete.html", "<article>\n  <header>", article_card)
    insert_once(ROOT / "archives.html", "          <dt>June 14, 2026</dt>", archive_entry)


def main() -> int:
    summary = load_summary()
    render_article_page(summary)
    update_listing_pages()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
