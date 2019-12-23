from . import remark

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


# TODO: html should already be handled by upstream Pelican rendering - would
# need an integration test for that
def test_html_images_are_replaced():
    content = "<img alt='picture' src='{static}/images/git-status.png'></img>"
    replaced = remark.replace_internal_links(content)
    assert content != replaced


def test_html_links_are_replaced():
    content = "<a src='{static}/images/git-status.png'>Click here</a>"
    replaced = remark.replace_internal_links(content)
    assert content != replaced


def test_links_within_code_blocks_are_preserved():
    content = "`[a file]({static}/file.pdf)`"
    replaced = remark.replace_internal_links(content)
    assert content == replaced

    content = """\
        ```
        [a file]({static}/file.pdf)
        ![an image]({static}/images/image.png)
        ```
    """
    replaced = remark.replace_internal_links(content)
    assert content == replaced
