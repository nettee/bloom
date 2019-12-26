package model

import (
	"bytes"
	"fmt"
	"github.com/jinzhu/copier"
	"io/ioutil"
	"net/url"
	"path"
	"path/filepath"
	"regexp"
	"strings"
)

type Paragraph interface {
	String() string
}

type Header struct {
	level int
	text  string
}

func ParseHeader(line string) *Header {
	re := regexp.MustCompile(`^(#+) (.*)$`)
	match := re.FindStringSubmatch(line)
	if len(match) == 0 {
		panic("Invalid header: `" + line + "'")
	}

	level := len(match[1])
	text := match[2]
	return &Header{level, text}
}

func (header *Header) String() string {
	return strings.Repeat("#", header.level) + " " + header.text
}

type Image struct {
	caption string
	uri     string
}

func ParseImageLine(line string) *Image {
	re := regexp.MustCompile(`!\[(.*)]\((.*)\)`)
	match := re.FindStringSubmatch(line)
	if len(match) == 0 {
		panic("Invalid image line: `" + line + "'")
	}

	caption := match[1]
	uri := match[2]
	return &Image{caption, uri}
}

func (image *Image) String() string {
	return fmt.Sprintf("![%s](%s)", image.caption, image.uri)
}

type CodeBlock struct {
	language string
	lines    []string
}

func (codeBlock *CodeBlock) String() string {
	var buffer bytes.Buffer
	buffer.WriteString(fmt.Sprintf("```%s\n", codeBlock.language))
	for _, line := range codeBlock.lines {
		buffer.WriteString(line)
		buffer.WriteString("\n")
	}
	buffer.WriteString("```")
	return buffer.String()
}

type NormalParagraph struct {
	lines []string
}

func (p *NormalParagraph) String() string {
	var buffer bytes.Buffer
	for i, line := range p.lines {
		buffer.WriteString(line)
		if i < len(p.lines)-1 {
			buffer.WriteString("\n")
		}
	}
	return buffer.String()
}

type MarkdownDoc struct {
	title string
	body  []Paragraph
}

func (doc *MarkdownDoc) Title() string {
	return doc.title
}

func (doc *MarkdownDoc) Body() string {
	var buffer bytes.Buffer
	for i, line := range doc.body {
		buffer.WriteString(line.String())
		if i < len(doc.body)-1 {
			buffer.WriteString("\n\n")
		}
	}
	return buffer.String()
}

func (doc *MarkdownDoc) Lines() int {
	return len(doc.body)
}

func NewMarkdownDoc(content string) MarkdownDoc {
	paragraphs := parse(content)

	if len(paragraphs) > 0 {
		if header, ok := paragraphs[0].(*Header); ok && header.level == 1 {
			return MarkdownDoc{header.text, paragraphs[1:]}
		}
	}
	return MarkdownDoc{"", paragraphs}
}

func parse(content string) []Paragraph {
	lines := strings.Split(content, "\n")

	var paragraphs []Paragraph
	start := -1

	inCodeBlock := false
	var language string

	for i, line := range lines {
		if inCodeBlock {
			if strings.HasPrefix(line, "```") {
				if start != -1 {
					paragraphs = append(paragraphs, &CodeBlock{language, lines[start:i]})
					start = -1
				} else {
					paragraphs = append(paragraphs, &CodeBlock{language, []string{}})
				}
				inCodeBlock = false
			} else {
				if start == -1 {
					start = i
				}
			}
		} else {
			if len(line) == 0 {
				if start != -1 {
					paragraphs = append(paragraphs, &NormalParagraph{lines[start:i]})
					start = -1
				}
			} else if strings.HasPrefix(line, "#") {
				if start != -1 {
					paragraphs = append(paragraphs, &NormalParagraph{lines[start:i]})
					start = -1
				}
				paragraphs = append(paragraphs, ParseHeader(line))
			} else if strings.HasPrefix(line, "!") {
				if start != -1 {
					paragraphs = append(paragraphs, &NormalParagraph{lines[start:i]})
					start = -1
				}
				paragraphs = append(paragraphs, ParseImageLine(line))
			} else if strings.HasPrefix(line, "```") {
				if start != -1 {
					paragraphs = append(paragraphs, &NormalParagraph{lines[start:i]})
					start = -1
				}
				inCodeBlock = true
				language = ParseCodeBlockLanguage(line)
			} else {
				if start == -1 {
					start = i
				}
			}
		}
	}
	return paragraphs
}

func ParseCodeBlockLanguage(line string) string {
	re := regexp.MustCompile("```(\\w+)")
	match := re.FindStringSubmatch(line)
	if len(match) == 0 {
		panic("Invalid code block: `" + line + "'")
	}

	language := match[1]
	return language
}

func ReadMarkdownDocFromFile(docFile string) (MarkdownDoc, error) {
	byts, err := ioutil.ReadFile(docFile)
	if err != nil {
		return MarkdownDoc{}, err
	}
	content := string(byts)
	return NewMarkdownDoc(content), nil
}

func (doc *MarkdownDoc) Show() {
	fmt.Printf("(title) %s\n", doc.title)
	for _, paragraph := range doc.body {
		fmt.Println("[Paragraph]")
		switch paragraph.(type) {
		case *Header:
			headerLine := paragraph.(*Header)
			fmt.Printf("(header %d) %s", headerLine.level, headerLine.text)
		case *Image:
			imageLine := paragraph.(*Image)
			fmt.Printf("(image) %s", imageLine.caption)
		case *CodeBlock:
			codeBlock := paragraph.(*CodeBlock)
			fmt.Printf("(code block) language: %s, %d lines", codeBlock.language, len(codeBlock.lines))
		case *NormalParagraph:
			fmt.Print(paragraph.String())
		}

		fmt.Println()
	}
}

func (doc *MarkdownDoc) PrependLines(lines []string) {
	//normalLines := make([]Line, len(lines))
	//for i, line := range lines {
	//	normalLines[i] = &NormalLine{line}
	//}
	//doc.body = append(normalLines, doc.body...)
}

func (doc *MarkdownDoc) AppendLines(lines []string) {
	//for _, line := range lines {
	//	doc.body = append(doc.body, &NormalLine{line})
	//}
}

func (doc *MarkdownDoc) InsertLines(n int, lines []string) {
	//// TODO index check
	//normalLines := make([]Line, len(lines))
	//for i, line := range lines {
	//	normalLines[i] = &NormalLine{line}
	//}
	//doc.body = append(doc.body[:n], append(normalLines, doc.body[n:]...)...)
}

func (doc *MarkdownDoc) TransferLinkToFootNote() {
	// mdnice does it
}

// transfer math equations: \\ to \newline
// TODO workaround, try to parse markdown
func (doc *MarkdownDoc) TransferMathEquationFormat() {
	// TODO broken
	//count := 0
	//for i, line := range doc.body {
	//	if strings.HasSuffix(line, "\\\\") {
	//		doc.body[i] = line[:len(line)-2] + "\\newline"
	//		count++
	//	}
	//}
	//fmt.Printf("Transfered %d math equations\n", count)
}

func (doc *MarkdownDoc) TransferImageUrl(baseUrl url.URL) error {
	for _, paragraph := range doc.body {
		if image, ok := paragraph.(*Image); ok {
			imageFileName := filepath.Base(image.uri)
			u := url.URL{}
			err := copier.Copy(&u, &baseUrl)
			if err == nil {
				u.Path = path.Join(u.Path, imageFileName)
				image.uri = u.String()
			}
		}
	}
	return nil
}
