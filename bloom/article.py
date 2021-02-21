from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Union, Optional, Any, Tuple

import yaml
from dacite import from_dict

from bloom.common import print_config
from bloom.markdown import MarkdownDoc


def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')


# tell pyyaml to serialize None as ''
yaml.add_representer(type(None), represent_none)


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
    category: str = field(default='article')
    tags: List[str] = field(default_factory=list)


@dataclass
class HexoInfo:
    readMore: int = field(default=6)


@dataclass
class GoldMinerTranslationInfo:
    postUrl: str


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

    @staticmethod
    def read(file: Path):
        with file.open('r') as f:
            data = yaml.load(f, Loader=yaml.CLoader)
            meta = from_dict(data_class=MetaInfo, data=data)
        return meta

    def save_to_directory(self, directory: Path) -> None:
        assert directory.is_dir()
        self.save_to_file(directory / Article.META_FILE_NAME)

    def save_to_file(self, file: Path) -> None:
        print(f'Save article meta to {file}')
        data = asdict(self)
        with file.open('w') as f:
            yaml.dump(data, f, allow_unicode=True)


META_FILENAMES = ('meta.yml', 'meta.yaml', 'meta.toml')


def _find_meta_file(article_path: Path) -> Path:
    for filename in META_FILENAMES:
        meta_file = article_path / filename
        if meta_file.exists():
            print(f'Load article meta from {meta_file}')
            return meta_file
    raise RuntimeError(f'article meta not found in {article_path}')


def _read_meta_info(article_path: Path):
    meta_path = _find_meta_file(article_path)
    return MetaInfo.read(meta_path)


@dataclass
class Article:
    path: Path
    meta: MetaInfo = field(repr=False)

    META_FILE_NAME = 'meta.yml'
    IMAGE_DIR_NAME = 'img'
    UPLOADED_IMAGE_DIR_NAME = 'img_uploaded'

    @classmethod
    def create(cls, path: Path, meta: MetaInfo) -> Article:
        return Article(path, meta)

    @classmethod
    def open(cls, path: Path) -> Article:
        meta = _read_meta_info(path)
        return Article(path, meta)

    def status(self):
        d = dataclasses.asdict(self.meta)
        print_config(d)

    def meta_path(self) -> Path:
        return self.path / Article.META_FILE_NAME

    def doc_path(self) -> Path:
        return self.path_to(self.meta.base.docName)

    def image_path(self) -> Path:
        return self.path_to(Article.IMAGE_DIR_NAME)

    def uploaded_image_path(self) -> Path:
        return self.path_to(Article.UPLOADED_IMAGE_DIR_NAME)

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
        self.meta.save_to_file(self.meta_path())

    def save_doc(self, doc: MarkdownDoc) -> None:
        self._mkdir()
        doc.save(self.doc_path())


