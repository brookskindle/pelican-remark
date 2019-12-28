from . import remark
import pytest

def test_internal_links_are_replaced():
    content = "[a file]({static}/file.pdf)"
    replaced = remark.replace_internal_links(content)
    assert content != replaced


def test_internal_images_are_replaced():
    content = "![]({static}/images/image.png)"
    replaced = remark.replace_internal_links(content)
    assert content != replaced


def test_links_not_in_link_form_are_preserved():
    content = "{static}/images/image.png"
    replaced = remark.replace_internal_links(content)
    assert content == replaced
