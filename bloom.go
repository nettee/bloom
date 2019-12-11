package main

import (
	"bytes"
	"errors"
	"fmt"
	"github.com/BurntSushi/toml"
	"github.com/atotto/clipboard"
	"github.com/urfave/cli/v2"
	"io"
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
	Name string `toml:"name"`
	Type string `toml:"type"`
	DocName string `toml:"docName"`
	TitleEn string `toml:"titleEn"`
	TitleCn string `toml:"titleCn"`
	CreateTime time.Time `toml:"createTime"`
	Labels []string `toml:"labels"`
}

type MetaInfo struct {
	Base BaseInfo `toml:"base"`
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
			Labels:     []string{},
		},
	}

	metaBuf := new(bytes.Buffer)
	err = toml.NewEncoder(metaBuf).Encode(meta)
	if err != nil {
		return err
	}

	metaFile, err := os.Create("meta.toml")
	_, err = io.WriteString(metaFile, metaBuf.String())
	if err != nil {
		return err
	}
	err = metaFile.Close()
	if err != nil {
		return err
	}

	err = os.Mkdir("img", os.ModePerm)
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
				Flags: []cli.Flag {
					&cli.StringFlag {
						Name: "en",
						Value: "",
						Usage: "The article's English name",
					},
					&cli.StringFlag {
						Name: "cn",
						Value: "",
						Usage: "The article's Chinese name",
					},
				},
				Action: func(c *cli.Context) error {
					// TODO check arg exists
					en := c.String("en")
					cn := c.String("cn")
					if en == "" {
						return errors.New("english name required")
					}
					if cn == "" {
						return errors.New("chinese name required")
					}
					return createArticle(en, cn)
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
