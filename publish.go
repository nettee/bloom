package main

import (
	"errors"
	"fmt"
	"github.com/atotto/clipboard"
	"io/ioutil"
	"os"
	"os/exec"
	"path"
	"strings"
)

const hexoProject = "/Users/william/projects/nettee.github.io"

type GetMeta = func(articlePath string) (MetaInfo, error)
type GetDoc = func(articlePath string, meta MetaInfo) (MarkdownDoc, error)
type Transfer = func(doc MarkdownDoc, meta MetaInfo) (MarkdownDoc, error)
type Save = func(articlePath string, doc MarkdownDoc, meta MetaInfo) error

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

	err = publisher.save(articlePath, doc, meta)
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
		"title: '" + doc.Title() + "'",
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
	doc.transferMathEquationFormat()
	return doc, nil
}


func transferDocForWechat(doc MarkdownDoc, meta MetaInfo) (MarkdownDoc, error) {
	// For wechat articles, we turn links to footnotes
	doc.transferLinkToFootNote()
	return doc, nil
}

func exportToHexo(articlePath string, doc MarkdownDoc, meta MetaInfo) error {
	hexoPosts := path.Join(hexoProject, "source/_posts")
	name := meta.Base.Name
	targetFile := path.Join(hexoPosts, name + ".md")


	// Write doc content to target file
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
	fmt.Println("Write to file:", targetFile)

	// Copy images to target directory
	// TODO modify image relative path (but it just works well in Hexo)
	sourceDir := path.Join(articlePath, "img")
	targetDir := path.Join(hexoPosts, name)
	err = os.MkdirAll(targetDir, os.ModePerm)
	if err != nil {
		return err
	}
	files, err := ioutil.ReadDir(sourceDir)
	if err != nil {
		return err
	}
	for _, file := range files {
		filePath := path.Join(sourceDir, file.Name())
		cmd := exec.Command("cp", "-r", filePath, targetDir)
		err := cmd.Run()
		if err != nil {
			return err
		}
	}

	fmt.Printf("Copy %d images to dir: %s\n", len(files), targetDir)

	return nil
}

func copyBody(articlePath string, doc MarkdownDoc, meta MetaInfo) error {
	// For wechat articles, we only copy body
	err := clipboard.WriteAll(doc.Body())
	if err != nil {
		return err
	}
	fmt.Println("document body copied to clipboard")
	return nil
}
