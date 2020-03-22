from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from functools import reduce
from pathlib import Path
from typing import List, Callable, cast, Type, TypeVar, Optional


@dataclass
class Line:
    text: str

    def is_empty(self) -> bool:
        return len(self.text) == 0

    def is_heading(self) -> bool:
        return self.text.startswith('#')

    def is_hr(self) -> bool:
        return self.text == '---' or self.text == '***'

    def is_image(self) -> bool:
        return self.text.startswith('!')

    def is_quoted(self) -> bool:
        return self.text.startswith('>')

    def is_math_block_border(self) -> bool:
        return self.text.startswith('$$')

    def is_code_block_border(self) -> bool:
        return self.text.startswith('```')

    def unindent_quote(self):
        if self.text.startswith('> '):
            self.text = self.text[2:]
        elif self.text.startswith('>'):
            self.text = self.text[1:]


@dataclass
class Link:
    text: str
    url: str

    PATTERN = re.compile(r'\[(.*?)\]\((.+?)\)')

    def __str__(self):
        return f'[{self.text}]({self.url})'


class Paragraph(metaclass=ABCMeta):

    @abstractmethod
    def line_strings(self) -> List[str]:
        pass

    def string(self) -> str:
        return '\n'.join(self.line_strings())

    def __str__(self):
        return self.string()


