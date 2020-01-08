from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

import toml

meta_file_name = 'meta.toml'


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
    createTime: datetime
    category: Category = field(default=Category.Article)
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.category, str):
            self.category = Category(self.category)


@dataclass
class HexoInfo:
    readMore: int = field(default=6)


@dataclass
class MetaInfo:
    base: BaseInfo
    hexo: HexoInfo

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


@dataclass(init=False)
class Article:
    path: Path
    meta: MetaInfo = field(repr=False)

    def __init__(self, path: Path) -> None:
        self.path = path
        self.read_meta()

    def read_meta(self) -> None:
        meta_path = self.path / meta_file_name
        self.meta = MetaInfo.read(meta_path)

    def doc_path(self):
        pass

    def path_to(self):
        pass

    def find_markdown_files(self):
        pass

    def image_path(self):
        pass

    def update(self, meta):
        pass

    def save(self):
        pass
