#! /usr/bin/env python
# ruff: noqa: E402
from typing import Optional
from dataclasses import dataclass
from importlib.util import find_spec
import json
from pathlib import Path
import logging

for mod in ["essentia", "mutagen", "rich_click", "requests"]:
    if find_spec(mod) is None:
        print(f"{mod} library not found. Please install it with `pip install {mod}`")
        exit(1)

import essentia.standard as es
import mutagen
from mutagen.id3 import ID3, TKEY, TXXX  # type: ignore
from mutagen.easyid3 import EasyID3
import requests
import rich_click as click
from rich.logging import RichHandler
import numpy as np

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(message)s", handlers=[RichHandler()])
logger = logging.getLogger("groovestamp")

# Constants
SAMPLE_RATE = 16000
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)
URL_ROOT = "https://essentia.upf.edu/models/"


class EssentiaModel:
    def __init__(
        self, name: str, type_: str = "classifiers", url_base: Optional[str] = None
    ):
        self.name = name
        self.type_ = type_
        self.base_name = name.split("-")[0]
        self.json_filepath = MODELS_DIR / f"{self.name}.json"
        self.weights_filepath = MODELS_DIR / f"{self.name}.pb"

        self.url_base = url_base or f"{URL_ROOT}/{type_}/{self.base_name}"
        self.json_url = f"{self.url_base}/{name}.json"
        self.weights_url = f"{self.url_base}/{name}.pb"

        self.download_if_not_present()

    @property
    def metadata(self):
        return json.load(open(self.json_filepath, "r"))

    def download_if_not_present(self):
        if not self.json_filepath.exists():
            logger.info(f"Model file {self.json_filepath} not found. Downloading...")
            with open(self.json_filepath, "wb") as f:
                f.write(requests.get(self.json_url).content)
        if not self.weights_filepath.exists():
            logger.info(f"Model file {self.weights_filepath} not found. Downloading...")
            with open(self.weights_filepath, "wb") as f:
                f.write(requests.get(self.weights_url).content)


MODELS = {
    "musicnn": EssentiaModel(
        "msd-musicnn-1", type_="autotagging", url_base=f"{URL_ROOT}/autotagging/msd"
    ),
    "danceability": EssentiaModel("danceability-musicnn-msd-2"),
    "mood_acoustic": EssentiaModel("mood_acoustic-musicnn-msd-2"),
    "mood_aggressive": EssentiaModel("mood_aggressive-musicnn-msd-2"),
    "mood_electronic": EssentiaModel("mood_electronic-musicnn-msd-2"),
    "mood_happy": EssentiaModel("mood_happy-musicnn-msd-2"),
    "mood_party": EssentiaModel("mood_party-musicnn-msd-2"),
    "mood_relaxed": EssentiaModel("mood_relaxed-musicnn-msd-2"),
    "mood_sad": EssentiaModel("mood_sad-musicnn-msd-2"),
}


@dataclass
class MusicAttributes:
    acoustic: float
    aggressive: float
    detected_genre: str
    danceability: float
    electronic: float
    energy: float
    happy: float
    key: str
    loudness: float
    party: float
    relaxed: float
    sad: float
    tempo: float


def add_custom_tags(file_path: str, attributes: MusicAttributes) -> None:
    """
    Adds custom tags for sadness, danceability, happiness, and energy to an MP3 file.
    Also fills out the genre tag if it is not present.
    """
    # Load the MP3 file
    audio = EasyID3(file_path)
    id3 = ID3(file_path)

    # Add custom tags
    for key, value in attributes.__dict__.items():
        if key == "detected_genre":
            if "genre" not in id3:
                audio["genre"] = value
        elif key == "key":
            if "key" not in id3:
                id3.add(TKEY(encoding=3, desc="key", text=value))
        else:
            id3.add(TXXX(encoding=3, desc=key, text=str(value)))

    logger.info(f"Writing {file_path}...")
    audio.save()
    id3.save()
    logger.info("New metadata:")
    logger.info(mutagen.File(file_path).pprint())  # type: ignore


def extract_music_attributes(file_path: str) -> MusicAttributes:
    """
    Extracts music attributes from an audio file using Essentia.

    :param file_path: Path to the audio file.
    :return: A MusicAttributes dataclass containing the extracted attributes.
    """

    # Lower level attributes
    extractor = es.MusicExtractor(  # type: ignore
        lowlevelStats=["mean", "stdev"],
        rhythmStats=["mean", "stdev"],
        tonalStats=["mean", "stdev"],
    )
    features, _ = extractor(file_path)
    audio = es.MonoLoader(filename=file_path, sampleRate=SAMPLE_RATE)()  # type: ignore

    # Genre
    musicnn_preds = es.TensorflowPredictMusiCNN(  # type: ignore
        graphFilename=str(MODELS["musicnn"].weights_filepath)
    )(audio)
    top_genre_ix = np.argmax(musicnn_preds, axis=1)[0]
    top_genre = MODELS["musicnn"].metadata["classes"][top_genre_ix]
    logger.debug(f"Detected genre: {top_genre}")

    # Classifiers
    attributes = {}
    for classifier_name, classifier in [
        (n, c) for n, c in MODELS.items() if c.type_ == "classifiers"
    ]:
        predictions = es.TensorflowPredictMusiCNN(  # type: ignore
            graphFilename=str(classifier.weights_filepath)
        )(audio)
        attribute = np.mean(predictions, axis=0)[0]
        logger.debug(f"{classifier.name}: {attribute}")
        attributes[classifier_name] = attribute

    return MusicAttributes(
        acoustic=attributes["mood_acoustic"],
        aggressive=attributes["mood_aggressive"],
        danceability=attributes["danceability"],
        detected_genre=top_genre,
        electronic=attributes["mood_electronic"],
        energy=features["lowlevel.average_loudness"],
        happy=attributes["mood_happy"],
        key=f"{features['tonal.key_edma.key']} {features['tonal.key_edma.scale']}",
        loudness=features["lowlevel.loudness_ebu128.integrated"],
        party=attributes["mood_party"],
        relaxed=attributes["mood_relaxed"],
        sad=attributes["mood_sad"],
        tempo=features["rhythm.bpm"],
    )


def download_classifiers() -> None:
    """Download classifiers if not present."""
    for model in MODELS.values():
        model.download_if_not_present()


@click.command()
@click.argument("file_path", type=click.Path(exists=True))
def main(file_path: str) -> None:
    """
    Adds custom tags for extracted music attributes to an MP3 file. Also fills out the genre tag if it is not present.
    """
    download_classifiers()
    logger.info(f"Processing {file_path}...")
    music_attributes = extract_music_attributes(str(file_path))
    logger.info(f"Extracted music attributes: {music_attributes}")
    logger.info("Adding custom tags to the file...")
    add_custom_tags(file_path, attributes=music_attributes)


if __name__ == "__main__":
    main()
