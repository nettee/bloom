package core

import (
	"github.com/nettee/bloom/model"
)

func ShowArticle(article model.Article) error {
	doc, err := model.ReadMarkdownDocFromFile(article.DocPath())
	if err != nil {
		return err
	}
	doc.Show()

	return nil
}
