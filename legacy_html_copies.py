"""Write duplicate pages for legacy `.html` article and page URLs."""

import shutil
from itertools import chain
from pathlib import Path

from pelican import signals


def _legacy_save_as(content) -> str | None:
    url = content.url.strip("/")
    if not url or url.endswith(".html"):
        return None

    legacy_save_as = f"{url}.html"
    if legacy_save_as == getattr(content, "save_as", None):
        return None

    return legacy_save_as


def _write_legacy_copy(generator, content) -> None:
    legacy_save_as = _legacy_save_as(content)
    if legacy_save_as is None:
        return

    source_path = Path(generator.output_path, content.save_as)
    output_path = Path(generator.output_path, legacy_save_as)

    if not source_path.is_file():
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, output_path)


def _write_article_copies(generator, writer) -> None:
    for article in chain(
        generator.translations,
        generator.articles,
        generator.hidden_translations,
        generator.hidden_articles,
    ):
        _write_legacy_copy(generator, article)


def _write_page_copies(generator, writer) -> None:
    for page in chain(
        generator.translations,
        generator.pages,
        generator.hidden_translations,
        generator.hidden_pages,
    ):
        _write_legacy_copy(generator, page)


def register() -> None:
    signals.article_writer_finalized.connect(_write_article_copies)
    signals.page_writer_finalized.connect(_write_page_copies)
