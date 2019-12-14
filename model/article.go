package model

import (
	"path"
)

type Article struct {
	Path string
}

func NewArticle(path string) Article {
	return Article {Path: path}
}

func (a *Article) MetaPath() string {
	return path.Join(a.Path, MetaFileName)
}

func (a *Article) ReadMeta() (MetaInfo, error) {
	return ReadMetaFromFile(a.MetaPath())
}

func (a *Article) WriteMeta(meta MetaInfo) error {
	return WriteMetaToFile(meta, a.MetaPath())
}