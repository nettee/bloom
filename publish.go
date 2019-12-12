package main

import (
	"errors"
	"fmt"
	"github.com/atotto/clipboard"
	"os"
	"path"
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
	doc, err := readMarkdownDocFromFile(docFile)
	if err != nil {
		return err
	}

	// TODO transfer math equations: \\ to \newline

	headerLines := []string {
		"title: " + doc.Title(),
		"date: " + meta.Base.CreateTime.Format("2006-01-02 15:04:05"),
		"tags: [" + strings.Join(meta.Base.Tags, ", ") + "]",
	}

	targetFileContent := strings.Join(headerLines, "\n") + "\n---\n\n" + doc.Body()

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
	doc, err := readMarkdownDocFromFile(docFile)
	if err != nil {
		return err
	}

	// For wechat articles, we turn links to footnotes
	doc.transferLinkToFootNote()

	// For wechat articles, we only copy body
	err = clipboard.WriteAll(doc.Body())
	if err != nil {
		return err
	}
	fmt.Println("document copied to clipboard")

	return nil
}







