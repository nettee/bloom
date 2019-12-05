from abc import ABCMeta, abstractmethod


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


class Importer(metaclass=ABCMeta):

    def import_it(self, source):
        print(f'fetcher: {self.fetcher}, sanitizer: {self.sanitizer}, dumper: {self.dumper}')
        doc = self.fetcher.fetch(source)
        doc2 = self.sanitizer.sanitize(doc)
        self.dumper.dump(doc2)