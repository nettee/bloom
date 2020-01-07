import logging

import pytest

from model.markdown import MarkdownDoc, MarkdownParser

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


if __name__ == '__main__':
    pytest.main(['-s', 'test_markdown.py'])
