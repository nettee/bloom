package main

import (
	"errors"
	"fmt"
	"github.com/atotto/clipboard"
	"io/ioutil"
	"os"
	"path"
	"regexp"
	"strings"
)

const hexoProject = "/Users/william/projects/nettee.github.io"

var platformPublisher = map[string] func(string) error {
	"wechat": publishArticleToWechat,
	"hexo": publishArticleToHexo,
}

func publishArticle(articlePath string, platform string) error {
	if platform == "" {
		return errors.New("publish platform not provided")
	}
	fmt.Printf("Publish to platform %s...\n", platform)

	publisher := platformPublisher[platform]
	return publisher(articlePath)
}

func publishArticleToHexo(articlePath string) error {
	fmt.Println("Process article: ", articlePath)

	metaFile := path.Join(articlePath, "meta.toml")
	meta, err := readMetaFromFile(metaFile)
	if err != nil {
		return err
	}

	fmt.Printf("%+v\n", meta)

	name := meta.Base.Name
	targetFile := path.Join(hexoProject, "source/_posts", name + ".md")

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

	title, body := separateTitle(content)

	headerLines := []string {
		"title: " + title,
		"date: " + meta.Base.CreateTime.Format("2006-01-02 15:04:05"),
		"tags: [" + strings.Join(meta.Base.Tags, ", ") + "]",
	}

	targetFileContent := strings.Join(headerLines, "\n") + "\n---\n\n" + body

	file, err := os.Create(targetFile)
	if err != nil {
		return err
	}
	_, err = file.WriteString(targetFileContent)
	if err != nil {
		return err
	}
	err = file.Close()
	if err != nil {
		return err
	}

	fmt.Println("Write to file: ", targetFile)

	return nil
}

func publishArticleToWechat(articlePath string) error {
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

	_, body := separateTitle(content)

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

// TODO omit wechat links (mp.weixin.qq.com)
func transferLinkToFootNote(doc string) (string, error) {
	// workaround regex, because Go does not support lookbehind
	re := regexp.MustCompile(`([^!])\[(.*)\]\((.*)\)`)
	res := re.ReplaceAll([]byte(doc), []byte(`$1[$2]($3 "$2")`))
	return string(res), nil
}

func readMarkdownDoc(docFile string) (string, error) {
	bytes, err := ioutil.ReadFile(docFile)
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

func separateTitle(doc string) (string, string) {
	lines := strings.Split(doc, "\n")
	titleLine := ""
	body := ""
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
	body = strings.Join(lines[i:], "\n")

	titleLeading := regexp.MustCompile(`^#\s+`)
	title := string(titleLeading.ReplaceAll([]byte(titleLine), []byte("")))

	return title, body
}

