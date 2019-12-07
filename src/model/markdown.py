from abc import ABCMeta, abstractmethod


class MdDoc(metaclass=ABCMeta):

    @abstractmethod
    def text(self):
        pass

    def __str__(self):
        return self.text()


class TextMdDoc(MdDoc):

    @staticmethod
    def from_lines(lines):
        return TextMdDoc('\n'.join(lines))

    def __init__(self, txt):
        self.txt = txt

    def text(self):
        return self.txt

    def lines(self):
        return self.txt.split('\n')


class TitledMdDoc(MdDoc):

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def title(self):
        return self.title

    def body(self):
        return self.body

    def text(self):
        return f'{self.title}\n\n{self.text}'

