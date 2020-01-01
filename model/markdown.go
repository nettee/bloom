package model

import (
	"bytes"
	"fmt"
	"github.com/jinzhu/copier"
	"io/ioutil"
	"net/url"
	"path"
	"path/filepath"
	"strings"
	"time"
)

type Paragraph interface {
	LineStrings() []string
}

func ParagraphString(p Paragraph) string {
	return strings.Join(p.LineStrings(), "\n")
}

type Heading struct {
	level int
	text  string
}

func (heading *Heading) String() string {
	return strings.Repeat("#", heading.level) + " " + heading.text
}

func (heading *Heading) LineStrings() []string {
	return []string{heading.String()}
}

type NormalParagraph struct {
	lines []Line
}

func (p *NormalParagraph) LineStrings() []string {
	var res []string
	for _, l := range p.lines {
		res = append(res, l.text)
	}
	return res
}

type Image struct {
	caption string
	uri     string
}

func (image *Image) String() string {
	return fmt.Sprintf("![%s](%s)", image.caption, image.uri)
}

func (image *Image) LineStrings() []string {
	return []string{image.String()}
}

func (image *Image) IsLocal() bool {
	return !image.IsOnline()
}

func (image *Image) IsOnline() bool {
	return strings.HasPrefix(image.uri, "http://") ||
		strings.HasPrefix(image.uri, "https://")
}

type Quote struct {
	paragraphs []Paragraph
}

func (quote *Quote) LineStrings() []string {
	var res []string
	for i, paragraph := range quote.paragraphs {
		for _, line := range paragraph.LineStrings() {
			res = append(res, ">"+line)
		}
		if i < len(quote.paragraphs)-1 {
			res = append(res, ">")
		}
	}
	return res
}

type CodeBlock struct {
	language string
	lines    []Line
}

func (codeBlock *CodeBlock) LineStrings() []string {
	res := []string{"```" + codeBlock.language}
	for _, line := range codeBlock.lines {
		res = append(res, line.text)
	}
	res = append(res, "```")
	return res
}

type MathBlock struct {
	lines []Line
}

func (mathBlock *MathBlock) LineStrings() []string {
	res := []string{"$$"}
	for _, line := range mathBlock.lines {
		res = append(res, line.text)
	}
	res = append(res, "$$")
	return res
}

type HexoHeader struct {
	Title      string
	CreateTime time.Time
	Tags       []string
}

func (hexoHeader *HexoHeader) LineStrings() []string {
	return []string{
		fmt.Sprintf("title: '%s'", hexoHeader.Title),
		fmt.Sprintf("date: %s", hexoHeader.CreateTime.Format("2006-01-02 15:04:05")),
		fmt.Sprintf("tags: [%s]", strings.Join(hexoHeader.Tags, ", ")),
		"---",
	}
}

type ReadMore struct {
}

func (readMore *ReadMore) String() string {
	return "<!-- more -->"
}

func (readMore *ReadMore) LineStrings() []string {
	return []string{readMore.String()}
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
	for _, paragraph := range doc.body {
		for _, line := range paragraph.LineStrings() {
			buffer.WriteString(line)
			buffer.WriteString("\n")
		}
		buffer.WriteString("\n")
	}
	return buffer.String()
}

func (doc *MarkdownDoc) Paragraphs() int {
	return len(doc.body)
}

func (doc *MarkdownDoc) images() []*Image {
	var images []*Image
	findImages(doc.body, &images)
	return images
}

func findImages(paragraphs []Paragraph, res *[]*Image) {
	for _, paragraph := range paragraphs {
		if image, ok := paragraph.(*Image); ok {
			*res = append(*res, image)
		} else if quote, ok := paragraph.(*Quote); ok {
			findImages(quote.paragraphs, res)
		}
	}
}

func (doc *MarkdownDoc) mathBlocks() []*MathBlock {
	var mathBlocks []*MathBlock
	for _, paragraph := range doc.body {
		if mathBlock, ok := paragraph.(*MathBlock); ok {
			mathBlocks = append(mathBlocks, mathBlock)
		}
	}
	return mathBlocks
}

func (doc *MarkdownDoc) codeBlocks() []*CodeBlock {
	var codeBlocks []*CodeBlock
	for _, paragraph := range doc.body {
		if codeBlock, ok := paragraph.(*CodeBlock); ok {
			codeBlocks = append(codeBlocks, codeBlock)
		}
	}
	return codeBlocks
}

func NewMarkdownDoc(content string) MarkdownDoc {
	parser := NewParser(content)
	paragraphs := parser.parse()

	if len(paragraphs) > 0 {
		if header, ok := paragraphs[0].(*Heading); ok && header.level == 1 {
			return MarkdownDoc{header.text, paragraphs[1:]}
		}
	}
	return MarkdownDoc{"", paragraphs}
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
		//fmt.Println()
		switch paragraph.(type) {
		case *Heading:
			headerLine := paragraph.(*Heading)
			fmt.Printf("(heading %d) %s", headerLine.level, headerLine.text)
		case *Image:
			imageLine := paragraph.(*Image)
			fmt.Printf("(image) %s", imageLine.caption)
		case *Quote:
			quote := paragraph.(*Quote)
			fmt.Println("(quote start)")
			fmt.Println(ParagraphString(quote))
			fmt.Print("(quote end)")
		case *CodeBlock:
			codeBlock := paragraph.(*CodeBlock)
			fmt.Printf("(code block) language: %s, %d lines", codeBlock.language, len(codeBlock.lines))
		case *MathBlock:
			mathBlock := paragraph.(*MathBlock)
			fmt.Printf("(math block) %d lines", len(mathBlock.lines))
		default:
			fmt.Print(ParagraphString(paragraph))
		}

		fmt.Println()
	}
}

func (doc *MarkdownDoc) PrependParagraph(paragraph Paragraph) {
	doc.body = append([]Paragraph{paragraph}, doc.body...)
}

func (doc *MarkdownDoc) AppendParagraph(paragraph Paragraph) {
	doc.body = append(doc.body, paragraph)
}

func (doc *MarkdownDoc) InsertParagraph(n int, paragraph Paragraph) {
	if n < 0 || n >= len(doc.body) {
		fmt.Printf("Warning: invalid paragraph index: %d\n", n)
		return
	}
	doc.body = append(doc.body[:n], append([]Paragraph{paragraph}, doc.body[n:]...)...)
}

func (doc *MarkdownDoc) TransferLinkToFootNote() {
	// mdnice does it
}

// transfer math equations: \\ to \newline
func (doc *MarkdownDoc) TransferMathEquationFormat() {
	count := 0
	for _, mathBlock := range doc.mathBlocks() {
		for i, line := range mathBlock.lines {
			text := line.text
			if strings.HasSuffix(text, "\\\\") {
				mathBlock.lines[i].text = text[:len(text)-2] + "\\newline"
				count++
			}
		}
	}
	fmt.Printf("Transfered %d math equations\n", count)
}

func (doc *MarkdownDoc) TransferImageUrl(baseUrl url.URL) error {
	for _, image := range doc.images() {
		if image.IsLocal() {
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
