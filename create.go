package main

import (
	"os"
	"regexp"
	"strings"
	"time"
)

func createArticle(en string, cn string) error {
	titleEn := en
	titleCn := cn

	nameSplitter := regexp.MustCompile(`[^0-9A-Za-z]+`)
	nameParts := nameSplitter.Split(en, -1)
	name := strings.Join(nameParts, "-")

	docNameSplitter := regexp.MustCompile(`\s+`)
	docNameParts := docNameSplitter.Split(cn, -1)
	docNameBare := strings.Join(docNameParts, "-")
	docName := docNameBare + ".md"

	err := os.Mkdir(docNameBare, os.ModePerm)
	if err != nil {
		return err
	}
	err = os.Chdir(docNameBare)
	if err != nil {
		return err
	}

	file, err := os.Create(docName)
	if err != nil {
		return err
	}
	err = file.Close()
	if err != nil {
		return err
	}

	meta := MetaInfo {
		Base: BaseInfo {
			Name:       name,
			Type:       "article", // TODO collection
			DocName:    docName,
			TitleEn:    titleEn,
			TitleCn:    titleCn,
			CreateTime: time.Now(),
			Tags:     []string{},
		},
	}

	err = writeMetaToFile(meta, "meta.toml")
	if err != nil {
		return err
	}

	err = os.Mkdir("img", os.ModePerm)
	if err != nil {
		return err
	}

	return nil
}

