import re
from pathlib import Path
from typing import Optional

from bloom.article import MetaInfo, BaseInfo


def init_article(directory: str = '.', title_en: Optional[str] = None, title_cn: Optional[str] = None):
    directory: Path = Path(directory)
    assert directory.exists() and directory.is_dir()

    name = re.sub(r'[^0-9A-Za-z]+', '-', title_en)
    doc_name = re.sub(r'\s+', '-', title_cn) + '.md'

    doc_file = directory / doc_name
    doc_file.touch(exist_ok=True)

    meta = MetaInfo(
        base=BaseInfo(
            name=name,
            docName=doc_name,
            titleEn=title_en,
            titleCn=title_cn,
        ),
    )

    meta.save_to_directory(directory)
