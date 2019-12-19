package core

import (
	"errors"
	"fmt"
	"github.com/atotto/clipboard"
	"github.com/nettee/bloom/model"
	"io/ioutil"
	"os"
	"os/exec"
	"path"
	"strings"
)

const hexoProject = "/Users/william/projects/nettee.github.io"

type GetMeta = func(article model.Article) (model.MetaInfo, error)
type GetDoc = func(article model.Article, meta model.MetaInfo) (model.MarkdownDoc, error)
type Transfer = func(doc model.MarkdownDoc, meta model.MetaInfo) (model.MarkdownDoc, error)
type Save = func(article model.Article, doc model.MarkdownDoc, meta model.MetaInfo) error

type Publisher struct {
	getMeta   GetMeta
	getDoc    GetDoc
	transfers []Transfer
	save      Save
}

func (publisher *Publisher) publish(article model.Article) error {
	fmt.Println("Process article: ", article.Path())

	meta, err := publisher.getMeta(article)
	if err != nil {
		return err
	}

	doc, err := publisher.getDoc(article, meta)
	if err != nil {
		return err
	}

	for _, transfer := range publisher.transfers {
		doc, err = transfer(doc, meta)
		if err != nil {
			return err
		}
	}

	err = publisher.save(article, doc, meta)
	if err != nil {
		return err
	}

	return nil
}

var platformPublisher = map[string]Publisher{
	"wechat": {
		getMeta: getMetaGeneral,
		getDoc:  getDocGeneral,
		transfers: []Transfer{
			transferDocForWechat,
		},
		save: copyTitleAndBody,
	},
	"hexo": {
		getMeta: getMetaGeneral,
		getDoc:  getDocGeneral,
		transfers: []Transfer{
			transferMathEquations,
			addReadMoreLabel,
			addHexoHeaderLines,
		},
		save: exportToHexo,
	},
	"xzl": {
		getMeta: getMetaGeneral,
		getDoc: getDocGeneral,
		transfers: []Transfer {},
		save: copyTitleAndBody,
	},
	"zhihu": {
		getMeta: getMetaGeneral,
		getDoc: getDocGeneral,
		transfers: []Transfer {},
		save: saveBodyToTemp,
	},
}

func PublishArticle(article model.Article, platform string) error {
	if platform == "" {
		return errors.New("publish platform not provided")
	}
	fmt.Printf("Publish to platform %s...\n", platform)

	publisher, present := platformPublisher[platform]
	if !present {
		return errors.New(fmt.Sprintf("No publisher found for platform %s", platform))
	}
	return publisher.publish(article)
}

func getMetaGeneral(article model.Article) (model.MetaInfo, error) {
	meta, err := article.ReadMeta()
	if err != nil {
		return model.MetaInfo{}, err
	}

	// TODO debug mode
	fmt.Printf("%+v\n", meta)
	return meta, nil
}

func getDocGeneral(article model.Article, meta model.MetaInfo) (model.MarkdownDoc, error) {
	docName := meta.Base.DocName
	if docName == "" {
		return model.MarkdownDoc{}, errors.New("docName is empty")
	}
	docFile := article.DocPath(docName)
	// TODO debug mode
	fmt.Println("Markdown document: ", docFile)
	return model.ReadMarkdownDocFromFile(docFile)

}

func addHexoHeaderLines(doc model.MarkdownDoc, meta model.MetaInfo) (model.MarkdownDoc, error) {
	headerLines := []string{
		"title: '" + doc.Title() + "'",
		"date: " + meta.Base.CreateTime.Format("2006-01-02 15:04:05"),
		"tags: [" + strings.Join(meta.Base.Tags, ", ") + "]",
		"---",
		"",
	}

	doc.PrependLines(headerLines)
	return doc, nil
}

// Hexo mathjax can only recognize `\newline` syntax instead of `\\`
func transferMathEquations(doc model.MarkdownDoc, meta model.MetaInfo) (model.MarkdownDoc, error) {
	doc.TransferMathEquationFormat()
	return doc, nil
}

func addReadMoreLabel(doc model.MarkdownDoc, meta model.MetaInfo) (model.MarkdownDoc, error) {
	n := meta.Hexo.ReadMore
	if n < 15 {
		n = 15
	}

	if doc.Lines() < n {
		return doc, nil
	}

	readMoreLines := []string{
		"",
		"<!-- more -->",
		"",
	}
	doc.InsertLines(n, readMoreLines)

	return doc, nil
}

func transferDocForWechat(doc model.MarkdownDoc, meta model.MetaInfo) (model.MarkdownDoc, error) {
	// For wechat articles, we turn links to footnotes
	doc.TransferLinkToFootNote()
	return doc, nil
}

func exportToHexo(article model.Article, doc model.MarkdownDoc, meta model.MetaInfo) error {
	hexoPosts := path.Join(hexoProject, "source/_posts")
	name := meta.Base.Name
	targetFile := path.Join(hexoPosts, name+".md")

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
	sourceDir := article.ImagePath()
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

func saveBodyToTemp(article model.Article, doc model.MarkdownDoc, meta model.MetaInfo) error {
	home, err := os.UserHomeDir()
	if err != nil {
		return err
	}
	tempFile := path.Join(home, "Desktop", meta.Base.DocName)
	fmt.Println(tempFile)

	file, err := os.Create(tempFile)
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
	fmt.Println("Write to file:", tempFile)

	return nil
}

// Copy title and body seperately
// Use clipboard tools to fetch clipboard history
func copyTitleAndBody(article model.Article, doc model.MarkdownDoc, meta model.MetaInfo) error {
	err := clipboard.WriteAll(doc.Title())
	if err != nil {
		return err
	}
	fmt.Println("document title copied to clipboard")
	err = clipboard.WriteAll(doc.Body())

	if err != nil {
		return err
	}
	fmt.Println("document body copied to clipboard")
	return nil
}
