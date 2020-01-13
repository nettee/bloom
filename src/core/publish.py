from dataclasses import dataclass, field
from typing import List, Callable

from base.config import get_bloomstore
from model.article import Article
from model.markdown import MarkdownDoc

Transfer = Callable[[Article, MarkdownDoc], MarkdownDoc]
Save = Callable[[Article, MarkdownDoc], None]


@dataclass
class PublishProcess:
    save: Save
    transfers: List[Transfer] = field(default_factory=list)

    def with_transfer(self, t: Transfer):
        self.transfers.append(t)


def publish(article: Article, publish_process: PublishProcess = None):
    print('publishing', article.path)
    doc = article.read_doc()


if __name__ == '__main__':
    article_path = get_bloomstore() / 'LeetCode 例题精讲/03-从二叉树遍历到回溯算法'
    publish(Article(article_path))
