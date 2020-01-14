from pathlib import Path

import pytest

from core.publish import publish
from model.article import Article

article_path = Path('/Users/william/bloomstore/LeetCode 例题精讲/03-从二叉树遍历到回溯算法/')
article = Article.open(article_path)


class TestPublish:

    def test_publish(self):
        publish(article)


if __name__ == '__main__':
    pytest.main(['-q', 'test_publish.py'])
