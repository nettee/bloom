package core

import (
	"errors"
	"fmt"
	"github.com/nettee/bloom/model"
	"log"
	"os"
)

func UpdateArticleMeta(article model.Article) error {
	meta, err := article.ReadMeta()
	if err != nil {
		return err
	}

	docFile := article.DocPath(meta.Base.DocName)

	if _, err = os.Stat(docFile); os.IsNotExist(err) {
		log.Printf("doc %s not found\n", meta.Base.DocName)
		// docFile not exists
		markdownFiles, err := article.FindMarkdownFiles()
		if err != nil {
			return err
		}
		if len(markdownFiles) == 0 {
			return errors.New("no .md files found in directory")
		} else if len(markdownFiles) == 1 {
			docName := markdownFiles[0]
			docFile = article.DocPath(docName)
			log.Printf("update docName to %s\n", docFile)
		} else {
			return errors.New("too many .md files found in directory")
		}
	}

	doc, err := model.ReadMarkdownDocFromFile(docFile)
	if err != nil {
		return err
	}

	// Update doc title to meta
	title := doc.Title()
	if meta.Base.TitleCn != title {
		fmt.Println("Update title:", title)
		meta.Base.TitleCn = title
	}

	err = article.WriteMeta(meta)
	if err != nil {
		return err
	}

	return nil
}
