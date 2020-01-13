from pathlib import Path

from base.config import get_bloomstore
from model.article import Article


def publish(article: Article):
    print('publishing', article.path)


if __name__ == '__main__':
    article_path = get_bloomstore() / 'LeetCode 例题精讲/03-从二叉树遍历到回溯算法'
    publish(Article(article_path))
