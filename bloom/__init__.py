from pathlib import Path
from typing import Optional

import fire

from bloom.article import Article
from bloom.create import init_article
from bloom.publish import publish, Platform


class Bloom:
    """Blog output manager"""

    def init(self, directory: str = '.', en: Optional[str] = None, cn: Optional[str] = None):
        init_article(directory=directory, title_en=en, title_cn=cn)

    def publish(self, article_path: str, platform: str):
        article_path: Path = Path(article_path)
        platform: Platform = Platform(platform)
        article = Article.open(article_path)
        publish(article, platform)


def main():
    bloom = Bloom()
    fire.Fire(bloom)