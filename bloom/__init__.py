from pathlib import Path

import fire

from bloom.publish import publish, Platform
from bloom.article import Article


class Bloom:
    """Blog output manager"""

    def __init__(self, platform: str):
        self.platform: Platform = Platform(platform)

    def publish(self, article_path: str):
        article_path: Path = Path(article_path)
        article = Article.open(article_path)
        publish(article, platform=self.platform)


def main():
    fire.Fire(Bloom)