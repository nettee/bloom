from pathlib import Path
from typing import Optional

import fire

from bloom.article import Article
from bloom.create import init_article, new_article
from bloom.publish import publish, Platform
from bloom.upload import upload


class Bloom:
    """Blog output manager"""

    def new(self, directory: str = '.', en: Optional[str] = None, cn: Optional[str] = None):
        new_article(directory=directory, title_en=en, title_cn=cn)

    def init(self, directory: str = '.', en: Optional[str] = None, cn: Optional[str] = None):
        init_article(directory=directory, title_en=en, title_cn=cn)

    def upload(self, directory: str = '.', all=False):
        article = Article.open(Path(directory))
        upload(article, all)

    def publish(self, article_path: str, platform: str):
        article_path: Path = Path(article_path)
        platform: Platform = Platform(platform)
        article = Article.open(article_path)
        publish(article, platform)


def main():
    bloom = Bloom()
    fire.Fire(bloom)