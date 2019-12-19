package model

import (
	"io/ioutil"
	"path"
	"strings"
)

type Article struct {
	path string
}

func NewArticle(path string) Article {
	return Article{path: path}
}

func (a *Article) Path() string {
	return a.path
}

func (a *Article) MetaPath() string {
	return path.Join(a.path, MetaFileName)
}

func (a *Article) DocPath(docName string) string {
	return path.Join(a.path, docName)
}

func (a *Article) FindMarkdownFiles() ([]string, error) {
	files, err := ioutil.ReadDir(a.path)
	if err != nil {
		return []string{}, err
	}
	var markdownFiles []string
	for _, file := range files {
		if strings.HasSuffix(file.Name(), ".md") {
			markdownFiles = append(markdownFiles, file.Name())
		}
	}
	return markdownFiles, nil
}

func (a *Article) ImagePath() string {
	return path.Join(a.path, "img")
}

func (a *Article) ReadMeta() (MetaInfo, error) {
	return ReadMetaFromFile(a.MetaPath())
}

func (a *Article) WriteMeta(meta MetaInfo) error {
	return WriteMetaToFile(meta, a.MetaPath())
}
