package model

import (
	"regexp"
	"strings"
)

type Line struct {
	text string
}

func (l *Line) isEmpty() bool {
	return len(l.text) == 0
}

func (l *Line) isHeading() bool {
	return strings.HasPrefix(l.text, "#")
}

func (l *Line) isImage() bool {
	return strings.HasPrefix(l.text, "!")
}

func (l *Line) isMathBlockBorder() bool {
	return strings.HasPrefix(l.text, "$$")
}

func (l *Line) isCodeBlockBorder() bool {
	return strings.HasPrefix(l.text, "```")
}

func (l *Line) isBorder() bool {
	return l.isHeading() || l.isImage() || l.isMathBlockBorder() || l.isCodeBlockBorder()
}

type LinePredicate = func(line Line) bool

type Parser struct {
	lines []Line
	pos   int
}

func NewParser(content string) Parser {
	var lines []Line
	for _, line := range strings.Split(content, "\n") {
		lines = append(lines, Line{line})
	}
	return Parser{lines, 0}
}

func (parser *Parser) eof() bool {
	return parser.pos >= len(parser.lines)
}

func (parser *Parser) nextLine() Line {
	return parser.lines[parser.pos]
}

func (parser *Parser) consumeLine() Line {
	line := parser.lines[parser.pos]
	parser.pos++
	return line
}

func (parser *Parser) consumeWhile(predicate LinePredicate) []Line {
	var lines []Line
	for !parser.eof() && predicate(parser.nextLine()) {
		lines = append(lines, parser.consumeLine())
	}
	return lines
}

func (parser *Parser) parse() []Paragraph {
	return parser.parseParagraphs()
}

func (parser *Parser) parseParagraphs() []Paragraph {
	var paragraphs []Paragraph
	for !parser.eof() {
		line := parser.nextLine()
		var p Paragraph
		if line.isEmpty() {
			parser.consumeLine()
		} else if line.isHeading() {
			p = parser.parseHeading()
		} else if line.isImage() {
			p = parser.parseImage()
		} else if line.isCodeBlockBorder() {
			p = parser.parseCodeBlock()
		} else if line.isMathBlockBorder() {
			p = parser.parseMathBlock()
		} else {
			p = parser.parseNormalParagraph()
		}
		if p != nil {
			paragraphs = append(paragraphs, p)
		}
	}
	return paragraphs
}

func (parser *Parser) parseHeading() Paragraph {
	line := parser.consumeLine()
	lineText := line.text
	re := regexp.MustCompile(`^(#+) (.*)$`)
	match := re.FindStringSubmatch(lineText)
	if len(match) == 0 {
		panic("Invalid heading: `" + lineText + "'")
	}

	level := len(match[1])
	text := match[2]
	return &Heading{level, text}
}

func (parser *Parser) parseImage() Paragraph {
	line := parser.consumeLine()
	lineText := line.text
	re := regexp.MustCompile(`!\[(.*)]\((.*)\)`)
	match := re.FindStringSubmatch(lineText)
	if len(match) == 0 {
		panic("Invalid image line: `" + lineText + "'")
	}

	caption := match[1]
	uri := match[2]
	return &Image{caption, uri}
}

func (parser *Parser) parseCodeBlock() Paragraph {
	language := parseCodeBlockLanguage(parser.consumeLine())
	lines := parser.consumeWhile(func(line Line) bool {
		return !line.isCodeBlockBorder()
	})
	_ = parser.consumeLine()
	return &CodeBlock{language, lines}
}

func parseCodeBlockLanguage(line1 Line) string {
	line := line1.text
	re := regexp.MustCompile("```(\\w+)")
	match := re.FindStringSubmatch(line)
	if len(match) == 0 {
		panic("Invalid code block: `" + line + "'")
	}

	language := match[1]
	return language
}

func (parser *Parser) parseMathBlock() Paragraph {
	_ = parser.consumeLine()
	lines := parser.consumeWhile(func(line Line) bool {
		return !line.isMathBlockBorder()
	})
	_ = parser.consumeLine()
	return &MathBlock{lines}
}

func (parser *Parser) parseNormalParagraph() Paragraph {
	lines := parser.consumeWhile(func(line Line) bool {
		return !line.isEmpty()
	})
	return &NormalParagraph{lines}
}
