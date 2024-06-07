import os
from pathlib import Path

import pytest

from pelican import Pelican
from pelican.settings import read_settings
from pelican_mp3 import MP3Reader

ROOT = Path(__file__).parent
MP3_FOLDER = ROOT / "mp3"
MP3_FILE = MP3_FOLDER / "sample-12s.mp3"
OUTPUT_FOLDER = ROOT / "output"


@pytest.fixture
def pelican():
    """Set up the test environment."""
    test_settings = {
        "PATH": ROOT,
        "OUTPUT_PATH": OUTPUT_FOLDER,
        "PLUGINS": ["pelican_mp3"],
        "TEMPLATE_PAGES": {"mp3_page.html": "mp3_page.html"},
    }
    settings = read_settings(override=test_settings)
    pelican = Pelican(settings=settings)
    pelican.run()
    yield

    pelican.clean()
    OUTPUT_FOLDER.rmdir()


def test_extract_metadata():
    """Test the metadata extraction from the MP3 file."""
    metadata = extract_metadata(str(MP3_FILE))
    assert metadata["title"] == "Unknown Title"
    assert metadata["artist"] == "Unknown Artist"
    assert metadata["album"] == "Unknown Album"
    assert metadata["cover"] is not None
    assert "sad" in metadata["extra"]
    assert "happy" in metadata["extra"]
    assert "party" in metadata["extra"]


def test_generate_mp3_pages(pelican):
    """Test the generation of MP3 pages."""
    # generate_mp3_pages(generator)
    output_file = os.path.join(settings["OUTPUT_PATH"], "mp3", "sample-12s.html")
    assert os.path.exists(output_file)

    with open(output_file) as f:
        content = f.read()
        assert "Unknown Title" in content
        assert "Unknown Artist" in content
        assert "Unknown Album" in content
        assert "sad" in content
        assert "happy" in content
        assert "party" in content
