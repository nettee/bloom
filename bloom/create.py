import re
from pathlib import Path
from typing import Optional

from bloom.article import MetaInfo, BaseInfo


def build_meta(title_en: Optional[str] = None, title_cn: Optional[str] = None):
    assert title_en is not None
    assert title_cn is not None

    name = re.sub(r'[^0-9A-Za-z]+', '-', title_en)
    doc_name = re.sub(r'\s+', '-', title_cn) + '.md'

    return MetaInfo(
        base=BaseInfo(
            name=name,
            docName=doc_name,
            titleEn=title_en,
            titleCn=title_cn,
        ),
    )


# Steps:
# 1. Create article directory
# 2. Create markdown file (empty)
# 3. Create meta.yml file
def new_article(directory: str = '.', title_en: Optional[str] = None, title_cn: Optional[str] = None):
    meta = build_meta(title_en, title_cn)

    directory: Path = Path(directory)
    assert directory.exists() and directory.is_dir()

    article_dir = directory / Path(meta.base.docName).stem
    article_dir.mkdir()

    doc_file = article_dir / meta.base.docName
    doc_file.touch(exist_ok=True)

    meta.save_to_directory(article_dir)


# Create meta.yml file only
def init_article(directory: str = '.', title_en: Optional[str] = None, title_cn: Optional[str] = None):
    meta = build_meta(title_en, title_cn)

    directory: Path = Path(directory)
    assert directory.exists() and directory.is_dir()

    meta.save_to_directory(directory)
