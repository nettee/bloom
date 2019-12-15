package core

import (
	"fmt"
	"github.com/nettee/bloom/model"
)

func UpdateArticleMeta(article model.Article) error {
	meta, err := article.ReadMeta()
	if err != nil {
		return err
	}

	docFile := article.DocPath(meta.Base.DocName)
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
