
class MetaInfo:
    pass


class Article:

    def __init__(self, path):
        self.path = path
        self.meta = None # TODO

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