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
from bloom.config import settings
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
    name: str  # 文章唯一标识，不含空格
    docName: str  # Markdown 文档文件名
    titleEn: str = field(default=None)  # 英文标题
    titleCn: str = field(default=None)  # 中文标题
    createTime: datetime = field(default=datetime.now())  # 创建时间
    category: str = field(default='article')  # 文章类型（保留字段）
    tags: List[str] = field(default_factory=list)  # 文章标签


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


@dataclass
class MetaInfo:
    base: BaseInfo  # 基本信息
    hexo: Optional[HexoInfo] = field(default=None)  # Hexo 博客文章元信息
    translation: Optional[TranslationInfo] = field(default=None)  # 掘金翻译计划文章元信息

    @staticmethod
    def read(file: Path):
        with file.open('r') as f:
            data = yaml.load(f, Loader=yaml.CLoader)
            meta = from_dict(data_class=MetaInfo, data=data)
        return meta

    def save_to_directory(self, directory: Path) -> None:
        assert directory.is_dir()
        self.save_to_file(directory / settings.article.metaFileName)

    def save_to_file(self, file: Path) -> None:
        data = asdict(self)
        with file.open('w') as f:
            yaml.dump(data, f, allow_unicode=True)
        print(f'Saved article meta {file}')


def _find_meta_file(article_path: Path) -> Path:
    meta_file = article_path / settings.article.metaFileName
    if not meta_file.exists():
        raise RuntimeError(f'article meta not found in {article_path}')
    return meta_file


def _read_meta_info(article_path: Path):
    meta_file = _find_meta_file(article_path)
    print(f'Load article meta from {meta_file}')
    return MetaInfo.read(meta_file)


@dataclass
class Article:
    path: Path
    meta: MetaInfo = field(repr=False)

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
        return self.path_to(settings.article.metaFileName)

    def doc_path(self) -> Path:
        return self.path_to(self.meta.base.docName)

    def image_path(self) -> Path:
        return self.path_to(settings.article.imageDirName)

    def uploaded_image_path(self) -> Path:
        return self.path_to(settings.article.uploadedImageDirName)

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
