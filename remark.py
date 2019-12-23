import os
import re

from markdown import Markdown
from pelican import signals
from pelican.readers import MarkdownReader
from pelican.utils import pelican_open
from pelican.contents import Content

# TODO: fetch from pelican
INTRASITE_LINK_REGEX = '[{|](?P<what>.*?)[|}]'


def get_markdown_link_regex():
    """Return a regex that matches Markdown link syntax

    For example,

        [text](link)
        ![](image.png)
        ![alt text](image.png)

    would all be matched
    """
    regex = (
        r"\!?"  # Optionally begin with an exclamation mark

        # Capture the link name, or image alt text within brackets
        # [], [click here], ![alt text]
        r"\[(?P<link>.*?)\]"

        r"\("
        + r"(?P<path>{0}".format(INTRASITE_LINK_REGEX)  # {...} or |...| to denote an internal link
        + r"(?P<value>.*?))"  # Then the link path, relative to the site
        r"\)"
    )
    return regex


def replace_internal_links(markdown):
    """Return markdown, but internal links are replaced"""
    regex = get_markdown_link_regex()

    # TODO: Use the link regex instead
    markdown = markdown.replace("{static}", "")

    return markdown


class RemarkReader(MarkdownReader):
    file_extensions = ["remark"]

    def read(self, source_path):
        # content is returned as HTML, but we don't want that.
        content, metadata = super().read(source_path)

        if metadata.get("template") is None:
            metadata["template"] = "remark"

        # Instead, replace content with the original markdown source
        with pelican_open(source_path) as text:
            md_content = text.strip()

            # Remove initial metadata at the top of the file
            delimeter = "\n\n"
            content = md_content[md_content.find(delimeter) + len(delimeter):]

        # content = "![]({static}/images/git-status.png)"
        # content = "<img src='{static}/images/git-status.png'></a>"
        # content = '<textarea id="source">![]({static}/images/git-status.png)</textarea>'

        content = replace_internal_links(content)
        return content, metadata


def add_reader(readers):
    for extension in RemarkReader.file_extensions:
        readers.reader_classes[extension] = RemarkReader


def register():
    signals.readers_init.connect(add_reader)
