package model

import (
	"bytes"
	"github.com/BurntSushi/toml"
	"io"
	"os"
	"time"
)

const MetaFileName = "meta.toml"

type BaseInfo struct {
	Name string `toml:"name"`
	Type string `toml:"type"`
	DocName string `toml:"docName"`
	TitleEn string `toml:"titleEn"`
	TitleCn string `toml:"titleCn"`
	CreateTime time.Time `toml:"createTime"`
	Tags []string `toml:"tags"`
}

type HexoInfo struct {
	ReadMore int `toml:"readMore"`
}

type MetaInfo struct {
	Base BaseInfo `toml:"base"`
	Hexo HexoInfo `toml:"hexo"`
}

func ReadMetaFromFile(fileName string) (MetaInfo, error) {
	var meta MetaInfo
	_, err := toml.DecodeFile(fileName, &meta)
	if err != nil {
		return MetaInfo{}, err
	}
	return meta, nil
}

func WriteMetaToFile(meta MetaInfo, fileName string) error {
	metaBuf := new(bytes.Buffer)
	err := toml.NewEncoder(metaBuf).Encode(meta)
	if err != nil {
		return err
	}
	metaFile, err := os.Create(fileName)
	_, err = io.WriteString(metaFile, metaBuf.String())
	if err != nil {
		return err
	}
	err = metaFile.Close()
	if err != nil {
		return err
	}
	return nil
}


