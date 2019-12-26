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

type Line interface {
	String() string
}

type EmptyLine struct {
}

func (l *EmptyLine) String() string {
	return ""
}

type HeaderLine struct {
	level int
	text  string
}

func ParseHeaderLine(line string) *HeaderLine {
	re := regexp.MustCompile(`^(#+) (.*)$`)
	match := re.FindStringSubmatch(line)
	if len(match) == 0 {
		panic("Invalid header line: `" + line + "'")
	}

	level := len(match[1])
	text := match[2]
	return &HeaderLine{level, text}
}

func (l *HeaderLine) String() string {
	return strings.Repeat("#", l.level) + " " + l.text
}

type ImageLine struct {
	caption string
	uri     string
}

func ParseImageLine(line string) *ImageLine {
	re := regexp.MustCompile(`!\[(.*)]\((.*)\)`)
	match := re.FindStringSubmatch(line)
	if len(match) == 0 {
		panic("Invalid image line: `" + line + "'")
	}

	caption := match[1]
	uri := match[2]
	return &ImageLine{caption, uri}
}

func (l *ImageLine) String() string {
	return fmt.Sprintf("![%s](%s)", l.caption, l.uri)
}

type CodeBlockBorderLine struct {
	language string // may be empty
}

func ParseCodeBlockBorderLine(line string) *CodeBlockBorderLine {
	re := regexp.MustCompile("```(\\w*)")
	match := re.FindStringSubmatch(line)
	if len(match) == 0 {
		panic("Invalid code block border line: `" + line + "'")
	}

	language := match[1]
	return &CodeBlockBorderLine{language}
}

func (l *CodeBlockBorderLine) String() string {
	return fmt.Sprintf("```%s", l.language)
}

type NormalLine struct {
	text string
}

func (l *NormalLine) String() string {
	return l.text
}

type Paragraph struct {
	lines []Line
}

type MarkdownDoc struct {
	title string
	body  []Line
}

func (doc *MarkdownDoc) Title() string {
	return doc.title
}

func (doc *MarkdownDoc) Body() string {
	var buffer bytes.Buffer
	for i, line := range doc.body {
		buffer.WriteString(line.String())
		if i < len(doc.body)-1 {
			buffer.WriteString("\n")
		}
	}
	return buffer.String()
}

func (doc *MarkdownDoc) Lines() int {
	return len(doc.body)
}

func NewMarkdownDoc(content string) MarkdownDoc {
	lines := parse(content)

	title := ""
	i := 0
	for len(lines) > i {
		if _, ok := lines[i].(*EmptyLine); ok { // checked type assertion
			// do nothing
		} else if line, ok := lines[i].(*HeaderLine); ok {
			title = line.text
		} else {
			break
		}
		i++
	}
	return MarkdownDoc{title, lines[i:]}
}

func parse(content string) []Line {
	lines := strings.Split(content, "\n")
	parsedLines := make([]Line, len(lines))
	for i, line := range lines {
		var parsed Line
		if len(line) == 0 {
			parsed = &EmptyLine{}
		} else if strings.HasPrefix(line, "#") {
			parsed = ParseHeaderLine(line)
		} else if strings.HasPrefix(line, "!") {
			parsed = ParseImageLine(line)
		} else if strings.HasPrefix(line, "```") {
			parsed = ParseCodeBlockBorderLine(line)
		} else {
			parsed = &NormalLine{line}
		}
		parsedLines[i] = parsed
	}
	return parsedLines
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
	for _, line := range doc.body {
		switch line.(type) {
		case *EmptyLine:
			fmt.Print("(empty line)")
		case *HeaderLine:
			headerLine := line.(*HeaderLine)
			fmt.Printf("(header %d) %s", headerLine.level, headerLine.text)
		case *ImageLine:
			imageLine := line.(*ImageLine)
			fmt.Printf("(image) %s", imageLine.caption)
		case *CodeBlockBorderLine:
			codeBlockBorderLine := line.(*CodeBlockBorderLine)
			fmt.Printf("(code block border) language = '%s'", codeBlockBorderLine.language)
		case *NormalLine:
			fmt.Print(line.String())
		}
		fmt.Println()
	}
}

func (doc *MarkdownDoc) PrependLines(lines []string) {
	normalLines := make([]Line, len(lines))
	for i, line := range lines {
		normalLines[i] = &NormalLine{line}
	}
	doc.body = append(normalLines, doc.body...)
}

func (doc *MarkdownDoc) AppendLines(lines []string) {
	for _, line := range lines {
		doc.body = append(doc.body, &NormalLine{line})
	}
}

func (doc *MarkdownDoc) InsertLines(n int, lines []string) {
	// TODO index check
	normalLines := make([]Line, len(lines))
	for i, line := range lines {
		normalLines[i] = &NormalLine{line}
	}
	doc.body = append(doc.body[:n], append(normalLines, doc.body[n:]...)...)
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
	for _, line := range doc.body {
		if imageLine, ok := line.(*ImageLine); ok {
			imageFileName := filepath.Base(imageLine.uri)
			u := url.URL{}
			err := copier.Copy(&u, &baseUrl)
			if err != nil {
				return err
			}
			u.Path = path.Join(u.Path, imageFileName)
			imageLine.uri = u.String()
		}
	}
	return nil
}
