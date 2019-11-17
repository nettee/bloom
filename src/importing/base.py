from abc import ABCMeta, abstractmethod

from model.markdown import MdDoc


class Fetcher(metaclass=ABCMeta):

    @abstractmethod
    def fetch(self, source):
        pass


class Sanitizer(metaclass=ABCMeta):

    @abstractmethod
    def sanitize(self, doc):
        pass


class Dumper(metaclass=ABCMeta):

    @abstractmethod
    def dump(self, doc):
        pass


class NullFetcher(Fetcher):

    def fetch(self, source):
        return MdDoc('')


class IdentitySanitizer(Sanitizer):

    def sanitize(self, doc):
        return doc


class NullDumper(Dumper):

    def dump(self, doc):
        pass


class Importer(metaclass=ABCMeta):

    def __init__(self):
        self.fetcher = NullFetcher()
        self.sanitizer = IdentitySanitizer()
        self.dumper = NullDumper()

    def import_it(self, source):
        print(f'fetcher: {self.fetcher}, sanitizer: {self.sanitizer}, dumper: {self.dumper}')
        doc = self.fetcher.fetch(source)
        doc2 = self.sanitizer.sanitize(doc)
        self.dumper.dump(doc2)