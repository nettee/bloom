package main

import (
	"fmt"
	"path"
)

func updateArticleMeta(articlePath string) error {
	article := NewArticle(articlePath)
	meta, err := article.readMeta()
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

	err = article.writeMeta(meta)
	if err != nil {
		return err
	}

	return nil
}
