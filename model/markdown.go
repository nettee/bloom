package model

import (
	"fmt"
	"io/ioutil"
	"net/url"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"strings"
)

type MarkdownDoc struct {
	title string
	body  []string
}

func (doc *MarkdownDoc) Title() string {
	return doc.title
}

func (doc *MarkdownDoc) Body() string {
	return strings.Join(doc.body, "\n")
}

func (doc *MarkdownDoc) Lines() int {
	return len(doc.body)
}

func NewMarkdownDoc(content string) MarkdownDoc {
	title, body := separateTitle(content)
	return MarkdownDoc{
		title: title,
		body:  body,
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

func (doc *MarkdownDoc) PrependLines(lines []string) {
	doc.body = append(lines, doc.body...)
}

func (doc *MarkdownDoc) AppendLines(lines []string) {
	doc.body = append(doc.body, lines...)
}

func (doc *MarkdownDoc) InsertLines(n int, lines []string) {
	// TODO index check
	doc.body = append(doc.body[:n], append(lines, doc.body[n:]...)...)
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
	count := 0
	for i, line := range doc.body {
		if strings.HasSuffix(line, "\\\\") {
			doc.body[i] = line[:len(line)-2] + "\\newline"
			count++
		}
	}
	fmt.Printf("Transfered %d math equations\n", count)
}

func (doc *MarkdownDoc) TransferImageUrl(baseUrlPath string) {

	u := url.URL{}
	u.Scheme = "http"
	u.Host = os.Getenv("BLOOM_HOST")

	re := regexp.MustCompile(`!\[(.*)]\((.*)\)`)
	for i, line := range doc.body {
		if !strings.HasPrefix(line, "!") {
			continue
		}
		match := re.FindStringSubmatch(line)
		if len(match) == 0 {
			continue
		}
		imageMarkdown := match[0]
		fmt.Println(imageMarkdown)
		caption := match[1]
		imageUri := match[2]
		imageFileName := filepath.Base(imageUri)
		fmt.Println(imageFileName)

		u.Path = path.Join(baseUrlPath, imageFileName)
		newImageMarkdown := fmt.Sprintf("![%s](%s)", caption, u.String())
		fmt.Println(newImageMarkdown)

		doc.body[i] = newImageMarkdown
	}
}
