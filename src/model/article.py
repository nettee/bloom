from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Union, Type, Optional

import toml

from model.markdown import MarkdownDoc


class Category(Enum):
    Article = 'article'

    @classmethod
    def _missing_(cls, value) -> Category:
        return Category.Article


@dataclass
class BaseInfo:
    name: str
    docName: str
    titleEn: str
    titleCn: str
    createTime: datetime = field(default=datetime.now())
    category: Category = field(default=Category.Article)
    tags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.category, str):
            self.category = Category(self.category)


@dataclass
class HexoInfo:
    readMore: int = field(default=6)


@dataclass
class MetaInfo:
    base: BaseInfo
    hexo: Optional[HexoInfo] = field(default=None)

    def __post_init__(self):
        if isinstance(self.base, dict):
            self.base = BaseInfo(**self.base)
        if isinstance(self.hexo, dict):
            self.hexo = HexoInfo(**self.hexo)

    @staticmethod
    def read(file: Path):
        with file.open('r') as f:
            t = toml.load(f)
            meta = MetaInfo(**t)
        return meta


@dataclass
class Article:
    path: Path
    meta: MetaInfo = field(repr=False)

    META_FILE_NAME = 'meta.toml'
    IMAGE_DIR_NAME = 'img'

    @classmethod
    def create(cls, path:Path, meta: MetaInfo) -> Article:
        return Article(path, meta)

    @classmethod
    def open(cls, path: Path) -> Article:
        meta = MetaInfo.read(path / Article.META_FILE_NAME)
        return Article(path, meta)

    def doc_path(self) -> Path:
        return self.path_to(self.meta.base.docName)

    def image_path(self) -> Path:
        return self.path_to(Article.IMAGE_DIR_NAME)

    def path_to(self, sub_path: Union[str, Path]) -> Path:
        return self.path / sub_path

    def read_doc(self) -> MarkdownDoc:
        doc_file = self.path_to(self.meta.base.docName)
        if not doc_file.exists():
            raise RuntimeError(f'doc file not exists: {doc_file}')
        return MarkdownDoc.from_file(doc_file)

    def find_markdown_files(self):
        pass

    def update(self, meta):
        pass

    def save(self):
        pass
