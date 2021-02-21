import re
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import List, Callable, Optional
from urllib.parse import urlparse

from bloom.article import Article, MetaInfo, BaseInfo, TranslationInfo, GoldMinerTranslationInfo
from bloom.config import settings
from bloom.markdown import MarkdownDoc, Quote, Link, Heading, HorizontalRule


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

    name = None
    doc_name = None
    title_en = None
    title_cn = None

    original_url = None
    translator_name = None
    translator_page = None

    p = doc.find_one(lambda p: isinstance(p, Quote))
    assert p is not None
    for line in p.line_strings():
        if '原文地址' in line:
            original_address = extract_link(line)
            title_en = original_address.text
            original_url = original_address.url
        elif '本文永久链接' in line:
            permalink = extract_link(line)
            url = permalink.url
            path = Path(urlparse(url).path)
            name = path.stem
            doc_name = path.name
        elif '译者' in line:
            translator = extract_link(line)
            translator_name = translator.text
            translator_page = translator.url

    heading1: Optional[Heading] = doc.find_one(lambda p: isinstance(p, Heading) and p.level == 1)
    if heading1 is not None:
        title_cn = heading1.text

    return MetaInfo(
        base=BaseInfo(
            name=name,
            docName=doc_name,
            titleEn=title_en,
            titleCn=title_cn,
            tags=['翻译'],
        ),
        translation=TranslationInfo(
            originalUrl=original_url,
            translatorName=translator_name,
            translatorPage=translator_page,
            goldMiner=GoldMinerTranslationInfo(
                postUrl='',
            ),
        ),
    )


def construct_article(dest: Path, meta: MetaInfo) -> Article:
    article_path = dest / meta.base.titleCn
    return Article(path=article_path, meta=meta)


def extract_gold_miner_header(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    doc.header = doc.remove_start_while(lambda p: isinstance(p, Quote))
    return doc


def remove_footer(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    doc.remove_end_while(lambda p: isinstance(p, Quote) or isinstance(p, HorizontalRule))
    return doc


def extract_title(article: Article, doc: MarkdownDoc) -> MarkdownDoc:
    heading1 = doc.remove_start(lambda p: isinstance(p, Heading) and p.level == 1)
    if heading1 is not None:
        doc.title = heading1.text
    return doc


def save_to_bloom(article: Article, doc: MarkdownDoc) -> None:
    print(f'Save article {article.path}')
    article.save_meta()
    article.save_doc(doc)


def import_docs(process: ImportProcess, doc_files: List[Path], dest: Path) -> None:
    for file in doc_files:
        doc = process.fetch(file)
        meta = process.extract(doc)
        article = process.construct(dest, meta)

        for transfer in process.transfers:
            doc = transfer(article, doc)

        process.save(article, doc)


gold_miner_process = ImportProcess(
    fetch=MarkdownDoc.from_file,
    extract=extract_meta,
    construct=construct_article,
    transfers=[
        extract_gold_miner_header,
        remove_footer,
        extract_title,
    ],
    save=save_to_bloom,
)


def import_from_gold_miner(doc_files: List[Path]) -> None:
    dest = Path(settings.bloomstore) / '掘金翻译计划'
    import_docs(gold_miner_process, doc_files, dest)


if __name__ == '__main__':
    gold_miner_project_dir = Path.home() / 'projects' / 'gold-miner'
    files = [
        'TODO1/tutorial-write-a-shell-in-c.md',
        'TODO1/writing-a-microservice-in-rust.md',
        'TODO1/retries-timeouts-backoff.md',
        'TODO1/blazingly-fast-parsing-part-1-optimizing-the-scanner.md',
        'TODO1/how_to_prep_your_github_for_job_seeking.md',
    ]
    docs = [gold_miner_project_dir / file for file in files]
    import_from_gold_miner(docs)
