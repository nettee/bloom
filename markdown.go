package main

import (
	"io/ioutil"
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

func NewMarkdownDoc(content string) MarkdownDoc {
	title, body := separateTitle(content)
	return MarkdownDoc{
		title: title,
		body:  body,
	}
}

func readMarkdownDocFromFile(docFile string) (MarkdownDoc, error) {
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

// TODO omit wechat links (mp.weixin.qq.com)
func (doc *MarkdownDoc) transferLinkToFootNote() {
	// workaround regex, because Go does not support lookbehind
	//re := regexp.MustCompile(`([^!])\[(.*)\]\((.*)\)`)
	//res := re.ReplaceAll([]byte(doc), []byte(`$1[$2]($3 "$2")`))
	//return string(res), nil
	// TODO currently not working
}