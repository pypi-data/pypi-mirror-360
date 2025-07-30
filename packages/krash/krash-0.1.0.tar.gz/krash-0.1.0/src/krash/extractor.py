from typing import Protocol, Iterator, Iterable
from youtube_transcript_api import YouTubeTranscriptApi

from .env import LANGUAGE


class Extractor(Protocol):
    """This class extracts plain text from a specific resource type containing spoken or written content."""

    def extract(self) -> Iterator[str]: ...


class TextExtractor:
    def __init__(self, text: Iterable[str]) -> None:
        self._text: Iterable[str] = text

    def extract(self) -> Iterator[str]:
        for line in self._text:
            yield line


class YoutubeSubtitleExtractor:
    def __init__(self, video_id: str) -> None:
        self._video_id: str = video_id

    def extract(self) -> Iterator[str]:
        fetched_transcript = YouTubeTranscriptApi().fetch(
            self._video_id, languages=[LANGUAGE]
        )
        for snippet in fetched_transcript:
            yield snippet.text
