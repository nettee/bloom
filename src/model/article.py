import pprint
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import toml

meta_file_name = 'meta.toml'


@dataclass
class BaseInfo:
    name: str
    type_: str
    doc_name: str
    title_en: str
    title_cn: str
    create_time: datetime
    tags: List[str]


@dataclass
class HexoInfo:
    read_more: int


@dataclass
class MetaInfo:
    base: BaseInfo
    hexo: HexoInfo

    @staticmethod
    def read_from_file(file: Path):
        with file.open('r') as f:
            t = toml.load(f)
            pp = pprint.PrettyPrinter()
            pp.pprint(t)


class Article:
    path: str
    meta: MetaInfo

    def __init__(self, path: str):
        self.path = path
        self.meta = None  # TODO

    def __str__(self):
        return self.path

    def __repr__(self):
        return f'Article[path={self.path}]'

    def meta_path(self):
        pass

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
