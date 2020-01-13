from base.config import get_bloomstore
from model.article import MetaInfo, Article

article_path = get_bloomstore() / 'LeetCode 例题精讲/03-从二叉树遍历到回溯算法'
meta_path = article_path / 'meta.toml'


def test_meta_read():
    print()
    meta = MetaInfo.read(meta_path)
    print(meta)


def test_new_article():
    print()
    article = Article(article_path)
    print(article)
