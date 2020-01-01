from abc import ABCMeta, abstractmethod


class MarkdownDoc:

    @staticmethod
    def from_file(filename):
        print('\n\n')
        with open(filename, 'r') as f:
            lines = f.readlines()
        return MarkdownDoc.from_lines([line.strip('\n') for line in lines])

    @staticmethod
    def from_string(content):
        return MarkdownDoc.from_lines(content.split('\n'))

    @staticmethod
    def from_lines(lines):
        parser = MarkdownParser.from_lines(lines)
        print(parser)
        # TODO parse it

    def __init__(self, title, body):
        self.title = title
        self.body = body


class MarkdownParser:

    @staticmethod
    def from_lines(lines):
        return MarkdownParser(lines)

    @staticmethod
    def from_string(content):
        return MarkdownParser.from_lines(content.split('\n'))

    def __init__(self, lines):
        self.lines = lines
        self.pos = 0


# ==============================


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

