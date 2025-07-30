from typing import Protocol, Iterator, TextIO
import click

from .resource import Resource
from .extractor import TextExtractor


class CLI:
    """This class has the core functions that should be exposed to a command-line user.

    To make a CLI application, this class must be wrapped by a command-line adapter.
    """

    def __init__(self) -> None:
        pass

    def extract_text_from_resource(self, resource: str) -> Iterator[str]:
        """Attempts to extract the spoken or written content of the resource and return it as plain text. Examples:
        * `extract_text_from_resource("https://www.youtube.com/watch?v=NiTsduRreug")`:  attempts to extract a transcript of the video.
        * `extract_text_from_resource("https://en.wikipedia.org/wiki/Stephen_Krashen")`:  attempts to extract the article text of the web page.
        * `extract_text_from_resource("my_book.epub:2")`: attempts to extract the second chapter of the given `epub` and convert it to plain text.

        :param resource: A URL or a file path pointing to the resource.
        :return: The extracted plain text of the resource.
        """
        ...
        extractor = Resource(resource).get_extractor()
        text = extractor.extract()
        for line in text:
            yield line

    def extract_text_from_stream(self, stream: TextIO) -> Iterator[str]:
        """Converts an input stream to plain text.

        :param stream: A text stream.
        :return: The input stream converted to plain text.
        """
        ...
        extractor = TextExtractor(stream)
        text = extractor.extract()
        for line in text:
            yield line


class CLIAdapter:
    """Command-line adapter that uses the click library."""

    def __init__(self, cli: CLI) -> None:
        self.cli: CLI = cli

    def _create_extract_command(self) -> click.Command:
        @click.command()
        @click.argument("resource", required=False)
        def extract(resource: str):
            if resource:
                extracted_text = self.cli.extract_text_from_resource(resource)
            else:
                stdin_text = click.get_text_stream("stdin")
                extracted_text = self.cli.extract_text_from_stream(stdin_text)

            for line in extracted_text:
                click.echo(line)

        return extract

    def run(self) -> None:
        cli = click.Group()
        cli.add_command(self._create_extract_command())
        cli()
