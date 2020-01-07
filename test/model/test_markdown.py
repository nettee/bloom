import logging

import pytest

from model.markdown import MarkdownDoc, MarkdownParser, Image

logger = logging.getLogger(__name__)

doc_path = '/Users/william/bloomstore/LeetCode 例题精讲/03-从二叉树遍历到回溯算法/03-从二叉树遍历到回溯算法.md'


def test_from_file():
    doc = MarkdownDoc.from_file(doc_path)
    doc._show()


def test_parse_heading():
    line = '###     Some Text'
    heading = MarkdownParser.parse_heading_from_line(line)
    assert heading.level == 3
    assert heading.text == 'Some Text'
    print()
    print(repr(heading))


def test_parse_image():
    caption = 'some caption'
    uri = 'some/uri.jpg'
    image = Image(caption=caption, uri=uri)
    line = str(image)
    image = MarkdownParser.parse_image_from_line(line)
    assert image.caption == caption
    assert image.uri == uri


def test_parse_code_language():
    line = '```java'
    language = MarkdownParser.parse_code_language_from_line(line)
    assert language == 'java'


if __name__ == '__main__':
    pytest.main(['-s', 'test_markdown.py'])
