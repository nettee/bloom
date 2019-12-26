package model

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/url"
	"regexp"
	"strings"
)

type Line struct {
	text string
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
		buffer.WriteString(line.text)
	}
	return buffer.String()
}

func (doc *MarkdownDoc) Lines() int {
	return len(doc.body)
}

func NewMarkdownDoc(content string) MarkdownDoc {
	title, body := separateTitle(content)
	// TODO workaround
	var bodyLines []Line
	for _, line := range body {
		bodyLines = append(bodyLines, Line{line})
	}
	return MarkdownDoc{
		title: title,
		body:  bodyLines,
	}
}

func ReadMarkdownDocFromFile(docFile string) (MarkdownDoc, error) {
	bytes, err := ioutil.ReadFile(docFile)
	if err != nil {
		return MarkdownDoc{}, err
	}
	content := string(bytes)
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
		fmt.Println("^" + line.text + "$")
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
