package main

import "path"

type Article struct {
	Path string
}

func NewArticle(path string) Article {
	return Article {Path: path}
}

func (a *Article) MetaPath() string {
	return path.Join(a.Path, MetaFileName)
}

func (a *Article) readMeta() (MetaInfo, error) {
	return readMetaFromFile(a.MetaPath())
}

func (a *Article) writeMeta(meta MetaInfo) error {
	return writeMetaToFile(meta, a.MetaPath())
}