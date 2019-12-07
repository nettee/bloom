package main

import (
	"fmt"
	"github.com/BurntSushi/toml"
	"github.com/atotto/clipboard"
	"github.com/urfave/cli/v2"
	"io/ioutil"
	"log"
	"os"
	"path"
	"strings"
	"time"
)

const bloomStore = "/Users/william/bloomstore"

func listItems() error {
	items, err := ioutil.ReadDir(bloomStore)
	if err != nil {
		log.Fatal(err)
	}

	count := 0
	for _, item := range items {
		itemName := item.Name()
		if strings.HasPrefix(itemName, ".") {
			continue
		}
		fmt.Println(itemName)
		count += 1
	}
	fmt.Printf("%v articles(collections).\n", count)

	return nil
}

type BaseInfo struct {
	Name string
	Type string
	DocName string
	TitleEn string
	TitleCn string
	CreateTime time.Time
	Labels []string
}

type MetaInfo struct {
	Base BaseInfo
}

func publishArticle(articlePath string) error {
	fmt.Println(articlePath)

	metaFile := path.Join(articlePath, "meta.toml")
	fmt.Println(metaFile)

	var meta MetaInfo
	_, err := toml.DecodeFile(metaFile, &meta)
	if err != nil {
		return err
	}

	fmt.Printf("%+v\n", meta)

	docName := meta.Base.DocName
	content, err := ioutil.ReadFile(docName)
	if err != nil {
		return err
	}

	err = clipboard.WriteAll(string(content))
	if err != nil {
		return err
	}

	return nil
}

func main() {

	app := &cli.App {
		Name: "bloom",
		Version: "0.0.1",
		Authors: [] *cli.Author {
			{
				Name:  "nettee",
				Email: "nettee.liu@gmail.com",
			},
		},
		Usage: "Markdown article manager",
		Commands: [] *cli.Command {
			{
				Name:    "new",
				Aliases: [] string{"n"},
				Usage:   "create article or collection",
				Action: func(c *cli.Context) error {
					return nil
				},
			},
			{
				Name:    "list",
				Aliases: [] string{"l"},
				Usage:   "list articles and collections",
				Action: func(c *cli.Context) error {
					return listItems()
				},
			},
			{
				Name: "publish",
				Aliases: [] string{"pub", "p", "deploy", "d"},
				Usage: "publish an article to (possibly) different platforms",
				Action: func(c *cli.Context) error {
					// TODO check arg exists
					articlePath := c.Args().First()
					return publishArticle(articlePath)
				},
			},
		},
	}

	err := app.Run(os.Args)
	if err != nil {
		log.Fatal(err)
	}
}
