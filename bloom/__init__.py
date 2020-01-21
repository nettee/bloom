import fire


class Bloom:
    """Blog output manager"""

    def publish(self, article_path):
        print('bloom publish')
        print(article_path)


def main():
    fire.Fire(Bloom)