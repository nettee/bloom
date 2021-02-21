from pathlib import Path
from typing import Optional

import fire

from bloom import config
from bloom.article import Article
from bloom.create import init_article, new_article
from bloom.interact import interact
from bloom.publish import publish, Platform
from bloom.upload import upload


class Bloom:
    """Blog output manager"""

    def config(self, list: Optional[bool] = False):
        if list:
            config.list_settings()

    def new(self, directory: str = '.', en: Optional[str] = None, cn: Optional[str] = None):
        new_article(directory=directory, title_en=en, title_cn=cn)

    def init(self, directory: str = '.', en: Optional[str] = None, cn: Optional[str] = None):
        init_article(directory=directory, title_en=en, title_cn=cn)

    def status(self, directory: str = '.'):
        article = Article.open(Path(directory))
        article.status()

    def upload(self, directory: str = '.', to: str = 'none', all=False):
        article = Article.open(Path(directory))
        upload(article, to, all)

    def publish(self, article_path: str, platform: Optional[str] = None, to: Optional[str] = None):
        article_path: Path = Path(article_path)
        article = Article.open(article_path)
        publish(article, platform, to)

    def here(self):
        # Enter interactive mode
        interact()


def main():
    bloom = Bloom()
    fire.Fire(bloom)
