package main

import (
	"errors"
	"fmt"
	"github.com/atotto/clipboard"
	"io/ioutil"
	"path"
	"regexp"
	"strings"
)

// TODO omit wechat links (mp.weixin.qq.com)
func transferLinkToFootNote(doc string) (string, error) {
	// workaround regex, because Go does not support lookbehind
	re := regexp.MustCompile(`([^!])\[(.*)\]\((.*)\)`)
	res := re.ReplaceAll([]byte(doc), []byte(`$1[$2]($3 "$2")`))
	return string(res), nil
}

// Currently: for wechat
func publishArticle(articlePath string) error {
	fmt.Println("Process article: ", articlePath)

	metaFile := path.Join(articlePath, "meta.toml")

	meta, err := readMetaFromFile(metaFile)
	if err != nil {
		return err
	}

	// TODO debug mode
	fmt.Printf("%+v\n", meta)

	docName := meta.Base.DocName
	if docName == "" {
		return errors.New("docName is empty")
	}
	docFile := path.Join(articlePath, docName)
	fmt.Println("Markdown document: ", docFile)
	content, err := readMarkdownDoc(docFile)
	if err != nil {
		return err
	}

	_, body := seperateTitle(content)

	// For wechat articles, we turn links to footnotes
	body, err = transferLinkToFootNote(body)
	if err != nil {
		return err
	}

	// For wechat articles, we only copy body
	err = clipboard.WriteAll(body)
	if err != nil {
		return err
	}
	fmt.Println("document copied to clipboard")

	return nil
}


func readMarkdownDoc(docFile string) (string, error) {
	bytes, err := ioutil.ReadFile(docFile)
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

func seperateTitle(doc string) (string, string) {
	lines := strings.Split(doc, "\n")
	title := ""
	body := ""
	i := 0
	for len(lines) > i {
		if lines[i] == "" {
			// do nothing
		} else if strings.HasPrefix(lines[i], "# ") {
			title = lines[0]
		} else {
			break
		}
		i++
	}
	body = strings.Join(lines[i:], "\n")
	return title, body
}

