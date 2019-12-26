package model

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/url"
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

func (l *HeaderLine) String() string {
	return strings.Repeat("#", l.level) + " " + l.text
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

type ImageLine struct {
	caption string
	uri     string
}

func (l *ImageLine) String() string {
	return fmt.Sprintf("![%s](%s)", l.caption, l.uri)
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

type NormalLine struct {
	text string
}

func (l *NormalLine) String() string {
	return l.text
}

type MarkdownDoc struct {
	title string
	body  []Line
}

func (doc *MarkdownDoc) Title() string {
	return doc.title
}

func (doc *MarkdownDoc) Body() string {
	//return strings.Join(doc.body, "\n")
	var buffer bytes.Buffer
	for _, line := range doc.body {
		buffer.WriteString(line.String())
	}
	return buffer.String()
}

func (doc *MarkdownDoc) Lines() int {
	return len(doc.body)
}

func NewMarkdownDoc(content string) MarkdownDoc {

	lines := parse(content)

	return MarkdownDoc{
		title: "",
		body:  lines,
	}

	//title, body := separateTitle(content)
	//// TODO workaround
	//var bodyLines []Line
	//for _, line := range body {
	//	bodyLines = append(bodyLines, &NormalLine{line})
	//}
	//return MarkdownDoc{
	//	title: title,
	//	body:  bodyLines,
	//}
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

func separateTitle(content string) (string, []string) {
	lines := strings.Split(content, "\n")
	titleLine := ""
	i := 0
	for len(lines) > i {
		if lines[i] == "" {
			// do nothing
		} else if strings.HasPrefix(lines[i], "# ") {
			titleLine = lines[0]
		} else {
			break
		}
		i++
	}
	body := lines[i:]

	titleLeading := regexp.MustCompile(`^#\s+`)
	title := string(titleLeading.ReplaceAll([]byte(titleLine), []byte("")))

	return title, body
}

func (doc *MarkdownDoc) Show() {
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
		case *NormalLine:
			fmt.Print(line.String())
		}
		fmt.Println()
	}
}

func (doc *MarkdownDoc) PrependLines(lines []string) {
	// TODO
	//doc.body = append(lines, doc.body...)
}

func (doc *MarkdownDoc) AppendLines(lines []string) {
	// TODO
	//doc.body = append(doc.body, lines...)
}

func (doc *MarkdownDoc) InsertLines(n int, lines []string) {
	// TODO index check
	// TODO
	//doc.body = append(doc.body[:n], append(lines, doc.body[n:]...)...)
}

// TODO omit wechat links (mp.weixin.qq.com)
func (doc *MarkdownDoc) TransferLinkToFootNote() {
	// workaround regex, because Go does not support lookbehind
	//re := regexp.MustCompile(`([^!])\[(.*)\]\((.*)\)`)
	//res := re.ReplaceAll([]byte(doc), []byte(`$1[$2]($3 "$2")`))
	//return string(res), nil
	// TODO currently not working
}

// transfer math equations: \\ to \newline
// TODO workaround, try to parse markdown
func (doc *MarkdownDoc) TransferMathEquationFormat() {
	// TODO
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
	// TODO
	//re := regexp.MustCompile(`!\[(.*)]\((.*)\)`)
	//for i, line := range doc.body {
	//	if !strings.HasPrefix(line, "!") {
	//		continue
	//	}
	//	match := re.FindStringSubmatch(line)
	//	if len(match) == 0 {
	//		continue
	//	}
	//	caption := match[1]
	//	imageUri := match[2]
	//	imageFileName := filepath.Base(imageUri)
	//
	//	u := url.URL{}
	//	err := copier.Copy(&u, &baseUrl)
	//	if err != nil {
	//		return err
	//	}
	//	u.Path = path.Join(u.Path, imageFileName)
	//	newImageMarkdown := fmt.Sprintf("![%s](%s)", caption, u.String())
	//
	//	doc.body[i] = newImageMarkdown
	//}
	return nil
}
