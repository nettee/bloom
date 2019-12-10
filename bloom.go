package main

import (
	"errors"
	"fmt"
	"github.com/BurntSushi/toml"
	"github.com/atotto/clipboard"
	"github.com/urfave/cli/v2"
	"io/ioutil"
	"log"
	"os"
	"path"
	"regexp"
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

func readMarkdownDoc(docFile string) (string, error) {
	bytes, err := ioutil.ReadFile(docFile)
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

func seperateTitle(doc string) (string, string) {
	lines := strings.Split(doc, "\n")
	title := ""
	body := ""
	i := 0
	for len(lines) > i {
		if lines[i] == "" {
			// do nothing
		} else if strings.HasPrefix(lines[i], "# ") {
			title = lines[0]
		} else {
			break
		}
		i++
	}
	body = strings.Join(lines[i:], "\n")
	return title, body
}

// TODO omit wechat links (mp.weixin.qq.com)
func transferLinkToFootNote(doc string) (string, error) {
	// workaround regex, because Go does not support lookbehind
	re := regexp.MustCompile(`([^!])\[(.*)\]\((.*)\)`)
	res := re.ReplaceAll([]byte(doc), []byte(`$1[$2]($3 "$2")`))
	return string(res), nil
}

// Currently: for wechat
func publishArticle(articlePath string) error {
	fmt.Println("Process article: ", articlePath)

	metaFile := path.Join(articlePath, "meta.toml")

	var meta MetaInfo
	_, err := toml.DecodeFile(metaFile, &meta)
	if err != nil {
		return err
	}

	// TODO debug mode
	fmt.Printf("%+v\n", meta)

	docName := meta.Base.DocName
	if docName == "" {
		return errors.New("docName is empty")
	}
	docFile := path.Join(articlePath, docName)
	fmt.Println("Markdown document: ", docFile)
	content, err := readMarkdownDoc(docFile)
	if err != nil {
		return err
	}

	_, body := seperateTitle(content)

	// For wechat articles, we turn links to footnotes
	body, err = transferLinkToFootNote(body)
	if err != nil {
		return err
	}

	// For wechat articles, we only copy body
	err = clipboard.WriteAll(body)
	if err != nil {
		return err
	}
	fmt.Println("document copied to clipboard")

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
