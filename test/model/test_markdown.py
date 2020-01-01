import pytest

from model.markdown import MarkdownDoc

doc_path = '/Users/william/bloomstore/LeetCode 例题精讲/03-从二叉树遍历到回溯算法/03-从二叉树遍历到回溯算法.md'


class TestMarkdown:

    def test_from_file(self):
        MarkdownDoc.from_file(doc_path)


if __name__ == '__main__':
    pytest.main(['-q', 'test_markdown.py'])
