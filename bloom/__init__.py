from pathlib import Path

import fire

from bloom.publish import publish
from bloom.article import Article


class Bloom:
    """Blog output manager"""

    def publish(self, article_path: Path = Path('.')):
        article = Article.open(article_path)
        publish(article)


def main():
    fire.Fire(Bloom)