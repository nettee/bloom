from pathlib import Path

from model.article import Article


def publish(article: Article):
    print('publishing', article.path)


if __name__ == '__main__':
    article_path = Path('/Users/william/bloomstore/LeetCode 例题精讲/03-从二叉树遍历到回溯算法')
    publish(Article(article_path))
