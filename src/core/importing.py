import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import List, Callable, Optional
from urllib.parse import urlparse

from model.article import Article, MetaInfo, BaseInfo
from model.markdown import MarkdownDoc, Quote, Link, Heading


class Platform(Enum):
    GoldMiner = auto()


Fetch = Callable[[Path], MarkdownDoc]
Extract = Callable[[MarkdownDoc], MetaInfo]
Construct = Callable[[Path, MetaInfo], Article]
Transfer = Callable[[Article, MarkdownDoc], MarkdownDoc]
Save = Callable[[Article, MarkdownDoc], None]


@dataclass
class ImportProcess:
    fetch: Fetch
    extract: Extract
    construct: Construct
    transfers: List[Transfer]
    save: Save


@dataclass
class GoldMinerHeader:
    original_address: Optional[Link] = field(default=None)
    original_author: Optional[Link] = field(default=None)
    permalink: Optional[Link] = field(default=None)
    translator: Optional[Link] = field(default=None)
    proofreader: List[Link] = field(default_factory=list)

    def name(self):
        url = self.permalink.url
        path = urlparse(url).path
        return Path(path).stem

    def doc_name(self):
        url = self.permalink.url
        path = urlparse(url).path
        return Path(path).name

    def title_en(self):
        return self.original_address.text
    
    
def extract_link(line: str) -> Optional[Link]:
    m = re.search(Link.PATTERN, line)
    if m is None:
        return None
    text = m.group(1)
    url = m.group(2)
    return Link(text=text, url=url)


def extract_all_links(line: str) -> List[Link]:
    links = []
    for m in re.finditer(Link.PATTERN, line):
        if m is None:
            continue
        text = m.group(1)
        url = m.group(2)
        links.append(Link(text=text, url=url))
    return links


def extract_meta(doc: MarkdownDoc) -> MetaInfo:
    p = doc.body[0]
    assert isinstance(p, Quote)
    header = GoldMinerHeader()
    for line in p.line_strings():
        if '原文地址' in line:
            header.original_address = extract_link(line)
        elif '本文永久链接' in line:
            header.permalink = extract_link(line)
        elif '译者' in line:
            header.translator = extract_link(line)
        elif '校对者' in line:
            header.proofreader = extract_all_links(line)

    name = header.name()
    doc_name = header.doc_name()
    title_en = header.title_en()
    heading1: Optional[Heading] = doc.find_one(lambda p: isinstance(p, Heading) and p.level == 1)
    title_cn = heading1.text if heading1 is not None else None

    return MetaInfo(BaseInfo(name=name, docName=doc_name, titleEn=title_en, titleCn=title_cn))


def construct_article(dest: Path, meta: MetaInfo) -> Article:
    article_path = dest / meta.base.name
    return Article(path=article_path, meta=meta)


def strip_header_and_footer(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    pass


def save_to_bloom(article: Article, doc: MarkdownDoc) -> None:
    pass


gold_miner_process = ImportProcess(
    fetch=MarkdownDoc.from_file,
    extract=extract_meta,
    construct=construct_article,
    transfers=[
        strip_header_and_footer,
    ],
    save=save_to_bloom,
)


def import_from_gold_miner(doc_files: List[Path], dest: Path) -> None:

    process = gold_miner_process

    for file in doc_files:
        doc = process.fetch(file)
        meta = process.extract(doc)
        article = process.construct(dest, meta)
        print(article)


if __name__ == '__main__':
    dir = Path('/home/william/projects/gold-miner/TODO1/')
    files = [
        'tutorial-write-a-shell-in-c.md',
        # 'writing-a-microservice-in-rust.md',
        # 'retries-timeouts-backoff.md',
        # 'how_to_prep_your_github_for_job_seeking.md',
    ]
    docs = [dir / file for file in files]
    dest = Path('/home/william/bloomstore/掘金翻译计划')
    import_from_gold_miner(docs, dest)