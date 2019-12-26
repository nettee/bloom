package model

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/url"
	"regexp"
	"strings"
)

//type CodeBlockBorderLine struct {
//	language string // may be empty
//}
//
//func ParseCodeBlockBorderLine(line string) *CodeBlockBorderLine {
//	re := regexp.MustCompile("```(\\w*)")
//	match := re.FindStringSubmatch(line)
//	if len(match) == 0 {
//		panic("Invalid code block border line: `" + line + "'")
//	}
//
//	language := match[1]
//	return &CodeBlockBorderLine{language}
//}
//
//func (l *CodeBlockBorderLine) String() string {
//	return fmt.Sprintf("```%s", l.language)
//}

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
	return MarkdownDoc{"", paragraphs}

	//title := ""
	//i := 0
	//for len(lines) > i {
	//	if _, ok := lines[i].(*EmptyLine); ok { // checked type assertion
	//		// do nothing
	//	} else if line, ok := lines[i].(*Header); ok {
	//		title = line.text
	//	} else {
	//		break
	//	}
	//	i++
	//}
	//return MarkdownDoc{title, lines[i:]}
}

func parse(content string) []Paragraph {
	lines := strings.Split(content, "\n")

	paragraphs := []Paragraph{}
	normalLines := []string{}
	for _, line := range lines {
		if len(line) == 0 {
			if len(normalLines) > 0 {
				paragraphs = append(paragraphs, &NormalParagraph{normalLines})
				normalLines = []string{}
			}
		} else if strings.HasPrefix(line, "#") {
			if len(normalLines) > 0 {
				paragraphs = append(paragraphs, &NormalParagraph{normalLines})
				normalLines = []string{}
			}
			paragraphs = append(paragraphs, ParseHeader(line))
		} else if strings.HasPrefix(line, "!") {
			if len(normalLines) > 0 {
				paragraphs = append(paragraphs, &NormalParagraph{normalLines})
				normalLines = []string{}
			}
			paragraphs = append(paragraphs, ParseImageLine(line))
			//} else if strings.HasPrefix(line, "```") {
			//	parsed = ParseCodeBlockBorderLine(line)
		} else {
			normalLines = append(normalLines, line)
		}
	}
	return paragraphs
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
		switch paragraph.(type) {
		case *Header:
			headerLine := paragraph.(*Header)
			fmt.Printf("(header %d) %s", headerLine.level, headerLine.text)
		case *Image:
			imageLine := paragraph.(*Image)
			fmt.Printf("(image) %s", imageLine.caption)
		//case *CodeBlockBorderLine:
		//	codeBlockBorderLine := line.(*CodeBlockBorderLine)
		//	fmt.Printf("(code block border) language = '%s'", codeBlockBorderLine.language)
		case *NormalParagraph:
			fmt.Print(paragraph.String())
		}
		fmt.Println()
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
	//for _, line := range doc.body {
	//	if imageLine, ok := line.(*Image); ok {
	//		imageFileName := filepath.Base(imageLine.uri)
	//		u := url.URL{}
	//		err := copier.Copy(&u, &baseUrl)
	//		if err != nil {
	//			return err
	//		}
	//		u.Path = path.Join(u.Path, imageFileName)
	//		imageLine.uri = u.String()
	//	}
	//}
	return nil
}
