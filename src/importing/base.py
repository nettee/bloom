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
        print(f'fetcher: {self.fetcher}, sanitizer: {self.sanitizers}, dumper: {self.dumper}')
        doc = self.fetcher.fetch(source)
        for sanitizer in self.sanitizers:
            doc = sanitizer.sanitize(doc)
        self.dumper.dump(doc)