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

type GetDoc = func(article model.Article) (model.MarkdownDoc, error)
type Transfer = func(article model.Article, doc model.MarkdownDoc) (model.MarkdownDoc, error)
type Save = func(article model.Article, doc model.MarkdownDoc) error

type Publisher struct {
	getDoc    GetDoc
	transfers []Transfer
	save      Save
}

func (publisher *Publisher) publish(article model.Article) error {
	fmt.Println("Process article: ", article.Path())

	doc, err := publisher.getDoc(article)
	if err != nil {
		return err
	}

	for _, transfer := range publisher.transfers {
		doc, err = transfer(article, doc)
		if err != nil {
			return err
		}
	}

	err = publisher.save(article, doc)
	if err != nil {
		return err
	}

	return nil
}

var platformPublisher = map[string]Publisher{
	"xzl": {
		getDoc:    getDocGeneral,
		transfers: []Transfer{
			transferImageUrl,
		},
		save:      copyBody,
	},
	"wechat": {
		getDoc:    getDocGeneral,
		transfers: []Transfer{
			transferImageUrl,
		},
		save:      copyBody,
	},
	"hexo": {
		getDoc:  getDocGeneral,
		transfers: []Transfer{
			transferMathEquations,
			addReadMoreLabel,
			addHexoHeaderLines,
		},
		save: exportToHexo,
	},
	"zhihu": {
		getDoc: getDocGeneral,
		transfers: []Transfer{
			transferImageUrl,
		},
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
		return errors.New(fmt.Sprintf("no publisher found for platform %s", platform))
	}
	return publisher.publish(article)
}

func getDocGeneral(article model.Article) (model.MarkdownDoc, error) {
	meta := article.Meta()
	docName := meta.Base.DocName
	if docName == "" {
		return model.MarkdownDoc{}, errors.New("docName is empty")
	}
	docFile := article.DocPath()
	// TODO debug mode
	fmt.Println("Markdown document: ", docFile)
	return model.ReadMarkdownDocFromFile(docFile)

}

func transferImageUrl(article model.Article, doc model.MarkdownDoc) (model.MarkdownDoc, error) {
	baseUrlPath := os.Getenv("BLOOM_BASE_URL_PATH")
	doc.TransferImageUrl(path.Join(baseUrlPath, article.Meta().Base.Name))
	return doc, nil
}

func addHexoHeaderLines(article model.Article, doc model.MarkdownDoc) (model.MarkdownDoc, error) {
	meta := article.Meta()
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
func transferMathEquations(article model.Article, doc model.MarkdownDoc) (model.MarkdownDoc, error) {
	doc.TransferMathEquationFormat()
	return doc, nil
}

func addReadMoreLabel(article model.Article, doc model.MarkdownDoc) (model.MarkdownDoc, error) {
	meta := article.Meta()
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

func exportToHexo(article model.Article, doc model.MarkdownDoc) error {
	meta := article.Meta()
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

func saveBodyToTemp(article model.Article, doc model.MarkdownDoc) error {
	meta := article.Meta()
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

func copyBody(article model.Article, doc model.MarkdownDoc) error {
	err := clipboard.WriteAll(doc.Body())
	if err != nil {
		return err
	}
	fmt.Println("document body copied to clipboard")
	return nil
}
