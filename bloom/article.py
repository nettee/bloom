from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Union, Optional, Any, Tuple

import toml

from bloom.markdown import MarkdownDoc


class Category(Enum):
    Article = 'article'

    @classmethod
    def _missing_(cls, value) -> Category:
        return Category.Article


# TOML table
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


# TOML table
@dataclass
class HexoInfo:
    readMore: int = field(default=6)


# TOML table
@dataclass
class GoldMinerTranslationInfo:
    postUrl: str


# TOML table
@dataclass
class TranslationInfo:
    originalUrl: Optional[str] = field(default=None)
    translatorName: Optional[str] = field(default=None)
    translatorPage: Optional[str] = field(default=None)
    goldMiner: Optional[GoldMinerTranslationInfo] = field(default=None)


DictItems = List[Tuple[str, Any]]


def toml_dict_factory(items: DictItems) -> dict:
    """
    Serialize values of obscure types (e.g. Category) in toml.dump().
    The dict factory will be called multiple times for a TOML document.
    """
    normal_types = {type(None), bool, int, float, str, datetime, list, dict}

    def serialize(v: Any) -> Any:
        if type(v) in normal_types:
            return v
        elif isinstance(v, Enum):
            return v.value
        else:
            return str(v)

    # TODO deal with nested obscure type in array
    new_items = [(key, serialize(value)) for (key, value) in items]

    return dict(new_items)


# TOML document
@dataclass
class MetaInfo:
    base: BaseInfo
    hexo: Optional[HexoInfo] = field(default=None)
    translation: Optional[TranslationInfo] = field(default=None)

    # TODO remove this, use from_dict
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

    def save(self, file: Path) -> None:
        with file.open('w') as f:
            toml.dump(asdict(self, dict_factory=toml_dict_factory), f)


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

    def meta_path(self) -> Path:
        return self.path / Article.META_FILE_NAME

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

    def _mkdir(self) -> None:
        self.path.mkdir(exist_ok=True)

    def save_meta(self) -> None:
        self._mkdir()
        self.meta.save(self.meta_path())

    def save_doc(self, doc: MarkdownDoc) -> None:
        self._mkdir()
        doc.save(self.doc_path())


