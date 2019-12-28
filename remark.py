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


def match_is_within_code_block(m: re.Match) -> bool:
    """Return True if a given regex match is within a markdown code block

    return False otherwise
    """
    substring_before_match = m.string[:m.start()]
    num_backticks = substring_before_match.count("`")
    within_code_block = (num_backticks % 2 == 1)

    return within_code_block


def replace_internal_links(markdown):
    """Return markdown, but internal links are replaced"""
    link_regex = get_markdown_link_regex()

    def replace(m):
        """Replace the internal link if not within a code block"""
        if not match_is_within_code_block(m):
            # Remove "what" {static}
            return f"{m.group('is_image')}[{m.group('link')}]({m.group('value')})"
        return m.string[m.start():m.end()]

    markdown_replaced = re.sub(link_regex, replace, markdown)
    return markdown_replaced


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
