import os
import re

from markdown import Markdown
from pelican import signals
from pelican.readers import MarkdownReader
from pelican.utils import pelican_open
from pelican.contents import Content
import pelican.settings as settings

INTRASITE_LINK_REGEX = settings.read_settings()["INTRASITE_LINK_REGEX"]


def get_markdown_link_regex():
    """Return a regex that matches Markdown link syntax

    For example,

        [text](link)
        ![](image.png)
        ![alt text](image.png)

    would all be matched
    """
    regex = (
        r"(?P<is_image>\!?)"  # Optionally begin with an exclamation mark

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
    link_regex = get_markdown_link_regex()

    def replace(m):
        # Remove "what" group. IE, "{static}"
        return f"{m.group('is_image')}[{m.group('link')}]({m.group('value')})"

    markdown = re.sub(link_regex, replace, markdown)
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

        content = replace_internal_links(content)
        return content, metadata


def add_reader(readers):
    for extension in RemarkReader.file_extensions:
        readers.reader_classes[extension] = RemarkReader


def register():
    signals.readers_init.connect(add_reader)
