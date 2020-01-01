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
	String() string
}

type BundledParagraph interface {
	Paragraphs() []Paragraph
	String() string
}

type Heading struct {
	level int
	text  string
}

func (heading *Heading) String() string {
	return strings.Repeat("#", heading.level) + " " + heading.text
}

type NormalParagraph struct {
	lines []Line
}

func (p *NormalParagraph) String() string {
	var buffer bytes.Buffer
	for i, line := range p.lines {
		buffer.WriteString(line.text)
		if i < len(p.lines)-1 {
			buffer.WriteString("\n")
		}
	}
	return buffer.String()
}

type Image struct {
	caption string
	uri     string
}

func (image *Image) String() string {
	return fmt.Sprintf("![%s](%s)", image.caption, image.uri)
}

func (image *Image) IsLocal() bool {
	return !image.IsOnline()
}

func (image *Image) IsOnline() bool {
	return strings.HasPrefix(image.uri, "http://") ||
		strings.HasPrefix(image.uri, "https://")
}

type CodeBlock struct {
	language string
	lines    []Line
}

func (codeBlock *CodeBlock) String() string {
	var buffer bytes.Buffer
	buffer.WriteString(fmt.Sprintf("```%s\n", codeBlock.language))
	for _, line := range codeBlock.lines {
		buffer.WriteString(line.text)
		buffer.WriteString("\n")
	}
	buffer.WriteString("```")
	return buffer.String()
}

type MathBlock struct {
	lines []Line
}

func (mathBlock *MathBlock) String() string {
	var buffer bytes.Buffer
	buffer.WriteString("$$\n")
	for _, line := range mathBlock.lines {
		buffer.WriteString(line.text)
		buffer.WriteString("\n")
	}
	buffer.WriteString("$$")
	return buffer.String()
}

type HexoHeader struct {
	Title      string
	CreateTime time.Time
	Tags       []string
}

func (hexoHeader *HexoHeader) String() string {
	template := `title: '%s'
date: %s
tags: [%s]
---`
	return fmt.Sprintf(template, hexoHeader.Title, hexoHeader.CreateTime.Format("2006-01-02 15:04:05"),
		strings.Join(hexoHeader.Tags, ", "))
}

type ReadMore struct {
}

func (readMore *ReadMore) String() string {
	return "<!-- more -->"
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
	buffer.WriteString("\n")
	return buffer.String()
}

func (doc *MarkdownDoc) Paragraphs() int {
	return len(doc.body)
}

func (doc *MarkdownDoc) images() []*Image {
	var images []*Image
	for _, paragraph := range doc.body {
		if image, ok := paragraph.(*Image); ok {
			images = append(images, image)
		}
	}
	return images
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
		case *CodeBlock:
			codeBlock := paragraph.(*CodeBlock)
			fmt.Printf("(code block) language: %s, %d lines", codeBlock.language, len(codeBlock.lines))
		case *MathBlock:
			mathBlock := paragraph.(*MathBlock)
			fmt.Printf("(math block) %d lines", len(mathBlock.lines))
		case *NormalParagraph:
			fmt.Print(paragraph.String())
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
