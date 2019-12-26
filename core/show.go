package core

import (
	"fmt"
	"github.com/nettee/bloom/model"
)

func ShowArticle(article model.Article) error {
	doc, err := model.ReadMarkdownDocFromFile(article.DocPath())
	if err != nil {
		return err
	}
	fmt.Println(doc.Body())

	return nil
}
