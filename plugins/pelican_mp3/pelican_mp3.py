import logging
from pathlib import Path
from datetime import datetime
from typing import Any, ClassVar

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TXXX  # type: ignore
from pelican import signals  # , contents
from pelican.readers import BaseReader
from jinja2 import Environment, BaseLoader

logger = logging.getLogger(__name__)

template = """
# {{ title }}

Artist: {{ artist }}
Album: {{ album }}
{% if cover %}
<img src="{{ cover }}" alt="Cover Image">
{% endif %}

<audio controls>
    <source src="{{ mp3_path }}" type="audio/mpeg">
    Your browser does not support the audio element.
</audio>

## Additional Metadata
<ul>
    {% for key, value in extra_metadata.items() %}
    <li>{{ key }}: {{ value }}</li>
    {% endfor %}
</ul>
"""


class MP3Reader(BaseReader):
    """A Pelican reader for MP3 files."""

    enabled: bool = True
    file_extensions: ClassVar[list[str]] = ["mp3"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_path = None

    def _extract_metadata(self) -> dict[str, Any]:
        """Extract metadata from an MP3 file.

        Args:
        ----
            None

        Returns:
        -------
            dict[str, Any]: A dictionary containing the title, artist, album, cover
            image path, and additional metadata.

        """
        print(f"Extracting metadata from {self.source_path}")
        assert Path(self.source_path).exists(), f"{self.source_path} does not exist."
        audio = MP3(self.source_path, ID3=ID3)
        metadata = {
            "title": str(audio.get("TIT2", "Unknown Title")),
            "artist": str(audio.get("TPE1", "Unknown Artist")),
            "album": str(audio.get("TALB", "Unknown Album")),
            "cover": None,
            "extra": {},
        }
        # Use `get` more liberally to avoid raising exceptions.
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                cover_path = self.source_path.replace(".mp3", ".jpg")
                with open(cover_path, "wb") as img:
                    img.write(tag.data)
                metadata["cover"] = cover_path
            elif isinstance(tag, TXXX):
                metadata["extra"][tag.desc] = tag.text[0]
        return metadata

    def _process_metadata(self, metadata) -> tuple[str, dict[str, Any]]:
        """Generate a page for each MP3 file in the specified directory.

        Args:
        ----
            metadata: A dictionary containing the title, artist, album, cover, etc.

        """
        rtemplate = Environment(loader=BaseLoader()).from_string(template)
        content = rtemplate.render(
            title=metadata["title"],
            artist=metadata["artist"],
            album=metadata["album"],
            cover=metadata["cover"],
            mp3_path=self.source_path,
            extra_metadata=metadata["extra"],
        )
        return content, metadata | {
            "date": self.get_file_creation_date(self.source_path),
        }

    @staticmethod
    def get_file_creation_date(file_path):
        """Get the creation date of a file."""
        creation_ts = Path(file_path).stat().st_ctime
        return datetime.fromtimestamp(creation_ts)

    def read(self, source_path):
        """Read the content of an MP3 file."""
        print("## Got:", source_path)
        self.source_path = source_path
        metadata = self._extract_metadata()
        return self._process_metadata(metadata)


def add_reader(readers):
    """Add the MP3 reader to the Pelican readers, and any associated file
    extensions.
    """
    for ext in MP3Reader.file_extensions:
        readers.reader_classes[ext] = MP3Reader


def register() -> None:
    """Register the plugin with Pelican."""
    signals.readers_init.connect(add_reader)
