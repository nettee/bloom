from dataclasses import dataclass, field
from enum import Enum
from typing import List, Callable

import pyperclip

from base.config import get_bloomstore
from model.article import Article
from model.markdown import MarkdownDoc

Transfer = Callable[[Article, MarkdownDoc], MarkdownDoc]
Save = Callable[[Article, MarkdownDoc], None]


class Platform(Enum):
    Xiaozhuanlan = 'xzl'
    WeChat = 'wechat'
    Hexo = 'hexo'
    Zhihu = 'zhihu'
    Default = 'default'

    @classmethod
    def _missing_(cls, value):
        return Platform.Default


@dataclass
class PublishProcess:
    transfers: List[Transfer] = field(default_factory=list)
    save: Save = field(default=lambda article, doc: None)

    def with_transfer(self, t: Transfer):
        self.transfers.append(t)

    def with_save(self, s: Save):
        self.save = s


def transfer_image_url(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    # TODO
    print('transfer_image_url')
    return doc


def transfer_math_equations(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    # TODO
    print('transfer_math_equations')
    return doc


def add_read_more_label(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    # TODO
    print('add_read_more_label')
    return doc


def add_hexo_header_lines(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    # TODO
    print('add_hexo_header_lines')


def copy_body(article: Article, doc: MarkdownDoc) -> None:
    # TODO
    print('copy_body')
    content = doc.body_string()
    pyperclip.copy(content)
    print('document body copied to clipboard')


def save_body_to_temp(article: Article, doc: MarkdownDoc) -> None:
    # TODO
    print('save_body_to_temp')


def export_to_hexo(article: Article, doc: MarkdownDoc) -> None:
    # TODO
    print('export_to_hexo')


platform_publishes = {
    Platform.Xiaozhuanlan: PublishProcess(
        transfers=[
            transfer_image_url,
        ],
        save=copy_body,
    ),
    Platform.WeChat: PublishProcess(
        transfers=[
            transfer_image_url
        ],
        save=copy_body,
    ),
    Platform.Hexo: PublishProcess(
        transfers=[
            transfer_math_equations,
            add_read_more_label,
            add_hexo_header_lines
        ],
        save=export_to_hexo,
    ),
    Platform.Zhihu: PublishProcess(
        transfers=[
            transfer_image_url,
        ],
        save=save_body_to_temp,
    ),
}


def publish(article: Article, platform: Platform):
    print('publishing', article.path)
    doc = article.read_doc()

    process = platform_publishes[platform]

    for t in process.transfers:
        doc = t(article, doc)

    process.save(article, doc)


if __name__ == '__main__':
    article_path = get_bloomstore() / 'LeetCode 例题精讲/03-从二叉树遍历到回溯算法'
    publish(Article(article_path), platform=Platform.Xiaozhuanlan)
