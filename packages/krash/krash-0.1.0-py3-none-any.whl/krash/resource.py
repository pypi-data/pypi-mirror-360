from typing import Protocol
from urllib import parse
import pathlib
from .extractor import Extractor, TextExtractor, YoutubeSubtitleExtractor


class Resource:
    """This class parses selected resource identifiers (e.g. URL's, file paths), and chooses the appropriate text extractor."""

    def __init__(self, identifier: str) -> None:
        self._identifier = identifier

    def get_extractor(self) -> Extractor:
        if (url := parse.urlparse(self._identifier)).netloc:
            return self._get_extractor_from_url(url)
        elif (path := pathlib.Path(self._identifier)).exists():
            return self._get_extractor_from_path(path)
        else:
            raise Exception(
                f"'{self._identifier}' is not a valid URL or a path to an existing file."
            )

    def _get_extractor_from_url(self, url: parse.ParseResult) -> Extractor:
        match url.hostname:
            case "www.youtube.com":
                return self._get_youtube_extractor(url)
            case _:
                return TextExtractor("Found url")

    def _get_youtube_extractor(self, url: parse.ParseResult) -> Extractor:
        try:
            return YoutubeSubtitleExtractor(video_id=parse.parse_qs(url.query)["v"][0])
        except KeyError:
            raise Exception(f"'{url.geturl()}' is missing the 'v' query parameter.")

    def _get_extractor_from_path(self, path: pathlib.Path) -> Extractor:
        return TextExtractor("Found path")
