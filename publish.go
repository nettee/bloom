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

type GetMeta = func(articlePath string) (MetaInfo, error)
type GetDoc = func(articlePath string, meta MetaInfo) (MarkdownDoc, error)
type Transfer = func(doc MarkdownDoc, meta MetaInfo) (MarkdownDoc, error)
type Save = func(doc MarkdownDoc, meta MetaInfo) error

type Publisher struct {
	getMeta   GetMeta
	getDoc    GetDoc
	transfers []Transfer
	save      Save
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

	for _, transfer := range publisher.transfers {
		doc, err = transfer(doc, meta)
		if err != nil {
			return err
		}
	}

	err = publisher.save(doc, meta)
	if err != nil {
		return err
	}

	return nil
}

var platformPublisher = map[string]Publisher {
	"wechat": {
		getMeta:   getMetaGeneral,
		getDoc:    getDocGeneral,
		transfers: []Transfer {
			transferDocForWechat,
		},
		save:      copyBody,
	},
	"hexo": {
		getMeta:   getMetaGeneral,
		getDoc:    getDocGeneral,
		transfers: []Transfer {
			addHexoHeaderLines,
			transferMathEquations,
		},
		save:      exportToHexo,
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

func addHexoHeaderLines(doc MarkdownDoc, meta MetaInfo) (MarkdownDoc, error) {
	headerLines := []string {
		"title: " + doc.Title(),
		"date: " + meta.Base.CreateTime.Format("2006-01-02 15:04:05"),
		"tags: [" + strings.Join(meta.Base.Tags, ", ") + "]",
		"---",
		"",
	}

	newBody := append(headerLines, doc.body...)

	return MarkdownDoc{title: doc.title, body: newBody}, nil
}

// Hexo mathjax can only recognize `\newline` syntax instead of `\\`
func transferMathEquations(doc MarkdownDoc, meta MetaInfo) (MarkdownDoc, error) {
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

	file, err := os.Create(targetFile)
	if err != nil {
		return err
	}
	_, err = file.WriteString(doc.Body())
	if err != nil {
		return err
	}
	err = file.Close()
	if err != nil {
		return err
	}

	// TODO copy images

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
