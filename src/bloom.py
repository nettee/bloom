from pathlib import Path

import fire

from core.publish import publish
from model.article import Article


class Bloom:
    """Blog output manager"""

    def publish(self, article_path: Path = Path('.')):
        article = Article.open(article_path)
        publish(article)


if __name__ == '__main__':
    fire.Fire(Bloom)
