import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class Line:
    text: str

    def is_empty(self) -> bool:
        return len(self.text) == 0

    def is_heading(self) -> bool:
        return self.text.startswith('#')

    def is_image(self) -> bool:
        return self.text.startswith('!')

    def is_quoted(self) -> bool:
        return self.text.startswith('>')

    def is_math_block_border(self) -> bool:
        return self.text.startswith('$$')

    def is_code_block_border(self) -> bool:
        return self.text.startswith('```')

    def unindent_quote(self):
        if self.text.startswith('>'):
            self.text = self.text[1:]


class Paragraph(metaclass=ABCMeta):

    @abstractmethod
    def line_strings(self) -> List[str]:
        pass

    def string(self) -> str:
        return '\n'.join(self.line_strings())

    def __str__(self):
        return self.string()


@dataclass
class Heading(Paragraph):
    level: int
    text: str

    def line_strings(self) -> List[str]:
        return [self.__str__()]

    def __str__(self):
        return '#' * self.level + ' ' + self.text


@dataclass
class NormalParagraph(Paragraph):
    lines: List[str]

    def line_strings(self) -> List[str]:
        return self.lines

    def __repr__(self):
        if len(self.lines) == 0:
            lines_str = '[]'
        else:
            lines_str = '[\n' + '\n'.join(' ' * 4 + line for line in self.lines) + '\n]'
        return f'NormalParagraph(lines={lines_str})'


@dataclass
class Image(Paragraph):
    caption: str
    uri: str

    def line_strings(self) -> List[str]:
        return [self.__str__()]

    def __str__(self):
        return f'![{self.caption}]({self.uri})'

    def is_local(self) -> bool:
        return not self.is_online()

    def is_online(self) -> bool:
        return self.uri.startswith('http://') \
               or self.uri.startswith('https://')


@dataclass
class Quote(Paragraph):
    paragraphs: List[Paragraph]

    def line_strings(self) -> List[str]:
        res = []
        for p in self.paragraphs:
            res.extend(p.line_strings())
        return res

    def __repr__(self):
        paragraphs_str = '\n'.join(' ' * 4 + repr(p) for p in self.paragraphs)
        return f"Quote(paragraphs=[\n{paragraphs_str}\n]"


@dataclass
class CodeBlock(Paragraph):
    language: str
    lines: List[str]

    def line_strings(self) -> List[str]:
        res = ['```' + self.language]
        res.extend(self.lines)
        res.append('```')
        return res

    def __repr__(self):
        lines_str = '\n'.join(' ' * 4 + line for line in self.line_strings())
        return f"CodeBlock(language='{self.language}', lines=[\n{lines_str}\n]"


@dataclass
class MathBlock(Paragraph):
    lines: List[str]

    def line_strings(self) -> List[str]:
        res = ['$$']
        res.extend(self.lines)
        res.append('$$')
        return res


@dataclass
class HexoHeader(Paragraph):
    # TODO
    title: str

    def line_strings(self) -> List[str]:
        # TODO
        raise NotImplementedError()


class ReadMore(Paragraph):

    def line_strings(self) -> List[str]:
        return [self.__str__()]

    def __str__(self):
        return '<!-- more -->'


@dataclass
class MarkdownDoc:
    title: str
    body: List[Paragraph]

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
        return parser.parse()

    # For debug only
    def _show(self) -> None:
        print('title:', self.title)
        for paragraph in self.body:
            print(repr(paragraph))
            print()


class MarkdownParseException(Exception):
    pass


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

    def parse(self) -> MarkdownDoc:
        paragraphs = self.parse_paragraphs()
        return MarkdownDoc(title='', body=paragraphs)

    def parse_paragraphs(self) -> List[Paragraph]:
        paragraphs = []
        while not self.eof():
            line = self.next_line()
            if line.is_empty():
                self.consume_line()
            else:
                paragraphs.append(self.parse_paragraph())
        return paragraphs

    def parse_paragraph(self) -> Paragraph:
        line = self.next_line()
        if line.is_heading():
            return self.parse_heading()
        elif line.is_image():
            return self.parse_image()
        elif line.is_quoted():
            return self.parse_quote()
        elif line.is_code_block_border():
            return self.parse_code_block()
        elif line.is_math_block_border():
            return self.parse_math_block()
        else:
            return self.parse_normal_paragraph()

    def parse_heading(self) -> Heading:
        line = self.consume_line()
        return self.parse_heading_from_line(line.text)

    @staticmethod
    def parse_heading_from_line(line: str) -> Heading:
        # TODO restrict the number of #'s
        pattern = re.compile(r'^(#+)\s+(.+)$')
        m = re.match(pattern, line)
        if m is None:
            raise MarkdownParseException(f"Invalid heading `{line}'")
        level = len(m.group(1))
        text = m.group(2)
        return Heading(level=level, text=text)

    def parse_image(self) -> Image:
        line = self.consume_line()
        return self.parse_image_from_line(line.text)

    @staticmethod
    def parse_image_from_line(line: str) -> Image:
        pattern = re.compile(r'!\[(.*)\]\((.+)\)')
        m = re.match(pattern, line)
        if m is None:
            raise MarkdownParseException(f"Invalid image `{line}'")

        caption = m.group(1)
        uri = m.group(2)
        return Image(caption=caption, uri=uri)

    def parse_quote(self) -> Quote:
        lines = self.consume_while(lambda line: line.is_quoted())
        for line in lines:
            line.unindent_quote()
        sub_parser = MarkdownParser([l.text for l in lines])
        paragraphs = sub_parser.parse_paragraphs()
        return Quote(paragraphs)

    def parse_code_block(self) -> CodeBlock:
        start_line = self.consume_line()
        language = self.parse_code_language_from_line(start_line.text)
        lines = self.consume_while(lambda line: not line.is_code_block_border())
        self.consume_line()
        return CodeBlock(language=language, lines=[l.text for l in lines])

    @staticmethod
    def parse_code_language_from_line(line: str) -> str:
        pattern = re.compile(r'```(\S*)')
        m = re.match(pattern, line)
        if m is None:
            raise MarkdownParseException(f"Invalid code block start `{line}'")

        language = m.group(1)
        return language

    def parse_math_block(self) -> MathBlock:
        self.consume_line()
        lines = self.consume_while(lambda line: not line.is_math_block_border())
        self.consume_line()
        return MathBlock([l.text for l in lines])

    def parse_normal_paragraph(self) -> NormalParagraph:
        lines = self.consume_while(lambda line: not line.is_empty())
        return NormalParagraph([l.text for l in lines])

    def consume_while(self, predicate) -> List[Line]:
        lines = []
        while not self.eof() and predicate(self.next_line()):
            lines.append(self.consume_line())
        return lines

    def consume_line(self) -> Line:
        line = Line(self.lines[self.pos])
        self.pos += 1
        return line

    def next_line(self) -> Line:
        return Line(self.lines[self.pos])

    def eof(self) -> bool:
        return self.pos >= len(self.lines)

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

