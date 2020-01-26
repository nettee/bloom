from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Callable
from urllib.parse import ParseResult

import pyperclip

from bloom.config import get_bloomstore, settings
from bloom.article import Article
from bloom.markdown import MarkdownDoc

Transfer = Callable[[Article, MarkdownDoc], MarkdownDoc]
Save = Callable[[Article, MarkdownDoc], None]


class Platform(Enum):
    Xiaozhuanlan = 'xzl'
    Juejin = 'juejin'
    WeChat = 'wechat'
    Hexo = 'hexo'
    Zhihu = 'zhihu'


@dataclass
class PublishProcess:
    transfers: List[Transfer] = field(default_factory=list)
    save: Save = field(default=lambda article, doc: None)


def transfer_image_uri_as_public(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    def transfer(uri: str) -> str:
        base_url_path = settings.image.baseUrlPath
        article_name = article.meta.base.name
        file_name = Path(uri).name
        url_path = Path(base_url_path).joinpath(article_name, file_name)
        url = ParseResult(
            scheme='http',
            netloc=settings.image.host,
            path=str(url_path),
            params='',
            query='',
            fragment='',
        ).geturl()
        return url

    doc.transfer_image_uri(
        test=lambda image: image.is_local(),
        transfer=transfer,
    )
    return doc


# Hexo only support '\newline' rather than '\\' in math equations
def transfer_math_equations_newline(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    doc.transfer_math_block_by_line(
        test=lambda line: line.endswith(r'\\'),
        transfer=lambda line: line[:-2] + r'\newline',
    )
    return doc


def add_read_more_label(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    # TODO
    print('add_read_more_label')
    return doc


def add_hexo_header_lines(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    # TODO
    print('add_hexo_header_lines')
    return doc


def copy_body(article: Article, doc: MarkdownDoc) -> None:
    pyperclip.copy(doc.body_string())
    print('document body copied to clipboard')


def save_body_to_temp(article: Article, doc: MarkdownDoc) -> None:
    # TODO
    print('save_body_to_temp')


def export_to_hexo(article: Article, doc: MarkdownDoc) -> None:
    # TODO
    print('export_to_hexo')


platform_processes = {
    Platform.Xiaozhuanlan: PublishProcess(
        transfers=[
            transfer_image_uri_as_public,
        ],
        save=copy_body,
    ),
    Platform.Juejin: PublishProcess(
        transfers=[
            transfer_image_uri_as_public,
        ],
        save=copy_body,
    ),
    Platform.WeChat: PublishProcess(
        transfers=[
            transfer_image_uri_as_public
        ],
        save=copy_body,
    ),
    Platform.Hexo: PublishProcess(
        transfers=[
            transfer_math_equations_newline,
            add_read_more_label,
            add_hexo_header_lines
        ],
        save=export_to_hexo,
    ),
    Platform.Zhihu: PublishProcess(
        transfers=[
            transfer_image_uri_as_public,
        ],
        save=save_body_to_temp,
    ),
}


def publish(article: Article, platform: Platform):
    print('publishing', article.path)
    doc = article.read_doc()

    process = platform_processes[platform]

    for t in process.transfers:
        doc = t(article, doc)

    process.save(article, doc)


if __name__ == '__main__':
    article_path = get_bloomstore() / 'LeetCode 例题精讲/03-从二叉树遍历到回溯算法'
    publish(Article.open(article_path), platform=Platform.Xiaozhuanlan)
