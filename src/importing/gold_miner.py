from importing.base import Fetcher, Sanitizer, Dumper, Importer
from model.markdown import MdDoc


# Import loop
# fetch -> sanitize -> save
class FileFetcher(Fetcher):

    def fetch(self, path):
        f = open(path, 'r')
        text = f.read()
        return MdDoc(text)


class GoldMinerSanitizer(Sanitizer):

    def sanitize(self, doc):
        print('before sanitize:', doc)
        lines = doc.lines()
        while self.is_redundant_head(lines[0]):
            lines.pop(0)
        while self.is_redundant_foot(lines[-1]):
            lines.pop()
        doc2 = MdDoc('\n'.join(lines))
        print('after sanitize:', doc2)
        return doc2

    @staticmethod
    def is_redundant_head(line):
        return len(line) == 0 or line.startswith('>')

    @staticmethod
    def is_redundant_foot(line):
        return len(line) == 0 or line == '---' or line.startswith('>')


class FileDumper(Dumper):

    def dump(self, doc):
        f = open('a.md', 'w')
        print(doc, file=f)
        f.close()


class GoldMinerFileImporter(Importer):

    def __init__(self):
        self.fetcher = FileFetcher()
        self.sanitizer = GoldMinerSanitizer()
        self.dumper = FileDumper()


def import_from_file(file):
    GoldMinerFileImporter().import_it(file)