P = TypeVar('P', bound=Paragraph)
ParagraphPredicate = Callable[[Paragraph], bool]


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
class HorizontalRule(Paragraph):

    def line_strings(self) -> List[str]:
        return [self.__str__()]

    def __str__(self):
        return '---'


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

    # TODO nested quote
    def line_strings(self) -> List[str]:
        def f(left: List[str], right: List[str]):
            left.append('')
            left.extend(right)
            return left
        lines = reduce(f, (p.line_strings() for p in self.paragraphs))
        return ['> ' + line for line in lines]

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
    title: str = field(default='')
    body: List[Paragraph] = field(default_factory=list)
    header: List[Paragraph] = field(default_factory=list)
    footer: List[Paragraph] = field(default_factory=list)

    @staticmethod
    def from_file(file: Path) -> MarkdownDoc:
        with file.open('r') as f:
            lines = f.readlines()
            return MarkdownDoc.from_lines([line.strip('\n') for line in lines])

    @staticmethod
    def from_string(content: str) -> MarkdownDoc:
        return MarkdownDoc.from_lines(content.split('\n'))

    @staticmethod
    def from_lines(lines: List[str]) -> MarkdownDoc:
        parser = MarkdownParser.from_lines(lines)
        return parser.parse()

    def string(self) -> str:
        res = self.title_string() + '\n\n'
        if len(self.header) > 0:
            res += self.header_string()
            res += '\n\n'
            res += str(HorizontalRule())
            res += '\n\n'
        res += self.body_string()
        if len(self.footer) > 0:
            res += '\n\n'
            res += str(HorizontalRule())
            res += '\n\n'
            res += self.footer_string()
        return res

    def title_string(self) -> str:
        return str(Heading(1, self.title))

    def full_body_string(self) -> str:
        paragraphs = []
        paragraphs.extend(self.header)
        if len(self.header) > 0:
            paragraphs.append(HorizontalRule())
        paragraphs.extend(self.body)
        if len(self.footer) > 0:
            paragraphs.append(HorizontalRule())
        paragraphs.extend(self.footer)
        return '\n\n'.join(p.string() for p in paragraphs)

    def body_string(self) -> str:
        return '\n\n'.join(p.string() for p in self.body)

    def header_string(self) -> str:
        return '\n\n'.join(p.string() for p in self.header)

    def footer_string(self) -> str:
        return '\n\n'.join(p.string() for p in self.footer)

    def images(self) -> List[Image]:
        return self._find_paragraph_by_class(Image)

    def math_blocks(self) -> List[MathBlock]:
        return self._find_paragraph_by_class(MathBlock)

    def _find_paragraph_by_class(self, cls: Type[P]) -> List[P]:
        res = []
        MarkdownDoc._find_paragraph_by_class_rec(self.body, cls, res)
        return res

    @staticmethod
    def _find_paragraph_by_class_rec(paragraphs: List[Paragraph], cls: Type[P], res: List[P]) -> None:
        for p in paragraphs:
            if isinstance(p, cls):
                res.append(p)
            elif isinstance(p, Quote):
                quote = cast(Quote, p)
                MarkdownDoc._find_paragraph_by_class_rec(quote.paragraphs, cls, res)

    def find_one(self, test: ParagraphPredicate) -> Optional[Paragraph]:
        for p in self.body:
            if test(p):
                return p
        return None

    def find_all(self, test: ParagraphPredicate) -> List[Paragraph]:
        return [p for p in self.body if test(p)]

    def find_adjacent(self, test: ParagraphPredicate) -> List[List[Paragraph]]:
        n = len(self.body)
        res = []
        i = 0
        while i < n:
            while i < n and not test(self.body[i]):
                i += 1
            j = i
            while j < n and test(self.body[j]):
                j += 1
            if j > i:
                res.append(self.body[i:j])
            i = j
        return res

    def remove_start(self, test: ParagraphPredicate) -> Optional[Paragraph]:
        if len(self.body) > 0 and test(self.body[0]):
            res = self.body[0]
            self.body = self.body[1:]
            return res
        else:
            return None

    def remove_start_while(self, test: ParagraphPredicate) -> List[Paragraph]:
        i = 0
        while i < len(self.body) and test(self.body[i]):
            i += 1
        res = self.body[:i]
        self.body = self.body[i:]
        return res

    def remove_start_until(self, test: ParagraphPredicate) -> List[Paragraph]:
        return self.remove_start_while(lambda p: not test(p))

    def remove_end(self, test: ParagraphPredicate) -> Optional[Paragraph]:
        if len(self.body) > 0 and test(self.body[-1]):
            res = self.body[-1]
            self.body = self.body[:-1]
            return res
        else:
            return None

    def remove_end_while(self, test: ParagraphPredicate) -> List[Paragraph]:
        i = len(self.body)
        while i > 0 and test(self.body[i-1]):
            i -= 1
        res = self.body[i:]
        self.body = self.body[:i]
        return res

    def remove_end_until(self, test: ParagraphPredicate) -> List[Paragraph]:
        return self.remove_end_while(lambda p: not test(p))

    def transfer_image_uri(self, test: Callable[[Image], bool], transfer: Callable[[str], str]) -> int:
        """
        returns: number of transfers
        """
        count = 0
        for image in self.images():
            if test(image):
                image.uri = transfer(image.uri)
                count += 1
        return count

    def transfer_math_block_by_line(self, test: Callable[[str], bool], transfer: Callable[[str], str]) -> int:
        """
        returns: number of transfers
        """
        count = 0
        for math_block in self.math_blocks():
            for i, line in enumerate(math_block.lines):
                if test(line):
                    math_block.lines[i] = transfer(line)
                    count += 1
        return count

    # For debug only
    def _show(self) -> None:
        print('title:', self.title)
        for paragraph in self.body:
            print(repr(paragraph))
            print()

    def save(self, path: Path) -> None:
        with path.open('w') as f:
            print(self.string(), file=f)


class MarkdownParseException(Exception):
    pass


class MarkdownParser:

    @staticmethod
    def from_lines(lines: List[str]) -> MarkdownParser:
        return MarkdownParser(lines)

    @staticmethod
    def from_string(content: str) -> MarkdownParser:
        return MarkdownParser.from_lines(content.split('\n'))

    def __init__(self, lines: List[str]):
        self.lines = lines
        self.pos = 0

    def parse(self) -> MarkdownDoc:
        paragraphs = self.parse_paragraphs()
        if len(paragraphs) > 0 and isinstance(paragraphs[0], Heading):
            title = cast(Heading, paragraphs[0]).text
            return MarkdownDoc(title=title, body=paragraphs[1:])
        else:
            return MarkdownDoc(body=paragraphs)

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
        elif line.is_hr():
            return self.parse_hr()
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

    def parse_hr(self) -> HorizontalRule:
        self.consume_line()
        return HorizontalRule()

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
        lines = self.consume_while(lambda l: l.is_quoted())
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

    def consume_while(self, predicate: Callable[[Line], bool]) -> List[Line]:
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
