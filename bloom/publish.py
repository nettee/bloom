import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Callable, Optional, cast
from urllib.parse import ParseResult

import pyperclip
from termcolor import colored

from bloom.config import get_bloomstore, settings
from bloom.article import Article
from bloom.markdown import MarkdownDoc, CodeBlock, NormalParagraph

Transfer = Callable[[Article, MarkdownDoc], MarkdownDoc]
Save = Callable[[Article, MarkdownDoc], None]


class Platform(Enum):
    WeChat = 'wechat'
    Xiaozhuanlan = 'xzl'
    LeetCodeCn = 'lcn'
    Zhihu = 'zhihu'
    Juejin = 'juejin'
    Hexo = 'hexo'

    def description(self):
        return {
            Platform.WeChat: '微信公众号',
            Platform.Xiaozhuanlan: '小专栏',
            Platform.LeetCodeCn: 'LeetCode 题解',
            Platform.Zhihu: '知乎专栏',
            Platform.Juejin: '掘金专栏',
            Platform.Hexo: 'Hexo',
        }[self]


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


# 将外链去掉，转化为特殊粗体，用于微信公众号
def transfer_link_to_bold(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    pattern = re.compile(r'\[(.*?)\]\((.*?)\)')

    for p in doc.body:
        if not isinstance(p, NormalParagraph):
            continue
        for i, line in enumerate(p.lines):
            m = re.search(pattern, line)
            if m is None:
                continue
            url = m.group(2)
            if 'mp.weixin.qq.com' in url:
                continue
            p.lines[i] = re.sub(pattern, r'<span class="outer-link">\1</span>', line)

    return doc


# For leetcode-cn solutions, we can write code blocks with multiple tabs
def group_code_blocks(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    code_block_groups = doc.find_adjacent(lambda p: isinstance(p, CodeBlock))
    for group in code_block_groups:
        for p in group:
            code_block: CodeBlock = p
            code_block.language = code_block.language + ' []'
    return doc


def add_read_more_label(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    # TODO
    print('add_read_more_label')
    return doc


def add_hexo_header_lines(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    # TODO
    print('add_hexo_header_lines')
    return doc


def add_lcn_footer(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    print('add lcn footer')
    script_path = os.path.realpath(__file__)
    project_path = Path(script_path).parent.parent
    file = project_path / 'snippet' / 'footer' / 'lcn.md'
    footer = MarkdownDoc.from_file(file)
    doc.footer = footer.body
    return doc


def copy_body(article: Article, doc: MarkdownDoc) -> None:
    pyperclip.copy(doc.full_body_string())
    print('document body copied to clipboard')


def save_body_to_temp(article: Article, doc: MarkdownDoc) -> None:
    filename = article.meta.base.docName
    file = Path.home() / 'Desktop' / filename
    with file.open('w') as f:
        print(doc.body_string(), file=f)
    print(f'document body exported to file {file}')


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
            transfer_image_uri_as_public,
            transfer_link_to_bold,
        ],
        save=copy_body,
    ),
    Platform.LeetCodeCn: PublishProcess(
        transfers=[
            transfer_image_uri_as_public,
            group_code_blocks,
            add_lcn_footer,
        ],
        save=copy_body,
    ),
    Platform.Hexo: PublishProcess(
        transfers=[
            transfer_math_equations_newline,
            add_read_more_label,
            add_hexo_header_lines,
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


def eprint(value: str, end: str = '\n') -> None:
    print(colored(value, 'red'), end=end, file=sys.stderr)


def publish(article: Article, platform: Optional[str] = None, to: Optional[str] = None):
    print('publishing', article.path)

    assert platform is not None or to is not None
    platform: str = platform if platform is not None else to
    try:
        platform: Platform = Platform(platform)
    except ValueError as e:
        eprint(f'Error: {str(e)}')
        exit(1)

    doc = article.read_doc()

    if platform not in platform_processes:
        eprint(f"Error: no process defined for platform '{platform.value}'")
        exit(1)
    process = platform_processes[platform]

    for t in process.transfers:
        doc = t(article, doc)

    process.save(article, doc)


if __name__ == '__main__':
    article_path = get_bloomstore() / 'LeetCode 例题精讲/03-从二叉树遍历到回溯算法'
    publish(Article.open(article_path), platform='xzl')
