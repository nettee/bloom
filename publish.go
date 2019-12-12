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

type Publisher struct {
	getMeta  func(articlePath string) (MetaInfo, error)
	getDoc   func(articlePath string, meta MetaInfo) (MarkdownDoc, error)
	transfer func(doc MarkdownDoc, meta MetaInfo) (MarkdownDoc, error)
	save     func(doc MarkdownDoc, meta MetaInfo) error
}

func (publisher *Publisher) publish(articlePath string) error {
	fmt.Println("Process article: ", articlePath)

	meta, err := publisher.getMeta(articlePath)
	if err != nil {
		return err
	}

	doc, err := publisher.getDoc(articlePath, meta)
	if err != nil {
		return err
	}

	doc, err = publisher.transfer(doc, meta)

	err = publisher.save(doc, meta)
	if err != nil {
		return err
	}

	return nil
}

var platformPublisher = map[string]Publisher {
	"wechat": {
		getMeta:  getMetaGeneral,
		getDoc:   getDocGeneral,
		transfer: transferDocForWechat,
		save:     copyBody,
	},
	"hexo": {
		getMeta:  getMetaGeneral,
		getDoc:   getDocGeneral,
		transfer: transferDocForHexo,
		save:     exportToHexo,
	},
}

func publishArticle(articlePath string, platform string) error {
	if platform == "" {
		return errors.New("publish platform not provided")
	}
	fmt.Printf("Publish to platform %s...\n", platform)

	publisher := platformPublisher[platform]
	return publisher.publish(articlePath)
}

func getMetaGeneral(articlePath string) (MetaInfo, error) {
	metaFile := path.Join(articlePath, "meta.toml")
	meta, err := readMetaFromFile(metaFile)
	if err != nil {
		return MetaInfo{}, err
	}

	// TODO debug mode
	fmt.Printf("%+v\n", meta)
	return meta, nil
}

func getDocGeneral(articlePath string, meta MetaInfo) (MarkdownDoc, error) {
	docName := meta.Base.DocName
	if docName == "" {
		return MarkdownDoc{}, errors.New("docName is empty")
	}
	docFile := path.Join(articlePath, docName)
	// TODO debug mode
	fmt.Println("Markdown document: ", docFile)
	return readMarkdownDocFromFile(docFile)

}

func transferDocForHexo(doc MarkdownDoc, meta MetaInfo) (MarkdownDoc, error) {
	// TODO transfer math equations: \\ to \newline
	return doc, nil
}

func transferDocForWechat(doc MarkdownDoc, meta MetaInfo) (MarkdownDoc, error) {
	// For wechat articles, we turn links to footnotes
	doc.transferLinkToFootNote()
	return doc, nil
}

func exportToHexo(doc MarkdownDoc, meta MetaInfo) error {
	name := meta.Base.Name
	targetFile := path.Join(hexoProject, "source/_posts", name + ".md")

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

func copyBody(doc MarkdownDoc, meta MetaInfo) error {
	// For wechat articles, we only copy body
	err := clipboard.WriteAll(doc.Body())
	if err != nil {
		return err
	}
	fmt.Println("document body copied to clipboard")
	return nil
}






