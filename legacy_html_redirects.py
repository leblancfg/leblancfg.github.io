"""Generate client-side redirects for legacy `.html` article and page URLs."""

import html
import json
from itertools import chain
from pathlib import Path

from pelican import signals


REDIRECT_TEMPLATE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Redirecting…</title>
  <link rel=\"canonical\" href=\"{canonical_url}\">
  <meta http-equiv=\"refresh\" content=\"0; url={redirect_url}\">
  <script>window.location.replace({redirect_url_json});</script>
</head>
<body>
  <p>This page moved to <a href=\"{redirect_url}\">{redirect_url}</a>.</p>
</body>
</html>
"""


def _public_url(content) -> str:
    return f"/{content.url.lstrip('/')}"


def _legacy_save_as(content) -> str | None:
    url = content.url.strip("/")
    if not url or url.endswith(".html"):
        return None

    legacy_save_as = f"{url}.html"
    if legacy_save_as == getattr(content, "save_as", None):
        return None

    return legacy_save_as


def _canonical_url(settings, redirect_url: str) -> str:
    siteurl = settings.get("SITEURL", "").rstrip("/")
    if not siteurl:
        return redirect_url
    return f"{siteurl}{redirect_url}"


def _redirect_html(settings, redirect_url: str) -> str:
    escaped_redirect_url = html.escape(redirect_url, quote=True)
    return REDIRECT_TEMPLATE.format(
        canonical_url=html.escape(_canonical_url(settings, redirect_url), quote=True),
        redirect_url=escaped_redirect_url,
        redirect_url_json=json.dumps(redirect_url),
    )


def _write_redirect(generator, content) -> None:
    legacy_save_as = _legacy_save_as(content)
    if legacy_save_as is None:
        return

    output_path = Path(generator.output_path, legacy_save_as)
    if output_path.exists():
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        _redirect_html(generator.settings, _public_url(content)),
        encoding="utf-8",
    )


def _write_article_redirects(generator, writer) -> None:
    for article in chain(
        generator.translations,
        generator.articles,
        generator.hidden_translations,
        generator.hidden_articles,
    ):
        _write_redirect(generator, article)


def _write_page_redirects(generator, writer) -> None:
    for page in chain(
        generator.translations,
        generator.pages,
        generator.hidden_translations,
        generator.hidden_pages,
    ):
        _write_redirect(generator, page)


def register() -> None:
    signals.article_writer_finalized.connect(_write_article_redirects)
    signals.page_writer_finalized.connect(_write_page_redirects)
