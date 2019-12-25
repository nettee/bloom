package model

import (
	"io/ioutil"
	"os"
	"path"
	"strings"
)

// An article is an organized file structure, including
// a directory
// a metadata file
type Article struct {
	path string
	meta MetaInfo
}

func NewArticle(articlePath string) (Article, error) {
	if _, err := os.Stat(articlePath); os.IsNotExist(err) {
		return Article{}, err
	}
	metaPath := path.Join(articlePath, MetaFileName)
	meta, err := ReadMetaFromFile(metaPath)
	if err != nil {
		return Article{}, err
	}
	return Article{path: articlePath, meta: meta}, nil
}

func (a *Article) Path() string {
	return a.path
}

func (a *Article) Meta() MetaInfo {
	return a.meta
}

func (a *Article) metaPath() string {
	return path.Join(a.path, MetaFileName)
}

func (a *Article) DocPath() string {
	return path.Join(a.path, a.meta.Base.DocName)
}

func (a *Article) PathTo(relPath string) string {
	return path.Join(a.path, relPath)
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

func (a *Article) Update(meta MetaInfo) {
	a.meta = meta
}

func (a *Article) Save() error {
	return WriteMetaToFile(a.meta, a.metaPath())
}

