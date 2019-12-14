package main

import (
	"fmt"
	"github.com/nettee/bloom/model"
	"path"
)

func updateArticleMeta(articlePath string) error {
	article := model.NewArticle(articlePath)
	meta, err := article.ReadMeta()
	if err != nil {
		return err
	}

	docFile := path.Join(article.Path, meta.Base.DocName)
	doc, err := readMarkdownDocFromFile(docFile)
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
